// แบบประเมินทักษะ — ม็อกอัพ 09-assessment-intro และ 10-assessment-question
// 2 ขั้น: หน้าแนะนำ -> ตอบทีละข้อ
// ฟอร์มไม่ยิง API เอง ส่งคำตอบทั้งชุดออกทาง onSubmit ให้ chatStore ของ P1
"use client";

import { useState } from "react";
import { ArrowLeft, ArrowRight, CircleCheck, Info, ListChecks } from "lucide-react";
import type { AssessmentFormData } from "@/types/contract";
import { SKILL_ORDER } from "./skillLabels";

type Stage = "intro" | "questions" | "later" | "done";

const SECONDS_PER_QUESTION = 15; // ใช้ประมาณเวลาที่แสดงในหน้าแนะนำเท่านั้น

interface AssessmentFormProps {
  data: AssessmentFormData;
  onSubmit: (answers: { question_id: string; value: number }[]) => Promise<void>;
  disabled?: boolean;
}

export function AssessmentForm({ data, onSubmit, disabled = false }: AssessmentFormProps) {
  const [stage, setStage] = useState<Stage>("intro");
  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const total = data.questions.length;
  const question = data.questions[current];
  const answered = question ? answers[question.id] : undefined;
  const isLast = current === total - 1;
  const locked = disabled || submitting;

  if (total === 0) return null;

  if (stage === "done") {
    return (
      <p className="flex items-center gap-2 rounded-xl border border-success/30 bg-success/10 px-4 py-3 text-success">
        <CircleCheck aria-hidden="true" className="size-5" />
        ส่งคำตอบแล้ว กำลังสรุปผลให้ครับ
      </p>
    );
  }

  if (stage === "later") {
    return (
      <p className="flex flex-wrap items-center gap-2 text-sm text-muted">
        เก็บแบบประเมินไว้ก่อน
        <button
          type="button"
          onClick={() => setStage("intro")}
          className="font-medium text-copie-teal underline underline-offset-2"
        >
          กลับมาทำเมื่อไหร่ก็ได้
        </button>
      </p>
    );
  }

  if (stage === "intro") {
    return (
      <section className="copie-panel flex flex-col gap-4 rounded-xl border border-deep-navy/12 bg-surface p-5">
        <h2 className="copie-heading font-display text-xl font-bold text-deep-navy">{data.title}</h2>

        <dl className="grid grid-cols-3 gap-3 text-center">
          <Stat label="คำถาม" value={`${total}`} unit="ข้อ" />
          <Stat label="ทักษะ" value={`${SKILL_ORDER.length}`} unit="ด้าน" />
          <Stat label="ใช้เวลา" value={`${Math.max(1, Math.round((total * SECONDS_PER_QUESTION) / 60))}`} unit="นาที" />
        </dl>

        <p className="flex items-center gap-2 text-sm text-muted">
          <Info aria-hidden="true" className="size-4 shrink-0" />
          ตอบตามประสบการณ์จริง ไม่มีถูกหรือผิด
        </p>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setStage("questions")}
            disabled={locked}
            className="inline-flex items-center gap-2 rounded-lg bg-copie-teal px-4 py-2.5 font-medium text-surface disabled:opacity-50"
          >
            <ListChecks aria-hidden="true" className="size-4" />
            เริ่มแบบประเมิน
          </button>

          <button
            type="button"
            onClick={() => setStage("later")}
            disabled={locked}
            className="rounded-lg border border-deep-navy/15 px-4 py-2.5 text-deep-navy disabled:opacity-40"
          >
            ไว้ทีหลัง
          </button>
        </div>
      </section>
    );
  }

  const percent = Math.round(((current + 1) / total) * 100);

  return (
    <section className="copie-panel flex flex-col gap-4 rounded-xl border border-deep-navy/12 bg-surface p-5">
      <div className="flex items-center gap-3">
        <p className="copie-eyebrow text-xs font-semibold tracking-[0.2em] text-copie-teal">SKILL ASSESSMENT</p>
        <p className="ml-auto font-display text-lg font-bold tabular-nums text-deep-navy">
          {current + 1} <span className="text-base font-normal text-muted">/ {total}</span>
        </p>
      </div>

      <div
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={total}
        aria-valuenow={current + 1}
        aria-label={`ข้อที่ ${current + 1} จาก ${total} ข้อ`}
        className="h-2 w-full overflow-hidden rounded-full bg-mist"
      >
        <div className="h-full rounded-full bg-copie-teal transition-[width]" style={{ width: `${percent}%` }} />
      </div>

      <fieldset className="flex flex-col gap-3" disabled={locked}>
        <legend className="flex items-baseline gap-3 pb-2">
          <span className="copie-index font-display text-xl font-bold italic text-copie-teal">Q{current + 1}</span>
          <span className="font-display text-lg font-semibold text-deep-navy">{question.text}</span>
        </legend>

        {question.options.map((option) => {
          const selected = answered === option.value;
          return (
            <label
              key={option.value}
              className={`flex cursor-pointer items-center gap-3 rounded-lg border px-4 py-3 transition ${
                selected ? "border-copie-teal bg-copie-teal/8" : "border-deep-navy/12 hover:border-copie-teal/40"
              }`}
            >
              <input
                type="radio"
                name={`${data.assessment_id}-${question.id}`}
                value={option.value}
                checked={selected}
                onChange={() => setAnswers((current) => ({ ...current, [question.id]: option.value }))}
                className="size-4 accent-copie-teal"
              />
              <span className={selected ? "font-medium text-deep-navy" : "text-ink"}>{option.label}</span>
            </label>
          );
        })}
      </fieldset>

      {error && (
        <p className="text-sm text-danger" role="alert">
          {error}
        </p>
      )}

      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={() => setCurrent((index) => Math.max(0, index - 1))}
          disabled={locked || current === 0}
          className="inline-flex items-center gap-2 rounded-lg border border-deep-navy/15 px-4 py-2.5 text-deep-navy disabled:opacity-40"
        >
          <ArrowLeft aria-hidden="true" className="size-4" />
          ย้อนกลับ
        </button>

        <button
          type="button"
          onClick={isLast ? submit : () => setCurrent((index) => Math.min(total - 1, index + 1))}
          disabled={locked || answered === undefined}
          className="inline-flex items-center gap-2 rounded-lg bg-copie-teal px-4 py-2.5 font-medium text-surface disabled:opacity-50"
        >
          {isLast ? (submitting ? "กำลังส่ง..." : "ดูผล") : "ข้อถัดไป"}
          <ArrowRight aria-hidden="true" className="size-4" />
        </button>

        <p className="ml-auto text-xs text-muted">
          ตอบครบแล้ว {Object.keys(answers).length} / {total} ข้อ
        </p>
      </div>
    </section>
  );

  async function submit() {
    if (submitting) return; // กันกดส่งซ้ำ
    setSubmitting(true);
    setError(null);
    try {
      await onSubmit(data.questions.map((item) => ({ question_id: item.id, value: answers[item.id] })));
      setStage("done");
    } catch {
      setError("ส่งคำตอบไม่สำเร็จ ลองกดดูผลอีกครั้งครับ");
    } finally {
      setSubmitting(false);
    }
  }
}

function Stat({ label, value, unit }: { label: string; value: string; unit: string }) {
  return (
    <div className="rounded-lg border border-deep-navy/12 px-3 py-2">
      <dt className="text-xs text-muted">{label}</dt>
      <dd className="font-display text-xl font-bold tabular-nums text-deep-navy">
        {value} <span className="text-sm font-normal text-muted">{unit}</span>
      </dd>
    </div>
  );
}
