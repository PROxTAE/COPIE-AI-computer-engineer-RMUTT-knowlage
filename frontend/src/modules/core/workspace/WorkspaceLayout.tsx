"use client";

import type { ReactNode } from "react";
import { Button } from "@heroui/react";
import { MotionConfig, motion } from "motion/react";

import { CopieMascot, type CopieMascotState } from "@/modules/mascot";

import type { WorkspaceMode } from "../chatStore";
import { Icon, StatusLabel } from "../ui";
import { MascotSidebar } from "./MascotSidebar";

type WorkspaceLayoutProps = {
  layout: WorkspaceMode;
  copieState: CopieMascotState;
  hasResponse: boolean;
  isInteractive?: boolean;
  mascotQuote?: string;
  onAsk?: (text: string) => void;
  onHide: () => void;
  onShow: () => void;
  onBack?: () => void;
  onRead?: () => void;
  children: ReactNode;
};

const layoutClass: Record<WorkspaceMode, string> = {
  center: "flex items-center justify-center overflow-y-auto",
  split: "flex flex-col lg:grid h-full min-h-0 gap-6 lg:grid-cols-[minmax(0,1fr)_320px] xl:grid-cols-[minmax(0,1fr)_360px] overflow-hidden items-stretch",
  rail: "flex flex-col lg:grid h-full min-h-0 gap-6 lg:grid-cols-[minmax(0,1fr)_300px] xl:grid-cols-[minmax(0,1fr)_340px] overflow-hidden items-stretch",
  hidden: "block h-full min-h-0 overflow-y-auto",
};

export function WorkspaceLayout({
  layout,
  copieState,
  hasResponse,
  isInteractive = false,
  mascotQuote,
  onAsk,
  onHide,
  onShow,
  onBack,
  onRead,
  children,
}: WorkspaceLayoutProps) {
  const showPanel = layout !== "center";
  const showMascot = layout !== "hidden";

  return (
    <MotionConfig reducedMotion="user">
      <section
        className={`relative z-10 min-h-0 flex-1 px-4 sm:px-8 lg:px-12 py-2 sm:py-3 w-full max-w-[1760px] mx-auto ${layoutClass[layout]}`}
        data-layout={layout}
      >
        {showPanel && (
          <motion.div
            layout
            transition={{ duration: 0.42 }}
            className={`relative z-10 flex min-w-0 flex-col self-stretch ${
              layout === "rail" || layout === "split" ? "h-full min-h-0" : ""
            } ${layout === "hidden" ? "mx-auto max-w-5xl" : "w-full"}`}
          >
            {layout === "hidden" && (
              <div className="mb-2 flex shrink-0 justify-end">
                <Button variant="outline" onPress={onShow} className="rounded-full bg-white text-xs">
                  แสดงมาสคอต
                </Button>
              </div>
            )}
            <div
              className={`min-h-40 min-w-0 ${
                layout === "rail" || layout === "split"
                  ? "flex-1 overflow-y-auto pr-2 pb-6 copie-scroll"
                  : ""
              }`}
              aria-label="คำตอบของ COPIE"
            >
              {hasResponse ? children : <p className="text-cyber-muted">คำตอบจะแสดงที่นี่</p>}
            </div>
          </motion.div>
        )}
        {showMascot && (
          layout === "center" ? (
            <motion.div
              layout
              transition={{ duration: 0.42 }}
              className="relative z-10 flex min-w-0 flex-col items-center justify-center w-full my-auto shrink-0 px-2 py-1"
            >
              <div
                className="copie-halo absolute w-[240px] sm:w-[380px] md:w-[500px] lg:w-[650px] max-w-[88vw] aspect-square pointer-events-none"
                aria-hidden="true"
              />
              <CopieMascot
                state={copieState}
                layout="center"
                priority
                className="relative max-h-[min(26dvh,210px)] sm:max-h-[min(36dvh,320px)] md:max-h-[min(48dvh,440px)] lg:max-h-[min(54dvh,500px)] w-auto! drop-shadow-[0_16px_32px_rgba(21,95,242,0.18)]"
              />
              <StatusLabel label={`COPIE / ${copieState}`} className="relative mt-2 text-[10px] sm:text-xs" />
              {hasResponse && onRead && (
                <Button variant="outline" onPress={onRead} className="relative mt-3 rounded-full bg-white shadow-sm font-semibold text-xs sm:text-sm">
                  {isInteractive ? "ดูผลวิเคราะห์ทักษะ" : "อ่านคำตอบ"}
                </Button>
              )}
            </motion.div>
          ) : (
            <motion.div
              layout
              transition={{ duration: 0.42 }}
              className="relative z-10 hidden lg:flex min-w-0 flex-col h-full self-stretch shrink-0 border-l border-[#d2e0f5]/60 pl-3 xl:pl-5"
            >
              <MascotSidebar
                copieState={copieState}
                quote={mascotQuote}
                onHide={onHide}
                onAsk={onAsk}
                showQuickActions={!isInteractive}
              />
            </motion.div>
          )
        )}
      </section>
    </MotionConfig>
  );
}

