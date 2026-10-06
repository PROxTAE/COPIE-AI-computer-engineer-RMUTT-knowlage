# data/eval

เจ้าของ: **P8 (qa)**

`questions.jsonl` ชุดคำถามทดสอบ 60 ข้อ — ดู §6.4 · P7 ใช้เป็น test set ของ intent classifier

## ไฟล์

| ไฟล์ | ใช้ทำอะไร |
|---|---|
| `questions.jsonl` | 1 บรรทัด = 1 คำถาม · field ตาม `08_EXPORT_QA_EVAL.md`: `id`, `question`, `intent`, `expected_type`, `must_contain`, `user_type`, `study_year` |
| `evidence.json` | ต่อ `id`: กลุ่ม (`group`), ผู้ตรวจเฉลย (`review`), และที่มาของ `must_contain` (`evidence`) |

ตรวจทุกครั้งที่แก้: `python scripts/eval/check_questions.py` (ต้องได้ `OK: 60 questions valid`)

## กติกาการติด label

- `intent` = intent ที่ถูกต้องตามนิยามใน `ROUTER_SYSTEM` (`backend/app/modules/agent/prompts.py`) ไม่ใช่ผลที่ระบบตอบตอนนี้
- `expected_type` ต้องเป็น type ที่ intent นั้นผลิตได้ตาม §8 ของ contract
- คำถามนอกขอบเขตติด `intent: general` + `expected_type: text` (คาดว่าปฏิเสธสุภาพหรือ "ไม่พบข้อมูล") แยกกลุ่มด้วย `group: out_of_scope` ใน `evidence.json`
- `user_type` / `study_year` คือโปรไฟล์ของผู้ถาม · `prospective` ไม่มี `study_year`
- `skill_analysis` ทุกข้อถามจาก user ที่ยังไม่เคยทำแบบประเมิน จึงคาด `assessment_form`

## ที่มาของ `must_contain`

ทุกคำใน `must_contain` ต้องมาจากข้อมูลจริงใน repo ไม่แต่งเอง สคริปต์ตรวจตาม `evidence.kind`:

| kind | ตรวจอย่างไร |
|---|---|
| `term` | คำนวณจาก `curriculum.json` ปี/เทอมนั้น: รหัส, ชื่อไทย/อังกฤษ, `credit_detail`, ผลรวมหน่วยกิต |
| `course` | field ของวิชารหัสนั้น + `"ปี Y เทอม S"` |
| `program_total` | `total_credits` และต้องเท่ากับผลรวมหน่วยกิตทุกวิชา |
| `overview` | `"ปี N"` ของชั้นปีที่มีข้อมูล |
| `assessment` | `assessment_id` ใน `data/assessment/skill_v1.json` |
| `doc` | ข้อความอยู่ในไฟล์ `data/knowledge/*.md` ที่อ้าง (ไฟล์ต้องมี `source_url`) · ไฟล์ที่อ้าง = source ที่คาดว่าจะได้ |
| `none` | ไม่มีข้อมูลให้ตรวจ (`general`, นอกขอบเขต) → `must_contain` ว่าง |

คำตอบแบบเปิด (เช่น "ภาคคอมเรียนเกี่ยวกับอะไร") ใช้ `must_contain: []` แต่ยังระบุเอกสารที่ควรเป็น source

## Coverage

| กลุ่ม | intent | จำนวน | expected_type | ผู้ตรวจเฉลย |
|---|---|---:|---|---|
| curriculum | `curriculum` | 12 | `course_table` 10, `cards` 2 | P5 |
| course_detail | `course_detail` | 8 | `cards` | P5 |
| department_info | `department_info` | 15 | `text` (+ sources) | P4 |
| skill_analysis | `skill_analysis` | 6 | `assessment_form` | P5 |
| general | `general` | 9 | `text` | P3 |
| out_of_scope | `general` | 10 | `text` | P3 |

- โปรไฟล์: prospective 29, current_student 26, near_graduate 5 · ครอบคลุมทุกเทอมปี 1–4
- `must_contain` 57 คำ ใน 40 ข้อ ตรวจย้อนกลับถึงไฟล์ข้อมูลได้ทุกคำ

## สถานะการตรวจเฉลย

เฉลยทุกข้อดึงจากข้อมูลที่ merge แล้ว (`curriculum.json` ของ P5 อ้างเล่มหลักสูตร 2568, knowledge ของ P4 อ้าง `source_url`) แต่ **ยังรอเจ้าของข้อมูลยืนยัน**:

- **รอ P5**: e001–e020, e036–e041 — โดยเฉพาะ e011 (หลักสูตรทั้งหมดกี่หน่วยกิต → 141) ที่ข้อมูลมีแต่การ์ดภาพรวมยังไม่แสดง
- **รอ P4**: e021–e035 — คำใน `must_contain` เลือกแบบที่ LLM น่าจะคงรูป (เช่น `3460` แทนเบอร์เต็ม) ถ้าพบว่าตกเพราะรูปแบบตัวเลข/วันที่ ให้ปรับคำ ไม่ใช่ปรับข้อมูล
- **รอ P3**: e042–e060 — ยืนยันว่าคำถามนอกขอบเขตควรได้ `general` ตามแผน (ไม่ใช่ `department_info` + "ไม่พบข้อมูล")

ยังไม่มีในชุดนี้: คำถามกำกวมที่ควรได้ `clarify` และคำถามแบบ "เทอมหน้า"/"ปี 3 ทั้งปีกี่หน่วยกิต" ที่ระบบยังไม่มีพฤติกรรมที่ตกลงกัน
