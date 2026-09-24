# P4 — Department RAG + Knowledge Base

## Mission

รวบรวมข้อมูล **จริง** ของภาควิชาวิศวกรรมคอมพิวเตอร์ RMUTT ให้เป็น Knowledge Base ที่สะอาด แล้วสร้าง Retrieval แบบ Hybrid (BM25 + Vector) ที่คืนเนื้อหาพร้อม **แหล่งอ้างอิงที่ตรวจสอบได้** ให้ Agent ใช้ตอบคำถามเกี่ยวกับภาค

**ความสำคัญ:** นี่คือส่วน "University RAG" + "Retrieval / Knowledge" + "Knowledge Base" ใน diagram ถ้าข้อมูลไม่จริงหรือค้นไม่เจอ COPIE จะตอบมั่วหรือตอบว่าไม่รู้ ซึ่งทำให้ระบบ "ตอบข้อมูลได้จริง" ไม่ผ่าน

## Ownership

แก้ได้โดยตรง
- `data/knowledge/**`
- `backend/app/modules/rag/**` (รวม tests)

ต้องขอ review เพิ่ม
- `backend/app/modules/agent/prompts.py` ส่วน RAG — ร่วมกับ P3
- `backend/requirements.txt` (เพิ่ม `sentence-transformers`, `chromadb`, `rank-bm25`, `pythainlp`) — P3

Dependency

| รับจาก | อะไร |
|---|---|
| P5 | ข้อความสรุปโครงสร้างหลักสูตร (Day 4) เพื่อให้ RAG ตอบภาพรวมหลักสูตรได้ |
| P8 | ผล eval คำถาม `department_info` (Day 4) |

ส่งให้: **P3** `search_department_knowledge()` (stub D1 17:00, จริง D2 21:00, hybrid D3)

## Stack

- `sentence-transformers` + `intfloat/multilingual-e5-small` (รองรับไทย, CPU ได้, ~470MB)
- `chromadb` (PersistentClient, โฟลเดอร์ `CHROMA_DIR`)
- `rank-bm25` + `pythainlp.word_tokenize` (engine `newmm`)
- `python-frontmatter` หรือแยก YAML เอง

## Target folder structure

```text
data/knowledge/
├─ ce-overview.md            # ภาพรวมภาค ประวัติ ปรัชญา
├─ program-structure.md      # โครงสร้างหลักสูตร หน่วยกิตรวม หมวดวิชา
├─ admission.md              # รอบรับสมัคร คุณสมบัติ
├─ tuition-scholarship.md
├─ labs-facilities.md
├─ careers.md
├─ coop-internship.md
├─ faq-prospective.md
├─ faq-current-student.md
├─ contact.md
├─ activities-clubs.md
└─ study-plan-overview.md    # (จาก P5 Day 4)

backend/app/modules/rag/   # 👤 P4
├─ __init__.py     # public: search_department_knowledge, ensure_index
├─ chunker.py      # parse front-matter, split by "## ", max 800 chars, overlap 100
├─ ingest.py       # python -m app.modules.rag.ingest [--rebuild]
├─ retriever.py    # vector_search(), bm25_search(), rrf_merge()
├─ service.py      # search_department_knowledge() — public function ให้ P3
├─ README.md       # วิธีเพิ่มเอกสาร / ingest ใหม่
└─ tests/          # test_rag.py
```

## Design details

### กติกาข้อมูล

- ทุกไฟล์มี front-matter `doc_id`, `title`, `source_url`, `updated` (ดูรูปแบบใน `00_API_AND_DATA_CONTRACTS.md` §6.1)
- **ห้ามแต่งข้อมูลเอง** — ทุกย่อหน้าต้องมาจากแหล่งที่ระบุ ถ้าสรุปเองให้สรุปจากแหล่งนั้นเท่านั้น
- แหล่งที่ใช้ได้: เว็บภาค/คณะวิศวกรรมศาสตร์ RMUTT, เอกสารหลักสูตร (มคอ.2), ประกาศรับสมัคร, เพจทางการของภาค
- ตัดเมนูเว็บ, footer, ข้อความซ้ำ · หัวข้อย่อยใช้ `##` เพื่อให้ chunk ตามหัวข้อ
- ข้อมูลบุคคล: ใส่เฉพาะที่เผยแพร่สาธารณะ (ชื่อ-ตำแหน่งอาจารย์ได้, ห้ามเบอร์ส่วนตัว)

### Pipeline

```text
*.md → parse front-matter → split "## " sections → ตัดยาว > 800 (overlap 100)
     → chunk_id = f"{doc_id}#{i}", metadata {doc_id,title,section,url}
     → embed("passage: " + title + " | " + section + "\n" + text)
     → Chroma collection "ce_knowledge" (cosine)
     → BM25 index (tokenized ด้วย pythainlp) เก็บ pickle ใน storage/bm25.pkl
```

### Query

```text
search_department_knowledge(query, top_k=4):
  v = vector_search("query: " + query, k=10)        # score = 1 - distance
  b = bm25_search(tokenize(query), k=10)
  merged = RRF(v, b, k=60)                           # score_rrf = Σ 1/(60 + rank)
  กรอง: ถ้า vector score สูงสุด < RAG_MIN_SCORE และ BM25 ไม่มีผล → []
  คืน top_k เป็น RetrievedChunk(text, Source(doc_id,title,section,url,snippet=text[:200],score))
```

- ถ้า BM25 ยังไม่เสร็จ ให้ `service.py` ใช้ vector อย่างเดียว (flag ใน code) — interface ไม่เปลี่ยน
- `ensure_index()` ให้ P3 เรียกตอน startup: ถ้า collection ว่าง → ingest อัตโนมัติ

### Prompt RAG (ร่วมกับ P3)

```text
ตอบคำถามโดยใช้เฉพาะข้อมูลใน CONTEXT ด้านล่าง
- อ้างอิงแหล่งด้วย [1], [2] ตามหมายเลข context
- ถ้า context ไม่พอ ให้บอกตรงๆ ว่าไม่พบข้อมูลในเอกสารของภาค และแนะนำให้ติดต่อภาค
- ห้ามเดาตัวเลข วันที่ ค่าเทอม ที่ไม่มีใน context
CONTEXT:
[1] (title — section) text...
```

## Implementation steps

### Phase 0 — Collect (Day 1 AM)
1. ลิสต์ URL แหล่งข้อมูลทั้งหมดใน `data/knowledge/SOURCES.md`
2. แบ่งหัวข้อ 12 ไฟล์ตามโครงสร้างด้านบน

### Phase 1 — Clean + stub (Day 1 PM)
1. เขียน/clean อย่างน้อย 8 ไฟล์
2. `service.py` stub คืน 2 chunk mock ตาม type

Exit: **M1** — P3 import `search_department_knowledge` ได้

### Phase 2 — Vector RAG (Day 2)
1. AM: `chunker.py`, `ingest.py` → Chroma
2. PM: `retriever.vector_search`, `service.py` ของจริง, ครบ 12 ไฟล์, `rag/README.md`

Exit: **M2** — `python -m app.modules.rag.ingest && python -c "from app.modules.rag import search_department_knowledge as s; print(s('ภาคคอมเรียนอะไร'))"` ได้ผลที่มี source

### Phase 3 — Hybrid + prompt (Day 3)
1. AM: BM25 + RRF + threshold
2. PM: prompt RAG กับ P3, `test_rag.py` 20 คำถาม (`query → doc_id ที่ควรเจอ`)

Exit: **M3** — hit@4 ≥ 80%

### Phase 4 — Tuning (Day 4)
- ปรับ chunk size/top_k/threshold ตามผล eval ของ P8, เติมเอกสารสำหรับคำถามที่ตอบไม่ได้, รับข้อความหลักสูตรจาก P5

Exit: **M4**

### Phase 5 — Data fix (Day 5)
- ตรวจข้อมูลกับเว็บต้นทางอีกรอบ, แก้ตาม feedback 👎 "ข้อมูลไม่ถูกต้อง"

## Required tests

| ประเภท | Cases |
|---|---|
| Chunker | ไฟล์มี/ไม่มี `##`, section ยาวเกิน, front-matter ขาด → error ชัดเจน |
| Retrieval | 20 คำถาม hit@4 ≥ 80% (บันทึกผลใน handoff) |
| Out-of-scope | "ราคาทองวันนี้", "ภาคไฟฟ้าเรียนอะไร" → `[]` หรือ score ต่ำกว่า threshold |
| Ingest | รัน 2 ครั้งไม่เกิด chunk ซ้ำ (`--rebuild` ล้างก่อน) |

## Acceptance checklist

- [ ] ≥ 12 ไฟล์ knowledge พร้อม `source_url` จริงทุกไฟล์
- [ ] ingest ได้ด้วยคำสั่งเดียวและ startup ingest อัตโนมัติใน Docker
- [ ] คืน `Source` ครบ field, ลิงก์เปิดได้
- [ ] hybrid search ทำงาน (หรือ vector-only ที่ผ่าน hit@4 ≥ 80%)
- [ ] คำถามนอกขอบเขตไม่คืนเอกสารมั่ว
- [ ] ไม่มีข้อมูลที่แต่งขึ้นเอง

## Branch / PR breakdown

1. `rag/knowledge-v1` — SOURCES.md + 8 ไฟล์ + stub
2. `rag/ingest-pipeline` — chunker + ingest
3. `rag/vector-retriever` — vector search + service + 12 ไฟล์
4. `rag/hybrid-search` — BM25 + RRF
5. `rag/eval-and-prompt` — test 20 คำถาม + prompt
6. `rag/tuning`, `rag/data-fix`

## Completion report requirements

สร้าง `docs/handoffs/P4-department-rag.md` ระบุเพิ่ม: รายการเอกสาร + URL, จำนวน chunk, ค่า chunk size/top_k/threshold ที่เลือกและเหตุผล, ตาราง 20 คำถาม + ผล hit, ตัวอย่างคำตอบพร้อม sources, วิธีเพิ่มเอกสารใหม่
