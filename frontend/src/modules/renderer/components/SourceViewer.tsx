// แหล่งอ้างอิง — ม็อกอัพ 05-reading-mode ส่วนล่าง
// การ์ดเรียงเป็นกริด กดเพื่อกางดู snippet และเปิดเอกสารต้นทางในแท็บใหม่
// เลขในการ์ดตรงกับ badge [n] ใน TextResponse (1-based)
"use client";

import { useEffect, useRef } from "react";
import { BookOpen, ChevronDown, ExternalLink, FileText } from "lucide-react";
import { motion, useReducedMotion } from "motion/react";
import type { Source } from "@/types/contract";
import { FOCUS_RING } from "./styles";

interface SourceViewerProps {
  sources: Source[];
  /** แหล่งที่กำลังกางอยู่ (1-based) — null คือปิดทั้งหมด */
  activeIndex: number | null;
  onActiveChange: (index: number | null) => void;
}

export function SourceViewer({ sources, activeIndex, onActiveChange }: SourceViewerProps) {
  if (sources.length === 0) return null;

  return (
    <section className="copie-panel flex flex-col gap-3.5 p-4 sm:p-6" aria-label="แหล่งอ้างอิง">
      <h2 className="flex items-center gap-2 font-display text-base font-semibold text-deep-navy">
        <BookOpen aria-hidden="true" className="size-5 text-copie-teal" />
        แหล่งอ้างอิง
        <span className="text-sm font-normal text-muted tabular-nums">({sources.length})</span>
      </h2>

      <ul className="grid gap-3.5 @lg:grid-cols-2 @3xl:grid-cols-3">
        {sources.map((source, position) => (
          <SourceCard
            key={`${source.doc_id}-${position}`}
            source={source}
            index={position + 1}
            order={position}
            open={activeIndex === position + 1}
            onToggle={() => onActiveChange(activeIndex === position + 1 ? null : position + 1)}
          />
        ))}
      </ul>
    </section>
  );
}

function SourceCard({
  source,
  index,
  order,
  open,
  onToggle,
}: {
  source: Source;
  index: number;
  order: number;
  open: boolean;
  onToggle: () => void;
}) {
  const item = useRef<HTMLLIElement>(null);
  const reducedMotion = useReducedMotion();

  // กด badge [n] ในคำตอบแล้วต้องเลื่อนมาเห็นการ์ดใบนี้
  useEffect(() => {
    if (open) {
      item.current?.scrollIntoView({ block: "nearest", behavior: reducedMotion ? "auto" : "smooth" });
    }
  }, [open, reducedMotion]);

  const panelId = `source-panel-${index}`;

  return (
    <motion.li
      ref={item}
      id={`source-${index}`}
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, delay: order * 0.04 }}
      className={`flex flex-col rounded-xl border bg-white transition ${
        open ? "border-copie-teal shadow-xs ring-1 ring-copie-teal/25" : "border-deep-navy/12 hover:border-deep-navy/25"
      }`}
    >
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={open}
        aria-controls={panelId}
        className="flex items-start gap-2.5 rounded-xl p-3.5 text-left transition-colors hover:bg-slate-50/70 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-copie-teal"
      >
        <FileText aria-hidden="true" className="mt-0.5 size-4 shrink-0 text-copie-teal" />
        <span className="min-w-0 flex-1">
          <span className="block text-sm font-medium text-deep-navy">{source.title}</span>
          <span className="block text-xs text-muted mt-0.5">
            <span className="tabular-nums font-semibold text-copie-teal">[{index}]</span>
            {source.section ? ` · ${source.section}` : ""}
          </span>
        </span>
        <ChevronDown
          aria-hidden="true"
          className={`mt-0.5 size-4 shrink-0 text-muted transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>

      {open && (
        <div id={panelId} className="flex flex-col gap-2.5 border-t border-deep-navy/10 p-4 bg-slate-50/50 rounded-b-xl">
          <p className="text-sm leading-6 text-ink">{source.snippet}</p>
          {source.url ? (
            <a
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className={`inline-flex items-center gap-1.5 self-start rounded text-sm font-medium text-copie-teal underline underline-offset-2 ${FOCUS_RING}`}
            >
              <ExternalLink aria-hidden="true" className="size-4" />
              เปิดเอกสารต้นทาง
            </a>
          ) : (
            <p className="text-xs text-muted">ยังไม่มีลิงก์เอกสารต้นทาง</p>
          )}
        </div>
      )}
    </motion.li>
  );
}
