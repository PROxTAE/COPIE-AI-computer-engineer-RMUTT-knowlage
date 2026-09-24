# COPIE Frontend

Next.js 16 (App Router) · React 19 · TypeScript · Tailwind CSS v4 — แอปเดียว แบ่งโค้ดตาม module ใน `src/modules/`

```bash
npm ci          # ติดตั้งตาม package-lock.json (ห้ามใช้ npm install ถ้าไม่ได้เพิ่ม library)
npm run dev     # http://localhost:3000 (เรียก /api/* ผ่าน rewrite ไป http://localhost:8000)
npm run lint
npm run build
```

```text
src/
├─ app/            # routes (บางที่สุด) — /, /chat, /login, /onboarding, /dev
├─ modules/        # โค้ดจริงแยกตามเจ้าของ → ดู src/modules/README.md
└─ types/contract.ts   🔒 shared contract (แก้ผ่าน contract/* PR เท่านั้น)
```

เพิ่ม library ใหม่: ทำใน PR ของตัวเองและให้ P1 approve (`package.json` + `package-lock.json` ต้องมาคู่กัน)
