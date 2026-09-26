"use client";

import { useCallback, useEffect, useState } from "react";
import { Button } from "@heroui/react";

import { api, ApiError, Icon, useChatStore } from "@/modules/core";
import type { ConversationDetail, ConversationSummary } from "@/types/contract";

import { ConversationItem } from "./ConversationItem";

type HistorySidebarProps = {
  desktopOpen: boolean;
  mobileOpen: boolean;
  onCloseMobile: () => void;
  refreshKey: string;
};

function errorMessage(error: unknown) {
  return error instanceof ApiError ? error.message : "โหลดประวัติบทสนทนาไม่สำเร็จ กรุณาลองใหม่";
}

export function HistorySidebar({ desktopOpen, mobileOpen, onCloseMobile, refreshKey }: HistorySidebarProps) {
  const conversationId = useChatStore((state) => state.conversationId);
  const loadConversation = useChatStore((state) => state.loadConversation);
  const newConversation = useChatStore((state) => state.newConversation);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadSummaries = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setConversations(await api<ConversationSummary[]>("/api/conversations"));
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => { void loadSummaries(); }, 0);
    return () => window.clearTimeout(timer);
  }, [loadSummaries, refreshKey]);

  const selectConversation = async (id: string) => {
    if (pendingId) return;
    setPendingId(id);
    setError(null);
    try {
      const detail = await api<ConversationDetail>(`/api/conversations/${encodeURIComponent(id)}`);
      loadConversation(detail);
      onCloseMobile();
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setPendingId(null);
    }
  };

  const startNewConversation = () => {
    newConversation();
    onCloseMobile();
  };

  const content = (
    <>
      <div className="flex items-center justify-between gap-3">
        <div>
          <span className="copie-eyebrow">HISTORY</span>
          <h2 className="mt-1 font-display text-lg font-semibold text-cyber-ink">บทสนทนา</h2>
        </div>
        <Button isIconOnly variant="outline" aria-label="โหลดประวัติใหม่" onPress={() => { void loadSummaries(); }}>
          <Icon name="refresh" size={17} />
        </Button>
      </div>
      <Button variant="primary" className="w-full" onPress={startNewConversation}>
        + New Chat
      </Button>
      {loading && <p className="text-sm text-cyber-muted" role="status">กำลังโหลดประวัติ...</p>}
      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700" role="alert">
          <p>{error}</p>
          <button type="button" className="mt-2 font-semibold underline" onClick={() => { void loadSummaries(); }}>ลองอีกครั้ง</button>
        </div>
      )}
      {!loading && !error && conversations.length === 0 && (
        <p className="rounded-xl border border-dashed border-cyber-line p-4 text-center text-sm text-cyber-muted">
          ยังไม่มีประวัติบทสนทนา
        </p>
      )}
      <div className="flex min-h-0 flex-1 flex-col gap-2 overflow-y-auto" aria-label="รายการบทสนทนา">
        {conversations.map((item) => (
          <ConversationItem
            key={item.id}
            conversation={item}
            selected={item.id === conversationId}
            pending={pendingId !== null}
            onSelect={() => { void selectConversation(item.id); }}
          />
        ))}
      </div>
    </>
  );

  return (
    <>
      {desktopOpen && (
        <aside className="copie-ui hidden h-dvh w-72 shrink-0 flex-col gap-4 overflow-hidden border-r border-cyber-line !bg-cyber-paper p-5 before:!hidden after:!hidden lg:flex">
          {content}
        </aside>
      )}
      {mobileOpen && (
        <div className="copie-ui fixed inset-0 z-50 lg:hidden" role="dialog" aria-modal="true" aria-label="ประวัติบทสนทนา">
          <button type="button" className="absolute inset-0 bg-slate-950/35" aria-label="ปิดประวัติ" onClick={onCloseMobile} />
          <aside className="relative flex h-full w-[min(86vw,320px)] flex-col gap-4 overflow-hidden border-r border-cyber-line bg-cyber-paper p-5 shadow-2xl">
            <div className="flex justify-end">
              <Button isIconOnly variant="outline" aria-label="ปิด" onPress={onCloseMobile}>×</Button>
            </div>
            {content}
          </aside>
        </div>
      )}
    </>
  );
}
