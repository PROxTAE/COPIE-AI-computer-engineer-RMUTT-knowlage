# COPIE — AI Assistant ภาควิชาวิศวกรรมคอมพิวเตอร์ RMUTT

Mini Project ทีม 8 คน (5 วัน) — ระบบ AI Assistant สำหรับภาควิชาวิศวกรรมคอมพิวเตอร์ มหาวิทยาลัยเทคโนโลยีราชมงคลธัญบุรี (RMUTT) ให้ข้อมูลเกี่ยวกับภาควิชา หลักสูตร รายวิชา และวิเคราะห์ทักษะของผู้ใช้ ผ่านมาสคอต 3D ชื่อ **COPIE** และ Dynamic UI แทน chatbot ธรรมดา

> 📘 แผนงานทั้งหมดอยู่ใน [`IMPLEMENTATION_PLANS/`](IMPLEMENTATION_PLANS/README.md) — เริ่มอ่านที่ README ของโฟลเดอร์นั้น

---

## ระบบเดียว แบ่งโฟลเดอร์ตาม module

COPIE เป็น **เว็บเดียว**: frontend Next.js 1 แอป + backend FastAPI 1 แอป ทำงานร่วมกันผ่าน `/api/*`
โค้ดในแต่ละแอปแบ่งเป็น **module ตามผู้รับผิดชอบ** เพื่อให้รู้ว่าใครดูแลส่วนไหน — ไม่ได้แยกเป็น service คนละตัว

| Module | เจ้าของ | Frontend | Backend | Data | แผนงาน |
|---|---|---|---|---|---|
| **core** | P1 | `frontend/src/modules/core/` | — | — | [01](IMPLEMENTATION_PLANS/01_FRONTEND_CORE_3D_MASCOT.md) |
| **mascot** | P1 | `frontend/src/modules/mascot/` | — | — | [01](IMPLEMENTATION_PLANS/01_FRONTEND_CORE_3D_MASCOT.md) |
| **user** | P2 | `frontend/src/modules/user/` | `backend/app/modules/user/` | — | [02](IMPLEMENTATION_PLANS/02_USER_SYSTEM.md) |
| **agent** | P3 | — | `backend/app/modules/agent/` + `app/main.py`, `app/core/` | — | [03](IMPLEMENTATION_PLANS/03_AI_AGENT_BACKEND.md) |
| **rag** | P4 | — | `backend/app/modules/rag/` | `data/knowledge/` | [04](IMPLEMENTATION_PLANS/04_DEPARTMENT_RAG.md) |
| **tools** | P5 | — | `backend/app/modules/tools/` | `data/curriculum/`, `data/assessment/` | [05](IMPLEMENTATION_PLANS/05_CURRICULUM_SKILL_TOOLS.md) |
| **renderer** | P6 | `frontend/src/modules/renderer/` | — | — | [06](IMPLEMENTATION_PLANS/06_DYNAMIC_RENDERER.md) |
| **suggest** / **intent-ml** | P7 | `frontend/src/modules/suggest/` | `backend/app/modules/intent_ml/` | — | [07](IMPLEMENTATION_PLANS/07_SUGGESTIONS_LOCAL_INTENT_ML.md) |
| **export** / **qa** | P8 | `frontend/src/modules/export/` | — | `data/eval/`, `scripts/eval/` | [08](IMPLEMENTATION_PLANS/08_EXPORT_QA_EVAL.md) |

ชื่อ module = **ชื่อ branch prefix** เช่น P4 ทำงานบน `rag/hybrid-search` และแก้ไฟล์ใน `backend/app/modules/rag/` + `data/knowledge/`

### ส่วนกลาง (shared)

| Path | เจ้าของ | หมายเหตุ |
|---|---|---|
| `frontend/src/types/contract.ts` | 🔒 P1 + P3 | Type กลางของ API — แก้ผ่าน `contract/*` PR เท่านั้น |
| `backend/app/schemas/contract.py` | 🔒 P1 + P3 | ต้องตรงกับ `contract.ts` เสมอ |
| `frontend/src/app/` | ตาม route | route เป็นแค่ประตู — logic อยู่ใน module |
| `frontend/package.json`, `backend/requirements.txt` | P1 / P3 approve | เพิ่ม library ใน PR ของตัวเองได้ |
| `.github/`, `.githooks/`, `scripts/check-ai-watermark.sh` | P1 | กติกา repo |

---

## โครงสร้างโปรเจกต์

```text
COPIE/
├─ frontend/                      # Next.js 16 · React 19 · Tailwind v4 — แอปเดียว
│  └─ src/
│     ├─ app/                     # routes: / · /chat · /login · /onboarding · /dev
│     ├─ modules/
│     │  ├─ core/        P1       # design system, workspace, api client, chat store
│     │  ├─ mascot/      P1       # 3D COPIE
│     │  ├─ user/        P2       # login, onboarding, history, feedback
│     │  ├─ renderer/    P6       # dynamic response UI + mock + /dev
│     │  ├─ suggest/     P7       # suggested questions
│     │  └─ export/      P8       # copy / export
│     └─ types/contract.ts  🔒
│
├─ backend/                       # FastAPI — แอปเดียว process เดียว
│  └─ app/
│     ├─ main.py, core/  P3       # entry point + config
│     ├─ schemas/contract.py  🔒
│     └─ modules/
│        ├─ user/        P2       # DB, auth, history, skill store, feedback
│        ├─ agent/       P3       # intent router, orchestrator, LLM, /api/chat
│        ├─ rag/         P4       # knowledge retrieval
│        ├─ tools/       P5       # curriculum + skill assessment
│        └─ intent_ml/   P7       # local intent classifier
│
├─ data/                          # ข้อมูลจริงของภาค
│  ├─ knowledge/         P4
│  ├─ curriculum/        P5
│  ├─ assessment/        P5
│  └─ eval/              P8
├─ scripts/
│  ├─ check-ai-watermark.sh  P1
│  └─ eval/              P8
├─ docs/                          # handoffs, acceptance, eval report
├─ IMPLEMENTATION_PLANS/          # แผนงานของทีม
├─ assets/mascot/     P1          # concept design ของ COPIE
└─ resource/                      # เอกสารโจทย์ต้นทาง
```

แต่ละ module มี `README.md` บอกหน้าที่ ไฟล์ที่จะสร้าง และ public API

## Module boundary (ทำให้เป็นระบบเดียวกันโดยไม่ชนกัน)

- **Frontend:** import ข้าม module ผ่าน index เท่านั้น — `import { ResponseRenderer } from "@/modules/renderer"` · ESLint บล็อก `@/modules/renderer/components/...`
- **Backend:** เรียกข้าม module ผ่าน `__init__.py` — `from app.modules.rag import search_department_knowledge`
- ข้อมูลที่ส่งข้ามกันใช้ type จาก contract เท่านั้น
- ตาราง DB เป็นของ `user` — module อื่นใช้ผ่าน function ของ `user`

---

## เริ่มต้นใช้งาน

```bash
git clone https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage.git
cd COPIE-AI-computer-engineer-RMUTT-knowlage
git config core.hooksPath .githooks          # ครั้งเดียวหลัง clone (บังคับ)
cp .env.example .env                          # แล้วใส่ค่าจริง (ห้าม commit .env)
git switch develop
```

**Backend** (Python 3.11)
```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate                 # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000      # http://localhost:8000/api/health
```

**Frontend** (Node.js 22)
```bash
cd frontend
npm ci
npm run dev                                    # http://localhost:3000
```

## กติกาทีม (สรุป)

1. ห้าม push ตรงเข้า `main` / `develop` — แตก branch `<module>/<feature>` จาก `develop` แล้วเปิด PR
2. แก้เฉพาะโฟลเดอร์ของ module ตัวเอง
3. ห้ามมีลายน้ำ AI ใน commit / PR / code และห้าม commit ไฟล์ของ AI tool (hook + CI ตรวจ)
4. PR Cutoff 17:00 ทุกวัน · Daily Report 21:00

รายละเอียด: [`IMPLEMENTATION_PLANS/00_GIT_DELIVERY_RULES.md`](IMPLEMENTATION_PLANS/00_GIT_DELIVERY_RULES.md) · Timeline: [`IMPLEMENTATION_PLANS/00_TIMELINE_AND_SYNC.md`](IMPLEMENTATION_PLANS/00_TIMELINE_AND_SYNC.md)
