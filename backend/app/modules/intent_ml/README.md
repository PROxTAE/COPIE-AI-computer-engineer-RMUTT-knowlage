# intent_ml — Local Intent Classifier (ML)

| | |
|---|---|
| เจ้าของ | **P7** |
| แผนงาน | [`07_SUGGESTIONS_LOCAL_INTENT_ML.md`](../../../../IMPLEMENTATION_PLANS/07_SUGGESTIONS_LOCAL_INTENT_ML.md) |
| Branch prefix | ดู `IMPLEMENTATION_PLANS/00_GIT_DELIVERY_RULES.md` §2 |

## หน้าที่

โมเดล TF-IDF (char n-gram) + Logistic Regression ที่รันในเครื่อง จำแนก intent ของคำถาม — ส่วน "Local AI Model" ใน diagram (optional, เปิดด้วย `USE_LOCAL_INTENT=true`)

## โครงไฟล์ที่จะสร้าง

```text
intent_ml/
├─ __init__.py       # predict_intent
├─ dataset.jsonl
├─ train.py          # python -m app.modules.intent_ml.train
├─ predict.py
├─ model.joblib
├─ report/           # metrics.json, confusion_matrix.png
└─ tests/
```

## Public API (สิ่งที่ module อื่นเรียกใช้ได้)

`predict_intent(text) -> tuple[str, float]`

## ใช้ของ module อื่นได้จาก

`app.schemas.contract`

> ชื่อโฟลเดอร์ใช้ `intent_ml` (Python import ใช้ `-` ไม่ได้) แต่ branch prefix คือ `intent-ml/`
