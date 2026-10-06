import { api } from "@/modules/core";
import type {
  ConversationDetail,
  ConversationSummary,
  ConversationUpdate,
  Project,
  ProjectInput,
} from "@/types/contract";

const conversationPath = (id: string) => `/api/conversations/${encodeURIComponent(id)}`;
const projectPath = (id: string) => `/api/projects/${encodeURIComponent(id)}`;
const json = (method: string, body: unknown): RequestInit => ({ method, body: JSON.stringify(body) });

export const historyApi = {
  list: () => api<ConversationSummary[]>("/api/conversations"),
  detail: (id: string) => api<ConversationDetail>(conversationPath(id)),
  update: (id: string, changes: ConversationUpdate) =>
    api<ConversationSummary>(conversationPath(id), json("PATCH", changes)),
  remove: (id: string) => api<void>(conversationPath(id), { method: "DELETE" }),

  projects: () => api<Project[]>("/api/projects"),
  createProject: (body: ProjectInput) => api<Project>("/api/projects", json("POST", body)),
  renameProject: (id: string, body: ProjectInput) => api<Project>(projectPath(id), json("PATCH", body)),
  removeProject: (id: string) => api<void>(projectPath(id), { method: "DELETE" }),
};
