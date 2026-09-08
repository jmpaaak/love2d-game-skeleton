# LANE SCOPE — main

This worktree is the autonomous loop for this LÖVE project.
Process `docs/feedback/INBOX.md` pending items from the top. Commit and push to
`main` after tests pass.

---

# Autonomous development brief

**중요 — 상시 구조화/모듈화/캡슐화, INBOX 기능보다 먼저 (2026-09-08):** 원본 `docs/MODULE_STRUCTURE.md`.
- 매 사이클 기능보다 **모듈 분리 리팩토링이 최우선**. 손대려는 파일이 800줄/80KB를 넘으면 그 사이클은 분리만. GREEN 전에 그 파일에 새 기능 금지.
- `play.lua` / `self_test.lua` / `main.lua`를 더 키우지 마라. 슬라이스 = 모듈 1개. 순수 규칙과 씬 드로우를 섞지 마라.
- INBOX 최상단이 기능이어도 거대 파일에 붙어야 하면 **먼저 쪼갠다**. 이미 독립 모듈 경로가 있는 항목만 기능 진행.
- 처리 대기를 **파일/모듈이 안 겹치는 단위로 최대로** 워크트리 병렬화한다. 겹치면 분리 후 병렬.
- JSON/`tools/`/순수 `game/*.lua`처럼 이미 독립인 항목은 모듈화를 기다리지 말고 즉시 WT.
- INBOX 항목에는 담당 모듈 경로를 적는다. 안 적으면 전부 `play.lua`에 붙어 1레인이 된다.

**중요 — 재감사 방지 규칙:** 이미 완료된 INBOX 항목을 STATUS만 다시 쓰지 마라. 할 일이 없으면 IDLE.
**중요 — FAIL + 미커밋:** preflight FAIL이면 실패 수정+커밋만. 새 INBOX 금지.
**중요 — 한 사이클 한 조각:** 검증 가능한 최소 단위 하나만 커밋.

## Required workflow

1. Read only the pending item for this cycle (TOKEN RULE: no full INBOX read).
2. `git status --short` first. Finish prior-cycle dirty work.
3. If a target file is ≥800 lines / 80KB, split it this cycle. Do not add features to it.
4. TDD. `make verify LOVE=/Users/jm/.local/bin/love` before commit.
5. STATUS.md this cycle only. Push when clean. Empty 처리 대기 = IDLE.
