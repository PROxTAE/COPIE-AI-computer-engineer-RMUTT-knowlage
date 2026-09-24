# P3 — AI Agent + Backend Lead

## Mission

สร้าง **สมองกลางของ COPIE**: FastAPI backend, `modules/agent/llm_client.py`, และ Agent ที่ (1) เข้าใจ intent (2) ตรวจว่าข้อมูลพอหรือยัง ถ้าไม่พอถามกลับ (3) เลือก Tool ที่ถูก (4) คืน `AgentResponse` ที่ตรง Contract เสมอ พร้อม multi-step flow ของ Skill Assessment และดูแล Docker/CI ของทั้งระบบ

**ความสำคัญ:** ทุกคำตอบผ่านจุดนี้ ถ้า Agent เลือก Tool ผิดหรือคืน JSON ผิด frontend จะแสดงผลไม่ได้และ Demo 2–4 ล้มทั้งหมด

## Ownership

แก้ได้โดยตรง
- `backend/app/main.py`, `backend/app/core/`, `backend/app/modules/agent/**` (รวม tests)
- `backend/requirements.txt`, `backend/Dockerfile`, `docker-compose.yml`, `.env.example`, `.github/workflows/ci.yml`

ต้องขอ review เพิ่ม
- 🔒 `backend/app/schemas/contract.py` — P1 approve ด้วย
- `modules/agent/prompts.py` ส่วน RAG — ให้ P4 review

Dependency

| รับจาก | อะไร | ภายใน |
|---|---|---|
| P2 | `get_user_context`, history functions, `skill_store` | stub D1 17:00 · จริง D3 AM |
| P4 | `search_department_knowledge` | stub D1 17:00 · จริง D2 PM |
| P5 | curriculum + skill functions | stub D1 17:00 · จริง D2–D3 |
| P7 | `predict_intent` (optional) | D3 PM |
| P8 | eval report สำหรับปรับ prompt | D4 |

ส่งให้: **P1/P6** `/api/chat` (mock ตั้งแต่ D1 AM), **P8** endpoint สำหรับ eval

## Stack

- FastAPI + Uvicorn, Pydantic v2, `python-dotenv`
- `google-genai` (Gemini) ผ่าน `modules/agent/llm_client.py` ไฟล์เดียว — เปลี่ยน provider ได้ที่นี่
- ไม่ใช้ LangChain/LangGraph — flow เป็น Python ธรรมดาเพื่อให้ debug ง่าย

## Target folder structure

```text
backend/app/
├─ main.py            # 👤 P3 — FastAPI(), include_router ของทุก module, startup: create_all + ensure_index
├─ core/config.py     # 👤 P3 — settings จาก .env
├─ schemas/contract.py# 🔒 P1 + P3
└─ modules/agent/     # 👤 P3
   ├─ __init__.py     # public: router
   ├─ router.py       # POST /api/chat, POST /api/assessment/submit
   ├─ orchestrator.py # handle_chat(), handle_assessment_submit()
   ├─ intent_router.py# route() → RouteResult
   ├─ rule_router.py  # regex fallback
   ├─ generator.py    # answer_from_rag(), explain_skill(), general_answer()
   ├─ prompts.py      # system prompts + few-shot
   ├─ llm_client.py   # generate_text, generate_json — จุดเดียวที่คุยกับ Gemini
   └─ tests/          # test_agent.py
```

## Design details

### RouteResult

```python
class RouteResult(BaseModel):
    intent: Intent                 # 6 ค่าตาม contract
    year: int | None = None
    semester: int | None = None
    course_query: str | None = None
    search_query: str | None = None   # คำถามที่เขียนใหม่ให้เหมาะกับ RAG
    source: Literal["ml", "llm", "rule"]
```

### Router prompt (ร่าง)

```text
คุณคือตัวจำแนกคำถามของ COPIE ผู้ช่วยภาควิชาวิศวกรรมคอมพิวเตอร์ RMUTT
ตอบเป็น JSON เท่านั้น: {"intent": ..., "year": int|null, "semester": int|null,
"course_query": str|null, "search_query": str|null}
intent:
- curriculum: ถามว่าปี/เทอมไหนเรียนวิชาอะไร หน่วยกิต แผนการเรียน
- course_detail: ถามรายละเอียดวิชาเจาะจง (รหัส/ชื่อวิชา)
- department_info: ข้อมูลภาค หลักสูตรภาพรวม การรับสมัคร แล็บ อาชีพ FAQ
- skill_analysis: วิเคราะห์/ประเมิน/ดู skill ของตัวเอง
- general: ทักทาย หรือคำถามทั่วไปที่เกี่ยวกับการเรียนคอมพิวเตอร์
- clarify: คำถามกำกวมจนเลือกไม่ได้
ข้อมูลผู้ใช้: {user_type}, ปี {study_year}
บทสนทนาล่าสุด: {recent}
+ few-shot 10 ตัวอย่าง (ไทยปนอังกฤษ, ภาษาพูด เช่น "เทอมหน้าเรียนไร")
```

### Orchestrator logic

```text
handle_chat(user, req):
  t0 = now
  ctx  = get_user_context(user.id)
  cid  = get_or_create_conversation(...); add_user_message(...)
  r    = route(req.message, ctx, get_recent_messages(cid))
  # Missing-info
  if r.intent == "curriculum":
      year = r.year or ctx.user.study_year
      if year is None or r.semester is None → ถามกลับ:
          response_type="text", intent="clarify",
          actions=[ask "ปี {y} เทอม {s}" ...]  (ถ้ารู้ year ให้เสนอแค่ 2 เทอมของปีนั้น)
  dispatch → build AgentResponse(message_id=uuid4, meta.latency_ms=now-t0)
  AgentResponse.model_validate(...)      # ห้ามคืนของผิด contract
  add_assistant_message(cid, resp); return resp
```

| intent | Tool | response_type | message |
|---|---|---|---|
| `department_info` | `search_department_knowledge(search_query)` → ถ้า `[]` ตอบว่า "ยังไม่พบข้อมูลนี้ในเอกสารของภาค" + action แนะนำคำถามอื่น | `text` + sources | LLM จาก context เท่านั้น อ้าง `[1]` |
| `curriculum` | `get_courses(year, semester)` → `None` = ไม่มีข้อมูลเทอมนั้น | `course_table` | template สั้นๆ (ไม่ต้องใช้ LLM) |
| `course_detail` | `get_course_detail(course_query)` → ไม่เจอ → fallback RAG | `cards` | template |
| `skill_analysis` | `get_latest_skill` → None → `get_assessment()` | `assessment_form` | "ยังไม่มีข้อมูล skill ของคุณ ลองตอบ 12 ข้อนี้ก่อนนะ" |
| `skill_analysis` (มีแล้ว) | skill ล่าสุด + `explain_skill` | `skill_radar` | LLM อธิบายจากคะแนน |
| `general` / `clarify` | `general_answer` | `text` | persona COPIE, ปฏิเสธนอกขอบเขตอย่างสุภาพ |

`handle_assessment_submit`: `calculate_skill` → `save_skill_profile` → `explain_skill` → `skill_radar` → บันทึก history

### Failure handling

| เหตุการณ์ | ทำอย่างไร |
|---|---|
| LLM router timeout/error/JSON พัง | ใช้ `rule_router` (`source="rule"`) |
| LLM generator ล่ม | RAG: แสดง snippet ของ chunk แรก + sources · general: `response_type="error"` code `llm_unavailable` |
| Tool exception | log + `response_type="error"` code `tool_failed` |
| ผลลัพธ์ไม่ผ่าน Pydantic | log + `error` code `unknown` (ห้ามส่ง 500 ให้ UI) |

## Implementation steps

### Phase 0 — Scaffold + mock (Day 1 AM)
1. FastAPI scaffold, `config.py`, `contract.py` ตาม `00_API_AND_DATA_CONTRACTS.md` §3.2, `/api/health`
2. `POST /api/chat` แบบ mock: keyword "ปี" → course_table fixture, "skill" → assessment_form, อื่นๆ → text

Exit: **M0** — frontend เรียก `/api/chat` ได้ทันที

### Phase 1 — LLM client + rule router + CI (Day 1 PM)
1. `generate_text`, `generate_json` (JSON mode, timeout, retry 1 ครั้ง, log latency)
2. `rule_router.py`: regex `ปี\s*([1-4])`, `เทอม\s*([12])`, รหัสวิชา, คำว่า skill/ถนัด/ประเมิน, fallback `department_info`
3. `ci.yml` (มีแล้วใน repo — ตรวจว่ารันผ่าน)

Exit: **M1**

### Phase 2 — Intent router + Orchestrator (Day 2)
1. AM: prompt + few-shot, `route()` พร้อม fallback, ทดสอบ 20 ประโยค
2. PM: `orchestrator.py` ครบตารางด้านบนโดยเรียก **stub** ของ P2/P4/P5, missing-info + action chips, `test_agent.py` 10 เคส

Exit: **M2** — ทุก intent คืน response_type ถูก (ข้อมูลยังเป็น stub)

### Phase 3 — Real tools + Skill flow (Day 3)
1. AM: สลับเป็น function จริง, `generator.py` (prompt RAG ร่วมกับ P4: ตอบจาก context เท่านั้น, อ้าง `[n]`, ภาษาไทยสุภาพ, ≤ 180 คำ)
2. PM: `/api/assessment/submit`, ใช้ user context + recent messages, บันทึก history ทุกคำตอบ

Exit: **M3** — Demo 2, 3, 4 ผ่านผ่าน API จริง

### Phase 4 — Docker + hardening (Day 4)
1. AM: `backend/Dockerfile`, `docker-compose.yml` (web + api, volume storage, ingest ตอน start), failure handling ตามตาราง
2. PM: ต่อ `predict_intent` (flag `USE_LOCAL_INTENT`), ปรับ prompt ตาม eval ของ P8

Exit: **M4** — `docker compose up --build` ผ่าน Demo 1–6

### Phase 5 — Tuning (Day 5)
- ปรับ prompt จากคำถามที่ตอบผิด, latency เฉลี่ย < 8 วินาที, แก้ P0/P1

## Required tests

| ประเภท | Cases |
|---|---|
| Router | 20 ประโยค/ภาษาพูด → intent ถูก ≥ 85%; rule_router จับ ปี/เทอม ถูก |
| Orchestrator | แต่ละ intent คืน response_type ถูก, curriculum ไม่มีปี → clarify, skill ไม่มี → form |
| Contract | ทุก response ผ่าน `AgentResponse.model_validate` |
| Failure | ปิด `GEMINI_API_KEY` → curriculum/skill ยังตอบได้, RAG/general ได้ `error` ที่อ่านเข้าใจ |
| API | `/api/chat` ไม่มี token → 401, conversation ของคนอื่น → 403 |

## Acceptance checklist

- [ ] ทุก response ตรง Contract (validate ก่อนส่ง)
- [ ] เลือก Tool ถูกตาม Demo 2–4 และถามกลับเมื่อข้อมูลไม่พอ
- [ ] รายวิชา/หน่วยกิต/คะแนน มาจาก Tool เท่านั้น
- [ ] RAG ตอบพร้อม sources และบอก "ไม่พบ" เมื่อไม่มีข้อมูล
- [ ] Skill flow: form → submit → radar → ถามซ้ำได้ radar ทันที
- [ ] LLM ล่มแล้วระบบไม่ crash
- [ ] `docker compose up --build` รันทั้งระบบได้

## Branch / PR breakdown

1. `agent/backend-scaffold` — FastAPI, contract.py, health, mock chat
2. `agent/llm-client` — LLM client, rule router, CI
3. `agent/intent-router` — LLM router + few-shot
4. `agent/orchestrator` — dispatch + missing-info (stubs)
5. `agent/real-tools` — tool จริง + generator
6. `agent/skill-flow` — assessment submit + context + history
7. `agent/docker` — Dockerfile, compose, failure handling
8. `agent/prompt-tuning` — local intent + ปรับ prompt

## Completion report requirements

สร้าง `docs/handoffs/P3-ai-agent.md` ระบุเพิ่ม: flow diagram ของ orchestrator, prompt ทั้งหมด (router/RAG/skill/general), ตาราง intent → tool → response_type, ผล eval ล่าสุด (intent accuracy, latency), ตาราง failure behavior, วิธีเปลี่ยน LLM provider
