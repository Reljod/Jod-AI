"use client";

import type { Message } from "@/lib/api";

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-primary text-primary-foreground rounded-br-sm"
            : "bg-muted text-muted-foreground rounded-bl-sm"
        }`}
      >
        <div className="text-sm whitespace-pre-wrap">{message.content}</div>
        {message.token_count && (
          <div className="text-[10px] opacity-50 mt-1 text-right">
            {message.token_count} tokens
          </div>
        )}
      </div>
    </div>
  );
}

export function StreamingMessage({ content }: { content: string }) {
  return (
    <div className="flex justify-start">
      <div className="max-w-[80%] rounded-2xl rounded-bl-sm px-4 py-3 bg-muted text-muted-foreground">
        <div className="text-sm whitespace-pre-wrap">
          {content}
          <span className="inline-block w-2 h-4 bg-primary ml-0.5 animate-pulse" />
        </div>
      </div>
    </div>
  );
}
