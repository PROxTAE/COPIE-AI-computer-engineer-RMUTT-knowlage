import type { ReactNode } from "react";

type AppHeaderProps = {
  profile?: ReactNode;
  historyAction?: ReactNode;
  status?: string;
  modeControl?: ReactNode;
};

export function AppHeader({ profile, historyAction, status = "AI // ACTIVE", modeControl }: AppHeaderProps) {
  return (
    <header className="relative z-10 flex items-center justify-between gap-3 px-4 py-4 sm:px-12 sm:py-5">
      {/* Brand Logo & Subtitle */}
      <div className="flex min-w-0 items-center gap-3 sm:gap-4">
        <span className="copie-wordmark text-2xl sm:text-4xl font-black text-cyber-strong tracking-tighter">
          COPIE
        </span>
        <span className="hidden sm:block border-l-2 border-cyber-blue pl-4 font-label text-[10px] sm:text-[11px] font-bold uppercase leading-tight tracking-[0.16em] text-cyber-subtle">
          AI ASSISTANT<br />FOR YOUR IDEAS
        </span>
      </div>

      {/* Right: Status & History & Profile Avatar */}
      <div className="flex items-center gap-2 sm:gap-5">
        {modeControl}
        <div className="hidden lg:inline-flex items-center gap-2 rounded-full border border-cyber-blue/20 bg-blue-50/60 px-3.5 py-1">
          <span className="size-2 rounded-full bg-cyber-blue shadow-[0_0_8px_var(--copie-cyber-blue)]" />
          <span className="font-label text-xs font-bold tracking-[0.16em] text-cyber-blue uppercase">
            {status}
          </span>
        </div>
        {historyAction}
        {profile}
      </div>
    </header>
  );
}
