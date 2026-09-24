# user — Auth / Profile / History / Skill store / Feedback (backend)

| | |
|---|---|
| เจ้าของ | **P2** |
| แผนงาน | [`02_USER_SYSTEM.md`](../../../../IMPLEMENTATION_PLANS/02_USER_SYSTEM.md) |
| Branch prefix | ดู `IMPLEMENTATION_PLANS/00_GIT_DELIVERY_RULES.md` §2 |

## หน้าที่

ตาราง DB ทั้งหมด (SQLite/SQLModel), Google verify + JWT, endpoint `/api/auth/*`, `/api/users/*`, `/api/conversations*`, `/api/skills/me`, `/api/feedback`, `/api/stats` และ service ที่ Agent เรียกใช้

## โครงไฟล์ที่จะสร้าง

```text
user/
├─ __init__.py       # re-export public functions + router
├─ database.py       # engine, get_session(), create_all()
├─ models.py         # User, Conversation, Message, SkillProfileRow, Feedback
├─ auth/             # google.py, jwt.py, deps.py (get_current_user)
├─ services/         # user_service.py, history_service.py, skill_store.py
├─ routers/          # auth.py, users.py, history.py, feedback.py, skills.py, stats.py
└─ tests/
```

## Public API (สิ่งที่ module อื่นเรียกใช้ได้)

`router`, `get_current_user`, `get_session`, `get_user_context`, `get_or_create_conversation`, `add_user_message`, `add_assistant_message`, `get_recent_messages`, `save_skill_profile`, `get_latest_skill` (signature ใน `00_API_AND_DATA_CONTRACTS.md` §4)

## ใช้ของ module อื่นได้จาก

`app.core`, `app.schemas.contract`
