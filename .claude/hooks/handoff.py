"""Writes and loads handoff files so a session can resume after compaction.

Usage (called by Claude Code hooks, JSON payload on stdin):
  handoff.py save   PreCompact: fills the handoff template and writes it
  handoff.py load   SessionStart: prints the latest handoff file to the context

The template is .claude/templates/handoff.md. Handoffs live in data/handoffs/
(local, not committed). Only the newest one is loaded. Errors never block
compaction or session start.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "handoff.md"
RECENT_REQUESTS = 5
TEXT_LIMIT = 300
ASSISTANT_LIMIT = 1200
CORRECTION = re.compile(
    r"\b(no|not|don't|dont|wrong|instead|stop|never|shouldn't|actually|revert|undo)\b",
    re.IGNORECASE,
)


def project_root() -> Path:
    return Path(
        os.environ.get("CLAUDE_PROJECT_DIR", Path(__file__).resolve().parents[2])
    )


def handoff_dir(root: Path) -> Path:
    return root / "data" / "handoffs"


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else "(unavailable)"


def message_text(message: dict) -> str:
    content = message.get("content", "")
    if isinstance(content, str):
        return content.strip()
    parts = [
        item.get("text", "")
        for item in content
        if isinstance(item, dict) and item.get("type") == "text"
    ]
    return "\n".join(part for part in parts if part).strip()


def read_transcript(path: str) -> tuple[list[str], str]:
    """Return (all user texts, last assistant text) from a transcript file."""
    user_texts: list[str] = []
    last_assistant = ""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return [], ""
    for line in lines:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        message = entry.get("message") or {}
        role = message.get("role") or entry.get("type")
        text = message_text(message)
        if not text:
            continue
        if role == "user":
            user_texts.append(text)
        elif role == "assistant":
            last_assistant = text
    return user_texts, last_assistant


def truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit].rstrip() + " ..."


def one_line(text: str) -> str:
    return truncate(" ".join(text.split()), TEXT_LIMIT)


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) or "- (none)"


def render(payload: dict, root: Path) -> str:
    user_texts, last_assistant = read_transcript(payload.get("transcript_path", ""))
    corrections = [one_line(text) for text in user_texts if CORRECTION.search(text)]
    values = {
        "branch": git(root, "rev-parse", "--abbrev-ref", "HEAD"),
        "session": str(payload.get("session_id", "unknown")),
        "trigger": str(payload.get("trigger", "pre-compaction")),
        "created": datetime.now().isoformat(timespec="seconds"),
        "original_request": one_line(user_texts[0]) if user_texts else "(none)",
        "corrections": bullets(corrections[-RECENT_REQUESTS:]),
        "recent_requests": bullets(
            [one_line(t) for t in user_texts[-RECENT_REQUESTS:]]
        ),
        "last_assistant": truncate(last_assistant, ASSISTANT_LIMIT) or "(none)",
        "working_tree": git(root, "status", "--short") or "(clean)",
        "commits": git(root, "log", "--oneline", "-5"),
    }
    text = TEMPLATE.read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def save(payload: dict, root: Path) -> None:
    directory = handoff_dir(root)
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    session = str(payload.get("session_id", "nosession"))[:8]
    (directory / f"{stamp}-{session}.md").write_text(
        render(payload, root), encoding="utf-8"
    )


def load(root: Path) -> None:
    directory = handoff_dir(root)
    if not directory.is_dir():
        return
    files = sorted(directory.glob("*.md"))
    if not files:
        return
    latest = files[-1]
    print(
        f"Latest handoff from a previous context ({latest}). "
        "Read it to see what we were working on:\n"
    )
    print(latest.read_text(encoding="utf-8"))


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    root = project_root()
    try:
        if mode == "save":
            save(json.load(sys.stdin), root)
        elif mode == "load":
            load(root)
    except (OSError, ValueError) as error:  # never block compaction or startup
        print(f"handoff.py {mode} failed: {error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
