// แบบประเมินทักษะ — ม็อกอัพ 09-assessment-intro และ 10-assessment-question
// 2 ขั้น: หน้าแนะนำแบบ Panoramic 3 ส่วน -> หน้าตอบคำถามทีละข้อ
"use client";

import { useState } from "react";
import { ArrowLeft, ArrowRight, CheckCircle2, Clock, FileText, Info, Layers } from "lucide-react";
import type { AssessmentFormData } from "@/types/contract";
import { CopieMascot } from "@/modules/mascot";

type Stage = "intro" | "questions" | "later" | "done";

interface AssessmentFormProps {
  data: AssessmentFormData;
  onSubmit: (answers: { question_id: string; value: number }[]) => Promise<void>;
  onBack?: () => void;
  disabled?: boolean;
}

export function AssessmentForm({ data, onSubmit, onBack, disabled = false }: AssessmentFormProps) {
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
      <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-emerald-200 bg-emerald-50/80 p-8 text-center backdrop-blur-sm">
        <div className="size-14 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-600">
          <CheckCircle2 aria-hidden="true" className="size-8" />
        </div>
        <h3 className="font-display text-xl font-bold text-cyber-ink">ส่งคำตอบเรียบร้อยแล้ว</h3>
        <p className="text-sm text-cyber-muted max-w-md">
          COPIE กำลังประมวลผลคะแนนและสร้างกราฟสรุปทักษะ (Skill Radar) ให้คุณสักครู่ครับ...
        </p>
      </div>
    );
  }

  if (stage === "later") {
    return (
      <div className="flex flex-col gap-4 rounded-2xl border border-cyber-line bg-white/95 p-6 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <span className="copie-eyebrow text-xs font-semibold tracking-[0.16em] text-cyber-blue">
            SKILL ASSESSMENT
          </span>
          {onBack && (
            <button
              type="button"
              onClick={onBack}
              className="inline-flex items-center gap-1.5 rounded-full border border-cyber-line bg-white px-3.5 py-1.5 text-xs font-semibold text-cyber-ink shadow-xs hover:border-cyber-blue/50 hover:bg-slate-50 transition-all cursor-pointer"
            >
              <ArrowLeft className="size-3.5 text-cyber-blue" />
              กลับหน้าสนทนา
            </button>
          )}
        </div>
        <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4">
          <Info className="size-5 text-cyber-blue shrink-0" />
          <p className="text-sm text-cyber-ink">
            คุณสามารถกลับมาทำแบบประเมินทักษะได้ทุกเมื่อที่ต้องการเพื่ออัปเดตผล Skill Radar
          </p>
        </div>
        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => setStage("intro")}
            className="inline-flex items-center gap-2 rounded-xl bg-cyber-blue px-5 py-2.5 font-semibold text-cyber-on-accent shadow-sm transition hover:bg-cyber-blue-hover active:scale-[0.98] cursor-pointer"
          >
            เปิดแบบประเมินอีกครั้ง
          </button>
          {onBack && (
            <button
              type="button"
              onClick={onBack}
              className="rounded-xl border border-cyber-line bg-white px-4 py-2.5 font-medium text-cyber-ink hover:bg-cyber-paper transition cursor-pointer"
            >
              สนทนากับ COPIE ต่อ
            </button>
          )}
        </div>
      </div>
    );
  }

  // Stage 1: Intro (Matching Mockup 09-assessment-intro.png)
  if (stage === "intro") {
    return (
      <section className="relative w-full py-4" aria-label="แนะนำแบบประเมินทักษะ">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
          {/* Left Column: Heading & Subtitles */}
          <div className="lg:col-span-4 flex flex-col gap-4">
            <div className="flex items-center gap-2">
              <span className="size-2 bg-cyber-blue" />
              <span className="font-label text-xs font-bold tracking-[0.2em] text-cyber-blue uppercase">
                COPIE / AI RESPONSE
              </span>
            </div>

            <div className="relative">
              <h1 className="copie-heading font-display text-4xl sm:text-5xl font-black italic tracking-tight text-cyber-strong leading-tight">
                มาสำรวจ<br />
                <span className="relative inline-block">
                  ทักษะของคุณ
                  {/* Cyan speed lines behind title */}
                  <span
                    className="absolute -right-24 top-1/2 -translate-y-1/2 w-32 h-8 bg-[url('/copie-ui/effects/data-streak.svg')] bg-contain bg-no-repeat pointer-events-none opacity-80"
                    aria-hidden="true"
                  />
                </span>
              </h1>
            </div>

            <div className="text-base text-cyber-strong/80 leading-relaxed font-medium">
              <p>ตอบคำถามสั้น ๆ เพื่อเห็นภาพทักษะของคุณ</p>
              <p className="text-cyber-subtle">ไม่มีการให้คะแนนถูกหรือผิด</p>
            </div>

            {/* Cyan dashed bar /////// */}
            <div className="flex items-center gap-1.5 py-1 text-cyber-glow font-mono text-sm tracking-widest select-none" aria-hidden="true">
              {"////////"}
            </div>

            <div className="mt-4 font-label text-[10px] font-bold tracking-[0.2em] text-cyber-subtle uppercase">
              <p>KNOW YOURSELF</p>
              <p>BUILD A BRIGHTER TOMORROW</p>
            </div>
          </div>

          {/* Center Column: Mascot with Halo */}
          <div className="lg:col-span-4 relative flex items-center justify-center min-h-[200px] sm:min-h-[260px] lg:min-h-[340px] py-2 sm:py-4">
            <div className="copie-halo absolute w-[240px] sm:w-[320px] lg:w-[420px] max-w-[85vw] aspect-square pointer-events-none" aria-hidden="true" />
            <div className="relative z-10">
              <CopieMascot
                state="welcome"
                priority
                className="max-h-[min(26dvh,220px)] sm:max-h-[min(36dvh,320px)] lg:max-h-[min(48dvh,400px)] w-auto! drop-shadow-[0_16px_32px_rgb(var(--copie-accent-rgb)/0.18)]"
              />
            </div>
          </div>

          {/* Right Column: 3 Stat Cards & Actions */}
          <div className="lg:col-span-4 flex flex-col gap-4">
            {/* Stat 1: 12 Questions */}
            <div className="flex items-center gap-4 rounded-2xl border border-cyber-edge/80 bg-white/90 p-4 shadow-xs">
              <div className="flex size-12 items-center justify-center rounded-xl bg-blue-50 text-cyber-blue shrink-0">
                <FileText className="size-6" />
              </div>
              <div>
                <div className="flex items-baseline gap-2">
                  <span className="font-display text-2xl font-black italic text-cyber-blue">{total}</span>
                  <span className="font-display text-lg font-bold text-cyber-strong">คำถาม</span>
                </div>
                <p className="text-xs text-cyber-subtle mt-0.5">คำถามสั้น ๆ ครอบคลุมหลากหลายสถานการณ์</p>
              </div>
            </div>

            {/* Stat 2: 6 Skill Dimensions */}
            <div className="flex items-center gap-4 rounded-2xl border border-cyber-edge/80 bg-white/90 p-4 shadow-xs">
              <div className="flex size-12 items-center justify-center rounded-xl bg-blue-50 text-cyber-blue shrink-0">
                <Layers className="size-6" />
              </div>
              <div>
                <div className="flex items-baseline gap-2">
                  <span className="font-display text-2xl font-black italic text-cyber-blue">6</span>
                  <span className="font-display text-lg font-bold text-cyber-strong">ด้านทักษะ</span>
                </div>
                <p className="text-xs text-cyber-subtle mt-0.5">ครอบคลุมทักษะที่จำเป็นในโลกการทำงานยุคใหม่</p>
              </div>
            </div>

            {/* Stat 3: 5 Minutes */}
            <div className="flex items-center gap-4 rounded-2xl border border-cyber-edge/80 bg-white/90 p-4 shadow-xs">
              <div className="flex size-12 items-center justify-center rounded-xl bg-blue-50 text-cyber-blue shrink-0">
                <Clock className="size-6" />
              </div>
              <div>
                <div className="flex items-baseline gap-2">
                  <span className="font-display text-sm font-semibold text-cyber-strong">ประมาณ</span>
                  <span className="font-display text-2xl font-black italic text-cyber-blue">5 นาที</span>
                </div>
                <p className="text-xs text-cyber-subtle mt-0.5">ใช้เวลาไม่นาน ก็เห็นภาพรวมทักษะของคุณ</p>
              </div>
            </div>

            {/* Primary Action Button */}
            <div className="pt-2 flex flex-col items-center gap-2.5">
              <button
                type="button"
                onClick={() => setStage("questions")}
                disabled={locked}
                className="group flex w-full items-center justify-center gap-3 rounded-full bg-gradient-to-r from-cyber-blue-deep to-cyber-blue px-8 py-3.5 font-display text-base font-bold text-cyber-on-accent shadow-[0_8px_24px_rgb(var(--copie-accent-rgb)/0.3)] hover:shadow-[0_12px_32px_rgb(var(--copie-accent-rgb)/0.45)] hover:-translate-y-0.5 active:translate-y-0 transition-all cursor-pointer"
              >
                <span>เริ่มแบบประเมิน</span>
                <ArrowRight className="size-5 group-hover:translate-x-1 transition-transform" />
              </button>

              <button
                type="button"
                onClick={() => setStage("later")}
                disabled={locked}
                className="font-display text-sm font-semibold text-cyber-blue hover:underline underline-offset-4 cursor-pointer py-1"
              >
                ไว้ทีหลัง
              </button>
            </div>
          </div>
        </div>
      </section>
    );
  }

  // Stage 2: Question (Matching Mockup 10-assessment-question.png)
  const percent = Math.round(((current + 1) / total) * 100);

  return (
    <section className="flex flex-col gap-6 rounded-2xl border border-cyber-edge bg-white/95 p-6 sm:p-8 shadow-sm backdrop-blur-sm" aria-label="คำถามแบบประเมิน">
      {/* Question Header & Progress */}
      <div className="flex flex-col gap-3 pb-3 border-b border-cyber-edge/60">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="size-2 bg-cyber-blue" />
              <span className="font-label text-xs font-bold tracking-[0.2em] text-cyber-blue uppercase">
                SKILL ASSESSMENT
              </span>
            </div>
            <div className="relative">
              <h2 className="copie-heading font-display text-2xl sm:text-3xl font-black italic tracking-tight text-cyber-strong">
                ประเมินทักษะ
                <span
                  className="inline-block ml-4 w-28 h-6 bg-[url('/copie-ui/effects/data-streak.svg')] bg-contain bg-no-repeat align-middle pointer-events-none opacity-80"
                  aria-hidden="true"
                />
              </h2>
            </div>
            <p className="text-sm font-medium text-cyber-subtle mt-1">
              ตอบคำถามทีละข้อ เพื่อให้เราเข้าใจทักษะของคุณมากขึ้น
            </p>
          </div>

          {/* Progress Counter & Sleek Bar */}
          <div className="flex flex-col items-end gap-1.5 shrink-0">
            <p className="font-display text-xl sm:text-2xl font-black italic tabular-nums text-cyber-strong">
              <span className="text-cyber-blue">{current + 1}</span>{" "}
              <span className="text-base font-normal text-cyber-subtle">/ {total}</span>
            </p>
            <div
              role="progressbar"
              aria-valuemin={0}
              aria-valuemax={total}
              aria-valuenow={current + 1}
              aria-label={`ข้อที่ ${current + 1} จาก ${total} ข้อ`}
              className="h-2 w-32 sm:w-44 overflow-hidden rounded-full bg-slate-100 border border-slate-200"
            >
              <div
                className="h-full rounded-full bg-gradient-to-r from-cyber-blue to-cyber-glow transition-all duration-300"
                style={{ width: `${percent}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Question & Options */}
      <fieldset className="flex flex-col gap-5 pt-1" disabled={locked}>
        <legend className="flex items-baseline gap-3 pb-2 w-full">
          <span className="font-display text-2xl sm:text-3xl font-black italic text-cyber-blue shrink-0">
            Q{current + 1}
          </span>
          <span className="h-6 w-px bg-cyber-edge shrink-0 self-center" />
          <span className="font-display text-lg sm:text-xl font-bold text-cyber-strong leading-relaxed">
            {question.text}
          </span>
        </legend>

        <div className="flex flex-col gap-3">
          {question.options.map((option) => {
            const selected = answered === option.value;
            return (
              <label
                key={option.value}
                onClick={() => setAnswers((curr) => ({ ...curr, [question.id]: option.value }))}
                className={`group flex cursor-pointer items-center gap-4 rounded-xl px-5 py-3.5 transition-all shadow-xs ${
                  selected
                    ? "border-2 border-cyber-blue bg-blue-50/80 text-cyber-strong shadow-[0_0_16px_rgb(var(--copie-accent-rgb)/0.18)]"
                    : "border border-cyber-edge bg-white hover:border-cyber-blue/50 hover:bg-slate-50/60 text-cyber-strong"
                }`}
              >
                {/* Custom Radio Circle matching Mockup */}
                <div
                  className={`size-5 rounded-full flex items-center justify-center shrink-0 transition-all ${
                    selected
                      ? "border-2 border-cyber-blue bg-white"
                      : "border-2 border-cyber-field bg-white group-hover:border-cyber-blue"
                  }`}
                >
                  {selected && <div className="size-2.5 rounded-full bg-cyber-blue" />}
                </div>

                <span className={`text-sm sm:text-base ${selected ? "font-bold text-cyber-strong" : "font-medium text-cyber-strong/80"}`}>
                  {option.label}
                </span>
              </label>
            );
          })}
        </div>
      </fieldset>

      {error && (
        <p className="text-sm text-red-600 rounded-lg bg-red-50 p-3 border border-red-200" role="alert">
          {error}
        </p>
      )}

      {/* Navigation Footer */}
      <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-cyber-edge/60 mt-2">
        <div className="flex items-center gap-2 text-xs font-medium text-cyber-subtle">
          <Info className="size-4 text-cyber-blue" />
          <span>ตอบตามประสบการณ์จริง ไม่มีถูกหรือผิด</span>
        </div>

        <div className="flex items-center gap-3 ml-auto">
          {current > 0 && (
            <button
              type="button"
              onClick={() => setCurrent((index) => Math.max(0, index - 1))}
              disabled={locked}
              className="inline-flex items-center gap-2 rounded-full border border-cyber-blue bg-white px-6 py-2.5 font-display text-sm font-semibold text-cyber-blue hover:bg-blue-50 transition-all cursor-pointer shadow-xs disabled:opacity-40"
            >
              <ArrowLeft className="size-4" />
              ย้อนกลับ
            </button>
          )}

          <button
            type="button"
            onClick={isLast ? submit : () => setCurrent((index) => Math.min(total - 1, index + 1))}
            disabled={locked || answered === undefined}
            className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-cyber-blue-deep to-cyber-blue px-7 py-2.5 font-display text-sm font-bold text-cyber-on-accent shadow-[0_4px_16px_rgb(var(--copie-accent-rgb)/0.25)] hover:shadow-[0_6px_20px_rgb(var(--copie-accent-rgb)/0.35)] transition-all cursor-pointer disabled:opacity-40"
          >
            <span>{isLast ? (submitting ? "กำลังส่งข้อมูล..." : "ดูผลการวิเคราะห์") : "ข้อถัดไป"}</span>
            <ArrowRight className="size-4" />
          </button>
        </div>
      </div>
    </section>
  );

  async function submit() {
    if (submitting) return;
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
