"use client";

import { useState, type DragEvent, type ReactNode } from "react";
import { Dropdown } from "@heroui/react";
import { ChevronRight, Folder, FolderOpen, MoreHorizontal, Pencil, Trash2 } from "lucide-react";

import type { Project } from "@/types/contract";

import { CHAT_DRAG_TYPE } from "./ConversationItem";
import { InlineNameInput } from "./InlineNameInput";

type ProjectGroupProps = {
  project: Project;
  expanded: boolean;
  count: number;
  onToggle: () => void;
  onRename: (name: string) => void;
  onDelete: () => void;
  onDropChat: (conversationId: string) => void;
  children: ReactNode;
};

// Accepts chats dragged from the history list (desktop) as a shortcut for "move to project".
export function useChatDropTarget(onDropChat: (conversationId: string) => void) {
  const [over, setOver] = useState(false);
  const accepts = (event: DragEvent) => event.dataTransfer.types.includes(CHAT_DRAG_TYPE);
  return {
    over,
    handlers: {
      onDragOver: (event: DragEvent) => {
        if (!accepts(event)) return;
        event.preventDefault();
        event.dataTransfer.dropEffect = "move";
        setOver(true);
      },
      onDragLeave: () => setOver(false),
      onDrop: (event: DragEvent) => {
        setOver(false);
        const id = event.dataTransfer.getData(CHAT_DRAG_TYPE);
        if (id) {
          event.preventDefault();
          onDropChat(id);
        }
      },
    },
  };
}

export function ProjectGroup({ project, expanded, count, onToggle, onRename, onDelete, onDropChat, children }: ProjectGroupProps) {
  const [editing, setEditing] = useState(false);
  const drop = useChatDropTarget(onDropChat);
  const FolderIcon = expanded ? FolderOpen : Folder;

  return (
    <div className="flex flex-col gap-1.5" {...drop.handlers}>
      <div
        className={`group relative flex items-center gap-2 rounded-xl border px-2 py-2 transition-colors ${
          drop.over ? "border-cyber-blue bg-blue-50" : "border-transparent hover:bg-white/70"
        }`}
      >
        {editing ? (
          <>
            <FolderIcon className="size-4 shrink-0 text-cyber-blue" />
            <InlineNameInput
              initial={project.name}
              maxLength={60}
              label="ชื่อโปรเจกต์"
              onSave={(name) => { setEditing(false); onRename(name); }}
              onCancel={() => setEditing(false)}
            />
          </>
        ) : (
          <button
            type="button"
            onClick={onToggle}
            onDoubleClick={() => setEditing(true)}
            aria-expanded={expanded}
            className="flex min-w-0 flex-1 items-center gap-2 text-left cursor-pointer pr-6"
          >
            <ChevronRight className={`size-3.5 shrink-0 text-cyber-subtle transition-transform ${expanded ? "rotate-90" : ""}`} />
            <FolderIcon className="size-4 shrink-0 text-cyber-blue" />
            <span className="truncate font-display text-sm font-bold text-cyber-strong" title={project.name}>{project.name}</span>
            <span className="ml-auto shrink-0 rounded-full bg-blue-50 px-2 py-0.5 text-[10px] font-bold text-cyber-blue">{count}</span>
          </button>
        )}

        {!editing && (
          <Dropdown>
            <Dropdown.Trigger
              aria-label={`ตัวเลือกของโปรเจกต์ ${project.name}`}
              className="absolute right-1 rounded-md p-1 text-cyber-subtle hover:bg-blue-50 hover:text-cyber-strong lg:opacity-0 lg:group-hover:opacity-100 lg:group-focus-within:opacity-100"
            >
              <MoreHorizontal className="size-4" />
            </Dropdown.Trigger>
            <Dropdown.Popover placement="bottom end" className="min-w-48">
              <Dropdown.Menu
                aria-label="ตัวเลือกโปรเจกต์"
                onAction={(key) => {
                  if (key === "rename") setEditing(true);
                  if (key === "delete") onDelete();
                }}
              >
                <Dropdown.Item id="rename" textValue="เปลี่ยนชื่อโปรเจกต์">
                  <Pencil className="size-4" />
                  เปลี่ยนชื่อโปรเจกต์
                </Dropdown.Item>
                <Dropdown.Item id="delete" textValue="ลบโปรเจกต์" variant="danger">
                  <Trash2 className="size-4" />
                  ลบโปรเจกต์
                </Dropdown.Item>
              </Dropdown.Menu>
            </Dropdown.Popover>
          </Dropdown>
        )}
      </div>
      {expanded && (
        <div className="ml-3 flex flex-col gap-1.5 border-l border-cyber-edge/70 pl-2">
          {count === 0 ? (
            <p className="px-2 py-1.5 text-[11px] text-cyber-subtle">ยังไม่มีแชท — ลากแชทมาวาง หรือใช้เมนู “ย้ายไปโปรเจกต์”</p>
          ) : children}
        </div>
      )}
    </div>
  );
}
