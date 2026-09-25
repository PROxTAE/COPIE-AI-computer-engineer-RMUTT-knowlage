"use client";

import { useState, type FormEvent, type KeyboardEvent } from "react";
import { Button, TextArea } from "@heroui/react";

import { Icon } from "./Icon";

type ChatInputProps = {
  onSend?: (text: string) => void | Promise<void>;
  pending?: boolean;
  disabled?: boolean;
  placeholder?: string;
};

export function ChatInput({ onSend, pending = false, disabled = false, placeholder = "พิมพ์คำถามของคุณ..." }: ChatInputProps) {
  const [text, setText] = useState("");
  const canSend = text.trim().length > 0 && !pending && !disabled && Boolean(onSend);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSend) return;
    const message = text.trim();
    setText("");
    void onSend?.(message);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault();
      event.currentTarget.form?.requestSubmit();
    }
  }

  return (
    <form onSubmit={submit} className="w-full max-w-[720px]" aria-label="ถาม COPIE">
      <div className="copie-input relative z-10 w-full">
        <Icon name="search" size={22} className="text-cyber-ink" />
        <TextArea
          aria-label="พิมพ์คำถาม"
          placeholder={placeholder}
          value={text}
          onChange={(event) => setText(event.target.value)}
          onKeyDown={handleKeyDown}
          maxLength={1000}
          rows={1}
          disabled={pending || disabled}
          className="max-h-32 min-h-7 w-full flex-1 resize-none border-0 bg-transparent p-0 font-sans text-base text-cyber-ink shadow-none outline-none placeholder:text-cyber-muted"
        />
        <Button type="submit" variant="primary" isIconOnly isDisabled={!canSend} aria-label="ส่งคำถาม" className="h-11 w-11 rounded-full">
          <Icon name="send" size={21} />
        </Button>
      </div>
      {!disabled && <p className="mt-2 pl-5 text-xs text-cyber-muted">กด Enter เพื่อส่ง · Shift+Enter เพื่อขึ้นบรรทัดใหม่</p>}
    </form>
  );
}
