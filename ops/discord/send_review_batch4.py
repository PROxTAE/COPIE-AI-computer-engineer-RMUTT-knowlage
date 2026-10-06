#!/usr/bin/env python
"""Send Batch 4 PR review and merge notifications to Discord."""
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
        "title": "⚡ สรุปผลการ Review & Merge PRs (Batch 4)",
        "description": "รีวิว PR ล่าสุดทั้งหมดเรียบร้อยแล้ว ทั้ง 3 PR ผ่านเกณฑ์คุณภาพ Code, Tests, Contract, CI 100% เขียว และถูก **Merge เข้า `develop`** เรียบร้อยแล้วครับ! 🎉",
        "color": 0x10B981,
        "fields": [
            {
                "name": "✅ PR #24 · rag (P4)",
                "value": (
                    "[feat(rag): rerank Thai BM25 + vector candidates and reject out-of-scope questions](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/24)\n"
                    "• Rerank ด้วย Cross-Encoder (BAAI/bge-reranker-v2-m3) ผสาน Custom PyThaiNLP BM25\n"
                    "• ปฏิเสธคำถามนอกขอบเขตอัตโนมัติ (`MIN_RELEVANCE = 0.005`) + 194 passing tests"
                ),
                "inline": False,
            },
            {
                "name": "✅ PR #27 · suggest (P7)",
                "value": (
                    "[feat(suggest): add suggested prompts chips](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/27)\n"
                    "• เพิ่มคอมโพเนนต์ `<SuggestedPrompts />` พร้อมชุดคำถามแนะนำตามกลุ่มผู้ใช้ (ม.6, ปี 1-4, ใกล้จบ)\n"
                    "• *แก้ base branch จาก `main` เป็น `develop` เรียบร้อย และ CI ผ่านเขียวทั้งหมด*"
                ),
                "inline": False,
            },
            {
                "name": "✅ PR #30 · user (P2)",
                "value": (
                    "[feat(user): add dev auth and user models](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/30)\n"
                    "• เพิ่ม SQLModel 5 ตารางหลัก (User, Conversation, Message, SkillProfile, Feedback)\n"
                    "• ระบบ Dev Auth (`POST /api/auth/dev`), JWT Handling และ `GET /api/users/me`"
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
        "PR #24 ของคุณ (`rag/hybrid-search`) ผ่านการรีวิวและ **Merge เข้า `develop`** เรียบร้อยแล้วครับ!\n"
        "✨ **ผลการรีวิว:** ยอดเยี่ยมมาก! ระบบ Cross-Encoder Reranking + BM25 มีเกณฑ์ตัด out-of-scope ชัดเจน และ fallback เมื่อโมเดลไม่พร้อมทำงานได้สมบูรณ์\n"
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

    # 3. Notify P7 (ปกครอง ทับโทน @24madcap)
    p7_msg = (
        f"🎉 <@256420422298370055> (<@&{roles['p7-suggest-ml']}>)\n"
        "PR #27 ของคุณ (`suggest/prompt-chips`) ผ่านการรีวิวและ **Merge เข้า `develop`** เรียบร้อยแล้วครับ!\n\n"
        "📌 **ข้อชี้แจง & คำแนะนำ:**\n"
        "1. ⚠️ **สิ่งที่แก้ไขให้:** เดิม PR ตั้ง base branch เข้า `main` ทำให้ CI `branch-name` fail (`main รับ PR จาก develop หรือ release/* เท่านั้น`) — ตอนนี้ช่วยแก้ base เป็น `develop` และ CI เขียวครบ 100% แล้ว\n"
        "2. 💡 **การตั้งค่า Git ประจำตัว:** ใน commit เดิมชื่อ-อีเมลยังเป็นค่าเริ่มต้น แนะนำให้รันคำสั่งนี้ในเครื่อง:\n"
        "   ```bash\n"
        '   git config user.name "ปกครอง ทับโทน"\n'
        '   git config user.email "อีเมลของคุณที่ผูกกับ GitHub"\n'
        "   ```\n"
        "3. 🌿 **อัปเดตเครื่องก่อนเริ่มงานถัดไป:**\n"
        "   ```bash\n"
        "   git switch develop\n"
        "   git pull --ff-only origin develop\n"
        "   git switch -c suggest/context-aware\n"
        "   ```"
    )
    api.send_message(
        chans["p7-suggest-ml"],
        {"content": p7_msg, "allowed_mentions": {"users": ["256420422298370055"], "roles": [roles["p7-suggest-ml"]]}},
    )
    print("Notified P7")

    # 4. Notify P2 (เตชิษฏ์ จาดยางโทน @TJANDFRIEND)
    p2_msg = (
        f"🎉 <@252787270078169088> (<@&{roles['p2-user']}>)\n"
        "PR #30 ของคุณ (`user/db-and-dev-auth`) ผ่านการรีวิวและ **Merge เข้า `develop`** เรียบร้อยแล้วครับ!\n"
        "✨ **ผลการรีวิว:** โครงสร้าง SQLModel, Dev Auth, JWT และการผูกเข้ากับ FastAPI lifecycle สมบูรณ์พร้อมเทสผ่านทั้งหมด\n"
        "💡 **คำแนะนำ:**\n"
        "```bash\n"
        "git switch develop\n"
        "git pull --ff-only origin develop\n"
        "# อัปเดต dependencies ใน backend venv (เพิ่ม sqlmodel, PyJWT)\n"
        "cd backend && pip install -r requirements.txt\n"
        "```\n"
        "พร้อมลุยงานถัดไปต่อได้เลยครับ (`user/google-login-api` หรือ `user/onboarding-flow`)"
    )
    api.send_message(
        chans["p2-user"],
        {"content": p2_msg, "allowed_mentions": {"users": ["252787270078169088"], "roles": [roles["p2-user"]]}},
    )
    print("Notified P2")


if __name__ == "__main__":
    main()
