"use client";

import { useCallback, useEffect, useState } from "react";
import { Plus, Search, X } from "lucide-react";

import { api, ApiError, useChatStore } from "@/modules/core";
import type { ConversationDetail, ConversationSummary } from "@/types/contract";

import { ConversationItem } from "./ConversationItem";

type HistorySidebarProps = {
  desktopOpen: boolean;
  mobileOpen: boolean;
  onCloseDesktop?: () => void;
  onCloseMobile: () => void;
  refreshKey: string;
};

function errorMessage(error: unknown) {
  return error instanceof ApiError ? error.message : "โหลดประวัติบทสนทนาไม่สำเร็จ กรุณาลองใหม่";
}

function isSameDay(d1: Date, d2: Date) {
  return (
    d1.getDate() === d2.getDate() &&
    d1.getMonth() === d2.getMonth() &&
    d1.getFullYear() === d2.getFullYear()
  );
}

export function HistorySidebar({
  desktopOpen,
  mobileOpen,
  onCloseDesktop,
  onCloseMobile,
  refreshKey,
}: HistorySidebarProps) {
  const conversationId = useChatStore((state) => state.conversationId);
  const loadConversation = useChatStore((state) => state.loadConversation);
  const newConversation = useChatStore((state) => state.newConversation);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
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

  const filteredConversations = conversations.filter((item) =>
    (item.title || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
    (item.last_message || "").toLowerCase().includes(searchQuery.toLowerCase())
  );

  const now = new Date();
  const todayChats = filteredConversations.filter((item) => {
    const d = new Date(item.updated_at);
    return !Number.isNaN(d.getTime()) && isSameDay(d, now);
  });
  const earlierChats = filteredConversations.filter((item) => {
    const d = new Date(item.updated_at);
    return Number.isNaN(d.getTime()) || !isSameDay(d, now);
  });

  const renderContent = (isMobile = false) => (
    <div className="flex h-full flex-col gap-4">
      {/* Drawer Top Header with Wordmark and Close button */}
      <div className="flex items-center justify-between border-b border-[#d2e0f5]/60 pb-3">
        <div className="flex items-center gap-3">
          <span className="copie-wordmark text-2xl font-black text-[#080b12] tracking-tighter">
            COPIE
          </span>
          <span className="border-l border-[#155ff2] pl-3 font-label text-[9px] font-bold uppercase leading-tight tracking-[0.14em] text-[#6b82a6]">
            AI ASSISTANT<br />FOR YOUR IDEAS
          </span>
        </div>
        <button
          type="button"
          onClick={isMobile ? onCloseMobile : onCloseDesktop}
          className="flex size-8 items-center justify-center rounded-full text-[#6b82a6] hover:bg-slate-100 hover:text-[#080b12] transition-colors cursor-pointer"
          aria-label="ปิดประวัติ"
        >
          <X className="size-5 text-[#155ff2]" />
        </button>
      </div>

      {/* Title */}
      <div>
        <h2 className="font-display text-2xl font-black text-[#080b12]">
          ประวัติการสนทนา
        </h2>
      </div>

      {/* New Chat Primary CTA Button */}
      <button
        type="button"
        onClick={startNewConversation}
        className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[#0f5ff0] to-[#155ff2] px-4 py-3 font-display text-sm font-bold text-white shadow-[0_4px_14px_rgba(21,95,242,0.25)] hover:shadow-[0_6px_20px_rgba(21,95,242,0.35)] transition-all cursor-pointer"
      >
        <Plus className="size-4.5 stroke-[2.5]" />
        <span>สนทนาใหม่</span>
      </button>

      {/* Search Input matching Mockup 06 */}
      <div className="relative flex items-center">
        <Search className="absolute left-3.5 size-4 text-[#6b82a6]" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="ค้นหาบทสนทนา"
          className="w-full rounded-xl border border-[#d2e0f5] bg-white py-2.5 pl-10 pr-4 font-sans text-sm text-[#080b12] outline-none placeholder:text-[#6b82a6] focus:border-[#155ff2] focus:ring-2 focus:ring-[#155ff2]/15 transition-all shadow-xs"
        />
        {searchQuery.length > 0 && (
          <button
            type="button"
            onClick={() => setSearchQuery("")}
            className="absolute right-3 text-[#6b82a6] hover:text-[#080b12]"
          >
            <X className="size-3.5" />
          </button>
        )}
      </div>

      {/* Conversations List with Groups */}
      <div className="flex-1 overflow-y-auto pr-1 copie-scroll flex flex-col gap-4">
        {loading && <p className="text-center text-xs text-[#6b82a6] py-4" role="status">กำลังโหลดประวัติ...</p>}
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-xs text-red-700" role="alert">
            <p>{error}</p>
            <button type="button" className="mt-1 font-semibold underline cursor-pointer" onClick={() => { void loadSummaries(); }}>
              ลองอีกครั้ง
            </button>
          </div>
        )}
        {!loading && !error && filteredConversations.length === 0 && (
          <p className="rounded-xl border border-dashed border-[#d2e0f5] p-6 text-center text-xs text-[#6b82a6]">
            {searchQuery ? "ไม่พบบทสนทนาที่ค้นหา" : "ยังไม่มีประวัติบทสนทนา"}
          </p>
        )}

        {/* Group: วันนี้ */}
        {todayChats.length > 0 && (
          <div className="flex flex-col gap-1.5">
            <span className="font-display text-xs font-bold text-[#6b82a6] px-1">
              วันนี้
            </span>
            <div className="flex flex-col gap-1.5">
              {todayChats.map((item) => (
                <ConversationItem
                  key={item.id}
                  conversation={item}
                  selected={item.id === conversationId}
                  pending={pendingId !== null}
                  onSelect={() => { void selectConversation(item.id); }}
                />
              ))}
            </div>
          </div>
        )}

        {/* Group: ก่อนหน้านี้ */}
        {earlierChats.length > 0 && (
          <div className="flex flex-col gap-1.5">
            <span className="font-display text-xs font-bold text-[#6b82a6] px-1">
              ก่อนหน้านี้
            </span>
            <div className="flex flex-col gap-1.5">
              {earlierChats.map((item) => (
                <ConversationItem
                  key={item.id}
                  conversation={item}
                  selected={item.id === conversationId}
                  pending={pendingId !== null}
                  onSelect={() => { void selectConversation(item.id); }}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <>
      {desktopOpen && (
        <aside className="relative z-40 hidden h-dvh w-84 max-w-[340px] shrink-0 flex-col overflow-hidden border-r border-[#d2e0f5] bg-white p-5 shadow-lg lg:flex">
          {renderContent(false)}
        </aside>
      )}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden" role="dialog" aria-modal="true" aria-label="ประวัติบทสนทนา">
          <button
            type="button"
            className="absolute inset-0 bg-slate-950/40 backdrop-blur-xs"
            aria-label="ปิดประวัติ"
            onClick={onCloseMobile}
          />
          <aside className="relative flex h-full w-[min(88vw,340px)] flex-col overflow-hidden border-r border-[#d2e0f5] bg-white p-5 shadow-2xl">
            {renderContent(true)}
          </aside>
        </div>
      )}
    </>
  );
}
