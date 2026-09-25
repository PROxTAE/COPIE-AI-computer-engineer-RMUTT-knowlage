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
ensure_index() -> int   # โหลดเอกสาร + sync vector index + โหลดโมเดลทั้งสอง คืนจำนวน chunk
```

- ผลเรียงจากเกี่ยวข้องมากไปน้อย · `source.score` = ความน่าจะเป็น 0–1 จาก reranker ว่า chunk นี้ตอบคำถามได้ · ทุกผลมี `source.url` เป็นลิงก์จริงจาก front-matter
- คืน `[]` เมื่อ: query ว่าง, `top_k <= 0`, มีคำหยาบ, ถามถึงภาค/คณะ/มหาวิทยาลัยอื่น, หรือไม่มี chunk ที่ตอบได้ (Agent ควรตอบว่า "ไม่พบข้อมูลในเอกสารของภาค")
- **เรียก `ensure_index()` ตอน startup** (main.py ทำแล้ว) — โหลดโมเดลครั้งแรก ~30 วินาที ไม่งั้นคำถามแรกจะช้า
- ถ้าโหลดโมเดล/Chroma ไม่ได้ จะ log error ค้นด้วยวิธีสำรอง และลองโหลดใหม่ทุก 60 วินาที (ไม่ throw)

## วิธีค้น

```text
คำถาม
 ├─ กรอง: ว่าง / คำหยาบ (guard.py) / ถามถึงหน่วยงานอื่น (scope.py)          → []
 ├─ candidates: vector e5 top 10 (×2) + BM25 คำไทย top 10 (×1) รวมด้วย RRF k=60
 ├─ reranker (bge-reranker-v2-m3) ให้คะแนน 6 อันดับแรก 0–1
 └─ ตัดที่ MIN_RELEVANCE = 0.005 → top_k
```

ทำไมต้องมี reranker: vector (e5) วัดว่า "หัวข้อคล้ายกัน" คะแนนคำถามที่ไม่เกี่ยวกับภาคจึงอยู่ช่วงเดียวกับคำถามจริง (~0.74–0.9) ส่วน cross-encoder อ่านคำถามคู่กับ chunk แล้วบอกว่า "ตอบได้จริงไหม" — บนชุดจูน คำถามนอกขอบเขตได้สูงสุด 0.0034 คำถามที่ตอบได้ส่วนใหญ่ > 0.01

ทำไมต้องมีกฎหน่วยงานอื่น: "ภาคไฟฟ้าเรียนอะไร" ต่างจาก "ภาคคอมเรียนอะไร" แค่คำเดียว reranker ยังให้ 0.16 ได้ · ถ้าถามเปรียบเทียบกับภาคคอม ("ภาคคอมกับภาคไฟฟ้าต่างกันยังไง") จะไม่ตัดทิ้ง

วิธีสำรอง: ไม่มี reranker → กรองด้วยสัดส่วน 3-gram (`lexical.py`, `MIN_COVERAGE`) และเรียงด้วย RRF · ไม่มี vector → ใช้ BM25 อย่างเดียว

## โครงไฟล์

```text
rag/
├─ __init__.py          # export search_department_knowledge, ensure_index
├─ chunker.py           # front-matter + แบ่ง section ตาม "## " + ตัด section ยาวเกิน 800 ตัวอักษร (overlap 100)
├─ ingest.py            # สร้าง vector index ใน Chroma: python -m app.modules.rag.ingest [--rebuild]
├─ retriever.py         # vector_search() บน Chroma, sync_index() (embed ใหม่เฉพาะที่เปลี่ยน), rrf_merge()
├─ thai_text.py         # ตัดคำไทย (pythainlp + ศัพท์ของภาค) + BM25
├─ reranker.py          # cross-encoder ให้คะแนนคู่ (คำถาม, chunk) 0–1
├─ scope.py             # กฎ: ถามถึงภาค/คณะ/มหาวิทยาลัยอื่น = นอกขอบเขต
├─ lexical.py           # คำพ้อง (แล็บ → ห้องปฏิบัติการ) + TF-IDF 3-gram สำหรับวิธีสำรอง
├─ guard.py             # ตรวจคำหยาบ (รองรับเว้นวรรค/ลากเสียง, ไม่จับคำปกติเช่น "สัดส่วน")
├─ service.py           # search_department_knowledge() — จุดเดียวที่ P3 เรียก
└─ tests/
   ├─ conftest.py       # test ปกติไม่โหลดโมเดล · RUN_LIVE_RAG=1 = ใช้โมเดลจริง
   ├─ test_rag.py       # data, chunker, contract, profanity, accuracy (live)
   ├─ test_service.py   # scope, BM25, reranker (ปลอม), fallback, retry
   ├─ test_ingest.py    # ตัด chunk ยาว, ingest ซ้ำไม่เกิด chunk ซ้ำ, --rebuild
   ├─ test_retriever.py # RRF, embed เฉพาะที่เปลี่ยน, sync
   └─ retrieval_cases.py# ชุดคำถาม → doc_id ที่ควรเจอ (ชุดจูน + held-out 4 ชุด + นอกขอบเขต)
```

## สร้าง vector index

```bash
cd backend
python -m app.modules.rag.ingest            # เพิ่ม/อัปเดต/ลบ chunk ที่เปลี่ยน (รันซ้ำได้ ไม่เกิดซ้ำ)
python -m app.modules.rag.ingest --rebuild  # ล้าง collection แล้ว embed ใหม่ทั้งหมด
```

- `EMBEDDING_MODEL` (ค่าเริ่มต้น `intfloat/multilingual-e5-small`, ~470MB) และ reranker `BAAI/bge-reranker-v2-m3` (~2.2GB, เปลี่ยนได้ด้วย env `RERANK_MODEL`) ดาวน์โหลดครั้งแรกอัตโนมัติ
- index อยู่ที่ `CHROMA_DIR` (ค่าเริ่มต้น `./storage/chroma`, อยู่ใน `.gitignore`) collection `ce_knowledge` (cosine)
- ข้อความที่ embed = `passage: <title> | <section>\n<text>` (e5 ต้องมี prefix `passage:` / `query:`)
- แต่ละ chunk เก็บ hash ของเนื้อหาใน metadata → แก้เอกสารแล้ว `ensure_index()` จะ embed ใหม่เฉพาะ chunk ที่เปลี่ยน

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
4. รัน test (รวมแบบ live) แล้วดูว่าความแม่นยำไม่ลดลง

## วิธีทดสอบ

```bash
cd backend
python -m pytest -q app/modules/rag                      # เร็ว ไม่โหลดโมเดล (วิธีสำรอง)
RUN_LIVE_RAG=1 python -m pytest -q app/modules/rag       # ใช้โมเดลจริง + วัดความแม่นยำทุกชุด (~10 นาที)
python -c "from app.modules.rag import ensure_index, search_department_knowledge as s; ensure_index(); print(s('ค่าเทอมเท่าไหร่'))"
```

## ค่าที่ปรับได้ (service.py เว้นแต่ระบุ)

| ค่า | ความหมาย |
|---|---|
| `MIN_RELEVANCE = 0.005` | คะแนน reranker ต่ำกว่านี้ = chunk ไม่ตอบคำถาม |
| `RERANK_CANDIDATES = 6` | จำนวน candidate ที่ส่งให้ reranker (10 แม่นขึ้น 1 ข้อใน 113 แต่ช้าขึ้น 60%) |
| `CANDIDATES = 10`, `VECTOR_WEIGHT = 2.0`, `BM25_WEIGHT = 1.0` | จำนวนผลจากแต่ละวิธีและน้ำหนักใน RRF |
| `USE_VECTOR`, `USE_RERANKER` | `False` = ไม่โหลดโมเดลนั้น (ใช้วิธีสำรอง) |
| `MIN_COVERAGE = 0.2` | ตัวกรองของวิธีสำรองเมื่อไม่มี reranker |
| `KNOWLEDGE_DIR`, `RERANK_MODEL` | env (ไม่บังคับ) โฟลเดอร์เอกสาร / ชื่อโมเดล reranker |
| `QUERY_SYNONYMS` (`lexical.py`), `DOMAIN_WORDS` (`thai_text.py`) | คำพ้องและศัพท์ของภาคสำหรับการค้นแบบคำ |

## ใช้ของ module อื่นได้จาก

`app.core`, `app.schemas.contract`
