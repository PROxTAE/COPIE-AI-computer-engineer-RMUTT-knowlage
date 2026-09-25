"""Curriculum interface pending the Phase 2 service implementation."""

from app.schemas.contract import CardsData, Course, CourseTableData


def _unavailable() -> None:
    raise NotImplementedError(
        "Curriculum service is planned for P5 Phase 2"
    )


def get_courses(year: int, semester: int) -> CourseTableData | None:
    _unavailable()


def get_course_detail(query: str) -> Course | None:
    _unavailable()


def get_total_credits(year: int | None = None, semester: int | None = None) -> int:
    _unavailable()


def get_curriculum_overview() -> CardsData:
    _unavailable()
