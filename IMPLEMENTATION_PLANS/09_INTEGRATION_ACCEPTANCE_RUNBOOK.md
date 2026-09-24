# 09 — Integration and Acceptance Runbook

> ใช้เมื่อรวมงานบน `develop` (Day 3 เย็น – Day 5), ก่อน merge เข้า `main` และก่อน Demo
> ผู้รัน: **P8** (QA) + **P1** (Integration lead) · ทุกคนต้องอยู่ในช่องทางติดต่อระหว่างรัน

## 1. Entry criteria

- PR ของ module ที่จะทดสอบ merge เข้า `develop` แล้ว และ CI เขียว
- `.env` มีค่าจริงครบ: `GEMINI_API_KEY`, `GOOGLE_CLIENT_ID`, `NEXT_PUBLIC_GOOGLE_CLIENT_ID`, `JWT_SECRET`
- `data/knowledge/` ≥ 12 ไฟล์, `data/curriculum/curriculum.json` ผ่าน `validate`
- ไม่มี mock ใน flow `/chat` (ตรวจใน §3)

## 2. บันทึกข้อมูลการทดสอบ

สร้าง `docs/acceptance/YYYY-MM-DD-<รอบ>.md`

```text
วันที่/เวลา:
ผู้ทดสอบ:
Git SHA (git log -1 --oneline):
รันแบบ: dev / docker
เบราว์เซอร์/เครื่อง:
LLM model ที่ใช้:
USE_LOCAL_INTENT:
```

ห้ามใส่ API key, JWT เต็ม หรือข้อมูลส่วนตัวในไฟล์นี้

## 3. Static preflight

```bash
git switch develop && git pull --ff-only
git status --short                       # ต้องว่าง
bash scripts/check-ai-watermark.sh --range origin/main..origin/develop

# ไม่มี secret ใน repo
git grep -nE "AIza[0-9A-Za-z_-]{20,}|GOCSPX-|sk-[A-Za-z0-9]{20,}" -- . ':!*.lock' || echo "no secrets"

# ไม่มี mock ใน flow จริง (MOCKS ต้องถูกใช้เฉพาะใน renderer module / DevPlayground)
git grep -n "MOCKS" -- frontend/src ':!frontend/src/modules/renderer'

# ข้อมูลหลักสูตรถูกต้อง
cd backend && python -m app.modules.tools.curriculum.validate && cd ..
```

## 4. Build and start

### แบบ Docker (ใช้สำหรับ M4, M5 และ Demo)

```bash
docker compose down -v
docker compose up --build -d
docker compose ps                        # web, api = running
docker compose logs api | tail -n 30     # ต้องเห็น ingest สำเร็จ + Uvicorn running
```

### Smoke test

```bash
curl -s localhost:8000/api/health                                     # {"status":"ok"}
TOKEN=$(curl -s -X POST localhost:8000/api/auth/dev -H 'Content-Type: application/json' \
  -d '{"email":"qa@example.com","name":"QA"}' | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl -s -X PUT localhost:8000/api/users/me/profile -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"display_name":"QA","age_range":"21_23","user_type":"current_student","study_year":2}'
curl -s -X POST localhost:8000/api/chat -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"conversation_id":null,"message":"ปี 2 เทอม 1 เรียนอะไรบ้าง"}' | python -m json.tool | head -n 20
```

เปิด http://localhost:3000 → ต้องเห็นหน้า login ไม่มี error ใน DevTools Console

## 5. Demo scenarios (ต้องผ่านครบทั้ง 6)

### Demo 1 — Login + Onboarding (P2, P1)

1. เปิดเว็บด้วย browser โหมด incognito → กด Continue with Google → login ด้วยบัญชีจริง
2. เข้า `/onboarding` → กรอกชื่อ, อายุ, "นักศึกษาปัจจุบัน", ปี 2 → บันทึก
3. เข้า `/chat` เห็น COPIE ทักด้วยชื่อที่กรอก
4. refresh → ยังอยู่ `/chat` · logout → login ใหม่ → ไม่ต้อง onboarding ซ้ำ

Expected: ผู้ใช้ใหม่ไป onboarding, ผู้ใช้เดิมไป chat, COPIE `idle` ขยับ

### Demo 2 — Department RAG (P4, P3, P6)

1. ถาม "ภาควิชาวิศวกรรมคอมพิวเตอร์เรียนเกี่ยวกับอะไร"
2. สังเกต COPIE `thinking` → `responding`
3. กด source chip → เห็น snippet → เปิดลิงก์ต้นทางได้

Expected: `response_type=text`, มี `[n]` และ sources ≥ 1, เนื้อหาตรงกับเว็บต้นทาง
Negative: ถาม "ภาคไฟฟ้าเรียนอะไร" → บอกว่าไม่พบข้อมูลในเอกสารของภาค (ไม่แต่ง)

### Demo 3 — Curriculum table (P5, P3, P6)

1. ถาม "ปี 2 เทอม 1 เรียนอะไรบ้าง" → ตาราง
2. เปิดเล่มหลักสูตร → สุ่มเทียบ 3 วิชา + หน่วยกิตรวม
3. ถาม "เทอมหน้าเรียนอะไร" (ไม่ระบุปี) → ระบบใช้ปีจาก profile หรือถามกลับพร้อมปุ่ม
4. กด action chip "ดูปี 2 เทอม 2" → ได้ตารางใหม่

Expected: ข้อมูลตรงเล่ม 100%, `meta.tool = curriculum.get_courses`

### Demo 4 — Skill Agent flow (P5, P3, P6, P2)

1. ใช้ user ที่ยังไม่เคยประเมิน → ถาม "ช่วยวิเคราะห์ skill ของผม"
2. ได้ฟอร์ม 12 ข้อ → ตอบครบ → ดูผล
3. ได้ Radar 6 ด้าน + สรุป, COPIE `success`
4. ถามซ้ำ "skill ผมเป็นยังไง" → ได้ radar ทันทีไม่ต้องทำฟอร์ม

Expected: คะแนนเท่ากับที่คำนวณมือจากสูตร (P5 เตรียมชุดคำตอบตัวอย่าง), บันทึกใน DB

### Demo 5 — History (P2)

1. สร้าง 2 บทสนทนา → กด New chat → เปิดบทสนทนาเก่าจาก sidebar
2. ถามต่อในบทสนทนาเก่า → ข้อความต่อท้ายถูกที่
3. login ด้วยอีกบัญชี → ไม่เห็นบทสนทนาของบัญชีแรก

### Demo 6 — Feedback (P2)

1. กด 👍 บนคำตอบหนึ่ง, 👎 + เลือก "ข้อมูลไม่ครบ" บนอีกคำตอบ
2. เปิดบทสนทนาใหม่แล้วกลับมา → สถานะปุ่มยังอยู่
3. (optional) `GET /api/stats` เห็นจำนวน feedback เพิ่ม

## 6. Optional features

| Feature | ตรวจ |
|---|---|
| Suggested prompts (P7) | เปลี่ยนตาม user_type/ปี, กดแล้วได้คำตอบจริง |
| Copy / Export (P8) | copy ตาราง/radar ได้ข้อความอ่านรู้เรื่อง, TXT/JSON ดาวน์โหลดได้ |
| Local intent (P7) | `USE_LOCAL_INTENT=true` แล้ว Demo 2–4 ยังผ่าน |

## 7. Failure scenarios

| สถานการณ์ | วิธีจำลอง | Expected |
|---|---|---|
| LLM ใช้ไม่ได้ | ใส่ `GEMINI_API_KEY` ผิด แล้ว restart api | curriculum/skill ยังตอบได้ (rule router), RAG/general ได้ error ที่อ่านเข้าใจ + ปุ่มลองใหม่ ไม่มีหน้าขาว |
| token หมดอายุ | ลบ token ใน localStorage | กลับหน้า login |
| backend ปิด | `docker compose stop api` | toast แจ้ง, COPIE กลับ idle, ไม่ค้าง thinking |
| คำถามยาว/แปลก | วางข้อความ 1000 ตัวอักษร, emoji ล้วน | ไม่ crash |
| WebGL ใช้ไม่ได้ | ปิด hardware acceleration | เห็น COPIE fallback 2D |

## 8. UI check

- [ ] 1440 / 1024 / 390 px ไม่มี scroll แนวนอนของทั้งหน้า
- [ ] ข้อความไทยไม่ตกขอบ, ฟอนต์ไทยโหลดถูก
- [ ] Tab ไปได้ทุกปุ่ม, focus มองเห็น
- [ ] COPIE ครบ 5 state

## 9. Evaluation

```bash
python scripts/eval/run_eval.py --base http://localhost:8000
```

เป้าหมาย: intent accuracy ≥ 85%, response_type ≥ 90%, must_contain ≥ 80%, latency เฉลี่ย < 8 วินาที

## 10. Release sign-off (Day 5 16:00)

| รายการ | ผู้เซ็น | ✅ |
|---|---|---|
| Demo 1–6 ผ่านบน `main` ด้วย docker จาก clone ใหม่ | P8 | |
| Eval ผ่านเป้า (แนบ `EVAL_REPORT.md`) | P3 | |
| ข้อมูลหลักสูตร/ภาคตรวจแล้ว | P4, P5 | |
| ไม่มี secret / ลายน้ำ AI / mock ใน flow จริง | P1 | |
| Handoff report ครบ 8 คน | P1 | |
| Tag `v1.0` | P1 | |

```bash
git switch main && git pull --ff-only
git tag -a v1.0 -m "COPIE mini project release"
git push origin v1.0
```
