// text · intent "clarify" — Agent ข้อมูลไม่พอ จึงถามกลับพร้อมตัวเลือก
import type { AgentResponse } from "@/types/contract";
import { base } from "./base";

export const clarifyMock: AgentResponse = {
  ...base({
    message_id: "dev-clarify-01",
    message: "อยากดูรายวิชาของชั้นปีไหนครับ เลือกได้เลย หรือพิมพ์บอกผมก็ได้",
    intent: "clarify",
    latency_ms: 480,
    actions: [
      { type: "ask", label: "ปี 1", payload: { text: "ปี 1 เทอม 1 เรียนอะไรบ้าง" } },
      { type: "ask", label: "ปี 2", payload: { text: "ปี 2 เทอม 1 เรียนอะไรบ้าง" } },
      { type: "ask", label: "ปี 3", payload: { text: "ปี 3 เทอม 1 เรียนอะไรบ้าง" } },
      { type: "ask", label: "ปี 4", payload: { text: "ปี 4 เทอม 1 เรียนอะไรบ้าง" } },
    ],
  }),
  response_type: "text",
  data: null,
};
