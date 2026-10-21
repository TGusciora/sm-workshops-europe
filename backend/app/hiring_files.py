"""Reads and writes job descriptions in hiring/<position>/<position>.md."""

import re
from pathlib import Path

SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
PROVENANCE_LINE = re.compile(
    r"^<!-- Accepted by the hiring manager from AI output \d+\. -->\n?", re.MULTILINE
)


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.strip().lower()).strip("-")
    return slug[:64].strip("-")


def is_valid_slug(slug: str) -> bool:
    return SLUG_PATTERN.fullmatch(slug) is not None


def job_description_path(hiring_dir: Path, slug: str) -> Path:
    if not is_valid_slug(slug):
        raise ValueError(f"invalid position slug: {slug!r}")
    return hiring_dir / slug / f"{slug}.md"


def read_job_description(hiring_dir: Path, slug: str) -> str | None:
    """The text without the provenance lines. They stay in the file, but sent back to
    Claude they would be copied into the next draft and point at the wrong output."""
    path = job_description_path(hiring_dir, slug)
    if not path.is_file():
        return None
    text = PROVENANCE_LINE.sub("", path.read_text(encoding="utf-8"))
    return text.rstrip() + "\n"


def write_job_description(
    hiring_dir: Path, slug: str, text: str, ai_output_id: int
) -> Path:
    """Write the accepted text and a last line that links it to the AI output record."""
    path = job_description_path(hiring_dir, slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = text.rstrip() + "\n"
    link = f"<!-- Accepted by the hiring manager from AI output {ai_output_id}. -->\n"
    path.write_text(body + "\n" + link, encoding="utf-8")
    return path
