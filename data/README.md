# data/

ข้อมูลจริงที่ระบบใช้ตอบคำถาม — backend อ่านจากที่นี่ (ใน Docker mount แบบ read-only)

| โฟลเดอร์ | เจ้าของ | ใช้โดย |
|---|---|---|
| `knowledge/` | P4 | `app.modules.rag` |
| `curriculum/` | P5 | `app.modules.tools` |
| `assessment/` | P5 | `app.modules.tools` |
| `eval/` | P8 | `scripts/eval/`, `app.modules.intent_ml` (test set) |

ห้ามแต่งข้อมูลเอง — ทุกไฟล์ต้องอ้างอิงแหล่งจริงได้
