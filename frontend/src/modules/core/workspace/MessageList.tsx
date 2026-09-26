"use client";

import type { ReactNode } from "react";

import type { AgentResponse, ChatMessage } from "@/types/contract";
import { ResponseRenderer, type AssessmentAnswer } from "@/modules/renderer";

type MessageListProps = {
  messages: ChatMessage[];
  liveMessageId?: string | null;
  disabled?: boolean;
  onAsk?: (text: string) => void;
  onSubmitAssessment?: (answers: AssessmentAnswer[], formResponse: AgentResponse) => Promise<void>;
  renderAssistantFooter?: (message: Extract<ChatMessage, { role: "assistant" }>) => ReactNode;
};

const unavailableAsk = () => {};
const unavailableAssessment = async () => {};

export function MessageList({
  messages,
  liveMessageId = null,
  disabled = false,
  onAsk,
  onSubmitAssessment,
  renderAssistantFooter,
}: MessageListProps) {
  return (
    <div className="flex flex-col gap-6" role="log" aria-label="บทสนทนากับ COPIE" aria-live="polite">
      {messages.map((message) => message.role === "user" ? (
        <p key={message.id} className="ml-auto max-w-[90%] rounded-2xl border border-cyber-line bg-cyber-paper px-4 py-3 text-cyber-ink">
          {message.content}
        </p>
      ) : (
        <div key={message.id} className="flex flex-col gap-3">
          <ResponseRenderer
            response={message.response}
            onAsk={onAsk ?? unavailableAsk}
            onSubmitAssessment={onSubmitAssessment ? (answers) => onSubmitAssessment(answers, message.response) : unavailableAssessment}
            disabled={disabled || !onAsk || !onSubmitAssessment}
            animate={message.id === liveMessageId}
          />
          {renderAssistantFooter?.(message)}
        </div>
      ))}
    </div>
  );
}
