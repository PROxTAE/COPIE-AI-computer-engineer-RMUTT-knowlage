"use client";

import { useRef, useState, type KeyboardEvent } from "react";
import { Button, Modal } from "@heroui/react";
import { motion } from "motion/react";

import type { InteractionMode } from "@/types/contract";

import { hasSeenDevilIntro, markDevilIntroSeen } from "../chatStore";
import { Icon, type IconName } from "./Icon";

export type ModeOrigin = { x: number; y: number };

export const MODE_INFO: Record<InteractionMode, { label: string; hint: string; status: string; icon: IconName }> = {
  normal: { label: "Normal", hint: "เป็นมิตร ชัดเจน ชวนถามต่อ", status: "AI // ACTIVE", icon: "spark" },
  devil: { label: "Devil", hint: "ตรง ท้าทายเหตุผล ชวนลงมือพิสูจน์", status: "AI // DEVIL MODE", icon: "mode-devil" },
  developer: { label: "Developer", hint: "กระชับ เป็นขั้นตอน ใช้ตัวอย่างเทคนิค", status: "AI // DEV MODE", icon: "mode-developer" },
};

const ORDER: InteractionMode[] = ["normal", "devil", "developer"];

type ModeSwitcherProps = {
  value: InteractionMode;
  onChange: (mode: InteractionMode, origin: ModeOrigin) => void;
  className?: string;
};

export function ModeSwitcher({ value, onChange, className = "" }: ModeSwitcherProps) {
  const buttons = useRef<Partial<Record<InteractionMode, HTMLButtonElement | null>>>({});
  const [askDevil, setAskDevil] = useState<ModeOrigin | null>(null);

  function originOf(mode: InteractionMode): ModeOrigin {
    const rect = buttons.current[mode]?.getBoundingClientRect();
    return rect ? { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 } : { x: window.innerWidth / 2, y: 0 };
  }

  function choose(mode: InteractionMode) {
    if (mode === value) return;
    const origin = originOf(mode);
    if (mode === "devil" && !hasSeenDevilIntro()) {
      setAskDevil(origin);
      return;
    }
    onChange(mode, origin);
  }

  function onKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    const step = event.key === "ArrowRight" || event.key === "ArrowDown" ? 1 : event.key === "ArrowLeft" || event.key === "ArrowUp" ? -1 : 0;
    if (!step) return;
    event.preventDefault();
    const next = ORDER[(ORDER.indexOf(value) + step + ORDER.length) % ORDER.length];
    buttons.current[next]?.focus();
    choose(next);
  }

  return (
    <>
      <div
        role="radiogroup"
        aria-label="โหมดการคุยกับ COPIE"
        onKeyDown={onKeyDown}
        className={`relative inline-flex shrink-0 items-center gap-0.5 rounded-full border border-cyber-blue/25 bg-white/80 p-0.5 sm:p-1 shadow-xs backdrop-blur-sm ${className}`}
      >
        {ORDER.map((mode) => {
          const info = MODE_INFO[mode];
          const active = mode === value;
          return (
            <button
              key={mode}
              ref={(node) => { buttons.current[mode] = node; }}
              type="button"
              role="radio"
              aria-checked={active}
              aria-label={`${info.label} mode — ${info.hint}`}
              title={info.hint}
              tabIndex={active ? 0 : -1}
              onClick={() => choose(mode)}
              className={`relative inline-flex h-7 sm:h-8 items-center gap-1.5 rounded-full px-2 sm:px-2.5 font-label text-[11px] font-bold uppercase tracking-[0.12em] transition-colors cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-cyber-focus focus-visible:ring-offset-1 focus-visible:ring-offset-transparent ${
                active ? "text-cyber-on-accent" : "text-cyber-subtle hover:text-cyber-blue"
              }`}
            >
              {active && (
                <motion.span
                  layoutId="copie-mode-pill"
                  className="absolute inset-0 rounded-full bg-cyber-blue shadow-[0_0_14px_rgb(var(--copie-accent-rgb)/0.45)]"
                  transition={{ type: "spring", stiffness: 420, damping: 34 }}
                  aria-hidden="true"
                />
              )}
              <Icon name={info.icon} size={15} className="relative" />
              <span className="relative hidden md:inline">{info.label}</span>
            </button>
          );
        })}
      </div>

      <Modal isOpen={askDevil !== null} onOpenChange={(open) => { if (!open) setAskDevil(null); }}>
        <Modal.Backdrop className="bg-slate-950/40" isDismissable>
          <Modal.Container placement="center" size="md">
            <Modal.Dialog className="border border-cyber-line">
              <Modal.Header>
                <Modal.Heading className="flex items-center gap-2 font-display text-xl font-semibold text-cyber-ink">
                  <Icon name="mode-devil" size={22} className="text-[#f66cac]" />
                  เปิด Devil Mode?
                </Modal.Heading>
              </Modal.Header>
              <Modal.Body className="grid gap-2 text-sm leading-relaxed text-cyber-ink">
                <p>
                  Devil Mode เป็น<strong>สไตล์การคุย</strong>ที่ตรงและท้าทายขึ้น COPIE จะชวนตั้งคำถามกับสมมติฐาน
                  และผลักให้ลองลงมือพิสูจน์ แทนการปลอบใจอย่างเดียว
                </p>
                <p className="text-cyber-muted">
                  ข้อมูลภาควิชา รายวิชา คะแนน และแหล่งอ้างอิงยังเหมือนเดิมทุกอย่าง COPIE จะไม่ดูถูกหรือตัดสินตัวคุณ
                  และเปลี่ยนกลับเป็นโหมดปกติได้ทุกเมื่อ
                </p>
              </Modal.Body>
              <Modal.Footer>
                <Button variant="outline" onPress={() => setAskDevil(null)}>ยังก่อน</Button>
                <Button
                  variant="primary"
                  onPress={() => {
                    const origin = askDevil ?? originOf("devil");
                    markDevilIntroSeen();
                    setAskDevil(null);
                    onChange("devil", origin);
                  }}
                >
                  เปิด Devil Mode
                </Button>
              </Modal.Footer>
            </Modal.Dialog>
          </Modal.Container>
        </Modal.Backdrop>
      </Modal>
    </>
  );
}
