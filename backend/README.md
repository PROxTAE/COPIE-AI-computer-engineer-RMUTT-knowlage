# COPIE Backend

Python 3.11 · FastAPI — แอปเดียว แบ่งโค้ดตาม module ใน `app/modules/`

```bash
python -m venv .venv
source .venv/Scripts/activate        # Windows Git Bash  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000     # http://localhost:8000/api/health
python -m pytest -q
```

### Docker (Day 4+)

```bash
docker compose up --build api        # backend อย่างเดียว → http://localhost:8000/api/health
docker compose up --build            # web + api (ต้องมี frontend/Dockerfile ของ P1)
docker compose logs -f api           # ดู log: intent, latency ของ LLM, knowledge index
docker compose down                  # หยุด (ข้อมูลใน backend/storage ยังอยู่)
```

- ค่าใน `.env` ถูกส่งเข้า container `api` · `data/` mount แบบ read-only ที่ `/app/data`
- `backend/storage/` (app.db, chroma/) mount จากเครื่อง ข้อมูลไม่หายตอน restart

```text
app/
├─ main.py             # FastAPI app + include routers (P3)
├─ core/               # config (P3)
├─ schemas/contract.py 🔒 shared contract
└─ modules/            # โค้ดจริงแยกตามเจ้าของ → ดู app/modules/README.md
storage/               # app.db, chroma/ (gitignored, สร้างตอนรัน)
```
