from __future__ import annotations

import json
from typing import Any, Literal

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

from app.config.settings import get_settings
from app.core.llm import count_tokens, get_chat_model
from app.core.context import ContextState, compact_context
from app.tools.file_manager import delete_file, list_files, read_file, search_files, write_file
from app.tools.registry import ToolRegistry
from app.tools.skills import execute_skill, list_skills
from app.tools.sub_agents import delegate_task
from app.tools.system_tools import get_current_time, think
from app.tools.web_search import web_search

settings = get_settings()


class AgentState(TypedDict):
    messages: list[BaseMessage]
    session_id: str
    model: str
    system_prompt: str | None
    context: dict[str, Any]
    token_count: int
    steps: list[dict[str, Any]]
    tools_used: list[str]
    sub_agents: list[dict[str, Any]]
    error: str | None


def _register_default_tools() -> None:
    tools = [
        read_file,
        write_file,
        list_files,
        delete_file,
        search_files,
        execute_skill,
        list_skills,
        delegate_task,
        web_search,
        get_current_time,
        think,
    ]
    for tool in tools:
        ToolRegistry.register(tool)


def _get_tools() -> list[BaseTool]:
    if not ToolRegistry.get_all():
        _register_default_tools()
    return ToolRegistry.get_all()


def _route_after_action(state: AgentState) -> Literal["tools", "respond", "compact"]:
    messages = state["messages"]
    last = messages[-1] if messages else None

    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"

    estimated = sum(
        len(m.content) if isinstance(m.content, str) else 0
        for m in messages
    )
    threshold = settings.max_context_tokens * settings.context_compaction_threshold
    if estimated > threshold:
        return "compact"

    return "respond"


def _create_graph() -> CompiledStateGraph:
    _register_default_tools()
    tools = _get_tools()
    tool_node = ToolNode(tools)

    workflow = StateGraph(AgentState)

    async def call_model(state: AgentState) -> dict[str, Any]:
        model_name = state.get("model") or settings.openrouter_default_model
        llm = get_chat_model(model=model_name)
        llm_with_tools = llm.bind_tools(tools)

        system_prompt = state.get("system_prompt") or None
        messages = list(state["messages"])

        if system_prompt:
            messages = [SystemMessage(content=system_prompt)] + messages

        response = await llm_with_tools.ainvoke(messages)

        token_count = await count_tokens(messages + [response])
        state["token_count"] = token_count

        tools_used = list(state.get("tools_used", []))
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tc in response.tool_calls:
                if tc["name"] not in tools_used:
                    tools_used.append(tc["name"])

        new_messages = state["messages"] + [response]

        return {
            "messages": new_messages,
            "tools_used": tools_used,
            "token_count": token_count,
            "steps": state.get("steps", []) + [{
                "type": "thought",
                "content": response.content[:500] if response.content else "",
                "tool_calls": [
                    {"name": tc["name"], "args": tc["args"]}
                    for tc in (response.tool_calls or [])
                ],
            }],
        }

    async def should_continue(state: AgentState) -> Literal["tools", "respond", "compact"]:
        return _route_after_action(state)

    async def compact_context_node(state: AgentState) -> dict[str, Any]:
        ctx = ContextState(messages=state["messages"])
        ctx = await compact_context(ctx)
        return {
            "messages": ctx.messages,
            "context": {**state.get("context", {}), "compacted": True},
        }

    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    workflow.add_node("compact", compact_context_node)

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "respond": END,
            "compact": "compact",
        },
    )

    workflow.add_edge("tools", "agent")
    workflow.add_edge("compact", "agent")

    return workflow.compile()


_graph_instance: CompiledStateGraph | None = None


def get_agent_graph() -> CompiledStateGraph:
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = _create_graph()
    return _graph_instance


async def run_agent(
    session_id: str,
    messages: list[BaseMessage],
    model: str | None = None,
    system_prompt: str | None = None,
) -> AgentState:
    graph = get_agent_graph()

    initial_state: AgentState = {
        "messages": messages,
        "session_id": session_id,
        "model": model or settings.openrouter_default_model,
        "system_prompt": system_prompt,
        "context": {},
        "token_count": 0,
        "steps": [],
        "tools_used": [],
        "sub_agents": [],
        "error": None,
    }

    result = await graph.ainvoke(
        initial_state,
        {"recursion_limit": settings.agent_recursion_limit},
    )

    return result


async def run_agent_stream(
    session_id: str,
    messages: list[BaseMessage],
    model: str | None = None,
    system_prompt: str | None = None,
):
    graph = get_agent_graph()

    initial_state: AgentState = {
        "messages": messages,
        "session_id": session_id,
        "model": model or settings.openrouter_default_model,
        "system_prompt": system_prompt,
        "context": {},
        "token_count": 0,
        "steps": [],
        "tools_used": [],
        "sub_agents": [],
        "error": None,
    }

    async for event in graph.astream_events(
        initial_state,
        version="v2",
        config={"recursion_limit": settings.agent_recursion_limit},
    ):
        kind = event.get("event")
        if kind == "on_chat_model_end":
            messages_out = event.get("data", {}).get("output", {})
            if isinstance(messages_out, AIMessage):
                yield {
                    "type": "message",
                    "content": messages_out.content,
                    "tool_calls": [
                        {"name": tc["name"], "args": tc["args"]}
                        for tc in (messages_out.tool_calls or [])
                    ],
                }
        elif kind == "on_tool_end":
            output = event.get("data", {}).get("output", "")
            yield {"type": "tool_result", "content": str(output)[:1000]}
