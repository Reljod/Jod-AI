"use client";

import { ChatMessage, StreamingMessage } from "@/components/chat/ChatMessage";
import { ChatInput } from "@/components/chat/ChatInput";
import { ModelSelector } from "@/components/chat/ModelSelector";
import { Sidebar } from "@/components/chat/Sidebar";
import { useChat, useSession, useSessions } from "@/lib/hooks";
import { api } from "@/lib/api";
import { Bot, PanelLeftClose, PanelLeft, Sparkles } from "lucide-react";
import { startTransition, useCallback, useEffect, useRef, useState } from "react";

export default function ChatPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { sessions, refresh: refreshSessions } = useSessions();
  const { session, loading: sessionLoading } = useSession(activeSessionId);
  const { messages, streaming, streamingText, send, cancel } = useChat(activeSessionId);

  useEffect(() => {
    if (session?.model) startTransition(() => setSelectedModel(session.model));
  }, [session?.model]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingText]);

  const handleCreateSession = useCallback(async () => {
    const data = await api.createSession({ title: "New Chat" });
    setActiveSessionId(data.id);
    await refreshSessions();
  }, [refreshSessions]);

  const handleSelectSession = useCallback((id: string) => {
    setActiveSessionId(id);
  }, []);

  const handleDeleteSession = useCallback(
    async (id: string) => {
      await api.deleteSession(id);
      if (activeSessionId === id) setActiveSessionId(null);
      await refreshSessions();
    },
    [activeSessionId, refreshSessions],
  );

  const handleSend = useCallback(
    async (content: string) => {
      if (!activeSessionId) return;
      await send(content, selectedModel || undefined);
      await refreshSessions();
    },
    [activeSessionId, selectedModel, send, refreshSessions],
  );

  const handleChangeModel = useCallback(
    async (model: string) => {
      setSelectedModel(model);
      if (activeSessionId) {
        await api.updateSession(activeSessionId, { model });
      }
    },
    [activeSessionId],
  );

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? "w-64" : "w-0"
        } transition-all duration-200 overflow-hidden border-r border-border`}
      >
        <Sidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelect={handleSelectSession}
          onCreate={handleCreateSession}
          onDelete={handleDeleteSession}
        />
      </div>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-14 border-b border-border flex items-center justify-between px-4 shrink-0">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              {sidebarOpen ? (
                <PanelLeftClose className="h-4 w-4" />
              ) : (
                <PanelLeft className="h-4 w-4" />
              )}
            </button>
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <h1 className="text-sm font-semibold">Jod-AI</h1>
            </div>
          </div>

          <ModelSelector value={selectedModel} onChange={handleChangeModel} />
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-6">
          {!activeSessionId ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <Bot className="h-12 w-12 text-muted-foreground/30 mb-4" />
              <h2 className="text-xl font-semibold text-foreground mb-2">
                Welcome to Jod-AI
              </h2>
              <p className="text-sm text-muted-foreground max-w-md">
                Start a new conversation or select an existing one. I can use
                tools, manage files, delegate tasks to sub-agents, and more.
              </p>
            </div>
          ) : sessionLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="animate-spin h-6 w-6 border-2 border-primary border-t-transparent rounded-full" />
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-4">
              {messages.length === 0 && !streaming && (
                <div className="text-center py-12">
                  <p className="text-sm text-muted-foreground">
                    Send a message to start the conversation
                  </p>
                </div>
              )}

              {messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))}

              {streaming && streamingText && (
                <StreamingMessage content={streamingText} />
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-border p-4">
          <div className="max-w-3xl mx-auto">
            <ChatInput
              onSend={handleSend}
              onCancel={cancel}
              streaming={streaming}
              disabled={!activeSessionId}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
