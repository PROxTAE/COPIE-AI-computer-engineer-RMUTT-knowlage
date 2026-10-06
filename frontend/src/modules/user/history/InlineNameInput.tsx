"use client";

import { useEffect, useRef, useState } from "react";

type InlineNameInputProps = {
  initial?: string;
  maxLength: number;
  label: string;
  placeholder?: string;
  onSave: (value: string) => void;
  onCancel: () => void;
};

// Text field used for renaming and naming new projects: Enter or leaving the field saves, Escape cancels.
export function InlineNameInput({ initial = "", maxLength, label, placeholder, onSave, onCancel }: InlineNameInputProps) {
  const [value, setValue] = useState(initial);
  const done = useRef(false);
  const input = useRef<HTMLInputElement>(null);

  useEffect(() => {
    input.current?.focus();
    input.current?.select();
  }, []);

  const finish = (save: boolean) => {
    if (done.current) return;
    done.current = true;
    const name = value.trim();
    if (save && name && name !== initial.trim()) onSave(name);
    else onCancel();
  };

  return (
    <input
      ref={input}
      value={value}
      maxLength={maxLength}
      aria-label={label}
      placeholder={placeholder}
      onChange={(event) => setValue(event.target.value)}
      onClick={(event) => event.stopPropagation()}
      onKeyDown={(event) => {
        event.stopPropagation();
        if (event.key === "Enter" && !event.nativeEvent.isComposing) finish(true);
        if (event.key === "Escape") finish(false);
      }}
      onBlur={() => finish(true)}
      className="w-full min-w-0 rounded-lg border border-cyber-blue bg-white px-2 py-1 font-display text-sm font-bold text-cyber-strong outline-none ring-2 ring-cyber-blue/15"
    />
  );
}
