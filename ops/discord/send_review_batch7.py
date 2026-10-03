#!/usr/bin/env python
"""Send Batch 7 PR review and merge notifications to Discord."""
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

    # 1. Post summary embed to #pull-requests
    summary_embed = {
        "title": "⚡ สรุปผลการ Review & Merge PRs (Batch 7)",
        "description": "รีวิว PR ล่าสุดทั้งหมดเรียบร้อยแล้ว ทั้ง 3 PR ผ่านการตรวจ Code Quality, Contract, Safety, Tests และ CI 100% เขียว จึงได้ทำการ **Merge เข้า `develop`** เรียบร้อยครับ! 🎉",
        "color": 0x10B981,
        "fields": [
            {
                "name": "✅ PR #38 · rag (P4)",
                "value": (
                    "[feat(rag): add sourced FAQ and per-section source links](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/38)\n"
                    "• เพิ่ม FAQ 17 ข้อสำหรับผู้สนใจเข้าศึกษา (16 เอกสาร / 88 chunks)\n"
                    "• รองรับการอ้างอิงลิงก์ `ที่มา: <url>` ราย section ใน Chunker ให้ Agent ชี้หน้าต้นทางที่แม่นยำ"
                ),
                "inline": False,
            },
            {
                "name": "✅ PR #39 · user (P2)",
                "value": (
                    "[feat(user): complete user system](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/39)\n"
                    "• **ปิดจ็อบ User System ครบทุกขอบเขต:** Conversation History API + Sidebar UI, Skills API, Feedback 👍/👎 + Dislike Reason Dialog, Profile Control & Logout\n"
                    "• พร้อมเอกสาร Handoff: `docs/handoffs/P2-user-system.md`"
                ),
                "inline": False,
            },
            {
                "name": "✅ PR #40 · rag (P4)",
                "value": (
                    "[fix(rag): stricter keyword scope filter when the reranker is off](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/40)\n"
                    "• ปรับปรุง Fallback search เมื่อไม่มี Reranker ด้วย Word coverage (IDF) ≥ 0.2 + 3-gram\n"
                    "• ปฏิเสธคำถามนอกขอบเขตในโหมดประหยัด RAM ได้แม่นยำยิ่งขึ้น"
                ),
                "inline": False,
            },
        ],
        "footer": {"text": "COPIE · CI/CD & Review Bot"},
    }

    api.send_message(chans["pull-requests"], {"embeds": [summary_embed]})
    print("Posted summary to #pull-requests")

    # 2. Notify P4 (สิรวิชญ์ ศิริสลุง @Peemaxnaja)
    p4_msg = (
        f"🎉 <@236323936223100928> (<@&{roles['p4-rag']}>)\n"
        "PR #38 (`rag/faq`) และ PR #40 (`rag/fallback-search`) ของคุณผ่านการรีวิวและ **Merge เข้า `develop`** เรียบร้อยแล้วครับ!\n\n"
        "✨ **ผลการรีวิว:**\n"
        "• FAQ ราย section ช่วยให้แหล่งอ้างอิงของ Agent ชี้ตรงจุดมากยิ่งขึ้น\n"
        "• Fallback search มีการจูน threshold IDF coverage ที่รอบคอบและปลอดภัย\n\n"
        "💡 **คำแนะนำ:**\n"
        "```bash\n"
        "git switch develop\n"
        "git pull --ff-only origin develop\n"
        "```"
    )
    api.send_message(
        chans["p4-rag"],
        {"content": p4_msg, "allowed_mentions": {"users": ["236323936223100928"], "roles": [roles["p4-rag"]]}},
    )
    print("Notified P4")

    # 3. Notify P2 (เตชิษฏ์ จาดยางโทน @TJANDFRIEND)
    p2_msg = (
        f"🎉 <@252787270078169088> (<@&{roles['p2-user']}>)\n"
        "PR #39 ของคุณ (`user/complete-user-system`) ผ่านการรีวิวและ **Merge เข้า `develop`** เรียบร้อยแล้วครับ!\n\n"
        "🏆 **ขอแสดงความยินดีด้วยครับ:** ระบบ User Module (P2) เสร็จสมบูรณ์ครบทุกส่วนตามแผนงาน:\n"
        "• Auth & Dev Login / Onboarding Flow\n"
        "• Conversation History (API + Sidebar UI + Restore message)\n"
        "• Skills API (`/api/skills/me`)\n"
        "• Feedback System (👍/👎 + Reason Dialog)\n"
        "• Profile Control & Greeting\n\n"
        "💡 **คำแนะนำ:**\n"
        "```bash\n"
        "git switch develop\n"
        "git pull --ff-only origin develop\n"
        "```"
    )
    api.send_message(
        chans["p2-user"],
        {"content": p2_msg, "allowed_mentions": {"users": ["252787270078169088"], "roles": [roles["p2-user"]]}},
    )
    print("Notified P2")


if __name__ == "__main__":
    main()
