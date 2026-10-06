# COPIE — Team Implementation Pack

ชุดเอกสารนี้แปลง `resource/RMUTT_CE_AI_Project_Summary_COPIE.md` และ diagram ของอาจารย์ให้เป็นแผนลงมือทำสำหรับทีม 8 คน ภายใน **5 วัน** (สร้าง Day 1–3, รวมระบบ Day 4, แก้บั๊ก + Demo Day 5)

เป้าหมาย: **ระบบทำงานได้จริง ตอบข้อมูลจริงของภาคได้ถูกต้อง หน้าตาสวย มี 3D COPIE** — ไม่ต้องถึงระดับ production

## กติกาสำคัญที่สุด

1. **ห้าม push ตรงเข้า `main` และ `develop`** — ทุกอย่างเข้าผ่าน Pull Request ไปที่ `develop` และต้องมี reviewer อย่างน้อย 1 คน
2. ชื่อ branch = **`<module>/<feature>`** โดย module ต้องเป็นของตัวเอง เช่น `rag/hybrid-search`
3. แก้ได้เฉพาะ **โฟลเดอร์ของตัวเอง** ตามตาราง ownership (`00_SHARED_PROJECT_CONTEXT.md` §8)
4. เขียนโค้ดตาม **Contract** ที่ Freeze Day 1 12:00 เท่านั้น — เปลี่ยนต้องผ่าน `contract/*` PR ที่ P1 + P3 approve
5. **ห้ามมีลายน้ำ AI** ใน commit / PR / code และห้าม commit ไฟล์ของ AI tool (`.claude/`, `.cursor/`, `CLAUDE.md` ฯลฯ) — มี hook + CI ตรวจ
6. ข้อมูลภาค/หลักสูตร **ต้องจริง** และมีแหล่งอ้างอิง · รายวิชา/หน่วยกิต/คะแนน skill ห้ามให้ LLM แต่ง
7. Mock ใช้ได้ระหว่างพัฒนา (Day 1–3) เพื่อไม่ต้องรอกัน แต่หลัง M3 ห้ามมี mock ใน flow จริง
8. **Merge ทุกวัน** — PR Cutoff 17:00, Daily Report 21:00
9. ก่อนเริ่มงานต้องอ่าน 00 ทั้ง 4 ไฟล์ แล้วจึงอ่านแผนของตัวเอง

## ไฟล์ที่ต้องอ่าน

| ลำดับ | ไฟล์ | เจ้าของ | ผลลัพธ์ |
|---|---|---|---|
| 00 | `00_SHARED_PROJECT_CONTEXT.md` | ทุกคน | เป้าหมาย, scope, UI, architecture, stack, โครงสร้างโฟลเดอร์ + เจ้าของ |
| 00 | `00_API_AND_DATA_CONTRACTS.md` | ทุกคน | API, `contract.ts` / `contract.py`, internal functions, DB, data formats |
| 00 | `00_GIT_DELIVERY_RULES.md` | ทุกคน | Git flow, PR, review, AI watermark, Docker, การสื่อสาร, freeze |
| 00 | `00_TIMELINE_AND_SYNC.md` + `gantt.html` | ทุกคน | Gantt, milestone, จุดอัปเดตรายวัน, checkpoint รายคน |
| 01 | `01_FRONTEND_CORE_3D_MASCOT.md` | P1 | Frontend หลัก, Design System, 3D COPIE, รวมชิ้นงาน |
| 02 | `02_USER_SYSTEM.md` | P2 | Google Login, Onboarding, Profile, History, Feedback |
| 03 | `03_AI_AGENT_BACKEND.md` | P3 | FastAPI, LLM client, Agent router/orchestrator, Docker |
| 04 | `04_DEPARTMENT_RAG.md` | P4 | Knowledge Base + Hybrid Retrieval + sources |
| 05 | `05_CURRICULUM_SKILL_TOOLS.md` | P5 | Curriculum data/tool + Skill assessment/scoring |
| 06 | `06_DYNAMIC_RENDERER.md` | P6 | Renderer ทุก response_type + mock fixtures + `/dev` |
| 07 | `07_SUGGESTIONS_LOCAL_INTENT_ML.md` | P7 | Suggested questions + Local intent classifier (ML) |
| 08 | `08_EXPORT_QA_EVAL.md` | P8 | Copy/Export + Eval set/script + QA + README |
| 09 | `09_INTEGRATION_ACCEPTANCE_RUNBOOK.md` | P1 + P8 + ทุกคน | วิธีรวมระบบ, Demo 1–6, failure tests, release sign-off |
| 10 | `10_WORK_COMPLETION_REPORT_TEMPLATE.md` | ทุกคน | รายงานจบงาน / handoff |
| 11 | `11_INTERACTION_MODES_AND_MASCOT_MOTION.md` | งานต่อยอด | โหมดบุคลิก/ธีม, มาสคอตตามโหมด และ motion interaction |
| AI | `AI_EXECUTION_INSTRUCTIONS.md` | ทุกคน | prompt สำหรับให้ AI ช่วยเขียนโดยไม่ทิ้งลายน้ำ |
| PR | `PR_TEMPLATE.md` | ทุกคน | เนื้อหาที่ต้องกรอกใน PR (GitHub เติมให้อัตโนมัติ) |

## บทบาทและ dependency

| คน | Module (branch prefix) | รับของจาก | ส่งของให้ | ถ้าไม่เสร็จจะเกิดอะไร |
|---|---|---|---|---|
| P1 | `core`, `mascot` | P3, P6, P2, P7, P8 | ผู้ใช้ | ไม่มีหน้าหลัก/COPIE, งาน frontend ของทุกคนไม่มีที่แสดง |
| P2 | `user` | P3 (scaffold) | P3, P1, P8 | login/onboarding ไม่ได้, agent ไม่รู้บริบทผู้ใช้, ไม่มี history/feedback |
| P3 | `agent` | P2, P4, P5, P7 | P1, P6, P8 | ไม่มีสมองกลาง — ถามอะไรก็ตอบไม่ได้ |
| P4 | `rag` | ข้อมูลภาคจริง, P5 | P3 | ตอบข้อมูลภาคไม่ได้หรือไม่มีแหล่งอ้างอิง |
| P5 | `tools` | เล่มหลักสูตรจริง | P3, P4 | ไม่มีตารางรายวิชา/แบบประเมิน skill |
| P6 | `renderer` | Contract, P1 | P1, ทุกคน (mock) | คำตอบแสดงเป็น JSON/ข้อความเปล่า ไม่มี Dynamic UI |
| P7 | `suggest`, `intent-ml` | P8, P1, P2 | P1, P3 | (optional) ไม่มีปุ่มคำถามแนะนำ / ไม่มีโมเดล ML ในเครื่อง — Core ยังทำงาน |
| P8 | `export`, `qa` | P2, P3, P1 | P7, P3, ทุกคน | (optional สำหรับ export) ไม่มีใครวัดผลว่าระบบตอบถูกจริง |

## ลำดับการทำงานที่ลดการรอกัน

```text
Day 1 AM  Contract Freeze (P1 + P3 นำ, ทุกคนร่วม)
             │
Day 1 PM  ├── P1 design system + app shell      ├── P6 mock fixtures + /dev
          ├── P3 LLM client + rule router       ├── P2 DB + dev login + stubs
          ├── P4 knowledge + stub               ├── P5 curriculum data + stubs
          └── P7 suggested prompts              └── P8 eval set
             │   (ทุกคน merge stub ภายใน 17:00 = M1)
Day 2–3   ทุกคนทำของจริงคู่ขนาน โดยใช้ stub/mock ของคนอื่น
             │
          P4, P5, P2 ──► P3 Agent ──► /api/chat ──► P1 Workspace ◄── P6 Renderer
                                                        ▲
                                              P2 History/Feedback, P7, P8
Day 4     Integration + QA 2 รอบ → Feature Freeze 18:00 → main v0.9
Day 5     Bug fix → Code Freeze 15:00 → v1.0 16:00 → ซ้อม Demo
```

## Definition of Done ระดับทีม

- `docker compose up --build` จาก clone ใหม่แล้วเว็บ + API ขึ้นครบ
- Demo 1–6 ใน `09_INTEGRATION_ACCEPTANCE_RUNBOOK.md` ผ่านบน `main`
- Eval: intent accuracy ≥ 85%, latency เฉลี่ย < 8 วินาที
- ข้อมูลหลักสูตรตรงเล่ม, คำตอบ RAG มี sources ที่เปิดได้
- ไม่มี secret, ลายน้ำ AI หรือ mock ใน flow จริง
- ทุกคนส่ง `docs/handoffs/PX-<module>.md` ตาม template 10
