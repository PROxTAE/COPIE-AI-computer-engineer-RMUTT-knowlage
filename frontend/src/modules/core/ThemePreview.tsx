import Link from "next/link";
import { Button, Chip } from "@heroui/react";

import { CopieMascot, MascotStatePreview, type CopieMascotState } from "@/modules/mascot";

// Development preview of the White Cyberism theme and mascot states.
const STATES: CopieMascotState[] = ["idle", "listening", "thinking", "responding", "success", "no-answer", "skill-guide"];

const ROUTES = [
  { href: "/login", label: "Login", owner: "P2" },
  { href: "/onboarding", label: "Onboarding", owner: "P2" },
  { href: "/chat", label: "Chat", owner: "P1" },
  { href: "/dev", label: "Renderer playground", owner: "P6" },
];

export function ThemePreview() {
  return (
    <main className="copie-ui">
      <div className="copie-floor" />
      <div className="mx-auto flex max-w-7xl flex-col gap-12 px-4 py-10 sm:px-10">
        <header className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <span className="copie-wordmark">COPIE</span>
            <span className="hidden font-label text-[0.7rem] font-semibold uppercase leading-relaxed tracking-[0.14em] text-cyber-muted sm:block">
              AI Assistant
              <br />
              for your ideas
            </span>
          </div>
          <span className="copie-status flex items-center gap-2">
            <span className="copie-status-dot copie-status-pulse" /> AI // Active
          </span>
        </header>

        <section className="grid items-center gap-10 lg:grid-cols-[1.1fr_1fr]">
          <div className="flex flex-col gap-6">
            <span className="copie-eyebrow">AI agent for education</span>
            <h1 className="copie-heading text-4xl sm:text-6xl">ยินดีต้อนรับสู่ COPIE</h1>
            <p className="max-w-xl text-lg leading-relaxed text-cyber-muted">
              ผู้ช่วย AI ภาควิชาวิศวกรรมคอมพิวเตอร์ RMUTT — หน้านี้แสดงธีม White Cyberism, ฟอนต์ และมาสคอต 2.5D
              เพื่อให้ทุก module ใช้ชุดเดียวกัน
            </p>
            <div className="flex flex-wrap gap-3">
              <Button variant="primary">ตัวอย่างปุ่มหลัก</Button>
              <Button variant="outline">ตัวอย่างปุ่มรอง</Button>
            </div>
            <div className="flex flex-wrap gap-2">
              <Chip color="accent" variant="soft">หลักสูตร</Chip>
              <Chip color="accent" variant="soft">รายวิชา</Chip>
              <Chip color="accent" variant="soft">ทักษะ</Chip>
            </div>
          </div>
          <div className="relative grid place-items-center">
            <div className="copie-halo absolute" />
            <CopieMascot state="welcome" priority className="relative" />
          </div>
        </section>

        <section className="copie-response flex flex-col gap-4">
          <span className="copie-eyebrow">Type system</span>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="flex flex-col gap-2">
              <span className="copie-index text-3xl">01 /</span>
              <p className="font-display text-2xl font-bold italic">Kanit — หัวข้อ ภาพรวมหลักสูตร</p>
              <p className="text-cyber-muted">หัวข้อคำตอบ, ตัวเลขลำดับ, คะแนน (ตัวหนาเอียง)</p>
            </div>
            <div className="flex flex-col gap-2">
              <span className="copie-index text-3xl">02 /</span>
              <p className="font-label text-lg font-semibold uppercase tracking-[0.14em] text-cyber-blue">
                Chakra Petch — AI // Active · สถานะ
              </p>
              <p className="text-cyber-muted">ป้ายสถานะ, eyebrow, label เชิงเทคนิค</p>
            </div>
            <div className="flex flex-col gap-2">
              <span className="copie-index text-3xl">03 /</span>
              <p className="text-lg">IBM Plex Sans Thai — เนื้อหาภาษาไทยที่อ่านง่าย เรียนรู้การเขียนโปรแกรม โครงสร้างข้อมูล และอัลกอริทึม</p>
              <p className="text-cyber-muted">เนื้อหาคำตอบ, ฟอร์ม, ตาราง</p>
            </div>
            <div className="flex flex-col gap-2">
              <span className="copie-index text-3xl">04 /</span>
              <p className="font-wordmark text-3xl font-black tracking-tight">COPIE</p>
              <p className="text-cyber-muted">Unbounded — ใช้กับ wordmark เท่านั้น</p>
            </div>
          </div>
        </section>

        <section className="flex flex-col gap-4">
          <span className="copie-eyebrow">Mascot states (2.5D)</span>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 lg:grid-cols-7">
            {STATES.map((state) => (
              <figure key={state} className="copie-panel flex flex-col items-center gap-2 p-3">
                <CopieMascot state={state} layout="rail" animated={false} className="!w-full" />
                <figcaption className="copie-status text-[0.7rem]">{state}</figcaption>
              </figure>
            ))}
          </div>
        </section>

        <MascotStatePreview />

        <nav className="flex flex-wrap gap-3 pb-10">
          {ROUTES.map((r) => (
            <Link key={r.href} href={r.href} className="copie-button">
              {r.label} <span className="text-cyber-muted">· {r.owner}</span>
            </Link>
          ))}
        </nav>
      </div>
    </main>
  );
}
