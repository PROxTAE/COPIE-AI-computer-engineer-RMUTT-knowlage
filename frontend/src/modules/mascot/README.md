# mascot — 3D COPIE

| | |
|---|---|
| เจ้าของ | **P1** |
| แผนงาน | [`01_FRONTEND_CORE_3D_MASCOT.md`](../../../../IMPLEMENTATION_PLANS/01_FRONTEND_CORE_3D_MASCOT.md) |
| Branch prefix | ดู `IMPLEMENTATION_PLANS/00_GIT_DELIVERY_RULES.md` §2 |

## หน้าที่

Reference design: [`assets/mascot/copie-computer-concept-v2.png`](../../../../assets/mascot/copie-computer-concept-v2.png)

ฉาก 3D และตัว COPIE (React Three Fiber) พร้อม animation 5 state: idle, listening, thinking, responding, success และ fallback 2D เมื่อไม่มี WebGL

## โครงไฟล์ที่จะสร้าง

```text
mascot/
├─ index.ts
├─ CopieScene.tsx       # <Canvas>, camera, lights, Environment, ContactShadows
├─ CopieModel.tsx       # COPIE จาก primitive
├─ useCopieAnimation.ts
└─ CopieFallback.tsx
```

## Public API (สิ่งที่ module อื่นเรียกใช้ได้)

`<Copie state=... />` (โหลดด้วย `next/dynamic`, `ssr: false`), type `CopieState`

## ใช้ของ module อื่นได้จาก

`@/modules/core` (ui เท่านั้น)
