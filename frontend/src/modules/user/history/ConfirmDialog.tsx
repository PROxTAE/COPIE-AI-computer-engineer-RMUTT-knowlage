"use client";

import { Button, Modal } from "@heroui/react";

type ConfirmDialogProps = {
  open: boolean;
  title: string;
  description: string;
  confirmLabel: string;
  pending?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
};

export function ConfirmDialog({ open, title, description, confirmLabel, pending = false, onConfirm, onCancel }: ConfirmDialogProps) {
  return (
    <Modal isOpen={open} onOpenChange={(isOpen) => { if (!isOpen && !pending) onCancel(); }}>
      <Modal.Backdrop className="bg-slate-950/40" isDismissable={!pending} isKeyboardDismissDisabled={pending}>
        <Modal.Container placement="center" size="sm">
          <Modal.Dialog className="border border-cyber-line">
            <Modal.Header>
              <Modal.Heading className="font-display text-lg font-semibold text-cyber-ink">{title}</Modal.Heading>
            </Modal.Header>
            <Modal.Body className="text-sm leading-relaxed text-cyber-muted">{description}</Modal.Body>
            <Modal.Footer>
              <Button variant="outline" onPress={onCancel} isDisabled={pending}>ยกเลิก</Button>
              <Button variant="danger" onPress={onConfirm} isDisabled={pending}>
                {pending ? "กำลังลบ..." : confirmLabel}
              </Button>
            </Modal.Footer>
          </Modal.Dialog>
        </Modal.Container>
      </Modal.Backdrop>
    </Modal>
  );
}
