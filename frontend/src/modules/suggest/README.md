# suggest — Suggested Questions

| | |
|---|---|
| เจ้าของ | **P7** |
| แผนงาน | [`07_SUGGESTIONS_LOCAL_INTENT_ML.md`](../../../../IMPLEMENTATION_PLANS/07_SUGGESTIONS_LOCAL_INTENT_ML.md) |
| Branch prefix | ดู `IMPLEMENTATION_PLANS/00_GIT_DELIVERY_RULES.md` §2 |

## หน้าที่

ปุ่มคำถามแนะนำที่เปลี่ยนตาม `user_type` และชั้นปี (optional — ถอดออกได้โดยระบบไม่พัง)

## โครงไฟล์ที่จะสร้าง

```text
suggest/
├─ index.ts
├─ suggested-prompts.ts
└─ SuggestedPrompts.tsx
```

## Public API (สิ่งที่ module อื่นเรียกใช้ได้)

`<SuggestedPrompts userType studyYear onAsk compact />`, `getSuggestedPrompts()`

## ใช้ของ module อื่นได้จาก

`@/modules/core` (ui เท่านั้น), `@/types/contract`
