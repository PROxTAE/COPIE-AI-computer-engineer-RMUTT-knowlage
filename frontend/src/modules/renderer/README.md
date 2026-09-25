# renderer — Dynamic Response Renderer

| | |
|---|---|
| เจ้าของ | **P6** |
| แผนงาน | [`06_DYNAMIC_RENDERER.md`](../../../../IMPLEMENTATION_PLANS/06_DYNAMIC_RENDERER.md) |
| Branch prefix | ดู `IMPLEMENTATION_PLANS/00_GIT_DELIVERY_RULES.md` §2 |

## หน้าที่

แปลง `AgentResponse` ทุก `response_type` เป็น UI (Text, CourseTable, InfoCards, AssessmentForm, SkillRadar, SourceViewer, ActionChips, Error) และเป็นเจ้าของ mock fixtures + หน้า `/dev`

## โครงไฟล์

```text
renderer/
├─ index.ts                 # public API
├─ ResponseRenderer.tsx     # switch(response_type) + exhaustive never check
├─ DevPlayground.tsx        # หน้า /dev
├─ components/              # TextResponse, Markdown, SourceViewer, CourseTable, InfoCards,
│                           # AssessmentForm, SkillRadar, ActionChips, ErrorResponse, skillLabels.ts
└─ mock/                    # fixtures ของทุก response_type (ใช้ได้เฉพาะ /dev และ test)
```

คู่มือใช้งานฉบับเต็ม: [`docs/handoffs/P6-dynamic-renderer.md`](../../../../docs/handoffs/P6-dynamic-renderer.md)

## Public API (สิ่งที่ module อื่นเรียกใช้ได้)

`<ResponseRenderer response onAsk onSubmitAssessment disabled />`, `DevPlayground`, `MOCKS`

## ใช้ของ module อื่นได้จาก

`@/modules/core` (ui เท่านั้น), `@/types/contract`

> หลัง Milestone M3 ห้าม import `MOCKS` ในหน้า `/chat`
