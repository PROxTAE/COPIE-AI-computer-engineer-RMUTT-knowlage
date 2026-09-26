"use client";

import { useState } from "react";
import { Button } from "@heroui/react";

import { api, ApiError, Icon } from "@/modules/core";
import type { FeedbackReason, FeedbackRequest } from "@/types/contract";

import { ReasonDialog } from "./ReasonDialog";

type Rating = "up" | "down";

type FeedbackBarProps = {
  messageId: string;
  initialFeedback: Rating | null;
};

function errorMessage(error: unknown) {
  return error instanceof ApiError ? error.message : "ส่ง feedback ไม่สำเร็จ กรุณาลองใหม่";
}

export function FeedbackBar({ messageId, initialFeedback }: FeedbackBarProps) {
  const [selected, setSelected] = useState<Rating | null>(initialFeedback);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [reason, setReason] = useState<FeedbackReason | null>(null);
  const [comment, setComment] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
    <div className="flex flex-wrap items-center gap-2 border-t border-cyber-line pt-3" aria-label="ให้ feedback คำตอบนี้">
      <span className="text-xs font-semibold text-cyber-muted">คำตอบนี้เป็นประโยชน์ไหม</span>
      <Button
        isIconOnly
        size="sm"
        variant={selected === "up" ? "primary" : "outline"}
        aria-label="ชอบคำตอบนี้"
        isDisabled={pending}
        onPress={sendUp}
      >
        <Icon name="thumb-up" size={16} />
      </Button>
      <Button
        isIconOnly
        size="sm"
        variant={selected === "down" ? "primary" : "outline"}
        aria-label="คำตอบนี้ควรปรับปรุง"
        isDisabled={pending}
        onPress={() => { setError(null); setDialogOpen(true); }}
      >
        <Icon name="thumb-down" size={16} />
      </Button>
      {pending && <span className="text-xs text-cyber-muted" role="status">กำลังบันทึก...</span>}
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
