# P8 — Copy / Export + QA & Evaluation + README / Demo Script

## Mission

1. **Copy / Export** — ปุ่มคัดลอกคำตอบ และ Export บทสนทนาเป็น TXT / JSON
2. **QA & Evaluation** — ชุดคำถามทดสอบ 60 ข้อ + สคริปต์วัดผล Agent อัตโนมัติ + เป็นผู้คุมคุณภาพช่วง Integration (Day 4–5)
3. **README / Demo Script** — วิธีติดตั้ง/รัน และสคริปต์ Demo ทีละขั้น

**ความสำคัญ:** Copy/Export เป็น optional แต่ **QA/Eval คือสิ่งที่ทำให้ทีมรู้ว่าระบบ "ตอบถูกจริง"** และตัวเลข accuracy/latency ใช้ในรายงาน ถ้าไม่มีคนนี้ ทุกคนจะคิดว่าของตัวเองใช้ได้แต่ไม่มีใครเดินทั้ง flow

## Ownership

แก้ได้โดยตรง
- `frontend/src/modules/export/**`
- `data/eval/**`, `scripts/eval/**`
- `docs/EVAL_REPORT.md`, `docs/DEMO_CHECKLIST.md`, `README.md` (P1 review)

ต้องขอ review เพิ่ม
- วางปุ่มใน Workspace (P1), ข้อมูลคาดหวังของ eval (P4 สำหรับ department_info, P5 สำหรับ curriculum)

Dependency

| รับจาก | อะไร |
|---|---|
| P2 | `/api/auth/dev` สำหรับ eval script |
| P3 | `/api/chat` จริง (Day 3) |
| P1 | `chatStore.messages` สำหรับ export |
| P4 / P5 | คำตอบที่ถูกต้องสำหรับ `must_contain` |

ส่งให้: **P7** eval set (Day 2 12:00) · **P3/P4** eval report (Day 4) · **ทุกคน** GitHub Issues จาก QA

## Stack

- Frontend: React, Clipboard API, `Blob` + `URL.createObjectURL`
- Eval: Python `requests` (หรือ `httpx`), ผลลัพธ์เป็น Markdown

## Target folder structure

```text
frontend/src/modules/export/   # 👤 P8
├─ index.ts               # public: CopyButton, ExportMenu
├─ CopyButton.tsx         # props: { response: AgentResponse }
├─ ExportMenu.tsx         # props: { messages: ChatMessage[], title: string }
└─ formatters.ts          # responseToText(), conversationToText(), conversationToJson()

data/eval/questions.jsonl
scripts/eval/run_eval.py  # python scripts/eval/run_eval.py --base http://localhost:8000
docs/EVAL_REPORT.md       # สร้างโดยสคริปต์
docs/DEMO_CHECKLIST.md
README.md
```

## Design details

### Copy / Export

| ปุ่ม | พฤติกรรม |
|---|---|
| Copy | `responseToText`: message + (ตาราง → "รหัส ชื่อ หน่วยกิต" ทีละบรรทัด + รวม) + (cards → หัวข้อ/เนื้อหา) + (radar → คะแนน 6 ด้าน) + sources (ชื่อ + URL) · สำเร็จ → icon ✓ 2 วินาที · clipboard ใช้ไม่ได้ → เลือกข้อความใน textarea ชั่วคราวให้ผู้ใช้ copy เอง |
| Export TXT | หัวเรื่อง + วันที่ + ทุกข้อความ (`ผู้ใช้:` / `COPIE:`) · ชื่อไฟล์ `copie-<title>-<yyyyMMdd>.txt` |
| Export JSON | `ConversationDetail` ตาม contract (pretty print 2 spaces) |

### Eval set (`questions.jsonl`)

| กลุ่ม | จำนวน | ตัวอย่าง |
|---|---|---|
| `curriculum` | 12 | ปี 2 เทอม 1 เรียนอะไร / เทอมหน้าเรียนไร (ผู้ใช้ปี 1) / ปี 3 มีกี่หน่วยกิต |
| `course_detail` | 8 | วิชา Data Structure เรียนอะไร / 04-xxx-xxx คือวิชาอะไร |
| `department_info` | 15 | ภาคคอมเรียนอะไร / รับสมัครรอบไหน / มีแล็บอะไรบ้าง |
| `skill_analysis` | 6 | วิเคราะห์ skill ให้หน่อย / ฉันถนัดสายไหน |
| `general` | 9 | สวัสดี / ควรเริ่มเขียนโปรแกรมจากภาษาอะไร |
| นอกขอบเขต | 10 | ราคาทอง / ภาคไฟฟ้าเรียนอะไร / เขียน essay ให้หน่อย → คาด `general` + ปฏิเสธสุภาพ หรือ "ไม่พบข้อมูล" |

field: `id`, `question`, `intent`, `expected_type`, `must_contain` (list คำที่ต้องมีในคำตอบ/ข้อมูล), `user_type`, `study_year` (optional สำหรับ context)

### `run_eval.py`

```text
1. POST /api/auth/dev → token (สร้าง user ต่อ user_type/study_year ที่ต้องใช้ + PUT profile)
2. ต่อคำถาม: POST /api/chat (conversation ใหม่ทุกข้อ) → จับเวลา
3. ตรวจ: intent == meta.intent, response_type == expected_type,
         must_contain อยู่ใน message หรือ json.dumps(data), มี sources เมื่อ department_info
4. สรุป: accuracy แยก intent, response_type accuracy, must_contain pass rate,
         latency avg/p90, รายการข้อที่ fail
5. เขียน docs/EVAL_REPORT.md (มีวันเวลา + git SHA)
```

### Demo Checklist

ทีละ step ของ Demo 1–6 (ดู `09_INTEGRATION_ACCEPTANCE_RUNBOOK.md` §5) พร้อมช่อง ✅/❌, ผู้ทดสอบ, เวลา, หมายเหตุ

## Implementation steps

### Phase 1 — Eval set (Day 1 PM)
1. เขียน 60 ข้อ, ถาม P4/P5 เพื่อใส่ `must_contain` ที่ถูกต้อง

Exit: **M1** — ส่ง P7 ได้ภายใน Day 2 12:00

### Phase 2 — Copy / Export (Day 2)
1. AM: `formatters.ts` + `CopyButton`
2. PM: `ExportMenu` + โชว์ใน `/dev`, วางใน Workspace กับ P1

Exit: **M2**

### Phase 3 — Eval script + checklist (Day 3)
1. AM: `run_eval.py` (ทดสอบกับ mock ของ P3 ได้ก่อน)
2. PM: `DEMO_CHECKLIST.md`, README ร่าง (prerequisites, `.env`, รัน dev, รัน docker)

Exit: **M3**

### Phase 4 — QA (Day 4)
1. **11:00** รอบ 1: Demo checklist + eval บน develop → Issues (P0/P1/P2 + module) → แจ้ง `#status`
2. **16:00** รอบ 2: regression + eval ใหม่ → ส่ง report ให้ P3/P4/P7
3. 19:00 smoke test หลัง merge window

Exit: **M4** — report รอบ 2 ไม่มี P0

### Phase 5 — Release support (Day 5)
1. AM: regression หลังแก้บั๊ก, README ฉบับสมบูรณ์ (+ screenshot)
2. PM: smoke test บน `main` หลัง release (clone ใหม่ → docker compose up), จับเวลาซ้อม Demo

## Required tests

| ประเภท | Cases |
|---|---|
| Formatter | แต่ละ response_type แปลงเป็นข้อความถูก, ไม่มี `undefined`/`[object Object]` |
| Export | ไฟล์ TXT/JSON เปิดได้, JSON parse กลับเป็น `ConversationDetail` ได้ |
| Eval script | รันซ้ำได้, backend ปิดอยู่ → error ชัดเจนไม่ crash |

## Acceptance checklist

- [ ] Copy ใช้ได้ทุก response_type, Export TXT/JSON ได้
- [ ] Eval set 60 ข้อครบทุก intent + นอกขอบเขต
- [ ] `run_eval.py` สร้าง `EVAL_REPORT.md` ได้ด้วยคำสั่งเดียว
- [ ] QA 2 รอบใน Day 4 และทุกบั๊กเป็น GitHub Issue
- [ ] README ทำให้คนใหม่ clone แล้วรันได้โดยไม่ต้องถาม
- [ ] Demo checklist ผ่านครบบน `main`

## Branch / PR breakdown

1. `qa/eval-set`
2. `export/copy-button`
3. `export/export-menu`
4. `qa/eval-script`
5. `qa/demo-checklist`
6. `qa/readme`

## Completion report requirements

สร้าง `docs/handoffs/P8-export-qa.md` ระบุเพิ่ม: ผล eval รอบแรกเทียบรอบสุดท้าย, รายการ Issue ที่เปิด/ปิด, ผล Demo checklist บน main, เวลาซ้อม Demo, ข้อจำกัดที่เหลือ
