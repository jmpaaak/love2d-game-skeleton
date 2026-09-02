#!/usr/bin/env python3
"""Reusable pending-feedback parsing/compaction for a preflight gate script.

Every game generated from this skeleton is expected to set up an
autonomous dev loop (cron/launchd spawning a fresh-context coding agent
every N minutes) that reads `docs/feedback/INBOX.md`. That file must
contain exactly one `## 처리 대기` (pending) section and one `## 처리 완료`
(done) section, each pending item as a top-level `- ` bullet.

Import this from the project's own `loop/preflight.py` instead of dumping
the full text of every pending item into each cycle's first prompt — that
duplicates content the agent will read from INBOX.md anyway and inflates
input tokens on every single cycle.

    from pending_feedback import pending_feedback, compact_pending_feedback

    pending = pending_feedback(root)
    if pending:
        print("PENDING_FEEDBACK:")
        print("\n".join(compact_pending_feedback(pending)))
"""

from __future__ import annotations

from pathlib import Path

MAX_PENDING_PROMPT_ITEMS = 4
MAX_PENDING_PROMPT_CHARS = 220


def pending_feedback(root: Path, inbox_relpath: str = "docs/feedback/INBOX.md") -> list[str]:
    path = root / inbox_relpath
    text = path.read_text(encoding="utf-8")
    before, marker, after = text.partition("## 처리 대기")
    if not marker or "## 처리 완료" not in after:
        raise RuntimeError(f"{inbox_relpath} must contain one pending and one completed section")
    section = after.split("## 처리 완료", 1)[0]
    return [line for line in section.splitlines() if line.strip().startswith("-")]


def compact_pending_feedback(pending: list[str], inbox_relpath: str = "docs/feedback/INBOX.md") -> list[str]:
    """Keep only short titles in the cycle prompt; the agent reads the inbox file."""
    titles: list[str] = []
    for line in pending:
        stripped = line.strip()
        if not stripped.startswith("-"):
            continue
        cut = stripped
        for marker in (":**", ":"):
            index = stripped.find(marker)
            if 0 < index <= MAX_PENDING_PROMPT_CHARS:
                cut = stripped[: index + (1 if marker == ":" else 3)]
                break
        else:
            cut = stripped[:MAX_PENDING_PROMPT_CHARS].rstrip()
        titles.append(cut)
    if not titles:
        return pending
    header = [
        f"PENDING_FEEDBACK titles only. Read {inbox_relpath} 처리 대기 for the full text of the one item this cycle will finish.",
    ]
    shown = titles[:MAX_PENDING_PROMPT_ITEMS]
    omitted = len(titles) - len(shown)
    if omitted:
        shown.append(f"- ({omitted} more pending items omitted from this cycle prompt)")
    return header + shown
