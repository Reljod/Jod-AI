from __future__ import annotations

import json
import uuid

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

from app.core.llm import get_chat_model


@tool
async def delegate_task(
    task: str,
    context: str = "",
    model: str = "",
) -> str:
    """Delegate a complex sub-task to a specialized sub-agent.

    Use this when you need to work on multiple independent tasks in parallel,
    or when a task requires deep focus on a specific area.

    Args:
        task: Clear description of what the sub-agent should do
        context: Optional context or relevant information for the sub-agent
        model: Optional model override (e.g., 'openai/o3-mini' for reasoning tasks)

    Returns:
        The sub-agent's complete response
    """
    agent_id = str(uuid.uuid4())[:8]
    llm = get_chat_model(model=model) if model else get_chat_model()

    messages = [
        HumanMessage(
            content=f"""You are a focused sub-agent (ID: {agent_id}) working on a delegated task.

**Task:**
{task}

**Context:**
{context}

**Guidelines:**
1. Focus solely on this task
2. Be thorough and complete
3. Return your final answer with all relevant details
4. If you need to create files, describe what to create

**Your Response:**"""
        )
    ]

    result = await llm.ainvoke(messages)

    return f"**[Sub-Agent {agent_id} Result]:**\n\n{result.content}"
