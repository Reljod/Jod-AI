from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.config.settings import get_settings
from app.core.llm import count_tokens, get_chat_model

settings = get_settings()


@dataclass
class ContextState:
    messages: list[BaseMessage] = field(default_factory=list)
    summaries: list[str] = field(default_factory=list)
    total_tokens: int = 0
    is_compacted: bool = False

    def add_message(self, message: BaseMessage) -> None:
        self.messages.append(message)

    def to_langchain(self) -> list[BaseMessage]:
        if not self.summaries:
            return self.messages

        summary_block = SystemMessage(
            content=f"## Conversation Summary\n\n"
            + "\n\n".join(self.summaries)
            + "\n\n(The above is a summary of earlier conversation history.)"
        )
        return [summary_block] + self.messages

    def estimate_tokens(self) -> int:
        import tiktoken

        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            texts = []
            for s in self.summaries:
                texts.append(s)
            for m in self.messages:
                if isinstance(m.content, str):
                    texts.append(m.content)
            return len(encoding.encode(" ".join(texts)))
        except Exception:
            return sum(len(m.content) if isinstance(m.content, str) else 0 for m in self.messages)


SYSTEM_PROMPT = """You are Jod-AI, a capable AI assistant powered by a deep agent framework.

You have access to various tools that you can use to accomplish tasks:
- **Skills**: Execute specialized capabilities (code, research, data analysis)
- **File Management**: Read, write, list, and manage files in the workspace
- **Sub-Agents**: Delegate complex sub-tasks to specialized agents
- **Web Search**: Search the web for up-to-date information

When using tools:
1. Think step by step about what tools you need
2. Use the most appropriate tool for each step
3. Synthesize the results into a coherent response
4. If you need to do multiple independent things, use sub-agents

Be thorough, helpful, and precise in your responses."""


def build_system_message(custom_prompt: str | None = None) -> SystemMessage:
    prompt = custom_prompt or SYSTEM_PROMPT
    return SystemMessage(content=prompt)


COMPACTION_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a conversation summarizer. Compress the following conversation into a concise summary "
        "that retains all important information, decisions, code snippets, and context needed to continue "
        "the conversation seamlessly. Focus on: key facts, user preferences, decisions made, code/files created, "
        "and unresolved tasks.",
    ),
    MessagesPlaceholder(variable_name="messages"),
])


async def compact_context(context: ContextState) -> ContextState:
    estimated = context.estimate_tokens()
    threshold = int(settings.max_context_tokens * settings.context_compaction_threshold)

    if estimated <= threshold:
        return context

    llm = get_chat_model(model=settings.summary_model)
    chain = COMPACTION_PROMPT | llm

    result = await chain.ainvoke({"messages": context.messages})

    summary = f"Summary of messages {len(context.summaries) + 1}:\n{result.content}"

    context.summaries.append(summary)
    context.messages.clear()
    context.is_compacted = True

    return context


async def prepare_messages(
    messages: list[BaseMessage],
    custom_system_prompt: str | None = None,
) -> list[BaseMessage]:
    system = build_system_message(custom_system_prompt)
    return [system] + messages


def serialize_messages(messages: list[BaseMessage]) -> list[dict[str, Any]]:
    return [
        {
            "role": "assistant" if isinstance(m, AIMessage) else ("user" if isinstance(m, HumanMessage) else m.type),
            "content": m.content,
        }
        for m in messages
    ]


def deserialize_messages(data: list[dict[str, Any]]) -> list[BaseMessage]:
    role_map = {
        "user": HumanMessage,
        "assistant": AIMessage,
        "system": SystemMessage,
    }
    result = []
    for item in data:
        cls = role_map.get(item.get("role", "user"), HumanMessage)
        result.append(cls(content=item.get("content", "")))
    return result
