#!/usr/bin/env python
"""Draw the COPIE handoff flow in the web theme and publish its revision."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from discord_api import Discord, load_dotenv

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "docs" / "diagrams" / "copie-handoff-flow.png"
MARKER = "copie-handoff-flow-v2"
OLD_MARKER = "copie-team-start-2026-09-25"
INK, BLUE, CYAN = "#111A30", "#155FF2", "#45CFE9"
MUTED, LINE, PAPER = "#5F7088", "#D7E5F8", "#F8FBFF"


def ft(size: int, bold: bool = False, latin: bool = False) -> ImageFont.FreeTypeFont:
    path = Path("C:/Windows/Fonts")
    name = "IBMPlexSans-Bold.ttf" if latin else ("leelawdb.ttf" if bold else "LeelawUI.ttf")
    return ImageFont.truetype(str(path / name), size)


def lines(d: ImageDraw.ImageDraw, xy: tuple[int, int], rows: list[str], size: int,
          color: str = INK, gap: int = 11, bold: bool = False) -> None:
    x, y = xy
    for row in rows:
        d.text((x, y), row, font=ft(size, bold), fill=color)
        y += size + gap


def arrow(d: ImageDraw.ImageDraw, points: list[tuple[int, int]], color: str = BLUE,
          width: int = 7, dash: bool = False, head: int = 23) -> None:
    if dash:
        for a, b in zip(points, points[1:]):
            length = math.dist(a, b)
            steps = max(1, int(length / 32))
            for i in range(0, steps, 2):
                p = (a[0] + (b[0] - a[0]) * i / steps, a[1] + (b[1] - a[1]) * i / steps)
                q = (a[0] + (b[0] - a[0]) * min(i + 1, steps) / steps,
                     a[1] + (b[1] - a[1]) * min(i + 1, steps) / steps)
                d.line((p, q), fill=color, width=width)
    else:
        d.line(points, fill=color, width=width, joint="curve")
    a, b = points[-2], points[-1]
    theta = math.atan2(b[1] - a[1], b[0] - a[0])
    left = (b[0] - head * math.cos(theta) + head * 0.53 * math.sin(theta),
            b[1] - head * math.sin(theta) - head * 0.53 * math.cos(theta))
    right = (b[0] - head * math.cos(theta) - head * 0.53 * math.sin(theta),
             b[1] - head * math.sin(theta) + head * 0.53 * math.cos(theta))
    d.polygon([b, left, right], fill=color)


def box(d: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], key: str, title: str,
        body: list[str], accent: str = BLUE, size: int = 31) -> None:
    x1, y1, x2, y2 = rect
    d.rounded_rectangle((x1 + 7, y1 + 10, x2 + 7, y2 + 10), 27, fill="#EAF2FC")
    d.rounded_rectangle(rect, 27, fill="white", outline=LINE, width=3)
    d.rectangle((x1, y1 + 24, x1 + 8, y2 - 24), fill=accent)
    d.text((x1 + 34, y1 + 24), key, font=ft(33, True, True), fill=accent)
    d.text((x1 + 117, y1 + 18), title, font=ft(39, True), fill=INK)
    d.line((x1 + 34, y1 + 85, x2 - 32, y1 + 85), fill=LINE, width=3)
    lines(d, (x1 + 34, y1 + 97), body, size, MUTED, 6)


def label(d: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, color: str = BLUE,
          bg: str = "#FFFFFF", size: int = 27) -> None:
    x, y = xy
    f = ft(size, True)
    width = int(d.textlength(text, font=f))
    d.rounded_rectangle((x - 10, y - 7, x + width + 10, y + size + 15), 10, fill=bg)
    d.text((x, y), text, font=f, fill=color)


def render() -> Path:
    im = Image.new("RGB", (2400, 1800), "white")
    d = ImageDraw.Draw(im)
    # The light grid, corner frame and cyan line match the login mockup.
    for x in range(62, 2400, 91):
        d.line((x, 0, x, 1800), fill="#EAF4FF", width=2)
    for y in range(55, 1800, 91):
        d.line((0, y, 2400, y), fill="#EAF4FF", width=2)
    d.rectangle((55, 55, 2345, 1745), outline="#A7D7FF", width=3)
    d.rectangle((55, 213, 2345, 217), fill=LINE)
    d.rectangle((55, 296, 2345, 300), fill=LINE)
    d.rectangle((55, 340, 64, 1530), fill=CYAN)
    d.rectangle((2336, 340, 2345, 1530), fill=BLUE)
    d.text((107, 79), "COPIE", font=ft(88, True, True), fill="#050910")
    d.line((430, 94, 430, 175), fill=BLUE, width=3)
    d.text((458, 96), "TEAM  /  HANDOFF FLOW", font=ft(36, True, True), fill=BLUE)
    d.text((107, 228), "ใครส่งอะไรให้ใคร  •  ผู้รับนำไปทำอะไร", font=ft(47, True), fill=INK)
    d.text((2350, 232), "WORKFLOW  01 / 08", font=ft(25, True, True), fill=MUTED, anchor="ra")
    mascot = Image.open(ROOT / "assets/web-ui/mascot/states/copie-front-laptop.png").convert("RGBA")
    mascot.thumbnail((185, 218))
    halo = (2130, 45, 2370, 275)
    d.ellipse(halo, outline="#B6EFFF", width=3)
    im.paste(mascot, (2180, 40), mascot)

    # Connector paths are drawn first, so cards cover their endpoints cleanly.
    source = [(110, 405, 655, 613), (110, 674, 655, 882),
              (110, 943, 655, 1151), (110, 1212, 655, 1420)]
    targets = [760, 845, 930, 1110]
    for i, rect in enumerate(source):
        routing_x = 850 if i == 3 else 800
        arrow(d, [(rect[2], (rect[1] + rect[3]) // 2), (routing_x, (rect[1] + rect[3]) // 2),
                  (routing_x, targets[i]), (940, targets[i])],
              color="#679BFF" if i == 3 else BLUE, dash=i == 3, width=6)
    # Request route and response handoff.
    arrow(d, [(2065, 507), (2065, 653)], CYAN, 7)
    arrow(d, [(1805, 708), (1570, 708), (1570, 690), (1465, 690)], CYAN, 7)
    arrow(d, [(1465, 980), (1615, 980), (1615, 838), (1805, 838)], BLUE, 8)
    arrow(d, [(2065, 891), (2065, 1070)], BLUE, 8)
    arrow(d, [(2065, 1308), (2065, 1430)], BLUE, 8)
    # QA and evaluation feedback.
    arrow(d, [(1160, 1430), (1160, 1180)], "#5F7088", 5, True)
    arrow(d, [(940, 1510), (380, 1510), (380, 1420)], "#5F7088", 5, True)

    box(d, source[0], "P2", "ผู้ใช้ / ประวัติ", ["ส่ง context + history ให้ P3", "ส่ง login / sidebar ให้ P1", "P3 ใช้ปรับคำตอบตามชั้นปี"], size=27)
    box(d, source[1], "P4", "RAG ข้อมูลภาค", ["ส่งข้อความค้นพบ + sources", "Agent ใช้อ้างอิงข้อมูลจริง"], size=29)
    box(d, source[2], "P5", "หลักสูตร / Skill", ["ส่งรายวิชา + คะแนนให้ P3", "ส่งข้อมูลตัวอย่างให้ P6", "P3 ใช้สร้างตาราง / เรดาร์"], size=27)
    box(d, source[3], "P7", "Intent ML (เสริม)", ["ส่งชนิดคำถามที่ทำนาย", "Agent ใช้ช่วยเลือก Tool"], accent="#5F7088", size=29)

    box(d, (940, 634, 1465, 1180), "P3", "Agent + API",
        ["รับคำถามจาก P1", "รวมข้อมูลจาก P2 / P4 / P5", "เลือก Tool และตรวจความพอ", "ส่ง AgentResponse ตาม contract"], size=33)
    box(d, (1805, 653, 2325, 891), "P1", "เว็บ + มาสคอต",
        ["รับคำถาม แล้วเรียก /api/chat", "รับ AgentResponse เพื่อแสดงผล"], size=30)
    box(d, (1805, 1070, 2325, 1308), "P6", "ตัวเรนเดอร์",
        ["รับ response จาก P1", "รับข้อมูลตัวอย่างจาก P5", "ทำ text / table / form / radar"], size=28)
    box(d, (940, 1430, 1465, 1624), "P8", "QA + Eval",
        ["ส่งชุดคำถามให้ P7", "ส่งผลทดสอบให้ P3 และทีม"], accent="#5F7088", size=28)

    d.rounded_rectangle((1805, 357, 2325, 507), 24, fill="#EAF4FF", outline="#B6DAFF", width=3)
    d.text((1840, 379), "ผู้ใช้ถาม COPIE", font=ft(37, True), fill=INK)
    d.text((1840, 433), "คำถาม + token ส่งให้ P1", font=ft(29), fill=MUTED)
    d.rounded_rectangle((1805, 1430, 2325, 1580), 24, fill="#EAF4FF", outline="#B6DAFF", width=3)
    d.text((1840, 1454), "หน้าจอที่ผู้ใช้เห็น", font=ft(37, True), fill=INK)
    d.text((1840, 1507), "ข้อความ / ตาราง / ฟอร์ม / กราฟ", font=ft(28), fill=MUTED)

    label(d, (1482, 920), "ตอบกลับ: AgentResponse", BLUE, "#F8FBFF", 27)
    label(d, (1610, 644), "POST /api/chat", BLUE, "#F8FBFF", 25)
    label(d, (1750, 971), "ให้ P6 สร้าง UI", BLUE, "#F8FBFF", 25)
    label(d, (1210, 1294), "ผล QA กลับไปปรับ Agent", MUTED, "#F8FBFF", 25)
    label(d, (480, 1458), "ชุดคำถามมี label", MUTED, "#F8FBFF", 25)

    d.line((110, 1673, 2288, 1673), fill=LINE, width=3)
    d.text((110, 1690), "เริ่มพร้อมกันได้ด้วย mock / stub ตาม contract", font=ft(30, True), fill=BLUE)
    d.text((990, 1690), "เส้นทึบ = ส่งของจริงตอนรวมระบบ    เส้นประ = งานเสริม / วงจร QA", font=ft(27), fill=MUTED)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    im.save(OUT, optimize=True)
    return OUT


def marked(api: Discord, channel: str, marker: str) -> dict | None:
    for message in api.get(f"/channels/{channel}/messages?limit=100"):
        if marker in (message.get("content") or ""):
            return message
    return None


def post(png: Path) -> str:
    load_dotenv()
    api = Discord()
    ids = json.loads((HERE / "out" / "discord-ids.json").read_text(encoding="utf-8"))
    channels, roles = ids["channel_ids"], ids["role_ids"]
    summary, announcements = channels["project-summary"], channels["announcements"]
    body = (
        "**อ่านลูกศรจากต้นทางไปปลายทาง:** P2 ส่งข้อมูลผู้ใช้, P4 ส่งข้อความพร้อมแหล่งอ้างอิง, "
        "P5 ส่งรายวิชา/คะแนนที่คำนวณแล้ว และ P7 ส่ง intent ที่ทำนาย (ส่วนเสริม) → "
        "P3 รวมข้อมูล เลือก Tool และส่ง `AgentResponse` → P1 ส่งให้ P6 วาด UI → ผู้ใช้เห็นคำตอบบนหน้า COPIE. "
        "P8 ส่งชุดคำถามให้ P7 และผลทดสอบกลับให้ P3/ทีม.\n\n"
        "**เริ่มพร้อมกันได้:** P1 ทำ chat shell/mascot, P2 ทำ Dev Login + user stub, "
        "P3 ทำ mock `/api/chat` + router, P4 หาเอกสารจริง + search stub, "
        "P5 หาเล่มหลักสูตร + tool stub, P6 ทำ fixtures/renderer, P7 ทำ prompts static, P8 ทำ eval set/checklist.\n"
        "**จุดที่ต้องรอของจริง:** P3 ต่อ user/RAG/tools จาก P2/P4/P5; P1 ต่อ API/Renderer จาก P3/P6; "
        "P7 ฝึก ML หลังได้ชุดคำถามจาก P8; P8 วัดผล end to end หลัง P2/P3/P4/P5 ส่งงาน. "
        "ระหว่างนั้นใช้ mock/stub ที่ตรง contract ได้; ก่อน demo ต้องเปลี่ยนเป็นข้อมูลจริง.\n\n"
        "**สถานะใน repo:** มี contract, โครงแอป, ธีมและมาสคอตแล้ว; ยังไม่พบ knowledge จริง, "
        "`curriculum.json`, `skill_v1.json`, `questions.jsonl`, chat API จริง และ Docker Compose. "
        f"ติดเอกสารหรือ handoff ใดให้แจ้ง <#{channels['blockers']}> พร้อมชื่อไฟล์หรือฟังก์ชันที่รอ."
    )
    payload = {
        "content": f"📘 COPIE · ไดอะแกรมโฟลว์การส่งงาน | {MARKER}",
        "embeds": [{"title": "ใครส่งข้อมูลให้ใคร และนำไปทำอะไร", "description": body,
                    "color": 0x155FF2, "image": {"url": f"attachment://{png.name}"}}],
        "allowed_mentions": {"parse": []},
    }
    previous = marked(api, summary, MARKER)
    if previous:
        detail = api.edit_message_files(summary, previous["id"], payload, files=[(png.name, png)])
    else:
        detail = api.send_message(summary, payload, files=[(png.name, png)])
    if not detail.get("pinned"):
        api.pin_message(summary, detail["id"])
    link = f"https://discord.com/channels/{ids['guild_id']}/{summary}/{detail['id']}"

    keys = ("p1-core-mascot", "p2-user", "p3-agent", "p4-rag", "p5-tools", "p6-renderer", "p7-suggest-ml", "p8-export-qa")
    pings = " ".join(f"<@&{roles[key]}>" for key in keys)
    alert_payload = {
        "content": (f"🔔 **อัปเดตไดอะแกรม COPIE ใหม่ — โฟลว์ว่าใครส่งอะไรให้ใคร** {pings}\n"
                    f"ดูภาพธีมเดียวกับเว็บ + งานที่เริ่มได้ + จุดรอของจริง: {link}\n-# {MARKER}"),
        "allowed_mentions": {"roles": [roles[key] for key in keys]},
    }
    old_alert = marked(api, announcements, MARKER)
    if old_alert:
        api.edit_message(announcements, old_alert["id"], alert_payload)
    else:
        api.send_message(announcements, alert_payload)

    # Retire only the two posts made by the earlier, card-style version.
    for channel in (summary, announcements):
        obsolete = marked(api, channel, OLD_MARKER)
        if obsolete and obsolete["id"] != detail["id"]:
            api.delete(f"/channels/{channel}/messages/{obsolete['id']}")
    return link


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--post", action="store_true")
    args = parser.parse_args()
    picture = render()
    print(picture)
    if args.post:
        print(post(picture))
