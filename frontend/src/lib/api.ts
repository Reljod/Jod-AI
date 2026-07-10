const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Session {
  id: string;
  title: string;
  model: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  model: string | null;
  token_count: number | null;
  created_at: string;
}

export interface ModelInfo {
  id: string;
  name: string;
  provider: string;
  description: string;
  pricing: { prompt: number; completion: number };
  context_length: number;
}

export interface ToolInfo {
  name: string;
  description: string;
  args: Record<string, unknown>;
}

export interface AgentRun {
  id: string;
  steps: Array<{
    type: string;
    content: string;
    tool_calls: Array<{ name: string; args: Record<string, unknown> }>;
  }>;
  tools_used: string[];
  sub_agents: unknown[];
  token_usage: Record<string, unknown>;
}

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const body = await res.text();
    throw new ApiError(res.status, body || res.statusText);
  }

  return res.json();
}

export const api = {
  // Sessions
  async listSessions() {
    return request<{ sessions: Session[] }>("/api/sessions");
  },

  async createSession(data: {
    title?: string;
    model?: string;
    system_prompt?: string;
  }) {
    return request<Session & { system_prompt: string | null }>(
      "/api/sessions",
      {
        method: "POST",
        body: JSON.stringify(data),
      },
    );
  },

  async getSession(sessionId: string) {
    return request<{
      id: string;
      title: string;
      model: string;
      system_prompt: string | null;
      messages: Message[];
      created_at: string;
      updated_at: string;
    }>(`/api/sessions/${sessionId}`);
  },

  async updateSession(
    sessionId: string,
    data: { title?: string; model?: string },
  ) {
    return request<{ status: string }>(`/api/sessions/${sessionId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },

  async deleteSession(sessionId: string) {
    return request<{ status: string }>(`/api/sessions/${sessionId}`, {
      method: "DELETE",
    });
  },

  // Chat
  async sendMessage(sessionId: string, message: string, model?: string) {
    return request<{
      message: Message;
      agent_run: AgentRun | null;
    }>("/api/chat", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId, message, model }),
    });
  },

  streamChat(
    sessionId: string,
    message: string,
    model?: string,
    onChunk: (text: string) => void = () => {},
    onTool: (text: string) => void = () => {},
    onDone: (fullText: string) => void = () => {},
  ): AbortController {
    const controller = new AbortController();

    fetch(`${API_BASE}/api/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message, model }),
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok || !response.body) return;
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === "chunk") onChunk(data.content);
              else if (data.type === "tool") onTool(data.content);
              else if (data.type === "done") onDone(data.content);
            } catch {
              // skip unparseable
            }
          }
        }
      })
      .catch(() => {});

    return controller;
  },

  // Models
  async listModels() {
    return request<{ models: ModelInfo[] }>("/api/models");
  },

  async getDefaultModel() {
    return request<{ model: string }>("/api/models/default");
  },

  // Tools
  async listTools() {
    return request<{ tools: Record<string, ToolInfo> }>("/api/tools");
  },
};
