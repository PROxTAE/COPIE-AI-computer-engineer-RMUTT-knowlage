# scripts/eval

เจ้าของ: **P8 (qa)** — `run_eval.py` ยิงคำถามใน `data/eval/questions.jsonl` เข้า `/api/chat` แล้วสร้าง `docs/EVAL_REPORT.md` (ดู `08_EXPORT_QA_EVAL.md`)

| สคริปต์ | คำสั่ง |
|---|---|
| `check_questions.py` | `python scripts/eval/check_questions.py` — ตรวจ JSONL ทุกบรรทัด, จำนวน 60, สัดส่วน label และที่มาของ `must_contain` (ไม่ต้องรัน backend) |
