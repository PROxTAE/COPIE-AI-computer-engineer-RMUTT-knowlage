"""Validate data/eval/questions.jsonl against the plan and against the real data files.

    python scripts/eval/check_questions.py

Checks every line: JSON, fields, labels, 60 questions with the planned group sizes, and that
every must_contain term can be found in the data it cites in data/eval/evidence.json
(curriculum terms are recomputed from curriculum.json, not copied). Exit code 1 on any error.
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUESTIONS = ROOT / "data/eval/questions.jsonl"
EVIDENCE = ROOT / "data/eval/evidence.json"

INTENTS = {"department_info", "curriculum", "course_detail", "skill_analysis", "general", "clarify"}
USER_TYPES = {"prospective", "current_student", "near_graduate"}
# 00_API_AND_DATA_CONTRACTS.md section 8: which response_type each intent may produce
TYPES_BY_INTENT = {
    "curriculum": {"course_table", "cards"},
    "course_detail": {"cards"},
    "department_info": {"text"},
    "skill_analysis": {"assessment_form", "skill_radar"},
    "general": {"text"},
    "clarify": {"text"},
}
# 08_EXPORT_QA_EVAL.md "Eval set": group -> (intent, count)
GROUPS = {
    "curriculum": ("curriculum", 12),
    "course_detail": ("course_detail", 8),
    "department_info": ("department_info", 15),
    "skill_analysis": ("skill_analysis", 6),
    "general": ("general", 9),
    "out_of_scope": ("general", 10),
}
FIELDS = {"id": str, "question": str, "intent": str, "expected_type": str, "must_contain": list,
          "user_type": str, "study_year": (int, type(None))}

errors: list[str] = []


def error(where: str, text: str) -> None:
    errors.append(f"{where}: {text}")


def load_questions() -> list[dict]:
    rows = []
    for number, line in enumerate(QUESTIONS.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            error(f"line {number}", "empty line")
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            error(f"line {number}", f"invalid JSON ({exc})")
            continue
        rows.append(row)
    return rows


def check_fields(row: dict) -> None:
    where = row.get("id", "?")
    for name, kind in FIELDS.items():
        if name not in row:
            error(where, f"missing field {name}")
        elif not isinstance(row[name], kind):
            error(where, f"{name} has the wrong type")
    extra = set(row) - set(FIELDS)
    if extra:
        error(where, f"unknown fields {sorted(extra)}")
    if not str(row.get("question", "")).strip():
        error(where, "question is empty")
    if row.get("intent") not in INTENTS:
        error(where, f"unknown intent {row.get('intent')!r}")
    elif row.get("expected_type") not in TYPES_BY_INTENT[row["intent"]]:
        error(where, f"expected_type {row.get('expected_type')!r} is not produced by intent {row['intent']}")
    if not all(isinstance(t, str) and t.strip() for t in row.get("must_contain", [])):
        error(where, "must_contain must be non-empty strings")
    user_type, year = row.get("user_type"), row.get("study_year")
    if user_type not in USER_TYPES:
        error(where, f"unknown user_type {user_type!r}")
    elif user_type == "prospective" and year is not None:
        error(where, "prospective users have no study_year")
    elif user_type != "prospective" and year not in (1, 2, 3, 4):
        error(where, "students need study_year 1-4")


def curriculum() -> dict:
    return json.loads((ROOT / "data/curriculum/curriculum.json").read_text(encoding="utf-8"))


def course_terms(course: dict) -> set[str]:
    terms = {course["code"], course["name_th"], course["name_en"], f"ปี {course['year']} เทอม {course['semester']}"}
    if course.get("credit_detail"):
        terms.add(course["credit_detail"])
    return {t for t in terms if t}


def allowed_terms(evidence: dict) -> tuple[set[str] | None, str | None]:
    """Terms the cited data can back, or (None, text) to search a text file instead."""
    kind = evidence.get("kind")
    if kind == "term":
        courses = [c for c in curriculum()["courses"]
                   if (c["year"], c["semester"]) == (evidence["year"], evidence["semester"])]
        if not courses:
            return set(), None
        terms = set().union(*(course_terms(c) for c in courses))
        return terms | {str(sum(c["credits"] for c in courses))}, None
    if kind == "course":
        match = [c for c in curriculum()["courses"] if c["code"] == evidence["code"]]
        return (course_terms(match[0]) if match else set()), None
    if kind == "program_total":
        data = curriculum()
        total = data["total_credits"]
        if total != sum(c["credits"] for c in data["courses"]):
            return set(), None
        return {str(total)}, None
    if kind == "overview":
        return {f"ปี {y}" for y in sorted({c["year"] for c in curriculum()["courses"]})}, None
    if kind == "assessment":
        data = json.loads((ROOT / evidence["file"]).read_text(encoding="utf-8"))
        return {data["assessment_id"]}, None
    if kind == "doc":
        texts = []
        for path in evidence["files"]:
            text = (ROOT / path).read_text(encoding="utf-8")
            if "\nsource_url: http" not in text:
                error(path, "knowledge file has no source_url")
            texts.append(text)
        return None, "\n".join(texts)
    if kind == "none":
        return set(), None
    raise ValueError(f"unknown evidence kind {kind!r}")


def check_evidence(row: dict, entry: dict | None) -> None:
    where = row["id"]
    if entry is None:
        error(where, "no entry in evidence.json")
        return
    group = entry.get("group")
    if group not in GROUPS:
        error(where, f"unknown group {group!r}")
    elif GROUPS[group][0] != row["intent"]:
        error(where, f"group {group} expects intent {GROUPS[group][0]}")
    try:
        terms, text = allowed_terms(entry.get("evidence", {}))
    except (OSError, KeyError, ValueError) as exc:
        error(where, f"cannot read evidence ({exc})")
        return
    for term in row["must_contain"]:
        found = term in text if text is not None else term in terms
        if not found:
            error(where, f"must_contain {term!r} is not backed by {entry['evidence']}")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # Thai output on Windows consoles
    rows = load_questions()
    for row in rows:
        check_fields(row)
    ids = [row.get("id") for row in rows]
    expected_ids = [f"e{n:03d}" for n in range(1, len(rows) + 1)]
    if ids != expected_ids:
        error("ids", "ids must be unique and run e001, e002, ... in file order")
    if len(rows) != 60:
        error("count", f"{len(rows)} questions, plan requires 60")
    questions = {row["question"].strip() for row in rows if "question" in row}
    if len(questions) != len(rows):
        error("questions", "duplicate question text")

    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    if set(evidence) - set(ids):
        error("evidence.json", f"entries without a question: {sorted(set(evidence) - set(ids))}")
    for row in rows:
        if "id" in row and "intent" in row and isinstance(row.get("must_contain"), list):
            check_evidence(row, evidence.get(row["id"]))

    groups = Counter(evidence[i]["group"] for i in ids if i in evidence)
    print("group            intent           planned  actual")
    for group, (intent, planned) in GROUPS.items():
        mark = "" if groups[group] == planned else "  <-- mismatch"
        if mark:
            error("count", f"group {group} has {groups[group]}, plan requires {planned}")
        print(f"{group:<16} {intent:<16} {planned:>7}  {groups[group]:>6}{mark}")
    print("\nexpected_type:", dict(Counter(row.get("expected_type") for row in rows)))
    print("intent label: ", dict(Counter(row.get("intent") for row in rows)))
    print("user_type:    ", dict(Counter(row.get("user_type") for row in rows)))
    checked = sum(len(row.get("must_contain", [])) for row in rows)
    backed = sum(1 for row in rows if row.get("must_contain"))
    print(f"must_contain:  {checked} terms in {backed} questions, each traced to its data file")
    print("review:       ", dict(Counter(evidence[i]["review"] for i in ids if i in evidence)))

    if errors:
        print(f"\n{len(errors)} problem(s):")
        for line in errors:
            print("  -", line)
        return 1
    print(f"\nOK: {len(rows)} questions valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
