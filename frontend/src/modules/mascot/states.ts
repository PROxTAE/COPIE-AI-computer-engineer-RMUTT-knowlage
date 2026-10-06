import type { InteractionMode } from "@/types/contract";

// 2.5D COPIE: one transparent image per state (from assets/web-ui/mascot/states)
// and one full set per interaction mode (assets/web-ui/mascot/modes/<mode>/states).
export type CopieMascotState =
  | "idle"
  | "listening"
  | "thinking"
  | "responding"
  | "success"
  | "no-answer"
  | "skill-guide"
  | "welcome";

export type { InteractionMode };

export const INTERACTION_MODES: readonly InteractionMode[] = ["normal", "devil", "developer"];

const STATE_FILES: Record<CopieMascotState, string> = {
  idle: "copie-idle",
  listening: "copie-listening",
  thinking: "copie-thinking",
  responding: "copie-responding",
  success: "copie-success",
  "no-answer": "copie-no-answer",
  "skill-guide": "copie-skill-guide",
  welcome: "copie-front-laptop",
};

export const COPIE_STATES = Object.keys(STATE_FILES) as CopieMascotState[];

export function copieImage(mode: InteractionMode, state: CopieMascotState): string {
  const folder = mode === "normal" ? "/copie-ui/mascot" : `/copie-ui/mascot/modes/${mode}`;
  return `${folder}/${STATE_FILES[state]}.webp`;
}

// Normal-mode lookup kept for existing callers.
export const COPIE_IMAGES = Object.fromEntries(
  COPIE_STATES.map((state) => [state, copieImage("normal", state)]),
) as Record<CopieMascotState, string>;

// Source images are 1089 x 1445.
export const COPIE_IMAGE_SIZE = { width: 1089, height: 1445 } as const;
