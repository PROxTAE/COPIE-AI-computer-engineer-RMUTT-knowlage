#!/usr/bin/env python
"""Send PR review and merge notifications to Discord."""
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
        "title": "🎉 สรุปผลการ Review & Merge PRs (Phase 1–2 AM)",
        "description": "ทุก PR ผ่านการตรวจ Code Quality, Contract, CI และ Rule Check ทั้งหมด เรียบร้อยแล้วและถูก **Merge เข้า `develop`** เรียบร้อยแล้วครับ!",
        "color": 0x10B981,
        "fields": [
            {
                "name": "✅ PR #1 · agent (P3)",
                "value": "[feat(agent): add mock chat scaffold](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/1)\n• Contract-compliant mock chat & assessment endpoints\n• 16 passing tests",
                "inline": False,
            },
            {
                "name": "✅ PR #2 · rag (P4)",
                "value": "[data(rag): add verified department knowledge and search stub](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/2)\n• ข้อมูลภาควิชา 10 ไฟล์ + SOURCES.md พร้อมการค้นคืน Lexical Search\n• 46 passing tests (held-out hit@4 100%)",
                "inline": False,
            },
            {
                "name": "✅ PR #3 · agent (P3)",
                "value": "[feat(agent): add Gemini LLM client and rule router](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/3)\n• Gemini client (timeout/retry/JSON mode) + Regex Rule Router\n• 31 passing tests",
                "inline": False,
            },
            {
                "name": "✅ PR #4 · agent (P3)",
                "value": "[feat(agent): add LLM intent router with few-shot prompt](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/4)\n• LLM Intent Router (few-shot + prompt builder) พร้อม fallback\n• 42 passing tests",
                "inline": False,
            },
            {
                "name": "✅ PR #5 · tools (P5)",
                "value": "[data(tools): add verified year 1-2 curriculum](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/5)\n• ข้อมูลหลักสูตร ปี 1–2 จากเล่มหลักสูตรจริง 2568 พร้อม Pydantic validation\n• All tests passed",
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
        "PR ของคุณ (#1, #3, #4) ผ่านการรีวิวและ **Merge เข้า `develop`** เรียบร้อยแล้วครับ!\n"
        "💡 **Next steps:**\n"
        "```bash\n"
        "git switch develop\n"
        "git pull --ff-only origin develop\n"
        "```\n"
        "จากนั้นสามารถแตก branch ทำงาน Phase ถัดไป (`agent/orchestrator`) ได้เลยครับ"
    )
    api.send_message(
        chans["p3-agent"],
        {"content": p3_msg, "allowed_mentions": {"users": ["400608356492115968"], "roles": [roles["p3-agent"]]}},
    )
    print("Notified P3")

    # 3. Notify P4
    p4_msg = (
        f"🎉 <@236323936223100928> (<@&{roles['p4-rag']}>)\n"
        "PR #2 ของคุณ (`rag/knowledge-v1`) ผ่านการรีวิวและ **Merge เข้า `develop`** เรียบร้อยแล้วครับ!\n"
        "💡 **Next steps:**\n"
        "```bash\n"
        "git switch develop\n"
        "git pull --ff-only origin develop\n"
        "```\n"
        "จากนั้นสามารถแตก branch ทำงาน Phase ถัดไป (`rag/chunk-embed` หรือ Vector search) ได้เลยครับ"
    )
    api.send_message(
        chans["p4-rag"],
        {"content": p4_msg, "allowed_mentions": {"users": ["236323936223100928"], "roles": [roles["p4-rag"]]}},
    )
    print("Notified P4")

    # 4. Notify P5
    p5_msg = (
        f"🎉 <@381391956795850754> (<@&{roles['p5-tools']}>)\n"
        "PR #5 ของคุณ (`tools/curriculum-data-v1`) ผ่านการรีวิวและ **Merge เข้า `develop`** เรียบร้อยแล้วครับ!\n"
        "💡 **Next steps:**\n"
        "```bash\n"
        "git switch develop\n"
        "git pull --ff-only origin develop\n"
        "```\n"
        "จากนั้นสามารถแตก branch ทำงาน Phase ถัดไป (ข้อมูลปี 3–4 และ `tools/curriculum-service`) ได้เลยครับ"
    )
    api.send_message(
        chans["p5-tools"],
        {"content": p5_msg, "allowed_mentions": {"users": ["381391956795850754"], "roles": [roles["p5-tools"]]}},
    )
    print("Notified P5")


if __name__ == "__main__":
    main()
