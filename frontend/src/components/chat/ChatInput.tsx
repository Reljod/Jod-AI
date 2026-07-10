"use client";

import { useCallback, useRef } from "react";
import { Send, Square } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  onCancel: () => void;
  streaming: boolean;
  disabled?: boolean;
}

export function ChatInput({ onSend, onCancel, streaming, disabled }: ChatInputProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      const input = inputRef.current;
      if (!input || !input.value.trim()) return;
      onSend(input.value.trim());
      input.value = "";
    },
    [onSend],
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        const form = e.currentTarget.closest("form");
        form?.requestSubmit();
      }
    },
    [],
  );

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2">
      <input
        ref={inputRef}
        onKeyDown={handleKeyDown}
        placeholder={disabled ? "Select a session to start..." : "Type a message..."}
        disabled={disabled || streaming}
        className="flex-1 rounded-xl border border-input bg-background px-4 py-3 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50"
      />
      {streaming ? (
        <button
          type="button"
          onClick={onCancel}
          className="inline-flex items-center justify-center rounded-xl bg-destructive text-destructive-foreground hover:bg-destructive/90 h-11 w-11 transition-colors"
        >
          <Square className="h-4 w-4 fill-current" />
        </button>
      ) : (
        <button
          type="submit"
          disabled={disabled}
          className="inline-flex items-center justify-center rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 h-11 w-11 transition-colors disabled:opacity-50"
        >
          <Send className="h-4 w-4" />
        </button>
      )}
    </form>
  );
}
