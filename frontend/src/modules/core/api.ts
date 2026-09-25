import type { AgentResponse, AssessmentSubmit, ChatRequest } from "@/types/contract";

type AuthAdapter = {
  getToken: () => string | null;
  clearToken: () => void;
  onUnauthorized: () => void;
};

let authAdapter: AuthAdapter | null = null;

// P2 registers its token helpers when the user module is available.
export function configureApiAuth(adapter: AuthAdapter) {
  authAdapter = adapter;
}

export class ApiError extends Error {
  constructor(public status: number, detail: string) {
    super(detail);
    this.name = "ApiError";
  }
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30_000);
  const abort = () => controller.abort();
  if (init.signal?.aborted) controller.abort();
  init.signal?.addEventListener("abort", abort, { once: true });

  const headers = new Headers(init.headers);
  if (init.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const token = authAdapter?.getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  try {
    const response = await fetch(path, { ...init, headers, signal: controller.signal });
    if (response.status === 401) {
      authAdapter?.clearToken();
      authAdapter?.onUnauthorized();
    }
    if (!response.ok) {
      const body: unknown = await response.json().catch(() => null);
      const detail = body && typeof body === "object" && "detail" in body && typeof body.detail === "string"
        ? body.detail
        : `Request failed (${response.status})`;
      throw new ApiError(response.status, detail);
    }
    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (controller.signal.aborted && !init.signal?.aborted) throw new ApiError(0, "คำขอใช้เวลานานเกินไป กรุณาลองใหม่");
    throw new ApiError(0, "เชื่อมต่อเซิร์ฟเวอร์ไม่ได้ กรุณาลองใหม่");
  } finally {
    clearTimeout(timeout);
    init.signal?.removeEventListener("abort", abort);
  }
}

export const chatApi = {
  send: (body: ChatRequest) => api<AgentResponse>("/api/chat", { method: "POST", body: JSON.stringify(body) }),
  submitAssessment: (body: AssessmentSubmit) =>
    api<AgentResponse>("/api/assessment/submit", { method: "POST", body: JSON.stringify(body) }),
};
