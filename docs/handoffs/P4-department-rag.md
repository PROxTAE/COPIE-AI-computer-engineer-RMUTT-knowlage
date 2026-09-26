# [P4] Department RAG — Completion Report

## 1. Metadata

| Field | Value |
|---|---|
| ผู้รับผิดชอบ | P4 (`Peemaxnaja`) |
| แผนงาน | `IMPLEMENTATION_PLANS/04_DEPARTMENT_RAG.md` |
| PR ที่เกี่ยวข้อง | #2 (knowledge + stub) · #16 (ingest) · #20 (vector) · #24 (hybrid + reranker) · #36 (knowledge-v2) · #38 (FAQ) · #40 (fallback) |
| Final commit SHA | `93348c9` (develop หลัง merge #40) |
| Reviewer | `PROxTAE`, `kritsanapongpixel4` |
| วันที่ | 2026-09-26 |

## 2. สรุป

- คลังความรู้ภาควิชา 16 เอกสาร (88 chunks) ทุกย่อหน้ามาจากหน้าเว็บทางการของ RMUTT มี `source_url` จริงทุกไฟล์ และลิงก์ระดับ section (`ที่มา:`) เมื่อเนื้อหามาจากหน้าอื่น
- `search_department_knowledge()` ค้นแบบ hybrid: e5 vector + BM25 คำไทย → cross-encoder reranker ให้คะแนนความเกี่ยวข้อง 0–1 · กันคำถามนอกขอบเขต คำหยาบ และคำถามถึงหน่วยงานอื่น
- Agent (P3) เรียกผ่าน `app.modules.rag` · `ensure_index()` ตอน startup
- ความแม่นยำ (คำถามที่ไม่เคยใช้ปรับค่า 100 ข้อ): hit@1 91%, hit@4 95%, ปฏิเสธนอกขอบเขต 91%
- ข้อจำกัดสำคัญ: reranker ใช้ RAM ~4GB รวม e5 และ ~2.5–3 วินาที/คำถามบน CPU · ถ้าปิด reranker hit@1 ยังได้ 84% แต่ปฏิเสธนอกขอบเขตได้แค่ ~51%

## 3. Acceptance checklist จากแผน

- [x] ≥ 12 ไฟล์ knowledge พร้อม `source_url` จริงทุกไฟล์ — 16 ไฟล์ + `data/knowledge/SOURCES.md` · test `test_front_matter_is_complete_and_real`
- [x] ingest ได้ด้วยคำสั่งเดียว — `python -m app.modules.rag.ingest [--rebuild]` · startup: `ensure_index()` ใน `main.py` (P3) sync index อัตโนมัติ (embed เฉพาะ chunk ที่เปลี่ยน)
- [x] คืน `Source` ครบ field, ลิงก์เปิดได้ — `test_results_follow_contract`, `test_every_chunk_links_to_a_real_page`
- [x] hybrid search ทำงาน — vector + BM25 + RRF + reranker (#24) · hit@4 ≥ 80% ผ่าน (ได้ ~95%)
- [x] คำถามนอกขอบเขตไม่คืนเอกสารมั่ว — ปฏิเสธ 91% ในชุดที่ไม่เคยเห็น · "ภาคไฟฟ้าเรียนอะไร" → `[]`
- [x] ไม่มีข้อมูลที่แต่งขึ้นเอง — ตัวเลขทุกตัวถูกตรวจอัตโนมัติว่าอยู่ในหน้าต้นทาง · เอกสารที่ไม่มีต้นฉบับทางการ (REG-01–13 จากโปรเจกต์เดิม) ไม่ถูกใช้

## 4. สิ่งที่ทำ

| Feature | ทำงานอย่างไร | Entry point | สถานะ |
|---|---|---|---|
| คลังความรู้ | Markdown + front-matter, 1 ไฟล์ต่อหัวข้อ, `ที่มา:` ราย section | `data/knowledge/*.md`, `SOURCES.md` | เสร็จ |
| Chunking | แบ่งตาม `##`, ตัดที่ 800 ตัวอักษร overlap 100 | `rag/chunker.py` | เสร็จ |
| Vector index | e5-small บน Chroma, hash ต่อ chunk → embed เฉพาะที่เปลี่ยน | `rag/ingest.py`, `rag/retriever.py` | เสร็จ |
| Keyword | pythainlp + ศัพท์ภาค → BM25; 3-gram TF-IDF สำหรับโหมดสำรอง | `rag/thai_text.py`, `rag/lexical.py` | เสร็จ |
| Reranker + scope | bge-reranker-v2-m3 (0–1), ตัดที่ 0.005 · กฎหน่วยงานอื่น · คำหยาบ | `rag/reranker.py`, `rag/scope.py`, `rag/guard.py` | เสร็จ |
| Fallback | ไม่มีโมเดล → กรองด้วยคำ+3-gram, เรียงด้วย 3-gram (+vector) · โหลดใหม่ทุก 60 วินาที | `rag/service.py` | เสร็จ |
| FAQ | ถาม-ตอบ 17 ข้อ เรียบเรียงจากเอกสารในคลัง ทุกข้อมี `ที่มา:` | `data/knowledge/faq-prospective.md` | เสร็จ |

Flow หลัก:

```text
คำถาม → [ว่าง/คำหยาบ/หน่วยงานอื่น → []]
      → vector e5 top10 (×2) + BM25 top10 (×1) → RRF
      → reranker 6 อันดับแรก → ตัด < 0.005 → top_k RetrievedChunk (score 0–1)
```

สิ่งที่ **ไม่ได้ทำ**:
- เนื้อหากิจกรรม/ชมรม และจำนวนรับต่อรอบ — ยังไม่พบแหล่งทางการ
- REG-01–13 (ขอจบ, ลาพัก ฯลฯ) — เป็นเอกสารเรียบเรียงของโปรเจกต์เดิม ไม่มี URL ต้นฉบับ
- เทียบกับชุด eval ของ P8 — ตัดออกจากขอบเขต (ใช้ held-out ของ P4 ที่เขียนก่อนวัดแทน)

## 5. โครงสร้างโค้ด

| Path | หน้าที่ |
|---|---|
| `backend/app/modules/rag/service.py` | `search_department_knowledge()`, `ensure_index()`, fallback, retry |
| `backend/app/modules/rag/chunker.py` | front-matter, section, `ที่มา:`, ตัด chunk |
| `backend/app/modules/rag/ingest.py` | Chroma collection `ce_knowledge`, CLI ingest |
| `backend/app/modules/rag/retriever.py` | `vector_search`, `sync_index`, `rrf_merge` |
| `backend/app/modules/rag/thai_text.py` | tokenize ไทย, BM25, word coverage |
| `backend/app/modules/rag/reranker.py` | cross-encoder scoring |
| `backend/app/modules/rag/scope.py` | ภาค/คณะ/มหาวิทยาลัยอื่น |
| `backend/app/modules/rag/guard.py` | `contains_profanity()` |
| `backend/app/modules/rag/lexical.py` | คำพ้อง + 3-gram TF-IDF |
| `backend/app/modules/rag/tests/` | 127 tests (114 + 13 live), ชุดคำถาม `retrieval_cases.py` |

| Function | รับอะไร → คืนอะไร | หมายเหตุ |
|---|---|---|
| `search_department_knowledge(query, top_k=4)` | ข้อความ → `list[RetrievedChunk]` | `[]` = ไม่พบในเอกสารของภาค |
| `ensure_index()` | – → จำนวน chunk | เรียกตอน startup |
| `contains_profanity(text)` | ข้อความ → bool | ให้ agent ตอบคำหยาบอย่างสุภาพ |

การตัดสินใจสำคัญ:
- **reranker แทนการตั้ง threshold บน vector**: cosine ของ e5 ให้คำถามนอกขอบเขต 0.74–0.88 ซ้อนกับคำถามจริง แยกไม่ได้ · cross-encoder ให้คำถามนอกขอบเขตสูงสุด 0.0034
- **กฎหน่วยงานอื่น**: "ภาคไฟฟ้า…" ต่างจาก "ภาคคอม…" คำเดียว reranker ยังให้ 0.16
- **RERANK_CANDIDATES = 6, 256 tokens**: 10 candidates แม่นขึ้น 1 ข้อใน 113 แต่ช้าขึ้น 60%
- **FAQ**: A/B บนคำถามใหม่ 45 ข้อ hit@1 82.2% → 88.9%
- **ไม่แต่งข้อมูล**: ค่าที่แหล่งระบุไม่ตรงกัน (ค่าเทอม 20,000 vs 16,000, หน่วยกิต 141 vs 143) ใส่ทั้งสองค่าพร้อมที่มา

## 6. Contract / Data ที่เปลี่ยน

- Contract: ไม่มี (`Source.score` ใช้เป็นความเกี่ยวข้อง 0–1)
- `data/knowledge/`: 16 เอกสาร + `SOURCES.md`
- Env: `KNOWLEDGE_DIR` (ไม่บังคับ), `RERANK_MODEL` (ไม่บังคับ), `RUN_LIVE_RAG` (test)
- `requirements.txt`: chromadb, sentence-transformers, rank-bm25, pythainlp

## 7. วิธีรันและทดสอบ

```bash
cd backend
pip install -r requirements.txt
python -m app.modules.rag.ingest --rebuild
python -m pytest -q app/modules/rag                   # ไม่โหลดโมเดล (~5 วินาที)
RUN_LIVE_RAG=1 python -m pytest -q app/modules/rag    # โมเดลจริง + วัดความแม่นยำ (~15 นาที)
```

| Test | ผล |
|---|---|
| `pytest -q app/modules/rag` | ✅ 114 passed, 13 skipped (live) |
| `RUN_LIVE_RAG=1 pytest -q app/modules/rag` | ✅ 113 passed, 14 skipped (test ของโหมดไม่มีโมเดล) บน `93348c9` |
| backend ทั้งหมด (`pytest -q`) | ✅ 266 passed, 14 skipped |

## 8. หลักฐาน

ความแม่นยำ (โหมดปกติ, 16 เอกสาร) — held-out 4/5/6 เขียนหลังตั้งค่าเสร็จ วัดครั้งเดียว

| ชุด | hit@1 | hit@4 | ปฏิเสธนอกขอบเขต |
|---|---|---|---|
| held-out 4 (40 + 20) | 95.0% | 100% | 95% |
| held-out 5 (15 + 5) | 86.7% | 93.3% | 80% |
| held-out 6 (45 + 20) | 88.9% | 91.1% | 90% |
| **รวม 100 + 45** | **91%** | **95%** | **91.1%** |

โหมดไม่มี reranker (รวม held-out 4–6): hit@1 84%, hit@4 95%, ปฏิเสธ 51% · ไม่มีโมเดลเลย: 73% / 89% / 51% · เวลา: ~2.5–3 วินาที/คำถาม (reranker), 0.02 วินาที (ไม่มี reranker)

Demo 2 (runbook 09) ผ่าน `POST /api/chat` จริง + Gemini (`gemini-3.1-flash-lite`):

| คำถาม | ผล |
|---|---|
| ภาควิชาวิศวกรรมคอมพิวเตอร์เรียนเกี่ยวกับอะไร | `text`, อ้าง `[1]`, sources 4 (score 0.999 → https://engineer.rmutt.ac.th/com-course/) |
| ภาคไฟฟ้าเรียนอะไร | "ยังไม่พบข้อมูลนี้ในเอกสารของภาค" · sources 0 |
| ค่าเทอมเท่าไหร่ | แสดง 16,000 และ 20,000 พร้อม `[1]` `[3]` และเบอร์ภาค `[2]` — ตัวเลขทุกตัวตรงกับ chunk ที่อ้าง |
| เรียนจบได้วุฒิอะไร | วศ.บ. (วิศวกรรมคอมพิวเตอร์) / B.Eng. (Computer Engineering) `[1]` |

## 9. ปัญหาที่เจอและวิธีแก้

| ปัญหา | สาเหตุ | แก้อย่างไร |
|---|---|---|
| REG-01–13 ในโปรเจกต์เดิมดูเหมือนเอกสารทางการ | metadata: สร้างจาก browser print พร้อมกัน 13 ไฟล์, ข้อความ "เรียบเรียง" | ไม่ใช้ บันทึกเป็น blocker |
| `\w` ของ Python ตัดคำไทย | สระ/วรรณยุกต์ไม่ใช่ `\w` | เพิ่มช่วง U+0E00–U+0E7F |
| guard จับ "ผู้เชี่ยวชาญ" เป็นคำหยาบ | substring "เชี่ย" | allowlist + test |
| ตัวกรอง 3-gram รั่วเมื่อเอกสารเพิ่ม | คำทั่วไปตรงกับคลังที่ใหญ่ขึ้น | reranker + กฎหน่วยงานอื่น |
| PR #20 เปิดทั้งที่มี test ตก | `pytest | tail` กลบ exit code | เปลี่ยนเป็น Draft ทันที, สคริปต์ตรวจก่อน PR ที่หยุดเมื่อพลาด |
| live test ไม่ผ่านครั้งหนึ่ง ทำซ้ำไม่ได้ | ทศนิยมบน CPU ต่างกันเล็กน้อยเมื่อเครื่องทำงานหนัก | เกณฑ์ live ยอมคลาด 1 ข้อ, รัน live 2 รอบติดกันก่อน PR |

## 10. ข้อจำกัด / สิ่งที่ควรทำต่อ

- เครื่อง demo ต้องมี RAM พอสำหรับ reranker (~4GB รวม e5) ไม่งั้นคำถามนอกขอบเขตจะหลุดเข้ามาราวครึ่งหนึ่ง (agent ต้องกรองเอง)
- ข้อมูลที่ยังขาด: กิจกรรม/ชมรม, จำนวนรับ, ขั้นตอนงานทะเบียน (REG) จากประกาศต้นฉบับ
- ชุดทดสอบทั้งหมดเขียนโดย P4 (ไม่มีชุดจากคนนอก) ตัวเลขกับคำถามของผู้ใช้จริงอาจต่ำกว่านี้
- ตรวจหน้าเว็บต้นทางซ้ำก่อน demo (ค่าเทอม/กำหนดการอาจเปลี่ยน)

## 11. Handoff

- P3: เรียก `ensure_index()` ตอน startup (ทำแล้ว) · `[]` → "ไม่พบข้อมูลในเอกสารของภาค" · ใช้ `contains_profanity()` ได้ · `USE_RERANKER = False` ถ้า RAM ไม่พอ
- P1/P6: `Source.url` ลิงก์ไปหน้าที่มีข้อความจริง, `score` 0–1
- P8: ชุดคำถาม `backend/app/modules/rag/tests/retrieval_cases.py` ใช้เทียบได้
- P1/P3: `JWT_SECRET` ใน `.env` ต้องไม่ใช่ค่า default ไม่งั้น backend ไม่ start
- P3 (จาก Demo 2): "หลักสูตรมีกี่หน่วยกิต" ถูกส่งไป curriculum cards ที่ไม่บอกจำนวนหน่วยกิต (RAG มีคำตอบ: 141 ใน `program-structure`, 143 ใน `ce-overview`, ทั้งสองค่าใน `faq-prospective`) · คำตอบ intent general ชวนถามเรื่อง "กิจกรรมภายในภาควิชา" ซึ่งยังไม่มีข้อมูล
- จุดที่ควรดู: `service.py` (flow + fallback), `scope.py` (รายชื่อหน่วยงาน), `SOURCES.md`

## 12. ยืนยัน

- [x] โค้ดทั้งหมด merge เข้า `develop` แล้ว (#2, #16, #20, #24, #36, #38, #40)
- [x] ไม่มี secret / ลายน้ำ AI / mock ใน flow จริง
- [ ] ฉันอธิบายโค้ดทุกส่วนในรายงานนี้ได้เอง
