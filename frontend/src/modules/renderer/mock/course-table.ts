// course_table · ปี 2 เทอม 1
//
// PLACEHOLDER DATA — รหัสวิชา ชื่อวิชา และหน่วยกิตของจริงต้องมาจาก
// data/curriculum/curriculum.json + SOURCE.md ของ P5 (ห้ามใช้ตัวเลขชุดนี้ใน flow จริง)
// ส่วนที่ยังไม่ยืนยันใช้ "xxx" ตามรูปแบบใน 00_API_AND_DATA_CONTRACTS.md §6.2
// fixture นี้มีไว้ทดสอบ layout: ชื่อวิชายาวมาก, description ว่าง, แถวรวมหน่วยกิต
import type { AgentResponse, Course } from "@/types/contract";
import { base } from "./base";

const courses: Course[] = [
  {
    code: "04-xxx-201",
    name_th: "โครงสร้างข้อมูลและอัลกอริทึม",
    name_en: "Data Structures and Algorithms",
    credits: 3,
    credit_detail: "3(2-3-5)",
    category: "หมวดวิชาเฉพาะ",
    description: "โครงสร้างข้อมูลพื้นฐาน การวิเคราะห์ความซับซ้อน การเรียงลำดับและการค้นหา",
    year: 2,
    semester: 1,
  },
  {
    code: "04-xxx-202",
    name_th: "การเขียนโปรแกรมเชิงวัตถุ",
    name_en: "Object-Oriented Programming",
    credits: 3,
    credit_detail: "3(2-3-5)",
    category: "หมวดวิชาเฉพาะ",
    description: "คลาส ออบเจ็กต์ การสืบทอด และการออกแบบโปรแกรมเชิงวัตถุ",
    year: 2,
    semester: 1,
  },
  {
    code: "04-xxx-203",
    name_th: "การออกแบบและวิเคราะห์ระบบดิจิทัลสำหรับงานวิศวกรรมคอมพิวเตอร์ขั้นพื้นฐาน",
    name_en: "Fundamental Digital System Design and Analysis for Computer Engineering",
    credits: 3,
    credit_detail: "3(2-3-5)",
    category: "หมวดวิชาเฉพาะ",
    description: "ชื่อวิชายาวสำหรับทดสอบการตัดบรรทัดในตารางและการ์ดบนมือถือ",
    year: 2,
    semester: 1,
  },
  {
    code: "04-xxx-204",
    name_th: "ระบบฐานข้อมูล",
    name_en: "Database Systems",
    credits: 3,
    credit_detail: "3(2-3-5)",
    category: "หมวดวิชาเฉพาะ",
    description: null,
    year: 2,
    semester: 1,
  },
  {
    code: "04-xxx-205",
    name_th: "เครือข่ายคอมพิวเตอร์",
    name_en: "Computer Networks",
    credits: 3,
    credit_detail: "3(3-0-6)",
    category: "หมวดวิชาเฉพาะ",
    description: "แบบจำลองชั้นสื่อสาร โพรโทคอล TCP/IP และการจัดการเครือข่ายเบื้องต้น",
    year: 2,
    semester: 1,
  },
  {
    code: "04-xxx-206",
    name_th: "คณิตศาสตร์วิศวกรรม",
    name_en: "Engineering Mathematics",
    credits: 3,
    credit_detail: "3(3-0-6)",
    category: "หมวดวิชาพื้นฐานทางวิศวกรรม",
    description: null,
    year: 2,
    semester: 1,
  },
  {
    code: "04-xxx-207",
    name_th: "ภาษาอังกฤษเพื่อการสื่อสาร",
    name_en: "English for Communication",
    credits: 3,
    credit_detail: "3(2-2-5)",
    category: "หมวดวิชาศึกษาทั่วไป",
    description: null,
    year: 2,
    semester: 1,
  },
];

export const courseTableMock: AgentResponse = {
  ...base({
    message_id: "dev-course-table-01",
    message: "นี่คือรายวิชาของ **ปี 2 เทอม 1** รวม 21 หน่วยกิตครับ",
    intent: "curriculum",
    tool: "curriculum.get_courses",
    latency_ms: 1840,
    actions: [
      { type: "ask", label: "ดูปี 2 เทอม 2", payload: { text: "ปี 2 เทอม 2 เรียนอะไรบ้าง" } },
      { type: "ask", label: "วิชาไหนเกี่ยวกับ AI", payload: { text: "วิชาไหนในหลักสูตรเกี่ยวกับ AI บ้าง" } },
    ],
  }),
  response_type: "course_table",
  data: {
    year: 2,
    semester: 1,
    courses,
    total_credits: courses.reduce((sum, course) => sum + course.credits, 0),
  },
};
