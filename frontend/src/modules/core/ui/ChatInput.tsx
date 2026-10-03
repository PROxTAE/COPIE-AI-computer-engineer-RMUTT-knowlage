"use client";

import { useState, type FormEvent, type KeyboardEvent } from "react";
import { Search, SendHorizontal } from "lucide-react";

type ChatInputProps = {
  onSend?: (text: string) => void | Promise<void>;
  pending?: boolean;
  disabled?: boolean;
  placeholder?: string;
  onDraftChange?: (hasDraft: boolean) => void;
};

export function ChatInput({
  onSend,
  pending = false,
  disabled = false,
  placeholder = "พิมพ์คำถามของคุณ...",
  onDraftChange,
}: ChatInputProps) {
  const [text, setText] = useState("");
  const canSend = text.trim().length > 0 && !pending && !disabled && Boolean(onSend);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSend) return;
    const message = text.trim();
    setText("");
    void onSend?.(message);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault();
      event.currentTarget.form?.requestSubmit();
    }
  }

  return (
    <form onSubmit={submit} className="w-full max-w-[760px]" aria-label="ถาม COPIE">
      <div className="relative flex items-center gap-3 rounded-full border-2 border-[#155ff2]/80 bg-white px-5 py-2.5 shadow-[0_8px_24px_rgba(21,95,242,0.12)] focus-within:border-[#155ff2] focus-within:shadow-[0_10px_32px_rgba(21,95,242,0.22)] transition-all">
        <Search className="size-5 text-[#155ff2] shrink-0" />
        <input
          type="text"
          aria-label="พิมพ์คำถาม"
          placeholder={placeholder}
          value={text}
          onChange={(event) => {
            setText(event.target.value);
            onDraftChange?.(event.target.value.trim().length > 0);
          }}
          onKeyDown={handleKeyDown}
          maxLength={1000}
          disabled={pending || disabled}
          className="flex-1 min-w-0 border-0 bg-transparent font-sans text-base font-medium text-[#080b12] outline-none placeholder:text-[#6b82a6]"
        />
        <button
          type="submit"
          disabled={!canSend}
          aria-label="ส่งคำถาม"
          className="flex size-10 items-center justify-center rounded-full bg-gradient-to-r from-[#0f5ff0] to-[#155ff2] text-white shadow-sm hover:shadow-md hover:scale-105 active:scale-95 transition-all cursor-pointer disabled:opacity-40 disabled:pointer-events-none shrink-0"
        >
          <SendHorizontal className="size-5" />
        </button>
      </div>
    </form>
  );
}
