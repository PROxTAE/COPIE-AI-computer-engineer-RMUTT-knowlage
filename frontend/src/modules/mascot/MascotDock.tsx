"use client";

import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import Image from "next/image";
import { Hand } from "lucide-react";
import { animate, motion, useMotionValue, useReducedMotion } from "motion/react";

import { useMascotMode } from "./modeContext";
import { copieImage, type CopieMascotState, type InteractionMode } from "./states";

export type DockCorner = "top-left" | "top-right" | "bottom-left" | "bottom-right";

type MascotDockProps = {
  state: CopieMascotState;
  mode?: InteractionMode;
  /** Brings the full mascot back. */
  onRestore: () => void;
  /** Changes whenever guard elements may have moved (e.g. the page layout), to re-place the dock. */
  guardKey?: string;
};

/**
 * Mark page controls the dock must never cover:
 * `data-dock-guard="top"` (header, sticky toolbars) keeps top corners below the element,
 * `data-dock-guard="bottom"` (chat input bar) keeps bottom corners above it.
 */
export const DOCK_GUARD = "data-dock-guard";

// Full COPIE figure, scaled down (source images are 1089 x 1445).
const WIDTH = 84;
const HEIGHT = 112;
const HINT_MS = 4500;
const MARGIN = 16;
const CORNER_KEY = "copie.dockCorner.v1";
const CORNERS: DockCorner[] = ["top-left", "top-right", "bottom-left", "bottom-right"];

function readCorner(): DockCorner {
  try {
    const saved = window.localStorage.getItem(CORNER_KEY);
    return CORNERS.includes(saved as DockCorner) ? (saved as DockCorner) : "bottom-right";
  } catch {
    return "bottom-right";
  }
}

function saveCorner(corner: DockCorner) {
  try {
    window.localStorage.setItem(CORNER_KEY, corner);
  } catch {
    // The corner still applies for this visit.
  }
}

// Mini COPIE shown while the full mascot is hidden: the whole figure in its current pose, just
// smaller. Tap to bring COPIE back; drag it to any corner (it snaps to the nearest one and
// remembers it). Corners keep clear of the header and the chat input bar, and the dock is
// portalled to <body> above everything else (history drawer included) so it is never hidden.
export function MascotDock({ state, mode: modeProp, onRestore, guardKey }: MascotDockProps) {
  const contextMode = useMascotMode();
  const mode = modeProp ?? contextMode;
  const reduced = useReducedMotion() ?? false;
  const [corner, setCorner] = useState<DockCorner>(readCorner);
  const x = useMotionValue(-200);
  const y = useMotionValue(-200);
  const dragged = useRef(false);
  const ready = useRef(false);
  const [hint, setHint] = useState(true);

  // Say "tap me" for a moment when the dock appears; afterwards only on hover/focus.
  useEffect(() => {
    const timer = window.setTimeout(() => setHint(false), HINT_MS);
    return () => window.clearTimeout(timer);
  }, []);

  // Pixel position of each corner, pushed clear of guard elements that share its columns.
  const spots = () => {
    const guards = (side: "top" | "bottom") =>
      [...document.querySelectorAll(`[${DOCK_GUARD}="${side}"]`)]
        .map((element) => element.getBoundingClientRect())
        .filter((rect) => rect.width > 0 && rect.height > 0);
    const overlaps = (rect: DOMRect, x: number) => rect.left < x + WIDTH && rect.right > x;
    const left = MARGIN;
    const right = window.innerWidth - MARGIN - WIDTH;
    const topAt = (x: number) =>
      Math.max(MARGIN, ...guards("top").filter((rect) => overlaps(rect, x)).map((rect) => rect.bottom + 8));
    const bottomAt = (x: number) => {
      const limit = Math.min(
        window.innerHeight - MARGIN,
        ...guards("bottom").filter((rect) => overlaps(rect, x)).map((rect) => rect.top - 8),
      );
      return Math.max(topAt(x), limit - HEIGHT);
    };
    return {
      "top-left": { x: left, y: topAt(left) },
      "top-right": { x: right, y: topAt(right) },
      "bottom-left": { x: left, y: bottomAt(left) },
      "bottom-right": { x: right, y: bottomAt(right) },
    } satisfies Record<DockCorner, { x: number; y: number }>;
  };

  const moveTo = (target: DockCorner, instant = false) => {
    const spot = spots()[target];
    if (instant || reduced) {
      x.set(spot.x);
      y.set(spot.y);
      return;
    }
    const spring = { type: "spring", stiffness: 380, damping: 30 } as const;
    animate(x, spot.x, spring);
    animate(y, spot.y, spring);
  };

  // Follow the corner when the window or the guard elements change size.
  useEffect(() => {
    moveTo(corner, !ready.current);
    ready.current = true;
    const update = () => moveTo(corner, true);
    const observer = new ResizeObserver(update);
    document.querySelectorAll(`[${DOCK_GUARD}]`).forEach((element) => observer.observe(element));
    window.addEventListener("resize", update);
    return () => {
      observer.disconnect();
      window.removeEventListener("resize", update);
    };
    // moveTo reads the page at call time; re-run when the corner or the guards change.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [corner, guardKey]);

  const snap = () => {
    const centerX = x.get() + WIDTH / 2;
    const centerY = y.get() + HEIGHT / 2;
    const horizontal = centerX < window.innerWidth / 2 ? "left" : "right";
    const vertical = centerY < window.innerHeight / 2 ? "top" : "bottom";
    const next = `${vertical}-${horizontal}` as DockCorner;
    saveCorner(next);
    if (next === corner) moveTo(next);
    else setCorner(next);
  };

  const busy = state === "thinking";
  const fresh = state === "responding" || state === "success";

  if (typeof document === "undefined") return null;
  return createPortal(
    <motion.div
      className="fixed left-0 top-0 z-[70]"
      style={{ x, y, width: WIDTH, height: HEIGHT }}
      drag
      dragMomentum={false}
      dragElastic={0.12}
      onPointerDown={() => { dragged.current = false; }}
      onDragStart={() => { dragged.current = true; }}
      onDragEnd={snap}
      initial={reduced ? false : { scale: 0.2, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={reduced ? undefined : { scale: 0.2, opacity: 0 }}
      transition={{ type: "spring", stiffness: 420, damping: 22 }}
      whileHover={reduced ? undefined : { scale: 1.1 }}
      whileTap={reduced ? undefined : { scale: 0.9 }}
    >
      <button
        type="button"
        onClick={() => {
          if (!dragged.current) onRestore(); // a drag ending on the button is not a tap
        }}
        aria-label="แสดงมาสคอต COPIE (ลากไปวางมุมอื่นได้)"
        title="แตะเพื่อเรียก COPIE กลับมา · ลากเพื่อย้ายมุม"
        className="copie-dock group relative block size-full cursor-grab touch-none active:cursor-grabbing"
        data-busy={busy || undefined}
        data-hint={hint || undefined}
      >
        <span className="copie-dock-ground" aria-hidden="true" />
        <span className="copie-dock-figure" aria-hidden="true">
          <Image
            src={copieImage(mode, state)}
            alt=""
            width={168}
            height={223}
            sizes="84px"
            draggable={false}
            className="pointer-events-none size-full select-none object-contain"
          />
        </span>
        {fresh && <span className="copie-dock-badge" aria-hidden="true" />}
        <span className="copie-dock-hint" aria-hidden="true">
          <Hand className="size-3" />
          {busy ? "กำลังคิด…" : "แตะเพื่อเรียก"}
        </span>
      </button>
    </motion.div>,
    document.body,
  );
}
