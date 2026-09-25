// ชื่อและไอคอนของทักษะ 6 ด้านตาม SkillKey ใน contract
// ใช้ร่วมกันระหว่าง SkillRadar และที่อื่นที่ต้องแสดงชื่อด้าน
// ลำดับใน SKILL_ORDER คือลำดับแกนของ Radar และลำดับในรายการคะแนน
import { ChartColumn, Code, Cpu, Server, Share2, ShieldCheck, type LucideIcon } from "lucide-react";
import type { SkillKey } from "@/types/contract";

export interface SkillLabel {
  th: string;
  /** ชื่อสั้นสำหรับแกน Radar — ชื่อเต็มยาวเกินจนถูกตัดเมื่อกราฟแคบ */
  short: string;
  en: string;
  icon: LucideIcon;
}

export const SKILL_LABELS: Record<SkillKey, SkillLabel> = {
  frontend: { th: "ฟรอนต์เอนด์", short: "ฟรอนต์เอนด์", en: "Frontend", icon: Code },
  backend: { th: "แบ็กเอนด์", short: "แบ็กเอนด์", en: "Backend", icon: Server },
  network: { th: "เครือข่าย", short: "เครือข่าย", en: "Network", icon: Share2 },
  embedded: { th: "ระบบสมองกลฝังตัว", short: "สมองกลฝังตัว", en: "Embedded / IoT", icon: Cpu },
  ai_data: { th: "AI และข้อมูล", short: "AI / ข้อมูล", en: "AI / Data", icon: ChartColumn },
  cybersecurity: { th: "ความมั่นคงปลอดภัยไซเบอร์", short: "ไซเบอร์", en: "Cybersecurity", icon: ShieldCheck },
};

export const SKILL_ORDER: SkillKey[] = [
  "frontend",
  "backend",
  "network",
  "embedded",
  "ai_data",
  "cybersecurity",
];
