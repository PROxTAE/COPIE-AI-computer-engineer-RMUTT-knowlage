"use client";

import { useState } from "react";

import { ChatPage, useChatStore } from "@/modules/core";

import { FeedbackBar } from "../feedback/FeedbackBar";
import { HistorySidebar } from "../history/HistorySidebar";
import { useUserStore } from "../userStore";
import { AuthGuard } from "./AuthGuard";
import { ProfileControl } from "./ProfileControl";

type AuthenticatedChatPageProps = { debug?: boolean };

function ChatWithUser({ debug }: AuthenticatedChatPageProps) {
  const user = useUserStore((state) => state.user);
  const messages = useChatStore((state) => state.messages);
  const [desktopHistoryOpen, setDesktopHistoryOpen] = useState(false);
  const [mobileHistoryOpen, setMobileHistoryOpen] = useState(false);
  if (!user) return null;

  const latestAssistant = messages.findLast((message) => message.role === "assistant");
  const openHistory = () => {
    if (window.matchMedia("(min-width: 1024px)").matches) {
      setDesktopHistoryOpen((open) => !open);
    } else {
      setMobileHistoryOpen(true);
    }
  };

  return (
    <div className="fixed inset-0 flex min-h-0 overflow-hidden">
      <HistorySidebar
        desktopOpen={desktopHistoryOpen}
        mobileOpen={mobileHistoryOpen}
        onCloseDesktop={() => setDesktopHistoryOpen(false)}
        onCloseMobile={() => setMobileHistoryOpen(false)}
        refreshKey={latestAssistant?.id ?? ""}
      />
      <div className="min-h-0 min-w-0 flex-1">
        <ChatPage
          debug={debug}
          userType={user.user_type}
          studyYear={user.study_year}
          displayName={user.display_name ?? user.name}
          profileControl={<ProfileControl user={user} />}
          onOpenHistory={openHistory}
          renderAssistantFooter={(message) => (
            <FeedbackBar
              messageId={message.id}
              initialFeedback={message.feedback}
              messageContent={message.response?.message}
            />
          )}
        />
      </div>
    </div>
  );
}

export function AuthenticatedChatPage({ debug = false }: AuthenticatedChatPageProps) {
  return (
    <AuthGuard>
      <ChatWithUser debug={debug} />
    </AuthGuard>
  );
}
