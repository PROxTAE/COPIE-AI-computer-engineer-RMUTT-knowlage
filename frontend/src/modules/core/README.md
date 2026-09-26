# core — Frontend Core / Design System / Workspace

| | |
|---|---|
| เจ้าของ | **P1** |
| แผนงาน | [`01_FRONTEND_CORE_MASCOT.md`](../../../../IMPLEMENTATION_PLANS/01_FRONTEND_CORE_MASCOT.md) |
| Branch prefix | ดู `IMPLEMENTATION_PLANS/00_GIT_DELIVERY_RULES.md` §2 |

## หน้าที่

Design system (`ui/`), layout หน้า `/chat`, input, รายการข้อความ, `api.ts` (fetch + token + 401) และ `chatStore` (zustand) ที่คุมสถานะทั้งหน้า รวมถึงเป็นจุดที่ประกอบ module อื่นเข้าด้วยกัน

## โครงไฟล์

```text
core/
├─ index.ts          # public exports
├─ ui/               # AppHeader, HistoryButton, ChatInput, Icon, StatusLabel
├─ workspace/        # ChatPage, WorkspaceLayout, MessageList
├─ api.ts            # api<T>(), chatApi
└─ chatStore.ts      # messages, conversationId, copieState, layout และ request state
```

## Public API (สิ่งที่ module อื่นเรียกใช้ได้)

`AppHeader`, `HistoryButton`, `ChatInput`, `Icon`, `StatusLabel`, `api`, `chatApi`, `configureApiAuth`, `notifyApiAuthChanged`, `ChatPage`, `WorkspaceLayout`, `MessageList`, `useChatStore` ผ่าน `@/modules/core`

## ใช้ธีมระหว่างรอ workspace (P2/P6)

- `app/globals.css` โหลด HeroUI และ design kit แล้ว ครอบหน้าที่ต้องการพื้นกริด/halo ด้วย `className="copie-ui"`
- ใช้ Tailwind `bg-cyber-blue`, `text-cyber-ink`, `font-display`, `font-sans`, `font-label`, `font-wordmark` และ class ของ kit เช่น `copie-heading`, `copie-eyebrow`, `copie-panel`
- สีหลักอยู่ที่ `assets/web-ui/styles/tokens.css`; หากแก้ master ให้รัน `python scripts/sync_ui_assets.py` เพื่ออัปเดต CSS และ WebP ใน frontend
- ใช้ `CopieMascot` จาก `@/modules/mascot` พร้อม `state` และ `layout`; ดู state ทั้งหมดที่ `/` (theme preview)
- `ChatPage` ส่งคำถามและคำตอบแบบประเมินผ่าน API จริงเมื่อ P2 ลงทะเบียน token adapter; ไม่มี fixture response ในหน้า `/chat`
- P2 ลงทะเบียน `configureApiAuth({ getToken, clearToken, onUnauthorized })` ฝั่ง client ก่อนใช้หน้าแชต และเรียก `notifyApiAuthChanged()` เมื่อ token เปลี่ยน; เมื่อ 401 ให้พาไป `/login`
- `useChatStore` มี `loadConversation(detail)` ให้ P2 เรียกหลังเปิด History, `newConversation()` สำหรับเริ่มห้องใหม่ และ `send`/`submitAssessment` สำหรับ action จริง; การสลับห้องยกเลิก request ที่ค้างอยู่
- `MessageList` ส่ง action callbacks ไป `ResponseRenderer` ของ P6 โดยผูกแบบประเมินกับ response ที่แสดง; ปิด action เมื่อไม่มี auth หรือระหว่าง pending
- `/chat?debug=1` เปิดปุ่มสลับ layout/state เฉพาะ `next dev`; production จะไม่แสดงเครื่องมือ debug
- การจัดเนื้อหาสองฝั่งรอบมาสคอตตาม mockup 04 ต้องให้ P6 expose ส่วนเนื้อหา/แหล่งอ้างอิงเป็น slot เพิ่มเติม; ปัจจุบัน Renderer ส่งเป็นก้อนเดียว จึงแสดงฝั่งซ้ายในโหมด split

## ใช้ของ module อื่นได้จาก

`@/modules/mascot`, `@/modules/renderer`, `@/modules/user`, `@/modules/suggest`, `@/modules/export`, `@/types/contract`
