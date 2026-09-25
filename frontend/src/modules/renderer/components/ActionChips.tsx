// ปุ่มคำถามต่อยอดใต้คำตอบ
// type "ask" ส่งข้อความกลับเข้าแชตผ่าน onAsk · type "open_url" เป็นลิงก์ออกนอกเว็บ
"use client";

import { ArrowUpRight, MessageCircleQuestion } from "lucide-react";
import type { Action } from "@/types/contract";

interface ActionChipsProps {
  actions: Action[];
  onAsk: (text: string) => void;
  disabled?: boolean;
}

export function ActionChips({ actions, onAsk, disabled = false }: ActionChipsProps) {
  if (actions.length === 0) return null;

  return (
    <ul className="flex flex-wrap gap-2" aria-label="คำถามต่อยอด">
      {actions.map((action, position) => (
        <li key={`${action.label}-${position}`}>
          {action.type === "open_url" && action.payload.url ? (
            <a
              href={action.payload.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 rounded-full border border-deep-navy/15 px-3.5 py-2 text-sm text-deep-navy transition hover:border-copie-teal hover:text-copie-teal"
            >
              {action.label}
              <ArrowUpRight aria-hidden="true" className="size-4" />
            </a>
          ) : (
            <button
              type="button"
              onClick={() => onAsk(action.payload.text ?? action.label)}
              disabled={disabled}
              className="inline-flex items-center gap-1.5 rounded-full border border-deep-navy/15 px-3.5 py-2 text-sm text-deep-navy transition hover:border-copie-teal hover:text-copie-teal disabled:opacity-40"
            >
              <MessageCircleQuestion aria-hidden="true" className="size-4 text-copie-teal" />
              {action.label}
            </button>
          )}
        </li>
      ))}
    </ul>
  );
}
