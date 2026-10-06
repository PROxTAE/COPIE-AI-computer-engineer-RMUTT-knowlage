"use client";

import type { UserType } from "@/types/contract";

import { getSuggestedPrompts } from "./suggested-prompts";

export type SuggestedPromptsProps = {
  userType?: UserType | null;
  studyYear?: number | null;
  onAsk: (text: string) => void;
  compact?: boolean;
};

export function SuggestedPrompts({ userType, studyYear, onAsk, compact = false }: SuggestedPromptsProps) {
  const prompts = getSuggestedPrompts(userType, studyYear);

  return (
    <section aria-label="คำถามแนะนำ" className="w-full">
      <div className={compact ? "flex w-full gap-2 overflow-x-auto pb-1.5 scrollbar-none [scrollbar-width:none] [-ms-overflow-style:none] overscroll-x-contain" : "flex flex-wrap gap-2"}>
        {prompts.map((prompt) => (
          <button
            key={prompt.text}
            type="button"
            onClick={() => onAsk(prompt.text)}
            className="shrink-0 rounded-full border border-cyber-blue/20 bg-white/95 px-3.5 py-1.5 sm:px-4 sm:py-2 text-left text-xs sm:text-sm font-medium text-cyber-strong shadow-xs transition-all hover:border-cyber-blue hover:bg-blue-50/60 active:scale-95 cursor-pointer focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyber-blue"
          >
            {prompt.label}
          </button>
        ))}
      </div>
    </section>
  );
}