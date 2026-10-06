"use client";

import { useEffect, useLayoutEffect, useRef, useSyncExternalStore, type ReactNode } from "react";
import { flushSync } from "react-dom";
import { Button } from "@heroui/react";
import { AnimatePresence } from "motion/react";

import { COPIE_STATES, INTERACTION_MODES, MascotDock, MascotModeProvider } from "@/modules/mascot";
import { SuggestedPrompts } from "@/modules/suggest";
import type { ChatMessage, InteractionMode, UserType } from "@/types/contract";

import { getApiAuthSnapshot, subscribeApiAuth } from "../api";
import { layoutFromResponse, useChatStore, type WorkspaceMode } from "../chatStore";
import { AppHeader, ChatInput, CyberHudFrame, HistoryButton, MODE_INFO, ModeSwitcher, type ModeOrigin } from "../ui";
import { MessageList } from "./MessageList";
import { WorkspaceLayout } from "./WorkspaceLayout";

type ChatPageProps = {
  debug?: boolean;
  userType?: UserType | null;
  studyYear?: number | null;
  displayName?: string | null;
  profileControl?: ReactNode;
  onOpenHistory?: () => void;
  renderAssistantFooter?: (message: Extract<ChatMessage, { role: "assistant" }>) => ReactNode;
};
const MODES: WorkspaceMode[] = ["center", "split", "rail", "hidden"];

// The mascot sidebar only exists from the lg breakpoint (WorkspaceLayout); below it the dock stands in.
const DESKTOP_QUERY = "(min-width: 1024px)";
function subscribeDesktop(listener: () => void) {
  const query = window.matchMedia(DESKTOP_QUERY);
  query.addEventListener("change", listener);
  return () => query.removeEventListener("change", listener);
}
const isDesktopSnapshot = () => window.matchMedia(DESKTOP_QUERY).matches;

// The new theme grows as a circle from the mode button (View Transitions API where supported).
function switchModeWithReveal(apply: () => void, origin: ModeOrigin) {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce || document.hidden || typeof document.startViewTransition !== "function") {
    apply();
    return;
  }
  const root = document.documentElement.style;
  const radius = Math.hypot(Math.max(origin.x, window.innerWidth - origin.x), Math.max(origin.y, window.innerHeight - origin.y));
  root.setProperty("--copie-reveal-x", `${origin.x}px`);
  root.setProperty("--copie-reveal-y", `${origin.y}px`);
  root.setProperty("--copie-reveal-r", `${Math.ceil(radius)}px`);
  const transition = document.startViewTransition(() => flushSync(apply));
  // The browser may skip the animation (e.g. the tab is not rendered); the mode still applies.
  transition.ready.catch(() => {});
  transition.finished.catch(() => {});
}

export function ChatPage({
  debug = false,
  userType,
  studyYear,
  displayName,
  profileControl,
  onOpenHistory,
  renderAssistantFooter,
}: ChatPageProps) {
  const canChat = useSyncExternalStore(subscribeApiAuth, getApiAuthSnapshot, () => false);
  const isDesktop = useSyncExternalStore(subscribeDesktop, isDesktopSnapshot, () => true);
  const messages = useChatStore((state) => state.messages);
  const liveMessageId = useChatStore((state) => state.liveMessageId);
  const layout = useChatStore((state) => state.layout);
  const lastVisibleLayout = useChatStore((state) => state.lastVisibleLayout);
  const copieState = useChatStore((state) => state.copieState);
  const interactionMode = useChatStore((state) => state.interactionMode);
  const interactionModeReady = useChatStore((state) => state.interactionModeReady);
  const setInteractionMode = useChatStore((state) => state.setInteractionMode);
  const restoreInteractionMode = useChatStore((state) => state.restoreInteractionMode);
  const pending = useChatStore((state) => state.pending);
  const error = useChatStore((state) => state.error);
  const setLayout = useChatStore((state) => state.setLayout);
  const setCopieState = useChatStore((state) => state.setCopieState);
  const newConversation = useChatStore((state) => state.newConversation);
  const send = useChatStore((state) => state.send);
  const submitAssessment = useChatStore((state) => state.submitAssessment);
  const wasAuthenticated = useRef(false);
  const hasResponse = messages.some((message) => message.role === "assistant");
  const lastAssistant = messages.findLast((message) => message.role === "assistant");
  const isInteractive = lastAssistant?.role === "assistant" && (
    lastAssistant.response.response_type === "skill_radar" || 
    lastAssistant.response.response_type === "assessment_form"
  );
  // The input stays available beside every answer (skill radar included) so the chat can go on in
  // place; it is only hidden while an assessment form is still waiting for its answers.
  const formPending = lastAssistant?.role === "assistant" && lastAssistant.response.response_type === "assessment_form";
  const showComposer = layout === "center" || !formPending;
  const followUpAfterRadar = lastAssistant?.role === "assistant" && lastAssistant.response.response_type === "skill_radar";
  const responseLayout = lastAssistant?.role === "assistant"
    ? layoutFromResponse(lastAssistant.response)
    : lastVisibleLayout;
  // Mini COPIE replaces the full mascot whenever it is hidden, or on small screens while reading an answer.
  const showDock = layout === "hidden" || (layout !== "center" && !isDesktop);
  const restoreMascot = () => setLayout(isDesktop ? lastVisibleLayout : "center");

  const getMascotQuote = () => {
    if (!lastAssistant || lastAssistant.role !== "assistant") return "“พร้อมช่วยค้นหา เรียนรู้ และเติบโตไปด้วยกัน”";
    switch (lastAssistant.response.response_type) {
      case "skill_radar":
        return "“ไอเดียของคุณ ไปได้ไกลกว่าเดิมเสมอ”";
      case "assessment_form":
        return "“ค่อย ๆ ตอบไปทีละข้อ เราอยู่ข้างคุณเสมอ”";
      case "course_table":
      case "cards":
        return "“แตะรายวิชาเพื่อดูรายละเอียด”";
      default:
        return "“พร้อมช่วยค้นหา เรียนรู้ และเติบโตไปด้วยกัน”";
    }
  };

  // Restore the saved mode before the first paint, so COPIE does not play the mode-switch
  // animation on page load (the page renders nothing until the mode is known).
  useLayoutEffect(() => {
    restoreInteractionMode();
  }, [restoreInteractionMode]);

  // Mirror the mode on <html> so portals (history drawer, dialogs) and the page background follow it.
  useLayoutEffect(() => {
    document.documentElement.dataset.copieMode = interactionMode;
  }, [interactionMode]);
  useEffect(() => () => { delete document.documentElement.dataset.copieMode; }, []);

  const changeMode = (mode: InteractionMode, origin: ModeOrigin) =>
    switchModeWithReveal(() => setInteractionMode(mode), origin);

  useEffect(() => {
    if (wasAuthenticated.current && !canChat) newConversation();
    wasAuthenticated.current = canChat;
  }, [canChat, newConversation]);

  if (!interactionModeReady) return null;

  return (
    <MascotModeProvider value={interactionMode}>
      <main className="copie-ui flex h-dvh min-h-0 flex-col relative overflow-hidden" data-copie-mode={interactionMode}>
        <CyberHudFrame />
        <div className="copie-floor" aria-hidden="true" />
        <div data-dock-guard="top" className="relative z-30">
          <AppHeader
            profile={profileControl}
            historyAction={
              <div className="sm:hidden">
                <HistoryButton onPress={onOpenHistory} isDisabled={!onOpenHistory} compact />
              </div>
            }
            modeControl={<ModeSwitcher value={interactionMode} onChange={changeMode} />}
            status={isInteractive ? (lastAssistant.response.response_type === "skill_radar" ? "AI // SKILL RADAR" : "AI // ASSESSMENT") : MODE_INFO[interactionMode].status}
          />
        </div>
        <WorkspaceLayout
          layout={layout}
          copieState={copieState}
          interactionMode={interactionMode}
          hasResponse={hasResponse}
          isInteractive={isInteractive}
          mascotQuote={getMascotQuote()}
          onAsk={canChat ? (text) => { void send(text); } : undefined}
          onHide={() => setLayout("hidden")}
          onShow={() => setLayout(lastVisibleLayout)}
          onBack={() => setLayout("center")}
          onRead={() => setLayout(responseLayout)}
          onNewChat={newConversation}
        >
          <MessageList
            messages={messages}
            liveMessageId={liveMessageId}
            disabled={pending || !canChat}
            onAsk={canChat ? (text) => { void send(text); } : undefined}
            onSubmitAssessment={canChat ? submitAssessment : undefined}
            onBack={() => setLayout("center")}
            renderAssistantFooter={renderAssistantFooter}
          />
        </WorkspaceLayout>
        {pending && <p className="relative z-20 px-5 text-center text-sm text-cyber-blue font-medium" role="status">COPIE กำลังค้นหาคำตอบ...</p>}
        {error && <p className="relative z-20 px-5 text-center text-sm text-red-700 font-medium" role="alert">{error}</p>}
        {debug && (
          <div className="relative z-20 mx-auto flex max-w-6xl flex-wrap items-center justify-center gap-2 px-5 pb-3" aria-label="เครื่องมือทดสอบ layout">
            <span className="font-label text-xs text-cyber-muted">DEV ONLY</span>
            {MODES.map((mode) => (
              <Button key={mode} size="sm" variant={layout === mode ? "primary" : "outline"} onPress={() => setLayout(mode)}>{mode}</Button>
            ))}
            {INTERACTION_MODES.map((mode) => (
              <Button key={mode} size="sm" variant={interactionMode === mode ? "primary" : "outline"} onPress={() => setInteractionMode(mode)}>{mode}</Button>
            ))}
            {COPIE_STATES.map((state) => (
              <Button key={state} size="sm" variant={copieState === state ? "primary" : "outline"} onPress={() => setCopieState(state)}>{state}</Button>
            ))}
            <Button size="sm" variant="outline" onPress={newConversation}>reset</Button>
          </div>
        )}
        <div data-dock-guard="bottom" className="relative z-20 mx-auto flex w-full max-w-[1672px] items-end gap-3 sm:gap-4 px-4 sm:px-10 pb-3 sm:pb-8">
          <div className="hidden sm:block shrink-0">
            <HistoryButton onPress={onOpenHistory} isDisabled={!onOpenHistory} />
          </div>
          <div className="flex min-w-0 w-full flex-1 flex-col items-center [&_.copie-input:focus-within]:!border-cyber-field [&_textarea]:!leading-7 [&_textarea:focus]:!ring-0">
            {canChat && messages.length === 0 && displayName && (
              <p className="mb-1.5 sm:mb-2 text-center font-label text-xs sm:text-sm font-semibold text-cyber-blue px-2">
                สวัสดี {displayName} วันนี้อยากให้ช่วยเรื่องอะไรครับ
              </p>
            )}
            {showComposer && (
              <>
                {messages.length === 0 && (
                  <div className="mb-1 text-center">
                    <span className="font-label text-[10px] sm:text-[11px] font-medium text-cyber-subtle tracking-wider">
                      กด Enter เพื่อส่ง
                    </span>
                  </div>
                )}
                <ChatInput
                  onSend={send}
                  onDraftChange={(hasDraft) => {
                    if (canChat && !pending) setCopieState(hasDraft ? "listening" : "idle");
                  }}
                  pending={pending}
                  disabled={!canChat}
                  placeholder={
                    !canChat
                      ? "กำลังเชื่อมต่อระบบสมาชิก"
                      : followUpAfterRadar
                        ? "ถามต่อจากผลประเมินได้เลย เช่น ควรเริ่มฝึกอะไรก่อน?"
                        : "พิมพ์คำถามของคุณ..."
                  }
                />
                {canChat && !pending && messages.length === 0 && (
                  <div className="mt-2.5 sm:mt-3 w-full max-w-[760px]">
                    <SuggestedPrompts userType={userType} studyYear={studyYear} onAsk={(text) => { void send(text); }} compact />
                  </div>
                )}
                {!canChat && <p className="mt-2 text-center text-xs text-cyber-muted">พร้อมรับคำถามเมื่อเชื่อมต่อบัญชีผู้ใช้</p>}
              </>
            )}
          </div>
          <div className="hidden w-[115px] shrink-0 sm:block" aria-hidden="true" />
        </div>
        <AnimatePresence>
          {showDock && (
            <MascotDock
              key="copie-dock"
              state={copieState}
              onRestore={restoreMascot}
              guardKey={`${layout}:${showComposer}`}
            />
          )}
        </AnimatePresence>
      </main>
    </MascotModeProvider>
  );
}
