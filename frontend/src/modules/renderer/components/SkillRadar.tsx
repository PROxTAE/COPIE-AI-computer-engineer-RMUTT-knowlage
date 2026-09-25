// ผลวิเคราะห์ทักษะ — ม็อกอัพ 11-skill-radar
// ซ้าย: Radar 6 แกน 0-100  ·  ขวา: ทักษะเด่น สรุป และคะแนนรายด้านเป็นตัวเลข + แถบ
// ตัวเลขทุกค่าต้องอ่านได้เป็นข้อความด้วย ไม่ใช่เห็นจากกราฟอย่างเดียว (a11y)
"use client";

import { RefreshCw, Star, Trophy } from "lucide-react";
import { PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer } from "recharts";
import type { SkillKey, SkillRadarData } from "@/types/contract";
import { Markdown } from "./Markdown";
import { SKILL_LABELS, SKILL_ORDER } from "./skillLabels";
import { FOCUS_RING } from "./styles";

const RETAKE_QUESTION = "ขอทำแบบประเมิน skill ใหม่";

interface SkillRadarProps {
  data: SkillRadarData;
  onAsk: (text: string) => void;
  disabled?: boolean;
}

export function SkillRadar({ data, onAsk, disabled = false }: SkillRadarProps) {
  const points = SKILL_ORDER.map((key) => ({
    key,
    label: SKILL_LABELS[key].th,
    axisLabel: SKILL_LABELS[key].short,
    score: data.scores[key],
  }));

  return (
    <section className="copie-panel flex flex-col gap-4 @3xl:flex-row" aria-label="ผลวิเคราะห์ทักษะ">
      <div className="flex min-w-0 flex-1 flex-col gap-2 rounded-xl border border-deep-navy/12 bg-surface p-4">
        <div className="flex items-baseline justify-between gap-2">
          <h2 className="copie-heading font-display text-base font-semibold text-deep-navy">กราฟสรุปทักษะทั้ง 6 ด้าน</h2>
          <p className="text-xs text-muted">หน่วยคะแนน (0 - 100)</p>
        </div>

        {/* กราฟเป็นภาพประกอบ ตัวเลขจริงอ่านได้จากรายการคะแนนด้านขวา */}
        <div className="h-72 w-full" aria-hidden="true">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={points} outerRadius="72%">
              <PolarGrid stroke="var(--color-copie-teal)" strokeOpacity={0.25} />
              <PolarAngleAxis
                dataKey="axisLabel"
                tick={{ fill: "var(--color-deep-navy)", fontSize: 12 }}
              />
              <PolarRadiusAxis
                // angle 90 = วางสเกลตั้งขึ้นบนแกนแรก ไม่ให้ตัวเลขเฉียงทับกราฟ
                angle={90}
                domain={[0, 100]}
                tickCount={6}
                tick={{ fill: "var(--color-muted)", fontSize: 10 }}
                axisLine={false}
              />
              <Radar
                dataKey="score"
                stroke="var(--color-copie-teal)"
                fill="var(--color-copie-teal)"
                fillOpacity={0.25}
                strokeWidth={2}
                isAnimationActive={false}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        <p className="text-xs text-muted">
          ทำแบบประเมินเมื่อ <time dateTime={data.taken_at}>{formatDate(data.taken_at)}</time>
        </p>
      </div>

      <div className="flex min-w-0 flex-1 flex-col gap-4 rounded-xl border border-deep-navy/12 bg-surface p-4">
        <h2 className="copie-heading font-display text-base font-semibold text-deep-navy">ข้อมูลสรุปผลการประเมิน</h2>

        {data.top_skills.length > 0 && (
          <ul className="grid gap-2 @xl:grid-cols-2">
            {data.top_skills.slice(0, 2).map((key, position) => (
              <TopSkill key={key} skill={key} score={data.scores[key]} rank={position} />
            ))}
          </ul>
        )}

        {data.summary.trim().length > 0 && (
          <Markdown className="flex flex-col gap-2 text-sm leading-6">{data.summary}</Markdown>
        )}

        <div className="flex flex-col gap-2">
          <div className="flex items-baseline justify-between gap-2">
            <h3 className="font-display text-sm font-semibold text-deep-navy">คะแนนรายด้าน</h3>
            <p className="text-xs text-muted">หน่วยคะแนน (0 - 100)</p>
          </div>
          <ul className="flex flex-col gap-2">
            {points.map((point) => {
              const Icon = SKILL_LABELS[point.key].icon;
              return (
                <li key={point.key} className="flex items-center gap-2">
                  <Icon aria-hidden="true" className="size-4 shrink-0 text-copie-teal" />
                  <span className="w-44 shrink-0 truncate text-sm text-ink" title={point.label}>
                    {point.label}
                  </span>
                  <span className="w-9 shrink-0 text-right font-display text-sm font-bold tabular-nums text-deep-navy">
                    {point.score}
                  </span>
                  <span className="h-2 min-w-8 flex-1 overflow-hidden rounded-full bg-mist">
                    <span
                      className="block h-full rounded-full bg-copie-teal"
                      style={{ width: `${clamp(point.score)}%` }}
                    />
                  </span>
                </li>
              );
            })}
          </ul>
        </div>

        <button
          type="button"
          onClick={() => onAsk(RETAKE_QUESTION)}
          disabled={disabled}
          className={`inline-flex items-center justify-center gap-2 rounded-lg bg-copie-teal px-4 py-2.5 font-medium text-surface disabled:opacity-50 ${FOCUS_RING}`}
        >
          <RefreshCw aria-hidden="true" className="size-4" />
          ทำแบบประเมินใหม่
        </button>
      </div>
    </section>
  );
}

function TopSkill({ skill, score, rank }: { skill: SkillKey; score: number; rank: number }) {
  const Icon = rank === 0 ? Trophy : Star;
  return (
    <li className="flex items-center gap-3 rounded-lg border border-copie-teal/25 bg-copie-teal/8 p-3">
      <Icon aria-hidden="true" className="size-5 shrink-0 text-copie-teal" />
      <div className="min-w-0">
        <p className="text-xs text-muted">{rank === 0 ? "ทักษะที่โดดเด่นที่สุด" : "ทักษะที่โดดเด่นรองลงมา"}</p>
        <p className="flex items-baseline gap-2">
          <span className="truncate font-display font-semibold text-deep-navy">{SKILL_LABELS[skill].th}</span>
          <span className="font-display text-lg font-bold tabular-nums text-copie-teal">{score}</span>
        </p>
      </div>
    </li>
  );
}

const clamp = (score: number) => Math.min(100, Math.max(0, score));

function formatDate(iso: string) {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleDateString("th-TH", { year: "numeric", month: "long", day: "numeric" });
}
