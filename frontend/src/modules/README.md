# Frontend modules

แอป Next.js **ตัวเดียว** แบ่งโค้ดเป็น module ตามผู้รับผิดชอบ — build และ deploy รวมกันเป็นเว็บเดียว

| Module | เจ้าของ | หน้าที่ |
|---|---|---|
| [`core/`](core/README.md) | P1 | Design system, workspace `/chat`, api client, chat store |
| [`mascot/`](mascot/README.md) | P1 | 3D COPIE + animation |
| [`user/`](user/README.md) | P2 | Login, onboarding, history, feedback |
| [`renderer/`](renderer/README.md) | P6 | Dynamic response UI + mock + `/dev` |
| [`suggest/`](suggest/README.md) | P7 | Suggested questions |
| [`export/`](export/README.md) | P8 | Copy / Export |

## กติกา module boundary

1. **แก้ได้เฉพาะ module ของตัวเอง** — ต้องแก้ของคนอื่นให้คุยกับเจ้าของหรือเปิด Issue
2. **import ข้าม module ผ่าน `index.ts` เท่านั้น** — `import { ResponseRenderer } from "@/modules/renderer"` ✅ · `from "@/modules/renderer/components/CourseTable"` ❌ (ESLint จะแจ้ง error)
3. ไฟล์ภายใน module เดียวกัน import กันแบบ relative (`./components/CourseTable`)
4. Type ที่ใช้ร่วมกันมาจาก `@/types/contract` เท่านั้น — ห้ามสร้าง type ของ API ซ้ำ
5. หน้าใน `src/app/**` เป็นแค่ "ประตู" — ใส่ logic ใน module แล้ว page import มาแสดง
