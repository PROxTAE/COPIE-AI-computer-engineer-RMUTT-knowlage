#!/usr/bin/env python
"""Post the weekend COPIE deadline in #announcements."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from discord_api import Discord, load_dotenv

HERE = Path(__file__).resolve().parent
MARKER = "copie-weekend-deadline-2026-09-27"
ROLE_KEYS = (
    "p1-core-mascot", "p2-user", "p3-agent", "p4-rag",
    "p5-tools", "p6-renderer", "p7-suggest-ml", "p8-export-qa",
)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    load_dotenv()
    api = Discord()
    ids = json.loads((HERE / "out" / "discord-ids.json").read_text(encoding="utf-8"))
    channels, roles = ids["channel_ids"], ids["role_ids"]
    channel = channels["announcements"]
    pings = " ".join(f"<@&{roles[key]}>" for key in ROLE_KEYS)
    diagram = (
        f"https://discord.com/channels/{ids['guild_id']}/"
        f"{channels['project-summary']}/1552966747986862081"
    )
    content = (
        f"📣 **เดดไลน์งาน COPIE: ภายในสุดสัปดาห์นี้** {pings}\n\n"
        "เวลาที่เหลือน้อยแล้ว ขอให้ **ทุกคนเริ่มงานทันทีและทำส่วนที่รับผิดชอบให้เสร็จภายในเสาร์–อาทิตย์นี้** "
        "(26–27 ก.ย. 2026). ตอนสั่ง AI ให้ใช้ชุดไฟล์และพรอมป์ที่ปักหมุดในห้องของตัวเอง "
        "สั่งให้ทำงานต่อเนื่องตามแผนจนจบ โดยแบ่งเป็น PR เล็ก ๆ และตรวจผลหลังแต่ละส่วน อย่าหยุดแค่ PR แรก\n\n"
        "**ภายในวันอาทิตย์ที่ 27 ก.ย. เวลา 23:59 น. (เวลาไทย)** ทุกคนต้องมีโค้ดที่ตนเองตรวจแล้ว **commit + push** "
        "และเปิด PR เข้า `develop` พร้อมหลักฐานการทดสอบ หากส่วนใดยังรอเพื่อนให้เปิด **Draft PR** "
        f"และระบุว่ารอไฟล์/ฟังก์ชันอะไร แจ้งความคืบหน้าและลิงก์ PR ใน <#{channels['status']}>; "
        f"ถ้าติดขัดให้บอกใน <#{channels['blockers']}> ทันที\n\n"
        "**อย่ารอทำวันสุดท้าย** เพราะทีมต้องมีเวลารวมระบบและทดสอบ flow จริง งานที่เพื่อนทำไว้จะต่อกันไม่ทัน "
        "และผลงานรวมจะแสดงได้ไม่เต็มที่ หากใครไม่เริ่มงานหรือไม่มีความคืบหน้าภายในกำหนด "
        "จะถูกตัดชื่อออกจากกลุ่ม\n\n"
        f"ดูโฟลว์ส่งต่องาน: {diagram}\n"
        f"-# {MARKER}"
    )
    if len(content) > 2000:
        raise ValueError(f"Discord content too long: {len(content)}")
    payload = {"content": content, "allowed_mentions": {"roles": [roles[key] for key in ROLE_KEYS]}}
    old = next((m for m in api.get(f"/channels/{channel}/messages?limit=100")
                if MARKER in (m.get("content") or "")), None)
    if old:
        message = api.edit_message(channel, old["id"], payload)
    else:
        message = api.send_message(channel, payload)
    if not message.get("pinned"):
        api.pin_message(channel, message["id"])
    print(f"https://discord.com/channels/{ids['guild_id']}/{channel}/{message['id']}")


if __name__ == "__main__":
    main()
