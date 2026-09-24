# P6 — Dynamic Response Renderer

## Mission

เปลี่ยน `AgentResponse` ทุกแบบให้กลายเป็น UI ที่สวยและใช้งานได้: ข้อความ, ตารางรายวิชา, การ์ด, ฟอร์มประเมิน, Radar Chart, แหล่งอ้างอิง และปุ่มคำถามต่อ รวมถึงเป็นเจ้าของ **mock fixtures** ที่ทุกคนใช้พัฒนาคู่ขนาน

**ความสำคัญ:** นี่คือส่วนที่ทำให้ COPIE "ไม่ใช่ chatbot ธรรมดา" (Dynamic UI) ถ้าไม่เสร็จ ผู้ใช้จะเห็นแค่ JSON หรือข้อความเปล่าๆ และ Demo 2–4 ไม่มีภาพที่เห็นผล

## Ownership

แก้ได้โดยตรง
- `frontend/src/modules/renderer/**` (components, mock, DevPlayground)
- route `frontend/src/app/dev/`

ต้องขอ review เพิ่ม
- `package.json` (เพิ่ม `react-markdown`, `remark-gfm`, `recharts@3`) — P1
- 🔒 `contract.ts` — ถ้าพบว่าข้อมูลไม่พอสำหรับ UI ให้เปิด `contract/*` PR

Dependency

| รับจาก | อะไร |
|---|---|
| Contract | shape ของทุก `response_type` |
| P1 | `ui/` components, design tokens, ตำแหน่งใน Workspace |
| P5 | ตัวอย่างข้อมูลหลักสูตรจริงสำหรับ fixture |

ส่งให้: **P1** `<ResponseRenderer />` · **ทุกคน** mock fixtures + หน้า `/dev`

## Stack

- React 19 + TypeScript + Tailwind v4 (อยู่ในโปรเจกต์ Next.js 16 ของ P1), `motion` (`import { motion } from "motion/react"`)
- `react-markdown` + `remark-gfm` (ห้าม `dangerouslySetInnerHTML`)
- `recharts` (RadarChart), `lucide-react` (icon ใน InfoCard)

## Target folder structure

```text
frontend/src/modules/renderer/      # 👤 P6
├─ index.ts                         # public: ResponseRenderer, DevPlayground, MOCKS
├─ ResponseRenderer.tsx             # switch(response_type) + never check
├─ DevPlayground.tsx                # dropdown เลือก fixture → render
├─ components/
│  ├─ TextResponse.tsx              # markdown + [n] → citation badge
│  ├─ SourceViewer.tsx              # chips → expand snippet + open url
│  ├─ CourseTable.tsx               # desktop table / mobile card list
│  ├─ InfoCards.tsx
│  ├─ AssessmentForm.tsx            # step-by-step
│  ├─ SkillRadar.tsx
│  ├─ ActionChips.tsx
│  ├─ ErrorResponse.tsx
│  └─ skillLabels.ts                # SkillKey → ชื่อไทย/อังกฤษ + icon
└─ mock/
   ├─ index.ts                      # export const MOCKS: Record<string, AgentResponse>
   ├─ text.ts  text-with-sources.ts  course-table.ts  cards.ts
   └─ assessment-form.ts  skill-radar.ts  error.ts  clarify.ts

frontend/src/app/dev/page.tsx       # export { DevPlayground as default } from "@/modules/renderer";
```

## Design details

### Props (ตกลงกับ P1 ใน Day 1)

```tsx
<ResponseRenderer
  response={AgentResponse}
  onAsk={(text: string) => void}                                   // ActionChips / ปุ่มลองใหม่
  onSubmitAssessment={(answers: {question_id: string; value: number}[]) => Promise<void>}
  disabled?: boolean                                               // ระหว่าง pending
/>
```

- Renderer **ไม่เรียก API เอง** — ส่งผ่าน callback ให้ `chatStore` ของ P1
- ทุก component รับ props จาก `contract.ts` ตรงๆ ห้ามสร้าง type ซ้ำ
- `ResponseRenderer` แสดง `message` (markdown) ด้านบนเสมอ แล้วตามด้วย component ตาม type → `SourceViewer` (ถ้า sources ไม่ว่าง) → `ActionChips` (ถ้ามี)

### Component spec

| Component | ต้องมี |
|---|---|
| `TextResponse` | markdown (หัวข้อ, list, bold, ตาราง gfm), `[1]` → badge กดแล้ว scroll/เปิด source นั้น, typing animation ~20ms/ตัวอักษร (ข้ามได้เมื่อคลิก, ปิดเมื่อ reduced-motion) |
| `SourceViewer` | chip `title · section`, กดขยาย snippet, ปุ่มเปิด `url` (`target="_blank" rel="noopener noreferrer"`) |
| `CourseTable` | หัว "ปี X เทอม Y", คอลัมน์ รหัส / ชื่อวิชา (ไทย + อังกฤษตัวเล็ก) / หน่วยกิต / หมวด, แถวสรุปหน่วยกิตรวม, คลิกแถวเห็น description, `tabular-nums`, mobile เป็น card list |
| `InfoCards` | grid 1–3 คอลัมน์, icon จาก `lucide-react` ตามชื่อ (fallback `BookOpen`), tags |
| `AssessmentForm` | ทีละข้อ, progress "3 / 12", ปุ่มตัวเลือกใหญ่กดง่าย, ย้อนกลับได้, ข้อสุดท้ายปุ่ม "ดูผล", disable ระหว่าง submit, ถ้าเคยตอบใน response เดิมแล้วแสดงสถานะ "ส่งแล้ว" |
| `SkillRadar` | RadarChart 6 แกน 0–100 (ชื่อไทย), top skills เป็น badge, `summary` markdown, วันที่ทำ, ปุ่ม "ทำแบบประเมินใหม่" → `onAsk("ขอทำแบบประเมิน skill ใหม่")` |
| `ActionChips` | `ask` → `onAsk(payload.text)`, `open_url` → ลิงก์ |
| `ErrorResponse` | ข้อความตาม `data.code` + ปุ่ม "ลองใหม่" ส่งคำถามเดิม |

- สี/ฟอนต์จาก token ของ P1 · ตัวเลขใช้ `tabular-nums` · ใช้ text + icon ไม่ใช่สีอย่างเดียว

### Fixtures

- ทุก fixture ต้อง type-check เป็น `AgentResponse` (ถ้า contract เปลี่ยน build จะแดงทันที)
- ใช้ข้อมูลที่ดูสมจริง (รหัสวิชา/ชื่อจาก P5) และมี edge case: ชื่อวิชายาวมาก, 0 sources, 5 sources, 12 คำถาม, คะแนน 0 และ 100
- fixture ใช้ได้ **เฉพาะ `/dev` และ tests** — หลัง M3 ห้าม import ใน `/chat`

## Implementation steps

### Phase 0 — Contract review (Day 1 AM)
1. ตรวจทุก `response_type` ว่ามีข้อมูลพอสำหรับ UI, ตกลง props กับ P1

### Phase 1 — Mocks + core (Day 1 PM)
1. fixtures ครบทุก type, `ResponseRenderer` (switch + `const _exhaustive: never`), หน้า `/dev`

Exit: **M1** — P1 วาง Renderer ใน workspace ได้ทันที

### Phase 2 — Text / Sources / Table / Cards (Day 2)
1. AM: `TextResponse` + citation badge + `SourceViewer`
2. PM: `CourseTable` + `InfoCards`

Exit: **M2**

### Phase 3 — Form / Radar / Chips (Day 3)
1. AM: `AssessmentForm`
2. PM: `SkillRadar`, `ActionChips`, `ErrorResponse`

Exit: **M3** — `/dev` แสดงครบทุก type, P1 ต่อเข้ากับ API จริงแล้วแสดงผลถูก

### Phase 4 — Animation + Integration (Day 4)
1. AM: `motion` (fade/slide-up, stagger แถวตาราง/การ์ด 40ms), ทำงานกับ P1 ให้ panel ไม่กระโดดเมื่อคำตอบยาว
2. PM: responsive 390px ทุก component, keyboard (Tab/Enter ในฟอร์ม)

Exit: **M4**

### Phase 5 — Polish (Day 5)
- แก้บั๊กจาก QA, ปรับระยะ/ตัวอักษรให้เท่ากันทุก component

## Required tests

| ประเภท | Cases |
|---|---|
| Type | `npm run build` ผ่าน = fixture ตรง contract |
| Manual (`/dev`) | ทุก fixture, sources ว่าง/เยอะ, ชื่อยาว, radar 0/100 |
| Interaction | ฟอร์มย้อนกลับได้, ส่งซ้ำไม่ได้, chip ส่งข้อความถูก, ลิงก์ source เปิด tab ใหม่ |
| Responsive | 1440 / 390 ไม่มี overflow แนวนอน (ตารางเลื่อนในกล่องตัวเองได้) |
| A11y | ปุ่มมี label, focus มองเห็น, radar มีตัวเลขเป็น text ด้วย |

## Acceptance checklist

- [ ] Render ครบ 6 `response_type` + sources + actions
- [ ] Markdown ปลอดภัย (ไม่มี raw HTML)
- [ ] AssessmentForm ส่งคำตอบผ่าน callback และแสดงสถานะส่งแล้ว
- [ ] SkillRadar อ่านง่าย ชื่อด้านภาษาไทย
- [ ] CourseTable แสดงหน่วยกิตรวม และใช้งานบนมือถือได้
- [ ] `/dev` ใช้ทดสอบได้โดยไม่ต้องมี backend
- [ ] ไม่มี mock ใน flow `/chat` หลัง M3

## Branch / PR breakdown

1. `renderer/core-and-mocks` — fixtures, ResponseRenderer, /dev
2. `renderer/text-and-sources`
3. `renderer/table-and-cards`
4. `renderer/assessment-form`
5. `renderer/skill-radar` — radar + chips + error
6. `renderer/animation`, `renderer/responsive`, `renderer/polish`

## Completion report requirements

สร้าง `docs/handoffs/P6-dynamic-renderer.md` ระบุเพิ่ม: ตาราง response_type → component → props, screenshot ทุก type (desktop + mobile), วิธีเพิ่ม response_type ใหม่ (ขั้นตอน contract → fixture → component → switch)
