// error · LLM ไม่พร้อมใช้งาน — ErrorResponse ต้องมีปุ่มลองใหม่ที่ส่งคำถามเดิมกลับไป
import type { AgentResponse } from "@/types/contract";
import { base } from "./base";

export const errorMock: AgentResponse = {
  ...base({
    message_id: "dev-error-01",
    message: "ตอนนี้ผมเชื่อมต่อกับระบบ AI ไม่ได้ ลองส่งคำถามอีกครั้งในอีกสักครู่นะครับ",
    intent: "general",
    latency_ms: 120,
    actions: [{ type: "ask", label: "ลองใหม่อีกครั้ง", payload: { text: "ภาคคอมเรียนเกี่ยวกับอะไร" } }],
  }),
  response_type: "error",
  data: { code: "llm_unavailable" },
};

export const toolErrorMock: AgentResponse = {
  ...base({
    message_id: "dev-error-02",
    message: "ผมดึงข้อมูลรายวิชาไม่สำเร็จครับ",
    intent: "curriculum",
    tool: "curriculum.get_courses",
    latency_ms: 340,
    actions: [],
  }),
  response_type: "error",
  data: { code: "tool_failed" },
};
