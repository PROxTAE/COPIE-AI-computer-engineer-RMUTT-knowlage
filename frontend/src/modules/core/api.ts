import type { AgentResponse, AssessmentSubmit, ChatRequest } from "@/types/contract";

export type AuthAdapter = {
  getToken: () => string | null;
  clearToken: () => void;
  onUnauthorized: () => void;
};

let authAdapter: AuthAdapter | null = null;
const authListeners = new Set<() => void>();

export function notifyApiAuthChanged() {
  authListeners.forEach((listener) => listener());
}

export function subscribeApiAuth(listener: () => void) {
  authListeners.add(listener);
  return () => { authListeners.delete(listener); };
}

export function getApiAuthSnapshot() {
  try {
    return Boolean(authAdapter?.getToken());
  } catch {
    return false;
  }
}

// P2 registers its token helpers when the user module is available.
export function configureApiAuth(adapter: AuthAdapter | null) {
  authAdapter = adapter;
  notifyApiAuthChanged();
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
      notifyApiAuthChanged();
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
  send: (body: ChatRequest, signal?: AbortSignal) =>
    api<AgentResponse>("/api/chat", { method: "POST", body: JSON.stringify(body), signal }),
  submitAssessment: (body: AssessmentSubmit, signal?: AbortSignal) =>
    api<AgentResponse>("/api/assessment/submit", { method: "POST", body: JSON.stringify(body), signal }),
};
