// skill_radar · ผลประเมิน 6 ด้าน (0-100)
//
// PLACEHOLDER DATA — คะแนนจริงคำนวณโดย skill.calculate_skill ของ P5 ตามสูตรใน §6.3
// score[skill] = round( Σ(value × weight) / Σ(4 × weight) × 100 )
import type { AgentResponse } from "@/types/contract";
import { base } from "./base";

export const skillRadarMock: AgentResponse = {
  ...base({
    message_id: "dev-radar-01",
    message: "นี่คือผลประเมินความถนัดของคุณครับ",
    intent: "skill_analysis",
    tool: "skill.calculate_skill",
    latency_ms: 2080,
    actions: [
      { type: "ask", label: "วิชาไหนช่วยเสริมด้าน AI", payload: { text: "มีวิชาไหนช่วยเสริมทักษะด้าน AI บ้าง" } },
    ],
  }),
  response_type: "skill_radar",
  data: {
    scores: { frontend: 75, backend: 88, network: 44, embedded: 31, ai_data: 69, cybersecurity: 52 },
    top_skills: ["backend", "frontend"],
    summary:
      "คุณถนัดงาน **Backend** มากที่สุด รองลงมาคือ **Frontend** เหมาะกับการทำงานพัฒนาเว็บแบบเต็มระบบ\n\nด้านที่ยังพัฒนาได้อีกคือ **ระบบสมองกลฝังตัว** ลองเริ่มจากโครงงาน IoT เล็ก ๆ ดูครับ",
    taken_at: "2026-09-25T09:30:00Z",
  },
};

// edge case: คะแนนต่ำสุด 0 และสูงสุด 100 อยู่ในชุดเดียวกัน + top_skills ใบเดียว
export const skillRadarEdgeMock: AgentResponse = {
  ...base({
    message_id: "dev-radar-02",
    message: "ผลประเมินของคุณออกมาสุดขั้วในบางด้านครับ",
    intent: "skill_analysis",
    tool: "skill.calculate_skill",
    latency_ms: 1990,
    actions: [],
  }),
  response_type: "skill_radar",
  data: {
    scores: { frontend: 100, backend: 0, network: 100, embedded: 0, ai_data: 50, cybersecurity: 0 },
    top_skills: ["frontend"],
    summary: "ทดสอบการแสดงผลเมื่อคะแนนเป็น 0 และ 100 พร้อมกัน",
    taken_at: "2026-09-25T09:30:00Z",
  },
};
