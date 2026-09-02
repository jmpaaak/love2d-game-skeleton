#!/usr/bin/env python3
"""Compact a growing docs/STATUS.md so coding-loop agents stop ingesting
hundreds of kilobytes of completed-cycle history on every turn.

Newest-first logs keep a short head. Oldest-first logs keep the title plus
the newest tail. Overflow is prepended to docs/STATUS_HISTORY.md. No git
commit — the caller/next coding cycle owns that. Skip if the file is
already small or was written in the last 45s (a live agent may be
mid-edit).

Every game generated from this skeleton starts with this script already
wired in. Call it from whatever runs frequently and read-only for the
project (e.g. a periodic progress-report cron job) so docs/STATUS.md never
grows unbounded and re-inflates every autonomous cycle's input tokens.

Usage:
    python3 scripts/compact_status.py docs/STATUS.md [--keep-chars N]

Library:
    from compact_status import compact_status
    compact_status(Path("docs/STATUS.md"))
"""

from __future__ import annotations

import argparse
from pathlib import Path
import time

KEEP_CHARS = 16_000
RECENT_WRITE_SECONDS = 45
HISTORY_NAME = "STATUS_HISTORY.md"


def _paragraph_break(text: str, limit: int, from_start: bool) -> int:
    if from_start:
        cut = text.rfind("\n\n", 0, limit)
        return cut + 2 if cut >= 80 else limit
    start = max(0, len(text) - limit)
    cut = text.find("\n\n", start)
    return cut + 2 if cut != -1 else start


def compact_status(status_path: Path, keep_chars: int = KEEP_CHARS) -> dict[str, object]:
    if not status_path.is_file():
        return {"action": "missing", "path": str(status_path)}

    age = time.time() - status_path.stat().st_mtime
    if age < RECENT_WRITE_SECONDS:
        return {"action": "skipped-recent-write", "age_s": round(age, 1), "bytes": status_path.stat().st_size}

    text = status_path.read_text(encoding="utf-8")
    original = len(text.encode("utf-8"))
    if original <= keep_chars:
        return {"action": "noop", "bytes": original}

    newest_first = "- 2026-" in text[:4000] or "- 2025-" in text[:4000]
    if newest_first:
        keep_at = _paragraph_break(text, keep_chars, from_start=True)
        kept = text[:keep_at].rstrip() + "\n"
        archived = text[keep_at:].lstrip()
    else:
        title_end = text.find("\n", 0)
        title = text[: title_end + 1] if title_end != -1 else "# STATUS\n"
        body = text[len(title) :]
        keep_at = _paragraph_break(body, keep_chars, from_start=False)
        archived = body[:keep_at].rstrip() + "\n"
        kept = title + body[keep_at:].lstrip()

    if not archived.strip():
        return {"action": "noop", "bytes": original}

    pointer = (
        "\n> Older cycle history lives in `docs/STATUS_HISTORY.md`. "
        "Only search it when tracking a specific past bug; do not read it by default.\n"
    )
    if pointer.strip() not in kept:
        kept = kept.rstrip() + "\n" + pointer

    history_path = status_path.with_name(HISTORY_NAME)
    stamp = time.strftime("%Y-%m-%d %H:%M")
    block = f"\n\n## Archived from STATUS.md ({stamp})\n\n{archived.rstrip()}\n"
    if history_path.is_file():
        previous = history_path.read_text(encoding="utf-8")
    else:
        previous = "# STATUS history\n\nAutomatically archived. The dev loop does not read this by default.\n"
    history_path.write_text(previous.rstrip() + block, encoding="utf-8")
    status_path.write_text(kept if kept.endswith("\n") else kept + "\n", encoding="utf-8")
    new_bytes = status_path.stat().st_size
    return {
        "action": "compacted",
        "bytes_before": original,
        "bytes_after": new_bytes,
        "archived_chars": len(archived),
        "history": str(history_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("status", type=Path)
    parser.add_argument("--keep-chars", type=int, default=KEEP_CHARS)
    args = parser.parse_args()
    result = compact_status(args.status, keep_chars=args.keep_chars)
    print(result)
    return 0 if result["action"] != "missing" else 1


if __name__ == "__main__":
    raise SystemExit(main())
