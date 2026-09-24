# agent — AI Agent / LLM / Chat API

| | |
|---|---|
| เจ้าของ | **P3** |
| แผนงาน | [`03_AI_AGENT_BACKEND.md`](../../../../IMPLEMENTATION_PLANS/03_AI_AGENT_BACKEND.md) |
| Branch prefix | ดู `IMPLEMENTATION_PLANS/00_GIT_DELIVERY_RULES.md` §2 |

## หน้าที่

สมองกลาง: แยก intent (LLM + rule fallback + local ML), ตรวจข้อมูลที่ขาด, เรียก tool, สร้าง `AgentResponse` ให้ตรง contract และ endpoint `/api/chat`, `/api/assessment/submit`

## โครงไฟล์ที่จะสร้าง

```text
agent/
├─ __init__.py       # router
├─ router.py         # POST /api/chat, POST /api/assessment/submit
├─ orchestrator.py
├─ intent_router.py
├─ rule_router.py
├─ generator.py
├─ prompts.py
├─ llm_client.py     # generate_text(), generate_json() — จุดเดียวที่คุย Gemini
└─ tests/
```

## Public API (สิ่งที่ module อื่นเรียกใช้ได้)

`router`

## ใช้ของ module อื่นได้จาก

`app.modules.user`, `app.modules.rag`, `app.modules.tools`, `app.modules.intent_ml`, `app.core`, `app.schemas.contract`
