import type { ReactNode } from "react";

import { StatusLabel } from "./StatusLabel";

type AppHeaderProps = {
  profile?: ReactNode;
  status?: string;
};

export function AppHeader({ profile, status = "AI // ACTIVE" }: AppHeaderProps) {
  return (
    <header className="relative z-10 flex items-center justify-between gap-4 px-5 py-5 sm:px-10">
      <div className="flex min-w-0 items-center gap-4">
        <span className="copie-wordmark">COPIE</span>
        <span className="hidden border-l border-cyber-blue pl-4 font-label text-[0.65rem] font-semibold uppercase leading-relaxed tracking-[0.14em] text-cyber-muted sm:block">
          AI Assistant<br />for your ideas
        </span>
      </div>
      <div className="flex items-center gap-5">
        <StatusLabel label={status} className="hidden sm:inline-flex" />
        {profile}
      </div>
    </header>
  );
}
