"""Scope rule: COPIE answers only about Computer Engineering at RMUTT.

A question that names another department, faculty or university is outside the
department documents, even when it looks almost the same as an in-scope one
("ภาคไฟฟ้าเรียนอะไร" vs "ภาคคอมเรียนอะไร") — similarity scores cannot tell these apart.
"""
import re

_OTHER_DEPARTMENTS = (
    "ไฟฟ้า", "โยธา", "เครื่องกล", "อุตสาหการ", "อิเล็กทรอนิกส์", "โทรคมนาคม", "เคมี", "สิ่งทอ",
    "เกษตร", "วัสดุ", "โลหการ", "เมคคาทรอนิกส์", "เมคาทรอนิกส์", "ชีวการแพทย์", "สิ่งแวดล้อม",
    "ฟิสิกส์", "คณิตศาสตร์", "ชีววิทยา", "สถิติ", "การบัญชี", "การตลาด",
)
_OTHER_FACULTIES = (
    "บริหารธุรกิจ", "ครุศาสตร์", "วิทยาศาสตร์", "ศิลปศาสตร์", "สถาปัตยกรรม", "เทคโนโลยีการเกษตร",
    "การแพทย์บูรณาการ", "พยาบาล", "เทคโนโลยีสื่อสารมวลชน", "ศิลปกรรม", "คหกรรม", "แพทย",
    "นิติศาสตร์", "นิเทศ", "บัญชี", "เศรษฐศาสตร์", "อักษรศาสตร์", "รัฐศาสตร์", "วิศวกรรมศาสตร์และเทคโนโลยี",
)
_OTHER_UNIVERSITIES = (
    "จุฬา", "มหิดล", "ธรรมศาสตร์", "ลาดกระบัง", "สจล", "บางมด", "มจธ", "พระนครเหนือ", "มจพ",
    "ขอนแก่น", "ศรีนครินทร", "ศิลปากร", "บูรพา", "นเรศวร", "รามคำแหง", "แม่ฟ้าหลวง", "สุรนารี",
    "มหาวิทยาลัยเชียงใหม่", "มหาวิทยาลัยเกษตร", "ม.เกษตร", "มหาลัยเกษตร", "สงขลานครินทร์",
)
_RMUTT_CAMPUSES = ("ล้านนา", "กรุงเทพ", "พระนคร", "ตะวันออก", "อีสาน", "ศรีวิชัย", "สุวรรณภูมิ", "รัตนโกสินทร์")


def _alternatives(words: tuple[str, ...]) -> str:
    return "|".join(re.escape(w) for w in words)


_OTHER_UNIT = re.compile(
    # ภาค / ภาควิชา / สาขา / สาขาวิชา [+ วิศวกรรม] + another department
    rf"(ภาค|สาขา)(วิชา)?(วิศวกรรม)?({_alternatives(_OTHER_DEPARTMENTS)})"
    # วิศวกรรม + another engineering department, e.g. "วิศวกรรมไฟฟ้า", "วิศวะโยธา"
    rf"|วิศว(กรรม|ะ)({_alternatives(_OTHER_DEPARTMENTS[:14])})"
    rf"|คณะ({_alternatives(_OTHER_FACULTIES)})"
)
_OTHER_UNIVERSITY = re.compile(
    rf"{_alternatives(_OTHER_UNIVERSITIES)}|(ราชมงคล|มทร\.?)({_alternatives(_RMUTT_CAMPUSES)})"
)
# A comparison such as "ภาคคอมกับภาคไฟฟ้าต่างกันยังไง" still has a computer-engineering part to answer.
_OUR_DEPARTMENT = re.compile(r"คอม|computer|cpe")


def mentions_other_unit(query: str) -> bool:
    """True if the question is about another university, or about another department
    or faculty without also asking about computer engineering."""
    compact = re.sub(r"\s+", "", query.lower())
    if _OTHER_UNIVERSITY.search(compact):
        return True
    return bool(_OTHER_UNIT.search(compact)) and not _OUR_DEPARTMENT.search(compact)
