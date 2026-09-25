// Mock fixtures — ใช้ได้เฉพาะหน้า /dev และ tests เท่านั้น
// หลัง Milestone M3 ห้าม import ไฟล์ในโฟลเดอร์นี้จาก flow /chat
//
// ทุก fixture ประกาศเป็น AgentResponse ตรง ๆ ถ้า contract.ts เปลี่ยน npm run build จะแดงทันที
import type { AgentResponse } from "@/types/contract";
import { textMock } from "./text";
import { textWithSourcesMock } from "./text-with-sources";
import { clarifyMock } from "./clarify";
import { courseTableMock } from "./course-table";
import { cardsMock } from "./cards";
import { assessmentFormMock } from "./assessment-form";
import { skillRadarMock, skillRadarEdgeMock } from "./skill-radar";
import { errorMock, toolErrorMock } from "./error";

export const MOCKS = {
  text: textMock,
  "text-with-sources": textWithSourcesMock,
  clarify: clarifyMock,
  "course-table": courseTableMock,
  cards: cardsMock,
  "assessment-form": assessmentFormMock,
  "skill-radar": skillRadarMock,
  "skill-radar-edge": skillRadarEdgeMock,
  error: errorMock,
  "error-tool-failed": toolErrorMock,
} satisfies Record<string, AgentResponse>;

export type MockKey = keyof typeof MOCKS;

// ป้ายกำกับในหน้า /dev — เรียงตามลำดับที่อยากให้เห็นในรายการ
export const MOCK_LABELS: { key: MockKey; label: string; note: string }[] = [
  { key: "text", label: "text", note: "ไม่มีแหล่งอ้างอิง" },
  { key: "text-with-sources", label: "text + sources", note: "5 แหล่งจริง + citation [n] + ตาราง" },
  { key: "clarify", label: "text (clarify)", note: "ถามกลับ + ตัวเลือก 4 ปุ่ม" },
  { key: "course-table", label: "course_table", note: "ข้อมูลจริง 8 วิชา · 20 หน่วยกิต" },
  { key: "cards", label: "cards", note: "3 ใบ · มี icon ที่ต้อง fallback" },
  { key: "assessment-form", label: "assessment_form", note: "ข้อจริง 12 ข้อ · 5 ระดับ" },
  { key: "skill-radar", label: "skill_radar", note: "คะแนนปกติ · top 2 ด้าน" },
  { key: "skill-radar-edge", label: "skill_radar (0/100)", note: "คะแนนสุดขั้ว 0 และ 100" },
  { key: "error", label: "error", note: "llm_unavailable" },
  { key: "error-tool-failed", label: "error (tool)", note: "tool_failed · ไม่มีปุ่ม action" },
];
