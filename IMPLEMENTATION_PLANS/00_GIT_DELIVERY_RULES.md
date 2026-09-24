# 00 — Git, Docker and Delivery Rules

> กติกากลางบังคับสำหรับทั้ง 8 คน เป้าหมายคือ merge งานทุกวันโดยไม่มี branch ใหญ่ที่รวมยาก และทุกคนรันผลลัพธ์เดียวกันได้
> เปลี่ยนกติกาได้โดยเปิด PR แก้ไฟล์นี้ และได้ approve จาก P1 + P3

---

## 1. Repository bootstrap

Repo: https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage

โครงโปรเจกต์ (frontend + backend แยก module, contract, กติกา, แผนงาน) ถูก push ขึ้น `main` และ `develop` แล้ว — นี่เป็นการ push ตรงครั้งเดียวของโปรเจกต์ หลังจากนี้ทุกอย่างเข้าผ่าน PR

ทุกคนทำหลัง clone:

```bash
git clone https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage.git
cd COPIE-AI-computer-engineer-RMUTT-knowlage
git config core.hooksPath .githooks
git switch develop
```

### ตั้งค่า GitHub ก่อนให้ทีมเริ่ม (Settings → Branches → Branch protection)

| Branch | ตั้งค่า |
|---|---|
| `main` | Require PR · Require 1 approval · Require status checks (`ai-watermark`, `branch-name`, `frontend`, `backend`) · Block force push/deletion · รับ PR จาก `develop` หรือ `release/*` เท่านั้น |
| `develop` | Require PR · Require 1 approval (**Require review from Code Owners**) · Require status checks เหมือน main · Block force push/deletion · Require conversation resolution |

- Merge method: เปิด **Squash merge** อย่างเดียว · เปิด "Automatically delete head branches"
- เพิ่มสมาชิก 8 คนเป็น Collaborator (Write) · P1, P3 เป็น Maintain
- แก้ `.github/CODEOWNERS` ให้เป็น GitHub username จริง (PR `docs/codeowners`)

---

## 2. Roster (กรอกก่อนเริ่ม Day 1)

| ID | ชื่อ | GitHub | Module prefix | แผนงาน |
|---|---|---|---|---|
| P1 | | @ | `core`, `mascot` | `01_FRONTEND_CORE_3D_MASCOT.md` |
| P2 | | @ | `user` | `02_USER_SYSTEM.md` |
| P3 | | @ | `agent` | `03_AI_AGENT_BACKEND.md` |
| P4 | | @ | `rag` | `04_DEPARTMENT_RAG.md` |
| P5 | | @ | `tools` | `05_CURRICULUM_SKILL_TOOLS.md` |
| P6 | | @ | `renderer` | `06_DYNAMIC_RENDERER.md` |
| P7 | | @ | `suggest`, `intent-ml` | `07_SUGGESTIONS_LOCAL_INTENT_ML.md` |
| P8 | | @ | `export`, `qa` | `08_EXPORT_QA_EVAL.md` |

**ผู้กด merge:** P1 (frontend, `main`), P3 (backend) — คนอื่นเปิด PR และ approve ได้ แต่ไม่กด merge เอง

---

## 3. Branch strategy

```text
main          ← เวอร์ชัน Demo (Protected) — รับจาก develop / release/* เท่านั้น ที่ Milestone M4, M5
  └── develop ← Integration branch (Protected) — ทุกคน PR เข้าที่นี่
        ├── core/app-shell
        ├── mascot/copie-states
        ├── user/google-login-api
        ├── agent/intent-router
        ├── rag/hybrid-search
        ├── tools/curriculum-service
        ├── renderer/course-table
        ├── suggest/prompt-chips
        ├── intent-ml/tfidf-classifier
        ├── export/copy-button
        └── qa/eval-script
```

รูปแบบ: **`<module>/<feature>`**
- `<module>` ต้องเป็นของตัวเองตาม Roster
- `<feature>` เป็น kebab-case ภาษาอังกฤษ สั้น บอกสิ่งที่ทำ
- ห้ามใช้ชื่อคน, `dev`, `test`, `new`, `mybranch`, ภาษาไทย
- branch มีอายุ **ไม่เกิน 1 วัน** — ทำเป็น slice เล็กๆ แล้ว merge ทุกวัน

Branch พิเศษ

| Prefix | ใช้เมื่อ | ใครเปิด | Approve |
|---|---|---|---|
| `contract/` | แก้ `contract.ts` / `contract.py` / API | ทุกคน | **P1 และ P3** |
| `hotfix/` | แก้บั๊กบน develop ช่วง Day 4–5 | ทุกคน | 1 คนที่ไม่ใช่ตัวเอง |
| `docs/` | แก้เอกสาร / แผน | ทุกคน | 1 คน |
| `release/` | เตรียม develop → main | P1 | P3 |

`pre-push` hook และ CI จะปฏิเสธชื่อ branch ที่ไม่ตรงรูปแบบ

---

## 4. ขั้นตอนเริ่มงานทุกครั้ง

```bash
git switch develop
git pull --ff-only origin develop
git status                       # ต้องสะอาดก่อนเริ่ม
git switch -c rag/hybrid-search
```

- ครั้งแรกหลัง clone: `git config core.hooksPath .githooks` (macOS/Linux เพิ่ม `chmod +x .githooks/* scripts/*.sh`)
- ห้ามแตก branch จาก branch ของคนอื่น — ถ้าต้องใช้ของที่ยังไม่ merge ให้ใช้ stub/mock ตาม Contract แทน

---

## 5. Commit discipline

รูปแบบ: **`<type>(<module>): <สรุปสั้นๆ>`** บรรทัดแรกไม่เกิน 72 ตัวอักษร

| type | ใช้เมื่อ |
|---|---|
| `feat` | เพิ่มฟีเจอร์ |
| `fix` | แก้บั๊ก |
| `refactor` | ปรับโค้ด พฤติกรรมไม่เปลี่ยน |
| `style` | UI / CSS / format |
| `test` | เพิ่ม/แก้ test |
| `docs` | เอกสาร |
| `chore` | config, dependency, script |
| `data` | เพิ่ม/แก้ข้อมูลใน `data/` |

```text
feat(rag): add BM25 + vector hybrid search with RRF
fix(renderer): course table overflow on mobile
data(tools): add year 3 semester 2 courses
```

กติกา
- 1 commit = 1 เรื่องที่ย้อนกลับได้ · ห้าม message แบบ `update`, `fix`, `done`, `final`, `wip`
- ใช้ `git add <ไฟล์ที่ตั้งใจ>` แทน `git add .` เพื่อไม่ดูด `.env` / ไฟล์ AI tool / งานคนอื่นเข้าไป
- ก่อน commit ดู diff ทุกครั้ง:

```bash
git status --short
git diff
git add <exact-files>
git diff --cached
git commit -m "feat(rag): add BM25 index builder"
```

---

## 6. Contract change protocol

1. เปิด branch `contract/<change>` แก้ **ทั้ง** `frontend/src/types/contract.ts` และ `backend/app/schemas/contract.py` ใน PR เดียว + อัปเดต `00_API_AND_DATA_CONTRACTS.md` + mock ของ P6
2. ประกาศใน `#contract` ว่าเปลี่ยนอะไร กระทบใคร
3. ต้องได้ approve จาก **P1 และ P3**
4. หลัง Day 1 12:00 เปลี่ยนได้เฉพาะ **additive** (เพิ่ม field optional / เพิ่ม enum / เพิ่ม `response_type`) — ห้ามลบหรือเปลี่ยนชื่อ field

---

## 7. Sync, push and Pull Request

```bash
git fetch origin
git merge origin/develop                                   # แก้ conflict ที่เครื่องตัวเอง
bash scripts/check-ai-watermark.sh --range origin/develop..HEAD
git push -u origin rag/hybrid-search                       # แล้วเปิด PR เข้า develop
```

- Base = **`develop`** เสมอ (ยกเว้น `release/*` → `main`)
- Title = รูปแบบเดียวกับ commit message
- Body = `PR_TEMPLATE.md` (GitHub เติมให้อัตโนมัติจาก `.github/pull_request_template.md`)
- **PR ละ 1 เรื่อง ≤ ~400 บรรทัด** (ไม่นับ data / lock file)
- แนบหลักฐาน: screenshot/GIF (frontend) หรือ ผล `curl` / `pytest` (backend)
- งานยังไม่เสร็จแต่ถึง 17:00 → เปิดเป็น **Draft PR**
- Merge แบบ **Squash and merge** เท่านั้น แล้วลบ branch

---

## 8. Review and merge rules

- Reviewer ตอบภายใน **2 ชั่วโมง** ในเวลาทำงาน (ช้ากว่านั้น tag ในกลุ่มได้)
- Reviewer ต้อง **pull branch มารันจริง** อย่างน้อย 1 ครั้งสำหรับ PR ที่เปลี่ยนพฤติกรรม
- ห้าม approve PR ตัวเอง · ห้าม merge ถ้า CI แดง

| เจ้าของ PR | Reviewer หลัก | สำรอง |
|---|---|---|
| P1 | P6 | P3 |
| P2 (frontend) | P1 | P6 |
| P2 (backend) | P3 | P5 |
| P3 | P1 | P4 |
| P4 | P3 | P5 |
| P5 | P3 | P4 |
| P6 | P1 | P7 |
| P7 | P1 (UI) / P3 (ML) | P8 |
| P8 | P1 (UI) / P3 (script) | P7 |

---

## 9. AI tools และลายน้ำ AI

ใช้ AI ช่วยเขียนโค้ดได้ **แต่ผลงานที่ commit ต้องไม่มีร่องรอยของ AI tool** และคน commit ต้อง **อ่าน เข้าใจ และอธิบายโค้ดนั้นได้เอง** (อาจารย์ถามได้ทุกบรรทัด)

### 9.1 สิ่งที่ห้ามปรากฏ

| ที่ | ห้ามมี (ตัวอย่าง) |
|---|---|
| Commit message | `Co-Authored-By: Claude ...`, `Co-authored-by: Copilot`, `Generated with [Claude Code]`, `🤖 Generated with`, `Generated by ChatGPT/Cursor/Gemini`, `noreply@anthropic.com` |
| PR title / description | footer แบบเดียวกับด้านบน |
| Code / comment | `// Generated by AI`, `# Here's the updated code`, `// ... rest of code unchanged`, ข้อความคุยกับ AI หลงเหลือ |
| ไฟล์ / โฟลเดอร์ | `.claude/`, `CLAUDE.md`, `.cursor/`, `.cursorrules`, `.windsurf/`, `.windsurfrules`, `.aider*`, `.continue/`, `.codeium/`, `.copilot/`, `.github/copilot-instructions.md`, `AGENTS.md`, `.gemini/`, `GEMINI.md` |

### 9.2 บังคับใช้ 3 ชั้น

1. **`.gitignore`** มี AI folders ครบ — ถ้า `git status` ยังเห็น แปลว่าเคยถูก track → `git rm -r --cached <path>`
2. **Git hooks** (`.githooks/`)
   - `pre-commit` — กัน commit บน `main`/`develop` + สแกนชื่อไฟล์และบรรทัดที่เพิ่ม
   - `commit-msg` — สแกน commit message
   - `pre-push` — กัน push ตรงเข้า `main`/`develop` + ตรวจชื่อ branch
3. **CI** job `ai-watermark` ตรวจทุก commit, diff, PR title/description — เจอ = merge ไม่ได้

### 9.3 ตั้งค่าเครื่องมือของตัวเอง

- ปิด attribution/co-author ใน AI tool ที่ใช้ (เช่น Claude Code ตั้ง `includeCoAuthoredBy: false`)
- **ให้ AI เขียนโค้ดได้ แต่ commit / push / เปิด PR เอง** และอ่าน message ก่อนกดทุกครั้ง
- ห้ามใช้ `--no-verify` หลัง bootstrap
- พลาดไปแล้ว (ยังไม่ merge):
  ```bash
  git commit --amend              # แก้ commit ล่าสุด
  git rebase -i origin/develop    # แก้หลาย commit แล้ว git push --force-with-lease
  ```

---

## 10. Docker standard (แบบง่าย)

```text
docker-compose.yml       # P3 — 2 services: web (3000), api (8000)
frontend/Dockerfile      # P1 — node:22-alpine, npm ci, npm run build, node .next/standalone/server.js
backend/Dockerfile       # P3 — python:3.11-slim, pip install, uvicorn
```

```bash
docker compose up --build        # รันทั้งระบบ
docker compose logs -f api       # ดู log backend
docker compose down              # หยุด (ข้อมูลยังอยู่ใน volume)
docker compose down -v           # ล้างข้อมูลทั้งหมด (DB + Chroma)
```

- volume `./backend/storage` เก็บ `app.db` และ `chroma/` · `./data` mount แบบ read-only
- `api` รัน `python -m app.modules.rag.ingest` อัตโนมัติถ้ายังไม่มี index
- `API_URL=http://api:8000` ต้องส่งเป็น build arg ให้ `web`
- ใช้ Docker ตั้งแต่ **Day 4** — Day 1–3 รันแบบ dev ปกติเร็วกว่า

---

## 11. Checks ที่ต้องรันก่อน push

```bash
# frontend (ถ้าแก้ frontend)
cd frontend && npm run lint && npm run build

# backend (ถ้าแก้ backend)
cd backend && python -m pytest -q tests/<test ของตัวเอง>.py

# ทุกคน
bash scripts/check-ai-watermark.sh --range origin/develop..HEAD
```

## 12. CI pipeline (`.github/workflows/ci.yml` — P3)

| Job | ตรวจอะไร |
|---|---|
| `ai-watermark` | commit message, diff, ไฟล์ AI tool, PR title/body |
| `branch-name` | `<module>/<feature>` และ main รับจาก develop/release เท่านั้น |
| `frontend` | `npm ci`, `lint`, `build` |
| `backend` | `ruff` (syntax/undefined name), `compileall` |

---

## 13. Communication rules

| เวลา | กิจกรรม | ช่องทาง | ใคร |
|---|---|---|---|
| 09:00–09:15 | Daily Stand-up (Day 1 = Kickoff 09:00–11:00) | Voice call | ทุกคน |
| 13:00 | Midday Status 1 บรรทัด | `#status` | ทุกคน |
| **17:00** | **PR Cutoff** | GitHub | ทุกคน |
| 17:00–19:00 | Review & Merge | GitHub | P1, P3 + reviewer |
| 19:00 | Smoke test develop (Day 3–5) | `#status` | P8 |
| **21:00** | **Daily Report** | `#status` | ทุกคน |

```text
[P4] 🟢/🟡/🔴
✅ เสร็จ: chunk + embed ครบ 14 ไฟล์, PR #12
🔨 กำลังทำ: BM25 hybrid
⛔ ติด: - (หรือ "รอ field X จาก P3")
📌 พรุ่งนี้: RRF + test 20 queries
```

- 🟢 ตามแผน · 🟡 ช้า < ครึ่งวัน · 🔴 ช้า ≥ ครึ่งวันหรือ blocked
- ติดเกิน **1 ชั่วโมง** → `#blockers` + tag คนที่เกี่ยวข้องทันที
- 🔴 สองวันติด → P1 ตัด scope หรือส่ง P7/P8 ไปช่วย
- ช่องทาง: `#status`, `#blockers`, `#contract`, GitHub Issues (บั๊ก Day 4–5)

---

## 14. Bug severity และ Freeze

| Level | ความหมาย | ต้องแก้ภายใน |
|---|---|---|
| **P0** | Demo scenario ใดพัง / app crash | ทันที (ทิ้งงานอื่น) |
| **P1** | ใช้ได้แต่ผิด เช่น ตอบข้อมูลผิด, UI แตกบนจอหลัก | ภายในวันนั้น |
| **P2** | สวยงาม / edge case | ถ้ามีเวลา (หลัง Code Freeze ห้ามแก้) |

Issue label: `bug` + `P0/P1/P2` + `module:<name>` · เจ้าของ module รับ Issue ภายใน 30 นาที

| เวลา | Freeze |
|---|---|
| Day 1 12:00 | Contract Freeze |
| Day 4 18:00 | Feature Freeze — รับเฉพาะ `fix`, `style`, `data`, `docs` · merge develop → main เป็น `v0.9` |
| Day 5 15:00 | Code Freeze — รับเฉพาะ P0 ที่ P1 อนุมัติ |
| Day 5 16:00 | Release `v1.0` (develop → main + tag) |

## 15. Definition of Done ของ 1 PR

- [ ] ตรงตาม Contract · แก้เฉพาะโฟลเดอร์ของตัวเอง (หรือเจ้าของอนุญาตแล้ว)
- [ ] build / test ของตัวเองผ่าน · มีหลักฐานใน PR
- [ ] ไม่มี debug print ค้าง, ไม่มี secret, ไม่มีลายน้ำ AI
- [ ] merge `origin/develop` ล่าสุดแล้ว ไม่มี conflict

## 16. Handoff ก่อนจบงาน

ภายใน **Day 5 12:00** ทุกคนสร้าง `docs/handoffs/PX-<module>.md` จาก `10_WORK_COMPLETION_REPORT_TEMPLATE.md` แล้วเปิด PR `docs/handoff-px`
