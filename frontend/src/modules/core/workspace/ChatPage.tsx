import { CopieMascot } from "@/modules/mascot";

import { AppHeader, ChatInput, HistoryButton, StatusLabel } from "../ui";

// The shell exposes P1's layout and component slots while P2's auth and history
// integration is in progress. It does not submit or display fixture responses.
export function ChatPage() {
  return (
    <main className="copie-ui flex h-dvh min-h-[600px] flex-col">
      <div className="copie-floor" aria-hidden="true" />
      <AppHeader />
      <div className="relative z-10 flex min-h-0 flex-1 flex-col items-center justify-center px-5 text-center">
        <div className="copie-halo absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" aria-hidden="true" />
        <CopieMascot state="idle" priority className="relative max-h-[min(60dvh,560px)] w-auto!" />
        <StatusLabel label="COPIE / IDLE" className="relative mt-1" />
      </div>
      <div className="relative z-20 mx-auto flex w-full max-w-[1672px] items-end gap-4 px-5 pb-5 sm:px-10 sm:pb-8">
        <div className="hidden shrink-0 sm:block">
          <HistoryButton isDisabled />
        </div>
        <div className="flex min-w-0 flex-1 flex-col items-center">
          <ChatInput disabled placeholder="กำลังเชื่อมต่อระบบสมาชิก" />
          <p className="mt-2 text-center text-xs text-cyber-muted">พร้อมรับคำถามเมื่อเชื่อมต่อบัญชีผู้ใช้</p>
        </div>
        <div className="hidden w-[115px] shrink-0 sm:block" aria-hidden="true" />
      </div>
    </main>
  );
}
