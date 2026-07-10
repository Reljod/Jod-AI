"use client";

import { startTransition, useCallback, useEffect, useRef, useState } from "react";

import { type Message, type ModelInfo, type Session, api } from "./api";

export function useSessions() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const data = await api.listSessions();
      startTransition(() => setSessions(data.sessions));
    } catch {
      // silent
    } finally {
      startTransition(() => setLoading(false));
    }
  }, []);

  useEffect(() => {
    let ignore = false;
    load().then(() => {
      if (ignore) return;
    });
    return () => { ignore = true; };
  }, [load]);

  return { sessions, loading, refresh: load };
}

export function useSession(sessionId: string | null) {
  const [session, setSession] = useState<{
    id: string;
    title: string;
    model: string;
    messages: Message[];
  } | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let ignore = false;

    if (!sessionId) {
      startTransition(() => setSession(null));
      return;
    }

    startTransition(() => setLoading(true));
    api
      .getSession(sessionId)
      .then((data) => {
        if (!ignore) {
          startTransition(() => {
            setSession({
              id: data.id,
              title: data.title,
              model: data.model,
              messages: data.messages,
            });
          });
        }
      })
      .catch(() => {
        if (!ignore) startTransition(() => setSession(null));
      })
      .finally(() => {
        if (!ignore) startTransition(() => setLoading(false));
      });

    return () => { ignore = true; };
  }, [sessionId]);

  return { session, loading, setSession };
}

export function useModels() {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let ignore = false;
    api
      .listModels()
      .then((data) => {
        if (!ignore) startTransition(() => setModels(data.models));
      })
      .catch(() => {})
      .finally(() => {
        if (!ignore) startTransition(() => setLoading(false));
      });
    return () => { ignore = true; };
  }, []);

  return { models, loading };
}

export function useChat(sessionId: string | null) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [streaming, setStreaming] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    let ignore = false;
    if (!sessionId) {
      startTransition(() => setMessages([]));
      return;
    }
    api.getSession(sessionId).then((data) => {
      if (!ignore) startTransition(() => setMessages(data.messages));
    });
    return () => { ignore = true; };
  }, [sessionId]);

  const send = useCallback(
    async (content: string, model?: string) => {
      if (!sessionId || streaming) return;

      const userMsg: Message = {
        id: `temp-${Date.now()}`,
        session_id: sessionId,
        role: "user",
        content,
        model: null,
        token_count: null,
        created_at: new Date().toISOString(),
      };

      startTransition(() => setMessages((prev) => [...prev, userMsg]));
      startTransition(() => setStreaming(true));
      startTransition(() => setStreamingText(""));

      try {
        abortRef.current = api.streamChat(
          sessionId,
          content,
          model,
          (chunk) => {
            startTransition(() => setStreamingText((prev) => prev + chunk));
          },
          () => {},
          (fullText) => {
            const assistantMsg: Message = {
              id: `msg-${Date.now()}`,
              session_id: sessionId,
              role: "assistant",
              content: fullText,
              model: model || null,
              token_count: null,
              created_at: new Date().toISOString(),
            };
            startTransition(() => {
              setMessages((prev) => [...prev, assistantMsg]);
              setStreaming(false);
              setStreamingText("");
            });
          },
        );
      } catch {
        startTransition(() => {
          setStreaming(false);
          setStreamingText("");
        });
      }
    },
    [sessionId, streaming],
  );

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    startTransition(() => {
      setStreaming(false);
      setStreamingText("");
    });
  }, []);

  return { messages, streaming, streamingText, send, cancel };
}
