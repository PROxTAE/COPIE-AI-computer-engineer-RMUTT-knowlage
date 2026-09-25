// คลาสที่ใช้ซ้ำทั้งโมดูล — เขียนเป็นสตริงเต็มเพื่อให้ Tailwind สแกนเจอ
//
// ปุ่มและลิงก์ทุกตัวในโมดูลนี้ต้องมี focus ring ที่มองเห็นได้ (Acceptance checklist ข้อ a11y)
// ใช้ outline แทน ring เพื่อไม่ให้ไปชนกับ border ของการ์ดที่มีอยู่แล้ว
export const FOCUS_RING =
  "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-copie-teal";
