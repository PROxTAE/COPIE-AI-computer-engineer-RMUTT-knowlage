#!/usr/bin/env python
"""Send Batch 3 PR review and merge notifications to Discord."""
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
        "title": "⚡ สรุปผลการ Review & Merge PRs (Batch 3)",
        "description": "ทุก PR ผ่านการตรวจ Code Quality, Contract, CI และ Rule Check ทั้งหมด เรียบร้อยแล้วและถูก **Merge เข้า `develop`** เรียบร้อยแล้วครับ!",
        "color": 0x10B981,
        "fields": [
            {
                "name": "✅ PR #20 · rag (P4)",
                "value": (
                    "[feat(rag): search with e5 vectors fused with keywords via RRF](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/20)\n"
                    "• Vector Search ด้วย multilingual-e5 ผสาน Keyword ด้วย RRF (Reciprocal Rank Fusion)\n"
                    "• Hash sync อัตโนมัติ + 72 passing tests"
                ),
                "inline": False,
            },
            {
                "name": "✅ PR #21 · agent (P3)",
                "value": (
                    "[fix(agent): add rapidfuzz for fuzzy course search](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/21)\n"
                    "• เพิ่ม `rapidfuzz==3.14.6` ใน `requirements.txt` สำหรับ fuzzy match รายวิชา"
                ),
                "inline": False,
            },
            {
                "name": "✅ PR #22 · renderer (P6)",
                "value": (
                    "[feat(renderer): make the renderer ready to drop into the chat page](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/22)\n"
                    "• เพิ่ม prop `animate` (พิมพ์เฉพาะข้อความล่าสุด) + จัดการกรณีตารางรายวิชาว่างได้สวยงาม\n"
                    "• เอกสาร handoff การนำไปแปะในหน้าแชตจริง"
                ),
                "inline": False,
            },
            {
                "name": "✅ PR #23 · tools (P5)",
                "value": (
                    "[fix(tools): make course name search reliable](https://github.com/PROxTAE/COPIE-AI-computer-engineer-RMUTT-knowlage/pull/23)\n"
                    "• ปรับใช้ RapidFuzz WRatio + default_process ค้นชื่อวิชาตัวพิมพ์เล็ก/ใหญ่และไทย/อังกฤษได้อย่างแม่นยำ"
                ),
                "inline": False,
            },
        ],
        "footer": {"text": "COPIE · CI/CD & Review Bot"},
    }

    api.send_message(chans["pull-requests"], {"embeds": [summary_embed]})
    print("Posted summary to #pull-requests")

    # 2. Notify P4
    p4_msg = (
        f"🎉 <@236323936223100928> (<@&{roles['p4-rag']}>)\n"
        "PR #20 ของคุณ (`rag/vector-retriever`) ผ่านการรีวิวและ **Merge เข้า `develop`** เรียบร้อยแล้วครับ!\n"
        "✨ ระบบ RAG ตอนนี้ใช้ Vector Search ร่วมกับ Keyword ด้วย RRF ได้อย่างรวดเร็วและแม่นยำ\n"
        "💡 **คำแนะนำ:** รัน `git switch develop && git pull --ff-only origin develop`"
    )
    api.send_message(
        chans["p4-rag"],
        {"content": p4_msg, "allowed_mentions": {"users": ["236323936223100928"], "roles": [roles["p4-rag"]]}},
    )
    print("Notified P4")

    # 3. Notify P3
    p3_msg = (
        f"🎉 <@400608356492115968> (<@&{roles['p3-agent']}>)\n"
        "PR #21 ของคุณ (`agent/add-rapidfuzz`) ผ่านการรีวิวและ **Merge เข้า `develop`** เรียบร้อยแล้วครับ!\n"
        "💡 **คำแนะนำ:** รัน `git switch develop && git pull --ff-only origin develop` และ `pip install -r requirements.txt`"
    )
    api.send_message(
        chans["p3-agent"],
        {"content": p3_msg, "allowed_mentions": {"users": ["400608356492115968"], "roles": [roles["p3-agent"]]}},
    )
    print("Notified P3")

    # 4. Notify P6
    p6_msg = (
        f"🎉 <@286434245210144768> (<@&{roles['p6-renderer']}>)\n"
        "PR #22 ของคุณ (`renderer/integration-ready`) ผ่านการรีวิวและ **Merge เข้า `develop`** เรียบร้อยแล้วครับ!\n"
        "✨ Component พร้อมให้ฝั่ง Workspace/Chat นำไปวางต่อได้ทันที\n"
        "💡 **คำแนะนำ:** รัน `git switch develop && git pull --ff-only origin develop`"
    )
    api.send_message(
        chans["p6-renderer"],
        {"content": p6_msg, "allowed_mentions": {"users": ["286434245210144768"], "roles": [roles["p6-renderer"]]}},
    )
    print("Notified P6")

    # 5. Notify P5
    p5_msg = (
        f"🎉 <@381391956795850754> (<@&{roles['p5-tools']}>)\n"
        "PR #23 ของคุณ (`tools/course-search-fix`) ผ่านการรีวิวและ **Merge เข้า `develop`** เรียบร้อยแล้วครับ!\n"
        "✨ ค้นชื่อวิชา (เช่น `data structure`, `โครงสร้างข้อมูล`) ผ่าน RapidFuzz ได้อย่างแม่นยำ\n"
        "💡 **คำแนะนำ:** รัน `git switch develop && git pull --ff-only origin develop`"
    )
    api.send_message(
        chans["p5-tools"],
        {"content": p5_msg, "allowed_mentions": {"users": ["381391956795850754"], "roles": [roles["p5-tools"]]}},
    )
    print("Notified P5")


if __name__ == "__main__":
    main()
