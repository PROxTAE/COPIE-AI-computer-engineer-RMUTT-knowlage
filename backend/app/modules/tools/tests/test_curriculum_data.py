"""Checks for the verified year 1–2 curriculum slice."""

import json
from collections import Counter
from pathlib import Path

from app.schemas.contract import Course


DATA_FILE = Path(__file__).resolve().parents[5] / "data" / "curriculum" / "curriculum.json"


def test_curriculum_year_one_and_two_match_study_plan() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    courses = [Course.model_validate(row) for row in data["courses"]]

    assert data["curriculum_year"] == "2568"
    assert data["total_credits"] == 141
    assert len(courses) == 29
    assert {(course.year, course.semester) for course in courses} == {
        (1, 1), (1, 2), (2, 1), (2, 2)
    }

    totals = Counter()
    for course in courses:
        totals[(course.year, course.semester)] += course.credits
    assert dict(totals) == {(1, 1): 19, (1, 2): 21, (2, 1): 20, (2, 2): 21}

    concrete_codes = [course.code for course in courses if "x" not in course.code]
    assert len(concrete_codes) == len(set(concrete_codes))
