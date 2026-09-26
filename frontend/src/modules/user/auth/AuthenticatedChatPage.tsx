"use client";

import { ChatPage } from "@/modules/core";

import { useUserStore } from "../userStore";
import { AuthGuard } from "./AuthGuard";

type AuthenticatedChatPageProps = { debug?: boolean };

function ChatWithUser({ debug }: AuthenticatedChatPageProps) {
  const user = useUserStore((state) => state.user);
  if (!user) return null;
  return <ChatPage debug={debug} userType={user.user_type} studyYear={user.study_year} />;
}

export function AuthenticatedChatPage({ debug = false }: AuthenticatedChatPageProps) {
  return (
    <AuthGuard>
      <ChatWithUser debug={debug} />
    </AuthGuard>
  );
}
