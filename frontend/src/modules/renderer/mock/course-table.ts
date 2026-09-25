// course_table · ปี 2 เทอม 1
//
// ข้อมูลจริงจาก data/curriculum/curriculum.json ของ P5
// (หลักสูตรปรับปรุง พ.ศ. 2568 · ที่มาและเลขหน้าอยู่ใน data/curriculum/SOURCE.md)
// รหัส 01-xxx-xxx เป็นแถวหมวดวิชาเลือกที่เล่มหลักสูตรไม่ได้ระบุวิชาเจาะจง — name_en จึงว่าง
// fixture นี้ครอบคลุม edge case ที่ต้องทดสอบ: ชื่อวิชายาว, name_en ว่าง, credit_detail และ description เป็น null
import type { AgentResponse, Course } from "@/types/contract";
import { base } from "./base";

const courses: Course[] = [
  {
    code: "01-xxx-xxx",
    name_th: "หมวดวิชาศึกษาทั่วไป-กลุ่มวิชาภาษาเพื่อการสื่อสาร (3)",
    name_en: "",
    credits: 3,
    credit_detail: null,
    category: "หมวดวิชาศึกษาทั่วไป",
    description: null,
    year: 2,
    semester: 1,
  },
  {
    code: "04-620-201",
    name_th: "ปฏิบัติการควบคุมเวอร์ชัน",
    name_en: "Version Control Laboratory",
    credits: 1,
    credit_detail: "1(0-3)",
    category: "หมวดวิชาเฉพาะ",
    description: null,
    year: 2,
    semester: 1,
  },
  {
    code: "04-620-202",
    name_th: "ปฏิบัติการโปรแกรมภาษาไพธอน",
    name_en: "Python Programming Laboratory",
    credits: 1,
    credit_detail: "1(0-3)",
    category: "หมวดวิชาเฉพาะ",
    description: null,
    year: 2,
    semester: 1,
  },
  {
    code: "04-621-201",
    name_th: "วงจรไฟฟ้าสำหรับวิศวกรรมคอมพิวเตอร์",
    name_en: "Electrical Circuits for Computer Engineering",
    credits: 3,
    credit_detail: "3(2-3)",
    category: "หมวดวิชาเฉพาะ",
    description: null,
    year: 2,
    semester: 1,
  },
  {
    code: "04-621-203",
    name_th: "การออกแบบวงจรดิจิทัลและตรรกะ",
    name_en: "Digital Circuit and Logic Design",
    credits: 3,
    credit_detail: "3(2-3)",
    category: "หมวดวิชาเฉพาะ",
    description: null,
    year: 2,
    semester: 1,
  },
  {
    code: "04-622-201",
    name_th: "โครงสร้างข้อมูลและอัลกอริทึม",
    name_en: "Data Structure and Algorithms",
    credits: 3,
    credit_detail: "3(2-3)",
    category: "หมวดวิชาเฉพาะ",
    description: null,
    year: 2,
    semester: 1,
  },
  {
    code: "04-623-201",
    name_th: "การสื่อสารข้อมูลและเครือข่ายคอมพิวเตอร์",
    name_en: "Data Communication and Computer Networking",
    credits: 3,
    credit_detail: "3(3-0)",
    category: "หมวดวิชาเฉพาะ",
    description: null,
    year: 2,
    semester: 1,
  },
  {
    code: "04-624-201",
    name_th: "ทฤษฎีการคำนวณ",
    name_en: "Theory of Computation",
    credits: 3,
    credit_detail: "3(3-0)",
    category: "หมวดวิชาเฉพาะ",
    description: null,
    year: 2,
    semester: 1,
  },
];

export const courseTableMock: AgentResponse = {
  ...base({
    message_id: "dev-course-table-01",
    message: "นี่คือรายวิชาของ **ปี 2 เทอม 1** รวม 20 หน่วยกิตครับ",
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
