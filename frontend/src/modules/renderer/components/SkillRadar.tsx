// ผลวิเคราะห์ทักษะ — ม็อกอัพ 11-skill-radar
// ซ้าย: Radar 6 แกน 0-100 พร้อมคะแนนตัวเลขบนแกน · ขวา: ทักษะเด่น สรุป และคะแนนรายด้านเป็นตัวเลข + แถบ
"use client";

import {
  ArrowLeft,
  ArrowRight,
  Award,
  Calendar,
  CheckCircle2,
  Compass,
  Flame,
  Lightbulb,
  MessageSquare,
  RefreshCw,
  Sparkles,
  Star,
  Target,
  Trophy,
  Zap,
  BarChart2,
} from "lucide-react";
import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from "recharts";
import type { SkillKey, SkillRadarData } from "@/types/contract";
import { Markdown } from "./Markdown";
import { SKILL_LABELS, SKILL_ORDER } from "./skillLabels";
import { FOCUS_RING } from "./styles";

const RETAKE_QUESTION = "ขอทำแบบประเมิน skill ใหม่";

const DYNAMIC_ICONS = [Sparkles, Target, Compass, Lightbulb, Flame, Award, CheckCircle2, Star, Zap];

interface SkillRadarProps {
  data: SkillRadarData;
  onAsk: (text: string) => void;
  onBack?: () => void;
  disabled?: boolean;
}

export function SkillRadar({ data, onAsk, onBack, disabled = false }: SkillRadarProps) {
  const isDynamic = Boolean(data.dimensions && data.dimensions.length >= 3);

  const points = isDynamic && data.dimensions
    ? data.dimensions.map((dim) => ({
        key: dim.key,
        label: dim.label,
        axisLabel: dim.short_label || dim.label,
        score: dim.score,
      }))
    : SKILL_ORDER.map((key) => ({
        key,
        label: SKILL_LABELS[key].th,
        axisLabel: SKILL_LABELS[key].short,
        score: data.scores[key] ?? 0,
      }));

  const sortedPoints = [...points].sort((a, b) => b.score - a.score);
  const topPoint1 = sortedPoints[0];
  const topPoint2 = sortedPoints[1];

  const displayTopic = data.topic || "วิศวกรรมคอมพิวเตอร์";
  const displayTitle = data.title || (data.topic ? `ผลวิเคราะห์ทักษะ${data.topic}` : "ผลวิเคราะห์ทักษะของคุณ");
  const displaySubtitle = data.topic
    ? `ผลลัพธ์จากแบบประเมินสะท้อนระดับความเชี่ยวชาญด้าน${data.topic} ทั้ง ${points.length} มิติ ช่วยให้คุณเห็นจุดแข็งและโอกาสในการพัฒนาทักษะได้ชัดเจนยิ่งขึ้น`
    : "ผลลัพธ์จากแบบประเมินสะท้อนระดับความเชี่ยวชาญในแต่ละด้าน ช่วยให้คุณเห็นจุดแข็งและโอกาสในการพัฒนาทักษะได้ชัดเจนยิ่งขึ้น";
  const chartTitle = isDynamic ? `กราฟสรุปทักษะ (${points.length} ด้าน)` : "กราฟสรุปทักษะทั้ง 6 ด้าน";

  // Custom Tick Renderer สำหรับ PolarAngleAxis: แสดงชื่อทักษะ + ตัวเลขคะแนนสีน้ำเงินตัวหนา
  const renderCustomAxisTick = (tickProps: {
    x?: number | string;
    y?: number | string;
    cx?: number | string;
    cy?: number | string;
    payload?: { value?: string };
  }) => {
    const { x = 0, y = 0, cx = 0, cy = 0, payload } = tickProps;
    if (!payload?.value) return null;

    const numX = Number(x);
    const numY = Number(y);
    const numCx = Number(cx);
    const numCy = Number(cy);

    const point = points.find((p) => p.axisLabel === payload.value || p.key === payload.value || p.label === payload.value);
    if (!point) return null;

    const dx = numX - numCx;
    const dy = numY - numCy;
    const isCenter = Math.abs(dx) < 20;
    const textAnchor = isCenter ? "middle" : dx > 0 ? "start" : "end";
    const xOffset = isCenter ? 0 : dx > 0 ? 8 : -8;

    let labelY = -4;
    let scoreY = 14;
    if (isCenter) {
      if (dy < 0) {
        labelY = -18;
        scoreY = -2;
      } else {
        labelY = 14;
        scoreY = 30;
      }
    }

    return (
      <g transform={`translate(${numX},${numY})`}>
        <text
          x={xOffset}
          y={labelY}
          textAnchor={textAnchor}
          className="fill-[#080b12] text-[13px] font-semibold"
          style={{ fontFamily: "var(--font-heading, Kanit), sans-serif" }}
        >
          {point.axisLabel}
        </text>
        <text
          x={xOffset}
          y={scoreY}
          textAnchor={textAnchor}
          className="fill-[#155ff2] text-[15px] font-bold"
          style={{ fontFamily: "var(--font-heading, Kanit), sans-serif" }}
        >
          {point.score}
        </text>
      </g>
    );
  };

  return (
    <section className="flex flex-col gap-6" aria-label="ผลวิเคราะห์ทักษะ">
      {/* Header Banner */}
      <div className="flex flex-col gap-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            {onBack && (
              <button
                type="button"
                onClick={onBack}
                className="inline-flex items-center gap-1.5 rounded-full border border-[#155ff2] bg-white px-4 py-1.5 text-xs font-semibold text-[#155ff2] shadow-xs hover:bg-blue-50 transition-all cursor-pointer"
              >
                <ArrowLeft className="size-3.5 text-[#155ff2]" />
                กลับหน้าสนทนา
              </button>
            )}
            <div className="flex items-center gap-2">
              <span className="size-2 bg-[#155ff2]" />
              <span className="font-label text-xs font-bold tracking-[0.2em] text-[#155ff2] uppercase">
                SKILL ASSESSMENT
              </span>
            </div>
          </div>
        </div>

        <div>
          <div className="flex flex-wrap items-center gap-4">
            <h1 className="copie-heading font-display text-3xl sm:text-4xl font-black italic tracking-tight text-[#080b12]">
              {displayTitle}
              <span
                className="inline-block ml-4 w-28 h-6 bg-[url('/copie-ui/effects/data-streak.svg')] bg-contain bg-no-repeat align-middle pointer-events-none opacity-80"
                aria-hidden="true"
              />
            </h1>

            {/* Pill Badge matching Mockup */}
            <span className="inline-flex items-center gap-1.5 rounded-full border border-[#155ff2]/30 bg-blue-50/80 px-3.5 py-1 text-xs font-semibold text-[#155ff2] shadow-xs">
              <BarChart2 className="size-3.5" />
              {data.topic ? `ผลการประเมิน${data.topic}` : "ข้อมูลผลลัพธ์ตัวอย่าง"}
            </span>
          </div>

          <p className="text-sm font-medium text-[#6b82a6] mt-2 max-w-3xl leading-relaxed">
            {displaySubtitle}
          </p>
        </div>
      </div>

      {/* Main Grid: Left Radar + Right Details */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Radar Chart */}
        <div className="lg:col-span-6 flex min-w-0 flex-col justify-between rounded-2xl border border-[#d2e0f5] bg-white/95 p-5 sm:p-6 shadow-sm backdrop-blur-sm relative overflow-hidden">
          <div className="flex items-baseline justify-between gap-2 pb-2 border-b border-[#d2e0f5]/60">
            <div>
              <h2 className="copie-heading font-display text-base font-bold text-[#080b12]">{chartTitle}</h2>
              <p className="text-xs text-[#6b82a6] mt-0.5">ภาพรวมระดับคะแนนทักษะในแต่ละมิติ</p>
            </div>
            <span className="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-semibold text-[#155ff2]">
              หน่วยคะแนน (0 - 100)
            </span>
          </div>

          <div className="h-[320px] sm:h-[380px] w-full my-2 flex items-center justify-center" aria-hidden="true">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={points} outerRadius="58%" margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
                <defs>
                  <linearGradient id="copieRadarGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#155ff2" stopOpacity="0.30" />
                    <stop offset="100%" stopColor="#00d4ff" stopOpacity="0.08" />
                  </linearGradient>
                </defs>
                <PolarGrid stroke="#a9bee0" strokeOpacity={0.4} />
                <PolarAngleAxis
                  dataKey="axisLabel"
                  tick={renderCustomAxisTick}
                />
                <PolarRadiusAxis
                  angle={90}
                  domain={[0, 100]}
                  tickCount={6}
                  tick={{ fill: "#94a3b8", fontSize: 10 }}
                  axisLine={false}
                />
                <Radar
                  name="คะแนนทักษะ"
                  dataKey="score"
                  stroke="#155ff2"
                  strokeWidth={2.5}
                  fill="url(#copieRadarGradient)"
                  fillOpacity={1}
                  dot={{ r: 4.5, fill: "#155ff2", stroke: "#ffffff", strokeWidth: 2 }}
                  activeDot={{ r: 6.5, fill: "#155ff2", stroke: "#ffffff", strokeWidth: 2.5 }}
                  isAnimationActive={false}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          <div className="flex items-center justify-between pt-3 border-t border-[#d2e0f5]/60 text-xs text-[#6b82a6]">
            <span className="inline-flex items-center gap-1.5 font-medium">
              <Calendar aria-hidden="true" className="size-3.5 text-[#155ff2]" />
              ทำแบบประเมินเมื่อ <time dateTime={data.taken_at}>{formatDate(data.taken_at)}</time>
            </span>
            <span className="font-label text-[11px] font-bold uppercase tracking-wider text-[#155ff2]">
              COPIE // RADAR ENGINE
            </span>
          </div>
        </div>

        {/* Right Column: Highlights, AI Summary & Score Breakdown */}
        <div className="lg:col-span-6 flex min-w-0 flex-col gap-5 rounded-2xl border border-[#d2e0f5] bg-white/95 p-5 sm:p-6 shadow-sm backdrop-blur-sm">
          <div className="flex items-center justify-between pb-2 border-b border-[#d2e0f5]/60">
            <h2 className="copie-heading font-display text-base font-bold text-[#080b12]">ข้อมูลสรุปผลการประเมิน</h2>
            <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
              <Sparkles className="size-3" /> ประเมินสมบูรณ์
            </span>
          </div>

          {/* Top 2 Highlight Cards */}
          {points.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {topPoint1 && (
                <TopSkillCard label={topPoint1.label} score={topPoint1.score} rank={0} />
              )}
              {topPoint2 && (
                <TopSkillCard label={topPoint2.label} score={topPoint2.score} rank={1} />
              )}
            </div>
          )}

          {/* AI Summary / Recommendations */}
          {data.summary.trim().length > 0 && (
            <div className="rounded-xl bg-slate-50/80 border border-[#d2e0f5]/70 p-4">
              <Markdown className="flex flex-col gap-2.5 text-sm leading-relaxed text-[#080b12]">
                {data.summary}
              </Markdown>
              {!data.summary.includes("หมายเหตุ") && (
                <p className="mt-3 text-[11px] text-[#6b82a6] italic border-t border-slate-200/60 pt-2">
                  หมายเหตุ: ผลลัพธ์นี้มาจากแบบประเมินตนเอง ใช้เป็นแนวทางในการพัฒนาทักษะและการวางแผนการเรียนเท่านั้นครับ
                </p>
              )}
            </div>
          )}

          {/* Skill Breakdown (คะแนนรายด้าน) */}
          <div className="flex flex-col gap-3">
            <div className="flex items-baseline justify-between">
              <h3 className="font-display text-sm font-bold text-[#080b12]">คะแนนรายด้าน</h3>
              <span className="text-xs text-[#6b82a6] font-medium">หน่วยคะแนน (0 - 100)</span>
            </div>
            <ul className="flex flex-col gap-2.5">
              {points.map((point, index) => {
                const Icon = (SKILL_LABELS as Record<string, { icon: typeof Trophy }>)[point.key]?.icon || DYNAMIC_ICONS[index % DYNAMIC_ICONS.length];
                return (
                  <li key={point.key} className="flex items-center gap-3">
                    <div className="size-7 rounded-lg bg-blue-50 flex items-center justify-center text-[#155ff2] shrink-0">
                      <Icon aria-hidden="true" className="size-4" />
                    </div>
                    <span className="w-36 sm:w-52 shrink-0 truncate text-sm font-semibold text-[#080b12]" title={point.label}>
                      {point.label}
                    </span>
                    <span className="w-8 shrink-0 text-right font-display text-sm font-bold tabular-nums text-[#155ff2]">
                      {point.score}
                    </span>
                    <div className="h-2.5 min-w-12 flex-1 overflow-hidden rounded-full bg-slate-100 border border-slate-200/50">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-[#155ff2] to-[#00d4ff] transition-all duration-700"
                        style={{ width: `${clamp(point.score)}%` }}
                      />
                    </div>
                  </li>
                );
              })}
            </ul>
          </div>

          {/* Big Blue CTA Button matching Mockup 11 */}
          <div className="pt-2 border-t border-[#d2e0f5]/60 mt-auto">
            <button
              type="button"
              onClick={() => onAsk(data.topic ? `ขอทำแบบประเมิน ${data.topic} ใหม่` : RETAKE_QUESTION)}
              disabled={disabled}
              className="group flex w-full items-center justify-center gap-3 rounded-full bg-gradient-to-r from-[#0f5ff0] to-[#155ff2] px-8 py-3.5 font-display text-base font-bold text-white shadow-[0_8px_24px_rgba(21,95,242,0.3)] hover:shadow-[0_12px_32px_rgba(21,95,242,0.45)] hover:-translate-y-0.5 active:translate-y-0 transition-all cursor-pointer disabled:opacity-50"
            >
              <RefreshCw className="size-5" />
              <span>{data.topic ? `ทำแบบประเมิน ${data.topic} ใหม่` : "ทำแบบประเมินใหม่"}</span>
              <ArrowRight className="size-5 group-hover:translate-x-1 transition-transform ml-1" />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

function TopSkillCard({ label, score, rank }: { label: string; score: number; rank: number }) {
  const Icon = rank === 0 ? Trophy : Star;
  const isTop1 = rank === 0;
  return (
    <div
      className={`flex items-center gap-3.5 rounded-xl border p-3.5 transition-all shadow-xs ${
        isTop1
          ? "border-[#155ff2]/30 bg-gradient-to-br from-blue-50/90 via-indigo-50/40 to-white"
          : "border-[#00d4ff]/30 bg-gradient-to-br from-cyan-50/70 via-blue-50/20 to-white"
      }`}
    >
      <div
        className={`size-10 rounded-xl flex items-center justify-center shrink-0 ${
          isTop1 ? "bg-amber-500/10 text-amber-600" : "bg-blue-500/10 text-blue-600"
        }`}
      >
        <Icon aria-hidden="true" className="size-5" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-xs font-semibold text-[#6b82a6]">
          {isTop1 ? "ทักษะที่โดดเด่นที่สุด" : "ทักษะที่โดดเด่นรองลงมา"}
        </p>
        <div className="flex items-baseline justify-between gap-2 mt-0.5">
          <p className="font-display font-bold text-[#080b12] truncate text-base" title={label}>
            {label}
          </p>
          <span className="font-display text-xl font-black tabular-nums text-[#155ff2]">
            {score}
          </span>
        </div>
      </div>
    </div>
  );
}

const clamp = (score: number) => Math.min(100, Math.max(0, score));

function formatDate(iso: string) {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleDateString("th-TH", { year: "numeric", month: "long", day: "numeric" });
}
