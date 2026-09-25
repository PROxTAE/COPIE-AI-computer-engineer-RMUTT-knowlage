# rag — Department Knowledge Retrieval

| | |
|---|---|
| เจ้าของ | **P4** |
| แผนงาน | [`04_DEPARTMENT_RAG.md`](../../../../IMPLEMENTATION_PLANS/04_DEPARTMENT_RAG.md) |
| Branch prefix | `rag/` |

## หน้าที่

อ่านเอกสารใน `data/knowledge/` แบ่ง chunk ตามหัวข้อ `##` แล้วค้นคืนเนื้อหาพร้อม `Source` (แหล่งอ้างอิงจริง)

## Public API (สิ่งที่ module อื่นเรียกใช้ได้)

```python
from app.modules.rag import search_department_knowledge, ensure_index

search_department_knowledge(query: str, top_k: int = 4) -> list[RetrievedChunk]
ensure_index() -> int   # โหลดเอกสารใหม่ คืนจำนวน chunk (เรียกตอน startup ได้)
```

- ผลเรียงจาก score มากไปน้อย ทุกผลมี `source.url` เป็นลิงก์จริงจาก front-matter
- คืน `[]` เมื่อ: query ว่าง, `top_k <= 0`, มีคำหยาบ, หรือคำถามไม่อยู่ในเอกสารของภาค (Agent ควรตอบว่า "ไม่พบข้อมูลในเอกสารของภาค")

## โครงไฟล์

```text
rag/
├─ __init__.py          # export search_department_knowledge, ensure_index
├─ chunker.py           # front-matter + แบ่ง section ตาม "## " (error ชัดเจนถ้า front-matter ไม่ครบ)
├─ lexical.py           # ค้นแบบ keyword: TF-IDF บน character 2/3-gram + query synonyms + ตัวกันคำถามนอกขอบเขต
├─ guard.py             # ตรวจคำหยาบ (รองรับเว้นวรรค/ลากเสียง, ไม่จับคำปกติเช่น "สัดส่วน")
├─ service.py           # search_department_knowledge() — จุดเดียวที่ P3 เรียก
└─ tests/
   ├─ test_rag.py       # data, chunker, contract, accuracy, out-of-scope, profanity
   └─ retrieval_cases.py# ชุดคำถาม → doc_id ที่ควรเจอ (ชุดจูน + held-out + นอกขอบเขต)
```

รอบถัดไป (ตามแผน): `ingest.py` + Chroma vector search → BM25 + RRF แทน `lexical.py` โดยไม่เปลี่ยน interface

## วิธีเพิ่มเอกสาร

1. สร้าง `data/knowledge/<doc_id>.md` ขึ้นต้นด้วย front-matter

   ```markdown
   ---
   doc_id: <ต้องตรงกับชื่อไฟล์>
   title: <ชื่อเอกสาร>
   source_url: https://<หน้าเว็บ rmutt.ac.th ที่มีข้อความนี้จริง>
   updated: YYYY-MM-DD
   ---
   # หัวเรื่อง
   ## หัวข้อย่อย
   เนื้อหาจากแหล่งเท่านั้น
   ```

2. เพิ่มแถวใน `data/knowledge/SOURCES.md`
3. ถ้าเนื้อหาบาง section มาจากหน้าอื่น ให้เขียน `ที่มา: <url>` ไว้ใต้หัวข้อนั้น
4. รัน test

## วิธีทดสอบ

```bash
cd backend
python -m pytest -q app/modules/rag
python -c "from app.modules.rag import search_department_knowledge as s; print(s('ค่าเทอมเท่าไหร่'))"
```

## ค่าที่ปรับได้

| ค่า | ที่อยู่ | ความหมาย |
|---|---|---|
| `MIN_COVERAGE = 0.2` | `service.py` | สัดส่วน 3-gram ของคำถามที่ต้องพบใน chunk ต่ำกว่านี้ถือว่านอกขอบเขต |
| `KNOWLEDGE_DIR` | env (ไม่บังคับ) | โฟลเดอร์เอกสาร ค่าเริ่มต้น `<repo>/data/knowledge` ใช้ตั้งใน Docker |
| `QUERY_SYNONYMS` | `lexical.py` | คำที่ผู้ใช้พิมพ์ → คำที่เอกสารใช้ เช่น "แล็บ" → "ห้องปฏิบัติการ" |

## ใช้ของ module อื่นได้จาก

`app.core`, `app.schemas.contract`
