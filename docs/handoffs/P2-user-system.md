# P2 User System — Completion Handoff

## สรุปงาน

P2 ดูแลวงจรผู้ใช้ครบตั้งแต่ Google/Dev Login, JWT, onboarding และ profile ไปจนถึงการเก็บ/เปิดประวัติ, skill profile และ feedback หน้า `/chat` ใช้ข้อมูลผู้ใช้จริง แสดง greeting และ profile control; logout ล้างทั้ง token/session และบทสนทนาในหน่วยความจำ

History ใช้ SQLite ผ่าน SQLModel ทุกห้องผูกกับ `user_id` และทุก endpoint ตรวจ JWT ผู้ใช้เปิดห้องเก่า ดูคำตอบแบบ structured เดิม และถามต่อใน `conversation_id` เดิมได้ Desktop ใช้ history panel และ mobile ใช้ overlay drawer

Stats ถูกตัดออกโดยตั้งใจ เพราะแผนและ contract ระบุว่าเป็น optional Monitoring scope

## Endpoint สุดท้าย

ทุก endpoint ยกเว้น auth และ health ต้องมี `Authorization: Bearer <JWT>`

| Method | Path | ผลลัพธ์ |
|---|---|---|
| POST | `/api/auth/google` | ตรวจ Google ID token, upsert user, คืน JWT |
| POST | `/api/auth/dev` | Dev Login เมื่อ backend `DEV_AUTH=true` |
| GET | `/api/users/me` | profile ของผู้ใช้ปัจจุบัน |
| PUT | `/api/users/me/profile` | บันทึก onboarding/profile |
| GET | `/api/conversations` | ห้องของผู้ใช้ เรียงอัปเดตล่าสุดก่อน |
| GET | `/api/conversations/{id}` | ข้อความเก่า→ใหม่ พร้อม structured response และ rating |
| GET | `/api/skills/me` | ผล skill ล่าสุด หรือ `404` |
| POST | `/api/feedback` | insert/update feedback ต่อคำตอบ |

`POST /api/chat` และ `POST /api/assessment/submit` เป็น endpoint ของ P3 แต่เรียก history/skill services ของ P2 เพื่อบันทึกข้อมูล

## ER / ความสัมพันธ์ข้อมูล

```text
users (1)
  ├──< conversations (1) ──< messages (1) ──< feedback
  ├──< skill_profiles
  └──< feedback

conversations.user_id    -> users.id
messages.conversation_id -> conversations.id
skill_profiles.user_id   -> users.id
feedback.message_id      -> messages.id
feedback.user_id         -> users.id
UNIQUE(feedback.message_id, feedback.user_id)
```

- `messages.role=user` เก็บ `content`
- `messages.role=assistant` เก็บ `response_json` ซึ่ง validate กลับด้วย `AgentResponse`
- `response_type`, `intent`, `latency_ms` เก็บแยกสำหรับค้น/วิเคราะห์
- skill profile เป็น append-only; แถวล่าสุดคือผลปัจจุบัน

## ตัวอย่าง curl

ตั้ง backend `DEV_AUTH=true` สำหรับตัวอย่างนี้

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/dev \
  -H 'Content-Type: application/json' \
  -d '{"email":"qa@example.com","name":"QA"}' \
  | python -c "import json,sys; print(json.load(sys.stdin)['access_token'])")

curl -s -X PUT http://localhost:8000/api/users/me/profile \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"display_name":"QA","age_range":"21_23","user_type":"current_student","study_year":2}'

curl -s http://localhost:8000/api/conversations \
  -H "Authorization: Bearer $TOKEN"

curl -s http://localhost:8000/api/conversations/CONVERSATION_ID \
  -H "Authorization: Bearer $TOKEN"

curl -s http://localhost:8000/api/skills/me \
  -H "Authorization: Bearer $TOKEN"

curl -s -X POST http://localhost:8000/api/feedback \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"message_id":"MESSAGE_ID","rating":"down","reason":"incomplete","comment":"ขอรายละเอียดเพิ่ม"}'
```

## Google OAuth setup

1. สร้าง OAuth 2.0 Client ID ประเภท Web application ใน Google Cloud Console
2. เพิ่ม Authorized JavaScript origin `http://localhost:3000`
3. ตั้ง client ID เดียวกันเป็น backend `GOOGLE_CLIENT_ID` และ frontend `NEXT_PUBLIC_GOOGLE_CLIENT_ID`
4. ตั้ง `JWT_SECRET` เป็นค่าจริงที่ไม่ใช่ `change-me`
5. restart web/api หลังเปลี่ยน environment

Google ส่ง ID token ให้ frontend แล้ว backend ตรวจ audience ด้วย `GOOGLE_CLIENT_ID` ก่อนออก JWT ของ COPIE ไม่มี Google client secret ใน repository

## Verification

ผลตรวจบน branch `user/complete-user-system`:

- backend P2 + Agent: `139 passed, 1 skipped`
- frontend ESLint: ผ่าน
- TypeScript `tsc --noEmit`: ผ่าน
- frontend production build: TypeScript/ESLint ผ่าน แต่ Turbopack ใน sandbox หยุดเพราะ process bind port ไม่ได้; webpack fallback ที่อนุญาต network แล้วพบปัญหาเดิม `ThemePreview.tsx` server/client boundary จากหน้า `/` ซึ่งเป็นไฟล์ P1 นอก scope
- `git diff --check`: ผ่าน
- `bash scripts/check-ai-watermark.sh --range origin/develop..HEAD`: ผ่าน

ต้องเดิน manual Demo 1, 4, 5 และ 6 บน Docker ที่ 1440 / 1024 / 390 px ก่อน merge โดยเฉพาะ Google Login จริง, mobile drawer, logout, การสลับบัญชี และ persisted feedback

## Known limitations

- JWT เก็บใน localStorage และไม่มี refresh token ตาม MVP non-goal
- ไม่มี conversation rename/delete หรือ pagination
- ไม่มี Stats endpoint; optional scope นี้ถูกตัดออกโดยตั้งใจ
- Dev Login แสดงเป็น fallback แต่ backend เป็นผู้ตัดสินด้วย `DEV_AUTH`; เมื่อปิดจะตอบ `404`
- P3 ยังมี `mock:` path ใน Agent router ซึ่งข้าม history persistence เป็น release caveat ที่ P3 เป็นเจ้าของ และไม่ได้แก้ใน PR นี้
- นโยบายกรณีบันทึก assistant history ล้มเหลวและ early assessment failure เป็นของ P3 และอยู่นอก scope
