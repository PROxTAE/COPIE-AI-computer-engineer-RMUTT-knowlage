#!/usr/bin/env python
"""Render and publish the current COPIE work split to Discord.

Run without arguments to render the image. Pass --post to update or create the
pinned detail in #project-summary and notify the team in #announcements.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from discord_api import Discord, load_dotenv

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "docs" / "diagrams" / "copie-team-start.png"
MARKER = "copie-team-start-2026-09-25"

INK = "#111A30"
BLUE = "#155FF2"
MUTED = "#5F7088"
LINE = "#D7E5F8"
PAPER = "#F8FBFF"
CYAN = "#45CFE9"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    file = "leelawdb.ttf" if bold else "LeelawUI.ttf"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / file), size)


def render() -> Path:
    im = Image.new("RGB", (1800, 1590), PAPER)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((55, 48, 1745, 1542), 36, fill="white", outline=LINE, width=3)
    d.rounded_rectangle((55, 48, 1745, 252), 36, fill=INK)
    d.rectangle((55, 205, 1745, 252), fill=INK)
    d.text((102, 81), "COPIE  /  ใครเริ่มอะไรได้เลย", font=font(55, True), fill="white")
    d.text((104, 164), "8 คนเริ่มพร้อมกันจาก contract กลาง • ใช้ mock / stub ระหว่างรอของจริง", font=font(30), fill="#CDEAFF")

    cards = [
        ("P1", "หน้าเว็บ + มาสคอต", "เริ่ม: app shell, workspace, สถานะ COPIE", "รับตอนต่อจริง: chat API P3, renderer P6, user P2"),
        ("P2", "ผู้ใช้ + ประวัติ", "เริ่ม: DB, Dev Login, API/context stub", "ส่ง: user context ให้ P3; login/history ให้ P1"),
        ("P3", "Agent + Backend", "เริ่ม: mock chat API, router, LLM client", "รับตอนต่อจริง: user P2, RAG P4, tools P5"),
        ("P4", "RAG ข้อมูลภาค", "เริ่ม: หาเอกสารจริง, จัดแหล่งอ้างอิง, search stub", "ส่ง: search + sources ให้ P3; รอเอกสารที่ยืนยันได้"),
        ("P5", "หลักสูตร + ทักษะ", "เริ่ม: หาเล่มหลักสูตร, schema, tool stub, สูตรคะแนน", "ส่ง: curriculum/skill ให้ P3; ตัวอย่างให้ P6"),
        ("P6", "หน้าตาคำตอบ", "เริ่ม: fixtures ตาม contract, /dev, text/table/form", "ส่ง: ResponseRenderer ให้ P1; รอข้อมูลจริงตอนรวม"),
        ("P7", "คำถามแนะนำ + ML", "เริ่ม: prompts แบบ static ได้ทันที", "รอ: ชุดคำถาม P8, user type P2; ส่ง ML ให้ P3"),
        ("P8", "QA + Export", "เริ่ม: 60 คำถาม, checklist, ปุ่ม Copy", "รอ: Dev Login P2, chat P3, เฉลย P4/P5"),
    ]
    for idx, (key, title, start, handoff) in enumerate(cards):
        col, row = idx % 2, idx // 2
        x = 105 + col * 810
        y = 305 + row * 264
        d.rounded_rectangle((x, y, x + 770, y + 226), 26, fill="#FFFFFF", outline=LINE, width=3)
        d.rounded_rectangle((x + 22, y + 22, x + 110, y + 80), 14, fill=BLUE if idx < 6 else "#33627F")
        d.text((x + 40, y + 29), key, font=font(30, True), fill="white")
        d.text((x + 131, y + 25), title, font=font(36, True), fill=INK)
        d.line((x + 24, y + 96, x + 746, y + 96), fill=LINE, width=2)
        d.text((x + 27, y + 111), start, font=font(25), fill=INK)
        d.text((x + 27, y + 163), handoff, font=font(23), fill=MUTED)

    y = 1381
    d.rounded_rectangle((105, y, 1695, y + 123), 22, fill="#EAF4FF")
    d.ellipse((139, y + 30, 167, y + 58), fill=CYAN)
    d.text((190, y + 23), "จุดรวมระบบ: P2 + P4 + P5 > P3 > P1 + P6 > ผู้ใช้", font=font(31, True), fill=INK)
    d.text((190, y + 69), "P7 เสริม P1/P3  •  P8 ทดสอบทุกเส้นทาง  •  mock ใช้พัฒนาเท่านั้น ห้ามอยู่ใน demo จริง", font=font(25), fill=MUTED)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    im.save(OUT, optimize=True)
    return OUT


def find_marked(api: Discord, channel: str, marker: str) -> dict | None:
    for message in api.get(f"/channels/{channel}/messages?limit=100"):
        if marker in (message.get("content") or ""):
            return message
    return None


def post(png: Path) -> None:
    load_dotenv()
    api = Discord()
    ids = json.loads((HERE / "out" / "discord-ids.json").read_text(encoding="utf-8"))
    channels, roles = ids["channel_ids"], ids["role_ids"]
    summary = channels["project-summary"]
    mention = lambda key: f"<@&{roles[key]}>"

    description = (
        "**เริ่มได้เลยทั้ง 8 คน** — contract ของ frontend/backend มีแล้ว จึงทำส่วนของตัวเองคู่ขนานได้ "
        "โดยใช้ stub (ฟังก์ชันชั่วคราว) หรือ fixture (ข้อมูลตัวอย่างตาม contract) ก่อนต่อของจริง\n\n"
        f"**P1** {mention('p1-core-mascot')} เว็บหลัก/ธีม/มาสคอต 2.5D: ทำ workspace และ chat store ได้เลย; "
        "ตอนรวมรับ `/api/chat` จาก P3, `<ResponseRenderer />` จาก P6 และ login/history จาก P2\n"
        f"**P2** {mention('p2-user')} ผู้ใช้: เริ่ม DB, Dev Login, onboarding, `get_user_context` และ history stub; "
        "ส่ง context/history ให้ P3, ส่ง AuthGuard/sidebar/feedback ให้ P1, Dev Login ให้ P8\n"
        f"**P3** {mention('p3-agent')} Agent/API: เริ่ม mock `/api/chat`, rule router, LLM client; "
        "ส่ง response ตาม contract ให้ P1/P6/P8; รอของจริงจาก P2/P4/P5 เฉพาะตอนต่อระบบ\n"
        f"**P4** {mention('p4-rag')} RAG: เริ่มรวบรวมเอกสารภาคที่ตรวจสอบที่มาได้ + search stub; "
        "ส่ง `search_department_knowledge()` พร้อม sources ให้ P3; รอเอกสารจริงที่อ้างอิงได้ และสรุปหลักสูตรจาก P5 ภายหลัง\n"
        f"**P5** {mention('p5-tools')} หลักสูตร/Skill: เริ่มหาเล่มหลักสูตร, กำหนดข้อมูลรายวิชา, tool stubs, แบบประเมินและสูตรคะแนน; "
        "ส่งฟังก์ชันให้ P3 และตัวอย่างข้อมูลให้ P6; ตารางจริงต้องตรวจจากเล่มก่อนใช้\n"
        f"**P6** {mention('p6-renderer')} Renderer: ทำ fixtures ครบทุก `response_type` และหน้า `/dev` ได้เลย; "
        "ส่ง `<ResponseRenderer />` ให้ P1; รับ tokens/UI จาก P1 และข้อมูลตัวอย่างจาก P5\n"
        f"**P7** {mention('p7-suggest-ml')} คำถามแนะนำ/ML: เริ่ม prompts แบบ static ได้; "
        "รับ eval set จาก P8 + user type จาก P2 ก่อน train/ปรับตามผู้ใช้; ส่ง component ให้ P1 และ `predict_intent()` ให้ P3 (ส่วนเสริม)\n"
        f"**P8** {mention('p8-export-qa')} QA/Export: เริ่มชุดทดสอบ 60 ข้อ, demo checklist, Copy ได้; "
        "รับ Dev Login P2, chat จริง P3, เฉลย P4/P5 ก่อนวัดผล; ส่งชุดคำถามให้ P7 และผล QA ให้ทุกคน"
    )
    status = (
        "**สถานะจากไฟล์ในเครื่อง ณ 25 ก.ย. 2026**\n"
        "✅ มี contract สองฝั่ง, โครง FastAPI/Next.js, ธีมและภาพมาสคอต, mockup 11 หน้า\n"
        "🟡 ยังเป็นโครง: `/chat`, login/onboarding, user service, Agent, RAG, Tools, Renderer, Suggestions, Export\n"
        "❗ยังไม่พบใน repo: เอกสาร knowledge จริง, `curriculum.json` + แหล่งที่มา, `skill_v1.json`, "
        "`questions.jsonl`, chat API จริง และ `docker-compose.yml`\n\n"
        "**สิ่งที่ต้องส่งให้กันก่อน:** P2/P4/P5 ส่ง stub signature ให้ P3, P3 ส่ง mock `/api/chat` ให้ P1/P6, "
        "P6 ส่ง fixtures/Renderer ให้ P1, P8 ส่งชุดคำถามมี label ให้ P7. "
        "เปลี่ยน contract ให้คุยในห้อง contract และให้ P1+P3 review\n"
        "**mock ใช้เพื่อพัฒนาได้** แต่ก่อน demo ต้องสลับเป็นข้อมูลจริงและทดสอบ flow 1–6; "
        f"ถ้าขาดเอกสาร/เล่มหลักสูตรหรือส่งต่องานไม่ทัน ให้แจ้ง <#{channels['blockers']}> พร้อมระบุไฟล์/ฟังก์ชันที่รอ"
    )
    payload = {
        "content": f"📌 แผนเริ่มงานและจุดส่งต่อ COPIE | {MARKER}",
        "embeds": [
            {"title": "ใครทำอะไร เริ่มได้เลยหรือรอใคร", "description": description, "color": 0x155FF2,
             "image": {"url": f"attachment://{png.name}"}},
            {"title": "ตอนนี้มีอะไรแล้ว / ยังขาดอะไร", "description": status, "color": 0x45CFE9},
        ],
        "allowed_mentions": {"parse": []},
    }
    old = find_marked(api, summary, MARKER)
    if old:
        detail = api.edit_message_files(summary, old["id"], payload, files=[(png.name, png)])
    else:
        detail = api.send_message(summary, payload, files=[(png.name, png)])
    if not detail.get("pinned"):
        api.pin_message(summary, detail["id"])
    link = f"https://discord.com/channels/{ids['guild_id']}/{summary}/{detail['id']}"
    announcement = channels["announcements"]
    alert = find_marked(api, announcement, MARKER)
    role_pings = " ".join(mention(k) for k in roles if k.startswith("p") and k in (
        "p1-core-mascot", "p2-user", "p3-agent", "p4-rag", "p5-tools", "p6-renderer", "p7-suggest-ml", "p8-export-qa"))
    alert_payload = {
        "content": (f"🔔 **COPIE: ทุกคนเริ่มงานส่วนตัวเองได้เลย** {role_pings}\n"
                    "แผนภาพ + รายคน + งานที่ทำด้วย mock/stub ได้ + จุดรอของจริง + สิ่งที่ repo ยังขาด: "
                    f"{link}\n"
                    f"-# {MARKER}"),
        "allowed_mentions": {"roles": [roles[k] for k in (
            "p1-core-mascot", "p2-user", "p3-agent", "p4-rag", "p5-tools", "p6-renderer", "p7-suggest-ml", "p8-export-qa")]},
    }
    if alert:
        api.edit_message(announcement, alert["id"], alert_payload)
    else:
        api.send_message(announcement, alert_payload)
    print(link)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--post", action="store_true")
    args = parser.parse_args()
    image = render()
    print(image)
    if args.post:
        post(image)
