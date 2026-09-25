"use client";

import type { ChatMessage } from "@/types/contract";
import { ResponseRenderer, type AssessmentAnswer } from "@/modules/renderer";

type MessageListProps = {
  messages: ChatMessage[];
  liveMessageId?: string | null;
  disabled?: boolean;
  onAsk?: (text: string) => void;
  onSubmitAssessment?: (answers: AssessmentAnswer[]) => Promise<void>;
};

const unavailableAsk = () => {};
const unavailableAssessment = async () => {};

export function MessageList({ messages, liveMessageId = null, disabled = false, onAsk, onSubmitAssessment }: MessageListProps) {
  return (
    <div className="flex flex-col gap-6" role="log" aria-label="บทสนทนากับ COPIE" aria-live="polite">
      {messages.map((message) => message.role === "user" ? (
        <p key={message.id} className="ml-auto max-w-[90%] rounded-2xl border border-cyber-line bg-cyber-paper px-4 py-3 text-cyber-ink">
          {message.content}
        </p>
      ) : (
        <ResponseRenderer
          key={message.id}
          response={message.response}
          onAsk={onAsk ?? unavailableAsk}
          onSubmitAssessment={onSubmitAssessment ?? unavailableAssessment}
          disabled={disabled || !onAsk || !onSubmitAssessment}
          animate={message.id === liveMessageId}
        />
      ))}
    </div>
  );
}
