"use client";

import { MessageSquare, MoreVertical } from "lucide-react";
import type { ConversationSummary } from "@/types/contract";

type ConversationItemProps = {
  conversation: ConversationSummary;
  selected: boolean;
  pending: boolean;
  onSelect: () => void;
};

function formatChatTime(dateStr: string): string {
  const date = new Date(dateStr);
  if (Number.isNaN(date.getTime())) return dateStr;
  const now = new Date();
  const isToday =
    date.getDate() === now.getDate() &&
    date.getMonth() === now.getMonth() &&
    date.getFullYear() === now.getFullYear();

  if (isToday) {
    return date.toLocaleTimeString("th-TH", { hour: "2-digit", minute: "2-digit", hour12: false });
  }
  return date.toLocaleDateString("th-TH", { day: "numeric", month: "short", year: "2-digit" });
}

export function ConversationItem({ conversation, selected, pending, onSelect }: ConversationItemProps) {
  const timeFormatted = formatChatTime(conversation.updated_at);

  return (
    <div
      onClick={onSelect}
      className={`group relative flex w-full items-start gap-3 rounded-xl border p-3 text-left transition-all cursor-pointer ${
        selected
          ? "border-[#155ff2] bg-blue-50/80 shadow-xs"
          : "border-transparent bg-white/60 hover:border-[#d2e0f5] hover:bg-white"
      } ${pending ? "opacity-60 cursor-wait" : ""}`}
    >
      {/* Icon */}
      <div className="flex size-8 items-center justify-center rounded-lg bg-blue-50 text-[#155ff2] shrink-0 mt-0.5">
        <MessageSquare className="size-4" />
      </div>

      {/* Title & Preview */}
      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-1">
          <span className="truncate font-display text-sm font-bold text-[#080b12]">
            {conversation.title || "บทสนทนาใหม่"}
          </span>
          <span className="shrink-0 text-[11px] font-medium text-[#6b82a6]">{timeFormatted}</span>
        </div>
        <p className="mt-0.5 truncate text-xs text-[#6b82a6] font-medium">
          {conversation.last_message || "คลิกเพื่อดูรายละเอียดบทสนทนา..."}
        </p>
      </div>

      {/* Menu Dots */}
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
        }}
        className="opacity-0 group-hover:opacity-100 p-1 text-[#6b82a6] hover:text-[#080b12] rounded transition-opacity"
        aria-label="ตัวเลือกบทสนทนา"
      >
        <MoreVertical className="size-3.5" />
      </button>
    </div>
  );
}
