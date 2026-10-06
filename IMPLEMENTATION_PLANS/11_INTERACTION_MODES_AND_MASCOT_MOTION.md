# COPIE — แผนทำ Interaction Modes และมาสคอตที่โต้ตอบได้

เอกสารส่งต่องานหลัง Mini Project รุ่นแรก เป้าหมายคือให้ COPIE ตัวเดิมเปลี่ยนทั้งบรรยากาศเว็บ ภาพมาสคอต และสไตล์การตอบตามโหมดที่ผู้ใช้เลือก พร้อมตอบสนองต่อเมาส์ การแตะ และสถานะสนทนาอย่างเป็นธรรมชาติ

## 1. ผลลัพธ์ที่ต้องการ

1. ผู้ใช้เลือก `normal`, `devil` หรือ `developer` ในหน้า `/chat` ได้ และเห็นการเปลี่ยนทันทีที่ธีม ป้ายสถานะ และมาสคอต
2. คำตอบของ COPIE ใช้ข้อมูลและเครื่องมือชุดเดิม แต่ปรับน้ำเสียงตามโหมดที่เลือกในแต่ละข้อความ
3. มาสคอตภาพ 2.5D เดิมเลื่อน/เอียงตามตำแหน่งเมาส์เล็กน้อย, ตอบสนองต่อ hover และยุบเด้งเมื่อกด โดยไม่ต้องแยกดวงตาหรือสร้างโมเดล 3D
4. โหมดและ interaction ทำงานใน `center`, `split`, `rail`, `hidden` ตามรูปแบบการจัดวางเดิม โดยไม่ทำให้แชต แบบประเมิน ประวัติ หรือแหล่งอ้างอิงเสีย

**คำที่ใช้ในโค้ด:** `interactionMode` = บุคลิกและธีม (`normal | devil | developer`); `layout` หรือ `WorkspaceMode` = การจัดหน้า (`center | split | rail | hidden`); `copieState` = ท่าตามสถานะ AI (`idle`, `thinking` ฯลฯ) ทั้งสามเรื่องเป็น state คนละแกน ห้ามใช้ตัวแปร `mode` ตัวเดียวแทนทั้งหมด `/dev` เดิมเป็นหน้า renderer playground ไม่ใช่ Developer Mode

## 2. สิ่งที่มีอยู่แล้วและใช้เป็นต้นทาง

| เรื่อง | ไฟล์ปัจจุบัน | หมายเหตุ |
| --- | --- | --- |
| ภาพมาสคอต 8 สถานะปกติ | `assets/web-ui/mascot/states/` | PNG โปร่งใส 1089 × 1445 |
| Devil Mode 8 สถานะ | `assets/web-ui/mascot/modes/devil/states/` | ไฟดวงตา/หูฟังชมพูม่วง |
| Developer Mode 8 สถานะ | `assets/web-ui/mascot/modes/developer/states/` | ไฟฟ้าเขียวและอนุภาควงจร |
| WebP สำหรับเว็บ | `frontend/public/copie-ui/mascot/` และ `.../mascot/modes/{devil,developer}/` | สร้างโดย `python scripts/sync_ui_assets.py`; อย่าแก้ WebP โดยตรง |
| พื้นหลัง/halo/กรอบ/เอฟเฟกต์โหมด | `assets/web-ui/backgrounds/`, `frames/`, `effects/`, `icons/` | ดู mapping และสีใน `assets/web-ui/MODES.md` |
| พรีวิว | `assets/web-ui/mode-preview.png`, `assets/web-ui/mascot/modes/states-preview.png` | ตรวจหน้าตาทั้งสามธีมและทุกท่า |
| ภาพใน React | `frontend/src/modules/mascot/states.ts`, `CopieMascot.tsx` | ตอนนี้รองรับเฉพาะชุดปกติ; ซ้อน 8 ภาพและ crossfade |
| สถานะสนทนา/ท่า/layout | `frontend/src/modules/core/chatStore.ts` | Zustand; `copieState` เปลี่ยนตามคำตอบ |
| จุดที่วางมาสคอต | `frontend/src/modules/core/workspace/WorkspaceLayout.tsx`, `MascotSidebar.tsx` | มีทั้งตำแหน่งกลางและ rail |
| หน้าแชตและช่องเลือกโหมด | `frontend/src/modules/core/workspace/ChatPage.tsx` | ยังไม่มีตัวเลือก interaction mode |
| ธีมปัจจุบัน | `frontend/src/modules/core/theme/theme.css`, `assets/web-ui/styles/` | มีทั้ง CSS variables และสี hardcode ในบาง component |
| ฝั่งคำตอบ | `backend/app/modules/agent/orchestrator.py`, `generator.py`, `prompts.py` | Gemini ผ่าน `llm_client.py`; มี template fallback |
| API contract | `frontend/src/types/contract.ts`, `backend/app/schemas/contract.py` | ต้องเปลี่ยนให้ตรงกัน; ดูกติกา contract ของ repo |

ก่อนแก้ frontend ให้อ่าน `frontend/AGENTS.md` และคู่มือ Next.js ของเวอร์ชันที่ติดตั้งตามไฟล์นั้น หากเริ่มจาก working tree นี้ ให้ตรวจ `git status` ก่อน เพราะ asset โหมดอาจยังเป็นไฟล์ที่ไม่ได้ commit

## 3. ความหมายของแต่ละโหมด

| โหมด | โทนคำตอบ | ภาพและสี | ตัวอย่างการตอบเมื่อผู้ใช้บอกว่า “เขียนโปรแกรมไม่เก่ง” |
| --- | --- | --- | --- |
| Normal | เป็นมิตร ชัดเจน ชวนถามต่อ | White Cyberism, น้ำเงิน/ฟ้า, มาสคอตชุดปกติ | “เริ่มจากพื้นฐานได้ครับ ตอนนี้ติดเรื่องไหนมากที่สุด” |
| Devil | ตรง กระตุ้นให้ทบทวนสมมติฐาน เสนอการลงมือพิสูจน์ | พื้นกรมท่า แสงชมพูม่วง มาสคอต Devil | “อย่าเพิ่งตัดสินว่าไม่ไหว ลองโจทย์สั้น ๆ แล้วดูว่าจุดที่ติดคืออะไร” |
| Developer | กระชับ เป็นขั้นตอน ใช้ตัวอย่างเทคนิคเมื่อเหมาะ | พื้นเขียวกรมท่า แสงมิ้นต์ มาสคอต Developer | “แยกปัญหาเป็น syntax, logic และการ debug ก่อน แล้วลองทำตัวอย่างทีละส่วน” |

- Devil Mode ต้องเป็น **opt-in** และเปลี่ยนกลับได้ทันที เข้มกับเหตุผล/เป้าหมาย ไม่โจมตีตัวตน ไม่ประชด ไม่ดูถูก และไม่สรุปว่าผู้ใช้ไม่เหมาะกับสาขา
- Developer Mode ไม่ใช่การเปิดสิทธิ์พิเศษหรือเผยข้อมูลภายในระบบ เป็นเพียงสไตล์ช่วยเรียนรู้แบบเทคนิค
- ทุกโหมดใช้ฐานข้อมูลภาค หลักสูตร ผลประเมิน และ source เดียวกัน ห้ามให้โหมดเปลี่ยนข้อเท็จจริง คะแนน หน่วยกิต วันรับสมัคร หรือ citation
- ถ้าคำถามต้องการข้อมูลที่ระบบไม่รู้ ให้บอกว่าไม่ทราบตามพฤติกรรมเดิม ไม่แต่งคำตอบเพื่อรักษาบุคลิก

## 4. ลำดับงาน

### A. เพิ่ม state ของโหมดและหน้าควบคุม

1. เพิ่ม type `InteractionMode = "normal" | "devil" | "developer"` ใน frontend module ที่เหมาะสม แยกจาก `WorkspaceMode` และ `CopieMascotState`
2. เก็บ `interactionMode` และ action `setInteractionMode` ใน store ของหน้าแชต ค่าเริ่มต้น `normal`; บันทึก preference ลง `localStorage` แบบ versioned key เพื่อคงค่าหลัง reload โดยอ่านหลัง hydration อย่างระวัง
3. ทำปุ่มเลือกโหมดที่ใช้งานได้จริงในหน้า `/chat`: ชื่อและคำอธิบายสั้น, สถานะ `aria-pressed` หรือ radio group, focus ที่เห็นชัด, ใช้แป้นพิมพ์ได้; บนมือถือไม่บังช่องพิมพ์หรือคำตอบ
4. แสดงโหมดปัจจุบันใน header หรือใกล้มาสคอต รวมถึงคำอธิบาย Devil Mode ก่อนเปิดครั้งแรกที่ชัดว่าเป็นสไตล์การคุย
5. การเปลี่ยนโหมดระหว่างมีคำขอค้างให้มีผลกับ **คำขอถัดไป**; snapshot โหมดของแต่ละ request เพื่อไม่ให้คำตอบที่กำลังกลับมาถูกตีความด้วยโหมดใหม่

### B. เปลี่ยน theme และ asset ตามโหมด

1. วาง `data-copie-mode={interactionMode}` ที่ root `.copie-ui` ใน `ChatPage` แล้วใช้ CSS variables ภายใต้ selector ของแต่ละโหมดสำหรับพื้น ข้อความ ปุ่ม ฟอร์ม focus เส้นกรอบ การ์ด ตาราง และข้อความ error ตรวจ hardcoded light colors ใน component จริงด้วย
2. ใช้ asset mapping จาก `assets/web-ui/MODES.md`: พื้นหลัง, halo, frame, effect และ icon ต้องเป็นโหมดเดียวกัน ใช้โทน Normal เดิมเมื่อไม่มีโหมดกำหนด
3. ขยาย `frontend/src/modules/mascot/states.ts` เป็น lookup แบบ `interactionMode + copieState -> WebP path`; `welcome` ใช้ `copie-front-laptop` เหมือนเดิม เพิ่ม prop `interactionMode` ใน `CopieMascot` แล้วส่งผ่าน `WorkspaceLayout` และ `MascotSidebar`
4. รักษาการ crossfade เมื่อเปลี่ยนทั้งท่าและโหมดโดยไม่เกิดเฟรมว่าง หลีกเลี่ยง preload ทุกภาพ 24 ภาพพร้อมกัน: โหลดภาพของโหมดปัจจุบันตามจำเป็น และเตรียม `idle` ของโหมดใหม่ก่อน transition หากต้องการ
5. ตรวจภาพธีมเข้มกับพื้นจริง โดยเฉพาะตา แสงขอบ ปุ่ม feedback, SourceViewer, CourseTable, AssessmentForm และ SkillRadar

### C. ส่งโหมดไปกำหนดสไตล์คำตอบ

1. เพิ่ม field optional `interaction_mode` ใน `ChatRequest` ทั้ง TypeScript และ Pydantic ค่าเริ่มต้นฝั่ง server เป็น `normal`; พิจารณาเพิ่มใน `AssessmentSubmit` เพราะคำอธิบายผล skill อาจสร้างจาก LLM ด้วย
2. แก้ `chatApi`/store ให้แนบโหมดที่ snapshot ตอนกดส่ง ห้ามอาศัยเพียง state ใน browser เมื่อ server สร้างคำตอบ
3. ใน backend ให้ validate ด้วย enum/allowlist แล้วส่ง mode จาก `handle_chat` ไปที่ generator ทุกเส้นทางที่สร้าง prose เช่น RAG, curriculum intro, course detail, general, skill explanation และ fallback ที่ผู้ใช้เห็น
4. สร้าง style instruction แยกเป็นชั้นสั้น ๆ ใน `prompts.py` แล้วประกอบกับ system prompt ของงานเดิม **หลัง**กติกาความถูกต้อง/การอ้างอิง ไม่ให้ style instruction เปลี่ยน intent routing, tool result หรือข้อมูลดิบ
5. ถ้าต้องแสดงโหมดที่ใช้กับคำตอบเก่า ให้เพิ่ม field optional ใน `ResponseMeta` และ serialize ลงประวัติ; ระวังข้อมูลเก่าที่ไม่มี field นี้ต้องอ่านได้ โดยแสดงเป็น `normal`
6. ทดสอบตัวอย่างคำถามเดียวกันในสามโหมด: ข้อเท็จจริงและ citation เหมือนกัน แต่น้ำเสียงต่างกันอย่างเห็นได้ชัด; กรณี LLM ล่ม template fallback ต้องยังเหมาะกับโหมด

### D. Motion interaction ของมาสคอตภาพเดิม

1. เพิ่ม **outer interaction wrapper** รอบ `CopieMascot` สำหรับเลื่อน/เอียง/ย่อเด้ง อย่าเขียน `transform` ทับ `.copie-mascot-breathe` บนภาพ เพราะ CSS เดิมใช้ `transform: translateY(...)` อยู่
2. Pointer tracking: คำนวณตำแหน่ง pointer เทียบศูนย์กลาง wrapper แล้ว clamp ค่าที่นุ่มนวล เช่น `translateX` ไม่เกิน 8px, `translateY` ไม่เกิน 6px, หมุนไม่เกิน 3°; ใช้ motion value หรือ `requestAnimationFrame` เพื่อไม่ render React ทุก `pointermove`; กลับสู่จุดกลางเมื่อ pointer ออก
3. Hover: scale ประมาณ 1.02 และขยับ halo/เงาเล็กน้อย ปรับค่าจากการดูบนทั้ง `center` และ `rail`; อย่าให้ภาพสั่นหรือรบกวนการอ่าน
4. Press/tap: ยุบตัวชั่วครู่ เช่น `scaleX(1.06) scaleY(0.93)` แล้วเด้งกลับ; จัดการ `pointerup`, `pointercancel`, pointer ออกระหว่างกด และป้องกันการกดถี่จน animation ค้าง ไม่ต้องมี PNG ท่าถูกจิ้มเพิ่ม
5. การกดมาสคอตเป็น interaction ภายในหน้าเท่านั้น อย่าส่งแชตหรือเปลี่ยนโหมดโดยไม่ตั้งใจ; หากมีคำพูดสั้นหรือเสียงตอบกลับ ให้เป็น optional และไม่บันทึกใน conversation history
6. ทำจุดกดที่ใช้คีย์บอร์ด Enter/Space ได้ มี label ที่สื่อความหมาย และมี focus ring; บนอุปกรณ์ touch ใช้ tap/press โดยไม่จำลอง hover ถาวร
7. เคารพ `prefers-reduced-motion: reduce`: ปิด pointer tracking, breathe และ squash หรือใช้การเปลี่ยนสถานะแบบนิ่งที่ยังรับรู้ได้; ตรวจไม่ให้ event handler ทำงานหนักเมื่อ hidden/offscreen

### E. ตรวจรับและเก็บรายละเอียด

1. เปลี่ยนโหมดครบสามแบบในหน้าแชตโดยไม่ reload: สี พื้น halo ไอคอน และภาพมาสคอตเปลี่ยนพร้อมกัน
2. ทดสอบทุก `copieState` × ทุก `interactionMode` ด้วย debug controls หรือ gallery; ภาพต้องไม่หาย ไม่ยืด และไม่กระพริบตอนเปลี่ยนท่า
3. ทดสอบเมาส์, touch, keyboard, reduced motion, จอมือถือ, `center/split/rail/hidden` และการเข้าออกโหมดขณะ AI กำลังคิด
4. ทดสอบถามข้อมูลภาค/รายวิชาและแบบประเมิน: `response_type`, sources, หน่วยกิต, skill scores และ history ยังถูกต้อง
5. ตรวจ contrast ในธีมเข้ม และตรวจไม่ให้ header, composer, cards, table, source viewer หรือ error state ค้างสีของธีมปกติ
6. รัน `python scripts/sync_ui_assets.py`, `npm run lint`, `npm run build`, backend tests ที่เกี่ยวกับ chat/contract และทดสอบจริงใน browser อย่างน้อย desktop + mobile

## 5. ขอบเขตและข้อควรระวัง

- ใช้ภาพ 2.5D ที่สร้างแล้ว ไม่ต้องสร้าง 3D, แยกชั้นหน้า/ตา, หรือติดตั้ง animation library ใหม่เพื่อทำงานชุดแรก (`motion/react` มีใน frontend อยู่แล้ว)
- รูปภาพโหมดทั้งหมดมีขนาด 1089 × 1445 และพื้นหลังโปร่งใส; PNG ใน `assets/` เป็นต้นฉบับ, WebP ใน `frontend/public/` เป็นไฟล์สำหรับเว็บ
- ถ้าปรับ asset ต้นฉบับ ให้รัน sync script ใหม่ และตรวจภาพที่ `assets/web-ui/mascot/modes/states-preview.html`
- ไม่ใช้ CSS filter ย้อมภาพมาสคอตชุดปกติ เพราะมีภาพของแต่ละโหมดครบแล้ว
- อย่าแก้ `frontend/src/modules/core/theme/kit/*` หรือ `frontend/public/copie-ui/*` ด้วยมือ เพราะ sync script เขียนทับ; แก้ไฟล์ต้นทางใน `assets/web-ui/` หรือ theme layer ที่ไม่ถูก sync
- เมื่อแก้ contract ให้รักษา backward compatibility กับ client/history เดิมและทำตามกติกา review ของ repo

## 6. ลำดับส่งงานที่แนะนำ

1. **Slice 1 — visual mode:** ตัวเลือกโหมด + theme tokens + มาสคอต 24 ภาพ + พรีวิวทุกสถานะ
2. **Slice 2 — motion:** pointer/hover/press, keyboard/touch/reduced motion และ QA responsive
3. **Slice 3 — answer style:** request contract + backend prompts/fallback + history compatibility และ eval สามโหมด

แต่ละ slice ควรเปิดดูผลใน browser ก่อนเริ่ม slice ถัดไป แล้วส่งสรุปไฟล์ที่แก้ วิธีทดสอบ และข้อจำกัดที่ยังเหลือ
