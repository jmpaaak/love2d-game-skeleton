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


def compact_inbox_status_notes(root: Path, inbox_relpath: str = "docs/feedback/INBOX.md", max_note_chars: int = 300) -> None:
    """Collapse verbose '> 처리 상황 ...' note blocks in pending items to one line.

    Each '> 처리 상황' block can grow to thousands of words across many cycles.
    We keep only the first max_note_chars chars of the opening line, which carries
    the essential 'what was done / what's next' summary. Call this from preflight
    before running checks so every cycle starts with a compact INBOX.
    Writes only when the file actually shrinks (no-op when already compact).

    Usage in preflight.py:
        from pending_feedback import compact_inbox_status_notes
        compact_inbox_status_notes(root)
    """
    path = root / inbox_relpath
    original = path.read_text(encoding="utf-8")
    header, pend_marker, rest = original.partition("## 처리 대기")
    if not pend_marker:
        return
    pending_section, done_marker, done_section = rest.partition("## 처리 완료")

    lines = pending_section.splitlines(keepends=True)
    out: list[str] = []
    in_note = False
    note_first_line = ""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("> 처리 상황") or stripped.startswith(">  처리 상황"):
            in_note = True
            note_first_line = line.rstrip()[:max_note_chars]
            continue
        if in_note:
            if stripped.startswith(">") or stripped == "":
                continue
            else:
                out.append(note_first_line + " …(압축됨)\n")
                in_note = False
                out.append(line)
        else:
            out.append(line)
    if in_note:
        out.append(note_first_line + " …(압축됨)\n")

    new_text = header + pend_marker + "".join(out) + done_marker + done_section
    if len(new_text) >= len(original):
        return
    path.write_text(new_text, encoding="utf-8")
    print(f"[preflight] INBOX 처리 상황 주석 압축: -{len(original)-len(new_text):,} chars 절감", flush=True)

