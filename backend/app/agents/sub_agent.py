from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import TypedDict


class SubAgentState(TypedDict):
    task: str
    context: str
    model: str
    messages: list[BaseMessage]
    output: str


def _create_sub_agent_graph() -> CompiledStateGraph:
    workflow = StateGraph(SubAgentState)

    async def execute_task(state: SubAgentState) -> dict[str, Any]:
        from app.core.llm import get_chat_model

        llm = get_chat_model(model=state.get("model") or None)

        messages = [
            SystemMessage(
                content="You are a focused sub-agent executing a delegated task. "
                "Be thorough and return your complete findings."
            ),
            HumanMessage(
                content=f"**Task:** {state['task']}\n\n**Context:** {state['context']}"
            ),
        ]

        result = await llm.ainvoke(messages)
        return {"messages": messages + [result], "output": result.content}

    workflow.add_node("execute", execute_task)
    workflow.set_entry_point("execute")
    workflow.add_edge("execute", END)

    return workflow.compile()


_agent_cache: dict[str, CompiledStateGraph] = {}


async def run_sub_agent(
    task: str,
    context: str = "",
    model: str = "",
    agent_id: str | None = None,
) -> dict[str, Any]:
    key = agent_id or "default"
    if key not in _agent_cache:
        _agent_cache[key] = _create_sub_agent_graph()

    agent = _agent_cache[key]
    result = await agent.ainvoke({
        "task": task,
        "context": context,
        "model": model,
        "messages": [],
        "output": "",
    })

    return result
