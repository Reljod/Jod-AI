"use client";

import { useModels } from "@/lib/hooks";
import { ChevronDown } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

interface ModelSelectorProps {
  value: string;
  onChange: (model: string) => void;
}

export function ModelSelector({ value, onChange }: ModelSelectorProps) {
  const { models, loading } = useModels();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const currentModel = models.find((m) => m.id === value);

  const handleSelect = useCallback(
    (modelId: string) => {
      onChange(modelId);
      setOpen(false);
    },
    [onChange],
  );

  const grouped = models.reduce(
    (acc, m) => {
      const group = m.provider || "Other";
      if (!acc[group]) acc[group] = [];
      acc[group].push(m);
      return acc;
    },
    {} as Record<string, typeof models>,
  );

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        disabled={loading}
        className="inline-flex items-center gap-2 rounded-lg border border-input bg-background px-3 py-1.5 text-xs font-medium hover:bg-accent transition-colors disabled:opacity-50"
      >
        <span className="max-w-[160px] truncate">
          {loading ? "Loading..." : currentModel?.name || value || "Select model"}
        </span>
        <ChevronDown className="h-3 w-3 opacity-50" />
      </button>

      {open && (
        <div className="absolute top-full right-0 mt-1 w-72 max-h-96 overflow-y-auto rounded-lg border border-border bg-popover p-1 shadow-lg z-50">
          {Object.entries(grouped).map(([provider, providerModels]) => (
            <div key={provider}>
              <div className="px-2 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                {provider}
              </div>
              {providerModels.map((m) => (
                <button
                  key={m.id}
                  type="button"
                  onClick={() => handleSelect(m.id)}
                  className={`w-full text-left px-2 py-1.5 rounded-md text-xs transition-colors ${
                    m.id === value
                      ? "bg-primary/10 text-primary font-medium"
                      : "hover:bg-accent text-foreground"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="truncate">{m.name}</span>
                    {m.context_length > 0 && (
                      <span className="text-[10px] text-muted-foreground shrink-0 ml-2">
                        {(m.context_length / 1000).toFixed(0)}k
                      </span>
                    )}
                  </div>
                </button>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
