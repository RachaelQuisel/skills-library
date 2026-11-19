#!/usr/bin/env python3
"""Extract today's user messages from Claude Code session transcripts.

"Today" is a calendar date in America/Los_Angeles unless GEM_MINER_TIMEZONE
overrides it. Transcript timestamps are UTC (or offset-aware). Comparing those
strings to a local date drops anything said after 5pm PT (4pm PT in winter),
because that instant is already the next UTC date.
"""

import ast, glob, json, os, sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_TIMEZONE = "America/Los_Angeles"
TIMEZONE_ENV = "GEM_MINER_TIMEZONE"


def get_timezone():
    """Return the zone used for 'today' and for date arguments."""
    name = os.environ.get(TIMEZONE_ENV, "").strip() or DEFAULT_TIMEZONE
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as exc:
        sys.exit(f"error: {TIMEZONE_ENV}={name!r} is not a valid timezone ({exc})")


def resolve_date(date_str, tz, now=None):
    """Calendar date in `tz`. An explicit YYYY-MM-DD is used as-is."""
    if date_str:
        return date_str
    clock = now if now is not None else datetime.now(tz)
    if clock.tzinfo is None:
        clock = clock.replace(tzinfo=timezone.utc)
    return clock.astimezone(tz).date().isoformat()


def message_local_date(ts, tz):
    """Local calendar date for a transcript timestamp, or None if it cannot be parsed.

    Naive timestamps are treated as UTC. Claude Code writes UTC instants.
    """
    if not ts or not isinstance(ts, str):
        return None
    text = ts.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz).date().isoformat()


def session_files(projects_dir=None):
    """Every non-agent session jsonl under ~/.claude/projects/<folder>/.

    Sessions started in a project directory live in their own folder next to
    the home-directory folder. Reading only the home folder drops them.
    """
    root = projects_dir or os.path.expanduser("~/.claude/projects")
    files = sorted(glob.glob(os.path.join(root, "*", "*.jsonl")))
    return [f for f in files if "agent-" not in os.path.basename(f)]


def extract_messages(date_str=None, projects_dir=None, now=None, tz=None):
    """Extract user messages for a local date (default: today). Returns dicts with text and timestamp."""
    tz = tz or get_timezone()
    date_str = resolve_date(date_str, tz, now=now)

    messages = []
    for fpath in session_files(projects_dir):
        try:
            with open(fpath, "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get("type") != "user":
                            continue
                        ts = entry.get("timestamp", "")
                        if message_local_date(ts, tz) != date_str:
                            continue

                        msg = entry.get("message", "")
                        if isinstance(msg, str):
                            try:
                                msg = ast.literal_eval(msg)
                            except Exception:
                                continue
                        if not isinstance(msg, dict):
                            continue

                        content = msg.get("content", "")
                        text = ""
                        if isinstance(content, str):
                            text = content
                        elif isinstance(content, list):
                            for block in content:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    text += block.get("text", "") + "\n"
                                elif isinstance(block, str):
                                    text += block + "\n"

                        text = text.strip()
                        if len(text) < 5 or len(text) > 2000:
                            continue
                        if text.startswith("{") or text.startswith("[") or text.startswith("mutation") or text.startswith("```"):
                            continue

                        messages.append({"text": text, "timestamp": ts})
                    except Exception:
                        pass
        except Exception:
            pass

    return messages


if __name__ == "__main__":
    tz = get_timezone()
    date = resolve_date(sys.argv[1] if len(sys.argv) > 1 else None, tz)
    msgs = extract_messages(date, tz=tz)
    json.dump(msgs, sys.stdout, indent=2)
    print(f"\n# Extracted {len(msgs)} messages for {date} ({getattr(tz, 'key', tz)})", file=sys.stderr)
