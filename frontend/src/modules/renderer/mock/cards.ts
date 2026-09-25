// cards · รายละเอียดกลุ่มวิชา — ทดสอบ grid 3 ใบ, icon ที่ไม่มีจริง (ต้อง fallback), tags ว่าง
//
// PLACEHOLDER DATA — เนื้อหาของจริงมาจาก curriculum.get_course_detail /
// get_curriculum_overview ของ P5 และเอกสารภาคของ P4
import type { AgentResponse, InfoCard } from "@/types/contract";
import { base } from "./base";

const cards: InfoCard[] = [
  {
    title: "กลุ่มซอฟต์แวร์และ AI",
    body: "เน้นการพัฒนาโปรแกรม โครงสร้างข้อมูล ฐานข้อมูล และการเรียนรู้ของเครื่อง\n\n- เขียนโปรแกรมเชิงวัตถุ\n- ระบบฐานข้อมูล\n- ปัญญาประดิษฐ์",
    icon: "cpu",
    tags: ["Software", "AI/Data"],
  },
  {
    title: "กลุ่มเครือข่ายและความมั่นคงปลอดภัย",
    body: "ออกแบบและดูแลระบบเครือข่าย รวมถึงการป้องกันภัยคุกคามทางไซเบอร์",
    icon: "network",
    tags: ["Network", "Cybersecurity", "Infrastructure"],
  },
  {
    title: "กลุ่มระบบสมองกลฝังตัว",
    body: "เชื่อมฮาร์ดแวร์กับซอฟต์แวร์ ตั้งแต่ไมโครคอนโทรลเลอร์ไปจนถึงระบบ IoT",
    icon: "not-a-real-icon-name", // ทดสอบ fallback เป็น BookOpen
    tags: [],
  },
];

export const cardsMock: AgentResponse = {
  ...base({
    message_id: "dev-cards-01",
    message: "หลักสูตรแบ่งออกเป็น 3 กลุ่มวิชาหลักครับ กดดูรายละเอียดกลุ่มที่สนใจได้เลย",
    intent: "course_detail",
    tool: "curriculum.get_curriculum_overview",
    latency_ms: 1520,
    actions: [{ type: "open_url", label: "เว็บไซต์ภาควิชา", payload: { url: "https://www.en.rmutt.ac.th/" } }],
  }),
  response_type: "cards",
  data: { cards },
};
