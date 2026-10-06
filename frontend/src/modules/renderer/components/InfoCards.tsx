// การ์ดข้อมูล — ม็อกอัพ 08-info-cards
// ไอคอนในกรอบสี่เหลี่ยมมน + หัวข้อ + เนื้อหา markdown + tag chips + ปุ่ม "ดูรายละเอียด"
"use client";

import { ArrowRight, FileText } from "lucide-react";
import { motion } from "motion/react";
import { DynamicIcon, iconNames, type IconName } from "lucide-react/dynamic";
import type { CardsData, InfoCard } from "@/types/contract";
import { Markdown } from "./Markdown";

const FALLBACK_ICON: IconName = "book-open";

interface InfoCardsProps {
  data: CardsData;
  onAsk: (text: string) => void;
  disabled?: boolean;
  animate?: boolean;
}

export function InfoCards({ data, onAsk, disabled = false, animate = true }: InfoCardsProps) {
  if (data.cards.length === 0) return null;

  return (
    <section className="flex flex-col gap-6" aria-label="สำรวจข้อมูลภาควิชา">
      {/* Top Header */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="size-2 bg-cyber-blue" />
            <span className="font-label text-xs font-bold tracking-[0.2em] text-cyber-blue uppercase">
              AI RESPONSE
            </span>
          </div>
          <span className="hidden sm:inline font-label text-[10px] font-bold tracking-[0.2em] text-cyber-subtle uppercase">
            KNOWLEDGE TODAY // A BRIGHTER TOMORROW
          </span>
        </div>

        <div>
          <div className="flex items-center">
            <span className="inline-block w-1.5 h-8 bg-cyber-glow rounded-full mr-3 shrink-0" />
            <h1 className="copie-heading font-display text-3xl sm:text-4xl font-black italic tracking-tight text-cyber-strong">
              สำรวจข้อมูลภาควิชา
            </h1>
          </div>

          <div className="text-sm font-medium text-cyber-subtle mt-2 pl-4 leading-relaxed">
            <p>นี่คือข้อมูลสรุปของภาควิชาวิศวกรรมคอมพิวเตอร์ เพื่อให้คุณเข้าใจภาพรวมหลักสูตร รายวิชา และทักษะที่จะได้รับ</p>
            <p>รายละเอียดอาจแตกต่างกันตามแต่ละสถาบันการศึกษา โปรดตรวจสอบข้อมูลล่าสุดจากคณะ/มหาวิทยาลัยของคุณอีกครั้ง</p>
          </div>
        </div>
      </div>

      {/* 3 Cards Row */}
      <ul className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        {data.cards.map((card, position) => (
          <Card
            key={`${card.title}-${position}`}
            card={card}
            index={position}
            onAsk={onAsk}
            disabled={disabled}
            animate={animate}
          />
        ))}
      </ul>

      {/* Reference Bar Below */}
      <div className="flex items-center gap-4 rounded-xl border border-cyber-edge bg-white p-4 shadow-xs">
        <div className="flex size-10 items-center justify-center rounded-xl bg-blue-50 text-cyber-blue shrink-0">
          <FileText className="size-5" />
        </div>
        <div>
          <p className="font-display font-bold text-sm text-cyber-strong">แหล่งข้อมูล</p>
          <p className="text-xs text-cyber-subtle">ข้อมูลจากเอกสารประกอบการเรียน / หลักสูตรของมหาวิทยาลัย</p>
        </div>
      </div>
    </section>
  );
}

function Card({
  card,
  index,
  onAsk,
  disabled,
  animate,
}: {
  card: InfoCard;
  index: number;
  onAsk: (text: string) => void;
  disabled: boolean;
  animate: boolean;
}) {
  const getSubLabel = (idx: number, title: string) => {
    if (idx === 0 || title.includes("หลักสูตร")) return "OVERVIEW";
    if (idx === 1 || title.includes("วิชา")) return "CURRICULUM";
    return "SKILLS";
  };

  return (
    <motion.li
      initial={animate ? { opacity: 0, y: 8 } : false}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: animate ? index * 0.04 : 0 }}
      className="flex flex-col gap-3.5 rounded-2xl border border-cyber-edge bg-white p-6 shadow-xs hover:shadow-md hover:border-cyber-blue/40 transition-all"
    >
      <div className="flex items-center gap-3">
        <span className="flex size-12 items-center justify-center rounded-xl bg-blue-50 text-cyber-blue shrink-0">
          <DynamicIcon name={toIconName(card.icon)} aria-hidden="true" className="size-6 text-cyber-blue" />
        </span>
        <div>
          <span className="font-label text-[10px] font-bold tracking-[0.16em] text-cyber-subtle uppercase block">
            {getSubLabel(index, card.title)}
          </span>
          <h3 className="copie-heading font-display text-xl font-bold text-cyber-strong">{card.title}</h3>
        </div>
      </div>

      <div className="text-sm leading-relaxed text-cyber-strong/80 font-medium">
        <Markdown className="flex flex-col gap-2">{card.body}</Markdown>
      </div>

      {card.tags.length > 0 && (
        <ul className="flex flex-wrap gap-1.5 mt-auto pt-2">
          {card.tags.map((tag) => (
            <li
              key={tag}
              className="rounded-full bg-blue-50/80 px-3 py-1 font-display text-xs font-semibold text-cyber-blue"
            >
              {tag}
            </li>
          ))}
        </ul>
      )}

      <button
        type="button"
        onClick={() => onAsk(`ขอรายละเอียดเพิ่มเติมเกี่ยวกับ${card.title}`)}
        disabled={disabled}
        className="group inline-flex items-center gap-2 pt-2 text-sm font-bold text-cyber-blue hover:text-blue-700 transition-colors cursor-pointer disabled:opacity-50"
      >
        <span>ดูรายละเอียด</span>
        <ArrowRight aria-hidden="true" className="size-4 group-hover:translate-x-1 transition-transform" />
      </button>
    </motion.li>
  );
}

function toIconName(raw: string | null): IconName {
  if (!raw) return FALLBACK_ICON;
  const normalized = raw.trim().toLowerCase().replace(/[\s_]+/g, "-");
  return (iconNames as readonly string[]).includes(normalized) ? (normalized as IconName) : FALLBACK_ICON;
}
