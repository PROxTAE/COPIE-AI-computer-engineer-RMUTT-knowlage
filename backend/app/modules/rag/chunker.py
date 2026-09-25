"""Parse knowledge Markdown files into section chunks.

Each file starts with a front-matter block (doc_id, title, source_url, updated)
and is split into one chunk per "## " heading. A section longer than MAX_CHARS
is cut into overlapping pieces so every chunk fits the embedding model well.
"""
from dataclasses import dataclass
from pathlib import Path

REQUIRED_KEYS = ("doc_id", "title", "source_url", "updated")
FRONT_MATTER_FENCE = "---"
MAX_CHARS = 800
OVERLAP_CHARS = 100


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    section: str | None
    url: str
    text: str


class KnowledgeFormatError(ValueError):
    """A knowledge file is missing its front-matter or a required key."""


# "utf-8-sig" also accepts files saved with a BOM (common with Windows editors).
ENCODING = "utf-8-sig"


def has_front_matter(path: Path) -> bool:
    with path.open(encoding=ENCODING) as f:
        return f.readline().strip() == FRONT_MATTER_FENCE


def parse_front_matter(raw: str, source: str) -> tuple[dict[str, str], str]:
    lines = raw.splitlines()
    if not lines or lines[0].strip() != FRONT_MATTER_FENCE:
        raise KnowledgeFormatError(f"{source}: file must start with '---' front-matter")
    try:
        end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == FRONT_MATTER_FENCE)
    except StopIteration:
        raise KnowledgeFormatError(f"{source}: front-matter is not closed with '---'") from None

    meta: dict[str, str] = {}
    for line in lines[1:end]:
        key, sep, value = line.partition(":")
        if sep:
            meta[key.strip()] = value.strip()
    missing = [key for key in REQUIRED_KEYS if not meta.get(key)]
    if missing:
        raise KnowledgeFormatError(f"{source}: front-matter missing {', '.join(missing)}")
    return meta, "\n".join(lines[end + 1 :])


def split_sections(body: str) -> list[tuple[str | None, str]]:
    """Split on "## " headings. Text before the first heading has section None."""
    sections: list[tuple[str | None, list[str]]] = [(None, [])]
    for line in body.splitlines():
        if line.startswith("## "):
            sections.append((line[3:].strip(), []))
        elif not line.startswith("# "):
            sections[-1][1].append(line)
    result = [(heading, "\n".join(lines).strip()) for heading, lines in sections]
    return [(heading, text) for heading, text in result if text]


def split_long_text(text: str, max_chars: int = MAX_CHARS, overlap: int = OVERLAP_CHARS) -> list[str]:
    """Cut text into pieces of at most max_chars that overlap by about `overlap` chars.

    Cuts prefer a line break, then a space, in the second half of the window,
    so list items and sentences are not split in the middle.
    """
    if len(text) <= max_chars:
        return [text]
    pieces: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            window_mid = start + max_chars // 2
            cut = max(text.rfind("\n", window_mid, end), text.rfind(" ", window_mid, end))
            end = cut if cut > start else end
        pieces.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return [piece for piece in pieces if piece]


def chunk_file(path: Path) -> list[Chunk]:
    meta, body = parse_front_matter(path.read_text(encoding=ENCODING), path.name)
    pieces = [
        (heading, piece)
        for heading, text in split_sections(body)
        for piece in split_long_text(text)
    ]
    return [
        Chunk(
            chunk_id=f"{meta['doc_id']}#{i}",
            doc_id=meta["doc_id"],
            title=meta["title"],
            section=heading,
            url=meta["source_url"],
            text=text,
        )
        for i, (heading, text) in enumerate(pieces)
    ]


def load_chunks(knowledge_dir: Path) -> list[Chunk]:
    """Chunk every Markdown file that has front-matter (README.md / SOURCES.md are skipped)."""
    chunks: list[Chunk] = []
    for path in sorted(knowledge_dir.glob("*.md")):
        if has_front_matter(path):
            chunks.extend(chunk_file(path))
    return chunks
