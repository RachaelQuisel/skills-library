"""Parse execute-plan task emojis and the overall progress percentage.

A task is a checklist line that starts at column 0 with `-` or `*`, a checkbox,
and a status emoji. create-plan indents subtasks; those lines are not tasks.
execute flips the top-level line, and the progress share counts only those lines.
"""

from __future__ import annotations

import re

TASK_RE = re.compile(
    r"^[-*][ \t]+\[(?P<check>[ xX])\][ \t]*(?P<emoji>🟥|🟨|🟩)[ \t]+(?P<title>.+?)[ \t]*$",
    re.MULTILINE,
)
PROGRESS_RE = re.compile(r"(\*\*Overall Progress:\*\*\s*)(`?)(\d+)%(`?)")

EMOJI_STATUS = {"🟥": "todo", "🟨": "in_progress", "🟩": "done"}
STATUS_EMOJI = {status: emoji for emoji, status in EMOJI_STATUS.items()}


def clean_title(title: str) -> str:
    text = title.strip()
    if text.startswith("**") and text.endswith("**") and len(text) >= 4:
        text = text[2:-2].strip()
    return re.sub(r"\s+", " ", text)


def parse_tasks(text: str) -> list[dict]:
    tasks = []
    for match in TASK_RE.finditer(text):
        tasks.append(
            {
                "title": clean_title(match.group("title")),
                "status": EMOJI_STATUS[match.group("emoji")],
                "emoji": match.group("emoji"),
                "start": match.start(),
                "end": match.end(),
                "line": match.group(0),
            }
        )
    return tasks


def parse_progress(text: str) -> int | None:
    match = PROGRESS_RE.search(text)
    if not match:
        return None
    return int(match.group(3))


def done_share_percent(tasks: list[dict]) -> int | None:
    """Nearest integer percent of tasks marked done. Half rounds up."""
    total = len(tasks)
    if total == 0:
        return None
    done = sum(1 for task in tasks if task["status"] == "done")
    return (done * 100 + total // 2) // total


def set_task_status(text: str, title: str, status: str) -> str:
    tasks = [task for task in parse_tasks(text) if task["title"] == title]
    if len(tasks) != 1:
        raise ValueError(f"expected one task titled {title!r}, found {len(tasks)}")
    task = tasks[0]
    emoji = STATUS_EMOJI[status]
    if status == "done":
        new_line = re.sub(r"\[[ xX]\]", "[x]", task["line"], count=1)
    else:
        new_line = re.sub(r"\[[ xX]\]", "[ ]", task["line"], count=1)
    new_line = new_line.replace(task["emoji"], emoji, 1)
    return text[: task["start"]] + new_line + text[task["end"] :]


def set_progress(text: str, percent: int) -> str:
    match = PROGRESS_RE.search(text)
    if match is None:
        insert = f"\n**Overall Progress:** `{percent}%`\n"
        lines = text.splitlines(keepends=True)
        if lines and lines[0].startswith("#"):
            lines.insert(1, insert if insert.endswith("\n") else insert + "\n")
            return "".join(lines)
        return insert + text
    if match.group(2) or match.group(4):
        replacement = f"{match.group(1)}`{percent}%`"
    else:
        replacement = f"{match.group(1)}{percent}%"
    return text[: match.start()] + replacement + text[match.end() :]
