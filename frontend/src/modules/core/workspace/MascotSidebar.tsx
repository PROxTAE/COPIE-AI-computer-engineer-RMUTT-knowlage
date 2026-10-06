"use client";

import { EyeOff, BookOpen, Lightbulb, ListPlus, Compass } from "lucide-react";
import { MascotStage, type CopieMascotState } from "@/modules/mascot";
import type { InteractionMode } from "@/types/contract";

interface MascotSidebarProps {
  copieState: CopieMascotState;
  interactionMode?: InteractionMode;
  quote?: string;
  onHide?: () => void;
  onAsk?: (text: string) => void;
  showQuickActions?: boolean;
}

const QUICK_ACTIONS = [
  {
    icon: BookOpen,
    label: "สรุปเนื้อหา",
    prompt: "ช่วยสรุปเนื้อหาสำคัญให้หน่อยครับ",
  },
  {
    icon: Lightbulb,
    label: "อธิบายเพิ่มเติม",
    prompt: "ช่วยอธิบายเนื้อหาเพิ่มเติมอย่างละเอียดครับ",
  },
  {
    icon: ListPlus,
    label: "แนะนำหัวข้อที่เกี่ยวข้อง",
    prompt: "มีหัวข้อที่เกี่ยวข้องอะไรบ้างที่ควรรู้",
  },
  {
    icon: Compass,
    label: "ค้นหาแหล่งข้อมูลเพิ่มเติม",
    prompt: "แนะนำแหล่งข้อมูลหรือเอกสารอ้างอิงเพิ่มเติมหน่อยครับ",
  },
];

export function MascotSidebar({
  copieState,
  interactionMode = "normal",
  quote = "“พร้อมช่วยค้นหา เรียนรู้ และเติบโตไปด้วยกัน”",
  onHide,
  onAsk,
  showQuickActions = true,
}: MascotSidebarProps) {
  return (
    <aside className="relative flex flex-col items-center justify-between w-full h-full min-h-0 py-2 px-3">
      {/* Top Header Row in Sidebar */}
      <div className="flex w-full items-center justify-between gap-2 shrink-0 mb-2">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-cyber-blue shadow-[0_0_8px_var(--copie-cyber-blue)]" />
          <span className="font-label text-[11px] font-bold tracking-[0.14em] text-cyber-strong uppercase">
            COPIE <span className="text-cyber-subtle">/ AI AGENT ONLINE</span>
          </span>
        </div>
        {onHide && (
          <button
            type="button"
            onClick={onHide}
            className="inline-flex shrink-0 items-center gap-1.5 whitespace-nowrap rounded-full border border-cyber-edge bg-white/90 px-3 py-1 text-[11px] font-semibold text-cyber-strong shadow-xs hover:border-cyber-blue/40 hover:bg-slate-50 transition-all cursor-pointer"
          >
            <EyeOff className="size-3.5 text-cyber-blue" />
            ซ่อนมาสคอต
          </button>
        )}
      </div>

      {/* Mascot Center with Halo */}
      <div className="relative flex flex-col items-center justify-center flex-1 w-full min-h-0 my-auto py-2">
        {/* Mascot on its interactive stage (halo, parallax, reactions) */}
        <div className="relative z-10 flex items-center justify-center">
          <MascotStage
            state={copieState}
            mode={interactionMode}
            layout="rail"
            priority
            haloClassName="max-w-[280px] xl:max-w-[320px] aspect-square opacity-90"
            imageClassName="max-h-[min(30dvh,240px)] xl:max-h-[min(35dvh,280px)] w-auto! drop-shadow-[0_12px_24px_rgb(var(--copie-accent-rgb)/0.15)]"
          />
        </div>

        {/* Mascot Quote & Tagline */}
        <div className="relative z-10 mt-3 text-center px-2 max-w-[280px]">
          <p className="font-display text-sm xl:text-base font-bold text-cyber-strong leading-snug">
            {quote}
          </p>
          <p className="mt-1 font-label text-[9px] xl:text-[10px] font-semibold tracking-[0.18em] text-cyber-subtle uppercase">
            YOUR IDEAS, BRIGHTER TOGETHER
          </p>
        </div>
      </div>

      {/* Quick Action Menu Buttons */}
      {showQuickActions && onAsk && (
        <div className="w-full flex flex-col gap-2 shrink-0 pt-3 border-t border-cyber-edge/60 mt-auto">
          {QUICK_ACTIONS.map((action) => {
            const Icon = action.icon;
            return (
              <button
                key={action.label}
                type="button"
                onClick={() => onAsk(action.prompt)}
                className="group flex w-full items-center gap-3 rounded-xl border border-transparent px-3 py-2 text-left text-sm font-medium text-cyber-strong hover:border-cyber-edge hover:bg-white/80 transition-all cursor-pointer"
              >
                <div className="flex size-7 items-center justify-center rounded-lg bg-blue-50 text-cyber-blue group-hover:bg-cyber-blue group-hover:text-cyber-on-accent transition-colors shrink-0">
                  <Icon className="size-4" />
                </div>
                <span className="truncate">{action.label}</span>
              </button>
            );
          })}
        </div>
      )}
    </aside>
  );
}
