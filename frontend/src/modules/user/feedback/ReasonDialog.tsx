"use client";

import { Button, Modal } from "@heroui/react";

import type { FeedbackReason } from "@/types/contract";

const REASONS: { value: FeedbackReason; label: string }[] = [
  { value: "incorrect", label: "ข้อมูลไม่ถูกต้อง" },
  { value: "off_topic", label: "ไม่ตรงคำถาม" },
  { value: "hard_to_read", label: "อ่านยาก" },
  { value: "incomplete", label: "ข้อมูลไม่ครบ" },
  { value: "other", label: "อื่นๆ" },
];

type ReasonDialogProps = {
  open: boolean;
  reason: FeedbackReason | null;
  comment: string;
  pending: boolean;
  error: string | null;
  onReasonChange: (reason: FeedbackReason) => void;
  onCommentChange: (comment: string) => void;
  onCancel: () => void;
  onSubmit: () => void;
};

export function ReasonDialog(props: ReasonDialogProps) {
  return (
    <Modal
      isOpen={props.open}
      onOpenChange={(open) => {
        if (!open && !props.pending) props.onCancel();
      }}
    >
      <Modal.Backdrop
        className="bg-slate-950/35"
        isDismissable={!props.pending}
        isKeyboardDismissDisabled={props.pending}
      >
        <Modal.Container placement="center" size="md">
          <Modal.Dialog className="border border-cyber-line">
            <Modal.Header>
              <Modal.Heading className="font-display text-xl font-semibold text-cyber-ink">
                คำตอบนี้ควรปรับตรงไหน
              </Modal.Heading>
              <p className="text-sm text-cyber-muted">เลือกเหตุผลหนึ่งข้อเพื่อช่วยให้ COPIE พัฒนาขึ้น</p>
            </Modal.Header>
            <Modal.Body className="text-cyber-ink">
              <fieldset className="grid gap-2" disabled={props.pending}>
                {REASONS.map((item) => (
                  <label key={item.value} className={`cursor-pointer rounded-xl border px-3 py-2 text-sm ${props.reason === item.value ? "border-cyber-blue bg-blue-50 text-cyber-blue" : "border-cyber-line"}`}>
                    <input
                      className="mr-2"
                      type="radio"
                      name="feedback_reason"
                      checked={props.reason === item.value}
                      onChange={() => props.onReasonChange(item.value)}
                    />
                    {item.label}
                  </label>
                ))}
              </fieldset>
              <label className="mt-4 grid gap-1 text-sm font-semibold text-cyber-ink">
                ความคิดเห็นเพิ่มเติม (ไม่บังคับ)
                <textarea
                  className="min-h-24 resize-y rounded-xl border border-cyber-line bg-white px-3 py-2 font-normal outline-none focus:border-cyber-blue"
                  value={props.comment}
                  maxLength={500}
                  disabled={props.pending}
                  onChange={(event) => props.onCommentChange(event.target.value)}
                />
                <span className="text-right text-xs text-cyber-muted">{props.comment.length}/500</span>
              </label>
              {props.error && <p className="mt-3 text-sm text-red-700" role="alert">{props.error}</p>}
            </Modal.Body>
            <Modal.Footer>
              <Button variant="outline" onPress={props.onCancel} isDisabled={props.pending}>ยกเลิก</Button>
              <Button variant="primary" onPress={props.onSubmit} isDisabled={props.pending || !props.reason}>
                {props.pending ? "กำลังส่ง..." : "ส่ง feedback"}
              </Button>
            </Modal.Footer>
          </Modal.Dialog>
        </Modal.Container>
      </Modal.Backdrop>
    </Modal>
  );
}
