"use client";

import { create } from "zustand";

import type { AgentResponse, ChatMessage, ConversationDetail } from "@/types/contract";
import type { CopieMascotState } from "@/modules/mascot";
import type { AssessmentAnswer } from "@/modules/renderer";

import { ApiError, chatApi, getApiAuthSnapshot } from "./api";

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
  send: (text: string) => Promise<void>;
  submitAssessment: (answers: AssessmentAnswer[], formResponse?: AgentResponse) => Promise<void>;
  receiveResponse: (response: AgentResponse) => void;
  failRequest: (message: string) => void;
  loadConversation: (detail: ConversationDetail) => void;
  newConversation: () => void;
  setLayout: (layout: WorkspaceMode) => void;
  setCopieState: (state: CopieMascotState) => void;
};

const SHORT_ANSWER_LIMIT = 450;
let settleTimer: ReturnType<typeof setTimeout> | null = null;
let requestVersion = 0;
let activeController: AbortController | null = null;

function clearSettleTimer() {
  if (settleTimer) clearTimeout(settleTimer);
  settleTimer = null;
}

function cancelActiveRequest() {
  requestVersion += 1;
  activeController?.abort();
  activeController = null;
}

function requestError(error: unknown) {
  return error instanceof ApiError ? error.message : "ส่งคำขอไม่สำเร็จ กรุณาลองใหม่";
}

function latestAssessment(messages: ChatMessage[]): Extract<AgentResponse, { response_type: "assessment_form" }> | null {
  for (let index = messages.length - 1; index >= 0; index -= 1) {
    const message = messages[index];
    if (message.role === "assistant" && message.response.response_type === "assessment_form") return message.response;
  }
  return null;
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
  send: async (text) => {
    if (!getApiAuthSnapshot()) return;
    const message = text.trim();
    if (!get().beginRequest(message)) return;
    const version = ++requestVersion;
    const controller = new AbortController();
    activeController = controller;
    try {
      const response = await chatApi.send({ conversation_id: get().conversationId, message }, controller.signal);
      if (version === requestVersion) get().receiveResponse(response);
    } catch (error) {
      if (version === requestVersion) get().failRequest(requestError(error));
    } finally {
      if (version === requestVersion) activeController = null;
    }
  },
  submitAssessment: async (answers, formResponse) => {
    const form = formResponse?.response_type === "assessment_form" ? formResponse : latestAssessment(get().messages);
    if (!form || !get().conversationId || form.conversation_id !== get().conversationId || !getApiAuthSnapshot()) {
      throw new Error("ไม่พบแบบประเมินที่พร้อมส่ง");
    }
    if (get().pending) throw new Error("กรุณารอคำขอก่อนหน้า");
    clearSettleTimer();
    set({ pending: true, copieState: "thinking", error: null });
    const version = ++requestVersion;
    const controller = new AbortController();
    activeController = controller;
    try {
      const response = await chatApi.submitAssessment({
        conversation_id: form.conversation_id,
        assessment_id: form.data.assessment_id,
        answers,
      }, controller.signal);
      if (version === requestVersion) get().receiveResponse(response);
    } catch (error) {
      if (version === requestVersion) {
        get().failRequest(requestError(error));
        throw error;
      }
    } finally {
      if (version === requestVersion) activeController = null;
    }
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
    set({ pending: false, copieState: "idle", error: message });
  },
  loadConversation: (detail) => {
    cancelActiveRequest();
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
    cancelActiveRequest();
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
