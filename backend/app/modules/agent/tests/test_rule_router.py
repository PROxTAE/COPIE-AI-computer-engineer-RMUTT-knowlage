import pytest

from app.modules.agent.rule_router import rule_route


@pytest.mark.parametrize(
    ("message", "intent", "year", "semester"),
    [
        ("ปี 2 เทอม 1 เรียนอะไรบ้าง", "curriculum", 2, 1),
        ("ปี1เทอม2", "curriculum", 1, 2),
        ("ชั้นปีที่ 3 ภาคเรียนที่ 2 มีวิชาอะไร", "curriculum", 3, 2),
        ("year 4 semester 1", "curriculum", 4, 1),
        ("เทอมหน้าเรียนไร", "curriculum", None, None),
        ("หลักสูตรมีกี่หน่วยกิต", "curriculum", None, None),
        ("ปี 3 เรียนอะไร", "curriculum", 3, None),
        ("ปีสามเทอมสองเรียนไร", "curriculum", 3, 2),
    ],
)
def test_curriculum(message: str, intent: str, year: int | None, semester: int | None) -> None:
    route = rule_route(message)
    assert (route.intent, route.year, route.semester, route.source) == (intent, year, semester, "rule")


@pytest.mark.parametrize("message", ["ช่วยวิเคราะห์ skill ของผม", "ผมถนัดสายไหน", "อยากทำแบบประเมิน", "สกิลผมเป็นยังไง", "อยากรู้ว่าตัวเองเหมาะกับ AI ไหม"])
def test_skill(message: str) -> None:
    assert rule_route(message).intent == "skill_analysis"


@pytest.mark.parametrize(
    ("message", "query"),
    [
        ("04-000-101 คือวิชาอะไร", "04-000-101"),
        ("วิชา Data Structure เรียนเกี่ยวกับอะไร", "Data Structure"),
        ("วิชาไมโครคอนโทรลเลอร์ยากไหม", "ไมโครคอนโทรลเลอร์"),
    ],
)
def test_course_detail(message: str, query: str) -> None:
    route = rule_route(message)
    assert (route.intent, route.course_query) == ("course_detail", query)


@pytest.mark.parametrize("message", ["สวัสดีครับ", "ขอบคุณมาก", "hello"])
def test_greeting(message: str) -> None:
    assert rule_route(message).intent == "general"


@pytest.mark.parametrize("message", ["ภาคคอมเรียนเกี่ยวกับอะไร", "มีแล็บอะไรบ้าง", "ค่าเทอมเท่าไหร่", "จบไปทำงานอะไรได้"])
def test_department_info_is_fallback(message: str) -> None:
    route = rule_route(message)
    assert route.intent == "department_info"
    assert route.search_query == message
