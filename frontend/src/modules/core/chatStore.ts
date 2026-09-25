"use client";

import { create } from "zustand";

import type { AgentResponse, ChatMessage, ConversationDetail } from "@/types/contract";
import type { CopieMascotState } from "@/modules/mascot";

export type WorkspaceMode = "center" | "split" | "rail" | "hidden";

type ChatState = {
  conversationId: string | null;
  messages: ChatMessage[];
  liveMessageId: string | null;
  copieState: CopieMascotState;
  layout: WorkspaceMode;
  lastVisibleLayout: Exclude<WorkspaceMode, "hidden">;
  pending: boolean;
  error: string | null;
  beginRequest: (text: string) => boolean;
  receiveResponse: (response: AgentResponse) => void;
  failRequest: (message: string) => void;
  loadConversation: (detail: ConversationDetail) => void;
  newConversation: () => void;
  setLayout: (layout: WorkspaceMode) => void;
  setCopieState: (state: CopieMascotState) => void;
};

const SHORT_ANSWER_LIMIT = 450;
let settleTimer: ReturnType<typeof setTimeout> | null = null;

function clearSettleTimer() {
  if (settleTimer) clearTimeout(settleTimer);
  settleTimer = null;
}

export function layoutFromResponse(response: AgentResponse): Exclude<WorkspaceMode, "hidden"> {
  if (response.response_type === "text" && response.message.length <= SHORT_ANSWER_LIMIT) return "split";
  return "rail";
}

export function mascotStateFromResponse(response: AgentResponse): CopieMascotState {
  if (response.response_type === "error" ||
    (response.meta.tool === "rag.search_department_knowledge" && response.sources.length === 0)) return "no-answer";
  if (response.response_type === "skill_radar") return "success";
  if (response.response_type === "assessment_form") return "skill-guide";
  return "responding";
}

function latestAssistant(messages: ChatMessage[]): AgentResponse | null {
  for (let index = messages.length - 1; index >= 0; index -= 1) {
    const message = messages[index];
    if (message.role === "assistant") return message.response;
  }
  return null;
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversationId: null,
  messages: [],
  liveMessageId: null,
  copieState: "idle",
  layout: "center",
  lastVisibleLayout: "center",
  pending: false,
  error: null,
  beginRequest: (text) => {
    const message = text.trim();
    if (!message || message.length > 1000 || get().pending) return false;
    clearSettleTimer();
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: message,
      created_at: new Date().toISOString(),
    };
    set((state) => ({
      messages: [...state.messages, userMessage],
      liveMessageId: null,
      copieState: "thinking",
      pending: true,
      error: null,
    }));
    return true;
  },
  receiveResponse: (response) => {
    clearSettleTimer();
    const layout = layoutFromResponse(response);
    const copieState = mascotStateFromResponse(response);
    const assistantMessage: ChatMessage = {
      id: response.message_id,
      role: "assistant",
      response,
      feedback: null,
      created_at: new Date().toISOString(),
    };
    set((state) => ({
      conversationId: response.conversation_id,
      messages: [...state.messages, assistantMessage],
      liveMessageId: response.message_id,
      copieState,
      layout: state.layout === "hidden" ? "hidden" : layout,
      lastVisibleLayout: layout,
      pending: false,
      error: null,
    }));
    if (copieState === "responding") {
      settleTimer = setTimeout(() => {
        if (get().copieState === "responding") set({ copieState: "idle" });
        settleTimer = null;
      }, 2_500);
    }
  },
  failRequest: (message) => {
    clearSettleTimer();
    set({ pending: false, copieState: "no-answer", error: message });
  },
  loadConversation: (detail) => {
    clearSettleTimer();
    const response = latestAssistant(detail.messages);
    const layout = response ? layoutFromResponse(response) : "center";
    set({
      conversationId: detail.id,
      messages: detail.messages,
      liveMessageId: null,
      copieState: "idle",
      layout,
      lastVisibleLayout: layout,
      pending: false,
      error: null,
    });
  },
  newConversation: () => {
    clearSettleTimer();
    set({
      conversationId: null,
      messages: [],
      liveMessageId: null,
      copieState: "idle",
      layout: "center",
      lastVisibleLayout: "center",
      pending: false,
      error: null,
    });
  },
  setLayout: (layout) => set((state) => ({
    layout,
    lastVisibleLayout: layout === "hidden" ? state.lastVisibleLayout : layout,
  })),
  setCopieState: (copieState) => set({ copieState }),
}));
