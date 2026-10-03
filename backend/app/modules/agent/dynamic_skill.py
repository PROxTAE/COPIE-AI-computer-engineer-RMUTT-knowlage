"""Dynamic Skill Assessment generation, topic detection, and assessment registry."""

import hashlib
import logging
import re
from uuid import uuid4

from app.modules.agent.llm_client import LLMError, generate_json
from app.schemas.contract import (
    AssessmentAnswer,
    AssessmentFormData,
    AssessmentOption,
    AssessmentQuestion,
    SkillDimension,
    SkillProfile,
    SkillScores,
)

log = logging.getLogger(__name__)

# Registry: assessment_id -> assessment definition
DYNAMIC_ASSESSMENTS: dict[str, dict] = {}


def extract_skill_topic(message: str) -> tuple[str, bool]:
    """
    Extract the skill topic from user message.
    Returns (topic_name, is_general_cpe).
    """
    text = message.strip()

    # Pattern: "สกิล<topic>", "ทักษะ<topic>", "ด้าน<topic>"
    match = re.search(
        r"(?:สกิล|ทักษะ|ความสามารถด้าน|ความถนัดด้าน|เรื่อง)\s*([a-zA-Zก-๙0-9\s\.\+\#]+?)(?:\s*(?:ของผม|ของหนู|ของฉัน|ของเรา|ผม|หนู|ฉัน|เรา|ตอนนี้|ไหม|ดีไหม|เก่งไหม|ระดับไหน|หรือยัง|\?|$))",
        text,
        re.IGNORECASE,
    )
    if match:
        extracted = match.group(1).strip()
        extracted = re.sub(r"^(?:ของ|ใน|การ)\s*", "", extracted).strip()
        extracted = re.sub(r"\s+(?:ของผม|ของหนู|ของฉัน|ของเรา|ผม|หนู|ฉัน|เรา)$", "", extracted).strip()
        if extracted and len(extracted) >= 2 and extracted not in ("ผม", "หนู", "เรา", "ฉัน", "ตัวเอง"):
            if any(t in extracted.lower() for t in ("ทั่วไป", "skill", "สกิล", "ความถนัด")):
                return "วิศวกรรมคอมพิวเตอร์", True
            return extracted, False

    common_non_cpe = [
        "ทำอาหาร", "อาหาร", "cooking", "วาดรูป", "ดนตรี", "กีฬา", "ถ่ายภาพ", "ภาษาอังกฤษ",
        "การสื่อสาร", "การพูด", "การขาย", "การตลาด", "บัญชี", "จิตวิทยา", "บริหาร", "ทำขนม"
    ]
    for kw in common_non_cpe:
        if kw in text:
            return kw, False

    tech_topics = [
        "python", "javascript", "react", "vue", "golang", "java", "c++", "rust",
        "flutter", "docker", "kubernetes", "cloud", "aws", "gcp", "azure",
        "machine learning", "deep learning", "nlp", "computer vision",
        "sql", "database", "devops", "linux", "git", "web development", "game development"
    ]
    for tech in tech_topics:
        if tech in text.lower():
            return tech, False

    return "วิศวกรรมคอมพิวเตอร์", True


DYNAMIC_PROMPT_SYSTEM = """คุณคือผู้เชี่ยวชาญด้านการออกแบบแบบประเมินทักษะ (Skill Assessment)
สร้างแบบประเมินทักษะภาษาไทยในหัวข้อที่กำหนด โดยให้มี:
1. "dimensions": ด้าน/มิติของทักษะในหัวข้อนั้นๆ 5 ถึง 6 ด้าน เพื่อใช้พลอตกราฟ Radar และประเมินคะแนนรายด้าน แต่ละด้านมี:
   - "key": รหัสประจำด้าน (เช่น "dim1", "dim2", ...)
   - "label": ชื่อเต็มของด้านนั้น (เช่น "การเลือกและเตรียมวัตถุดิบ", "เทคนิคความร้อนและการปรุง", "การปรุงรสและบาลานซ์รสชาติ")
   - "short_label": ชื่อย่อกระชับสำหรับแกนกราฟ Radar 2-4 คำ (เช่น "เตรียมวัตถุดิบ", "เทคนิคความร้อน", "การปรุงรส")
2. "questions": คำถาม 5 ถึง 6 ข้อ โดยแต่ละข้อตรงกับ 1 ด้านใน dimensions (ระบุ "dimension_key" ให้ตรงกับ key ของ dimension) แต่ละข้อมีตัวเลือก 5 ระดับ (0 ถึง 4) ตั้งแต่ระดับเริ่มต้นจนถึงระดับเชี่ยวชาญ

ตอบเป็น JSON object เท่านั้น รูปแบบ:
{
  "title": "แบบประเมินทักษะ: <ชื่อหัวข้อ>",
  "dimensions": [
    {"key": "dim1", "label": "<ชื่อเต็มด้านที่ 1>", "short_label": "<ชื่อย่อด้านที่ 1>"},
    {"key": "dim2", "label": "<ชื่อเต็มด้านที่ 2>", "short_label": "<ชื่อย่อด้านที่ 2>"},
    {"key": "dim3", "label": "<ชื่อเต็มด้านที่ 3>", "short_label": "<ชื่อย่อด้านที่ 3>"},
    {"key": "dim4", "label": "<ชื่อเต็มด้านที่ 4>", "short_label": "<ชื่อย่อด้านที่ 4>"},
    {"key": "dim5", "label": "<ชื่อเต็มด้านที่ 5>", "short_label": "<ชื่อย่อด้านที่ 5>"},
    {"key": "dim6", "label": "<ชื่อเต็มด้านที่ 6>", "short_label": "<ชื่อย่อด้านที่ 6>"}
  ],
  "questions": [
    {
      "id": "q1",
      "dimension_key": "dim1",
      "text": "<คำถามที่ 1>",
      "options": [
        {"value": 0, "label": "ไม่มีพื้นฐาน / ไม่เคยทำ"},
        {"value": 1, "label": "มีความรู้เริ่มต้น ทำตามคำแนะนำได้"},
        {"value": 2, "label": "ทำได้ด้วยตนเองตามมาตรฐาน"},
        {"value": 3, "label": "คล่องแคล่ว แก้ปัญหาเฉพาะหน้าได้ดี"},
        {"value": 4, "label": "เชี่ยวชาญระดับสูง และถ่ายทอดเทคนิคได้"}
      ]
    },
    ... (รวม 5 หรือ 6 ข้อ id q1 ถึง q5 หรือ q6)
  ]
}
"""


def generate_dynamic_assessment_form(topic: str) -> AssessmentFormData:
    """Generate dynamic form with custom dimensions via LLM with fallback template."""
    prompt = f"สร้างแบบประเมินทักษะหัวข้อ: {topic}"
    try:
        data = generate_json(DYNAMIC_PROMPT_SYSTEM, prompt)
        raw_dims = data.get("dimensions", [])
        dims_map = {}
        dimensions = []
        for i, d in enumerate(raw_dims, start=1):
            key = str(d.get("key") or f"dim{i}")
            label = str(d.get("label") or f"ทักษะด้านที่ {i}")
            short_label = str(d.get("short_label") or label[:12])
            dim_obj = {"key": key, "label": label, "short_label": short_label}
            dimensions.append(dim_obj)
            dims_map[key] = dim_obj

        questions = []
        for i, q in enumerate(data.get("questions", []), start=1):
            qid = f"q{i}"
            dim_key = str(q.get("dimension_key") or f"dim{i}")
            qtext = q.get("text", f"ทักษะและการปฏิบัติด้าน {topic} ขั้นที่ {i}")
            options = []
            for opt in q.get("options", []):
                options.append(
                    AssessmentOption(
                        value=int(opt.get("value", 0)),
                        label=str(opt.get("label", "")),
                    )
                )
            if len(options) == 5:
                questions.append(AssessmentQuestion(id=qid, text=qtext, options=options))
                # ensure dimension key is recorded
                if dim_key not in dims_map and i <= len(dimensions):
                    dim_key = dimensions[i - 1]["key"]

        # If dimensions were missing from LLM response, create from questions
        if len(dimensions) < 3 and len(questions) >= 3:
            dimensions = []
            for i, q in enumerate(questions, start=1):
                key = f"dim{i}"
                label = q.text[:30].strip()
                dimensions.append({"key": key, "label": label, "short_label": label[:12]})

        if len(questions) >= 3:
            slug = hashlib.md5(topic.encode("utf-8")).hexdigest()[:8]
            assessment_id = f"dynamic_{slug}_{uuid4().hex[:6]}"
            title = data.get("title") or f"แบบประเมินทักษะ: {topic}"
            form = AssessmentFormData(assessment_id=assessment_id, title=title, questions=questions)
            DYNAMIC_ASSESSMENTS[assessment_id] = {
                "assessment_id": assessment_id,
                "title": title,
                "topic": topic,
                "dimensions": dimensions,
                "questions": [
                    {
                        "id": q.id,
                        "text": q.text,
                        "dimension_key": getattr(q, "dimension_key", f"dim{idx}"),
                        "options": [opt.model_dump() for opt in q.options],
                    }
                    for idx, q in enumerate(questions, start=1)
                ],
            }
            return form
    except Exception as exc:
        log.warning("failed to generate dynamic assessment via LLM (%s), using fallback", exc)

    return _fallback_dynamic_form(topic)


def _fallback_dynamic_form(topic: str) -> AssessmentFormData:
    slug = hashlib.md5(topic.encode("utf-8")).hexdigest()[:8]
    assessment_id = f"dynamic_{slug}_{uuid4().hex[:6]}"
    title = f"แบบประเมินทักษะ: {topic}"
    t_lower = topic.lower()

    if any(k in t_lower for k in ("อาหาร", "cooking", "ทำอาหาร", "ขนม", "เบเกอรี่")):
        aspect_dims = [
            ("dim1", "การเลือกและเตรียมวัตถุดิบ", "เตรียมวัตถุดิบ", "คุณมีทักษะในการคัดสรรวัตถุดิบสดใหม่และการเตรียมของ (Mise en Place) ระดับใด"),
            ("dim2", "เทคนิคความร้อนและการปรุง", "เทคนิคความร้อน", "ความเชี่ยวชาญในการควบคุมความร้อน การผัด ต้ม ทอด อบ และเทคนิคการปรุงของคุณ"),
            ("dim3", "การปรุงรสและบาลานซ์รสชาติ", "การปรุงรส", "ความสามารถในการชิม ปรับแต่ง และสร้างสมดุลของรสชาติอาหาร (เปรี้ยว หวาน เค็ม เผ็ด อูมามิ)"),
            ("dim4", "การจัดจานและความคิดสร้างสรรค์", "การจัดจาน", "ทักษะการนำเสนอ จัดแต่งจานอาหาร (Plating) และการสร้างสรรค์เมนูใหม่ๆ"),
            ("dim5", "สุขอนามัยและความปลอดภัยในครัว", "สุขอนามัย", "การรักษาความสะอาด สุขอนามัยอาหาร (Food Safety) และความปลอดภัยในการใช้อุปกรณ์"),
            ("dim6", "การบริหารครัวและเวลา", "บริหารเวลา", "ความสามารถในการจัดการเวลา ลำดับขั้นตอนการทำอาหาร และการดูแลจัดการครัวอย่างมีประสิทธิภาพ"),
        ]
    elif any(k in t_lower for k in ("python", "code", "เขียนโค้ด", "programming", "javascript", "golang", "java", "react")):
        aspect_dims = [
            ("dim1", f"ไวยากรณ์และโครงสร้างพื้นฐาน {topic}", "พื้นฐานภาษา", f"ความเข้าใจในไวยากรณ์ (Syntax) และโครงสร้างข้อมูลพื้นฐานของ {topic}"),
            ("dim2", "การออกแบบตรรกะและอัลกอริทึม", "ตรรกะและอัลกอริทึม", f"ความสามารถในการแปลงโจทย์ปัญหาเป็น Logic และเลือกใช้อัลกอริทึมที่เหมาะสมใน {topic}"),
            ("dim3", "การจัดการโมดูลและไลบรารี", "โมดูลและไลบรารี", f"ความคุ้นเคยกับการเลือกใช้ Ecosystem, Library, และ Framework สำคัญใน {topic}"),
            ("dim4", "การตรวจแก้และทดสอบโค้ด", "การ Debug และ Test", f"ทักษะการตรวจสอบบั๊ก (Debugging), Profiling และการเขียน Unit Test ใน {topic}"),
            ("dim5", "โครงสร้างโค้ดและความปลอดภัย", "Clean Code และ Sec", f"การเขียนโค้ดที่อ่านง่าย ยึด Clean Code, Design Patterns และความปลอดภัยของระบบ"),
            ("dim6", "การเชื่อมต่อและประยุกต์ใช้งานจริง", "การประยุกต์ใช้งาน", f"ประสบการณ์ในการนำ {topic} ไปทำโปรเจกต์จริง, เชื่อมต่อ API หรือ Deploy ขึ้น Production"),
        ]
    else:
        aspect_dims = [
            ("dim1", f"ความรู้พื้นฐานและหลักการสำคัญของ {topic}", "ความรู้พื้นฐาน", f"ระดับความเข้าใจในหลักการและทฤษฎีพื้นฐานของ {topic}"),
            ("dim2", f"ทักษะการลงมือปฏิบัติจริงใน {topic}", "การลงมือทำ", f"ประสบการณ์และความคล่องแคล่วในการลงมือทำจริงในงาน {topic}"),
            ("dim3", f"การแก้ไขปัญหาและข้อผิดพลาดใน {topic}", "การแก้ปัญหา", f"ความสามารถในการวิเคราะห์และแก้ไขปัญหาเฉพาะหน้าที่เกิดขึ้นใน {topic}"),
            ("dim4", f"การเลือกใช้เครื่องมือและเทคนิคใน {topic}", "เครื่องมือเทคนิค", f"การเลือกใช้เครื่องมือหรือเทคนิคเฉพาะทางที่ถูกต้องเหมาะสมสำหรับ {topic}"),
            ("dim5", f"ความคิดสร้างสรรค์และการประยุกต์ใช้", "การประยุกต์ใช้", f"การนำทักษะ {topic} ไปประยุกต์ใช้ในสถานการณ์ใหม่ๆ หรือสร้างสรรค์สิ่งใหม่"),
            ("dim6", f"การบริหารจัดการและมาตรฐานงาน {topic}", "มาตรฐานงาน", f"ความใส่ใจในคุณภาพ มาตรฐานความปลอดภัย และการจัดการเวลาในงาน {topic}"),
        ]

    dimensions = [{"key": k, "label": l, "short_label": s} for k, l, s, _ in aspect_dims]
    options = [
        AssessmentOption(value=0, label="ไม่มีพื้นฐาน / ไม่เคยทำ"),
        AssessmentOption(value=1, label="มีความรู้เริ่มต้น ทำตามคำแนะนำได้"),
        AssessmentOption(value=2, label="ทำได้ด้วยตนเองตามมาตรฐาน"),
        AssessmentOption(value=3, label="คล่องแคล่ว แก้ปัญหาเฉพาะหน้าได้ดี"),
        AssessmentOption(value=4, label="เชี่ยวชาญระดับสูง และถ่ายทอดเทคนิคได้"),
    ]
    questions = [
        AssessmentQuestion(id=f"q{i}", text=text, options=options)
        for i, (_, _, _, text) in enumerate(aspect_dims, start=1)
    ]
    form = AssessmentFormData(assessment_id=assessment_id, title=title, questions=questions)
    DYNAMIC_ASSESSMENTS[assessment_id] = {
        "assessment_id": assessment_id,
        "title": title,
        "topic": topic,
        "dimensions": dimensions,
        "questions": [
            {
                "id": f"q{i}",
                "text": text,
                "dimension_key": k,
                "options": [opt.model_dump() for opt in options],
            }
            for i, (k, _, _, text) in enumerate(aspect_dims, start=1)
        ],
    }
    return form


def score_dynamic_assessment(
    definition: dict,
    answers: list[AssessmentAnswer],
) -> tuple[int, SkillScores, list[str], list[SkillDimension], list[str]]:
    """Compute 0-100 score and dimension breakdown for dynamic assessment."""
    q_map = {q["id"]: q for q in definition.get("questions", [])}
    raw_dims = definition.get("dimensions", [])

    # Map questions to dimensions
    dim_answers: dict[str, list[int]] = {d["key"]: [] for d in raw_dims}
    for ans in answers:
        q_info = q_map.get(ans.question_id)
        dim_key = q_info.get("dimension_key") if q_info else None
        if not dim_key:
            dim_key = ans.question_id.replace("q", "dim")
        if dim_key in dim_answers:
            dim_answers[dim_key].append(ans.value)
        else:
            dim_answers.setdefault(dim_key, []).append(ans.value)

    # Compute score per dimension
    dimensions_list: list[SkillDimension] = []
    for d in raw_dims:
        vals = dim_answers.get(d["key"], [])
        if vals:
            score = round((sum(vals) / (len(vals) * 4)) * 100)
        else:
            score = 0
        dimensions_list.append(
            SkillDimension(
                key=d["key"],
                label=d["label"],
                short_label=d.get("short_label") or d["label"][:12],
                score=score,
            )
        )

    if not dimensions_list:
        total_val = sum(a.value for a in answers)
        pct = round((total_val / (max(len(answers), 1) * 4)) * 100)
        dimensions_list = [
            SkillDimension(key=f"dim{i}", label=f"ด้านที่ {i}", short_label=f"ด้านที่ {i}", score=pct)
            for i in range(1, 6)
        ]

    # Overall score is average of dimensions
    pct = round(sum(d.score for d in dimensions_list) / len(dimensions_list))

    # Sort descending by score for top skills
    sorted_dims = sorted(dimensions_list, key=lambda d: -d.score)
    custom_top_skills = [d.label for d in sorted_dims[:2]]

    # Also build a compliant SkillScores for legacy compatibility
    topic = definition.get("topic", "").lower()
    scores_dict = {
        "frontend": pct if any(k in topic for k in ("front", "web", "ui", "ux")) else 0,
        "backend": pct if any(k in topic for k in ("back", "api", "server", "sql")) else 0,
        "network": pct if any(k in topic for k in ("net", "network", "เครือข่าย")) else 0,
        "embedded": pct if any(k in topic for k in ("embed", "iot", "arduino", "hardware")) else 0,
        "ai_data": pct if any(k in topic for k in ("ai", "data", "ml", "model")) else 0,
        "cybersecurity": pct if any(k in topic for k in ("sec", "security", "ความปลอดภัย")) else 0,
    }
    if all(v == 0 for v in scores_dict.values()):
        scores_dict = {k: pct for k in scores_dict}

    scores = SkillScores(**scores_dict)
    values = scores.model_dump()
    top = sorted(values, key=lambda k: -values[k])[:2]
    return pct, scores, top, dimensions_list, custom_top_skills


def format_user_skills_context(skills: list[SkillProfile] | SkillProfile | None) -> str:
    """Format stored skill profiles into a succinct context for the LLM."""
    if not skills:
        return "ผู้ใช้ยังไม่มีข้อมูลประวัติการประเมินทักษะในระบบ"

    items: list[SkillProfile] = skills if isinstance(skills, list) else [skills]
    lines: list[str] = []

    for prof in items:
        if prof.topic:
            score_text = f"{prof.score}/100" if prof.score is not None else ""
            dim_str = ""
            if prof.dimensions:
                dim_str = " (คะแนนรายด้าน: " + ", ".join(f"{d.label}: {d.score}" for d in prof.dimensions) + ")"
            lines.append(f"- ทักษะด้าน {prof.topic}: {score_text}{dim_str}".strip())
        else:
            scores_dump = prof.scores.model_dump()
            top = ", ".join(prof.top_skills)
            scores_str = ", ".join(f"{k}: {v}" for k, v in scores_dump.items())
            lines.append(f"- ทักษะวิศวกรรมคอมพิวเตอร์ (CPE): {scores_str} (ด้านเด่น: {top})")

    return "\n".join(lines)

