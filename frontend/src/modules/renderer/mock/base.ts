// Shared envelope for fixtures. Every mock spreads this, then adds response_type + data,
// so a contract change breaks the build instead of silently drifting.
import type { Action, AgentResponse, Intent, Source } from "@/types/contract";

export type ResponseBase = Omit<Extract<AgentResponse, { response_type: "text" }>, "response_type" | "data">;

interface BaseInput {
  message_id: string;
  message: string;
  intent: Intent;
  tool?: string | null;
  latency_ms?: number;
  sources?: Source[];
  actions?: Action[];
  conversation_id?: string;
}

export function base(input: BaseInput): ResponseBase {
  return {
    conversation_id: input.conversation_id ?? "dev-conversation",
    message_id: input.message_id,
    message: input.message,
    sources: input.sources ?? [],
    actions: input.actions ?? [],
    meta: {
      intent: input.intent,
      tool: input.tool ?? null,
      latency_ms: input.latency_ms ?? 1200,
    },
  };
}
