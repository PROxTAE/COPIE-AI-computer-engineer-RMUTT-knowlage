// การ์ดข้อมูล — ม็อกอัพ 08-info-cards
// ไอคอนในกรอบสี่เหลี่ยมมน + หัวข้อ + เนื้อหา markdown + tag chips + ปุ่ม "ดูรายละเอียด"
// ปุ่มไม่ยิง API เอง แต่ส่งคำถามกลับไปให้ chatStore ผ่าน onAsk
"use client";

import { ArrowRight } from "lucide-react";
import { motion } from "motion/react";
import { DynamicIcon, iconNames, type IconName } from "lucide-react/dynamic";
import type { CardsData, InfoCard } from "@/types/contract";
import { Markdown } from "./Markdown";

const FALLBACK_ICON: IconName = "book-open";

interface InfoCardsProps {
  data: CardsData;
  onAsk: (text: string) => void;
  disabled?: boolean;
}

export function InfoCards({ data, onAsk, disabled = false }: InfoCardsProps) {
  if (data.cards.length === 0) return null;

  return (
    <ul className="grid gap-4 @lg:grid-cols-2 @3xl:grid-cols-3">
      {data.cards.map((card, position) => (
        <Card key={`${card.title}-${position}`} card={card} index={position} onAsk={onAsk} disabled={disabled} />
      ))}
    </ul>
  );
}

function Card({
  card,
  index,
  onAsk,
  disabled,
}: {
  card: InfoCard;
  index: number;
  onAsk: (text: string) => void;
  disabled: boolean;
}) {
  return (
    <motion.li
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: index * 0.04 }}
      className="copie-panel flex flex-col gap-3 rounded-xl border border-deep-navy/12 bg-surface p-4"
    >
      <span className="flex size-11 items-center justify-center rounded-xl border border-copie-teal/25 bg-copie-teal/8">
        <DynamicIcon name={toIconName(card.icon)} aria-hidden="true" className="size-5 text-copie-teal" />
      </span>

      <h3 className="copie-heading font-display text-lg font-bold text-deep-navy">{card.title}</h3>

      <Markdown className="flex flex-col gap-2 text-sm leading-6">{card.body}</Markdown>

      {card.tags.length > 0 && (
        <ul className="flex flex-wrap gap-1.5">
          {card.tags.map((tag) => (
            <li
              key={tag}
              className="rounded-full border border-copie-teal/25 bg-copie-teal/8 px-2.5 py-1 text-xs text-deep-navy"
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
        className="mt-auto inline-flex items-center gap-1.5 self-start rounded border-t border-deep-navy/10 pt-3 text-sm font-medium text-copie-teal disabled:opacity-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-copie-teal"
      >
        ดูรายละเอียด
        <ArrowRight aria-hidden="true" className="size-4" />
      </button>
    </motion.li>
  );
}

// contract ส่ง icon มาเป็นชื่อ lucide แบบ kebab-case เช่น "cpu"
// ชื่อที่ไม่มีอยู่จริง (หรือ null) ให้ใช้ book-open ตามที่แผนกำหนด
function toIconName(raw: string | null): IconName {
  if (!raw) return FALLBACK_ICON;
  const normalized = raw.trim().toLowerCase().replace(/[\s_]+/g, "-");
  return (iconNames as readonly string[]).includes(normalized) ? (normalized as IconName) : FALLBACK_ICON;
}
