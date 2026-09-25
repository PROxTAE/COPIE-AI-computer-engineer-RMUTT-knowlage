# core — Frontend Core / Design System / Workspace

| | |
|---|---|
| เจ้าของ | **P1** |
| แผนงาน | [`01_FRONTEND_CORE_MASCOT.md`](../../../../IMPLEMENTATION_PLANS/01_FRONTEND_CORE_MASCOT.md) |
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

## ใช้ธีมระหว่างรอ workspace (P2/P6)

- `app/globals.css` โหลด HeroUI และ design kit แล้ว ครอบหน้าที่ต้องการพื้นกริด/halo ด้วย `className="copie-ui"`
- ใช้ Tailwind `bg-cyber-blue`, `text-cyber-ink`, `font-display`, `font-sans`, `font-label`, `font-wordmark` และ class ของ kit เช่น `copie-heading`, `copie-eyebrow`, `copie-panel`
- สีหลักอยู่ที่ `assets/web-ui/styles/tokens.css`; หากแก้ master ให้รัน `python scripts/sync_ui_assets.py` เพื่ออัปเดต CSS และ WebP ใน frontend
- ใช้ `CopieMascot` จาก `@/modules/mascot` พร้อม `state` และ `layout`; ดู state ทั้งหมดที่ `/` (theme preview)
- `ui/`, `api.ts`, `chatStore` และ workspace จะส่งใน PR ถัดไป อย่า import ก่อน merge

## ใช้ของ module อื่นได้จาก

`@/modules/mascot`, `@/modules/renderer`, `@/modules/user`, `@/modules/suggest`, `@/modules/export`, `@/types/contract`
