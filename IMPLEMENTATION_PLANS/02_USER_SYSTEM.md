# P2 — User System: Auth · Onboarding · Profile · History · Feedback (Full-stack)

## Mission

ทำทุกอย่างที่เกี่ยวกับ "ผู้ใช้" ตั้งแต่ Login ด้วย Google → Onboarding → เก็บ Profile → เก็บประวัติบทสนทนา → เก็บผล Skill → เก็บ Feedback ทั้งฝั่ง backend (DB + API + service ให้ Agent เรียก) และฝั่ง frontend (หน้า login/onboarding, sidebar, ปุ่ม feedback)

**ความสำคัญ:** Agent ต้องใช้ User Context (ชั้นปี, skill) เพื่อตอบให้ตรงคน และ Demo 1, 5, 6 ขึ้นกับงานนี้ทั้งหมด ถ้า history ไม่ถูกบันทึก ระบบจะคุยต่อไม่ได้และไม่มีข้อมูลสำหรับ Monitoring

## Ownership

แก้ได้โดยตรง
- Backend: `backend/app/modules/user/**` (DB, auth, services, routers, tests)
- Frontend: `frontend/src/modules/user/**` และ routes `frontend/src/app/{login,onboarding}/`

ต้องขอ review เพิ่ม
- 🔒 contract (P1+P3), `backend/app/main.py` (P3 — ลงทะเบียน router), `requirements.txt` / `package.json`

Dependency

| รับจาก | อะไร | ระหว่างรอ |
|---|---|---|
| P3 | FastAPI scaffold, `contract.py`, `config.py` | สร้าง router แยกแล้วรอ include |
| P1 | `ui/` components, `modules/core/api.ts`, `chatStore.loadConversation` | Tailwind ธรรมดา |
| P5 | `SkillScores` จาก `calculate_skill` (ผ่าน P3) | ใช้ค่าทดสอบ |

ส่งให้: **P3** (`get_user_context`, history/skill functions — ต้องมี stub ภายใน Day 1 17:00), **P1** (AuthGuard, sidebar, feedback), **P8** (Dev login สำหรับ eval script)

## Stack

- Backend: FastAPI, SQLModel (SQLite), `pyjwt`, `google-auth` (verify id_token)
- Frontend: `@react-oauth/google`, zustand, `ui/` ของ P1

## Target folder structure

```text
backend/app/modules/user/          # 👤 P2
├─ __init__.py        # public: router, get_current_user, get_session, get_user_context,
│                     #         history functions, save_skill_profile, get_latest_skill
├─ database.py        # engine, get_session(), create_all() ตอน startup
├─ models.py          # User, Conversation, Message, SkillProfileRow, Feedback
├─ auth/
│  ├─ google.py       # verify_google_id_token(token) -> {sub, email, name, picture}
│  ├─ jwt.py          # create_access_token(user_id), decode
│  └─ deps.py         # get_current_user (Depends)
├─ services/
│  ├─ user_service.py # get_user_context, upsert_google_user, update_profile
│  ├─ history_service.py
│  └─ skill_store.py
├─ routers/           # auth.py users.py history.py feedback.py skills.py stats.py → รวมเป็น router เดียวใน __init__
└─ tests/             # test_user_api.py, test_services.py

frontend/src/modules/user/         # 👤 P2
├─ index.ts           # public: LoginPage, OnboardingPage, AuthGuard, HistorySidebar, FeedbackBar,
│                     #         useUserStore, getToken, clearToken
├─ auth/              # GoogleSignInButton, DevLoginButton, AuthGuard, LoginPage, token.ts (localStorage)
├─ onboarding/        # OnboardingForm, OnboardingPage
├─ history/           # HistorySidebar, ConversationItem
├─ feedback/          # FeedbackBar, ReasonDialog
└─ userStore.ts       # user, loading, loadMe(), logout()

frontend/src/app/login/page.tsx        # export { LoginPage as default } from "@/modules/user";
frontend/src/app/onboarding/page.tsx   # export { OnboardingPage as default } from "@/modules/user";
```

## Design details

### Auth flow

```text
GoogleSignInButton → credential (id_token)
  → POST /api/auth/google {id_token}
  → verify_oauth2_token(id_token, requests.Request(), GOOGLE_CLIENT_ID)
  → upsert users (google_sub) → JWT {sub: user_id, exp: +7 วัน} (HS256, JWT_SECRET)
  ← AuthResponse → setToken → user.onboarded ? /chat : /onboarding
```

- `POST /api/auth/dev` ทำงานเฉพาะ `DEV_AUTH=true` (ไม่งั้นคืน 404) — สร้าง user จาก email ที่ส่งมา
- `AuthGuard` ครอบ `/chat` และ `/onboarding`: ไม่มี token → `/login`; ยังไม่ onboard → `/onboarding`

### Onboarding form

| Field | UI | Validation |
|---|---|---|
| `display_name` | text (default = ชื่อจาก Google) | 1–50 ตัวอักษร |
| `age_range` | radio 4 ตัวเลือก | required |
| `user_type` | radio: สนใจเข้าศึกษา / นักศึกษาปัจจุบัน / ใกล้จบ | required |
| `study_year` | select ปี 1–4 — **แสดงเฉพาะ** `current_student`/`near_graduate` | ถ้าแสดงต้องเลือก |

### History service (P3 เรียก)

```python
get_or_create_conversation(db, user_id, conversation_id, first_message) -> str
    # conversation_id=None → สร้างใหม่ title=first_message[:40]
    # มี id แต่ไม่ใช่ของ user → raise HTTPException(403)
add_user_message(db, conversation_id, text) -> str
add_assistant_message(db, conversation_id, response: AgentResponse) -> None
    # เก็บ response.model_dump_json() ใน response_json, response_type, intent, latency_ms
    # อัปเดต conversations.updated_at
get_recent_messages(db, conversation_id, limit=6) -> list[dict]   # [{"role","text"}] เก่า→ใหม่
```

`GET /api/conversations/{id}` แปลง row → `ChatMessage` (assistant ใช้ `AgentResponse.model_validate_json`) และใส่ `feedback` ของ user คนนั้น

### Feedback

- 👍 ส่งทันที · 👎 เปิด `ReasonDialog` (5 เหตุผล + comment optional) แล้วส่ง
- upsert ตาม `(message_id, user_id)` — กดเปลี่ยนใจได้
- ปุ่มแสดงสถานะที่เลือกแล้ว (โหลดจาก history ด้วย)

### Stats (optional, Monitoring)

`GET /api/stats` นับจาก `users`, `messages` (group by intent, avg latency), `feedback` — ใช้โชว์ในรายงาน/สไลด์

## Implementation steps

### Phase 0 — Contract review (Day 1 AM)
1. ตรวจ `User`, `ProfileUpdate`, `ChatMessage`, `FeedbackRequest` ใน contract
2. ขอ Google OAuth Client ID (Web) — Authorized JavaScript origins: `http://localhost:3000`

### Phase 1 — DB + Dev auth + stubs (Day 1 PM)
1. `models.py` 5 ตาราง ตาม `00_API_AND_DATA_CONTRACTS.md` §5, `database.py`
2. `jwt.py`, `deps.get_current_user`, `POST /api/auth/dev`, `GET /api/users/me`
3. **stub** ของ `services/*` ครบทุก signature (คืนค่า mock ที่ถูก type) ให้ P3 เรียกได้

Exit: **M1** — ได้ token จาก dev login และเรียก `/api/users/me` ได้

### Phase 2 — Google login + Profile (Day 2)
1. AM: `POST /api/auth/google`, `PUT /api/users/me/profile`
2. PM: `/login` (Google + Dev button), `modules/user/auth/token.ts`, `userStore`, `AuthGuard`, `/onboarding`

Exit: **M2** — login ด้วย Google จริง → onboarding → เข้า `/chat` ได้, refresh แล้วยัง login

### Phase 3 — History + Skill store (Day 3)
1. AM: history_service/skill_store ของจริง, `GET /api/conversations`, `/{id}`, `GET /api/skills/me`
2. PM: `HistorySidebar` (list ใหม่→เก่า, คลิกโหลด → `chatStore.loadConversation`, ปุ่ม New chat, mobile drawer)

Exit: **M3** — คุยแล้วปิดหน้า เปิดใหม่เห็นบทสนทนาเดิมและคุยต่อได้

### Phase 4 — Feedback + Stats (Day 4)
1. AM: `POST /api/feedback` + `FeedbackBar` + `ReasonDialog`
2. PM: `GET /api/stats` (optional), เดิน Demo 1, 5, 6, แก้บั๊ก

Exit: **M4**

### Phase 5 — Bug fix (Day 5)
- แก้ Issue P0/P1, ตรวจทุกกรณี redirect, ตรวจว่า user A ไม่เห็นข้อมูล user B

## Required tests

| ประเภท | Cases |
|---|---|
| API (`pytest` + `TestClient`) | dev login, `/users/me` ไม่มี token → 401, update profile → onboarded=true |
| Service | get_or_create ใหม่/เดิม/ของคนอื่น → 403, recent messages เรียงถูก, save/get skill ล่าสุด |
| Feedback | ส่งซ้ำ = update ไม่ใช่ insert ซ้ำ |
| Manual | Google login จริง, onboarding ซ่อน/แสดงชั้นปี, sidebar โหลดบทสนทนาเก่า |

## Acceptance checklist

- [ ] Google login จริงทำงาน + Dev login ทำงานเฉพาะ `DEV_AUTH=true`
- [ ] ผู้ใช้ใหม่ → onboarding, ผู้ใช้เดิม → `/chat`
- [ ] Profile ถูกใช้ใน Agent (P3 ยืนยันว่าเห็น `study_year`)
- [ ] ทุกข้อความถูกบันทึกพร้อม intent/latency, เปิด history แล้วคุยต่อได้
- [ ] Skill ล่าสุดถูกดึงได้, Feedback 👍/👎 + เหตุผลถูกบันทึก
- [ ] ผู้ใช้เห็นเฉพาะข้อมูลของตัวเอง
- [ ] ไม่มี Client ID/Secret จริงใน repo

## Branch / PR breakdown

1. `user/db-and-dev-auth` — models, jwt, dev login, stubs
2. `user/google-login-api` — google verify, profile API
3. `user/login-onboarding-ui` — หน้า login/onboarding, AuthGuard, userStore
4. `user/history-service` — history/skill services + APIs
5. `user/history-sidebar` — sidebar UI
6. `user/feedback` — feedback API + UI
7. `user/stats` — stats endpoint (optional)

## Completion report requirements

สร้าง `docs/handoffs/P2-user-system.md` ระบุเพิ่ม: ER diagram 5 ตาราง, ตาราง endpoint + ตัวอย่าง curl, วิธีตั้ง Google OAuth Client, ตัวอย่างผล `/api/stats`, ข้อจำกัด (token ใน localStorage, ไม่มี refresh token)
