// แหล่งอ้างอิง — ม็อกอัพ 05-reading-mode ส่วนล่าง
// การ์ดเรียงเป็นกริด กดเพื่อกางดู snippet และเปิดเอกสารต้นทางในแท็บใหม่
// เลขในการ์ดตรงกับ badge [n] ใน TextResponse (1-based)
"use client";

import { useEffect, useRef } from "react";
import { BookOpen, ChevronDown, ExternalLink, FileText } from "lucide-react";
import { useReducedMotion } from "motion/react";
import type { Source } from "@/types/contract";

interface SourceViewerProps {
  sources: Source[];
  /** แหล่งที่กำลังกางอยู่ (1-based) — null คือปิดทั้งหมด */
  activeIndex: number | null;
  onActiveChange: (index: number | null) => void;
}

export function SourceViewer({ sources, activeIndex, onActiveChange }: SourceViewerProps) {
  if (sources.length === 0) return null;

  return (
    <section className="copie-panel flex flex-col gap-3" aria-label="แหล่งอ้างอิง">
      <h2 className="flex items-center gap-2 font-display text-base font-semibold text-deep-navy">
        <BookOpen aria-hidden="true" className="size-5 text-copie-teal" />
        แหล่งอ้างอิง
        <span className="text-sm font-normal text-muted tabular-nums">({sources.length})</span>
      </h2>

      <ul className="grid gap-3 @lg:grid-cols-2 @3xl:grid-cols-3">
        {sources.map((source, position) => (
          <SourceCard
            key={`${source.doc_id}-${position}`}
            source={source}
            index={position + 1}
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
  open,
  onToggle,
}: {
  source: Source;
  index: number;
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
    <li
      ref={item}
      id={`source-${index}`}
      className={`flex flex-col rounded-lg border bg-surface transition ${
        open ? "border-copie-teal" : "border-deep-navy/12"
      }`}
    >
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={open}
        aria-controls={panelId}
        className="flex items-start gap-2 p-3 text-left"
      >
        <FileText aria-hidden="true" className="mt-0.5 size-4 shrink-0 text-copie-teal" />
        <span className="min-w-0 flex-1">
          <span className="block text-sm font-medium text-deep-navy">{source.title}</span>
          <span className="block text-xs text-muted">
            <span className="tabular-nums">[{index}]</span>
            {source.section ? ` · ${source.section}` : ""}
          </span>
        </span>
        <ChevronDown
          aria-hidden="true"
          className={`mt-0.5 size-4 shrink-0 text-muted transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>

      {open && (
        <div id={panelId} className="flex flex-col gap-2 border-t border-deep-navy/10 p-3">
          <p className="text-sm leading-6 text-ink">{source.snippet}</p>
          {source.url ? (
            <a
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 self-start text-sm font-medium text-copie-teal underline underline-offset-2"
            >
              <ExternalLink aria-hidden="true" className="size-4" />
              เปิดเอกสารต้นทาง
            </a>
          ) : (
            <p className="text-xs text-muted">ยังไม่มีลิงก์เอกสารต้นทาง</p>
          )}
        </div>
      )}
    </li>
  );
}
