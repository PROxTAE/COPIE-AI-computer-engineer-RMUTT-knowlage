// จุดเดียวที่แปลง AgentResponse เป็น UI — module อื่นเรียกผ่าน "@/modules/renderer" เท่านั้น
//
// ลำดับการแสดงผลคงที่ทุก type ตาม 06_DYNAMIC_RENDERER.md:
//   message (markdown) -> component ตาม response_type -> SourceViewer -> ActionChips
// Renderer ไม่เรียก API เอง ทุกการกระทำส่งออกทาง callback ให้ chatStore ของ P1
"use client";

import { useState } from "react";
import type { AgentResponse } from "@/types/contract";
import { ActionChips } from "./components/ActionChips";
import { AssessmentForm } from "./components/AssessmentForm";
import { CourseTable } from "./components/CourseTable";
import { ErrorResponse } from "./components/ErrorResponse";
import { InfoCards } from "./components/InfoCards";
import { SkillRadar } from "./components/SkillRadar";
import { SourceViewer } from "./components/SourceViewer";
import { TextResponse } from "./components/TextResponse";

export interface AssessmentAnswer {
  question_id: string;
  value: number;
}

export interface ResponseRendererProps {
  response: AgentResponse;
  /** ผู้ใช้กดปุ่มที่ทำให้เกิดคำถามใหม่ (ActionChips, ปุ่มลองใหม่, ทำแบบประเมินใหม่) */
  onAsk: (text: string) => void;
  /** ส่งคำตอบแบบประเมิน — renderer รอ promise เพื่อ disable ปุ่มระหว่างส่ง */
  onSubmitAssessment: (answers: AssessmentAnswer[]) => Promise<void>;
  /** true ระหว่างที่ยังมี request ค้างอยู่ ปุ่มทุกปุ่มต้องกดไม่ได้ */
  disabled?: boolean;
}

export function ResponseRenderer({ response, onAsk, onSubmitAssessment, disabled = false }: ResponseRendererProps) {
  // แหล่งอ้างอิงที่กางอยู่ ใช้ร่วมกันระหว่าง badge [n] ในคำตอบกับการ์ดใน SourceViewer
  const [activeSource, setActiveSource] = useState<number | null>(null);

  // คำตอบใหม่มาถึง = ปิดการ์ดที่กางค้างไว้จากคำตอบก่อนหน้า (รีเซ็ตตอน render ไม่ใช่ใน effect)
  const [renderedId, setRenderedId] = useState(response.message_id);
  if (renderedId !== response.message_id) {
    setRenderedId(response.message_id);
    setActiveSource(null);
  }

  const isText = response.response_type === "text";

  // ErrorResponse ใช้ action "ask" ตัวแรกเป็นปุ่มลองใหม่อยู่แล้ว ไม่ต้องโผล่ซ้ำเป็น chip
  const retryAction = response.response_type === "error" ? response.actions.find((item) => item.type === "ask") : null;
  const chipActions = retryAction ? response.actions.filter((item) => item !== retryAction) : response.actions;

  return (
    <article className="@container flex flex-col gap-5" data-response-type={response.response_type} aria-busy={disabled}>
      {response.message.trim().length > 0 && (
        <TextResponse
          message={response.message}
          citationCount={response.sources.length}
          onCitationClick={setActiveSource}
          animate={isText}
          showEyebrow={isText}
        />
      )}

      <ResponseBody response={response} onAsk={onAsk} onSubmitAssessment={onSubmitAssessment} disabled={disabled} />

      <SourceViewer sources={response.sources} activeIndex={activeSource} onActiveChange={setActiveSource} />

      <ActionChips actions={chipActions} onAsk={onAsk} disabled={disabled} />
    </article>
  );
}

// switch เดียวที่ตัดสินหน้าตาของคำตอบ — เพิ่ม response_type ใหม่ใน contract แล้วไม่แก้ที่นี่ build จะแดง
function ResponseBody({
  response,
  onAsk,
  onSubmitAssessment,
  disabled,
}: {
  response: AgentResponse;
  onAsk: (text: string) => void;
  onSubmitAssessment: (answers: AssessmentAnswer[]) => Promise<void>;
  disabled: boolean;
}) {
  switch (response.response_type) {
    case "text":
      return null; // message ด้านบนคือเนื้อหาทั้งหมด

    case "course_table":
      return <CourseTable data={response.data} disabled={disabled} />;

    case "cards":
      return <InfoCards data={response.data} onAsk={onAsk} disabled={disabled} />;

    case "assessment_form":
      return <AssessmentForm data={response.data} onSubmit={onSubmitAssessment} disabled={disabled} />;

    case "skill_radar":
      return <SkillRadar data={response.data} onAsk={onAsk} disabled={disabled} />;

    case "error":
      return <ErrorResponse data={response.data} actions={response.actions} onAsk={onAsk} disabled={disabled} />;

    default: {
      const _exhaustive: never = response;
      return _exhaustive;
    }
  }
}
