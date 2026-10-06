"use client";

import { useState } from "react";
import { Dropdown } from "@heroui/react";
import { FolderInput, FolderMinus, MessageSquare, MoreVertical, Pencil, Trash2 } from "lucide-react";

import type { ConversationSummary, Project } from "@/types/contract";

import { InlineNameInput } from "./InlineNameInput";

export const CHAT_DRAG_TYPE = "application/x-copie-chat";

type ConversationItemProps = {
  conversation: ConversationSummary;
  projects: Project[];
  selected: boolean;
  pending: boolean;
  onSelect: () => void;
  onRename: (title: string) => void;
  onMove: (projectId: string | null) => void;
  onDelete: () => void;
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

export function ConversationItem({
  conversation,
  projects,
  selected,
  pending,
  onSelect,
  onRename,
  onMove,
  onDelete,
}: ConversationItemProps) {
  const [editing, setEditing] = useState(false);
  const title = conversation.title || "บทสนทนาใหม่";
  const targets = projects.filter((project) => project.id !== conversation.project_id);

  return (
    <div
      draggable={!editing}
      onDragStart={(event) => {
        event.dataTransfer.setData(CHAT_DRAG_TYPE, conversation.id);
        event.dataTransfer.effectAllowed = "move";
      }}
      className={`group relative flex w-full items-start gap-3 rounded-xl border p-3 transition-all ${
        selected
          ? "border-cyber-blue bg-blue-50/80 shadow-xs"
          : "border-transparent bg-white/60 hover:border-cyber-edge hover:bg-white"
      } ${pending ? "opacity-60" : ""}`}
    >
      <div className="flex size-8 items-center justify-center rounded-lg bg-blue-50 text-cyber-blue shrink-0 mt-0.5">
        <MessageSquare className="size-4" />
      </div>

      <div className="min-w-0 flex-1 pr-6">
        {editing ? (
          <InlineNameInput
            initial={conversation.title}
            maxLength={80}
            label="ชื่อบทสนทนา"
            onSave={(value) => { setEditing(false); onRename(value); }}
            onCancel={() => setEditing(false)}
          />
        ) : (
          <button
            type="button"
            onClick={onSelect}
            onDoubleClick={() => setEditing(true)}
            disabled={pending}
            aria-current={selected ? "true" : undefined}
            className="block w-full text-left cursor-pointer disabled:cursor-wait after:absolute after:inset-0 after:rounded-xl"
          >
            <span className="flex items-center justify-between gap-1">
              <span className="truncate font-display text-sm font-bold text-cyber-strong" title={title}>{title}</span>
              <span className="shrink-0 text-[11px] font-medium text-cyber-subtle">{formatChatTime(conversation.updated_at)}</span>
            </span>
            <span className="mt-0.5 block truncate text-xs text-cyber-subtle font-medium">
              {conversation.last_message || "คลิกเพื่อดูรายละเอียดบทสนทนา..."}
            </span>
          </button>
        )}
      </div>

      {!editing && (
        <Dropdown>
          <Dropdown.Trigger
            aria-label={`ตัวเลือกของ ${title}`}
            className="absolute right-1.5 top-2.5 z-10 rounded-md p-1 text-cyber-subtle opacity-100 transition-opacity hover:bg-blue-50 hover:text-cyber-strong data-[pressed=true]:opacity-100 lg:opacity-0 lg:group-hover:opacity-100 lg:group-focus-within:opacity-100"
          >
            <MoreVertical className="size-4" />
          </Dropdown.Trigger>
          <Dropdown.Popover placement="bottom end" className="min-w-52">
            <Dropdown.Menu
              aria-label="ตัวเลือกบทสนทนา"
              onAction={(key) => {
                if (key === "rename") setEditing(true);
                else if (key === "delete") onDelete();
                else if (key === "ungroup") onMove(null);
              }}
            >
              <Dropdown.Item id="rename" textValue="เปลี่ยนชื่อ">
                <Pencil className="size-4" />
                เปลี่ยนชื่อ
              </Dropdown.Item>
              {targets.length > 0 ? (
                <Dropdown.SubmenuTrigger>
                  <Dropdown.Item id="move" textValue="ย้ายไปโปรเจกต์">
                    <FolderInput className="size-4" />
                    ย้ายไปโปรเจกต์
                    <Dropdown.SubmenuIndicator />
                  </Dropdown.Item>
                  <Dropdown.Popover className="min-w-48">
                    <Dropdown.Menu aria-label="เลือกโปรเจกต์" onAction={(key) => onMove(String(key))}>
                      {targets.map((project) => (
                        <Dropdown.Item key={project.id} id={project.id} textValue={project.name}>
                          {project.name}
                        </Dropdown.Item>
                      ))}
                    </Dropdown.Menu>
                  </Dropdown.Popover>
                </Dropdown.SubmenuTrigger>
              ) : null}
              {conversation.project_id ? (
                <Dropdown.Item id="ungroup" textValue="นำออกจากโปรเจกต์">
                  <FolderMinus className="size-4" />
                  นำออกจากโปรเจกต์
                </Dropdown.Item>
              ) : null}
              <Dropdown.Item id="delete" textValue="ลบบทสนทนา" variant="danger">
                <Trash2 className="size-4" />
                ลบบทสนทนา
              </Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown.Popover>
        </Dropdown>
      )}
    </div>
  );
}
