#!/usr/bin/env python
"""Send Batch 6 PR review and merge notifications to Discord."""
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
        "title": "⚡ สรุปผลการ Review & Merge PRs (Batch 6)",
        "description": "รีวิว PR ล่าสุดทั้ง 2 รายการเรียบร้อยแล้ว ทั้งหมดผ่านการตรวจสอบ Code, Data Validity, Contract และ CI 100% เขียว จึงได้ทำการ **Merge เข้า `develop`** เรียบร้อยครับ! 🎉",
        "color": 0x10B981,
        "fields": [
            {
                "name": "✅ PR #36 · rag (P4)",
                "value": (
                    "[data(rag): add admission schedule, scholarships, co-op 2563 and student projects](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/36)\n"
                    "• เพิ่มเอกสารความรู้ทางการ 4 ฉบับ: กำหนดการรับสมัคร 2570, ทุนการศึกษา, สหกิจศึกษา 2563, ตัวอย่างโครงงาน\n"
                    "• ขยายคลังความรู้เป็น 15 เอกสาร (70 chunks) พร้อมชุดคำถาม held-out 5"
                ),
                "inline": False,
            },
            {
                "name": "✅ PR #37 · user (P2)",
                "value": (
                    "[feat(user): add login onboarding and auth guard](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/37)\n"
                    "• เพิ่มหน้า `/login` รองรับ Google Sign-In & Dev Login\n"
                    "• เพิ่มหน้า `/onboarding` เก็บ display name, ช่วงอายุ, สถานะผู้ใช้ และชั้นปี\n"
                    "• ระบบ `AuthGuard` ป้องกัน `/chat` และ redirect ตามสถานะการยืนยันตัวตนอย่างถูกต้อง"
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
        "PR #36 ของคุณ (`rag/knowledge-v2`) ผ่านการรีวิวและ **Merge เข้า `develop`** เรียบร้อยแล้วครับ!\n\n"
        "✨ **ผลการรีวิว:**\n"
        "• เอกสารความรู้ทั้ง 4 ชุดมีความถูกต้อง ตรงตามแหล่งข้อมูลจริงของภาควิชาและมหาวิทยาลัย\n"
        "• การเชื่อมโยงลิงก์และชุดทดสอบ held-out 5 ชัดเจนมาก\n\n"
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
        "PR #37 ของคุณ (`user/onboarding-flow`) ผ่านการรีวิวและ **Merge เข้า `develop`** เรียบร้อยแล้วครับ!\n\n"
        "✨ **ผลการรีวิว:**\n"
        "• หน้า `/login` และ `/onboarding` ดีไซน์เข้ากับธีม Cyberism และใช้งานง่าย\n"
        "• การเชื่อมโยง Session ผ่าน Zustand (`useUserStore`) และการจัดการ AuthGuard บน Next.js routes ทำได้ราบรื่นมาก\n\n"
        "💡 **คำแนะนำ:**\n"
        "```bash\n"
        "git switch develop\n"
        "git pull --ff-only origin develop\n"
        "```\n"
        "พร้อมสำหรับ Phase ถัดไปเรื่อง Conversation History / Feedback (`user/history-api` หรือ `user/feedback`) ได้เลยครับ!"
    )
    api.send_message(
        chans["p2-user"],
        {"content": p2_msg, "allowed_mentions": {"users": ["252787270078169088"], "roles": [roles["p2-user"]]}},
    )
    print("Notified P2")


if __name__ == "__main__":
    main()
