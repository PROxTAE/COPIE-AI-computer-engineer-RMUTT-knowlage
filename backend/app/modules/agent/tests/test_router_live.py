"""Intent accuracy against the real LLM. Skipped unless GEMINI_API_KEY is set.

Run: python -m pytest -q app/modules/agent/tests/test_router_live.py -s
"""
import pytest

from app.core.config import settings
from app.modules.agent.intent_router import route

pytestmark = pytest.mark.skipif(not settings.gemini_api_key, reason="GEMINI_API_KEY not set")

TARGET_ACCURACY = 0.85

CASES = [
    ("ปี 2 เทอม 1 เรียนอะไรบ้าง", "curriculum"),
    ("เทอมหน้าเรียนไรอะ", "curriculum"),
    ("ปี1 เทอม2 มีวิชาไรบ้าง", "curriculum"),
    ("หลักสูตรนี้ต้องเก็บกี่หน่วยกิต", "curriculum"),
    ("ปีสามเรียนหนักไหม มีวิชาอะไร", "curriculum"),
    ("วิชา Data Structure เรียนเกี่ยวกับอะไร", "course_detail"),
    ("ไมโครคอนโทรลเลอร์ เรียนเกี่ยวกับอะไรครับ", "course_detail"),
    ("วิชา network เบื้องต้นสอนอะไร", "course_detail"),
    ("ภาคคอมเรียนเกี่ยวกับอะไร", "department_info"),
    ("จบคอมไปทำงานอะไรได้บ้าง", "department_info"),
    ("ค่าเทอมเท่าไหร่", "department_info"),
    ("มีแล็บอะไรบ้าง", "department_info"),
    ("สมัครเรียนต้องใช้เกรดเท่าไหร่", "department_info"),
    ("ฝึกงานตอนปีไหน", "department_info"),
    ("ช่วยวิเคราะห์ skill ของผมหน่อย", "skill_analysis"),
    ("ผมถนัดสายไหน", "skill_analysis"),
    ("อยากรู้ว่าตัวเองเหมาะกับ AI ไหม", "skill_analysis"),
    ("สวัสดีครับ", "general"),
    ("ขอบคุณมากครับ", "general"),
    ("เริ่มเขียนโปรแกรมควรเรียนภาษาอะไรก่อน", "general"),
]


def test_router_accuracy() -> None:
    results = [(q, want, route(q)) for q, want in CASES]
    wrong = [(q, want, r.intent, r.source) for q, want, r in results if r.intent != want]
    for row in wrong:
        print("MISS", row)
    accuracy = 1 - len(wrong) / len(CASES)
    print(f"accuracy {accuracy:.0%} ({len(CASES) - len(wrong)}/{len(CASES)})")
    assert accuracy >= TARGET_ACCURACY
