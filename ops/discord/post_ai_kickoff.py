#!/usr/bin/env python
"""Send each COPIE workstream a focused AI context bundle and work brief."""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

from discord_api import Discord, load_dotenv

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "ai-kickoff"
MARKER = "copie-ai-kickoff-v1"

COMMON = [
    "IMPLEMENTATION_PLANS/00_SHARED_PROJECT_CONTEXT.md",
    "IMPLEMENTATION_PLANS/00_API_AND_DATA_CONTRACTS.md",
    "IMPLEMENTATION_PLANS/00_GIT_DELIVERY_RULES.md",
    "IMPLEMENTATION_PLANS/00_TIMELINE_AND_SYNC.md",
    "IMPLEMENTATION_PLANS/AI_EXECUTION_INSTRUCTIONS.md",
    "IMPLEMENTATION_PLANS/PR_TEMPLATE.md",
    "IMPLEMENTATION_PLANS/09_INTEGRATION_ACCEPTANCE_RUNBOOK.md",
    "frontend/src/types/contract.ts",
    "backend/app/schemas/contract.py",
    "docs/diagrams/copie-handoff-flow.png",
]

ROLES = {
    "p1-core-mascot": {
        "id": "P1", "plan": "01_FRONTEND_CORE_MASCOT.md", "module": "core",
        "branch": "core/white-cyberism-theme", "title": "ธีม White Cyberism + มาสคอต",
        "pr_title": "style(core): add white cyberism theme", "reviewer": "P6",
        "first": "ตรวจงานธีมที่ทำอยู่ แล้วทำให้ asset kit, ฟอนต์, HeroUI theme, CopieMascot และหน้า preview ใช้งานได้ตามแผน; ส่ง screenshot เทียบ mockup",
        "handoff": "ส่ง tokens/ui และมาสคอตให้ P2/P6; เตรียมจุดต่อ chat API ของ P3 กับ Renderer ของ P6",
        "checks": "cd frontend แล้วรัน npm run lint และ npm run build; ถ่ายภาพหน้า preview/chat",
        "files": [
            "frontend/package.json", "frontend/src/app/chat/page.tsx", "frontend/src/app/globals.css",
            "frontend/src/modules/core/README.md", "frontend/src/modules/core/theme/theme.css",
            "frontend/src/modules/mascot/README.md", "frontend/src/modules/mascot/CopieMascot.tsx",
            "frontend/src/modules/mascot/states.ts", "assets/web-ui/ASSET_GUIDE.md",
            "assets/web-ui/styles/tokens.css", "assets/mockups/ui-flow-v1/SCREEN_GUIDE.md",
            "assets/mockups/ui-flow-v1/03-chat-composing.png",
            "assets/mockups/ui-flow-v1/04-chat-answer.png",
            "assets/mockups/ui-flow-v1/05-reading-mode.png",
            "assets/mockups/ui-flow-v1/11-skill-radar.png",
            "assets/web-ui/mascot/states/copie-front-laptop.png",
            "assets/web-ui/mascot/states/copie-idle.png",
            "assets/web-ui/mascot/states/copie-thinking.png",
            "assets/web-ui/mascot/states/copie-responding.png",
        ],
    },
    "p2-user": {
        "id": "P2", "plan": "02_USER_SYSTEM.md", "module": "user",
        "branch": "user/db-and-dev-auth", "title": "ฐานข้อมูลผู้ใช้ + Dev Login",
        "pr_title": "feat(user): add dev auth and user models", "reviewer": "P3",
        "first": "ทำ models/DB, JWT และ /api/auth/dev พร้อม get_user_context/history stubs ตาม contract; ยังไม่ทำ Google Login UI ใน PR นี้",
        "handoff": "ส่ง get_user_context/history stub ให้ P3, Dev Login ให้ P8; PR ถัดไปทำ login/onboarding ให้ P1 ใช้",
        "checks": "cd backend แล้วรัน pytest ของ user และ ruff check .; แนบตัวอย่างคำตอบ /api/auth/dev",
        "files": [
            "backend/app/main.py", "backend/app/core/config.py", "backend/requirements.txt",
            "backend/app/modules/user/README.md", "frontend/src/modules/user/README.md",
            "frontend/src/app/login/page.tsx", "frontend/src/app/onboarding/page.tsx",
            "assets/mockups/ui-flow-v1/SCREEN_GUIDE.md",
            "assets/mockups/ui-flow-v1/01-login-v2.png",
            "assets/mockups/ui-flow-v1/02-onboarding.png",
            "assets/mockups/ui-flow-v1/06-history-open.png",
        ],
    },
    "p3-agent": {
        "id": "P3", "plan": "03_AI_AGENT_BACKEND.md", "module": "agent",
        "branch": "agent/backend-scaffold", "title": "Backend scaffold + mock chat",
        "pr_title": "feat(agent): add mock chat scaffold", "reviewer": "P1",
        "first": "ตรวจ scaffold ที่มีแล้ว เติม /api/chat mock ที่คืน AgentResponse ตรง contract, health/test และจุดต่อ router; ยังไม่ต่อ LLM/Tools จริงใน PR นี้",
        "handoff": "ส่ง mock /api/chat + sample response ให้ P1/P6/P8; ตกลง function signatures กับ P2/P4/P5",
        "checks": "cd backend แล้วรัน pytest และ ruff check .; แนบผลเรียก /api/health กับ /api/chat",
        "files": [
            "backend/README.md", "backend/app/main.py", "backend/app/core/config.py",
            "backend/app/modules/agent/README.md", "backend/requirements.txt",
            "backend/app/core/tests/test_health.py",
        ],
    },
    "p4-rag": {
        "id": "P4", "plan": "04_DEPARTMENT_RAG.md", "module": "rag",
        "branch": "rag/knowledge-v1", "title": "Knowledge v1 + search stub",
        "pr_title": "data(rag): add verified department knowledge", "reviewer": "P3",
        "first": "รวบรวมเอกสารภาคที่มี URL ตรวจสอบได้, ทำ SOURCES.md + knowledge Markdown และ search stub คืน RetrievedChunk; ถ้ายังหาแหล่งจริงไม่ได้ ให้ระบุ blocker ห้ามแต่งข้อมูล",
        "handoff": "ส่ง search_department_knowledge() stub และ Source schema ให้ P3; ส่งรายการแหล่งจริงให้ P8 ช่วยตรวจ",
        "checks": "ตรวจ front matter/source_url ทุกไฟล์และรัน pytest ของ rag; แนบตัวอย่าง RetrievedChunk",
        "files": [
            "backend/app/modules/rag/README.md", "data/knowledge/README.md",
            "resource/RMUTT_CE_AI_Project_Summary_COPIE.md", "backend/requirements.txt",
        ],
    },
    "p5-tools": {
        "id": "P5", "plan": "05_CURRICULUM_SKILL_TOOLS.md", "module": "tools",
        "branch": "tools/curriculum-data-v1", "title": "หลักสูตรปี 1–2 + tool stubs",
        "pr_title": "data(tools): add verified curriculum data", "reviewer": "P3",
        "first": "หาเล่มหลักสูตรที่เป็นทางการก่อน ทำ SOURCE.md, curriculum.json เฉพาะข้อมูลที่ตรวจหน้าเอกสารได้ และ function stubs; ถ้ายังไม่มีเล่มให้ทำ draft/stub และแจ้ง blocker ห้ามเดารายวิชา",
        "handoff": "ส่ง get_courses()/skill function signatures ให้ P3 และ sample course data ให้ P6; ส่งสรุปหลักสูตรให้ P4 ภายหลัง",
        "checks": "รัน validate/pytest ของ tools ตามที่มี; แนบ URL และหน้าในเล่มที่ยืนยันข้อมูล",
        "files": [
            "backend/app/modules/tools/README.md", "data/curriculum/README.md",
            "data/assessment/README.md", "resource/RMUTT_CE_AI_Project_Summary_COPIE.md",
            "assets/mockups/ui-flow-v1/07-course-table.png",
            "assets/mockups/ui-flow-v1/11-skill-radar.png",
        ],
    },
    "p6-renderer": {
        "id": "P6", "plan": "06_DYNAMIC_RENDERER.md", "module": "renderer",
        "branch": "renderer/core-and-mocks", "title": "Renderer core + fixtures + /dev",
        "pr_title": "feat(renderer): add core and fixtures", "reviewer": "P1",
        "first": "ทำ typed fixtures ครบ response_type, ResponseRenderer switch และ /dev ที่เปิดดู fixture ได้; ยังไม่ต่อ API จริง และไม่ใส่ mock ใน /chat",
        "handoff": "ส่ง <ResponseRenderer /> และ fixtures ให้ P1/P3 ใช้ตรวจ contract; รอ P5 ส่งตัวอย่างรายวิชาจริงตอนเก็บงาน",
        "checks": "cd frontend แล้วรัน npm run lint และ npm run build; แนบ screenshot หน้า /dev",
        "files": [
            "frontend/package.json", "frontend/src/modules/renderer/README.md",
            "frontend/src/modules/renderer/index.ts", "frontend/src/app/dev/page.tsx",
            "assets/web-ui/ASSET_GUIDE.md", "assets/mockups/ui-flow-v1/SCREEN_GUIDE.md",
            "assets/mockups/ui-flow-v1/04-chat-answer.png",
            "assets/mockups/ui-flow-v1/05-reading-mode.png",
            "assets/mockups/ui-flow-v1/07-course-table.png",
            "assets/mockups/ui-flow-v1/08-info-cards.png",
            "assets/mockups/ui-flow-v1/09-assessment-intro.png",
            "assets/mockups/ui-flow-v1/10-assessment-question.png",
            "assets/mockups/ui-flow-v1/11-skill-radar.png",
        ],
    },
    "p7-suggest-ml": {
        "id": "P7", "plan": "07_SUGGESTIONS_LOCAL_INTENT_ML.md", "module": "suggest",
        "branch": "suggest/prompt-chips", "title": "Suggested prompts แบบ static",
        "pr_title": "feat(suggest): add suggested prompts", "reviewer": "P1",
        "first": "ทำ SuggestedPrompts ตาม user_type/study_year ด้วยรายการคำถามที่มีในแผน; component รับ onAsk callback และไม่แตะ chatStore ของ P1 ใน PR นี้",
        "handoff": "ส่ง component + props ให้ P1; รอ questions.jsonl จาก P8 ก่อนทำ branch intent-ml แยก",
        "checks": "cd frontend แล้วรัน npm run lint และ npm run build; แนบภาพตัวอย่าง chips",
        "files": [
            "frontend/src/modules/suggest/README.md", "frontend/src/modules/suggest/index.ts",
            "backend/app/modules/intent_ml/README.md", "data/eval/README.md",
            "frontend/src/app/chat/page.tsx", "assets/mockups/ui-flow-v1/03-chat-composing.png",
        ],
    },
    "p8-export-qa": {
        "id": "P8", "plan": "08_EXPORT_QA_EVAL.md", "module": "qa",
        "branch": "qa/eval-set", "title": "ชุดคำถามประเมิน 60 ข้อ",
        "pr_title": "data(qa): add evaluation questions", "reviewer": "P3",
        "first": "สร้าง questions.jsonl 60 ข้อตาม intent/label ในแผน พร้อม expected evidence ที่ตรวจได้; อย่าแต่งเฉลยข้อมูลภาค/หลักสูตร ถ้ายังไม่ยืนยันให้ทำเครื่องหมายรอ P4/P5",
        "handoff": "ส่ง questions.jsonl ที่มี intent label ให้ P7; ส่งเคสทดสอบให้ P3/P4/P5 ตรวจเฉลย",
        "checks": "ตรวจ JSONL ทุกบรรทัด, จำนวน 60, label distribution และแหล่งอ้างอิง; แนบสรุป coverage",
        "files": [
            "frontend/src/modules/export/README.md", "data/eval/README.md",
            "scripts/eval/README.md", "assets/mockups/ui-flow-v1/05-reading-mode.png",
        ],
    },
}


def prompt(role: dict) -> str:
    return f"""ฉันรับผิดชอบ {role['id']} ของโปรเจกต์ COPIE ต้องทำงานตามแผนให้มากที่สุดและ commit โค้ดภายในวันอาทิตย์ที่ 27 ก.ย. 2026 (เวลาไทย) งานนี้ต้องเดินต่อเนื่องจนจบส่วนที่รับผิดชอบ ไม่หยุดหลังทำ PR แรก

ให้เปิดอ่านไฟล์ใน ZIP ที่แนบทั้งหมดโดยเริ่มจาก START_HERE.md, เอกสาร 00 กลาง, AI_EXECUTION_INSTRUCTIONS.md, {role['plan']}, contract ทั้งสองฝั่ง และไฟล์ประกอบเฉพาะงาน (ภาพเป็นแบบหน้าตา ไม่ใช่ข้อมูลจริง) แล้วตรวจโค้ดใน repository ปัจจุบันก่อนแก้ อย่าทำงานซ้ำสิ่งที่มีอยู่แล้ว

เริ่มจาก PR แรก (`{role['branch']}`): {role['first']}
สิ่งที่ต้องส่งต่อให้ทีม: {role['handoff']}

ทำงานตาม Phase ของแผน {role['id']} ต่อเนื่องไปจนถึง Definition of Done โดยแยกเป็น PR เล็กตาม Branch / PR breakdown ในแผน อย่ารวมทุกอย่างใน PR เดียว หลังจบแต่ละ slice ให้ตรวจและสรุปผลเพื่อให้ฉัน commit/push/เปิด PR แล้วจึงไป slice ถัดไป ถ้างานใดต้องรอเพื่อน ให้ทำ stub/fixture ตาม contract เฉพาะระหว่างพัฒนา แจ้งว่ารอฟังก์ชันหรือข้อมูลอะไร แล้วทำงานส่วนอื่นต่อทันที

แก้เฉพาะไฟล์ที่แผนระบุว่าเป็น Ownership ของ {role['id']} ถ้าต้องแก้ contract หรือไฟล์เจ้าของอื่น ให้เสนอผลกระทบและหยุดก่อนแก้ ห้ามสร้าง field/endpoint เอง ข้อมูลภาค รายวิชา หน่วยกิต และคะแนนต้องมีแหล่งจริงหรือสูตรตรวจได้; ใช้ mock/stub เฉพาะงานพัฒนาและ tests ห้ามปล่อย mock ไว้ใน flow demo จริง

ก่อนเริ่ม ให้สรุปสั้น ๆ ว่า (1) เข้าใจ scope/contract อย่างไร (2) ไฟล์ใดมีอยู่แล้วหรือยังขาด (3) จะทำไฟล์ใดใน PR นี้ แล้วลงมือทำและรันการตรวจ: {role['checks']}

หลังแต่ละ slice รายงานไฟล์ที่แก้ ผลตรวจ หลักฐาน ข้อที่ยังรอคนอื่น และร่างข้อความ PR ตาม PR_TEMPLATE.md (PR แรกตัวอย่างชื่อ `{role['pr_title']}`, base `develop`, reviewer {role['reviewer']}) พร้อมแนะนำ slice ถัดไปทันที อย่า commit, push, เปิด PR หรือ merge แทนฉัน; ฉันจะตรวจ diff และทำ Git เองภายในสุดสัปดาห์ ห้ามใส่ AI attribution, secret หรือไฟล์ตั้งค่าของ AI ใน repo
"""


def make_bundle(key: str, role: dict) -> tuple[Path, Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    bundle = OUT / f"{role['id']}-ai-context.zip"
    prompt_file = OUT / f"{role['id']}-PROMPT_FOR_AI.txt"
    prompt_file.write_text(prompt(role), encoding="utf-8")
    paths = COMMON + [f"IMPLEMENTATION_PLANS/{role['plan']}"] + role["files"]
    unique = list(dict.fromkeys(paths))
    missing = [name for name in unique if not (ROOT / name).is_file()]
    if missing:
        raise FileNotFoundError(f"{role['id']} missing: {missing}")
    guide = (
        f"# COPIE — {role['id']} เริ่มงานกับ AI\n\n"
        f"PR แรก: `{role['branch']}` — {role['title']}\n\n"
        f"ตัวอย่างชื่อ PR: `{role['pr_title']}` · base `develop` · reviewer {role['reviewer']}\n\n"
        "## วิธีใช้\n\n"
        "1. clone/pull โปรเจกต์และเปิด AI ในโฟลเดอร์ repo; แตก ZIP นี้เพื่อดูไฟล์ทั้งหมดตาม path เดิม\n"
        "2. ถ้า AI เข้าถึง repo ได้ ให้ระบุ path เหล่านี้ให้อ่าน; ถ้าเป็นแชตที่ไม่มี repo ให้แนบไฟล์ใน ZIP เป็นรายไฟล์ โดยเฉพาะ .md, contract และภาพ .png (ZIP อย่างเดียวบาง AI อ่านไม่ได้)\n"
        "3. คัดลอก PROMPT_FOR_AI.txt ไปสั่ง AI ให้ทำต่อเนื่องตาม Phase จนจบงาน โดยแบ่งผลเป็น PR เล็กและเช็กหลังแต่ละ slice\n"
        "4. ตรวจ diff และผล test เอง; commit/push/เปิด PR เข้า develop เองตาม 00_GIT_DELIVERY_RULES.md ภายในอาทิตย์ 27 ก.ย. 2026\n"
        "5. ไฟล์ใน ZIP เป็น snapshot สำหรับบริบท ณ วันที่จัดชุด; ตรวจ develop ล่าสุดก่อนลงมือ และอย่าอัปโหลด .env หรือ token\n\n"
        "## ไฟล์ในชุดนี้\n\n" + "\n".join(f"- `{name}`" for name in unique) + "\n"
    )
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        archive.writestr("START_HERE.md", guide)
        archive.write(prompt_file, "PROMPT_FOR_AI.txt")
        for name in unique:
            archive.write(ROOT / name, name)
    return bundle, prompt_file


def find_marked(api: Discord, channel: str) -> dict | None:
    for item in api.get(f"/channels/{channel}/messages?limit=100"):
        if MARKER in (item.get("content") or ""):
            return item
    return None


def post_one(api: Discord, ids: dict, key: str, role: dict, bundle: Path, prompt_file: Path) -> str:
    channel = ids["channel_ids"][key]
    role_id = ids["role_ids"][key]
    plan = ROOT / "IMPLEMENTATION_PLANS" / role["plan"]
    role_files = "\n".join(f"• `{name}`" for name in role["files"])
    desc = (
        f"**PR แรก:** `{role['branch']}` → `develop` · {role['title']}\n"
        f"**ชื่อ PR:** `{role['pr_title']}` · reviewer {role['reviewer']}\n"
        f"**ลงมือทำ:** {role['first']}\n"
        f"**ส่งให้ใคร:** {role['handoff']}\n\n"
        "**ไฟล์ที่ต้องให้ AI อ่าน:**\n"
        "• เอกสารกลาง `00_SHARED_PROJECT_CONTEXT.md`, `00_API_AND_DATA_CONTRACTS.md`, `00_GIT_DELIVERY_RULES.md`, `00_TIMELINE_AND_SYNC.md`\n"
        f"• แผนของตัวเอง `{role['plan']}` + `AI_EXECUTION_INSTRUCTIONS.md` + `PR_TEMPLATE.md`\n"
        "• `contract.ts` และ `contract.py`\n"
        f"**ไฟล์เฉพาะงานที่แนบใน ZIP:**\n{role_files}\n\n"
        "**วิธีใช้กับ AI:** ดาวน์โหลด ZIP แล้วแตกไฟล์ตาม path; ถ้า AI อ่าน repo ได้ ให้สั่งเปิด path ในชุดนี้. "
        "ถ้าเป็น AI แบบแชต ให้แนบ `.md`/contract/ภาพจาก ZIP เป็นรายไฟล์ เพราะบางตัวอ่าน ZIP ไม่ได้. "
        "วางข้อความจากไฟล์ `PROMPT_FOR_AI.txt`; ให้ AI ทำต่อเนื่องตาม Phase จนจบงาน แยก PR เล็ก ๆ ไม่หยุดหลัง PR แรก; "
        "หลังแต่ละ slice ขอผลตรวจ/ไฟล์ที่เปลี่ยน/สิ่งที่ยังรอแล้วเจ้าของงาน commit และเปิด PR เอง\n\n"
        f"**ก่อนเปิด PR:** {role['checks']}. เจ้าของงานตรวจ diff เอง, push branch ของตัวเอง, เปิด PR เข้า `develop` "
        "ตาม `PR_TEMPLATE.md` พร้อมหลักฐาน แล้วขอ reviewer ตามกติกา. หากยังไม่เสร็จตอน cutoff ให้เปิด Draft PR. "
        "ต้องมีโค้ด commit และ PR ภายในอาทิตย์ 27 ก.ย. 2026; ห้ามแก้ contract นอก `contract/*` PR และอย่าแนบ `.env`/token ให้ AI"
    )
    payload = {
        "content": f"<@&{role_id}> 📦 ชุดเริ่มงานกับ AI สำหรับ {role['id']} — ดาวน์โหลดไฟล์แนบและเริ่ม PR แรกได้เลย\n-# {MARKER}:{key}",
        "embeds": [{"title": f"{role['id']} · {role['title']}", "description": desc, "color": 0x155FF2,
                    "footer": {"text": "COPIE · AI kickoff · รายการไฟล์ครบใน ZIP/START_HERE.md"}}],
        "allowed_mentions": {"roles": [role_id]},
    }
    if len(desc) > 4096:
        raise ValueError(f"{role['id']} Discord embed too long: {len(desc)}")
    files = [(bundle.name, bundle), (plan.name, plan), (prompt_file.name, prompt_file)]
    old = find_marked(api, channel)
    if old:
        msg = api.edit_message_files(channel, old["id"], payload, files=files)
    else:
        msg = api.send_message(channel, payload, files=files)
    if not msg.get("pinned"):
        api.pin_message(channel, msg["id"])
    return f"https://discord.com/channels/{ids['guild_id']}/{channel}/{msg['id']}"


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only", choices=list(ROLES))
    args = parser.parse_args()
    selected = [(key, role) for key, role in ROLES.items() if not args.only or key == args.only]
    prepared = [(key, role, *make_bundle(key, role)) for key, role in selected]
    for key, role, bundle, _ in prepared:
        print(f"{role['id']}: {bundle.name} {bundle.stat().st_size / 1024 / 1024:.1f} MiB")
    if args.dry_run:
        return
    load_dotenv()
    api = Discord()
    ids = json.loads((HERE / "out" / "discord-ids.json").read_text(encoding="utf-8"))
    for key, role, bundle, prompt_file in prepared:
        print(role["id"], post_one(api, ids, key, role, bundle, prompt_file))


if __name__ == "__main__":
    main()
