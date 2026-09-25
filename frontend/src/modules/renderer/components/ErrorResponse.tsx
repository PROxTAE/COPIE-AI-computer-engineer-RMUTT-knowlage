// สถานะผิดพลาด — ข้อความอธิบายตาม data.code พร้อมปุ่มลองถามคำถามเดิมอีกครั้ง
// ใช้ทั้งไอคอนและข้อความ ไม่สื่อด้วยสีอย่างเดียว
"use client";

import { CircleAlert, RotateCcw } from "lucide-react";
import type { Action, ErrorData } from "@/types/contract";
import { FOCUS_RING } from "./styles";

const MESSAGES: Record<ErrorData["code"], string> = {
  llm_unavailable: "ตอนนี้ระบบ AI ไม่พร้อมใช้งานชั่วคราว ลองส่งคำถามอีกครั้งในอีกสักครู่ครับ",
  tool_failed: "ผมดึงข้อมูลจากระบบของภาคไม่สำเร็จ ลองถามใหม่อีกครั้งหรือเปลี่ยนคำถามดูครับ",
  unknown: "เกิดข้อผิดพลาดที่ไม่คาดคิด ลองถามใหม่อีกครั้งครับ",
};

interface ErrorResponseProps {
  data: ErrorData;
  /** action ตัวแรกที่เป็น "ask" ใช้เป็นคำถามสำหรับปุ่มลองใหม่ */
  actions: Action[];
  onAsk: (text: string) => void;
  disabled?: boolean;
}

export function ErrorResponse({ data, actions, onAsk, disabled = false }: ErrorResponseProps) {
  const retry = actions.find((action) => action.type === "ask" && action.payload.text);

  return (
    <section
      role="alert"
      className="flex flex-col gap-3 rounded-xl border border-danger/30 bg-danger/8 p-4"
      aria-label="เกิดข้อผิดพลาด"
    >
      <p className="flex items-start gap-2 text-ink">
        <CircleAlert aria-hidden="true" className="mt-0.5 size-5 shrink-0 text-danger" />
        {MESSAGES[data.code]}
      </p>

      {retry?.payload.text && (
        <button
          type="button"
          onClick={() => onAsk(retry.payload.text as string)}
          disabled={disabled}
          className={`inline-flex items-center gap-2 self-start rounded-lg border border-danger/40 px-4 py-2 text-sm font-medium text-danger disabled:opacity-50 ${FOCUS_RING}`}
        >
          <RotateCcw aria-hidden="true" className="size-4" />
          ลองใหม่อีกครั้ง
        </button>
      )}

      <p className="text-xs text-muted">รหัสข้อผิดพลาด: {data.code}</p>
    </section>
  );
}
