from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.agent import run_agent
from app.core.context import (
    ContextState,
    build_system_message,
    serialize_messages,
)
from app.core.llm import get_chat_model
from app.db.models import AgentRun, Message as MessageModel
from app.db.models import Session as SessionModel
from app.db.session import get_db

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    session_id: str
    message: str
    model: str | None = None


class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    model: str | None = None
    token_count: int | None = None
    created_at: str


class ChatResponse(BaseModel):
    message: MessageResponse
    agent_run: dict[str, Any] | None = None


@router.post("")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    sess = await db.get(SessionModel, request.session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    model_name = request.model or sess.model

    result = await db.execute(
        select(MessageModel)
        .where(MessageModel.session_id == request.session_id)
        .order_by(MessageModel.created_at)
    )
    history = result.scalars().all()

    from langchain_core.messages import AIMessage, HumanMessage

    messages = [build_system_message(sess.system_prompt)]
    for msg in history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))

    messages.append(HumanMessage(content=request.message))

    agent_result = await run_agent(
        session_id=request.session_id,
        messages=messages,
        model=model_name,
        system_prompt=sess.system_prompt,
    )

    final_msg = agent_result["messages"][-1]
    response_content = final_msg.content if isinstance(final_msg, AIMessage) else str(final_msg.content) if hasattr(final_msg, "content") else ""

    user_msg = MessageModel(
        session_id=request.session_id,
        role="user",
        content=request.message,
        model=model_name,
    )
    db.add(user_msg)
    await db.flush()

    assistant_msg = MessageModel(
        session_id=request.session_id,
        role="assistant",
        content=response_content,
        model=model_name,
        token_count=agent_result.get("token_count", 0),
    )
    db.add(assistant_msg)
    await db.flush()

    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    agent_run = AgentRun(
        session_id=request.session_id,
        message_id=assistant_msg.id,
        status="completed",
        steps=agent_result.get("steps", []),
        tools_used=agent_result.get("tools_used", []),
        sub_agents=agent_result.get("sub_agents", []),
        token_usage={
            "estimated_tokens": agent_result.get("token_count", 0),
        },
        completed_at=now,
    )
    db.add(agent_run)

    await db.execute(
        update(SessionModel)
        .where(SessionModel.id == request.session_id)
        .values(title=request.message[:100] if len(history) == 0 else SessionModel.title)
    )

    return ChatResponse(
        message=MessageResponse(
            id=assistant_msg.id,
            session_id=request.session_id,
            role="assistant",
            content=response_content,
            model=model_name,
            token_count=agent_result.get("token_count", 0),
            created_at=assistant_msg.created_at.isoformat(),
        ),
        agent_run={
            "id": agent_run.id,
            "steps": agent_run.steps,
            "tools_used": agent_run.tools_used,
            "sub_agents": agent_run.sub_agents,
            "token_usage": agent_run.token_usage,
        },
    )


class StreamChatRequest(BaseModel):
    session_id: str
    message: str
    model: str | None = None


@router.post("/stream")
async def stream_chat(request: StreamChatRequest, db: AsyncSession = Depends(get_db)):
    sess = await db.get(SessionModel, request.session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    model_name = request.model or sess.model

    result = await db.execute(
        select(MessageModel)
        .where(MessageModel.session_id == request.session_id)
        .order_by(MessageModel.created_at)
    )
    history = result.scalars().all()

    from langchain_core.messages import AIMessage, HumanMessage

    messages = [build_system_message(sess.system_prompt)]
    for msg in history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))

    messages.append(HumanMessage(content=request.message))

    from app.core.agent import run_agent_stream
    from fastapi.responses import StreamingResponse

    async def event_stream():
        full_response = ""
        async for event in run_agent_stream(
            session_id=request.session_id,
            messages=messages,
            model=model_name,
            system_prompt=sess.system_prompt,
        ):
            if event["type"] == "message":
                chunk = event["content"] or ""
                if chunk:
                    full_response += chunk
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            elif event["type"] == "tool_result":
                yield f"data: {json.dumps({'type': 'tool', 'content': event['content']})}\n\n"

        yield f"data: {json.dumps({'type': 'done', 'content': full_response})}\n\n"

    import json

    return StreamingResponse(event_stream(), media_type="text/event-stream")
