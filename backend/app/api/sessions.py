from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import serialize_messages
from app.db.models import Message as MessageModel
from app.db.models import Session as SessionModel
from app.db.session import get_db

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class CreateSessionRequest(BaseModel):
    title: str = "New Chat"
    model: str | None = None
    system_prompt: str | None = None


class UpdateSessionRequest(BaseModel):
    title: str | None = None
    model: str | None = None
    system_prompt: str | None = None


@router.get("")
async def list_sessions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SessionModel).order_by(SessionModel.updated_at.desc()).limit(50)
    )
    sessions = result.scalars().all()

    return {
        "sessions": [
            {
                "id": s.id,
                "title": s.title,
                "model": s.model,
                "message_count": len(s.messages) if s.messages else 0,
                "created_at": s.created_at.isoformat(),
                "updated_at": s.updated_at.isoformat(),
            }
            for s in sessions
        ]
    }


@router.post("")
async def create_session(
    request: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
):
    sess = SessionModel(
        title=request.title,
        model=request.model,
        system_prompt=request.system_prompt,
    )
    db.add(sess)
    await db.flush()

    return {
        "id": sess.id,
        "title": sess.title,
        "model": sess.model,
        "system_prompt": sess.system_prompt,
        "created_at": sess.created_at.isoformat(),
    }


@router.get("/{session_id}")
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    sess = await db.get(SessionModel, session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    result = await db.execute(
        select(MessageModel)
        .where(MessageModel.session_id == session_id)
        .order_by(MessageModel.created_at)
    )
    messages = result.scalars().all()

    return {
        "id": sess.id,
        "title": sess.title,
        "model": sess.model,
        "system_prompt": sess.system_prompt,
        "created_at": sess.created_at.isoformat(),
        "updated_at": sess.updated_at.isoformat(),
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "model": m.model,
                "token_count": m.token_count,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
    }


@router.patch("/{session_id}")
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    db: AsyncSession = Depends(get_db),
):
    sess = await db.get(SessionModel, session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    updates = {}
    if request.title is not None:
        updates["title"] = request.title
    if request.model is not None:
        updates["model"] = request.model
    if request.system_prompt is not None:
        updates["system_prompt"] = request.system_prompt

    if updates:
        await db.execute(
            update(SessionModel)
            .where(SessionModel.id == session_id)
            .values(**updates)
        )

    return {"status": "updated"}


@router.delete("/{session_id}")
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    sess = await db.get(SessionModel, session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    await db.delete(sess)
    return {"status": "deleted"}
