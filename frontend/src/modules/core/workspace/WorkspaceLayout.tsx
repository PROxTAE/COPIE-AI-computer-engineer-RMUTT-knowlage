"use client";

import type { CSSProperties, ReactNode } from "react";
import { Button } from "@heroui/react";
import { ArrowLeft, Eye, SquarePen } from "lucide-react";
import { MotionConfig, motion } from "motion/react";

import { MascotStage, type CopieMascotState } from "@/modules/mascot";
import type { InteractionMode } from "@/types/contract";

import type { WorkspaceMode } from "../chatStore";
import { StatusLabel } from "../ui";
import { MascotSidebar } from "./MascotSidebar";
import { MASCOT_LAYOUT_ID, MASCOT_MORPH, PANEL_ENTER } from "./mascotMorph";

type WorkspaceLayoutProps = {
  layout: WorkspaceMode;
  copieState: CopieMascotState;
  interactionMode?: InteractionMode;
  hasResponse: boolean;
  isInteractive?: boolean;
  mascotQuote?: string;
  onAsk?: (text: string) => void;
  onHide: () => void;
  onShow: () => void;
  onBack?: () => void;
  onRead?: () => void;
  onNewChat?: () => void;
  children: ReactNode;
};

const barButton =
  "inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 font-display text-xs sm:text-sm font-bold transition-colors cursor-pointer";

const layoutClass: Record<WorkspaceMode, string> = {
  // A size container: the mascot reads the free height (cqh) so it always fits without scrolling,
  // even when the browser is zoomed to 125-150%.
  center: "flex items-center justify-center overflow-clip [container-type:size]",
  split: "flex flex-col lg:grid h-full min-h-0 gap-6 lg:grid-cols-[minmax(0,1fr)_320px] xl:grid-cols-[minmax(0,1fr)_360px] overflow-hidden items-stretch",
  rail: "flex flex-col lg:grid h-full min-h-0 gap-6 lg:grid-cols-[minmax(0,1fr)_300px] xl:grid-cols-[minmax(0,1fr)_340px] overflow-hidden items-stretch",
  hidden: "block h-full min-h-0 overflow-y-auto",
};

export function WorkspaceLayout({
  layout,
  copieState,
  interactionMode = "normal",
  hasResponse,
  isInteractive = false,
  mascotQuote,
  onAsk,
  onHide,
  onShow,
  onBack,
  onRead,
  onNewChat,
  children,
}: WorkspaceLayoutProps) {
  const showPanel = layout !== "center";
  const showMascot = layout !== "hidden";
  const showReadButton = hasResponse && Boolean(onRead);
  // Height kept free below COPIE for the status label, the mode line and the "read answer" button.
  // The button's 3.5rem is always reserved (the button itself is pinned to the stage bottom), so
  // showing or hiding it never resizes the mascot or moves anything else.
  const mascotReserve = 3 + (interactionMode !== "normal" ? 2 : 0) + 3.5;

  return (
    <MotionConfig reducedMotion="user">
      <section
        className={`relative z-10 min-h-0 flex-1 px-4 sm:px-8 lg:px-12 py-2 sm:py-3 w-full max-w-[1760px] mx-auto ${layoutClass[layout]}`}
        data-layout={layout}
      >
        {showPanel && (
          <motion.div
            initial={{ opacity: 0, x: -28 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ ...PANEL_ENTER, delay: 0.08 }}
            className={`relative z-10 flex min-w-0 flex-col self-stretch ${
              layout === "rail" || layout === "split" ? "h-full min-h-0" : ""
            } ${layout === "hidden" ? "mx-auto max-w-5xl" : "w-full"}`}
          >
            <div
              className={`min-h-40 min-w-0 ${
                layout === "rail" || layout === "split"
                  ? "flex-1 overflow-y-auto pr-2 pb-6 copie-scroll"
                  : ""
              }`}
              aria-label="คำตอบของ COPIE"
            >
              {/* Stays pinned while the answer scrolls, so going back never needs scrolling up. */}
              <nav
                aria-label="การนำทางคำตอบ"
                data-dock-guard="top"
                className="sticky top-0 z-20 mb-3 flex items-center justify-between gap-2 rounded-2xl border border-cyber-edge/70 bg-white/85 p-1 shadow-xs backdrop-blur-md"
              >
                {onBack && (
                  <button type="button" onClick={onBack} className={`${barButton} text-cyber-blue hover:bg-blue-50`}>
                    <ArrowLeft className="size-4" />
                    กลับหน้าแชทหลัก
                  </button>
                )}
                <div className="ml-auto flex items-center gap-1">
                  {layout === "hidden" && (
                    <button type="button" onClick={onShow} className={`${barButton} text-cyber-subtle hover:bg-blue-50 hover:text-cyber-blue`}>
                      <Eye className="size-4" />
                      <span className="hidden sm:inline">แสดงมาสคอต</span>
                    </button>
                  )}
                  {onNewChat && (
                    <button type="button" onClick={onNewChat} className={`${barButton} text-cyber-subtle hover:bg-blue-50 hover:text-cyber-blue`}>
                      <SquarePen className="size-4" />
                      <span className="hidden sm:inline">แชทใหม่</span>
                    </button>
                  )}
                </div>
              </nav>
              {hasResponse ? children : <p className="text-cyber-muted">คำตอบจะแสดงที่นี่</p>}
            </div>
          </motion.div>
        )}
        {showMascot && (
          layout === "center" ? (
            <div
              className="relative z-10 flex min-w-0 flex-col items-center justify-center w-full my-auto shrink-0 px-2 py-1"
              style={{ "--copie-mascot-reserve": `${mascotReserve}rem` } as CSSProperties}
            >
              <motion.div layoutId={MASCOT_LAYOUT_ID} transition={MASCOT_MORPH} className="relative">
              <MascotStage
                state={copieState}
                mode={interactionMode}
                layout="center"
                priority
                chatter={!hasResponse}
                haloClassName="w-[240px] sm:w-[380px] md:w-[500px] lg:w-[650px] max-w-[88vw] aspect-square"
                imageClassName="relative max-h-[min(calc(100cqh_-_var(--copie-mascot-reserve)),260px)] sm:max-h-[min(calc(100cqh_-_var(--copie-mascot-reserve)),360px)] md:max-h-[min(calc(100cqh_-_var(--copie-mascot-reserve)),460px)] lg:max-h-[min(calc(100cqh_-_var(--copie-mascot-reserve)),560px)] 2xl:max-h-[min(calc(100cqh_-_var(--copie-mascot-reserve)),680px)] w-auto! drop-shadow-[0_16px_32px_rgb(var(--copie-accent-rgb)/0.18)]"
              />
              </motion.div>
              <StatusLabel label={`COPIE / ${copieState}`} className="relative mt-2 text-[10px] sm:text-xs" />
              {interactionMode !== "normal" && <div className="copie-mode-effect relative mt-1" aria-hidden="true" />}
            </div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
              className="relative z-10 hidden lg:flex min-w-0 flex-col h-full self-stretch shrink-0 border-l border-cyber-edge/60 pl-3 xl:pl-5"
            >
              <MascotSidebar
                copieState={copieState}
                interactionMode={interactionMode}
                quote={mascotQuote}
                onHide={onHide}
                onAsk={onAsk}
                showQuickActions={!isInteractive}
              />
            </motion.div>
          )
        )}
        {/* Pinned to the bottom of the stage, just above the input: out of the flow, so it can
            never push the mascot or the top bar. */}
        {layout === "center" && showReadButton && (
          <div className="pointer-events-none absolute inset-x-0 bottom-2 z-20 flex justify-center px-4">
            <Button
              variant="outline"
              onPress={onRead}
              className="pointer-events-auto rounded-full border-cyber-blue/40 bg-cyber-surface text-cyber-strong shadow-md font-semibold text-xs sm:text-sm hover:border-cyber-blue hover:text-cyber-blue"
            >
              {isInteractive ? "ดูผลวิเคราะห์ทักษะ" : "อ่านคำตอบ"}
            </Button>
          </div>
        )}
      </section>
    </MotionConfig>
  );
}

