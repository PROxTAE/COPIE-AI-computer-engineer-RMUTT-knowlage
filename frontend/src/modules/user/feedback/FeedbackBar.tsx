"use client";

import { useState } from "react";
import { Check, Copy, ThumbsDown, ThumbsUp } from "lucide-react";

import { api, ApiError } from "@/modules/core";
import type { FeedbackReason, FeedbackRequest } from "@/types/contract";

import { ReasonDialog } from "./ReasonDialog";

type Rating = "up" | "down";

type FeedbackBarProps = {
  messageId: string;
  initialFeedback: Rating | null;
  messageContent?: string;
};

function errorMessage(error: unknown) {
  return error instanceof ApiError ? error.message : "ส่ง feedback ไม่สำเร็จ กรุณาลองใหม่";
}

export function FeedbackBar({ messageId, initialFeedback, messageContent }: FeedbackBarProps) {
  const [selected, setSelected] = useState<Rating | null>(initialFeedback);
  const [copied, setCopied] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [reason, setReason] = useState<FeedbackReason | null>(null);
  const [comment, setComment] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const copyToClipboard = async () => {
    if (!messageContent) return;
    try {
      await navigator.clipboard.writeText(messageContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback
    }
  };

  const submit = async (body: FeedbackRequest) => {
    setPending(true);
    setError(null);
    try {
      await api<{ ok: true }>("/api/feedback", { method: "POST", body: JSON.stringify(body) });
      setSelected(body.rating);
      setDialogOpen(false);
      setReason(null);
      setComment("");
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setPending(false);
    }
  };

  const sendUp = () => {
    void submit({ message_id: messageId, rating: "up", reason: null, comment: null });
  };

  const sendDown = () => {
    if (!reason) {
      setError("กรุณาเลือกเหตุผล");
      return;
    }
    void submit({
      message_id: messageId,
      rating: "down",
      reason,
      comment: comment.trim() || null,
    });
  };

  return (
    <div className="flex flex-wrap items-center gap-3 pt-3 border-t border-[#d2e0f5]/60 mt-1" aria-label="ให้ feedback คำตอบนี้">
      {/* Copy Button matching Mockup 05 */}
      {messageContent && (
        <>
          <button
            type="button"
            onClick={() => { void copyToClipboard(); }}
            className="inline-flex items-center gap-2 rounded-full border border-[#d2e0f5] bg-white px-4 py-1.5 text-xs font-semibold text-[#080b12] hover:border-[#155ff2]/50 hover:bg-slate-50 transition-all cursor-pointer shadow-xs"
          >
            {copied ? (
              <>
                <Check className="size-3.5 text-emerald-600" />
                <span className="text-emerald-700">คัดลอกแล้ว</span>
              </>
            ) : (
              <>
                <Copy className="size-3.5 text-[#155ff2]" />
                <span>คัดลอก</span>
              </>
            )}
          </button>
          <span className="h-4 w-px bg-[#d2e0f5]" />
        </>
      )}

      {/* Feedback Rating */}
      <span className="text-xs font-medium text-[#6b82a6]">ข้อความนี้มีประโยชน์หรือไม่?</span>
      <button
        type="button"
        onClick={sendUp}
        disabled={pending}
        aria-label="ชอบคำตอบนี้"
        className={`flex size-8 items-center justify-center rounded-full border transition-all cursor-pointer ${
          selected === "up"
            ? "border-[#155ff2] bg-blue-50 text-[#155ff2]"
            : "border-[#d2e0f5] bg-white text-[#6b82a6] hover:border-[#155ff2]/50 hover:text-[#155ff2]"
        }`}
      >
        <ThumbsUp className="size-3.5" />
      </button>

      <button
        type="button"
        onClick={() => { setError(null); setDialogOpen(true); }}
        disabled={pending}
        aria-label="คำตอบนี้ควรปรับปรุง"
        className={`flex size-8 items-center justify-center rounded-full border transition-all cursor-pointer ${
          selected === "down"
            ? "border-red-500 bg-red-50 text-red-600"
            : "border-[#d2e0f5] bg-white text-[#6b82a6] hover:border-red-300 hover:text-red-600"
        }`}
      >
        <ThumbsDown className="size-3.5" />
      </button>

      {pending && <span className="text-xs text-[#6b82a6]" role="status">กำลังบันทึก...</span>}
      {error && !dialogOpen && <span className="text-xs text-red-700" role="alert">{error}</span>}

      <ReasonDialog
        open={dialogOpen}
        reason={reason}
        comment={comment}
        pending={pending}
        error={error}
        onReasonChange={setReason}
        onCommentChange={setComment}
        onCancel={() => { if (!pending) setDialogOpen(false); }}
        onSubmit={sendDown}
      />
    </div>
  );
}
