// คำตอบแบบข้อความของ COPIE — ม็อกอัพ 04-chat-answer / 05-reading-mode
// หัวเรื่องกำกับ (eyebrow) + เนื้อหา markdown + พิมพ์ทีละตัวอักษร
// คลิกที่คำตอบเพื่อข้ามแอนิเมชัน และปิดอัตโนมัติเมื่อผู้ใช้ตั้งค่า reduced motion
"use client";

import { useEffect, useState, useSyncExternalStore } from "react";
import { useReducedMotion } from "motion/react";
import { Markdown } from "./Markdown";
import { FOCUS_RING } from "./styles";

const TYPING_MS_PER_CHAR = 20; // ตามแผน P6

interface TextResponseProps {
  message: string;
  /** จำนวนแหล่งอ้างอิง — ใช้ตัดสินว่า [n] ตัวไหนกดได้ */
  citationCount?: number;
  onCitationClick?: (index: number) => void;
  /** พิมพ์ทีละตัวอักษร (ใช้กับคำตอบที่เพิ่งมาถึงเท่านั้น) */
  animate?: boolean;
  /** แถบ "AI AGENT RESPONSE" ด้านบนตามม็อกอัพ */
  showEyebrow?: boolean;
}

export function TextResponse({
  message,
  citationCount = 0,
  onCitationClick,
  animate = false,
  showEyebrow = false,
}: TextResponseProps) {
  const reducedMotion = useReducedMotion();
  const { visible, done, skip } = useTypewriter(message, animate, reducedMotion === true);

  return (
    <section className="copie-response flex flex-col gap-4">
      {showEyebrow && (
        <div className="flex items-center gap-2">
          <span className="size-2 bg-cyber-blue" />
          <span className="font-label text-xs font-bold tracking-[0.2em] text-cyber-blue uppercase">
            AI AGENT RESPONSE
          </span>
          <span aria-hidden="true" className="h-px flex-1 bg-gradient-to-r from-cyber-blue/25 to-transparent ml-2" />
        </div>
      )}

      {/* ระหว่างพิมพ์ คลิกที่ใดก็ได้ในคำตอบเพื่อแสดงข้อความเต็มทันที */}
      <div onClick={done ? undefined : skip}>
        <Markdown className="flex flex-col gap-4" onCitationClick={onCitationClick} citationCount={citationCount}>
          {visible}
        </Markdown>
      </div>

      {!done && (
        <button
          type="button"
          onClick={skip}
          className={`self-start rounded text-xs text-muted underline underline-offset-2 hover:text-ink ${FOCUS_RING}`}
        >
          ข้ามการพิมพ์
        </button>
      )}
    </section>
  );
}

// แสดงข้อความทีละตัวอักษร; animate = false คืนข้อความเต็มทันที
//
// hydration: ทั้งฝั่ง server และ render รอบแรกของ client ต้องได้ผลเหมือนกันเสมอ
// จึงตัดสินจาก animate อย่างเดียวก่อน แล้วค่อยดู reduced motion หลัง mount
// รีเซ็ตตอน render (ไม่ใช่ใน effect) ตามแนวทาง React 19 — effect ตั้ง timer อย่างเดียว
function useTypewriter(text: string, animate: boolean, reducedMotion: boolean) {
  const mounted = useIsMounted();
  const typing = animate && mounted && !reducedMotion;

  const key = `${animate}|${text}`;
  const [progress, setProgress] = useState(() => ({ key, count: animate ? 0 : text.length }));

  if (progress.key !== key) {
    setProgress({ key, count: animate ? 0 : text.length });
  }

  useEffect(() => {
    if (!typing) return;

    const timer = window.setInterval(() => {
      setProgress((current) => {
        if (current.key !== key) return current; // ข้อความเปลี่ยนแล้ว ปล่อยให้รอบใหม่จัดการ
        if (current.count >= text.length) {
          window.clearInterval(timer);
          return current;
        }
        return { ...current, count: current.count + 1 };
      });
    }, TYPING_MS_PER_CHAR);

    return () => window.clearInterval(timer);
  }, [key, text.length, typing]);

  let count: number;
  if (!animate) count = text.length;
  else if (!mounted) count = 0; // render รอบแรก: ยังไม่เริ่มพิมพ์
  else if (reducedMotion) count = text.length; // ผู้ใช้ปิดแอนิเมชัน: ขึ้นเต็มทันที
  else count = progress.key === key ? progress.count : 0;

  return {
    visible: text.slice(0, count),
    done: count >= text.length,
    skip: () => setProgress({ key, count: text.length }),
  };
}

const subscribeToNothing = () => () => {};

// true หลัง hydration เท่านั้น — ใช้เลี่ยงการอ่านค่าจากเบราว์เซอร์ตอน render รอบแรก
function useIsMounted() {
  return useSyncExternalStore(
    subscribeToNothing,
    () => true,
    () => false,
  );
}
