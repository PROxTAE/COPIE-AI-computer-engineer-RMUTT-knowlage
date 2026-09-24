# 00 — API and Data Contracts

> เจ้าของ: **P3 (Backend Lead) + P1 (Frontend Lead)** · ทุกคนต้องอ่านก่อนเขียนโค้ด
> Contract Freeze v1 = **Day 1 12:00** · หลังจากนั้นเปลี่ยนได้เฉพาะแบบ additive ผ่าน branch `contract/<change>` (ดู `00_GIT_DELIVERY_RULES.md` §6)

## 1. Cross-cutting conventions

| เรื่อง | กติกา |
|---|---|
| Base path | `/api` (frontend เรียกผ่าน Next.js rewrite ไม่ต้องใส่ host) |
| Auth | `Authorization: Bearer <JWT>` ทุก endpoint ยกเว้น `/api/auth/*`, `/api/health` |
| Content type | `application/json; charset=utf-8` ทั้ง request/response |
| ID | `uuid4` เป็น string ทุกตัว |
| เวลา | ISO 8601 UTC เช่น `2026-09-24T09:30:00Z` — frontend แปลงเป็นเวลาไทยเอง |
| ชื่อ field | `snake_case` ทั้งสองฝั่ง (ไม่แปลง camelCase) |
| Error | HTTP 4xx/5xx + `{"detail": "ข้อความภาษาไทยที่ผู้ใช้อ่านเข้าใจ"}` (FastAPI default) |
| ความผิดพลาดของ Agent | ยังตอบ HTTP 200 แต่ `response_type = "error"` + `data.code` เพื่อให้ COPIE แสดงข้อความ + ปุ่มลองใหม่ |
| Validation | Backend validate ทุก request/response ด้วย Pydantic; frontend ใช้ type จาก `contract.ts` |
| Timeout | frontend รอ `/api/chat` ได้สูงสุด 30 วินาที; backend ตั้ง `LLM_TIMEOUT_S=20` |

| HTTP status | ใช้เมื่อ |
|---|---|
| 200 | สำเร็จ (รวม agent error ที่จัดการแล้ว) |
| 400 / 422 | body ผิดรูปแบบ (FastAPI validation) |
| 401 | ไม่มี/หมดอายุ token → frontend ล้าง token แล้วพาไป `/login` |
| 403 | เข้าถึง conversation ของคนอื่น |
| 404 | ไม่พบ resource เช่น `GET /api/skills/me` ยังไม่เคยทำแบบประเมิน |
| 500 | bug ที่ไม่ได้ตั้งใจ — ต้องเปิด Issue |

## 2. Public API (Freeze Day 1 12:00)

Base path: `/api` · Auth: `Authorization: Bearer <JWT>` ทุก endpoint ยกเว้น `auth/*` และ `health`
Error format (FastAPI default): `HTTP 4xx/5xx` + `{"detail": "ข้อความ"}`

| Method | Path | Body | Response | เจ้าของ |
|---|---|---|---|---|
| GET | `/api/health` | – | `{"status":"ok"}` | P3 |
| POST | `/api/auth/google` | `{id_token}` | `AuthResponse` | P2 |
| POST | `/api/auth/dev` | `{email, name}` (เฉพาะ `DEV_AUTH=true`) | `AuthResponse` | P2 |
| GET | `/api/users/me` | – | `User` | P2 |
| PUT | `/api/users/me/profile` | `ProfileUpdate` | `User` (onboarded = true) | P2 |
| POST | `/api/chat` | `ChatRequest` | `AgentResponse` | P3 |
| POST | `/api/assessment/submit` | `AssessmentSubmit` | `AgentResponse` (skill_radar) | P3 |
| GET | `/api/skills/me` | – | `SkillProfile` หรือ 404 | P2 |
| GET | `/api/conversations` | – | `ConversationSummary[]` (ใหม่สุดก่อน) | P2 |
| GET | `/api/conversations/{id}` | – | `ConversationDetail` | P2 |
| POST | `/api/feedback` | `FeedbackRequest` | `{"ok": true}` (ส่งซ้ำ = อัปเดต) | P2 |
| GET | `/api/stats` | – | `Stats` (optional, Monitoring) | P2 |

---


## 3. 🔒 Contract Files (LOCKED)

> สองไฟล์นี้คือ "แหล่งความจริงเดียว" ของทั้งทีม — P1 สร้าง `contract.ts`, P3 สร้าง `contract.py` ใน Day 1 ตามนี้ทุกตัวอักษร

### 3.1 `frontend/src/types/contract.ts`

```ts
// LOCKED: change only via a contract/* PR approved by P1 + P3.
// Keep in sync with backend/app/schemas/contract.py

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

export interface SkillProfile {
  scores: SkillScores;
  top_skills: SkillKey[];
  taken_at: string; // ISO 8601
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
  meta: { intent: Intent; tool: string | null; latency_ms: number };
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
export interface ChatRequest { conversation_id: string | null; message: string }

export interface AssessmentSubmit {
  conversation_id: string;
  assessment_id: string;
  answers: { question_id: string; value: number }[];
}

export type FeedbackReason = "incorrect" | "off_topic" | "hard_to_read" | "incomplete" | "other";
export interface FeedbackRequest {
  message_id: string;
  rating: "up" | "down";
  reason: FeedbackReason | null;
  comment: string | null;
}

// ---------- History ----------
export interface ConversationSummary { id: string; title: string; updated_at: string }

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
```

### 3.2 `backend/app/schemas/contract.py`

```python
# LOCKED: change only via a contract/* PR approved by P1 + P3.
# Keep in sync with frontend/src/types/contract.ts
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field

UserType = Literal["prospective", "current_student", "near_graduate"]
AgeRange = Literal["under_18", "18_20", "21_23", "24_plus"]
SkillKey = Literal["frontend", "backend", "network", "embedded", "ai_data", "cybersecurity"]
Intent = Literal["department_info", "curriculum", "course_detail", "skill_analysis", "general", "clarify"]
FeedbackReason = Literal["incorrect", "off_topic", "hard_to_read", "incomplete", "other"]
SKILL_KEYS: list[str] = ["frontend", "backend", "network", "embedded", "ai_data", "cybersecurity"]


# ---------- User ----------
class User(BaseModel):
    id: str
    email: str
    name: str
    picture_url: Optional[str] = None
    display_name: Optional[str] = None
    age_range: Optional[AgeRange] = None
    user_type: Optional[UserType] = None
    study_year: Optional[int] = Field(default=None, ge=1, le=4)
    onboarded: bool = False


class AuthResponse(BaseModel):
    access_token: str
    user: User
    is_new_user: bool


class ProfileUpdate(BaseModel):
    display_name: str = Field(min_length=1, max_length=50)
    age_range: AgeRange
    user_type: UserType
    study_year: Optional[int] = Field(default=None, ge=1, le=4)


# ---------- Skill ----------
class SkillScores(BaseModel):
    frontend: int = Field(ge=0, le=100)
    backend: int = Field(ge=0, le=100)
    network: int = Field(ge=0, le=100)
    embedded: int = Field(ge=0, le=100)
    ai_data: int = Field(ge=0, le=100)
    cybersecurity: int = Field(ge=0, le=100)


class SkillProfile(BaseModel):
    scores: SkillScores
    top_skills: list[SkillKey]
    taken_at: str


# ---------- Curriculum ----------
class Course(BaseModel):
    code: str
    name_th: str
    name_en: str
    credits: int
    credit_detail: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    year: int
    semester: int


class CourseTableData(BaseModel):
    year: int
    semester: int
    courses: list[Course]
    total_credits: int


class InfoCard(BaseModel):
    title: str
    body: str
    icon: Optional[str] = None
    tags: list[str] = []


class CardsData(BaseModel):
    cards: list[InfoCard]


class AssessmentOption(BaseModel):
    value: int = Field(ge=0, le=4)
    label: str


class AssessmentQuestion(BaseModel):
    id: str
    text: str
    options: list[AssessmentOption]


class AssessmentFormData(BaseModel):
    assessment_id: str
    title: str
    questions: list[AssessmentQuestion]


class SkillRadarData(BaseModel):
    scores: SkillScores
    top_skills: list[SkillKey]
    summary: str
    taken_at: str


class ErrorData(BaseModel):
    code: Literal["llm_unavailable", "tool_failed", "unknown"]


# ---------- Agent response ----------
class Source(BaseModel):
    doc_id: str
    title: str
    section: Optional[str] = None
    url: Optional[str] = None
    snippet: str
    score: float


class ActionPayload(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None


class Action(BaseModel):
    type: Literal["ask", "open_url"]
    label: str
    payload: ActionPayload


class ResponseMeta(BaseModel):
    intent: Intent
    tool: Optional[str] = None
    latency_ms: int = 0


ResponseType = Literal["text", "course_table", "cards", "assessment_form", "skill_radar", "error"]


class AgentResponse(BaseModel):
    conversation_id: str
    message_id: str
    message: str
    response_type: ResponseType
    data: Union[CourseTableData, CardsData, AssessmentFormData, SkillRadarData, ErrorData, None] = None
    sources: list[Source] = []
    actions: list[Action] = []
    meta: ResponseMeta


# ---------- Requests ----------
class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str = Field(min_length=1, max_length=1000)


class AssessmentAnswer(BaseModel):
    question_id: str
    value: int = Field(ge=0, le=4)


class AssessmentSubmit(BaseModel):
    conversation_id: str
    assessment_id: str
    answers: list[AssessmentAnswer]


class FeedbackRequest(BaseModel):
    message_id: str
    rating: Literal["up", "down"]
    reason: Optional[FeedbackReason] = None
    comment: Optional[str] = Field(default=None, max_length=500)


# ---------- History ----------
class ConversationSummary(BaseModel):
    id: str
    title: str
    updated_at: str


class ChatMessage(BaseModel):
    id: str
    role: Literal["user", "assistant"]
    content: Optional[str] = None           # role == "user"
    response: Optional[AgentResponse] = None  # role == "assistant"
    feedback: Optional[Literal["up", "down"]] = None
    created_at: str


class ConversationDetail(BaseModel):
    id: str
    title: str
    messages: list[ChatMessage]


# ---------- Internal tool contract (P3 <-> P4) ----------
class RetrievedChunk(BaseModel):
    text: str
    source: Source
```

---

## 4. Internal Interfaces (function ที่ต้อง export ให้ Agent เรียก)

> ให้ทุกคนสร้าง function signature + ค่าคืนแบบ mock ไว้ **ภายใน Day 1** เพื่อให้ P3 เรียกได้ก่อน แล้วค่อยเติมของจริง

```python
# ---- P2: backend/app/modules/user/services/  (import: from app.modules.user import ...) ----
# user_service.py
def get_user_context(db, user_id: str) -> UserContext        # UserContext = {user: User, skill: SkillProfile | None}
# history_service.py
def get_or_create_conversation(db, user_id: str, conversation_id: str | None, first_message: str) -> str  # -> conversation_id
def add_user_message(db, conversation_id: str, text: str) -> str
def add_assistant_message(db, conversation_id: str, response: AgentResponse) -> None  # ใช้ response.message_id เป็น PK
def get_recent_messages(db, conversation_id: str, limit: int = 6) -> list[dict]       # [{role, text}]
# skill_store.py
def save_skill_profile(db, user_id: str, scores: SkillScores, answers: list[AssessmentAnswer]) -> SkillProfile
def get_latest_skill(db, user_id: str) -> SkillProfile | None

# ---- P4: backend/app/modules/rag/service.py ----
def search_department_knowledge(query: str, top_k: int = 4) -> list[RetrievedChunk]  # เรียงจาก score มากไปน้อย, [] ถ้าไม่เจอ

# ---- P5: backend/app/modules/tools/curriculum/service.py ----
def get_courses(year: int, semester: int) -> CourseTableData | None
def get_course_detail(query: str) -> Course | None           # รับรหัสวิชาหรือชื่อ (fuzzy)
def get_total_credits(year: int | None = None, semester: int | None = None) -> int
def get_curriculum_overview() -> CardsData                   # การ์ดสรุปแต่ละชั้นปี

# ---- P5: backend/app/modules/tools/skill/service.py ----
def get_assessment() -> AssessmentFormData
def calculate_skill(answers: list[AssessmentAnswer]) -> SkillScores
def top_skills(scores: SkillScores, n: int = 2) -> list[str]

# ---- P7 (optional): backend/app/modules/intent_ml/predict.py ----
def predict_intent(text: str) -> tuple[str, float]           # (intent, confidence 0-1)

# ---- P3: backend/app/modules/agent/llm_client.py ----
def generate_text(system: str, prompt: str, *, temperature: float = 0.3) -> str
def generate_json(system: str, prompt: str) -> dict
```

---

## 5. Database (SQLite) — owner P2

```text
users            id PK, google_sub UNIQUE, email, name, picture_url,
                 display_name, age_range, user_type, study_year, onboarded, created_at
conversations    id PK, user_id FK, title, created_at, updated_at
messages         id PK, conversation_id FK, role ('user'|'assistant'),
                 content TEXT NULL, response_json TEXT NULL,
                 response_type, intent, latency_ms, created_at
skill_profiles   id PK, user_id FK, scores_json, answers_json, created_at   -- แถวล่าสุด = ปัจจุบัน
feedback         id PK, message_id FK, user_id FK, rating, reason, comment, created_at
                 UNIQUE(message_id, user_id)
```
- ID ทุกตัวเป็น `uuid4` string · เวลาเป็น ISO 8601 UTC
- `conversations.title` = 40 ตัวอักษรแรกของข้อความแรก
- สร้างตารางอัตโนมัติตอน startup (`SQLModel.metadata.create_all`) — ไม่ต้องทำ migration

---

## 6. Data Formats (`data/`)

### 6.1 Knowledge (P4) — `data/knowledge/*.md`
```markdown
---
doc_id: ce-overview
title: ภาพรวมภาควิชาวิศวกรรมคอมพิวเตอร์
source_url: https://...
updated: 2026-09-24
---
# ภาพรวมภาควิชา
## ประวัติ
...
## ห้องปฏิบัติการ
...
```
- 1 ไฟล์ = 1 หัวข้อใหญ่ · แบ่ง chunk ตาม `##` heading (ยาวเกิน ~800 ตัวอักษรค่อยตัดย่อย, overlap 100)
- `section` ใน Source = ชื่อ heading ของ chunk
- **ต้องมี `source_url` จริงทุกไฟล์** (ห้ามแต่งข้อมูลเอง)

### 6.2 Curriculum (P5) — `data/curriculum/curriculum.json`
```json
{
  "program": "วศ.บ. วิศวกรรมคอมพิวเตอร์",
  "curriculum_year": "25xx",
  "source_url": "https://...",
  "total_credits": 0,
  "courses": [
    {
      "code": "04-xxx-xxx",
      "name_th": "โครงสร้างข้อมูลและอัลกอริทึม",
      "name_en": "Data Structures and Algorithms",
      "credits": 3,
      "credit_detail": "3(2-3-5)",
      "category": "หมวดวิชาเฉพาะ",
      "description": "...",
      "year": 2,
      "semester": 1
    }
  ]
}
```

### 6.3 Assessment (P5) — `data/assessment/skill_v1.json`
```json
{
  "assessment_id": "skill_v1",
  "title": "ประเมินความถนัดสาย Computer Engineering",
  "scale": [
    {"value": 0, "label": "ไม่เคยเลย"}, {"value": 1, "label": "เคยได้ยิน"},
    {"value": 2, "label": "เคยลองทำ"}, {"value": 3, "label": "ทำได้"},
    {"value": 4, "label": "ทำได้ดี / สอนคนอื่นได้"}
  ],
  "questions": [
    {"id": "q1", "text": "สร้างหน้าเว็บด้วย HTML/CSS/JS หรือ React", "weights": {"frontend": 1.0}},
    {"id": "q2", "text": "เขียน REST API และต่อฐานข้อมูล", "weights": {"backend": 1.0, "frontend": 0.2}}
  ]
}
```
**สูตรคะแนน:** `score[skill] = round( Σ(value × weight) / Σ(4 × weight) × 100 )` เฉพาะข้อที่มี weight ของ skill นั้น
(`weights` ไม่ถูกส่งไป frontend — `get_assessment()` คืนแค่ `id`, `text`, `options`)

### 6.4 Eval set (P8) — `data/eval/questions.jsonl`
```json
{"id": "e001", "question": "ปี 2 เทอม 1 เรียนอะไรบ้าง", "intent": "curriculum", "expected_type": "course_table", "must_contain": ["โครงสร้างข้อมูล"]}
{"id": "e002", "question": "ภาคคอมเรียนเกี่ยวกับอะไร", "intent": "department_info", "expected_type": "text", "must_contain": []}
```
ใช้ทั้งทดสอบ Agent (P8) และเป็น training data ของ Local Intent Classifier (P7)

---


## 7. ตัวอย่าง Request / Response จริง (ใช้เป็น fixture อ้างอิง)

```bash
# Dev login
curl -s -X POST localhost:8000/api/auth/dev -H 'Content-Type: application/json'   -d '{"email":"tester@example.com","name":"Tester"}'

# ถามหลักสูตร
curl -s -X POST localhost:8000/api/chat -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json'   -d '{"conversation_id":null,"message":"ปี 2 เทอม 1 เรียนอะไรบ้าง"}'
```

```json
{
  "conversation_id": "5f0c...",
  "message_id": "a81e...",
  "message": "นี่คือรายวิชาของ **ปี 2 เทอม 1** รวม 21 หน่วยกิตครับ",
  "response_type": "course_table",
  "data": {
    "year": 2, "semester": 1, "total_credits": 21,
    "courses": [
      {"code": "04-xxx-xxx", "name_th": "โครงสร้างข้อมูลและอัลกอริทึม", "name_en": "Data Structures and Algorithms",
       "credits": 3, "credit_detail": "3(2-3-5)", "category": "หมวดวิชาเฉพาะ", "description": null, "year": 2, "semester": 1}
    ]
  },
  "sources": [],
  "actions": [{"type": "ask", "label": "ดูปี 2 เทอม 2", "payload": {"text": "ปี 2 เทอม 2 เรียนอะไรบ้าง"}}],
  "meta": {"intent": "curriculum", "tool": "curriculum.get_courses", "latency_ms": 1840}
}
```

> ข้อมูลรายวิชาในตัวอย่างเป็นตัวอย่างรูปแบบเท่านั้น — ของจริงต้องมาจาก `data/curriculum/curriculum.json`

## 8. ตาราง response_type → ใครผลิต → ใครแสดง

| `response_type` | Intent ที่ทำให้เกิด | ผู้ผลิต data | Component ที่แสดง (P6) |
|---|---|---|---|
| `text` | `department_info`, `general`, `clarify` | P3 (+ P4 sources) | `TextResponse` (+ `SourceViewer` ถ้ามี sources) |
| `course_table` | `curriculum` | P5 `get_courses` | `CourseTable` |
| `cards` | `course_detail`, ภาพรวมหลักสูตร | P5 `get_course_detail` / `get_curriculum_overview` | `InfoCards` |
| `assessment_form` | `skill_analysis` (ยังไม่มี profile) | P5 `get_assessment` | `AssessmentForm` |
| `skill_radar` | `skill_analysis` (มี profile), หลัง submit | P5 `calculate_skill` + P3 summary | `SkillRadar` |
| `error` | LLM ล่ม / tool error | P3 | `ErrorResponse` (ปุ่มลองใหม่) |

## 9. Contract acceptance checklist (Day 1 ก่อน 12:00)

- [ ] `contract.ts` และ `contract.py` ตรงกันทุก field/enum (P1 + P3 ตรวจคู่กัน)
- [ ] P6 สร้าง mock fixture ครบทุก `response_type` และ type-check ผ่านกับ `contract.ts`
- [ ] P2 ยืนยัน `User`, `ProfileUpdate`, `ConversationDetail`, `FeedbackRequest` พอสำหรับหน้าจอ
- [ ] P4 ยืนยัน `Source` / `RetrievedChunk` มี field ที่ต้องแสดงครบ
- [ ] P5 ยืนยัน `Course`, `AssessmentFormData`, `SkillScores` ตรงกับข้อมูลจริงในเล่มหลักสูตร
- [ ] P7 ยืนยันชื่อ `Intent` 6 ค่า (ใช้เป็น label ของ classifier)
- [ ] ทุกคนสร้าง stub function ตาม §4 ได้โดยไม่ต้องถามเพิ่ม
