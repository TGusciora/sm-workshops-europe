"""PreToolUse guard: blocks reads of .env files and dangerous operations.

Claude Code sends the tool call as JSON on stdin. Exit code 2 blocks the call,
and the message on stderr is shown to Claude. Standard library only.
"""

import json
import re
import sys
from pathlib import PurePosixPath

FILE_TOOLS = {"Read", "Edit", "Write", "MultiEdit", "NotebookEdit", "Grep", "Glob"}
PATH_KEYS = ("file_path", "path", "notebook_path", "glob", "pattern")

# Matches .env, .env.local, .env.production and similar, but not .envrc or my.env.
ENV_FILE = re.compile(r"(?<![\w.-])\.env(?:\.[\w-]+)*(?![\w-])")
ENV_TEMPLATE = re.compile(r"\.env\.(?:example|sample|template)$")

# Commands that remove files recursively, for example rm -rf or rm --recursive.
RECURSIVE_RM = re.compile(
    r"(?<![\w/.-])(?:sudo\s+)?rm\s+(?:[^;&|]*\s)?(?:-[a-zA-Z]*[rR][a-zA-Z]*|--recursive)\b"
)

DANGEROUS_COMMANDS = [
    (
        re.compile(r"\bgit\s+push\b[^;&|]*\s(?:--force(?!-with-lease)\b|-f\b)"),
        "git push --force rewrites remote history; use --force-with-lease or ask the user",
    ),
    (
        re.compile(r"\bgit\s+reset\s+--hard\b"),
        "git reset --hard discards uncommitted work",
    ),
    (
        re.compile(r"\bgit\s+clean\b[^;&|]*\s-\w*f"),
        "git clean -f deletes untracked files",
    ),
    (
        re.compile(r"\bgit\s+(?:checkout\s+--|restore)\s+\.(?=\s|$)"),
        "discarding all working-tree changes",
    ),
    (re.compile(r"\bsudo\b"), "sudo is not allowed"),
    (re.compile(r"\b(?:mkfs|shred|srm)\b"), "destructive disk or file wiping command"),
    (re.compile(r"\bdd\b[^;&|]*\bof=/dev/"), "dd writing to a device"),
    (
        re.compile(r">\s*/dev/(?:sd|disk|hd|nvme)"),
        "redirecting output to a disk device",
    ),
    (
        re.compile(r"\bdiskutil\s+(?:erase|partition|secureErase)"),
        "diskutil erase or partition command",
    ),
    (
        re.compile(r"\bchmod\s+(?:-\w*R\w*\s+)?0?777\b|\bchmod\s+-R\b"),
        "broad or recursive chmod",
    ),
    (re.compile(r"\bchown\s+-R\b"), "recursive chown"),
    (
        re.compile(r"\b(?:curl|wget)\b[^|;&]*\|\s*(?:sudo\s+)?(?:ba|z)?sh\b"),
        "piping a download straight into a shell",
    ),
    (re.compile(r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:"), "fork bomb"),
    (
        re.compile(r"(?:^|[;&|]\s*)(?:shutdown|reboot|halt)\b"),
        "system shutdown or reboot",
    ),
    (re.compile(r"\bfind\b[^;&|]*\s-delete\b"), "find -delete removes files"),
    (re.compile(r"\bkill\s+-9\s+-1\b|\bkillall\b"), "mass process termination"),
    (
        re.compile(r"\bdrop\s+(?:table|database|schema)\b", re.IGNORECASE),
        "SQL DROP statement",
    ),
    (
        re.compile(r"(?:^|[;&|(]\s*)printenv\b|(?:^|[;&|]\s*)env\s*(?:$|[;&|])"),
        "dumping the environment can expose secrets",
    ),
]


def find_env_files(text: str) -> list[str]:
    """Return .env file mentions in text, ignoring template files."""
    return [
        match.group(0)
        for match in ENV_FILE.finditer(text)
        if not ENV_TEMPLATE.search(match.group(0))
    ]


def check_file_tool(tool_input: dict) -> str | None:
    for key in PATH_KEYS:
        value = tool_input.get(key)
        if not isinstance(value, str):
            continue
        for match in find_env_files(PurePosixPath(value).name or value):
            return f".env files must not be read or changed by Claude ({match})"
    return None


def check_bash(command: str) -> str | None:
    if RECURSIVE_RM.search(command):
        return "recursive rm (rm -r / rm -rf) is blocked; ask the user to run it"
    for pattern, reason in DANGEROUS_COMMANDS:
        if pattern.search(command):
            return reason
    matches = find_env_files(command)
    if matches:
        return f".env files must not be read by shell commands ({matches[0]})"
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as error:
        print(f"guard.py: could not parse hook input: {error}", file=sys.stderr)
        return 2

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}

    reason = None
    if tool_name == "Bash":
        reason = check_bash(str(tool_input.get("command", "")))
    elif tool_name in FILE_TOOLS:
        reason = check_file_tool(tool_input)

    if reason:
        print(
            f"BLOCKED by .claude/hooks/guard.py: {reason}. "
            "If this is intended, ask the user to run it with the ! prefix.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
