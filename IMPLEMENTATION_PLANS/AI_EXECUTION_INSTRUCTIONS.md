# วิธีส่งแผนให้ AI Coding Agent

ใช้ข้อความนี้เมื่อให้ AI (Claude Code / Cursor / Copilot ฯลฯ) ช่วยทำงานในส่วนของตัวเอง แนบไฟล์ 00 ทั้ง 3 ไฟล์ + แผนของตัวเอง

```text
Implement my assigned module of the COPIE project in the current repository.

Authoritative files, in order:
1. IMPLEMENTATION_PLANS/00_SHARED_PROJECT_CONTEXT.md
2. IMPLEMENTATION_PLANS/00_API_AND_DATA_CONTRACTS.md
3. IMPLEMENTATION_PLANS/00_GIT_DELIVERY_RULES.md
4. IMPLEMENTATION_PLANS/<MY_PLAN_FILE>.md
5. IMPLEMENTATION_PLANS/09_INTEGRATION_ACCEPTANCE_RUNBOOK.md

Scope:
- Only edit files and folders that my plan lists under "Ownership". If something outside my
  ownership must change, stop and tell me what and why instead of editing it.
- Never edit frontend/src/types/contract.ts or backend/app/schemas/contract.py unless I say
  this is a contract/* branch.
- Follow the contract exactly. Do not invent fields, endpoints or response types.

Stack versions: Next.js 16 App Router + React 19 + TypeScript + Tailwind CSS v4 (tokens via @theme in
globals.css, no tailwind.config), motion ("motion/react"), @react-three/fiber v9, Node 22; backend Python 3.11 +
FastAPI + Pydantic v2. Do not use APIs from older Next.js versions (pages router, next lint, middleware.ts,
synchronous params).

Goal: a simple, working implementation for a 5-day student mini project — not production.
Keep code small and readable. No extra frameworks beyond the stack in my plan.
Curriculum data, credits and skill scores must come from data files and formulas, never from the LLM.
Mocks/stubs are allowed only where my plan allows them (before Day 3 / in /dev and tests).

Work phase by phase from my plan. After each phase, run the checks listed in my plan and
tell me the results.

Git rules (strict):
- Do NOT run git commit, git push, open PRs, or merge. I will do all git operations myself.
- Do NOT add any AI attribution anywhere: no "Co-Authored-By", no "Generated with ...",
  no AI tool names in code comments, commit message suggestions or PR text.
- Do NOT create AI tool files in the repo (.claude/, CLAUDE.md, .cursor/, AGENTS.md, etc.).
- When you suggest a commit message, use: <type>(<module>): <summary>

When a phase is done, give me: files changed, how to run/test, and anything still missing.
```

แทน `<MY_PLAN_FILE>` ด้วยไฟล์ของตัวเอง เช่น `04_DEPARTMENT_RAG.md` แล้วสั่งต่อท้ายได้ เช่น "เริ่ม Phase 2"

## ข้อควรจำ

- **AI เขียน, เรา commit** — อ่าน diff ทุกไฟล์ก่อน `git add` และต้องอธิบายโค้ดได้เอง
- ตรวจก่อน push ทุกครั้ง: `bash scripts/check-ai-watermark.sh --range origin/develop..HEAD`
- ปิด co-author/attribution ใน settings ของเครื่องมือที่ใช้ (เช่น Claude Code: `includeCoAuthoredBy: false`)
- ถ้า AI สร้างไฟล์ config ของตัวเองในโฟลเดอร์โปรเจกต์ → `.gitignore` กันไว้แล้ว แต่ให้ตรวจ `git status` อีกรอบ
- ห้ามให้ AI ใช้ API key จริงในโค้ด — ใส่ใน `.env` เท่านั้น
