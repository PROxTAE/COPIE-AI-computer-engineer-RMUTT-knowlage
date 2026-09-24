# Backend modules

FastAPI **แอปเดียว** (`app/main.py`) รันเป็น process เดียว — module เรียกกันเป็น Python function ธรรมดา ไม่มี HTTP ภายใน

| Module | เจ้าของ | หน้าที่ |
|---|---|---|
| [`user/`](user/README.md) | P2 | DB, auth, profile, history, skill store, feedback, stats |
| [`agent/`](agent/README.md) | P3 | Intent router, orchestrator, LLM, `/api/chat` |
| [`rag/`](rag/README.md) | P4 | Knowledge retrieval (BM25 + vector) |
| [`tools/`](tools/README.md) | P5 | Curriculum + Skill assessment |
| [`intent_ml/`](intent_ml/README.md) | P7 | Local intent classifier |

ส่วนกลาง (ไม่ใช่ module)
- `app/main.py`, `app/core/` — P3 (เพิ่ม router ของ module ใน `main.py` ผ่าน PR)
- `app/schemas/contract.py` — 🔒 shared contract (แก้ผ่าน `contract/*` PR, P1 + P3 approve)

## กติกา module boundary

1. **แก้ได้เฉพาะ module ของตัวเอง**
2. **เรียก module อื่นผ่าน `__init__.py` เท่านั้น** — `from app.modules.rag import search_department_knowledge` ✅ · `from app.modules.rag.retriever import ...` ❌
3. module ต้อง re-export ทุก function สาธารณะไว้ใน `__init__.py` ของตัวเอง
4. Request/response model ใช้จาก `app.schemas.contract` — ห้ามสร้างซ้ำ
5. ตาราง DB เป็นของ `user` — module อื่นอ่าน/เขียนผ่าน function ของ `user` เท่านั้น
6. test อยู่ใน `app/modules/<module>/tests/`
