import type { Transition } from "motion/react";

// COPIE is one shared element across layouts: the centre stage and the sidebar stage both carry
// this layoutId, so switching layout glides and resizes the mascot instead of swapping it.
// The wrappers hug the image (same aspect ratio in both places), so the resize never stretches.
export const MASCOT_LAYOUT_ID = "copie-mascot";

export const MASCOT_MORPH: Transition = { type: "spring", stiffness: 140, damping: 22, mass: 0.9 };

// Containers fade/slide in instead of using `layout`, which would scale text and boxes mid-way.
export const PANEL_ENTER = { type: "spring", stiffness: 220, damping: 28 } as const;
