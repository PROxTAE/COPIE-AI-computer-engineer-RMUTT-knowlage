# 📋 COPIE — Deployment & Tech Stack Specification

เอกสารสรุปสถาปัตยกรรมระบบ, Tech Stack และข้อกำหนดสำหรับการนำโปรเจกต์ **COPIE** ไป Deploy บน Cloud / VPS สำหรับ System Administrator หรือ Hosting Provider

---

## 1. ภาพรวมระบบ (System Architecture)

ระบบเป็น **AI-Powered Web Application (Chat & RAG System)** ทำงานในรูปแบบ Multi-container Orchestration ด้วย **Docker Compose** แบ่งเป็น 2 Services หลัก:

```
                      [ Internet / User ]
                                │
                                ▼  Port 80 / 443 (HTTPS)
                    ┌─────────────────────────┐
                    │ Reverse Proxy (Nginx)   │
                    └───────────┬─────────────┘
                                │
        ┌───────────────────────┴───────────────────────┐
        ▼ Port 3000                                     ▼ Port 8000
┌─────────────────────────┐                   ┌─────────────────────────┐
│     web (Frontend)      │ ───(API Calls)──> │      api (Backend)      │
│   Next.js / Node 22     │                   │     FastAPI / Py 3.11   │
└─────────────────────────┘                   └───────────┬─────────────┘
                                                          │
                                     ┌────────────────────┴────────────────────┐
                                     ▼                                         ▼
                         ┌───────────────────────┐                 ┌───────────────────────┐
                         │   SQLite (app.db)     │                 │   ChromaDB (Vector)   │
                         │  ./backend/storage    │                 │  ./backend/storage    │
                         └───────────────────────┘                 └───────────────────────┘
```

---

## 2. รายละเอียด Tech Stack

### 🔹 2.1 Frontend Service (`web`)
* **Framework:** Next.js (React / TypeScript)
* **Runtime:** Node.js 22 (Alpine)
* **Build Type:** Standalone Server (`node server.js`)
* **Internal Port:** `3000`
* **Healthcheck / เข้าถึง:** พอร์ต `3000` (รอรับ Reverse Proxy จากภายนอก)

### 🔹 2.2 Backend Service (`api`)
* **Framework:** FastAPI, Uvicorn
* **Runtime:** Python 3.11 (Slim)
* **Database (Relational):** SQLite (ผ่าน SQLModel / SQLAlchemy)
* **Vector Database:** ChromaDB (Local persistent directory)
* **NLP & Embeddings:**
  * โมเดล Local Embedding: `sentence-transformers` (โหลดโมเดล `intfloat/multilingual-e5-small` ลง Memory)
  * Tokenizer / ประมวลผลภาษาไทย: `pythainlp`
* **LLM Engine:** Google Gemini API (เชื่อมต่อผ่าน SDK `google-genai`)
* **Internal Port:** `8000`

---

## 3. ข้อกำหนดทรัพยากรเซิร์ฟเวอร์ (Server Requirements)

* **Operating System:** Ubuntu 22.04 LTS หรือ 24.04 LTS (64-bit)
* **CPU:** แนะนำ **2 vCPU** ขึ้นไป
* **Memory (RAM):**
  * **ขั้นต่ำ:** 4 GB
  * **แนะนำ (Optimal):** **8 GB** *(เนื่องจากระบบมีการโหลดโมเดล PyTorch / Embedding ลง RAM)*
* **Storage:** SSD / NVMe ขนาด **30–50 GB** ขึ้นไป
* **Software ที่ต้องมีบน Server:**
  * `git`
  * `docker` (เวอร์ชัน 24.x ขึ้นไป)
  * `docker compose` (Docker Compose Plugin v2)
  * `nginx` หรือ `caddy` (สำหรับทำ Reverse Proxy และ SSL)

---

## 4. โฟลเดอร์จัดเก็บข้อมูลถาวร (Persistent Volumes)

โปรเจกต์ต้องการ Volume Mount จาก Host ดังนี้ (ระบุไว้ใน `docker-compose.yml` แล้ว):

| Host Path | Container Path | สิทธิ์ | คำอธิบาย |
| :--- | :--- | :--- | :--- |
| `./backend/storage` | `/app/backend/storage` | `rw` | เก็บฐานข้อมูล `app.db` (SQLite) และโฟลเดอร์เวกเตอร์ `chroma/` |
| `./data` | `/app/data` | `ro` | ข้อมูลหลักสูตร, Knowledge base และ Assessment (อ่านอย่างเดียว) |

---

## 5. ตัวแปรสภาพแวดล้อม (Environment Variables)

ไฟล์ตั้งค่าอยู่ที่ `.env` (คัดลอกจาก `.env.example`):

```bash
# ---- Backend Configuration ----
JWT_SECRET=your-secure-jwt-secret-key
GOOGLE_CLIENT_ID=your-google-oauth-client-id.apps.googleusercontent.com
DEV_AUTH=false
GEMINI_API_KEY=your-gemini-api-key
LLM_MODEL=gemini-3.1-flash-lite
LLM_TIMEOUT_S=20
DATABASE_URL=sqlite:///./storage/app.db
CHROMA_DIR=./storage/chroma
EMBEDDING_MODEL=intfloat/multilingual-e5-small
RAG_MIN_SCORE=0.35
USE_LOCAL_INTENT=false

# ---- Frontend Configuration ----
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-oauth-client-id.apps.googleusercontent.com
API_URL=http://api:8000
```

---

## 6. คำสั่งในการ Deploy (Deployment Commands)

```bash
# 1. โคลนโปรเจกต์
git clone <REPOSITORY_URL>
cd COPIE

# 2. คัดลอกและแก้ไขค่า Environment Variables
cp .env.example .env
nano .env

# 3. สั่งรัน Containers ทั้งหมด
docker compose up -d --build

# 4. ตรวจสอบสถานะการทำงาน
docker compose ps

# 5. ตรวจสอบ Log หากมีปัญหา
docker compose logs -f
```

---

## 7. การตั้งค่า Reverse Proxy & SSL (สิ่งที่ Admin ต้อง Configure เพิ่ม)

แนะนำให้ตั้งค่า **Nginx** หรือ **Caddy** เพื่อรับ Request พอร์ต 80/443 และ Forward ไปยัง Frontend พอร์ต `3000`:

### ตัวอย่าง Nginx Configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```
*(จากนั้นใช้ `certbot --nginx -d yourdomain.com` เพื่อเปิดใช้งาน HTTPS)*
