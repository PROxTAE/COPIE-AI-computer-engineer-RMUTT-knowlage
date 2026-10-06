"use client";

import { useEffect, useRef, useState, type MouseEvent, type PointerEvent } from "react";
import {
  AnimatePresence,
  animate,
  motion,
  useMotionTemplate,
  useMotionValue,
  useReducedMotion,
  useSpring,
  useTransform,
} from "motion/react";

import { CopieMascot } from "./CopieMascot";
import { PERSONALITY, pick } from "./personality";
import type { CopieMascotState, InteractionMode } from "./states";

type StageLayout = "center" | "rail";

type MascotStageProps = {
  state: CopieMascotState;
  mode?: InteractionMode;
  layout?: StageLayout;
  priority?: boolean;
  /** Size classes for the mascot image (max-h, w-auto ...). */
  imageClassName?: string;
  /** Size classes for the halo behind the mascot. */
  haloClassName?: string;
  /** Let COPIE drop an occasional hint in its bubble when the page is quiet. */
  chatter?: boolean;
};

type Bubble = { id: number; text: string };

// Depth of each 2.5D layer, as a multiple of the normalised pointer offset (-1..1).
const DEPTH = {
  moveX: 8, // px, mascot
  moveY: 6, // px
  roll: 2.5, // deg, rotateZ
  turn: 10, // deg, rotateY
  pitch: 6, // deg, rotateX
  haloX: -14, // px, back layer moves against the pointer
  haloY: -10,
  frontX: 22, // px, front layer moves with the pointer, further than the mascot
  frontY: 15,
  shadowX: -12, // px, ground shadow falls away from the "light"
};
const FOLLOW = { stiffness: 120, damping: 17, mass: 0.7 };
const COMBO_TAPS = 5;
const COMBO_WINDOW_MS = 1800;
const PET_TURNS = 4;
const PET_WINDOW_MS = 1200;
const BUBBLE_MS = 3400;
const LOOK_AROUND_AFTER_MS = 5000;
const CHATTER_AFTER_MS = 25_000;
const CHATTER_MAX = 3;

const clamp = (value: number) => Math.max(-1, Math.min(1, value));

// Fixed spots for the floating glyphs in front of COPIE (percent of the stage).
const AMBIENT = [
  { left: "8%", top: "22%", delay: "0s", size: "0.8rem" },
  { left: "86%", top: "16%", delay: "-1.6s", size: "0.95rem" },
  { left: "14%", top: "70%", delay: "-3.1s", size: "0.7rem" },
  { left: "82%", top: "62%", delay: "-4.4s", size: "0.75rem" },
  { left: "50%", top: "2%", delay: "-2.2s", size: "0.65rem" },
];

export function MascotStage({
  state,
  mode = "normal",
  layout = "center",
  priority,
  imageClassName = "",
  haloClassName = "",
  chatter = false,
}: MascotStageProps) {
  const reduced = useReducedMotion() ?? false;
  const personality = PERSONALITY[mode];
  const rootRef = useRef<HTMLDivElement>(null);
  const burstRef = useRef<HTMLDivElement>(null);
  const ringRef = useRef<HTMLDivElement>(null);
  const lastPointerAt = useRef(0);
  const taps = useRef<number[]>([]);
  const petTurns = useRef<number[]>([]);
  const petDirection = useRef(0);
  const petCooldownUntil = useRef(0);
  const lastLine = useRef<string | undefined>(undefined);
  const prevState = useRef(state);
  const prevMode = useRef(mode);

  const [bubble, setBubble] = useState<Bubble | null>(null);
  const [seenMode, setSeenMode] = useState(mode);
  const [seenState, setSeenState] = useState(state);

  // Speech for prop changes is derived during render, not in an effect.
  if (seenMode !== mode) {
    setSeenMode(mode);
    setBubble({ id: (bubble?.id ?? 0) + 1, text: personality.greet });
  }
  if (seenState !== state) {
    setSeenState(state);
    if (state === "success") setBubble({ id: (bubble?.id ?? 0) + 1, text: personality.success });
  }

  // ---- motion values (no React renders on pointer move) ----
  const pointerX = useMotionValue(0);
  const pointerY = useMotionValue(0);
  const hover = useMotionValue(0);
  const squash = useMotionValue(0); // 1 = pressed flat, negative = stretched on rebound
  const hop = useMotionValue(0); // px, negative = up
  const spin = useMotionValue(0); // deg, extra rotateY for flips
  const shake = useMotionValue(0); // px
  const sway = useMotionValue(0); // deg
  const lean = useMotionValue(0); // 0..1, listening pose

  const followX = useSpring(pointerX, FOLLOW);
  const followY = useSpring(pointerY, FOLLOW);
  const hoverSoft = useSpring(hover, { stiffness: 260, damping: 22 });

  const x = useTransform<number, number>([followX, shake], ([px, s]) => px * DEPTH.moveX + s);
  const y = useTransform<number, number>([followY, hop, lean], ([py, h, l]) => py * DEPTH.moveY + h + l * 4);
  const rotateY = useTransform<number, number>([followX, spin], ([px, s]) => px * DEPTH.turn + s);
  const rotateX = useTransform<number, number>([followY, lean], ([py, l]) => -py * DEPTH.pitch - l * 5);
  const rotateZ = useTransform<number, number>([followX, sway], ([px, s]) => px * DEPTH.roll + s);
  const scale = useTransform<number, number>([hoverSoft, lean], ([h, l]) => 1 + h * 0.025 + l * 0.015);
  const scaleX = useTransform(squash, (s) => 1 + s * 0.07);
  const scaleY = useTransform(squash, (s) => 1 - s * 0.08);

  const haloX = useTransform(followX, (v) => v * DEPTH.haloX);
  const haloY = useTransform(followY, (v) => v * DEPTH.haloY);
  const frontX = useTransform(followX, (v) => v * DEPTH.frontX);
  const frontY = useTransform(followY, (v) => v * DEPTH.frontY);
  const shadowX = useTransform(followX, (v) => v * DEPTH.shadowX);
  const shadowScale = useTransform(hop, (h) => 1 + h / 70);
  const glowX = useTransform(followX, [-1, 1], [32, 68]);
  const glowY = useTransform(followY, [-1, 1], [28, 62]);
  const glow = useMotionTemplate`radial-gradient(circle at ${glowX}% ${glowY}%, var(--copie-stage-glow) 0%, transparent 58%)`;
  const glowOpacity = useTransform(hoverSoft, [0, 1], [0.6, 1]);

  // ---- helpers ----
  function say(text: string) {
    lastLine.current = text;
    setBubble((current) => ({ id: (current?.id ?? 0) + 1, text }));
  }

  function stageCenter() {
    const rect = rootRef.current?.getBoundingClientRect();
    return rect ? { x: rect.width / 2, y: rect.height * 0.42 } : { x: 0, y: 0 };
  }

  // Particles are plain DOM nodes animated with WAAPI, so a burst never re-renders React.
  function burst(origin: { x: number; y: number }, glyphs: readonly string[], count: number, spread = 1) {
    const layer = burstRef.current;
    if (!layer || reduced) return;
    for (let i = 0; i < count; i += 1) {
      const particle = document.createElement("span");
      particle.className = "copie-burst";
      particle.textContent = glyphs[i % glyphs.length];
      particle.style.left = `${origin.x}px`;
      particle.style.top = `${origin.y}px`;
      particle.style.color = i % 3 === 0 ? "var(--copie-glow)" : "var(--copie-cyber-blue)";
      particle.style.fontSize = `${0.7 + Math.random() * 0.7}rem`;
      const angle = (Math.PI * 2 * i) / count + Math.random() * 0.6;
      const distance = (46 + Math.random() * 64) * spread;
      const dx = Math.cos(angle) * distance;
      const dy = Math.sin(angle) * distance - 26;
      const turn = (Math.random() - 0.5) * 140;
      layer.append(particle);
      const animation = particle.animate(
        [
          { transform: "translate(-50%, -50%) scale(0.3)", opacity: 1 },
          { transform: `translate(calc(-50% + ${dx * 0.7}px), calc(-50% + ${dy * 0.7}px)) scale(1.05) rotate(${turn * 0.6}deg)`, opacity: 1, offset: 0.55 },
          { transform: `translate(calc(-50% + ${dx}px), calc(-50% + ${dy + 18}px)) scale(0.8) rotate(${turn}deg)`, opacity: 0 },
        ],
        { duration: 750 + Math.random() * 450, easing: "cubic-bezier(.2,.8,.2,1)" },
      );
      animation.onfinish = () => particle.remove();
      animation.oncancel = () => particle.remove();
    }
  }

  function press() {
    if (reduced) return;
    animate(squash, 1, { duration: 0.11, ease: "easeOut" });
  }

  function release() {
    if (reduced) return;
    animate(squash, 0, { type: "spring", stiffness: 620, damping: 9 });
  }

  function jump(height: number) {
    if (reduced) return;
    animate(hop, [0, -height, 0], { duration: 0.46, times: [0, 0.4, 1], ease: ["easeOut", "easeIn"] });
  }

  function flip(turns = 1) {
    if (reduced) return;
    animate(spin, spin.get() + 360 * turns, {
      duration: 0.75 + 0.25 * turns,
      ease: [0.2, 0.8, 0.2, 1],
      onComplete: () => spin.set(0),
    });
  }

  // ---- pointer interaction on COPIE ----
  function onPointerEnter(event: PointerEvent<HTMLButtonElement>) {
    if (event.pointerType === "mouse") hover.set(1);
  }

  function onPointerLeave() {
    hover.set(0);
    release();
  }

  function onPointerDown(event: PointerEvent<HTMLButtonElement>) {
    if (event.button === 0) press();
  }

  // Rubbing back and forth over COPIE counts as petting.
  function onPointerMove(event: PointerEvent<HTMLButtonElement>) {
    if (event.pointerType !== "mouse" || Math.abs(event.movementX) < 3) return;
    const direction = Math.sign(event.movementX);
    if (direction === petDirection.current) return;
    petDirection.current = direction;
    const now = performance.now();
    petTurns.current = [...petTurns.current.filter((t) => now - t < PET_WINDOW_MS), now];
    if (petTurns.current.length < PET_TURNS || now < petCooldownUntil.current) return;
    petTurns.current = [];
    petCooldownUntil.current = now + 4000;
    const rect = rootRef.current?.getBoundingClientRect();
    if (rect) burst({ x: event.clientX - rect.left, y: event.clientY - rect.top }, personality.hearts, 7, 0.7);
    jump(8);
    say(personality.pet);
  }

  function onClick(event: MouseEvent<HTMLButtonElement>) {
    const rect = rootRef.current?.getBoundingClientRect();
    const fromKeyboard = event.detail === 0 || !rect;
    const origin = fromKeyboard ? stageCenter() : { x: event.clientX - rect.left, y: event.clientY - rect.top };
    if (fromKeyboard && !reduced) {
      animate(squash, 1, { duration: 0.1 }).then(release);
    } else {
      release();
    }

    const now = performance.now();
    taps.current = [...taps.current.filter((t) => now - t < COMBO_WINDOW_MS), now];
    if (taps.current.length >= COMBO_TAPS) {
      taps.current = [];
      flip(2);
      if (!reduced) animate(sway, [0, -8, 8, -5, 5, 0], { duration: 1.1 });
      burst(stageCenter(), personality.sparks, 18, 1.4);
      say(personality.combo);
      return;
    }
    jump(10);
    burst(origin, personality.sparks, 8);
    say(pick(personality.poke, lastLine.current));
  }

  // ---- whole-page pointer tracking: COPIE turns toward the cursor ----
  useEffect(() => {
    const root = rootRef.current;
    if (!root || reduced || !window.matchMedia("(pointer: fine)").matches) return;
    let visible = true;
    let frame = 0;
    let last: { x: number; y: number } | null = null;

    const update = () => {
      frame = 0;
      if (!last) return;
      const rect = root.getBoundingClientRect();
      const reach = Math.max(rect.width, 320) * 1.15;
      pointerX.set(clamp((last.x - (rect.left + rect.width / 2)) / reach));
      pointerY.set(clamp((last.y - (rect.top + rect.height * 0.42)) / reach));
    };
    const onMove = (event: globalThis.PointerEvent) => {
      if (event.pointerType !== "mouse" && event.pointerType !== "pen") return;
      lastPointerAt.current = performance.now();
      if (!visible || document.hidden) return;
      pointerX.stop();
      pointerY.stop();
      last = { x: event.clientX, y: event.clientY };
      if (!frame) frame = requestAnimationFrame(update);
    };
    const center = () => {
      last = null;
      pointerX.set(0);
      pointerY.set(0);
    };
    const observer = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
      if (!visible) center();
    });

    observer.observe(root);
    window.addEventListener("pointermove", onMove, { passive: true });
    document.documentElement.addEventListener("pointerleave", center);
    window.addEventListener("blur", center);
    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
      window.removeEventListener("pointermove", onMove);
      document.documentElement.removeEventListener("pointerleave", center);
      window.removeEventListener("blur", center);
    };
  }, [reduced, pointerX, pointerY]);

  // ---- when nobody moves the pointer (or on touch screens), COPIE looks around by itself ----
  useEffect(() => {
    if (reduced) return;
    const timer = window.setInterval(() => {
      if (document.hidden || performance.now() - lastPointerAt.current < LOOK_AROUND_AFTER_MS) return;
      const ease = { duration: 1.6, ease: "easeInOut" } as const;
      animate(pointerX, (Math.random() - 0.5) * 1.1, ease);
      animate(pointerY, (Math.random() - 0.6) * 0.6, ease);
    }, 4200);
    return () => window.clearInterval(timer);
  }, [reduced, pointerX, pointerY]);

  // ---- poses per conversation state ----
  useEffect(() => {
    const previous = prevState.current;
    prevState.current = state;
    if (reduced) return;
    animate(lean, state === "listening" ? 1 : 0, { type: "spring", stiffness: 160, damping: 20 });
    const swaying = state === "thinking"
      ? animate(sway, [-1.8, 1.8], { duration: 1.5, repeat: Infinity, repeatType: "mirror", ease: "easeInOut" })
      : animate(sway, 0, { duration: 0.4 });
    if (state !== previous) {
      if (state === "success") {
        jump(18);
        burst(stageCenter(), PERSONALITY[mode].sparks, 14, 1.2);
      } else if (state === "no-answer") {
        animate(shake, [0, -7, 7, -5, 5, -2, 0], { duration: 0.6 });
      } else if (state === "responding") {
        jump(6);
      }
    }
    return () => swaying.stop();
    // Reacts to state changes only; mode is read for the particle style.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state, reduced]);

  // ---- switching mode: flip, shock ring and a burst in the new colours ----
  useEffect(() => {
    if (prevMode.current === mode) return;
    prevMode.current = mode;
    if (reduced) return;
    flip(1);
    animate(squash, [0, 0.9, 0], { duration: 0.5 });
    ringRef.current?.animate(
      [
        { transform: "translate(-50%, -50%) scale(0.35)", opacity: 0.95 },
        { transform: "translate(-50%, -50%) scale(1.55)", opacity: 0 },
      ],
      { duration: 900, easing: "cubic-bezier(.2,.8,.2,1)" },
    );
    burst(stageCenter(), PERSONALITY[mode].sparks, 16, 1.3);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, reduced]);

  // ---- bubble lifetime ----
  useEffect(() => {
    if (!bubble) return;
    const timer = window.setTimeout(() => setBubble(null), BUBBLE_MS);
    return () => window.clearTimeout(timer);
  }, [bubble]);

  // ---- an occasional hint when the page is quiet ----
  useEffect(() => {
    if (!chatter || state !== "idle") return;
    let lastActivity = performance.now();
    let shown = 0;
    const touch = () => { lastActivity = performance.now(); };
    const timer = window.setInterval(() => {
      if (document.hidden || shown >= CHATTER_MAX || performance.now() - lastActivity < CHATTER_AFTER_MS) return;
      shown += 1;
      lastActivity = performance.now();
      const text = pick(PERSONALITY[mode].idle, lastLine.current);
      lastLine.current = text;
      setBubble((current) => ({ id: (current?.id ?? 0) + 1, text }));
    }, 5000);
    window.addEventListener("pointerdown", touch);
    window.addEventListener("keydown", touch);
    return () => {
      window.clearInterval(timer);
      window.removeEventListener("pointerdown", touch);
      window.removeEventListener("keydown", touch);
    };
  }, [chatter, state, mode]);

  const isRail = layout === "rail";

  return (
    <div
      ref={rootRef}
      className="copie-stage relative flex items-center justify-center"
      data-layout={layout}
      style={{ perspective: isRail ? 700 : 1000 }}
    >
      {/* back layer: halo + soft light that follows the pointer */}
      <motion.div className="pointer-events-none absolute" style={{ x: haloX, y: haloY }} aria-hidden="true">
        <div className={`copie-halo copie-halo-spin ${haloClassName}`} />
      </motion.div>
      <motion.div
        className="pointer-events-none absolute inset-[-12%] rounded-full"
        style={{ backgroundImage: glow, opacity: glowOpacity }}
        aria-hidden="true"
      />
      <div ref={ringRef} className="copie-stage-ring" aria-hidden="true" />

      {/* ground contact shadow */}
      <motion.div
        className="copie-stage-shadow pointer-events-none absolute bottom-[1%] left-1/2 h-[7%] w-[52%] -translate-x-1/2"
        style={{ x: shadowX, scale: shadowScale }}
        aria-hidden="true"
      />

      {/* middle layer: COPIE itself */}
      <motion.div
        className="relative"
        style={{ x, y, rotateX, rotateY, rotateZ, scale, transformStyle: "preserve-3d" }}
      >
        <motion.button
          type="button"
          className="copie-stage-hit relative flex cursor-pointer select-none"
          style={{ scaleX, scaleY, originY: 1 }}
          aria-label="COPIE — แตะเพื่อทักทาย"
          onPointerEnter={onPointerEnter}
          onPointerLeave={onPointerLeave}
          onPointerDown={onPointerDown}
          onPointerUp={release}
          onPointerCancel={release}
          onPointerMove={onPointerMove}
          onClick={onClick}
          onContextMenu={(event) => event.preventDefault()}
        >
          <CopieMascot state={state} mode={mode} layout={layout} priority={priority} className={imageClassName} />
        </motion.button>
        {state === "thinking" && (
          <span className="copie-think-orbit" aria-hidden="true">
            <i />
            <i />
            <i />
          </span>
        )}
      </motion.div>

      {/* front layer: floating glyphs with the strongest parallax */}
      <motion.div className="copie-ambient pointer-events-none absolute inset-0" style={{ x: frontX, y: frontY }} aria-hidden="true">
        {AMBIENT.slice(0, isRail ? 3 : AMBIENT.length).map((spot, index) => (
          <span key={index} style={{ left: spot.left, top: spot.top, animationDelay: spot.delay, fontSize: spot.size }}>
            {personality.sparks[index % personality.sparks.length]}
          </span>
        ))}
      </motion.div>

      <div ref={burstRef} className="pointer-events-none absolute inset-0 z-20" aria-hidden="true" />

      <div className={`copie-bubble-anchor ${isRail ? "copie-bubble-anchor--rail" : ""}`} role="status" aria-live="polite">
        <AnimatePresence mode="wait">
          {bubble && (
            <motion.p
              key={bubble.id}
              className="copie-bubble"
              initial={{ opacity: 0, y: 8, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -6, scale: 0.96 }}
              transition={{ type: "spring", stiffness: 420, damping: 28 }}
            >
              {bubble.text}
            </motion.p>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
