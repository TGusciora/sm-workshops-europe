"""Gives the reviewer agent the project vision and review rules when it starts.

Usage (called by Claude Code hooks, JSON payload on stdin):
  review.py   SubagentStart for the reviewer: prints the vision and review rules
              as additional context for the agent.

Files: docs/vision.md and .claude/review-rules.md. A missing file is skipped.
Errors never block the reviewer from starting.
"""

import contextlib
import json
import os
from pathlib import Path

RULE_FILES = ("docs/vision.md", ".claude/review-rules.md")


def project_root() -> Path:
    return Path(
        os.environ.get("CLAUDE_PROJECT_DIR", Path(__file__).resolve().parents[2])
    )


def context_text(root: Path) -> str:
    sections = []
    for name in RULE_FILES:
        try:
            body = (root / name).read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if body:
            sections.append(f"## {name}\n\n{body}")
    return "\n\n".join(sections)


def main() -> None:
    text = context_text(project_root())
    if not text:
        return
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SubagentStart",
                    "additionalContext": "Project vision and review rules:\n\n" + text,
                }
            }
        )
    )


if __name__ == "__main__":
    # A hook failure must not block the reviewer from starting.
    with contextlib.suppress(Exception):
        main()
