"""Regex intent router. Used when the LLM router fails, so it must never raise."""
import re

from app.modules.agent.types import RouteResult

_YEAR = re.compile(r"(?:ปี|year)\s*(?:ที่\s*)?([1-4])", re.IGNORECASE)
_SEMESTER = re.compile(r"(?:เทอม|ภาคเรียน|ภาคการศึกษา|semester|term)\s*(?:ที่\s*)?([1-3])", re.IGNORECASE)
_COURSE_CODE = re.compile(r"\b\d{2}-\d{3}-\d{3}\b|\b\d{7,10}\b")
_SKILL = re.compile(r"skill|สกิล|ถนัด|ประเมิน|วิเคราะห์.*(?:ตัวเอง|ของ(?:ผม|หนู|ฉัน|เรา))|เหมาะกับสาย", re.IGNORECASE)
_CURRICULUM = re.compile(r"หน่วยกิต|แผนการเรียน|รายวิชา|เทอม(?:นี้|หน้า)|ปี(?:นี้|หน้า)|เรียนวิชาอะไร|credit", re.IGNORECASE)
_COURSE_NAME = re.compile(r"วิชา\s*(.+?)\s*(?:เรียน|คือ|เกี่ยวกับ|มีอะไร|สอน|ยาก|$)")
_GREETING = re.compile(r"^\s*(?:สวัสดี|หวัดดี|ดีครับ|ดีค่ะ|ขอบคุณ|hello|hi\b|hey\b|thank)", re.IGNORECASE)


def rule_route(message: str) -> RouteResult:
    text = message.strip()
    year = _first_int(_YEAR, text)
    semester = _first_int(_SEMESTER, text)

    if _SKILL.search(text):
        return RouteResult(intent="skill_analysis", source="rule")

    code = _COURSE_CODE.search(text)
    if code:
        return RouteResult(intent="course_detail", course_query=code.group(0), source="rule")

    if year or semester or _CURRICULUM.search(text):
        return RouteResult(intent="curriculum", year=year, semester=semester, source="rule")

    name = _COURSE_NAME.search(text)
    if name and name.group(1):
        return RouteResult(intent="course_detail", course_query=name.group(1), source="rule")

    if _GREETING.search(text):
        return RouteResult(intent="general", source="rule")

    return RouteResult(intent="department_info", search_query=text, source="rule")


def _first_int(pattern: re.Pattern[str], text: str) -> int | None:
    match = pattern.search(text)
    return int(match.group(1)) if match else None
