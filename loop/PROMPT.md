# LANE SCOPE — main

This worktree is the autonomous loop for this LÖVE project.
Process `docs/feedback/INBOX.md` pending items from the top. Commit and push to
`main` after tests pass.
Asset work must follow the binding `사진 기반 Asset Studio 고품질 픽셀 변환` workflow and all stricter project-specific overrides in `docs/ASSET_PIPELINE.md`; do not apply an asset that fails that contract.

---

# Autonomous development brief

**중요 — 상시 구조화/모듈화/캡슐화, INBOX 기능보다 먼저 (2026-09-08):** 원본 `docs/MODULE_STRUCTURE.md`.
- 리팩토링 사이클은 먼저 Hermes 스킬 `love2d-refactor-patterns`를 로드하고, 스캔 → 책임 하나 추출 → 기존 테스트 → 전체 참조 갱신 순서를 따른다.
- 매 사이클 기능보다 **모듈 분리 리팩토링이 최우선**. 손대려는 파일이 800줄/80KB를 넘으면 그 사이클은 분리만. GREEN 전에 그 파일에 새 기능 금지.
- `play.lua` / `self_test.lua` / `main.lua`를 더 키우지 마라. 슬라이스 = 모듈 1개. 순수 규칙과 씬 드로우를 섞지 마라.
- INBOX 최상단이 기능이어도 거대 파일에 붙어야 하면 **먼저 쪼갠다**. 이미 독립 모듈 경로가 있는 항목만 기능 진행.
- 처리 대기를 **파일/모듈이 안 겹치는 단위로 최대로** 워크트리 병렬화한다. 겹치면 분리 후 병렬. `loop/dispatch_inbox.py --apply`가 사이클 시작 시 독립 항목을 레인으로 띄운다.
- JSON/`tools/`/순수 `game/*.lua`처럼 이미 독립인 항목은 모듈화를 기다리지 말고 즉시 WT.
- INBOX 추가 시 담당 모듈 경로를 **백틱으로** 적는다. 예: (`game/play.lua`).
- **백틱이 없으면 직렬.** 백틱 없는 경로 언급은 병렬 대상이 아니다.

**중요 — 재감사 방지 규칙:** 이미 완료된 INBOX 항목을 STATUS만 다시 쓰지 마라. 할 일이 없으면 IDLE.
**중요 — FAIL + 미커밋:** preflight FAIL이면 실패 수정+커밋만. 새 INBOX 금지.
**중요 — 한 사이클 한 조각:** 검증 가능한 최소 단위 하나만 커밋.

## Required workflow

1. Read only the pending item for this cycle (TOKEN RULE: no full INBOX read).
2. `git status --short` first. Finish prior-cycle dirty work.
3. If a target file is ≥800 lines / 80KB, split it this cycle. Do not add features to it.
4. TDD. `make verify LOVE=/Users/jm/.local/bin/love` before commit.
5. STATUS.md this cycle only. Push when clean. Empty 처리 대기 = IDLE.

## 토큰 절약 규칙 (컨텍스트 관리)

- **테스트 출력**: `node --test` / `make verify` 등 긴 출력은 pass/fail 숫자 요약만 캡처. 전체 stdout을 컨텍스트에 두지 마라.
- **긴 로그**: 로그·덤프는 파일(`logs/` 또는 `scratch/`)에 저장하고, 필요한 구간만 `offset`+`limit`으로 읽어라.
- **독립 서브태스크**: 에셋 생성·린트·빌드·분석처럼 메인 흐름과 독립적인 작업은 서브에이전트로 위임해 중간 출력을 격리하라.
- **대형 소스 파일**: ≥80KB 파일은 절대 통째로 읽지 마라. `search_files`로 심볼을 찾고 주변 ≤80줄만 읽어라.
- **사이클 완료 후**: 큰 작업 묶음 하나가 끝나면 새 세션 시작을 권장 — 컨텍스트 압력 초기화.

## i18n 첫 화면 정책

- 정적 fallback 언어가 보였다가 번역으로 교체되는 i18n FOUC를 허용하지 않는다.
- 저장 언어/브라우저 언어 결정과 핵심 번역 적용은 카탈로그·세션 등 네트워크 요청보다 먼저 수행한다.
- 번역 준비 전 문서는 짧게 first-paint gate로 숨기고 완료 즉시 표시하되, `noscript`에서는 원문을 반드시 표시한다.
- 번역 적용 시 `html[lang]`을 함께 갱신하고 언어 전환의 레이아웃 이동을 최소화한다.
- 첫 visible frame이 이미 선택 언어인지 회귀 테스트로 고정한다. 언어와 무관한 API 때문에 first paint를 지연하지 않는다.

