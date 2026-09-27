#!/usr/bin/env python
"""Send Batch 5 PR review and merge notifications to Discord."""
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
        "title": "⚡ สรุปผลการ Review & Merge PRs (Batch 5)",
        "description": "PR ล่าสุดได้รับการรีวิว ตรวจสอบความถูกต้องของ Contract, Boundary, Tests และ CI ผ่านครบถ้วน 100% เขียว และถูก **Merge เข้า `develop`** เรียบร้อยแล้วครับ! 🎉",
        "color": 0x10B981,
        "fields": [
            {
                "name": "✅ PR #33 · user (P2)",
                "value": (
                    "[feat(user): add Google login and profile API](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/33)\n"
                    "• Google ID Token verification (`POST /api/auth/google`) ออก Project JWT ตาม Contract\n"
                    "• Profile Onboarding API (`PUT /api/users/me/profile`) บันทึกข้อมูลและตั้ง `onboarded=true`\n"
                    "• จัดการ error cases ได้ถูกต้องชัดเจน (503 / 409 / 401) + 36 passing user tests"
                ),
                "inline": False,
            },
        ],
        "footer": {"text": "COPIE · CI/CD & Review Bot"},
    }

    api.send_message(chans["pull-requests"], {"embeds": [summary_embed]})
    print("Posted summary to #pull-requests")

    # 2. Notify P2 (เตชิษฏ์ จาดยางโทน @TJANDFRIEND)
    p2_msg = (
        f"🎉 <@252787270078169088> (<@&{roles['p2-user']}>)\n"
        "PR #33 ของคุณ (`user/google-login-api`) ผ่านการรีวิวและ **Merge เข้า `develop`** เรียบร้อยแล้วครับ!\n\n"
        "✨ **ผลการรีวิว:**\n"
        "• การตรวจสอบ Google ID Token และการออก Project JWT ทำได้ถูกต้องตาม Contract\n"
        "• Endpoint `PUT /api/users/me/profile` พร้อมสำหรับการ Onboarding ผู้ใช้\n"
        "• Test coverage ครบถ้วน (mock Google verifier ปลอดภัย ไม่เรียก Google จริงใน test)\n\n"
        "💡 **คำแนะนำขั้นตอนถัดไป:**\n"
        "```bash\n"
        "git switch develop\n"
        "git pull --ff-only origin develop\n"
        "# ติดตั้ง backend dependencies ใหม่ (google-auth, requests)\n"
        "cd backend && pip install -r requirements.txt\n"
        "```\n"
        "สามารถแตก branch เริ่มทำหน้า Login UI / Onboarding UI (`user/onboarding-flow`) หรือทำ Frontend AuthGuard ได้เลยครับ!"
    )
    api.send_message(
        chans["p2-user"],
        {"content": p2_msg, "allowed_mentions": {"users": ["252787270078169088"], "roles": [roles["p2-user"]]}},
    )
    print("Notified P2")


if __name__ == "__main__":
    main()
