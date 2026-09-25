// text · ไม่มี sources — ทดสอบว่า SourceViewer ถูกซ่อนเมื่อ sources ว่าง
import type { AgentResponse } from "@/types/contract";
import { base } from "./base";

export const textMock: AgentResponse = {
  ...base({
    message_id: "dev-text-01",
    message: [
      "## ภาควิชาวิศวกรรมคอมพิวเตอร์ RMUTT",
      "",
      "ภาควิชาสอนตั้งแต่ **ฮาร์ดแวร์** ไปจนถึง **ซอฟต์แวร์** โดยเน้นให้ทำโครงงานจริงตั้งแต่ชั้นปีต้น",
      "",
      "### กลุ่มวิชาหลัก",
      "",
      "1. ระบบคอมพิวเตอร์และระบบสมองกลฝังตัว",
      "2. เครือข่ายและความมั่นคงปลอดภัย",
      "3. การพัฒนาซอฟต์แวร์และปัญญาประดิษฐ์",
      "",
      "ถ้าอยากรู้ว่าแต่ละชั้นปีเรียนอะไร ถามต่อได้เลยครับ",
    ].join("\n"),
    intent: "department_info",
    latency_ms: 940,
    actions: [
      { type: "ask", label: "ปี 1 เรียนอะไรบ้าง", payload: { text: "ปี 1 เทอม 1 เรียนอะไรบ้าง" } },
      { type: "ask", label: "จบแล้วทำงานอะไรได้", payload: { text: "จบวิศวกรรมคอมพิวเตอร์แล้วทำงานอะไรได้บ้าง" } },
    ],
  }),
  response_type: "text",
  data: null,
};
