"use client";

import { useEffect, useLayoutEffect, useRef, useState, useSyncExternalStore } from "react";
import { useRouter } from "next/navigation";
import { AnimatePresence, MotionConfig, motion, type Variants } from "motion/react";
import { Headphones } from "lucide-react";

import { CyberHudFrame, ModeSwitcher, useChatStore } from "@/modules/core";
import { MascotModeProvider, MascotStage, type CopieMascotState } from "@/modules/mascot";
import type { User } from "@/types/contract";

import { useUserStore } from "../userStore";
import { DevLoginForm } from "./DevLoginForm";
import { GoogleSignInButton } from "./GoogleSignInButton";
import { useAuthSession } from "./useAuthSession";

// COPIE cheers while the visitor points at the sign-in button.
const SIGN_IN_REACTION = { state: "success" as CopieMascotState, text: "กดเลย! เข้าสู่ระบบแล้วเริ่มคุยกันครับ 🚀" };

const TAGLINES = ["ค้นหาข้อมูลภาควิชา", "วางแผนรายวิชาแต่ละเทอม", "ประเมินทักษะของคุณ", "ค้นหาสายงานที่ใช่"];
const IDLE_LINES = ["เข้าสู่ระบบด้วย Google แล้วเริ่มคุยกันเลยครับ", "ลองแตะผมดูสิครับ 👋", "ลองเปลี่ยนบุคลิกของผมด้านล่างได้นะครับ"];
const GREETING = "สวัสดีครับ! ผม COPIE ผู้ช่วยของภาคคอมฯ 👋";

// One mascot stage at a time: beside the form on wide screens, above it on small ones.
const WIDE_QUERY = "(min-width: 1024px)";
function subscribeWide(listener: () => void) {
  const query = window.matchMedia(WIDE_QUERY);
  query.addEventListener("change", listener);
  return () => query.removeEventListener("change", listener);
}
const isWideSnapshot = () => window.matchMedia(WIDE_QUERY).matches;

const rise: Variants = {
  hidden: { opacity: 0, y: 18 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 260, damping: 26 } },
};
const stagger: Variants = { hidden: {}, show: { transition: { staggerChildren: 0.08, delayChildren: 0.05 } } };

export function LoginPage() {
  const router = useRouter();
  const status = useAuthSession();
  const user = useUserStore((state) => state.user);
  const mode = useChatStore((state) => state.interactionMode);
  const setMode = useChatStore((state) => state.setInteractionMode);
  const restoreMode = useChatStore((state) => state.restoreInteractionMode);
  const [showDevLogin, setShowDevLogin] = useState(false);
  const [pointing, setPointing] = useState(false);
  const [message, setMessage] = useState<{ id: number; text: string } | null>(null);
  const [tagline, setTagline] = useState(0);
  const pageRef = useRef<HTMLElement>(null);
  const wide = useSyncExternalStore(subscribeWide, isWideSnapshot, () => true);

  const routeUser = (authenticatedUser: User) => {
    router.replace(authenticatedUser.onboarded ? "/chat" : "/onboarding");
  };

  useEffect(() => {
    if (status === "authenticated" && user) {
      router.replace(user.onboarded ? "/chat" : "/onboarding");
    }
  }, [router, status, user]);

  // The mode chosen here is the one the chat opens with.
  useLayoutEffect(() => { restoreMode(); }, [restoreMode]);
  useLayoutEffect(() => { document.documentElement.dataset.copieMode = mode; }, [mode]);
  useEffect(() => () => { delete document.documentElement.dataset.copieMode; }, []);

  useEffect(() => {
    const timer = window.setInterval(() => setTagline((index) => (index + 1) % TAGLINES.length), 2600);
    return () => window.clearInterval(timer);
  }, []);

  // A soft light follows the cursor across the background (CSS variables, no React renders).
  useEffect(() => {
    const page = pageRef.current;
    if (!page || !window.matchMedia("(pointer: fine)").matches || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    let frame = 0;
    const onMove = (event: PointerEvent) => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        page.style.setProperty("--spot-x", `${event.clientX}px`);
        page.style.setProperty("--spot-y", `${event.clientY}px`);
      });
    };
    window.addEventListener("pointermove", onMove, { passive: true });
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("pointermove", onMove);
    };
  }, []);

  const point = (next: boolean) => {
    if (next === pointing) return;
    setPointing(next);
    if (next) setMessage((current) => ({ id: (current?.id ?? 0) + 1, text: SIGN_IN_REACTION.text }));
  };

  const checkingSession = status === "idle" || status === "loading" || status === "authenticated";
  const mascotState: CopieMascotState = checkingSession ? "thinking" : pointing ? SIGN_IN_REACTION.state : "welcome";

  const stage = (layout: "center" | "rail", imageClassName: string, haloClassName: string) => (
    <MascotStage
      state={mascotState}
      mode={mode}
      layout={layout}
      priority
      chatter
      greeting={GREETING}
      idleLines={IDLE_LINES}
      message={message}
      imageClassName={imageClassName}
      haloClassName={haloClassName}
    />
  );

  return (
    <MotionConfig reducedMotion="user">
      <MascotModeProvider value={mode}>
        <main ref={pageRef} className="copie-ui copie-login relative flex min-h-dvh flex-col overflow-clip" data-copie-mode={mode}>
          <div className="copie-login-aurora" aria-hidden="true" />
          <div className="copie-login-spot" aria-hidden="true" />
          <CyberHudFrame showStatusFooter={false} />
          <div className="copie-floor" aria-hidden="true" />

          <header className="copie-safe-top relative z-30 flex items-center justify-between px-6 pb-6 sm:px-12">
            <div className="flex items-center gap-4">
              <span className="copie-wordmark text-3xl sm:text-4xl font-black text-cyber-strong tracking-tighter">COPIE</span>
              <span className="hidden sm:block border-l-2 border-cyber-blue pl-4 font-label text-[10px] sm:text-[11px] font-bold uppercase leading-tight tracking-[0.16em] text-cyber-subtle">
                AI ASSISTANT<br />FOR YOUR IDEAS
              </span>
            </div>
            <div className="hidden sm:flex items-center gap-3 font-label text-[11px] font-bold tracking-[0.2em] text-cyber-subtle uppercase">
              <span>BUILD A BRIGHTER TOMORROW</span>
              <span className="h-0.5 w-6 bg-cyber-blue" />
            </div>
          </header>

          <section className="relative z-20 mx-auto grid w-full max-w-[1600px] flex-1 items-center gap-6 px-4 pb-8 sm:gap-8 sm:px-12 lg:grid-cols-[minmax(0,1.05fr)_minmax(420px,0.95fr)]">
            {/* Left: welcome and sign-in. Centred on small screens so the button is easy to reach. */}
            <motion.div
              className="mx-auto flex w-full max-w-xl flex-col items-center gap-5 text-center sm:gap-6 lg:mx-0 lg:items-start lg:text-left"
              variants={stagger}
              initial="hidden"
              animate="show"
            >
              {!wide && (
                <div className="flex flex-col items-center gap-3">
                  {stage("rail", "h-[min(34dvh,260px)]! sm:h-[min(38dvh,340px)]! w-auto! max-w-none!", "max-w-[340px] sm:max-w-[420px] aspect-square")}
                  <ModeSwitcher value={mode} onChange={(next) => setMode(next)} />
                </div>
              )}

              <motion.div variants={rise} className="flex items-center gap-2">
                <span className="size-2 bg-cyber-blue" />
                <span className="font-label text-xs font-bold uppercase tracking-[0.2em] text-cyber-blue">AI AGENT FOR EDUCATION</span>
              </motion.div>

              <motion.div variants={rise}>
                <h1 className="copie-heading font-display text-4xl font-black italic tracking-tight text-cyber-strong sm:text-5xl lg:text-6xl">
                  ยินดีต้อนรับสู่{" "}
                  <span className="copie-login-gradient not-italic">COPIE</span>
                </h1>
                <p className="mt-3 font-display text-lg font-bold text-cyber-strong/80 sm:text-2xl">ผู้ช่วย AI ภาควิชาวิศวกรรมคอมพิวเตอร์</p>
                <p className="mt-2 flex h-7 items-center justify-center gap-2 overflow-hidden font-display text-base font-semibold text-cyber-subtle sm:text-lg lg:justify-start" aria-live="polite">
                  {/* The whole line swaps together so a centred line never jumps sideways. */}
                  <AnimatePresence mode="wait" initial={false}>
                    <motion.span
                      key={tagline}
                      initial={{ y: 18, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      exit={{ y: -18, opacity: 0 }}
                      transition={{ duration: 0.28 }}
                    >
                      ช่วยคุณ <span className="text-cyber-blue">{TAGLINES[tagline]}</span>
                    </motion.span>
                  </AnimatePresence>
                </p>
              </motion.div>

              <motion.div
                variants={rise}
                className="flex flex-col items-center gap-3 lg:items-start"
                onPointerEnter={() => point(true)}
                onPointerLeave={() => point(false)}
                onFocus={() => point(true)}
                onBlur={() => point(false)}
              >
                {checkingSession ? (
                  <p className="font-medium text-cyber-muted" role="status">กำลังตรวจสอบการเข้าสู่ระบบ...</p>
                ) : (
                  <>
                    <GoogleSignInButton onAuthenticated={routeUser} onOpenDevLogin={() => setShowDevLogin(true)} />
                    <p className="text-sm font-medium text-cyber-subtle">ใช้บัญชี Google เพื่อเริ่มต้นใช้งาน COPIE</p>
                    <div className="flex w-full flex-col items-center pt-2 lg:items-start">
                      <button
                        type="button"
                        onClick={() => setShowDevLogin((prev) => !prev)}
                        className="text-xs font-medium text-cyber-subtle underline hover:text-cyber-blue cursor-pointer"
                      >
                        {showDevLogin ? "ซ่อนโหมด Dev Login" : "หรือเข้าสู่ระบบด้วย Dev Account"}
                      </button>
                      {showDevLogin && (
                        <div className="mt-3 w-full max-w-sm text-left">
                          <DevLoginForm onAuthenticated={routeUser} />
                        </div>
                      )}
                    </div>
                  </>
                )}
              </motion.div>

              <motion.div variants={rise} className="flex items-center gap-3 pt-2 text-left text-xs text-cyber-strong sm:pt-6">
                <div className="flex size-9 shrink-0 items-center justify-center rounded-full bg-blue-50 text-cyber-blue">
                  <Headphones className="size-5" />
                </div>
                <div>
                  <p className="font-bold text-cyber-strong">หากต้องการความช่วยเหลือ</p>
                  <p className="text-cyber-subtle">ติดต่อผู้ดูแลระบบ</p>
                </div>
              </motion.div>
            </motion.div>

            {/* Right: interactive COPIE and a persona preview */}
            {wide && <motion.div
              className="relative flex min-h-[560px] flex-col items-center justify-center gap-4"
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ type: "spring", stiffness: 180, damping: 24, delay: 0.15 }}
            >
              {stage("center", "relative max-h-[min(66dvh,660px)] w-auto! drop-shadow-[0_20px_40px_rgb(var(--copie-accent-rgb)/0.18)]", "max-w-[760px] aspect-square")}
              <div className="relative z-10 flex flex-col items-center gap-2">
                <span className="font-label text-[10px] font-bold uppercase tracking-[0.2em] text-cyber-subtle">ลองเปลี่ยนบุคลิกของ COPIE</span>
                <ModeSwitcher value={mode} onChange={(next) => setMode(next)} />
              </div>

              <div className="pointer-events-none absolute right-0 top-[18%] flex select-none flex-col gap-8 font-label text-[10px] font-bold tracking-[0.2em] text-cyber-subtle">
                <div className="flex items-start gap-2">
                  <span className="mt-1 size-2 shrink-0 rounded-full bg-cyber-blue" />
                  <div className="leading-relaxed">
                    <p>ASK</p>
                    <p>EXPLORE</p>
                    <p>LEARN</p>
                    <p>GROW</p>
                    <p>TOGETHER</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="size-2 shrink-0 rounded-full bg-cyber-blue" />
                  <div className="font-bold text-cyber-strong">
                    <p>COPIE</p>
                    <p className="text-[9px] text-cyber-subtle">AI AGENT ONLINE</p>
                  </div>
                </div>
              </div>
            </motion.div>}
          </section>

          <footer className="relative z-30 flex items-center justify-between px-6 py-4 font-label text-[11px] font-bold tracking-[0.16em] text-cyber-subtle sm:px-12">
            <div className="flex items-center gap-2">
              <span className="h-0.5 w-6 bg-cyber-blue" />
              <span>YOUR IDEAS, BRIGHTER TOGETHER</span>
            </div>
          </footer>
        </main>
      </MascotModeProvider>
    </MotionConfig>
  );
}
