# Autonomous loop token optimization (built in)

Any game generated from this skeleton that runs a fresh-context autonomous
dev loop (a `loop/loop.sh` + `loop/run_agent.py` cron/launchd pair spawning
a coding agent every N minutes) should apply these three rules from day
one, before `docs/STATUS.md` and `loop/PROMPT.md` grow large enough to
matter:

1. **Compact `docs/STATUS.md`.** Wire `scripts/compact_status.py` into
   whatever already runs frequently and read-only for this project (e.g. a
   progress-report cron job). It keeps a bounded recent slice in
   `docs/STATUS.md` and archives the rest into `docs/STATUS_HISTORY.md`,
   which the loop is told not to read by default. Only compact when the
   loop's own agent process is not currently running.

2. **Don't restate policy in `loop/PROMPT.md`.** Point at
   `docs/feedback/INBOX.md` / `docs/GAME_DESIGN.md` for the full text
   instead of duplicating multi-paragraph rules in the fixed prompt file
   sent every cycle. `loop/PROMPT.md`'s "Required workflow" step 1 should
   read: "Read only the pending feedback, game design, and current status
   needed for this cycle. Do not read `docs/STATUS.md` in full — latest
   `##` section plus next slice only. Do not read `docs/STATUS_HISTORY.md`
   unless tracking a specific past bug."

3. **Compact pending-feedback dumps in `loop/preflight.py`.** Import
   `pending_feedback` / `compact_pending_feedback` from
   `loop/pending_feedback.py` (shipped with this skeleton) instead of
   printing the full text of every pending `docs/feedback/INBOX.md` item
   into the cycle's first prompt. It prints short titles only, capped at 4
   items, and tells the agent to read the source section for full text.

4. **Move finished/blocked items out of `## 처리 대기` immediately
   (2026-09-03).** `loop/PROMPT.md`'s workflow steps must include an
   explicit rule: whenever a cycle judges a pending INBOX item fully done
   (or fully human-gated — nothing left that code/assets/tests can do
   until the user acts), move it out of `## 처리 대기` into
   `## 처리 완료` in the same commit, with the completion evidence (or a
   "human-gated: still waiting on <specific action>" note). Leaving a
   finished item in the pending section just means every future cycle (and
   any periodic progress-report cron reading the pending section) re-reads
   and re-restates the same "still blocked" text — pure wasted tokens. See
   `spaceship`/`man-of-korea`'s `loop/PROMPT.md` for the exact wording to
   copy into new projects' `## ③ 규칙과 근거` / "Required workflow" section.

See the Hermes skill `autonomous-loop-token-optimization` (any Hermes
profile) for the full writeup, verification steps, and rationale.
