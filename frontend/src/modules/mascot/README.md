# mascot — COPIE 2.5D

| | |
|---|---|
| เจ้าของ | **P1** |
| แผนงาน | [`01_FRONTEND_CORE_MASCOT.md`](../../../../IMPLEMENTATION_PLANS/01_FRONTEND_CORE_MASCOT.md) |
| Branch prefix | ดู `IMPLEMENTATION_PLANS/00_GIT_DELIVERY_RULES.md` §2 |

## หน้าที่

แสดง COPIE แบบ **2.5D** — ภาพโปร่งใส 1 ภาพต่อสถานะ ต่อโหมด (`normal` / `devil` / `developer`, sync จาก `assets/web-ui/mascot/states/` และ `assets/web-ui/mascot/modes/<mode>/states/`) พร้อม layout `center` / `rail` / `hidden` ภาพ 8 สถานะของโหมดปัจจุบันโหลดล่วงหน้าและซ้อนกันเพื่อ crossfade 200ms โดยไม่กระพริบ เมื่อเปลี่ยนโหมด ภาพโหมดเดิมยังแสดงจนภาพโหมดใหม่โหลดเสร็จ (ไม่โหลดครบ 24 ภาพพร้อมกัน)

`MascotStage` ทำให้ COPIE ดูมีชีวิตโดยไม่ต้องมีโมเดล 3D:

- **Parallax 2.5D** — halo (ชั้นหลัง) เลื่อนสวนทาง, COPIE เอียง `rotateX/Y` ตามเมาส์ทั้งหน้า, glyph ลอยชั้นหน้าเลื่อนมากที่สุด, เงาที่พื้นหายใจตามจังหวะ breathe; ใช้ motion values จึงไม่ re-render React ตอนขยับเมาส์
- **เล่นกับ COPIE ได้** — hover ขยายเล็กน้อย, กด = ยุบแล้วเด้ง (squash & stretch), แตะ = กระโดด + อนุภาคตามโหมด + คำพูดในบับเบิล, แตะรัว 5 ครั้ง = หมุนตัว, ลูบไปมาบนตัว = หัวใจลอย, ปล่อยไว้นาน ๆ = มองไปรอบ ๆ และให้คำใบ้เป็นครั้งคราว
- **ท่าตามสถานะ** — `listening` โน้มตัวมาทางช่องพิมพ์, `thinking` โยกตัว + จุดโคจรรอบหัว, `success` กระโดด + พลุ, `no-answer` ส่ายตัว
- **เปลี่ยนโหมด** — หมุนตัวแปลงร่าง + วงคลื่นกระแทก + อนุภาคสีโหมดใหม่ + ประโยคแนะนำโหมด
- ใช้คีย์บอร์ด Enter/Space ได้, มี focus ring, เคารพ `prefers-reduced-motion` (ปิด tracking/เด้ง/อนุภาค เหลือบับเบิล), หยุด tracking เมื่อหน้าถูกซ่อนหรือ stage ไม่อยู่ในจอ
- คำพูดทั้งหมดอยู่ใน `personality.ts` และ**ไม่ถูกส่งไป server หรือบันทึกในประวัติแชต**

## โครงไฟล์

```text
mascot/
├─ index.ts            # public exports
├─ states.ts           # (InteractionMode, CopieMascotState) → ภาพ
├─ CopieMascot.tsx     # กองภาพ 2.5D + crossfade ข้ามท่าและโหมด
├─ MascotStage.tsx     # stage แบบ interactive รอบ CopieMascot
├─ MascotDock.tsx      # mini COPIE ที่มุมจอ ตอนซ่อนมาสคอต (ลากย้ายมุมได้)
├─ personality.ts      # คำพูดและ glyph อนุภาคของแต่ละโหมด
├─ modeContext.ts      # MascotModeProvider — CopieMascot ในหน้าแชตใช้โหมดเดียวกันอัตโนมัติ
└─ mascot-stage.css    # สไตล์ stage (import ใน app/globals.css)
```

## Public API (สิ่งที่ module อื่นเรียกใช้ได้)

- `<MascotStage state="thinking" mode="devil" layout="rail" imageClassName="..." haloClassName="..." chatter />`
- `<CopieMascot state="thinking" mode="developer" layout="rail" />` — state: `welcome`, `idle`, `listening`, `thinking`, `responding`, `success`, `no-answer`, `skill-guide`; ไม่ส่ง `mode` จะใช้ค่าจาก `MascotModeProvider` (ค่าเริ่มต้น `normal`)
- `animated={false}` ใช้เฉพาะภาพนิ่งใน theme preview
- `copieImage(mode, state)`, `COPIE_IMAGES` (ชุดปกติ), `COPIE_STATES`, `INTERACTION_MODES`, types `CopieMascotState`, `InteractionMode`
- `MascotModeProvider`, `useMascotMode()`
- `<MascotDock state onRestore guardKey />` — ไอคอน COPIE กลมที่มุมจอ แตะเพื่อเรียกมาสคอตกลับ ลากแล้วจะ snap ไปมุมที่ใกล้ที่สุดและจำมุมไว้ (`localStorage`) ใส่ `data-dock-guard="top"` หรือ `"bottom"` ให้ element ที่ห้ามบัง (header, แถบนำทาง, ช่องพิมพ์) แล้ว dock จะหลบให้เอง

ต้องวางไว้ใน element ที่มี class `copie-ui` เพื่อให้ขนาดและ animation ของ kit ทำงาน สีของ stage มาจาก token ใน `core/theme/modes.css`

## ใช้ของ module อื่นได้จาก

ไม่มี — module นี้ไม่ import module อื่น (ใช้แค่ type `InteractionMode` จาก `@/types/contract`)
