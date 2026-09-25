// assessment_form · 12 ข้อ 6 ด้าน
//
// PLACEHOLDER DATA — ของจริงมาจาก data/assessment/skill_v1.json ของ P5 ผ่าน get_assessment()
// (weights ไม่ถูกส่งมา frontend — ได้แค่ id / text / options ตาม contract)
import type { AgentResponse, AssessmentOption, AssessmentQuestion } from "@/types/contract";
import { base } from "./base";

// scale ตาม 00_API_AND_DATA_CONTRACTS.md §6.3
const options: AssessmentOption[] = [
  { value: 0, label: "ไม่เคยเลย" },
  { value: 1, label: "เคยได้ยิน" },
  { value: 2, label: "เคยลองทำ" },
  { value: 3, label: "ทำได้" },
  { value: 4, label: "ทำได้ดี / สอนคนอื่นได้" },
];

const texts = [
  "สร้างหน้าเว็บด้วย HTML/CSS/JS หรือ React",
  "จัดวาง layout ให้ใช้งานได้ดีทั้งบนจอคอมและมือถือ",
  "เขียน REST API และต่อฐานข้อมูล",
  "ออกแบบตารางฐานข้อมูลและเขียนคำสั่ง SQL",
  "ตั้งค่าเครือข่าย เช่น IP, Subnet, Router หรือ Switch",
  "วิเคราะห์ปัญหาการเชื่อมต่อเครือข่ายด้วยเครื่องมือ เช่น ping หรือ Wireshark",
  "เขียนโปรแกรมควบคุมไมโครคอนโทรลเลอร์ เช่น Arduino หรือ ESP32",
  "ต่อวงจรและอ่านค่าจากเซนเซอร์เพื่อใช้ในโครงงาน",
  "ใช้ Python วิเคราะห์ข้อมูลหรือสร้างกราฟสรุปผล",
  "เทรนหรือใช้งานโมเดล Machine Learning กับข้อมูลจริง",
  "ตรวจหาช่องโหว่ของระบบ หรือทำ CTF / Penetration Testing",
  "ตั้งค่าความปลอดภัยของระบบ เช่น สิทธิ์ผู้ใช้ การเข้ารหัส หรือ Firewall",
];

const questions: AssessmentQuestion[] = texts.map((text, index) => ({
  id: `q${index + 1}`,
  text,
  options,
}));

export const assessmentFormMock: AgentResponse = {
  ...base({
    message_id: "dev-assessment-01",
    message:
      "ผมมีแบบประเมินความถนัด **12 ข้อ** ครอบคลุม 6 ด้าน ใช้เวลาประมาณ 3 นาที\n\nตอบตามความเป็นจริงได้เลยครับ ไม่มีถูกผิด",
    intent: "skill_analysis",
    tool: "skill.get_assessment",
    latency_ms: 760,
    actions: [{ type: "ask", label: "ขอดูรายวิชาปี 3 ก่อน", payload: { text: "ปี 3 เทอม 1 เรียนอะไรบ้าง" } }],
  }),
  response_type: "assessment_form",
  data: {
    assessment_id: "skill_v1",
    title: "ประเมินความถนัดสาย Computer Engineering",
    questions,
  },
};
