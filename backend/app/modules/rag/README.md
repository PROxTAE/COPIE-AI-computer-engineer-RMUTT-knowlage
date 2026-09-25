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
ensure_index() -> int   # โหลดเอกสาร + sync vector index + โหลดโมเดล คืนจำนวน chunk
```

- ผลเรียงจาก score มากไปน้อย (`score` 0–1 = RRF หารด้วยคะแนนสูงสุดที่เป็นไปได้) ทุกผลมี `source.url` เป็นลิงก์จริงจาก front-matter
- คืน `[]` เมื่อ: query ว่าง, `top_k <= 0`, มีคำหยาบ, หรือคำถามไม่อยู่ในเอกสารของภาค (Agent ควรตอบว่า "ไม่พบข้อมูลในเอกสารของภาค")
- **ควรเรียก `ensure_index()` ตอน startup** (โหลดโมเดล ~5–25 วินาที, ถ้า index ยังไม่มีจะ embed ให้) — ไม่เรียกก็ได้ แต่คำถามแรกจะช้าเท่านั้น
- ถ้าโหลดโมเดล/Chroma ไม่ได้ จะ log error แล้วค้นด้วย keyword อย่างเดียว (ยังคืน source จริง ไม่ throw)

## วิธีค้น

1. กรอง: query ว่าง / คำหยาบ (`guard.py`) / นอกขอบเขต (สัดส่วน 3-gram ของคำถามที่พบในเอกสาร < `MIN_COVERAGE`)
2. จัดอันดับ: vector (e5, top 10) น้ำหนัก 2 + keyword (`lexical.py`, top 10) น้ำหนัก 1 รวมด้วย RRF (k=60)
3. ตัด top_k

เหตุผลที่ใช้ keyword เป็นตัวกรองนอกขอบเขต: คะแนน cosine ของ e5 อยู่ช่วง ~0.74–0.9 ทั้งคำถามที่เกี่ยวและไม่เกี่ยว จึงตั้ง threshold จาก vector ไม่ได้ (`RAG_MIN_SCORE` ยังไม่ได้ใช้)

## โครงไฟล์

```text
rag/
├─ __init__.py          # export search_department_knowledge, ensure_index
├─ chunker.py           # front-matter + แบ่ง section ตาม "## " + ตัด section ยาวเกิน 800 ตัวอักษร (overlap 100)
├─ ingest.py            # สร้าง vector index ใน Chroma: python -m app.modules.rag.ingest [--rebuild]
├─ retriever.py         # vector_search() บน Chroma, sync_index() (embed ใหม่เฉพาะที่เปลี่ยน), rrf_merge()
├─ lexical.py           # ค้นแบบ keyword: TF-IDF บน character 2/3-gram + query synonyms + ตัวกันคำถามนอกขอบเขต
├─ guard.py             # ตรวจคำหยาบ (รองรับเว้นวรรค/ลากเสียง, ไม่จับคำปกติเช่น "สัดส่วน")
├─ service.py           # search_department_knowledge() — จุดเดียวที่ P3 เรียก
└─ tests/
   ├─ test_rag.py       # data, chunker, contract, accuracy, out-of-scope, profanity
   ├─ test_ingest.py    # ตัด chunk ยาว, ingest ซ้ำไม่เกิด chunk ซ้ำ, --rebuild (ใช้ embedder ปลอม ไม่โหลดโมเดล)
   ├─ test_retriever.py # RRF, embed เฉพาะที่เปลี่ยน, sync, fallback เป็น keyword เมื่อ vector ใช้ไม่ได้
   └─ retrieval_cases.py# ชุดคำถาม → doc_id ที่ควรเจอ (ชุดจูน + held-out 2 ชุด + นอกขอบเขต)
```

รอบถัดไป: ตัวกรองนอกขอบเขตระดับคำ (pythainlp) + BM25 แทน character n-gram

## สร้าง vector index

```bash
cd backend
python -m app.modules.rag.ingest            # เพิ่ม/อัปเดต/ลบ chunk ที่เปลี่ยน (รันซ้ำได้ ไม่เกิดซ้ำ)
python -m app.modules.rag.ingest --rebuild  # ล้าง collection แล้ว embed ใหม่ทั้งหมด
```

- โมเดล `EMBEDDING_MODEL` (ค่าเริ่มต้น `intfloat/multilingual-e5-small`, ~470MB) ดาวน์โหลดครั้งแรกอัตโนมัติ
- index อยู่ที่ `CHROMA_DIR` (ค่าเริ่มต้น `./storage/chroma`, อยู่ใน `.gitignore`) collection `ce_knowledge` (cosine)
- ข้อความที่ embed = `passage: <title> | <section>\n<text>` (e5 ต้องมี prefix `passage:` / `query:`)
- แต่ละ chunk เก็บ hash ของเนื้อหาใน metadata → แก้เอกสารแล้วไม่ต้อง ingest เอง: `ensure_index()` / คำถามแรกจะ embed ใหม่เฉพาะ chunk ที่เปลี่ยน

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
| `VECTOR_WEIGHT = 2.0`, `LEXICAL_WEIGHT = 1.0`, `CANDIDATES = 10` | `service.py` | น้ำหนักใน RRF และจำนวนผลที่นำมารวมจากแต่ละวิธี |
| `USE_VECTOR = True` | `service.py` | `False` = ค้นด้วย keyword อย่างเดียว (ไม่โหลดโมเดล) |
| `KNOWLEDGE_DIR` | env (ไม่บังคับ) | โฟลเดอร์เอกสาร ค่าเริ่มต้น `<repo>/data/knowledge` ใช้ตั้งใน Docker |
| `QUERY_SYNONYMS` | `lexical.py` | คำที่ผู้ใช้พิมพ์ → คำที่เอกสารใช้ เช่น "แล็บ" → "ห้องปฏิบัติการ" |

## ใช้ของ module อื่นได้จาก

`app.core`, `app.schemas.contract`
