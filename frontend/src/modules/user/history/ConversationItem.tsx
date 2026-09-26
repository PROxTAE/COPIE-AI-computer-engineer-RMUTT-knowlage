"use client";

import type { ConversationSummary } from "@/types/contract";

type ConversationItemProps = {
  conversation: ConversationSummary;
  selected: boolean;
  pending: boolean;
  onSelect: () => void;
};

const thaiDate = new Intl.DateTimeFormat("th-TH", {
  dateStyle: "short",
  timeStyle: "short",
  timeZone: "Asia/Bangkok",
});

export function ConversationItem({ conversation, selected, pending, onSelect }: ConversationItemProps) {
  const timestamp = new Date(conversation.updated_at);
  return (
    <button
      type="button"
      onClick={onSelect}
      disabled={pending}
      aria-current={selected ? "true" : undefined}
      className={`w-full rounded-xl border px-3 py-3 text-left transition focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyber-blue ${
        selected
          ? "border-cyber-blue bg-blue-50 text-cyber-blue"
          : "border-transparent bg-white/70 text-cyber-ink hover:border-cyber-line"
      } disabled:cursor-wait disabled:opacity-60`}
    >
      <span className="block truncate text-sm font-semibold">{conversation.title || "บทสนทนาใหม่"}</span>
      <span className="mt-1 block text-xs text-cyber-muted">
        {Number.isNaN(timestamp.getTime()) ? conversation.updated_at : thaiDate.format(timestamp)}
      </span>
    </button>
  );
}
