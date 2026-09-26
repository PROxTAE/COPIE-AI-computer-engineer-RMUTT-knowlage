"use client";

import type { ReactNode } from "react";
import { Button } from "@heroui/react";
import { MotionConfig, motion } from "motion/react";

import { CopieMascot, type CopieMascotState } from "@/modules/mascot";

import type { WorkspaceMode } from "../chatStore";
import { Icon, StatusLabel } from "../ui";

type WorkspaceLayoutProps = {
  layout: WorkspaceMode;
  copieState: CopieMascotState;
  hasResponse: boolean;
  onHide: () => void;
  onShow: () => void;
  onBack?: () => void;
  onRead?: () => void;
  children: ReactNode;
};

const layoutClass: Record<WorkspaceMode, string> = {
  center: "flex items-center justify-center",
  split: "grid content-center gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(320px,0.9fr)]",
  rail: "grid content-start gap-5 lg:grid-cols-[minmax(0,1fr)_300px]",
  hidden: "block",
};

export function WorkspaceLayout({ layout, copieState, hasResponse, onHide, onShow, onBack, onRead, children }: WorkspaceLayoutProps) {
  const showPanel = layout !== "center";
  const showMascot = layout !== "hidden";

  return (
    <MotionConfig reducedMotion="user">
      <section className={`relative z-10 min-h-0 flex-1 overflow-y-auto px-5 py-4 sm:px-10 ${layoutClass[layout]}`} data-layout={layout}>
        {showPanel && (
          <motion.div layout transition={{ duration: 0.42 }} className={`relative z-10 min-w-0 ${layout === "hidden" ? "mx-auto max-w-5xl" : ""}`}>
            <div className="mb-3 flex items-center justify-between gap-3">
              <span className="copie-eyebrow">AI answer</span>
              {layout === "rail" && onBack && (
                <Button variant="outline" onPress={onBack} className="rounded-full bg-white">
                  <Icon name="arrow-left" size={17} /> กลับหน้าสนทนา
                </Button>
              )}
              {layout === "hidden" && (
                <Button variant="outline" onPress={onShow} className="rounded-full">
                  แสดงมาสคอต
                </Button>
              )}
            </div>
            <div className="copie-panel min-h-40 overflow-hidden p-5 sm:p-7" aria-label="คำตอบของ COPIE">
              {hasResponse ? children : <p className="text-cyber-muted">คำตอบจะแสดงที่นี่</p>}
            </div>
          </motion.div>
        )}
        {showMascot && (
          <motion.div layout transition={{ duration: 0.42 }} className={`relative z-10 flex min-w-0 flex-col items-center justify-center ${layout === "center" ? "w-full" : ""}`}>
            <div className={`copie-halo absolute ${layout === "rail" ? "max-w-[320px]" : layout === "split" ? "max-w-[600px]" : "max-w-[650px]"}`} aria-hidden="true" />
            <CopieMascot
              state={copieState}
              layout={layout === "rail" ? "rail" : "center"}
              priority
              className={layout === "center" ? "relative max-h-[min(60dvh,560px)] w-auto!" : layout === "rail" ? "relative max-h-[min(38dvh,330px)] w-auto!" : "relative max-h-[min(58dvh,540px)] w-auto!"}
            />
            <StatusLabel label={`COPIE / ${copieState}`} className="relative mt-1" />
            {layout === "center" && hasResponse && onRead && (
              <Button variant="outline" onPress={onRead} className="relative mt-4 rounded-full bg-white">
                อ่านคำตอบ
              </Button>
            )}
            {showPanel && (
              <Button variant="outline" onPress={onHide} className="relative mt-4 rounded-full bg-white">
                <Icon name="eye-off" size={17} /> ซ่อนมาสคอต
              </Button>
            )}
          </motion.div>
        )}
      </section>
    </MotionConfig>
  );
}
