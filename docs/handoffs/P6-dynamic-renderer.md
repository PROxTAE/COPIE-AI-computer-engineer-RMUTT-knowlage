# P6 — Dynamic Response Renderer (handoff)

โมดูล `frontend/src/modules/renderer/` แปลง `AgentResponse` ทุก `response_type` เป็น UI
และเป็นเจ้าของ mock fixtures + หน้า `/dev`

## วิธีใช้จากโมดูลอื่น

```tsx
import { ResponseRenderer } from "@/modules/renderer";

<ResponseRenderer
  response={response}                  // AgentResponse จาก POST /api/chat
  onAsk={(text) => chatStore.send(text)}
  onSubmitAssessment={(answers) => chatStore.submitAssessment(answers)}
  disabled={chatStore.pending}
/>;
```

Renderer **ไม่เรียก API เอง** ทุกการกระทำของผู้ใช้ออกทาง callback เท่านั้น

ลำดับการแสดงผลคงที่ทุก type: `message` (markdown) → component ตาม `response_type` → `SourceViewer` → `ActionChips`

## ตาราง response_type → component → props

| `response_type` | Component | data ที่ใช้ | callback ที่เรียก |
|---|---|---|---|
| `text` | `TextResponse` | `message` | `onCitationClick` (ภายใน) |
| `course_table` | `CourseTable` | `CourseTableData` | – (เลือกแถวเป็น state ภายใน) |
| `cards` | `InfoCards` | `CardsData` | `onAsk("ขอรายละเอียดเพิ่มเติมเกี่ยวกับ<title>")` |
| `assessment_form` | `AssessmentForm` | `AssessmentFormData` | `onSubmitAssessment(answers)` |
| `skill_radar` | `SkillRadar` | `SkillRadarData` | `onAsk("ขอทำแบบประเมิน skill ใหม่")` |
| `error` | `ErrorResponse` | `ErrorData` + `actions` | `onAsk(<คำถามเดิม>)` |
| ทุก type | `SourceViewer` | `sources` | – |
| ทุก type | `ActionChips` | `actions` | `onAsk(payload.text)` หรือเปิด `payload.url` |

`clarify` ไม่ใช่ `response_type` — เป็น `meta.intent` ของ `text` ที่มี `actions` เป็นตัวเลือกให้กด

## หน้า `/dev`

`npm run dev` แล้วเปิด <http://localhost:3000/dev> — ไม่ต้องมี backend

- เลือก fixture จากรายการซ้าย (10 ตัว ครอบคลุมครบ 6 `response_type` + edge case)
- สลับ **Desktop / Mobile 390px** เพื่อดูพฤติกรรม responsive
- ปุ่ม **disabled** จำลองตอนมี request ค้าง (ปุ่มทุกปุ่มต้องกดไม่ได้)
- ปุ่ม **ดู JSON** แสดง `AgentResponse` ดิบ ใช้ตรวจ contract กับฝั่ง backend
- **Callback log** บันทึกว่า `onAsk` / `onSubmitAssessment` ถูกเรียกด้วยค่าอะไร

## Responsive: ใช้ container query ไม่ใช่ viewport

`ResponseRenderer` ตั้งตัวเองเป็น `@container` และลูกทุกตัวใช้ `@lg:` `@2xl:` `@3xl:`
แปลว่า component ปรับตาม **ความกว้างของกล่องที่วาง** ไม่ใช่ความกว้างจอ — เอาไปวางใน
แผงแคบของ workspace ได้โดยไม่ต้องแก้อะไร และโหมด Mobile 390px ใน `/dev` แสดงผลตรงกับของจริง

จุดสลับที่ใช้: `CourseTable` เปลี่ยนจากการ์ดเป็นตารางที่ `@2xl` (672px) · `InfoCards` และ
`SourceViewer` เป็น 2 คอลัมน์ที่ `@lg` และ 3 คอลัมน์ที่ `@3xl`

## วิธีเพิ่ม `response_type` ใหม่

1. **contract** — เปิด `contract/*` PR แก้ `frontend/src/types/contract.ts` + `backend/app/schemas/contract.py` พร้อมกัน (ต้องมี P1 + P3 approve)
2. **fixture** — เพิ่มไฟล์ใน `renderer/mock/` แล้ว export ใน `mock/index.ts` ทั้งใน `MOCKS` และ `MOCK_LABELS`
3. **component** — สร้างใน `renderer/components/` รับ `data` ตรงจาก contract ห้ามประกาศ type ซ้ำ
4. **switch** — เพิ่ม `case` ใน `ResponseBody` ของ `ResponseRenderer.tsx`

ข้ามข้อ 4 แล้ว `npm run build` จะแดงทันทีจาก `const _exhaustive: never = response;`
— นี่คือกันลืมของโมดูลนี้ ห้ามเอาออก

## ข้อจำกัดที่ยังค้าง

| เรื่อง | รอใคร |
|---|---|
| ข้อมูลรายวิชา หน่วยกิต และแบบประเมินใน fixture เป็น placeholder (รหัสใช้รูปแบบ `04-xxx-2xx`) | P5 — `data/curriculum/curriculum.json`, `data/assessment/skill_v1.json` |
| `Source.url` เป็น `null` ทั้งหมด การ์ดจึงขึ้นข้อความแทนลิงก์ | P4 — `source_url` จริงใน `data/knowledge/*.md` |
| ยังไม่ได้ใช้ HeroUI และ class `copie-*` จากชุด asset (ตอนนี้สไตล์ด้วย token ใน `globals.css`) | P1 — `@heroui/react` + `theme.css` + `copie-ui.css` |
| ปุ่มคัดลอกและ thumbs feedback ใต้คำตอบ (อยู่ในม็อกอัพ 05) ยังไม่ได้ทำ | P1 / P2 — `FeedbackRequest` เป็นของ P2 |

> `MOCKS` ใช้ได้เฉพาะ `/dev` และ tests — หลัง Milestone M3 ห้าม import ในหน้า `/chat`
