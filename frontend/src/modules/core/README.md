# core — Frontend Core / Design System / Workspace

| | |
|---|---|
| เจ้าของ | **P1** |
| แผนงาน | [`01_FRONTEND_CORE_3D_MASCOT.md`](../../../../IMPLEMENTATION_PLANS/01_FRONTEND_CORE_3D_MASCOT.md) |
| Branch prefix | ดู `IMPLEMENTATION_PLANS/00_GIT_DELIVERY_RULES.md` §2 |

## หน้าที่

Design system (`ui/`), layout หน้า `/chat`, input, รายการข้อความ, `api.ts` (fetch + token + 401) และ `chatStore` (zustand) ที่คุมสถานะทั้งหน้า รวมถึงเป็นจุดที่ประกอบ module อื่นเข้าด้วยกัน

## โครงไฟล์ที่จะสร้าง

```text
core/
├─ index.ts          # public exports
├─ ui/               # Button, Input, Card, Badge, Spinner, Toast, Drawer
├─ workspace/        # WorkspaceLayout, ChatInput, MessageList, Greeting, ChatPage
├─ api.ts            # api<T>(), chatApi
└─ chatStore.ts      # messages, conversationId, copieState, send(), submitAssessment()
```

## Public API (สิ่งที่ module อื่นเรียกใช้ได้)

`ui` components, `api`, `chatApi`, `useChatStore`, `ChatPage`

## ใช้ของ module อื่นได้จาก

`@/modules/mascot`, `@/modules/renderer`, `@/modules/user`, `@/modules/suggest`, `@/modules/export`, `@/types/contract`
