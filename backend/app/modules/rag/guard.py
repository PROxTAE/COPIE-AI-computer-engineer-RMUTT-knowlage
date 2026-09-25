"""Detect profanity in a user query so it is never searched or echoed back.

Thai has no spaces between words, so matching is done on a normalized string
(spaces, punctuation and repeated letters removed). Harmless words that contain
a profane substring (e.g. "สัดส่วน", "ห่าง") are removed before matching.
"""
import re

PROFANE_TERMS = (
    "เหี้ย", "เหี่ย", "สัส", "สัด", "ควย", "เย็ด", "หี", "แม่ง", "ห่า",
    "ชิบหาย", "ฉิบหาย", "ระยำ", "จัญไร", "ดอกทอง", "อีดอก", "ไอ้สัตว์", "อีสัตว์",
    "เชี่ย", "เชี้ย", "พ่อมึงตาย", "แม่มึงตาย", "กะหรี่", "ส้นตีน",
    "fuck", "shit", "bitch", "asshole", "dick", "pussy", "motherfucker",
)
# Ordinary words that contain a term above as a substring.
HARMLESS_WORDS = (
    "สัดส่วน", "หีบ", "ห่าง", "ห่าน", "ห่าม", "เหี่ยว", "เชี่ยว", "แม่งาน",
    "ดอกทองกวาว", "shitake", "dickens",
)

_STRIP_RE = re.compile(r"[^\w฀-๿]+")
_REPEAT_RE = re.compile(r"(.)\1+")


def _normalize(text: str) -> str:
    compact = _STRIP_RE.sub("", text.lower())
    for word in HARMLESS_WORDS:
        compact = compact.replace(word, "")
    return compact


def contains_profanity(text: str) -> bool:
    """True if `text` contains a profane term, also when letters are spaced out or repeated."""
    compact = _normalize(text)
    squeezed = _REPEAT_RE.sub(r"\1", compact)
    return any(term in compact or term in squeezed for term in PROFANE_TERMS)
