# mascot — COPIE 2.5D

| | |
|---|---|
| เจ้าของ | **P1** |
| แผนงาน | [`01_FRONTEND_CORE_MASCOT.md`](../../../../IMPLEMENTATION_PLANS/01_FRONTEND_CORE_MASCOT.md) |
| Branch prefix | ดู `IMPLEMENTATION_PLANS/00_GIT_DELIVERY_RULES.md` §2 |

## หน้าที่

แสดง COPIE แบบ **2.5D** — ภาพโปร่งใส 1 ภาพต่อสถานะ (`/copie-ui/mascot/*.webp`, sync จาก `assets/web-ui/mascot/states/`) พร้อม layout `center` / `rail` / `hidden` และ motion จาก kit (`copie-mascot-breathe`)

## โครงไฟล์

```text
mascot/
├─ index.ts          # public exports
├─ states.ts         # CopieMascotState → ภาพ
├─ CopieMascot.tsx   # 2.5D (ใช้ตัวนี้เป็นหลัก)
└─ Copie.tsx         # 3D จาก GLB (public/models/) — ทางเลือก รอทีมตัดสินใจ, ดูได้ที่ /mascot-demo
```

## Public API (สิ่งที่ module อื่นเรียกใช้ได้)

- `<CopieMascot state="thinking" layout="rail" />` — state: `welcome`, `idle`, `listening`, `thinking`, `responding`, `success`, `no-answer`, `skill-guide`
- `COPIE_IMAGES`, type `CopieMascotState`
- (3D) `<Copie state />`, type `CopieState` — งานทดลองระหว่างรอทีมตัดสินใจ; flow หลักใช้ 2.5D

ต้องวางไว้ใน element ที่มี class `copie-ui` เพื่อให้ขนาดและ animation ของ kit ทำงาน

## ใช้ของ module อื่นได้จาก

ไม่มี — module นี้ไม่ import module อื่น
