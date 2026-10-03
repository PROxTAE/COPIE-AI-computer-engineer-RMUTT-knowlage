# P1 — Frontend Core + COPIE Mascot 2.5D (Tech Lead)

## Mission

สร้างโครง frontend, ธีม **White Cyberism** (HeroUI v3 + Tailwind v4) และหน้า **Main AI Experience (`/chat`)** ที่มี **COPIE แบบ 2.5D** เป็นจุดศูนย์กลาง เปลี่ยนท่าตามสถานะของ AI และจัดวางตาม mockup ใน `assets/mockups/ui-flow-v1/` แล้วรวมทุกชิ้นของทีม (Renderer, History, Feedback, Suggestions, Export) ให้เป็นเว็บเดียว

**ความสำคัญ:** นี่คือจุดขายของโปรเจกต์และเป็น "ที่รวม" ของทุกคน ถ้าไม่เสร็จ งานของ P2, P6, P7, P8 จะไม่มีที่แสดง และ Demo จะดูเหมือน chatbot ธรรมดา

## Ownership

แก้ได้โดยตรง
- `frontend/src/modules/core/**` (รวม `theme/`), `frontend/src/modules/mascot/**`
- routes `frontend/src/app/{layout.tsx,page.tsx,globals.css,icon.svg,chat/}` และ config ของ `frontend/` (`package.json`, `next.config.ts`, `eslint.config.mjs`, `tsconfig.json`, `public/`)
- `assets/` (design kit + mockups) และ `scripts/sync_ui_assets.py`
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

ส่งให้: ทุกคนที่ทำ frontend ใช้ธีม, `ui/`, `api.ts`, layout และ `CopieMascot` ของ P1

## Stack

- Node.js 22 LTS · **Next.js 16** (App Router, Turbopack) + **React 19** + TypeScript strict + **Tailwind CSS v4**
  (ดูข้อแตกต่างจากรุ่นเก่าใน `00_SHARED_PROJECT_CONTEXT.md` §7)
- **HeroUI v3** (`@heroui/react`, `@heroui/styles`) — component พื้นฐาน ปรับให้เข้าธีมผ่าน CSS variable ใน `core/theme/theme.css`
- Mascot 2.5D: ภาพโปร่งใส 1 ภาพต่อสถานะ (`public/copie-ui/mascot/*.webp`) + `next/image` + CSS motion จาก kit
- `motion` (`import { motion } from "motion/react"`) สำหรับ transition ของ layout/panel, `zustand` (state)
- ฟอนต์จาก `next/font/google`: **Kanit** (หัวข้อ), **IBM Plex Sans Thai** (เนื้อหา), **Chakra Petch** (ป้ายสถานะ), **Unbounded** (wordmark)

## Target folder structure

```text
frontend/
├─ package.json, package-lock.json, next.config.ts, eslint.config.mjs, tsconfig.json, postcss.config.mjs
├─ Dockerfile
├─ public/copie-ui/               # synced จาก assets/web-ui ด้วย scripts/sync_ui_assets.py (ห้ามแก้ตรงนี้)
│  ├─ brand/ backgrounds/ frames/ effects/ icons/   # SVG
│  └─ mascot/                     # copie-{idle,listening,thinking,responding,success,no-answer,skill-guide,front-laptop}.webp
└─ src/
   ├─ app/                        # routes บางๆ: layout.tsx (fonts), page.tsx, globals.css, icon.svg, chat/page.tsx
   ├─ types/contract.ts           # 🔒 P1 + P3
   └─ modules/
      ├─ core/                    # 👤 P1
      │  ├─ index.ts              # public: ui, api, chatApi, useChatStore, ChatPage, ThemePreview
      │  ├─ theme/
      │  │  ├─ kit/               # tokens.css, copie-ui.css, motion.css (synced จาก assets/web-ui/styles)
      │  │  └─ theme.css          # map kit → Tailwind (@theme) + HeroUI variables + บทบาทฟอนต์
      │  ├─ ui/                   # wrapper บางๆ ของ HeroUI: AppHeader, HistoryButton, ChatInput, Icon (SVG kit), StatusLabel
      │  ├─ workspace/            # WorkspaceLayout (center / split / rail), MessageList, ChatPage
      │  ├─ api.ts
      │  └─ chatStore.ts
      └─ mascot/                  # 👤 P1
         ├─ index.ts              # public: CopieMascot, CopieMascotState, COPIE_IMAGES (+ Copie 3D — ดูหมายเหตุ)
         ├─ states.ts             # state → ภาพ
         ├─ CopieMascot.tsx       # 2.5D: next/image + crossfade + breathe
         └─ Copie.tsx             # 3D (GLB) ที่มีอยู่แล้ว — ทางเลือก รอทีมตัดสินใจ

# app/chat/page.tsx เหลือแค่:  export { ChatPage as default } from "@/modules/core";
```

## Design details

### Source of truth

- **Mockup 11 หน้าจอ:** `assets/mockups/ui-flow-v1/` + คำอธิบายทีละส่วนใน `SCREEN_GUIDE.md` (1672×941)
- **Asset kit:** `assets/web-ui/` (ดู `ASSET_GUIDE.md`) — SVG, mascot PNG, CSS tokens/components/motion
- ตัวอักษร/ตัวเลขในภาพ mockup เป็นตัวอย่าง — ข้อมูลจริงมาจาก API

### ธีม White Cyberism

| Token | ค่า | ใช้กับ |
|---|---|---|
| `cyber-blue` | `#155FF2` | ปุ่มหลัก, สถานะ, เส้นเน้น, ตัวเลขลำดับ (= HeroUI `--accent`) |
| `cyber-cyan` | `#45CFE9` | เส้นไล่สี, glow, halo |
| `cyber-ink` | `#111A30` | หัวข้อ/ข้อความหลัก |
| `cyber-muted` | `#5F7088` | ข้อความรอง |
| `cyber-line` | `#D7E5F8` | เส้นกรอบ, separator |
| `cyber-paper` | `#F8FBFF` | พื้นรอง |

Tailwind: `bg-cyber-blue`, `text-cyber-ink`, `font-display`, `font-label`, `font-wordmark` · Kit class: `copie-ui` (ครอบหน้า), `copie-heading`, `copie-eyebrow`, `copie-status`, `copie-index`, `copie-panel`, `copie-response`, `copie-input`, `copie-halo`, `copie-floor`, `copie-mascot`

**กติกา HeroUI:** ใช้ component ของ HeroUI ก่อนเสมอ (Button, TextField, RadioGroup, Table, Card, Chip, Drawer, ProgressBar, Tooltip, Toast) แล้วปรับหน้าตาผ่าน variable ใน `theme.css` — ห้ามเขียน CSS ทับ class ภายในของ HeroUI ทีละจุด ถ้าต้องการหน้าตาเฉพาะ (เช่นช่องพิมพ์แบบ pill) ให้ทำ wrapper ใน `core/ui/`

### COPIE 2.5D — state และภาพ

| State | ภาพ | ใช้เมื่อ | Mockup |
|---|---|---|---|
| `welcome` | `copie-front-laptop` | Login, Onboarding | 01, 02 |
| `idle` | `copie-idle` | เปิดหน้า / รอ | — |
| `listening` | `copie-listening` | ผู้ใช้กำลังพิมพ์ | 03 |
| `thinking` | `copie-thinking` | รอ `/api/chat` | — |
| `responding` | `copie-responding` | ได้คำตอบ (2.5 วินาที) | 04 |
| `success` | `copie-success` | ได้ `skill_radar` / ส่งแบบประเมินสำเร็จ | 11 |
| `no-answer` | `copie-no-answer` | RAG ไม่พบข้อมูล หรือ `response_type: error` | — |
| `skill-guide` | `copie-skill-guide` | ก่อนเริ่ม / ระหว่างทำแบบประเมิน | 09, 10 |

- เปลี่ยนภาพแบบ crossfade 200ms (preload ทุก state ตอนเข้า `/chat`) + `copie-mascot-breathe` ตอนนิ่ง
- `prefers-reduced-motion` → ไม่มี breathe/crossfade (kit จัดการให้แล้ว)

### Layout ตาม mockup (`WorkspaceLayout`)

| โหมด | COPIE | ใช้กับ | Mockup |
|---|---|---|---|
| `center` | ใหญ่กลางจอ + halo + floor | พิมพ์คำถาม, แนะนำแบบประเมิน | 03, 09 |
| `split` | ใหญ่กลางจอ คำตอบซ้าย/ขวา | คำตอบ `text` สั้น | 04 |
| `rail` | ย่อเป็นแถบขวา (`data-layout="rail"`) | คำตอบยาว (reading mode), ตาราง, การ์ด, ฟอร์ม, radar | 05, 07, 08, 10, 11 |
| `hidden` | ซ่อน (ปุ่ม "ซ่อนมาสคอต") | ผู้ใช้ต้องการพื้นที่อ่าน | 05 |

ส่วนประกอบถาวร: wordmark ซ้ายบน, `AI // ACTIVE` + โปรไฟล์ขวาบน, ปุ่ม `History` ซ้ายล่าง, ช่องพิมพ์ pill กลางล่าง (ซ่อนตอนตอบแบบประเมิน)

### COPIE 3D (มีอยู่แล้ว — ทางเลือก)

`mascot/Copie.tsx` + `public/models/copie-mascot-web.glb` เป็นเวอร์ชัน 3D (React Three Fiber) พร้อมหน้า `/mascot-demo` — แผนหลักใช้ 2.5D ตามที่ทีมตัดสินใจ เวอร์ชัน 3D จะเก็บไว้เป็นทางเลือกหรือถอดออก ให้ตัดสินใจก่อน Day 2 (ถ้าถอด ให้ลบ `three`, `@react-three/*`, `Copie.tsx`, `/mascot-demo`, GLB)

### `modules/core/api.ts`

```ts
export async function api<T>(path: string, init?: RequestInit): Promise<T>
// - แนบ Authorization จาก getToken() ของ @/modules/user (P2)
// - timeout 30s ด้วย AbortController
// - 401 → clear token → router.push('/login')
// - error → throw new ApiError(status, detail) ให้ UI แสดง toast (HeroUI Toast)
export const chatApi = {
  send: (body: ChatRequest) => api<AgentResponse>('/api/chat', {...}),
  submitAssessment: (body: AssessmentSubmit) => api<AgentResponse>('/api/assessment/submit', {...}),
};
```

### `chatStore` (zustand)

```ts
{
  conversationId: string | null;
  messages: ChatMessage[];                 // จาก contract
  copieState: CopieMascotState;            // จาก @/modules/mascot
  layout: 'center' | 'split' | 'rail' | 'hidden';
  pending: boolean;
  send(text: string): Promise<void>;
  submitAssessment(answers): Promise<void>;
  loadConversation(detail: ConversationDetail): void;   // P2 เรียกจาก HistorySidebar
  newConversation(): void;
}
```

`layout` เลือกอัตโนมัติจาก `response_type`: `text` สั้น → `split`, `text` ยาว / `course_table` / `cards` / `assessment_form` / `skill_radar` → `rail`

## Implementation steps

### Phase 0 — Kickoff + Contract (Day 1 09:00–12:00)

1. ✅ repo, scaffold Next.js 16, rewrites `/api/*`, `types/contract.ts` (ทำแล้ว — ดู commit แรกของ repo)
2. ✅ ธีม White Cyberism: HeroUI v3, ฟอนต์ 4 บทบาท, asset kit sync, `CopieMascot` 2.5D, หน้า `/` เป็น theme preview
3. ตั้ง branch protection + CODEOWNERS ด้วย username จริง, นำ review Contract ร่วมกับ P3

Exit: **M0** — ทุกคน clone แล้ว `npm ci && npm run dev` เห็น theme preview

### Phase 1 — `ui/` + app shell (Day 1 PM)

1. `core/ui/`: `AppHeader` (wordmark + สถานะ + โปรไฟล์), `HistoryButton`, `ChatInput` (pill + send), `Icon` (ใช้ SVG ใน `/copie-ui/icons/` แบบ CSS mask ให้เปลี่ยนสีได้), `StatusLabel`
2. `modules/core/api.ts` + หน้า `/chat` ที่มี layout เปล่า
3. `page.tsx` redirect (ใช้ `userStore` ของ P2 หรือ token ชั่วคราว)

Exit: **M1** — คนอื่นใช้ `ui/`, ธีม และ `api.ts` ได้, `npm run build` ผ่าน

### Phase 2 — Mascot + layout modes (Day 2)

1. AM: crossfade ระหว่าง state, preload ภาพ, ตัดสินใจเรื่อง 3D (เก็บ/ถอด)
2. PM: `WorkspaceLayout` 4 โหมด (`center`/`split`/`rail`/`hidden`) พร้อม transition ด้วย `motion` ตาม mockup 03 → 04 → 05 · ปุ่มทดสอบโหมดใน `/chat?debug=1`

Exit: **M2** — สลับ state และ layout ได้จาก store, หน้าตาตรง mockup 03/04/05

### Phase 3 — Workspace (Day 3 AM)

1. `ChatInput` (Enter ส่ง, Shift+Enter ขึ้นบรรทัด, disable ตอน pending, จำกัด 1000 ตัวอักษร)
2. `MessageList` แสดงคำตอบผ่าน Renderer (ใช้ mock ของ P6) · `chatStore` + mapping → state/layout

### Phase 4 — Wire real API + รวมชิ้นของทีม (Day 3 PM)

1. `send()` เรียก `/api/chat` จริง, `submitAssessment()` เรียก `/api/assessment/submit`
2. วาง `<ResponseRenderer response onAsk onSubmitAssessment />` (P6), `HistorySidebar` (P2), `FeedbackBar` (P2), `SuggestedPrompts` (P7), `CopyButton`/`ExportMenu` (P8)
3. greeting ใช้ `display_name` จาก `userStore`

Exit: **M3** — ถามจาก UI แล้วได้คำตอบจริงจาก backend ครบทุก response_type

### Phase 5 — Integration lead (Day 4)

1. AM: รวม PR, แก้ conflict, เดิน Demo 1–6 กับ P8 เทียบกับ mockup, จัดลำดับบั๊ก
2. PM: responsive (1440/1024/390 — kit ย่อมาสคอตที่ ≤ 900px), loading/error/empty state, `Dockerfile` frontend

Exit: **M4** — Demo 1–6 ผ่านบน develop, merge main เป็น `v0.9`

### Phase 6 — Polish + Release (Day 5)

1. AM: transition ระหว่างคำตอบ (`copie-answer-enter`, `copie-streak`), hover/focus, ตรวจทุกหน้ากับ mockup
2. PM: Code Freeze 15:00 → `release/v1.0` → tag → ซ้อม Demo

Exit: **M5**

## Required tests

| ประเภท | สิ่งที่ต้องทดสอบ |
|---|---|
| Build | `npm run lint` + `npm run build` ผ่านทุก PR |
| Visual | เทียบหน้า 01–11 กับ mockup ที่ 1672×941: ตำแหน่ง wordmark / History / input / มาสคอต ตรง |
| Manual | COPIE ครบ 8 state, ไม่กระพริบตอนเปลี่ยนภาพ, reduced motion หยุด animation |
| Manual | ส่งข้อความซ้ำเร็วๆ ไม่ส่งซ้ำ (pending lock), 401 พาไป login |
| Responsive | 1440 / 1024 / 390 ไม่มี horizontal scroll, input ไม่ถูกคีย์บอร์ดบัง |
| E2E | Demo 1–6 ใน `09_INTEGRATION_ACCEPTANCE_RUNBOOK.md` |

## Acceptance checklist

- [ ] ธีม White Cyberism + ฟอนต์ 4 บทบาทใช้ทั้งเว็บ, component มาจาก HeroUI ที่ปรับธีมแล้ว
- [ ] COPIE 2.5D เปลี่ยนภาพตามสถานะจริงของ request (thinking ระหว่างรอ, no-answer เมื่อไม่พบข้อมูล)
- [ ] Layout 4 โหมดตาม mockup และเปลี่ยนอัตโนมัติตาม `response_type`
- [ ] `/chat` ส่งคำถามได้และแสดงทุก `response_type` ผ่าน Renderer
- [ ] redirect login/onboarding/chat ถูกต้องทุกกรณี
- [ ] responsive 3 ขนาด, keyboard ใช้งานได้, focus มองเห็น
- [ ] ไม่มี secret ใน frontend (มีแค่ `NEXT_PUBLIC_GOOGLE_CLIENT_ID`)
- [ ] `docker compose up --build` แล้วเว็บเปิดได้ที่ :3000

## Branch / PR breakdown

1. `core/white-cyberism-theme` — HeroUI, ฟอนต์, asset kit sync, CopieMascot, theme preview
2. `core/ui-shell` — `ui/` components, AppHeader, ChatInput, api.ts
3. `mascot/state-transitions` — crossfade, preload, ตัดสินใจเรื่อง 3D
4. `core/workspace-layouts` — WorkspaceLayout 4 โหมด, MessageList, chatStore
5. `core/wire-chat-api` — ต่อ API จริง + วางชิ้นของทีม
6. `core/responsive` — responsive, states, Dockerfile
7. `core/polish` → `release/v1.0`

## Completion report requirements

สร้าง `docs/handoffs/P1-frontend-core.md` ระบุเพิ่ม: component tree ของ `/chat`, ตาราง state/layout → trigger, วิธีเพิ่ม state/ภาพใหม่ (แก้ kit → sync → `states.ts`), screenshot เทียบ mockup ทุกหน้า, จุด integration ที่ยังมีปัญหา
