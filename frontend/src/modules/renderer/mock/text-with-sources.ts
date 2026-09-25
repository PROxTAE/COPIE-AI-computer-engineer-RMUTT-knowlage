// text · 5 sources + citation markers [1]..[5] — ทดสอบ SourceViewer ตอนมีแหล่งอ้างอิงเยอะ
import type { AgentResponse, Source } from "@/types/contract";
import { base } from "./base";

// PLACEHOLDER: doc_id / url ของจริงมาจาก data/knowledge/*.md ของ P4 (ทุกไฟล์ต้องมี source_url จริง)
const sources: Source[] = [
  {
    doc_id: "ce-overview",
    title: "ภาพรวมภาควิชาวิศวกรรมคอมพิวเตอร์",
    section: "ประวัติภาควิชา",
    url: null,
    snippet: "ภาควิชาวิศวกรรมคอมพิวเตอร์ คณะวิศวกรรมศาสตร์ เปิดสอนหลักสูตรวิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมคอมพิวเตอร์",
    score: 0.91,
  },
  {
    doc_id: "ce-overview",
    title: "ภาพรวมภาควิชาวิศวกรรมคอมพิวเตอร์",
    section: "ห้องปฏิบัติการ",
    url: null,
    snippet: "ห้องปฏิบัติการรองรับการเรียนด้านระบบเครือข่าย ระบบสมองกลฝังตัว และการพัฒนาซอฟต์แวร์",
    score: 0.84,
  },
  {
    doc_id: "ce-curriculum",
    title: "โครงสร้างหลักสูตร",
    section: "หมวดวิชาเฉพาะ",
    url: null,
    snippet: "หมวดวิชาเฉพาะประกอบด้วยกลุ่มวิชาพื้นฐานทางวิศวกรรม กลุ่มวิชาชีพบังคับ และกลุ่มวิชาชีพเลือก",
    score: 0.78,
  },
  {
    doc_id: "ce-career",
    title: "แนวทางประกอบอาชีพ",
    section: null,
    url: null,
    snippet: "บัณฑิตสามารถทำงานเป็นวิศวกรซอฟต์แวร์ วิศวกรระบบเครือข่าย หรือวิศวกรระบบสมองกลฝังตัว",
    score: 0.71,
  },
  {
    doc_id: "ce-admission",
    title: "การรับเข้าศึกษา",
    section: "คุณสมบัติผู้สมัคร",
    url: null,
    snippet: "รับผู้สำเร็จการศึกษาระดับมัธยมศึกษาตอนปลายสายวิทย์-คณิต หรือระดับ ปวช. สาขาที่เกี่ยวข้อง",
    score: 0.66,
  },
];

export const textWithSourcesMock: AgentResponse = {
  ...base({
    message_id: "dev-text-02",
    message: [
      "## ภาคคอมเรียนเกี่ยวกับอะไร",
      "",
      "หลักสูตรครอบคลุมทั้งฮาร์ดแวร์และซอฟต์แวร์ โดยมีห้องปฏิบัติการรองรับทั้งงานเครือข่ายและระบบสมองกลฝังตัว [1][2]",
      "",
      "โครงสร้างหลักสูตรแบ่งเป็นหมวดวิชาศึกษาทั่วไป หมวดวิชาเฉพาะ และหมวดวิชาเลือกเสรี [3]",
      "",
      "| สายงาน | ตัวอย่างตำแหน่ง |",
      "| --- | --- |",
      "| ซอฟต์แวร์ | Software Engineer, Backend Developer |",
      "| เครือข่าย | Network Engineer |",
      "| ระบบสมองกลฝังตัว | Embedded Engineer |",
      "",
      "ผู้สมัครส่วนใหญ่มาจากสายวิทย์-คณิต หรือ ปวช. สาขาที่เกี่ยวข้อง [5] และเมื่อจบแล้วทำงานได้หลายสายตามที่ระบุไว้ [4]",
    ].join("\n"),
    intent: "department_info",
    tool: "rag.search",
    latency_ms: 2310,
    sources,
    actions: [{ type: "ask", label: "ดูรายวิชาปี 2", payload: { text: "ปี 2 เทอม 1 เรียนอะไรบ้าง" } }],
  }),
  response_type: "text",
  data: null,
};
