# P7 — Suggested Questions + Local Intent Classifier (ML)

## Mission

1. **Suggested Questions** — ปุ่มคำถามแนะนำที่เปลี่ยนตามประเภทผู้ใช้และชั้นปี ช่วยให้ผู้ใช้เริ่มคุยได้ทันที
2. **Local Intent Classifier** — โมเดล ML ที่รันในเครื่อง (TF-IDF + Logistic Regression) จำแนก intent ของคำถาม เป็นส่วน **"Local AI Model"** ใน diagram ของอาจารย์ และเป็นผลงาน ML ที่นำเสนอได้ในวิชา Advanced ML

**ความสำคัญ:** ทั้งสองงาน **ไม่เป็น dependency ของ Core** (ถอดออกได้ระบบยังทำงาน) แต่เพิ่มความสะดวกใน Demo และทำให้ระบบมีส่วน ML ของตัวเอง ไม่ได้พึ่ง LLM อย่างเดียว

## Ownership

แก้ได้โดยตรง
- `frontend/src/modules/suggest/**`
- `backend/app/modules/intent_ml/**` (รวม tests)

ต้องขอ review เพิ่ม
- `requirements.txt` (เพิ่ม `scikit-learn`, `joblib`) — P3
- การต่อเข้า router (`agent/intent_router.py` เป็นของ P3 — P3 เป็นคนแก้ เราส่ง function ให้)

Dependency

| รับจาก | อะไร | เมื่อไหร่ |
|---|---|---|
| P8 | `data/eval/questions.jsonl` (60 ข้อ มี label) | Day 2 12:00 |
| P1 | ตำแหน่ง/สไตล์ใน Workspace, `chatStore.send` | Day 2 |
| P2 | `userStore.user.user_type`, `study_year` | Day 2 |

ส่งให้: **P1** `SuggestedPrompts` · **P3** `predict_intent()` (Day 3 PM)

## Stack

- Frontend: React + Tailwind, `ui/` ของ P1
- ML: `scikit-learn` (`TfidfVectorizer`, `LogisticRegression`, `classification_report`, `confusion_matrix`), `joblib`, `matplotlib` (รูปสำหรับรายงาน)

## Target folder structure

```text
frontend/src/modules/suggest/     # 👤 P7
├─ index.ts              # public: SuggestedPrompts, getSuggestedPrompts
├─ suggested-prompts.ts
└─ SuggestedPrompts.tsx

backend/app/modules/intent_ml/    # 👤 P7 (branch prefix: intent-ml/)
├─ __init__.py           # public: predict_intent
├─ dataset.jsonl         # {"text": ..., "intent": ...} ~240 แถว
├─ train.py              # python -m app.modules.intent_ml.train
├─ predict.py            # predict_intent(text) -> (intent, confidence)
├─ model.joblib          # commit ได้ (ไฟล์เล็ก < 2MB)
├─ report/               # metrics.json, confusion_matrix.png
└─ tests/                # test_intent_ml.py
```

## Design details

### Suggested prompts

```ts
type PromptSet = { label: string; text: string }[];
export const SUGGESTED_PROMPTS: {
  prospective: PromptSet;
  current_student: Record<1 | 2 | 3 | 4, PromptSet>;
  near_graduate: PromptSet;
  default: PromptSet;
};
export function getSuggestedPrompts(userType?: UserType | null, studyYear?: number | null): PromptSet;
```

| กลุ่ม | ตัวอย่าง |
|---|---|
| prospective | ภาคคอมเรียนเกี่ยวกับอะไร? · ปี 1 เรียนอะไรบ้าง? · รับสมัครรอบไหนบ้าง? · จบแล้วทำงานอะไรได้? |
| current_student ปี 2 | ปี 2 เทอม 1 เรียนอะไร? · วิชา Data Structure เรียนอะไร? · วิเคราะห์ skill ของฉัน |
| near_graduate | สรุป skill ของฉัน · สหกิจศึกษาทำอย่างไร? · หลักสูตรมีกี่หน่วยกิต? |

- ทุกคำถามต้อง **ตอบได้จริง** โดยระบบ (ตรวจกับ P3/P4/P5 ก่อน merge)
- `SuggestedPrompts` props: `{ userType, studyYear, onPick(text), compact?: boolean }` — แสดงเต็มตอนยังไม่มีบทสนทนา, `compact` แถบเลื่อนแนวนอนเมื่อคุยแล้ว

### Intent classifier

- Label 6 ค่า = `Intent` ใน contract
- Dataset: ประโยคจาก eval set ของ P8 **ห้ามใช้ข้อเดียวกันทั้ง train และ test** — แยก eval set ของ P8 เป็น test set ทั้งหมด แล้วเขียนประโยค train ใหม่ ~40/intent (ภาษาพูด, สะกดผิด, ไทยปนอังกฤษ)
- Model: `TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), min_df=1, sublinear_tf=True)` + `LogisticRegression(max_iter=1000, class_weight="balanced")` ใน `Pipeline`
  - ใช้ character n-gram เพราะภาษาไทยไม่เว้นวรรค — ไม่ต้องตัดคำ
- `predict_intent(text)` → `(label, max predict_proba)` · โหลดโมเดลครั้งเดียว (`lru_cache`)
- Router ของ P3 ใช้ผล ML เมื่อ `USE_LOCAL_INTENT=true` และ confidence ≥ 0.80 ไม่งั้นใช้ LLM
- เทียบ **ML vs LLM router** บน test set: accuracy, macro-F1, latency เฉลี่ย → ใส่ในสไลด์

## Implementation steps

### Phase 1 — Suggested prompts (Day 1 PM)
1. `suggested-prompts.ts` + `SuggestedPrompts` + แสดงใน `/dev` (ขอ P6 เพิ่ม section หรือทำหน้า demo ในไฟล์ตัวเอง)

Exit: **M1**

### Phase 2 — Integration + dataset (Day 2)
1. AM: ต่อเข้า `/chat` ร่วมกับ P1 (`onPick` → `chatStore.send`)
2. PM: เขียน `dataset.jsonl` ~240 แถว (หลังได้ eval set ของ P8)

Exit: **M2**

### Phase 3 — Train + predict (Day 3)
1. AM: `train.py` — train บน dataset, ประเมินบน eval set ของ P8, บันทึก `model.joblib` + `report/metrics.json` + `confusion_matrix.png`
2. PM: `predict.py` + `test_intent_ml.py`, ส่ง function ให้ P3

Exit: **M3** — accuracy บน test set ≥ 80%

### Phase 4 — Router integration + comparison (Day 4)
1. ทำงานกับ P3 เปิด flag, วัด accuracy/latency ของ ML vs LLM vs hybrid (ML ก่อน, ไม่มั่นใจ → LLM)
2. เพิ่มข้อมูล train จากคำถามที่ผิด (ห้ามเอา test set มา train)

Exit: **M4**

### Phase 5 — QA + slides (Day 5)
- ช่วย P8 ทดสอบ, ทำสไลด์ส่วน ML (dataset, model, ผลเทียบ, confusion matrix)

## Required tests

| ประเภท | Cases |
|---|---|
| Unit | `predict_intent` คืน label ที่อยู่ใน 6 ค่า + confidence 0–1, ข้อความว่าง → `general` + 0.0 |
| Model | accuracy test set ≥ 80%, บันทึก report ทุกครั้งที่ train |
| Frontend | prompts ต่างกันตาม user_type/ชั้นปี, กดแล้วส่งข้อความจริง |

## Acceptance checklist

- [ ] ปุ่มคำถามแนะนำเปลี่ยนตามผู้ใช้ และทุกคำถามตอบได้จริง
- [ ] ถอด `SuggestedPrompts` ออกแล้วหน้า `/chat` ยังทำงาน
- [ ] โมเดล train ซ้ำได้ด้วยคำสั่งเดียว ผลลัพธ์ reproducible (`random_state=42`)
- [ ] train/test แยกกันจริง
- [ ] มีตารางเทียบ ML vs LLM router
- [ ] ปิด `USE_LOCAL_INTENT` แล้วระบบยังทำงานปกติ

## Branch / PR breakdown

1. `suggest/prompt-chips`
2. `suggest/workspace-integration`
3. `intent-ml/dataset`
4. `intent-ml/tfidf-classifier`
5. `intent-ml/predict-api`
6. `intent-ml/router-integration` (ส่วนที่แก้ใน router ให้ P3 เป็นคนทำ/approve)

## Completion report requirements

สร้าง `docs/handoffs/P7-suggest-intent-ml.md` ระบุเพิ่ม: รายการ prompt ทุกกลุ่ม, สถิติ dataset ต่อ intent, hyperparameters, classification report, confusion matrix, ตาราง ML vs LLM (accuracy/F1/latency), ข้อจำกัดของโมเดล
