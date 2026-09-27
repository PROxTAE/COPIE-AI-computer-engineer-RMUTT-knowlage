#!/usr/bin/env python
"""Send Batch 8 PR review and merge notifications to Discord."""
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
        "title": "⚡ สรุปผลการ Review & Merge PRs (Batch 8)",
        "description": "PR ล่าสุดได้รับการรีวิว ตรวจสอบเอกสาร Handoff, Contract, Tests และ CI 100% เขียว จึงได้ทำการ **Merge เข้า `develop`** เรียบร้อยครับ! 🎉",
        "color": 0x10B981,
        "fields": [
            {
                "name": "✅ PR #41 · rag (P4)",
                "value": (
                    "[docs(rag): add P4 department RAG completion handoff](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/41)\n"
                    "• **ปิดจ็อบ Department RAG (P4) สมบูรณ์:** สรุปโครงสร้าง Hybrid Retrieval, คลังความรู้ 16 เอกสาร (88 chunks), ผลวัดความแม่นยำ Held-out 4–6 (Hit@1 91%, Hit@4 95%, Reject 91.1%), ผล Demo 2 กับ Gemini จริง\n"
                    "• พร้อมเอกสาร Handoff และข้อแนะนำส่งต่อทีม: `docs/handoffs/P4-department-rag.md`"
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
        "PR #41 ของคุณ (`docs/handoff-p4`) ผ่านการรีวิวและ **Merge เข้า `develop`** เรียบร้อยแล้วครับ!\n\n"
        "🏆 **ขอแสดงความยินดีด้วยครับ:** โมดูล Department RAG (P4) เสร็จสมบูรณ์ครบถ้วน 100%:\n"
        "• Hybrid Retrieval (multilingual-e5 + Custom PyThaiNLP BM25 + BGE Reranker v2 m3)\n"
        "• คลังความรู้ทางการของภาควิชา 16 ฉบับ (88 chunks) พร้อม Source Link attribution ราย section\n"
        "• ผลวัดความแม่นยำบน Held-out sets และผล Demo 2 ยอดเยี่ยมมาก\n"
        "• เอกสาร Handoff ละเอียด ครอบคลุมจุดเชื่อมต่อของทุกโมดูล\n\n"
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


if __name__ == "__main__":
    main()
