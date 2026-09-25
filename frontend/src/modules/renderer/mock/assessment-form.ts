// assessment_form · 12 ข้อ 6 ด้าน
//
// คำถามและสเกลตรงกับ data/assessment/skill_v1.json ของ P5 ที่ get_assessment() จะส่งมาจริง
// weights ไม่ถูกส่งมาฝั่ง frontend — contract ให้แค่ id / text / options
import type { AgentResponse, AssessmentOption, AssessmentQuestion } from "@/types/contract";
import { base } from "./base";

const options: AssessmentOption[] = [
  { value: 0, label: "ยังไม่เคยทำ" },
  { value: 1, label: "เคยเห็นตัวอย่าง" },
  { value: 2, label: "เคยลองทำโดยมีคนช่วย" },
  { value: 3, label: "ทำได้ด้วยตนเอง" },
  { value: 4, label: "ทำได้และอธิบายให้ผู้อื่นได้" },
];

const texts = [
  "เคยสร้างหน้าเว็บด้วย HTML, CSS และ JavaScript แล้วทดสอบการแสดงผล",
  "เคยพัฒนาเว็บหลายหน้าด้วย React, Vue หรือ Next.js",
  "เคยเขียน REST API และเชื่อมต่อฐานข้อมูล",
  "เคยออกแบบตารางฐานข้อมูลและเขียนคำสั่ง SQL เพื่อค้นข้อมูล",
  "เคยตั้งค่า IP, subnet, router หรือ switch ในห้องปฏิบัติการ",
  "เคยใช้ Wireshark ตรวจแพ็กเก็ตเพื่อวิเคราะห์ปัญหาเครือข่าย",
  "เคยเขียนโปรแกรม Arduino หรือ ESP32 เพื่ออ่านค่าเซนเซอร์",
  "เคยต่อวงจรดิจิทัลหรือทดลองออกแบบวงจรด้วย FPGA",
  "เคยใช้ Python กับ pandas หรือ numpy เพื่อวิเคราะห์ข้อมูล",
  "เคยใช้ชุดข้อมูลฝึกและทดสอบโมเดล Machine Learning",
  "เคยตรวจหาช่องโหว่ SQL injection หรือ XSS ในเว็บสำหรับฝึกทดสอบ",
  "เคยฝึกโจทย์ CTF หรือใช้เครื่องมือทดสอบความปลอดภัยในสภาพแวดล้อมที่ได้รับอนุญาต",
];

const questions: AssessmentQuestion[] = texts.map((text, index) => ({
  id: `q${index + 1}`,
  text,
  options,
}));

export const assessmentFormMock: AgentResponse = {
  ...base({
    message_id: "dev-assessment-01",
    message: [
      "ผมมีแบบประเมินความถนัด **12 ข้อ** ครอบคลุม 6 ด้าน ใช้เวลาประมาณ 3 นาที",
      "",
      "ตอบตามความเป็นจริงได้เลยครับ ไม่มีถูกผิด",
    ].join("\n"),
    intent: "skill_analysis",
    tool: "skill.get_assessment",
    latency_ms: 760,
    actions: [{ type: "ask", label: "ขอดูรายวิชาปี 3 ก่อน", payload: { text: "ปี 3 เทอม 1 เรียนอะไรบ้าง" } }],
  }),
  response_type: "assessment_form",
  data: {
    assessment_id: "skill_v1",
    title: "ประเมินประสบการณ์ทักษะวิศวกรรมคอมพิวเตอร์",
    questions,
  },
};
