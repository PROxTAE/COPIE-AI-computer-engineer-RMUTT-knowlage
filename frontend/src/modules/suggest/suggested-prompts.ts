import type { UserType } from "@/types/contract";

export type SuggestedPrompt = { label: string; text: string };
export type PromptSet = readonly SuggestedPrompt[];

const prospectivePrompts: PromptSet = [
  { label: "ภาคคอมเรียนเกี่ยวกับอะไร?", text: "ภาคคอมเรียนเกี่ยวกับอะไร?" },
  { label: "ปี 1 เรียนอะไรบ้าง?", text: "ปี 1 เรียนอะไรบ้าง?" },
  { label: "ม.6 สมัครวิศวะคอมได้ไหม?", text: "ม.6 สมัครวิศวะคอมได้ไหม?" },
  { label: "จบแล้วทำงานอะไรได้?", text: "จบแล้วทำงานอะไรได้?" },
];

const generalStudentPrompts = (year: number): PromptSet => [
  { label: `ปี ${year} เรียนอะไรบ้าง?`, text: `ปี ${year} เรียนอะไรบ้าง?` },
  { label: "วิชานี้เกี่ยวกับอะไร?", text: "วิชานี้เกี่ยวกับอะไร?" },
  { label: "วิเคราะห์ skill ของฉัน", text: "วิเคราะห์ skill ของฉัน" },
];

const currentStudentPrompts: Record<1 | 2 | 3 | 4, PromptSet> = {
  1: generalStudentPrompts(1),
  2: [
    { label: "ปี 2 เทอม 1 เรียนอะไร?", text: "ปี 2 เทอม 1 เรียนอะไร?" },
    { label: "วิชา Data Structure เรียนอะไร?", text: "วิชา Data Structure เรียนอะไร?" },
    { label: "วิเคราะห์ skill ของฉัน", text: "วิเคราะห์ skill ของฉัน" },
  ],
  3: generalStudentPrompts(3),
  4: generalStudentPrompts(4),
};

const nearGraduatePrompts: PromptSet = [
  { label: "สรุป skill ของฉัน", text: "สรุป skill ของฉัน" },
  { label: "สหกิจศึกษาทำอย่างไร?", text: "สหกิจศึกษาทำอย่างไร?" },
  { label: "หลักสูตรมีกี่หน่วยกิต?", text: "หลักสูตรมีกี่หน่วยกิต?" },
];

export const SUGGESTED_PROMPTS = {
  prospective: prospectivePrompts,
  current_student: currentStudentPrompts,
  near_graduate: nearGraduatePrompts,
  default: prospectivePrompts,
};

export function getSuggestedPrompts(userType?: UserType | null, studyYear?: number | null): PromptSet {
  if (userType === "current_student" && studyYear && studyYear >= 1 && studyYear <= 4) {
    return SUGGESTED_PROMPTS.current_student[studyYear as 1 | 2 | 3 | 4];
  }

  if (userType === "near_graduate") return SUGGESTED_PROMPTS.near_graduate;
  if (userType === "prospective") return SUGGESTED_PROMPTS.prospective;
  return SUGGESTED_PROMPTS.default;
}