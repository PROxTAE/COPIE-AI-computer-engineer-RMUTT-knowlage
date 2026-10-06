// LOCKED: change only via a contract/* PR approved by P1 + P3.
// Keep in sync with backend/app/schemas/contract.py

// ---------- Interaction mode ----------
// Persona + theme of COPIE. Changes tone only; facts, sources and scores stay the same.
export type InteractionMode = "normal" | "devil" | "developer";

// ---------- User ----------
export type UserType = "prospective" | "current_student" | "near_graduate";
export type AgeRange = "under_18" | "18_20" | "21_23" | "24_plus";

export interface User {
  id: string;
  email: string;
  name: string;
  picture_url: string | null;
  display_name: string | null;
  age_range: AgeRange | null;
  user_type: UserType | null;
  study_year: number | null; // 1-4 (4 = year 4+), null if not a student
  onboarded: boolean;
}

export interface AuthResponse {
  access_token: string;
  user: User;
  is_new_user: boolean;
}

export interface ProfileUpdate {
  display_name: string;
  age_range: AgeRange;
  user_type: UserType;
  study_year: number | null;
}

// ---------- Skill ----------
export type SkillKey = "frontend" | "backend" | "network" | "embedded" | "ai_data" | "cybersecurity";
export type SkillScores = Record<SkillKey, number>; // integer 0-100

export interface SkillDimension {
  key: string;
  label: string;
  short_label?: string | null;
  score: number; // 0-100
  description?: string | null;
}

export interface SkillProfile {
  scores: SkillScores;
  top_skills: SkillKey[];
  taken_at: string; // ISO 8601
  topic?: string | null;
  score?: number | null;
  title?: string | null;
  dimensions?: SkillDimension[] | null;
  custom_top_skills?: string[] | null;
}

// ---------- Curriculum ----------
export interface Course {
  code: string;
  name_th: string;
  name_en: string;
  credits: number;
  credit_detail: string | null; // e.g. "3(2-2-5)"
  category: string | null;      // e.g. "หมวดวิชาเฉพาะ"
  description: string | null;
  year: number;
  semester: number;
}

// ---------- Response data per type ----------
export interface CourseTableData {
  year: number;
  semester: number;
  courses: Course[];
  total_credits: number;
}

export interface InfoCard {
  title: string;
  body: string; // markdown
  icon: string | null; // lucide icon name, e.g. "cpu"
  tags: string[];
}
export interface CardsData { cards: InfoCard[] }

export interface AssessmentOption { value: number; label: string } // value 0-4
export interface AssessmentQuestion { id: string; text: string; options: AssessmentOption[] }
export interface AssessmentFormData {
  assessment_id: string; // "skill_v1"
  title: string;
  questions: AssessmentQuestion[];
}

export interface SkillRadarData {
  scores: SkillScores;
  top_skills: SkillKey[];
  summary: string; // markdown, written by LLM from the computed scores
  taken_at: string;
  topic?: string | null;
  title?: string | null;
  dimensions?: SkillDimension[] | null;
  custom_top_skills?: string[] | null;
}

export interface ErrorData { code: "llm_unavailable" | "tool_failed" | "unknown" }

// ---------- Agent response ----------
export type Intent =
  | "department_info" | "curriculum" | "course_detail"
  | "skill_analysis" | "general" | "clarify";

export interface Source {
  doc_id: string;
  title: string;
  section: string | null;
  url: string | null;
  snippet: string;
  score: number;
}

export interface Action {
  type: "ask" | "open_url";
  label: string;
  payload: { text?: string; url?: string };
}

interface BaseResponse {
  conversation_id: string;
  message_id: string;
  message: string; // markdown, what COPIE says
  sources: Source[]; // render SourceViewer whenever non-empty
  actions: Action[]; // follow-up chips
  meta: { intent: Intent; tool: string | null; latency_ms: number; interaction_mode?: InteractionMode }; // missing in old history = "normal"
}

export type AgentResponse =
  | (BaseResponse & { response_type: "text"; data: null })
  | (BaseResponse & { response_type: "course_table"; data: CourseTableData })
  | (BaseResponse & { response_type: "cards"; data: CardsData })
  | (BaseResponse & { response_type: "assessment_form"; data: AssessmentFormData })
  | (BaseResponse & { response_type: "skill_radar"; data: SkillRadarData })
  | (BaseResponse & { response_type: "error"; data: ErrorData });

export type ResponseType = AgentResponse["response_type"];

// ---------- Requests ----------
export interface ChatRequest {
  conversation_id: string | null;
  message: string;
  interaction_mode?: InteractionMode; // server default "normal"
}

export interface AssessmentSubmit {
  conversation_id: string;
  assessment_id: string;
  answers: { question_id: string; value: number }[];
  interaction_mode?: InteractionMode; // server default "normal"
}

export type FeedbackReason = "incorrect" | "off_topic" | "hard_to_read" | "incomplete" | "other";
export interface FeedbackRequest {
  message_id: string;
  rating: "up" | "down";
  reason: FeedbackReason | null;
  comment: string | null;
}

// ---------- History ----------
export interface ConversationSummary {
  id: string;
  title: string;
  updated_at: string;
  last_message?: string | null;
  snippet?: string | null;
  project_id?: string | null; // null/missing = not in a project
}

// PATCH /api/conversations/{id}: send only what changes; project_id: null removes it from its project
export interface ConversationUpdate { title?: string; project_id?: string | null }

// A user's folder that groups related conversations
export interface Project {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
  conversation_count: number;
}

export interface ProjectInput { name: string } // 1-60 chars

export type ChatMessage =
  | { id: string; role: "user"; content: string; created_at: string }
  | { id: string; role: "assistant"; response: AgentResponse; feedback: "up" | "down" | null; created_at: string };

export interface ConversationDetail { id: string; title: string; messages: ChatMessage[] }

// ---------- Stats (optional) ----------
export interface Stats {
  total_users: number;
  total_messages: number;
  intent_counts: Record<Intent, number>;
  feedback_up: number;
  feedback_down: number;
  avg_latency_ms: number;
}
