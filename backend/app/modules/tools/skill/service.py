"""Skill interface pending the assessment and scoring phase."""

from app.schemas.contract import AssessmentAnswer, AssessmentFormData, SkillScores


def _unavailable() -> None:
    raise NotImplementedError("Skill assessment is planned for the later P5 phase")


def get_assessment() -> AssessmentFormData:
    _unavailable()


def calculate_skill(answers: list[AssessmentAnswer]) -> SkillScores:
    _unavailable()


def top_skills(scores: SkillScores, n: int = 2) -> list[str]:
    _unavailable()
