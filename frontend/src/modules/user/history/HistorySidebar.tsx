"use client";

import { useCallback, useEffect, useState } from "react";
import { FolderPlus, Plus, Search, X } from "lucide-react";

import { ApiError, useChatStore } from "@/modules/core";
import type { ConversationSummary, Project } from "@/types/contract";

import { ConfirmDialog } from "./ConfirmDialog";
import { ConversationItem } from "./ConversationItem";
import { historyApi } from "./historyApi";
import { InlineNameInput } from "./InlineNameInput";
import { ProjectGroup, useChatDropTarget } from "./ProjectGroup";

type HistorySidebarProps = {
  desktopOpen: boolean;
  mobileOpen: boolean;
  onCloseDesktop?: () => void;
  onCloseMobile: () => void;
  refreshKey: string;
};

type PendingDelete = { kind: "chat" | "project"; id: string; name: string };

function errorMessage(error: unknown, fallback = "โหลดประวัติบทสนทนาไม่สำเร็จ กรุณาลองใหม่") {
  return error instanceof ApiError ? error.message : fallback;
}

function isSameDay(d1: Date, d2: Date) {
  return (
    d1.getDate() === d2.getDate() &&
    d1.getMonth() === d2.getMonth() &&
    d1.getFullYear() === d2.getFullYear()
  );
}

const byName = (a: Project, b: Project) => a.name.localeCompare(b.name, "th");

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
  const [projects, setProjects] = useState<Project[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [collapsed, setCollapsed] = useState<ReadonlySet<string>>(() => new Set());
  const [addingProject, setAddingProject] = useState(false);
  const [pendingDelete, setPendingDelete] = useState<PendingDelete | null>(null);
  const [deleting, setDeleting] = useState(false);

  const loadSummaries = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [chats, folders] = await Promise.all([historyApi.list(), historyApi.projects()]);
      setConversations(chats);
      setProjects(folders.toSorted(byName));
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

  // Optimistic edits: update the list right away, reload from the server if the request fails.
  async function attempt(action: () => Promise<unknown>, failure: string) {
    try {
      await action();
    } catch (caught) {
      setError(errorMessage(caught, failure));
      void loadSummaries();
    }
  }

  const patchChat = (id: string, changes: Partial<ConversationSummary>) =>
    setConversations((list) => list.map((item) => (item.id === id ? { ...item, ...changes } : item)));

  const renameChat = (id: string, title: string) => {
    patchChat(id, { title });
    void attempt(() => historyApi.update(id, { title }), "เปลี่ยนชื่อบทสนทนาไม่สำเร็จ");
  };

  const moveChat = (id: string, projectId: string | null) => {
    if (conversations.find((item) => item.id === id)?.project_id === projectId) return;
    patchChat(id, { project_id: projectId });
    if (projectId) setCollapsed((set) => { const next = new Set(set); next.delete(projectId); return next; });
    void attempt(() => historyApi.update(id, { project_id: projectId }), "ย้ายบทสนทนาไม่สำเร็จ");
  };

  const createProject = (name: string) => {
    setAddingProject(false);
    void attempt(async () => {
      const project = await historyApi.createProject({ name });
      setProjects((list) => [...list, project].toSorted(byName));
    }, "สร้างโปรเจกต์ไม่สำเร็จ");
  };

  const renameProject = (id: string, name: string) => {
    setProjects((list) => list.map((item) => (item.id === id ? { ...item, name } : item)).toSorted(byName));
    void attempt(() => historyApi.renameProject(id, { name }), "เปลี่ยนชื่อโปรเจกต์ไม่สำเร็จ");
  };

  const confirmDelete = async () => {
    if (!pendingDelete) return;
    setDeleting(true);
    setError(null);
    const { kind, id } = pendingDelete;
    try {
      if (kind === "chat") {
        await historyApi.remove(id);
        setConversations((list) => list.filter((item) => item.id !== id));
        if (id === conversationId) newConversation();
      } else {
        await historyApi.removeProject(id);
        setProjects((list) => list.filter((item) => item.id !== id));
        setConversations((list) => list.map((item) => (item.project_id === id ? { ...item, project_id: null } : item)));
      }
      setPendingDelete(null);
    } catch (caught) {
      setError(errorMessage(caught, "ลบไม่สำเร็จ กรุณาลองใหม่"));
      setPendingDelete(null);
    } finally {
      setDeleting(false);
    }
  };

  const selectConversation = async (id: string) => {
    if (pendingId) return;
    setPendingId(id);
    setError(null);
    try {
      loadConversation(await historyApi.detail(id));
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

  const ungroupedDrop = useChatDropTarget((id) => moveChat(id, null));

  const query = searchQuery.trim().toLowerCase();
  const matches = (item: ConversationSummary) =>
    !query ||
    (item.title || "").toLowerCase().includes(query) ||
    (item.last_message || "").toLowerCase().includes(query);
  const filtered = conversations.filter(matches);
  const projectIds = new Set(projects.map((project) => project.id));
  const inProject = (item: ConversationSummary) => Boolean(item.project_id && projectIds.has(item.project_id));
  const ungrouped = filtered.filter((item) => !inProject(item));
  const visibleProjects = projects.filter(
    (project) => !query || project.name.toLowerCase().includes(query) || filtered.some((item) => item.project_id === project.id),
  );

  const now = new Date();
  const todayChats = ungrouped.filter((item) => {
    const d = new Date(item.updated_at);
    return !Number.isNaN(d.getTime()) && isSameDay(d, now);
  });
  const earlierChats = ungrouped.filter((item) => {
    const d = new Date(item.updated_at);
    return Number.isNaN(d.getTime()) || !isSameDay(d, now);
  });

  const renderItem = (item: ConversationSummary) => (
    <ConversationItem
      key={item.id}
      conversation={item}
      projects={projects}
      selected={item.id === conversationId}
      pending={pendingId !== null}
      onSelect={() => { void selectConversation(item.id); }}
      onRename={(title) => renameChat(item.id, title)}
      onMove={(projectId) => moveChat(item.id, projectId)}
      onDelete={() => setPendingDelete({ kind: "chat", id: item.id, name: item.title || "บทสนทนาใหม่" })}
    />
  );

  const renderContent = (isMobile = false) => (
    <div className="flex h-full flex-col gap-4">
      {/* Drawer Top Header with Wordmark and Close button */}
      <div className="flex items-center justify-between border-b border-cyber-edge/60 pb-3">
        <div className="flex items-center gap-3">
          <span className="copie-wordmark text-2xl font-black text-cyber-strong tracking-tighter">
            COPIE
          </span>
          <span className="border-l border-cyber-blue pl-3 font-label text-[9px] font-bold uppercase leading-tight tracking-[0.14em] text-cyber-subtle">
            AI ASSISTANT<br />FOR YOUR IDEAS
          </span>
        </div>
        <button
          type="button"
          onClick={isMobile ? onCloseMobile : onCloseDesktop}
          className="flex size-8 items-center justify-center rounded-full text-cyber-subtle hover:bg-slate-100 hover:text-cyber-strong transition-colors cursor-pointer"
          aria-label="ปิดประวัติ"
        >
          <X className="size-5 text-cyber-blue" />
        </button>
      </div>

      <h2 className="font-display text-2xl font-black text-cyber-strong">ประวัติการสนทนา</h2>

      <button
        type="button"
        onClick={startNewConversation}
        className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyber-blue-deep to-cyber-blue px-4 py-3 font-display text-sm font-bold text-cyber-on-accent shadow-[0_4px_14px_rgb(var(--copie-accent-rgb)/0.25)] hover:shadow-[0_6px_20px_rgb(var(--copie-accent-rgb)/0.35)] transition-all cursor-pointer"
      >
        <Plus className="size-4.5 stroke-[2.5]" />
        <span>สนทนาใหม่</span>
      </button>

      <div className="relative flex items-center">
        <Search className="absolute left-3.5 size-4 text-cyber-subtle" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="ค้นหาบทสนทนา"
          aria-label="ค้นหาบทสนทนา"
          className="w-full rounded-xl border border-cyber-edge bg-white py-2.5 pl-10 pr-4 font-sans text-sm text-cyber-strong outline-none placeholder:text-cyber-subtle focus:border-cyber-blue focus:ring-2 focus:ring-cyber-blue/15 transition-all shadow-xs"
        />
        {searchQuery.length > 0 && (
          <button
            type="button"
            onClick={() => setSearchQuery("")}
            aria-label="ล้างคำค้นหา"
            className="absolute right-3 text-cyber-subtle hover:text-cyber-strong"
          >
            <X className="size-3.5" />
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto pr-1 copie-scroll flex flex-col gap-4">
        {loading && <p className="text-center text-xs text-cyber-subtle py-4" role="status">กำลังโหลดประวัติ...</p>}
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-xs text-red-700" role="alert">
            <p>{error}</p>
            <button type="button" className="mt-1 font-semibold underline cursor-pointer" onClick={() => { void loadSummaries(); }}>
              ลองอีกครั้ง
            </button>
          </div>
        )}

        {/* Projects */}
        {!loading && (
          <section className="flex flex-col gap-1.5" aria-label="โปรเจกต์">
            <div className="flex items-center justify-between px-1">
              <span className="font-display text-xs font-bold text-cyber-subtle">โปรเจกต์</span>
              <button
                type="button"
                onClick={() => setAddingProject(true)}
                className="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-[11px] font-bold text-cyber-blue hover:bg-blue-50 cursor-pointer"
              >
                <FolderPlus className="size-3.5" />
                โปรเจกต์ใหม่
              </button>
            </div>
            {addingProject && (
              <div className="px-1">
                <InlineNameInput
                  maxLength={60}
                  label="ชื่อโปรเจกต์ใหม่"
                  placeholder="เช่น เตรียมสอบปี 2, สายงาน AI"
                  onSave={createProject}
                  onCancel={() => setAddingProject(false)}
                />
              </div>
            )}
            {projects.length === 0 && !addingProject && (
              <p className="rounded-xl border border-dashed border-cyber-edge px-3 py-2.5 text-[11px] text-cyber-subtle">
                จัดแชทที่เกี่ยวข้องไว้ด้วยกันเป็นโปรเจกต์ได้ เช่น “วางแผนเรียน” หรือ “ฝึกเขียนโค้ด”
              </p>
            )}
            {visibleProjects.map((project) => {
              const chats = filtered.filter((item) => item.project_id === project.id);
              return (
                <ProjectGroup
                  key={project.id}
                  project={project}
                  count={chats.length}
                  expanded={Boolean(query) || !collapsed.has(project.id)}
                  onToggle={() => setCollapsed((set) => {
                    const next = new Set(set);
                    if (next.has(project.id)) next.delete(project.id);
                    else next.add(project.id);
                    return next;
                  })}
                  onRename={(name) => renameProject(project.id, name)}
                  onDelete={() => setPendingDelete({ kind: "project", id: project.id, name: project.name })}
                  onDropChat={(id) => moveChat(id, project.id)}
                >
                  {chats.map(renderItem)}
                </ProjectGroup>
              );
            })}
          </section>
        )}

        {/* Chats outside any project (also a drop target to take a chat out of its project) */}
        <div
          {...ungroupedDrop.handlers}
          className={`flex flex-col gap-4 rounded-xl transition-colors ${ungroupedDrop.over ? "bg-blue-50/70 outline-2 outline-dashed outline-cyber-blue/50" : ""}`}
        >
          {!loading && !error && ungrouped.length === 0 && (
            <p className="rounded-xl border border-dashed border-cyber-edge p-6 text-center text-xs text-cyber-subtle">
              {query ? "ไม่พบบทสนทนาที่ค้นหา" : conversations.length ? "ทุกแชทอยู่ในโปรเจกต์แล้ว" : "ยังไม่มีประวัติบทสนทนา"}
            </p>
          )}
          {todayChats.length > 0 && (
            <div className="flex flex-col gap-1.5">
              <span className="font-display text-xs font-bold text-cyber-subtle px-1">วันนี้</span>
              <div className="flex flex-col gap-1.5">{todayChats.map(renderItem)}</div>
            </div>
          )}
          {earlierChats.length > 0 && (
            <div className="flex flex-col gap-1.5">
              <span className="font-display text-xs font-bold text-cyber-subtle px-1">ก่อนหน้านี้</span>
              <div className="flex flex-col gap-1.5">{earlierChats.map(renderItem)}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <>
      {desktopOpen && (
        <aside className="relative z-40 hidden h-full w-84 max-w-[340px] shrink-0 flex-col overflow-hidden border-r border-cyber-edge bg-white p-5 shadow-lg lg:flex">
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
          <aside className="relative flex h-full w-[min(88vw,340px)] flex-col overflow-hidden border-r border-cyber-edge bg-white p-5 shadow-2xl">
            {renderContent(true)}
          </aside>
        </div>
      )}
      <ConfirmDialog
        open={pendingDelete !== null}
        pending={deleting}
        title={pendingDelete?.kind === "project" ? "ลบโปรเจกต์นี้?" : "ลบบทสนทนานี้?"}
        description={
          pendingDelete?.kind === "project"
            ? `ลบโปรเจกต์ “${pendingDelete.name}” — แชทข้างในจะไม่ถูกลบ แต่จะย้ายออกมาอยู่นอกโปรเจกต์`
            : `ลบ “${pendingDelete?.name ?? ""}” และข้อความทั้งหมดในแชทนี้ถาวร กู้คืนไม่ได้`
        }
        confirmLabel={pendingDelete?.kind === "project" ? "ลบโปรเจกต์" : "ลบบทสนทนา"}
        onConfirm={() => { void confirmDelete(); }}
        onCancel={() => setPendingDelete(null)}
      />
    </>
  );
}
