// 2.5D COPIE: one transparent image per state (from assets/web-ui/mascot/states).
export type CopieMascotState =
  | "idle"
  | "listening"
  | "thinking"
  | "responding"
  | "success"
  | "no-answer"
  | "skill-guide"
  | "welcome";

export const COPIE_IMAGES: Record<CopieMascotState, string> = {
  idle: "/copie-ui/mascot/copie-idle.webp",
  listening: "/copie-ui/mascot/copie-listening.webp",
  thinking: "/copie-ui/mascot/copie-thinking.webp",
  responding: "/copie-ui/mascot/copie-responding.webp",
  success: "/copie-ui/mascot/copie-success.webp",
  "no-answer": "/copie-ui/mascot/copie-no-answer.webp",
  "skill-guide": "/copie-ui/mascot/copie-skill-guide.webp",
  welcome: "/copie-ui/mascot/copie-front-laptop.webp",
};

// Source images are 1089 x 1445.
export const COPIE_IMAGE_SIZE = { width: 1089, height: 1445 } as const;
