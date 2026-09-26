# Workspace handoff (P1 → P2/P6)

`ChatPage` ใช้ `WorkspaceLayout` สี่โหมดและ `MessageList` แสดง `ChatMessage` จาก contract ผ่าน `ResponseRenderer` ของ P6 หน้า `/chat` ไม่โหลด fixture ของ P6

| Trigger | Layout | COPIE state |
|---|---|---|
| เปิดหน้า / ห้องใหม่ | center | idle |
| เริ่ม request | คง layout เดิม | thinking |
| text ไม่เกิน 450 ตัวอักษร | split | responding 2.5 วินาที → idle |
| text ยาว หรือ course_table/cards/assessment_form/skill_radar/error | rail | ตามชนิดคำตอบ |
| skill_radar | rail | success |
| assessment_form | rail | skill-guide |
| error หรือ RAG ไม่พบแหล่งอ้างอิง | rail | no-answer |
| ผู้ใช้กดซ่อน | hidden | คง state เดิม |

P2 เรียก `useChatStore.getState().loadConversation(detail)` เมื่อได้ `ConversationDetail` จริงจาก History และ `newConversation()` เมื่อเริ่มห้องใหม่; ไม่มีการสร้างข้อมูลภาค/รายวิชา/คะแนนใน store

`send` และ `submitAssessment` เรียก `chatApi` ตาม contract และส่ง callback ของ `ResponseRenderer` แล้ว; หน้า `/chat` จะเปิด input/action เมื่อ P2 ลงทะเบียน `configureApiAuth({ getToken, clearToken, onUnauthorized })` ฝั่ง client และเรียก `notifyApiAuthChanged()` หลัง token เปลี่ยนเท่านั้น History ยังรอ UI/ข้อมูลจาก P2 การสลับห้องยกเลิกคำขอเก่าเพื่อไม่ให้คำตอบหลงห้อง

ขณะพิมพ์ COPIE ใช้ state `listening`; ระหว่าง request แสดง `thinking` และข้อความสถานะ; เมื่อแบบประเมินเป็นคำตอบล่าสุดจะซ่อนช่องพิมพ์จนส่งแบบประเมินสำเร็จหรือเปิดห้องใหม่ หน้าแชตใช้ `h-dvh` โดยไม่มีขั้นต่ำ 600px เพื่อให้ช่องพิมพ์ยังมองเห็นเมื่อคีย์บอร์ดมือถือทำให้ viewport เตี้ยลง

โหมด split แสดง Renderer ฝั่งซ้ายและมาสคอตฝั่งขวา เพราะ Renderer ปัจจุบันคืน component เดียว หากต้องการจัดเนื้อหา/แหล่งอ้างอิงสองฝั่งรอบมาสคอตเหมือน mockup 04 ต้องให้ P6 เพิ่ม slot ใน public API ก่อน P1 ปรับ layout โดยไม่แก้ไฟล์ของ P6 เอง
