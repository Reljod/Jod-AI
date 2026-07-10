# Jod-AI

Deep Agent Platform — a full-stack AI chat application with OpenRouter integration, LangGraph-powered deep agents, tool/skill/sub-agent extensibility, and context management.

## Architecture

```
jod-ai/
├── frontend/              # Next.js 16 + Tailwind CSS v4 + shadcn/ui
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx     → redirects to /chat
│   │   │   └── chat/
│   │   │       └── page.tsx  # Main chat UI
│   │   ├── components/
│   │   │   └── chat/
│   │   │       ├── ChatMessage.tsx   # Message bubbles
│   │   │       ├── ChatInput.tsx     # Input with send/cancel
│   │   │       ├── ModelSelector.tsx # OpenRouter model picker
│   │   │       └── Sidebar.tsx       # Session list
│   │   └── lib/
│   │       ├── api.ts       # HTTP client for all endpoints
│   │       └── hooks.ts     # React hooks (useSessions, useChat, useModels)
│   └── ...
├── backend/                # FastAPI + SQLAlchemy + LangGraph
│   ├── docker-compose.yml  # PostgreSQL (pgvector) + Redis
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py         # FastAPI entry point
│   │   ├── config/
│   │   │   └── settings.py # Pydantic settings (env-based)
│   │   ├── api/
│   │   │   ├── chat.py     # POST /api/chat + /api/chat/stream
│   │   │   ├── models.py   # GET /api/models
│   │   │   ├── sessions.py # CRUD /api/sessions
│   │   │   ├── tools.py    # GET /api/tools
│   │   │   └── files.py    # POST /api/files/upload
│   │   ├── core/
│   │   │   ├── llm.py      # OpenRouter LLM factory + model listing
│   │   │   ├── context.py  # Context window management + compaction
│   │   │   └── agent.py    # LangGraph deep agent graph
│   │   ├── tools/
│   │   │   ├── registry.py # Tool registration system
│   │   │   ├── file_manager.py  # read/write/list/search/delete files
│   │   │   ├── skills.py       # Skill execution tool
│   │   │   ├── sub_agents.py   # Sub-agent delegation tool
│   │   │   ├── web_search.py   # DuckDuckGo web search
│   │   │   └── system_tools.py # think(), get_current_time()
│   │   ├── agents/
│   │   │   └── sub_agent.py    # LangGraph sub-agent definition
│   │   ├── skills/
│   │   │   └── manager.py      # Skill loading/registry with @skill decorator
│   │   └── db/
│   │       ├── models.py   # SQLAlchemy models (Session, Message, File, AgentRun)
│   │       └── session.py  # Async database session management
│   └── requirements.txt
└── README.md
```

## Features

### Chat & Models
- **Full chat interface** with streaming responses (SSE)
- **OpenRouter integration** — use any model OpenRouter supports (GPT-4, Claude, Gemini, Llama, DeepSeek, etc.)
- **Model selector** in the UI, grouped by provider with context-length info
- **Per-session model selection** — each conversation can use a different model

### Deep Agent (LangGraph)
- **StateGraph-based agent** with tool-calling loop
- **Chain-of-thought reasoning** via `think()` tool
- **Recursion limit** protection and step tracking
- **Streaming agent events** for real-time UI updates

### Tools & Extensibility
- **Tool Registry** — centralized tool registration, easy to add new tools
- **File Management** — read, write, list, search, delete files in workspace
- **Skills** — pluggable skill system with `@skill` decorator; load from directory
- **Sub-Agents** — delegate tasks to focused sub-agents with optional model override
- **Web Search** — DuckDuckGo search for up-to-date information

### Context Management
- **Token estimation** via `tiktoken`
- **Adaptive compaction** — when context exceeds threshold, older messages are summarized
- **Configurable** max context tokens and compaction ratio

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (for database)
- OpenRouter API key

### 1. Start the database

```bash
cd backend
docker compose up -d
```

### 2. Configure environment

```bash
cd backend
cp .env.example .env
# Edit .env — set OPENROUTER_API_KEY
```

### 3. Start the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:3000

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/models` | List available OpenRouter models |
| GET | `/api/models/default` | Get default model |
| GET/POST | `/api/sessions` | List / create sessions |
| GET/PATCH/DELETE | `/api/sessions/:id` | Session CRUD |
| POST | `/api/chat` | Send message (non-streaming) |
| POST | `/api/chat/stream` | Send message (SSE streaming) |
| GET | `/api/tools` | List registered tools |
| POST | `/api/files/upload` | Upload a file |

## Adding a New Tool

1. Create a file in `backend/app/tools/` (or add to an existing file)
2. Define a function decorated with `@tool` from `langchain_core.tools`
3. Import and register it in `app/core/agent.py:_register_default_tools()`

```python
from langchain_core.tools import tool

@tool
async def my_custom_tool(param: str) -> str:
    """Description of what this tool does."""
    # Your implementation
    return result
```

## Adding a New Skill

1. Create `backend/skills/my_skill.py`
2. Use the `@skill` decorator:

```python
from app.skills.manager import skill

@skill(name="my-skill", description="Does something useful")
async def my_skill_handler(query: str) -> str:
    return f"Processed: {query}"
```

Skills are auto-loaded from the skills directory on startup.

## Development

- **Frontend lint:** `cd frontend && npm run lint`
- **Backend lint:** `cd backend && ruff check .`
- **Format:** `cd backend && ruff format .`
