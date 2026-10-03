import type { ReactNode } from "react";

type AppHeaderProps = {
  profile?: ReactNode;
  historyAction?: ReactNode;
  status?: string;
};

export function AppHeader({ profile, historyAction, status = "AI // ACTIVE" }: AppHeaderProps) {
  return (
    <header className="relative z-10 flex items-center justify-between gap-3 px-4 py-4 sm:px-12 sm:py-5">
      {/* Brand Logo & Subtitle */}
      <div className="flex min-w-0 items-center gap-3 sm:gap-4">
        <span className="copie-wordmark text-2xl sm:text-4xl font-black text-[#080b12] tracking-tighter">
          COPIE
        </span>
        <span className="hidden sm:block border-l-2 border-[#155ff2] pl-4 font-label text-[10px] sm:text-[11px] font-bold uppercase leading-tight tracking-[0.16em] text-[#6b82a6]">
          AI ASSISTANT<br />FOR YOUR IDEAS
        </span>
      </div>

      {/* Right: Status & History & Profile Avatar */}
      <div className="flex items-center gap-2.5 sm:gap-5">
        <div className="hidden sm:inline-flex items-center gap-2 rounded-full border border-[#155ff2]/20 bg-blue-50/60 px-3.5 py-1">
          <span className="size-2 rounded-full bg-[#155ff2] shadow-[0_0_8px_#155ff2]" />
          <span className="font-label text-xs font-bold tracking-[0.16em] text-[#155ff2] uppercase">
            {status}
          </span>
        </div>
        {historyAction}
        {profile}
      </div>
    </header>
  );
}
