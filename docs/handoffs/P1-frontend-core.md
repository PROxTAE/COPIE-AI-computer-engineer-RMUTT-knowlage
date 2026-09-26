# P1 — Frontend core และ COPIE 2.5D

อัปเดต 26 ก.ย. 2026 · ฐาน `develop` หลัง PR `core/responsive`

## Component tree ของ `/chat`

```text
app/chat/page.tsx
└─ core/ChatPage
   ├─ AppHeader (profile slot รอ P2)
   ├─ WorkspaceLayout (center / split / rail / hidden)
   │  ├─ MessageList → P6 ResponseRenderer
   │  │  └─ onAsk → send, onSubmitAssessment → submitAssessment
   │  └─ CopieMascot + StatusLabel
   ├─ loading / error status
   ├─ HistoryButton (handler รอ P2)
   ├─ ChatInput → useChatStore.send
   └─ P7 SuggestedPrompts → useChatStore.send (เมื่อ auth พร้อมและห้องยังว่าง)
```

`core/api.ts` ต่อ `/api/chat` และ `/api/assessment/submit` ด้วย request/response จาก `frontend/src/types/contract.ts` โดยไม่เปลี่ยน contract; `chatStore` เก็บบทสนทนา, ป้องกันส่งซ้ำขณะ pending และยกเลิก request เดิมเมื่อเปลี่ยนห้อง หน้า `/chat` ไม่มี fixture หรือข้อความวิชา/คะแนนตัวอย่าง. `/` แสดง theme preview เฉพาะ `next dev`; production ส่งต่อ `/login` ให้ P2 จัดการ auth/onboarding.

## State และ layout

| Trigger | COPIE | Layout | หมายเหตุ |
|---|---|---|---|
| เปิดห้องใหม่ | idle | center | ไม่มีข้อความตัวอย่าง |
| พิมพ์ใน ChatInput | listening | คงเดิม | clear ข้อความกลับ idle |
| ส่งคำถาม / ส่งแบบประเมิน | thinking | คงเดิม | input/action ปิดขณะ pending |
| คำตอบ `text` ≤ 450 ตัวอักษร | responding → idle 2.5 วินาที | split | Renderer แสดงเป็นก้อนฝั่งซ้าย |
| คำตอบยาว, `course_table`, `cards` | responding → idle | rail | เนื้อหาเป็นจริงจาก API |
| `assessment_form` | skill-guide | rail | ซ่อนช่องพิมพ์จนได้ผลหรือเปลี่ยนห้อง |
| `skill_radar` | success | rail | คะแนนมาจาก backend เท่านั้น |
| `error` response หรือ RAG ไม่พบ source | no-answer | rail | ใช้ action จาก P6 Renderer |
| network/timeout/401 | idle | คงเดิม | แสดง error; 401 เคลียร์ token และให้ P2 นำไป login |
| ซ่อนมาสคอต | คงเดิม | hidden | แสดงปุ่มเรียกกลับ |
| กลับหน้าสนทนา/อ่านคำตอบ | คงเดิม | center/rail | ข้อความยังอยู่ใน store |

## วิธีใช้ของ P2/P6

- P2: ลงทะเบียน `configureApiAuth({ getToken, clearToken, onUnauthorized })` ฝั่ง client และเรียก `notifyApiAuthChanged()` หลัง token เปลี่ยน; `onUnauthorized` นำไป `/login`. เมื่อ logout หรือสลับบัญชีให้เรียก `useChatStore.getState().newConversation()`; เมื่อเลือก History ให้ส่ง `ConversationDetail` จริงเข้า `loadConversation(detail)`.
- P2: ใส่ profile control ใน `AppHeader.profile`, handler ใน `HistoryButton`, และนำ `display_name` จริงมาเป็น greeting เมื่อ user module พร้อม. ปัจจุบัน `frontend/src/modules/user/index.ts` ยังไม่ export implementation; production `/chat` จึงปิดการส่งจน auth adapter พร้อม.
- P6: นำเข้า `CopieMascot`, `COPIE_IMAGES`, `CopieMascotState` จาก `@/modules/mascot` และ token/UI จาก `@/modules/core`. `MessageList` ส่ง callbacks ไป `ResponseRenderer` โดยผูก `assessment_form` กับข้อความนั้น. หากจะจัดคำตอบสองฝั่งรอบมาสคอตตาม mockup 04 ต้อง expose content/source slots ใน public API ของ Renderer; P1 ไม่แก้ไฟล์ P6 เอง.
- P7: `SuggestedPrompts` merge แล้วและวางใต้ composer เฉพาะผู้ใช้ที่มี auth เมื่อห้องยังว่าง; `userType`/`studyYear` เป็น props ของ `ChatPage` เพื่อให้ P2 ส่งโปรไฟล์จริงมาภายหลัง. ไม่มีการสมมติประเภทผู้ใช้หรือชั้นปี.
- P8: `modules/export` ยังเป็น public API เปล่า; เมื่อพร้อม P1 จึงวาง CopyButton และ ExportMenu ใน workspace โดยไม่สร้าง fixture ใน `/chat`.

## เพิ่ม state หรือภาพมาสคอต

1. เพิ่มภาพ PNG โปร่งใสที่ `assets/web-ui/mascot/states/` (ชุดภาพนี้เป็นแหล่งต้นทาง).
2. รัน `python scripts/sync_ui_assets.py` เพื่อสร้าง WebP ใน `frontend/public/copie-ui/mascot/`; อย่าแก้ WebP ที่ sync แล้วตรง ๆ.
3. เพิ่ม state/เส้นทางภาพใน `frontend/src/modules/mascot/states.ts`; ปรับ trigger ใน `core/chatStore.ts` ถ้าจำเป็น.
4. ตรวจหน้า preview ใน `next dev`, crossfade 200ms, การ preload, `prefers-reduced-motion`, แล้วรัน lint/build.

## ภาพเทียบ mockup

ภาพใน `assets/mockups/ui-flow-v1/` เป็นตัวอย่างหน้าตา ไม่ใช่ข้อมูลจริง. ภาพผลลัพธ์ด้านล่างมาจาก browser; ภาพที่มีป้าย `DEV ONLY` ใช้ตรวจ layout โดยไม่มีข้อมูลตัวอย่างใน `/chat`.

| Mockup | หลักฐานปัจจุบัน | ผลเทียบ / งานค้าง |
|---|---|---|
| [01 Login](../../assets/mockups/ui-flow-v1/01-login-v2.png) | [Theme preview](../../assets/screenshots/p1-theme-preview-1672x941.png) | ฟอนต์/ธีม/มาสคอตพร้อม; หน้า Login จริงรอ P2 |
| [02 Onboarding](../../assets/mockups/ui-flow-v1/02-onboarding.png) | [Theme preview](../../assets/screenshots/p1-theme-preview-1672x941.png) | UI ฟอร์มจริงรอ P2 |
| [03 Chat composing](../../assets/mockups/ui-flow-v1/03-chat-composing.png) | [หน้า chat](../../assets/screenshots/p1-wire-chat-gated-1672x941.png), [listening ใน dev](../../assets/screenshots/p1-polish-listening-debug-1672x941.png) | ตำแหน่ง wordmark/input/มาสคอตครบ; asset `copie-listening` ใน kit เป็นท่ายืน ต่างจากภาพ laptop ใน mockup; การพิมพ์จริงรอ token P2 |
| [04 Chat answer](../../assets/mockups/ui-flow-v1/04-chat-answer.png) | [split layout](../../assets/screenshots/p1-workspace-split-1672x941.png) | layout/action ต่อแล้ว; ยังขาด slots ของ P6 สำหรับคำตอบสองฝั่งและข้อมูล API จริง |
| [05 Reading mode](../../assets/mockups/ui-flow-v1/05-reading-mode.png) | [rail พร้อมปุ่มกลับใน dev](../../assets/screenshots/p1-polish-rail-back-debug-1672x941.png) | rail/hide/show/กลับหน้าสนทนาพร้อม; feedback/copy รอ P2/P8 |
| [06 History](../../assets/mockups/ui-flow-v1/06-history-open.png) | [chat shell](../../assets/screenshots/p1-ui-shell-1672x941.png) | จุดวาง HistoryButton พร้อม; sidebar/data รอ P2 |
| [07 Course table](../../assets/mockups/ui-flow-v1/07-course-table.png) | [rail layout](../../assets/screenshots/p1-workspace-rail-1672x941.png) | P6 Renderer ต่อแล้ว; end-to-end ต้องมี P2 auth และ backend จริง |
| [08 Info cards](../../assets/mockups/ui-flow-v1/08-info-cards.png) | [rail layout](../../assets/screenshots/p1-workspace-rail-1672x941.png) | เหมือน 07; ไม่คัดลอกข้อมูลจากภาพ |
| [09 Assessment intro](../../assets/mockups/ui-flow-v1/09-assessment-intro.png) | [center layout](../../assets/screenshots/p1-workspace-center-1672x941.png) | บริบทและ action ต้องมาจาก Agent/P6; ไม่สร้าง intro ปลอม |
| [10 Assessment form](../../assets/mockups/ui-flow-v1/10-assessment-question.png) | [rail layout](../../assets/screenshots/p1-workspace-rail-1672x941.png) | callback submit ต่อแล้วและซ่อน composer; ข้อคำถาม/ผลจริงรอ API พร้อม auth |
| [11 Skill radar](../../assets/mockups/ui-flow-v1/11-skill-radar.png) | [rail layout](../../assets/screenshots/p1-workspace-rail-1672x941.png) | P6 แสดงกราฟจาก response; คะแนนต้องมาจากสูตร backend |

Responsive production: [1440](../../assets/screenshots/p1-responsive-chat-1440x900.png) · [1024](../../assets/screenshots/p1-responsive-chat-1024x768.png) · [390](../../assets/screenshots/p1-responsive-chat-390x844.png). ทั้งสามขนาดไม่มี scroll แนวนอน; ที่ viewport 390×500 ช่องพิมพ์ยังเห็นครบ.

## Integration ที่ยังติด

1. P2 auth/profile/history/feedback ยังไม่ merge; `user/index.ts` ยังว่าง จึงตรวจ Demo 1, 5, 6 ไม่ได้. P1 ปิด input ใน flow จริงจนได้ token adapter.
2. P3 `backend/app/modules/agent/router.py` ยังมีทางลัด `mock:` และ `services.py` ยัง fallback ไป stub เมื่อ module ไม่พร้อม; ต้องถอด mock route และให้ `STUBBED` ว่างก่อน Demo 1–6. ไม่ใช้ทางลัดนี้ในหน้า `/chat`.
3. P6 Renderer ยังเป็น component ก้อนเดียว; mockup 04 ต้องการวางเนื้อหาและ sources สองฝั่งรอบมาสคอต. การปรับ public API ต้องให้ P6 ทำ/รีวิว.
4. P7 SuggestedPrompts ต่อแล้วแต่ยังไม่ได้ข้อมูล `user_type`/`study_year` จริงจาก P2; P8 public exports ยังว่างจึงยังไม่วาง Copy/Export.
5. เครื่องนี้ไม่มี Docker daemon ขณะตรวจ PR responsive; standalone server เปิด `/chat` และไฟล์มาสคอตได้ 200 แต่ `docker compose up --build` กับ Demo 1–6 ต้องรันทดสอบเมื่อ dependencies พร้อม.

P1 ผ่าน `npm run lint` และ `npm run build` ทุก PR; ยังไม่ถือว่า M3–M5 หรือ Definition of Done ทั้งโปรเจกต์ผ่านจนกว่าจะเชื่อมทีมและรัน runbook บน `develop` ด้วยข้อมูลจริง.
