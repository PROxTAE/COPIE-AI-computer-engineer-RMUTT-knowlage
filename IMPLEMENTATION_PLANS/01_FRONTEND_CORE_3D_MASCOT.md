# P1 — Frontend Core + 3D COPIE Mascot (Tech Lead)

## Mission

สร้างโครง frontend ทั้งหมด, Design System และหน้า **Main AI Experience (`/chat`)** ที่มี **COPIE 3D** เป็นจุดศูนย์กลาง ขยับตามสถานะ 5 แบบ และเป็นคนรวมทุกชิ้นของทีมเข้าด้วยกัน (Renderer, History, Feedback, Suggestions, Export) ให้กลายเป็นเว็บเดียว

**ความสำคัญ:** นี่คือจุดขายของโปรเจกต์และเป็น "ที่รวม" ของทุกคน ถ้าไม่เสร็จ งานของ P2, P6, P7, P8 จะไม่มีที่แสดง และ Demo จะดูเหมือน chatbot ธรรมดา

## Ownership

แก้ได้โดยตรง
- `frontend/src/modules/core/**`, `frontend/src/modules/mascot/**`
- routes `frontend/src/app/{layout.tsx,page.tsx,globals.css,chat/}` และ config ของ `frontend/` (`package.json`, `next.config.ts`, `eslint.config.mjs`, `tsconfig.json`, `public/`)
- `.gitignore`, `.gitattributes`, `.githooks/`, `.github/CODEOWNERS`, `.github/pull_request_template.md`, `scripts/check-ai-watermark.sh`

ต้องขอ review เพิ่ม
- 🔒 `frontend/src/types/contract.ts` — P3 ต้อง approve ด้วย
- `frontend/package.json` ถ้าคนอื่นเพิ่ม library → P1 approve

Dependency

| รับจาก | อะไร | ระหว่างรอใช้ |
|---|---|---|
| P3 | `/api/chat`, `/api/assessment/submit` | mock endpoint ของ P3 (Day 1) |
| P6 | `<ResponseRenderer />` | `<pre>{JSON.stringify(response)}</pre>` |
| P2 | `AuthGuard`, `HistorySidebar`, `FeedbackBar`, `userStore` | ข้าม auth ด้วย Dev token |
| P7 / P8 | `SuggestedPrompts`, `CopyButton`, `ExportMenu` | ไม่แสดง (optional) |

ส่งให้: ทุกคนที่ทำ frontend ใช้ `ui/`, `api.ts`, layout ของ P1

## Stack

- Node.js 22 LTS · **Next.js 16** (App Router, Turbopack) + **React 19** + TypeScript strict + **Tailwind CSS v4**
  (ดูข้อแตกต่างจากรุ่นเก่าใน `00_SHARED_PROJECT_CONTEXT.md` §7)
- `three`, `@react-three/fiber@9`, `@react-three/drei@10` (COPIE — รุ่นที่รองรับ React 19)
- `motion` (เดิมชื่อ framer-motion — `import { motion } from "motion/react"`) สำหรับ transition หน้า/panel, `zustand` (state), `lucide-react` (icon)
- ฟอนต์ไทยจาก `next/font/google`: IBM Plex Sans Thai (body), Bai Jamjuree (heading)

## Target folder structure

```text
frontend/
├─ package.json, package-lock.json, next.config.ts, eslint.config.mjs, tsconfig.json, postcss.config.mjs
├─ Dockerfile
└─ src/
   ├─ app/                        # routes บางๆ: layout.tsx, page.tsx, globals.css, chat/page.tsx
   ├─ types/contract.ts           # 🔒 P1 + P3
   └─ modules/
      ├─ core/                    # 👤 P1
      │  ├─ index.ts              # public: ui components, api, chatApi, useChatStore, ChatPage
      │  ├─ ui/                   # Button, Input, Textarea, Card, Badge, Spinner, Toast, Drawer
      │  ├─ workspace/            # WorkspaceLayout, ChatInput, MessageList, Greeting, ChatPage
      │  ├─ api.ts
      │  └─ chatStore.ts
      └─ mascot/                  # 👤 P1
         ├─ index.ts              # public: Copie, CopieState
         ├─ CopieScene.tsx        # <Canvas>, camera, lights, Environment, ContactShadows
         ├─ CopieModel.tsx        # ตัว COPIE จาก primitive
         ├─ useCopieAnimation.ts
         └─ CopieFallback.tsx     # รูป 2D เมื่อ WebGL ใช้ไม่ได้

# app/chat/page.tsx เหลือแค่:  export { ChatPage as default } from "@/modules/core";
```

## Design details

### COPIE model (primitive)

**Reference design:** `assets/mascot/copie-computer-concept-v2.png` (v2 ล่าสุด — หัวเป็นจอมอนิเตอร์มีหูแมว, ตา + ยิ้มเรืองแสงสีฟ้าบนจอสีเข้ม, หูฟังวงกลม 2 ข้าง, ปุ่ม 3 สีที่หน้าอก, ตัวสีขาวขอบ teal) · `copie-owl-concept-v1.png` เป็นแนวคิดเก่า
ใช้ primitive สร้างให้ใกล้เคียง v2: RoundedBox (หัว/จอ) + Cone (หู) + Cylinder (หูฟัง) + Capsule (ตัว/แขน/ขา) + emissive material สำหรับตาและยิ้ม

```text
        ●  ← antenna tip (sphere, emissive teal)
        |  ← antenna (cylinder) — หมุน/กระพริบตอน thinking
   ┌─────────┐
   │ ◉     ◉ │ ← head: RoundedBox, หน้าจอสีเข้ม, ตา 2 capsule emissive
   │   ‿‿‿   │ ← mouth: torus ครึ่งวง (scale Y ขยับตอน responding)
   └─────────┘
     ┌─────┐    ← body: capsule / RoundedBox เล็ก + โลโก้ CE
     └─────┘
   ◯ ContactShadows ด้านล่าง
```

### Animation state machine

| State | Trigger (chatStore) | Animation (`useFrame`) | ระยะเวลา |
|---|---|---|---|
| `idle` | default | ลอยขึ้นลง sin(t)·0.05, กระพริบตาทุก 3–5 วินาที | ต่อเนื่อง |
| `listening` | input มีข้อความ | เอียงหัวตาม pointer, ตาโตขึ้นเล็กน้อย | ขณะพิมพ์ |
| `thinking` | รอ API | antenna หมุน, ตากะพริบเร็ว, ตัวโยกช้าๆ | จนได้คำตอบ |
| `responding` | ได้ response | ปากขยับ, เด้งเบาๆ | 2.5 วินาที → idle |
| `success` | ได้ `skill_radar` | กระโดด + sparkles (drei `<Sparkles/>`) | 2 วินาที → idle |

- เปลี่ยน state แบบ lerp (ไม่กระตุก) · `prefers-reduced-motion` → ปิดการลอย/กระโดด เหลือแค่เปลี่ยนสีตา
- `CopieScene` โหลดด้วย `next/dynamic` + `ssr: false` · ถ้า WebGL ใช้ไม่ได้แสดง `CopieFallback`

### `modules/core/api.ts`

```ts
export async function api<T>(path: string, init?: RequestInit): Promise<T>
// - แนบ Authorization จาก getToken() ของ @/modules/user (P2)
// - timeout 30s ด้วย AbortController
// - 401 → clear token → router.push('/login')
// - error → throw new ApiError(status, detail) ให้ UI แสดง toast
export const chatApi = {
  send: (body: ChatRequest) => api<AgentResponse>('/api/chat', {...}),
  submitAssessment: (body: AssessmentSubmit) => api<AgentResponse>('/api/assessment/submit', {...}),
};
```

### `chatStore` (zustand)

```ts
{
  conversationId: string | null;
  messages: ChatMessage[];           // จาก contract
  copieState: 'idle'|'listening'|'thinking'|'responding'|'success';
  pending: boolean;
  send(text: string): Promise<void>;
  submitAssessment(answers): Promise<void>;
  loadConversation(detail: ConversationDetail): void;   // P2 เรียกจาก HistorySidebar
  newConversation(): void;
}
```

## Implementation steps

### Phase 0 — Kickoff + Contract (Day 1 09:00–12:00)

1. สร้าง repo ตาม `00_GIT_DELIVERY_RULES.md` §1, ตั้ง branch protection
2. นำ review Contract ร่วมกับ P3 แล้วสร้าง `types/contract.ts` ตาม `00_API_AND_DATA_CONTRACTS.md` §3.1
3. สร้าง frontend (รันที่ root ของ repo):
   ```bash
   npx create-next-app@latest frontend --ts --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm --no-agents-md --disable-git --yes
   ```
   - ได้ Next.js 16.x + React 19.2 + Tailwind v4 (Turbopack เป็นค่าเริ่มต้นแล้ว ไม่ต้องใส่ flag)
   - **ต้องใส่ `--no-agents-md`** — ค่าเริ่มต้นจะสร้าง `AGENTS.md` ซึ่งเป็นไฟล์ AI tool ที่กติกาห้าม commit
   - `--disable-git` เพราะ repo มี git อยู่แล้ว
   - เพิ่ม rewrites `/api/*` + `output: "standalone"` ใน `next.config.ts` · ใส่ `"engines": {"node": ">=22"}` · commit `package-lock.json`

Exit: **M0** — repo มี develop, frontend รัน `npm run dev` ได้, `contract.ts` merge แล้ว

### Phase 1 — Design system + app shell (Day 1 PM)

1. tokens ใน `globals.css` ด้วย `@theme` (Tailwind v4 ไม่มี `tailwind.config.ts`), ฟอนต์ไทยผ่าน `next/font/google`
2. `ui/` components ขั้นต่ำ + `modules/core/api.ts` + หน้า `/chat` ว่างที่มี layout
3. `page.tsx` redirect (ใช้ `userStore` ของ P2 หรือ token ชั่วคราว)

Exit: **M1** — คนอื่นใช้ `ui/` และ `api.ts` ได้, `npm run build` ผ่าน

### Phase 2 — COPIE 3D (Day 2 ทั้งวัน)

1. AM: `CopieScene` (camera fov 35, 3-point light, `Environment preset="city"`, `ContactShadows`) + `CopieModel`
2. PM: `useCopieAnimation(state)` ครบ 5 state + ปุ่มทดสอบ state ชั่วคราวในหน้า `/chat?debug=1`
3. วัด fps (ต้อง ≥ 50 บนโน้ตบุ๊ก), ใส่ fallback

Exit: **M2** — COPIE ขยับครบ 5 state และเปลี่ยน state ได้จาก store

### Phase 3 — Workspace (Day 3 AM)

1. `WorkspaceLayout`: desktop = sidebar ซ้าย + COPIE บน + response panel + input ล่าง; mobile = drawer
2. `ChatInput` (Enter ส่ง, Shift+Enter ขึ้นบรรทัด, disable ตอน pending, จำกัด 1000 ตัวอักษร)
3. `MessageList` แสดงข้อความ user + ส่ง assistant response ให้ Renderer (ใช้ mock ของ P6)
4. `chatStore` + mapping state → COPIE

### Phase 4 — Wire real API + รวมชิ้นของทีม (Day 3 PM)

1. `send()` เรียก `/api/chat` จริง, `submitAssessment()` เรียก `/api/assessment/submit`
2. วาง `<ResponseRenderer response onAsk onSubmitAssessment />` (P6), `HistorySidebar` (P2), `FeedbackBar` (P2), `SuggestedPrompts` (P7), `CopyButton`/`ExportMenu` (P8)
3. greeting ใช้ `display_name` จาก `userStore`

Exit: **M3** — ถามจาก UI แล้วได้คำตอบจริงจาก backend ครบทุก response_type

### Phase 5 — Integration lead (Day 4)

1. AM: รวม PR, แก้ conflict, เดิน Demo 1–6 กับ P8, จัดลำดับบั๊ก
2. PM: responsive (1440/1024/390), loading skeleton, error toast, empty state, `Dockerfile` frontend

Exit: **M4** — Demo 1–6 ผ่านบน develop, merge main เป็น `v0.9`

### Phase 6 — Polish + Release (Day 5)

1. AM: transition ระหว่างคำตอบ, hover/focus states, หน้า login ให้เข้าธีม (ร่วมกับ P2)
2. PM: Code Freeze 15:00 → `release/v1.0` → tag → ซ้อม Demo

Exit: **M5**

## Required tests

| ประเภท | สิ่งที่ต้องทดสอบ |
|---|---|
| Build | `npm run lint` + `npm run build` ผ่านทุก PR |
| Manual | COPIE ครบ 5 state, fps, fallback เมื่อปิด WebGL (Chrome flag) |
| Manual | ส่งข้อความซ้ำเร็วๆ ไม่ส่งซ้ำ (pending lock), 401 พาไป login |
| Responsive | 1440 / 1024 / 390 ไม่มี horizontal scroll, input ไม่ถูกคีย์บอร์ดบัง |
| E2E | Demo 1–6 ใน `09_INTEGRATION_ACCEPTANCE_RUNBOOK.md` |

## Acceptance checklist

- [ ] COPIE แสดงผลและขยับครบ 5 state, มี fallback 2D
- [ ] `/chat` ส่งคำถามได้และแสดงทุก `response_type` ผ่าน Renderer
- [ ] COPIE state สัมพันธ์กับ request จริง (thinking ระหว่างรอ)
- [ ] redirect login/onboarding/chat ถูกต้องทุกกรณี
- [ ] responsive 3 ขนาด, keyboard ใช้งานได้, focus มองเห็น
- [ ] ไม่มี secret ใน frontend (มีแค่ `NEXT_PUBLIC_GOOGLE_CLIENT_ID`)
- [ ] `docker compose up --build` แล้วเว็บเปิดได้ที่ :3000

## Branch / PR breakdown

1. `core/repo-setup` — governance files, hooks, CI (P3 approve)
2. `core/app-shell` — Next.js scaffold, rewrites, `contract.ts`
3. `core/design-system` — tokens, fonts, `ui/`, `api.ts`
4. `mascot/copie-model` — scene + model
5. `mascot/copie-states` — animation 5 state + fallback
6. `core/workspace` — layout, input, message list, chatStore
7. `core/wire-chat-api` — ต่อ API จริง + วางชิ้นของทีม
8. `core/responsive` — responsive, states, Dockerfile
9. `core/polish` → `release/v1.0`

## Completion report requirements

สร้าง `docs/handoffs/P1-frontend-core.md` ระบุเพิ่ม: component tree ของ `/chat`, ตาราง COPIE state → trigger, วิธีเพิ่ม state ใหม่, ผล fps, screenshot 3 ขนาดจอ, จุด integration ที่ยังมีปัญหา
