# COPIE Backend

Python 3.11 · FastAPI — แอปเดียว แบ่งโค้ดตาม module ใน `app/modules/`

```bash
python -m venv .venv
source .venv/Scripts/activate        # Windows Git Bash  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000     # http://localhost:8000/api/health
python -m pytest -q
```

```text
app/
├─ main.py             # FastAPI app + include routers (P3)
├─ core/               # config (P3)
├─ schemas/contract.py 🔒 shared contract
└─ modules/            # โค้ดจริงแยกตามเจ้าของ → ดู app/modules/README.md
storage/               # app.db, chroma/ (gitignored, สร้างตอนรัน)
```
