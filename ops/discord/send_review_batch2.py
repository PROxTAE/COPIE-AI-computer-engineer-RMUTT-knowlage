#!/usr/bin/env python
"""Send Batch 2 PR review and merge notifications to Discord."""
import json
from pathlib import Path
from discord_api import Discord, load_dotenv

HERE = Path(__file__).resolve().parent
IDS_FILE = HERE / "out" / "discord-ids.json"


def main():
    load_dotenv()
    api = Discord()
    ids = json.loads(IDS_FILE.read_text(encoding="utf-8"))
    chans = ids["channel_ids"]
    roles = ids["role_ids"]

    # 1. Post to #pull-requests
    summary_embed = {
        "title": "🚀 สรุปผลการ Review & Merge PRs (Phase 2–4)",
        "description": "ทุก PR ผ่านการตรวจ Code Quality, Contract, CI และ Rule Check ทั้งหมด เรียบร้อยแล้วและถูก **Merge เข้า `develop`** เรียบร้อยแล้วครับ!",
        "color": 0x10B981,
        "fields": [
            {
                "name": "✅ P5 · tools (#6, #7, #8, #11)",
                "value": (
                    "• [PR #6: data(tools): complete verified curriculum years 3-4](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/6) — แผน 141 หน่วยกิต 8 เทอม\n"
                    "• [PR #7: feat(tools): implement curriculum queries](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/7) — Service ค้นรายวิชา & Fuzzy\n"
                    "• [PR #8: feat(tools): add skill assessment and scoring](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/8) — แบบประเมิน 12 ข้อ & สูตรคำนวณ\n"
                    "• [PR #11: docs(tools): audit curriculum and hand off study plan](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/11) — Handoff report & study plan"
                ),
                "inline": False,
            },
            {
                "name": "✅ P6 · renderer (#9, #10, #18)",
                "value": (
                    "• [PR #9: feat(renderer): add core, fixtures and response components](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/9) — Dynamic UI ครบทุก response_type + `/dev`\n"
                    "• [PR #10: feat(renderer): animate responses and finish keyboard access](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/10) — Animation & Keyboard a11y\n"
                    "• [PR #18: data(renderer): use the real skill assessment questions](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/18) — ซิงค์แบบประเมินจริงจาก `skill_v1.json`"
                ),
                "inline": False,
            },
            {
                "name": "✅ P3 · agent (#12, #13, #14, #15, #17)",
                "value": (
                    "• [PR #14: fix(agent): use available Gemini model and skip retry on 4xx](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/14) — `gemini-3.1-flash-lite`\n"
                    "• [PR #12: feat(agent): add tool adapters with temporary stubs](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/12) — Service adapters & generator\n"
                    "• [PR #13: feat(agent): wire /api/chat to orchestrator](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/13) — ต่อ `/api/chat` เข้าสมองกลาง\n"
                    "• [PR #15: feat(agent): add assessment submit and multi-step skill flow](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/15) — Flow ประเมิน skill ครบวงจร\n"
                    "• [PR #17: feat(agent): add backend Dockerfile and docker compose](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/17) — Docker setup & index lifecycle"
                ),
                "inline": False,
            },
            {
                "name": "✅ P4 · rag (#16)",
                "value": (
                    "• [PR #16: feat(rag): add Chroma ingest pipeline and long-section chunking](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/16) — Chroma ingest & chunking > 800 chars"
                ),
                "inline": False,
            },
        ],
        "footer": {"text": "COPIE · CI/CD & Review Bot"},
    }

    api.send_message(chans["pull-requests"], {"embeds": [summary_embed]})
    print("Posted summary to #pull-requests")

    # 2. Notify P3
    p3_msg = (
        f"🎉 <@400608356492115968> (<@&{roles['p3-agent']}>)\n"
        "PR ทั้งหมดของคุณ (#12, #13, #14, #15, #17) ผ่านการรีวิวและ **Merge เข้า `develop`** ครบถ้วนแล้วครับ!\n"
        "✨ ระบบตอนนี้เชื่อม `/api/chat`, `/api/assessment/submit`, Gemini LLM, Tools จริง (P5) และ RAG จริง (P4) พร้อม Docker เรียบร้อยแล้ว\n"
        "💡 **คำแนะนำ:** รัน `git switch develop && git pull --ff-only origin develop`"
    )
    api.send_message(
        chans["p3-agent"],
        {"content": p3_msg, "allowed_mentions": {"users": ["400608356492115968"], "roles": [roles["p3-agent"]]}},
    )
    print("Notified P3")

    # 3. Notify P4
    p4_msg = (
        f"🎉 <@236323936223100928> (<@&{roles['p4-rag']}>)\n"
        "PR #16 ของคุณ (`rag/ingest-pipeline`) ผ่านการรีวิวและ **Merge เข้า `develop`** เรียบร้อยแล้วครับ!\n"
        "💡 **Next steps:**\n"
        "```bash\n"
        "git switch develop\n"
        "git pull --ff-only origin develop\n"
        "```\n"
        "จากนั้นสามารถลุยต่อใน Phase ถัดไป (`rag/vector-retriever` หรือ Hybrid Search BM25 + RRF) ได้เลยครับ"
    )
    api.send_message(
        chans["p4-rag"],
        {"content": p4_msg, "allowed_mentions": {"users": ["236323936223100928"], "roles": [roles["p4-rag"]]}},
    )
    print("Notified P4")

    # 4. Notify P5
    p5_msg = (
        f"🎉 <@381391956795850754> (<@&{roles['p5-tools']}>)\n"
        "PR ทั้งหมดของคุณ (#6, #7, #8, #11) ผ่านการรีวิวและ **Merge เข้า `develop`** เรียบร้อยแล้วครับ!\n"
        "✨ ข้อมูลหลักสูตรครบ 8 ภาคการศึกษา (141 หน่วยกิต), Curriculum Service, และระบบประเมิน Skill คำนวณได้ถูกต้องแม่นยำ\n"
        "💡 **คำแนะนำ:** รัน `git switch develop && git pull --ff-only origin develop`"
    )
    api.send_message(
        chans["p5-tools"],
        {"content": p5_msg, "allowed_mentions": {"users": ["381391956795850754"], "roles": [roles["p5-tools"]]}},
    )
    print("Notified P5")

    # 5. Notify P6
    p6_msg = (
        f"🎉 <@286434245210144768> (<@&{roles['p6-renderer']}>)\n"
        "PR ทั้งหมดของคุณ (#9, #10, #18) ผ่านการรีวิวและ **Merge เข้า `develop`** เรียบร้อยแล้วครับ!\n"
        "✨ Dynamic UI Components ครบทุก response_type พร้อม Animation, Keyboard a11y และข้อมูลประเมินจริงใน `/dev` สวยงามมากครับ\n"
        "💡 **คำแนะนำ:** รัน `git switch develop && git pull --ff-only origin develop`"
    )
    api.send_message(
        chans["p6-renderer"],
        {"content": p6_msg, "allowed_mentions": {"users": ["286434245210144768"], "roles": [roles["p6-renderer"]]}},
    )
    print("Notified P6")


if __name__ == "__main__":
    main()
