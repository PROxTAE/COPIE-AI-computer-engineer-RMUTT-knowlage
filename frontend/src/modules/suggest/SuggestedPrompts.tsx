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
    <section aria-label="คำถามแนะนำ">
      <div className={compact ? "flex max-w-full gap-2 overflow-x-auto pb-1" : "flex flex-wrap gap-2"}>
        {prompts.map((prompt) => (
          <button
            key={prompt.text}
            type="button"
            onClick={() => onAsk(prompt.text)}
            className="shrink-0 rounded-full border border-cyber-blue/20 bg-white/85 px-4 py-2 text-left text-sm text-cyber-ink transition-colors hover:border-cyber-blue hover:bg-cyber-blue/5 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyber-blue"
          >
            {prompt.label}
          </button>
        ))}
      </div>
    </section>
  );
}