"use client";

import { useEffect, useRef, useSyncExternalStore } from "react";
import { Button } from "@heroui/react";

import { COPIE_IMAGES, type CopieMascotState } from "@/modules/mascot";
import { SuggestedPrompts } from "@/modules/suggest";
import type { UserType } from "@/types/contract";

import { getApiAuthSnapshot, subscribeApiAuth } from "../api";
import { useChatStore, type WorkspaceMode } from "../chatStore";
import { AppHeader, ChatInput, HistoryButton } from "../ui";
import { MessageList } from "./MessageList";
import { WorkspaceLayout } from "./WorkspaceLayout";

type ChatPageProps = { debug?: boolean; userType?: UserType | null; studyYear?: number | null };
const MODES: WorkspaceMode[] = ["center", "split", "rail", "hidden"];
const STATES = Object.keys(COPIE_IMAGES) as CopieMascotState[];

export function ChatPage({ debug = false, userType, studyYear }: ChatPageProps) {
  const canChat = useSyncExternalStore(subscribeApiAuth, getApiAuthSnapshot, () => false);
  const messages = useChatStore((state) => state.messages);
  const liveMessageId = useChatStore((state) => state.liveMessageId);
  const layout = useChatStore((state) => state.layout);
  const lastVisibleLayout = useChatStore((state) => state.lastVisibleLayout);
  const copieState = useChatStore((state) => state.copieState);
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
  const showComposer = lastAssistant?.role !== "assistant" || lastAssistant.response.response_type !== "assessment_form";

  useEffect(() => {
    if (wasAuthenticated.current && !canChat) newConversation();
    wasAuthenticated.current = canChat;
  }, [canChat, newConversation]);

  return (
    <main className="copie-ui flex h-dvh min-h-0 flex-col">
      <div className="copie-floor" aria-hidden="true" />
      <AppHeader />
      <WorkspaceLayout
        layout={layout}
        copieState={copieState}
        hasResponse={hasResponse}
        onHide={() => setLayout("hidden")}
        onShow={() => setLayout(lastVisibleLayout)}
        onBack={() => setLayout("center")}
        onRead={() => setLayout(lastVisibleLayout)}
      >
        <MessageList
          messages={messages}
          liveMessageId={liveMessageId}
          disabled={pending || !canChat}
          onAsk={canChat ? (text) => { void send(text); } : undefined}
          onSubmitAssessment={canChat ? submitAssessment : undefined}
        />
      </WorkspaceLayout>
      {pending && <p className="relative z-20 px-5 text-center text-sm text-cyber-blue" role="status">COPIE กำลังค้นหาคำตอบ...</p>}
      {error && <p className="relative z-20 px-5 text-center text-sm text-red-700" role="alert">{error}</p>}
      {debug && (
        <div className="relative z-20 mx-auto flex max-w-6xl flex-wrap items-center justify-center gap-2 px-5 pb-3" aria-label="เครื่องมือทดสอบ layout">
          <span className="font-label text-xs text-cyber-muted">DEV ONLY</span>
          {MODES.map((mode) => (
            <Button key={mode} size="sm" variant={layout === mode ? "primary" : "outline"} onPress={() => setLayout(mode)}>{mode}</Button>
          ))}
          {STATES.map((state) => (
            <Button key={state} size="sm" variant={copieState === state ? "primary" : "outline"} onPress={() => setCopieState(state)}>{state}</Button>
          ))}
          <Button size="sm" variant="outline" onPress={newConversation}>reset</Button>
        </div>
      )}
      <div className="relative z-20 mx-auto flex w-full max-w-[1672px] items-end gap-4 px-5 pb-5 sm:px-10 sm:pb-8">
        <div className="hidden shrink-0 sm:block"><HistoryButton isDisabled /></div>
        <div className="flex min-w-0 flex-1 flex-col items-center">
          {showComposer && (
            <>
              <ChatInput
                onSend={send}
                onDraftChange={(hasDraft) => {
                  if (canChat && !pending) setCopieState(hasDraft ? "listening" : "idle");
                }}
                pending={pending}
                disabled={!canChat}
                placeholder={canChat ? "พิมพ์คำถามของคุณ..." : "กำลังเชื่อมต่อระบบสมาชิก"}
              />
              {canChat && !pending && messages.length === 0 && (
                <div className="mt-3 w-full max-w-[720px]">
                  <SuggestedPrompts userType={userType} studyYear={studyYear} onAsk={(text) => { void send(text); }} compact />
                </div>
              )}
              {!canChat && <p className="mt-2 text-center text-xs text-cyber-muted">พร้อมรับคำถามเมื่อเชื่อมต่อบัญชีผู้ใช้</p>}
            </>
          )}
        </div>
        <div className="hidden w-[115px] shrink-0 sm:block" aria-hidden="true" />
      </div>
    </main>
  );
}
