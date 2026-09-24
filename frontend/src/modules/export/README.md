# export — Copy / Export

| | |
|---|---|
| เจ้าของ | **P8** |
| แผนงาน | [`08_EXPORT_QA_EVAL.md`](../../../../IMPLEMENTATION_PLANS/08_EXPORT_QA_EVAL.md) |
| Branch prefix | ดู `IMPLEMENTATION_PLANS/00_GIT_DELIVERY_RULES.md` §2 |

## หน้าที่

ปุ่ม Copy คำตอบ และ Export บทสนทนาเป็น TXT / JSON (optional — ถอดออกได้โดยระบบไม่พัง)

## โครงไฟล์ที่จะสร้าง

```text
export/
├─ index.ts
├─ CopyButton.tsx
├─ ExportMenu.tsx
└─ formatters.ts
```

## Public API (สิ่งที่ module อื่นเรียกใช้ได้)

`<CopyButton response />`, `<ExportMenu messages title />`

## ใช้ของ module อื่นได้จาก

`@/modules/core` (ui เท่านั้น), `@/types/contract`
