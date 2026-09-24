# rag — Department Knowledge Retrieval

| | |
|---|---|
| เจ้าของ | **P4** |
| แผนงาน | [`04_DEPARTMENT_RAG.md`](../../../../IMPLEMENTATION_PLANS/04_DEPARTMENT_RAG.md) |
| Branch prefix | ดู `IMPLEMENTATION_PLANS/00_GIT_DELIVERY_RULES.md` §2 |

## หน้าที่

อ่านเอกสารใน `data/knowledge/`, แบ่ง chunk, สร้าง embedding ลง Chroma, ค้นแบบ hybrid (BM25 + vector) แล้วคืนเนื้อหาพร้อม `Source`

## โครงไฟล์ที่จะสร้าง

```text
rag/
├─ __init__.py       # search_department_knowledge, ensure_index
├─ chunker.py
├─ ingest.py         # python -m app.modules.rag.ingest [--rebuild]
├─ retriever.py
├─ service.py
└─ tests/
```

## Public API (สิ่งที่ module อื่นเรียกใช้ได้)

`search_department_knowledge(query, top_k=4) -> list[RetrievedChunk]`, `ensure_index()`

## ใช้ของ module อื่นได้จาก

`app.core`, `app.schemas.contract`
