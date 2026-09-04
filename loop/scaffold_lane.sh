#!/usr/bin/env bash
# Scaffold a parallel autonomous-dev lane as an independent git worktree.
#
# Usage:
#   loop/scaffold_lane.sh <lane-name> <worktrees-parent-dir> "<scope-description>" [base-branch]
#
# Run this from inside the primary project checkout (the one with loop/loop.sh
# already configured and working). See docs/PARALLEL_LANES.md for the full
# design rationale and the problems this addresses (duplicate work, merge
# conflicts, shared-doc write races, push races, rate limits).
set -euo pipefail

if [[ $# -lt 3 ]]; then
  printf 'Usage: %s <lane-name> <worktrees-parent-dir> "<scope-description>" [base-branch]\n' "$0" >&2
  exit 2
fi

LANE_NAME="$1"
PARENT_DIR="$2"
SCOPE_DESC="$3"
BASE_BRANCH="${4:-main}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_NAME="$(basename "${ROOT_DIR}")"
LANE_BRANCH="${PROJECT_NAME}-${LANE_NAME}"
LANE_DIR="${PARENT_DIR}/${LANE_NAME}"

if [[ ! -f "${SCRIPT_DIR}/loop.sh" ]]; then
  printf 'This script must be run from a project with loop/loop.sh already set up (%s missing).\n' \
    "${SCRIPT_DIR}/loop.sh" >&2
  exit 2
fi

mkdir -p "${PARENT_DIR}"

cd "${ROOT_DIR}"
if git show-ref --verify --quiet "refs/heads/${LANE_BRANCH}"; then
  printf 'Branch %s already exists; reusing it.\n' "${LANE_BRANCH}"
else
  git branch "${LANE_BRANCH}" "${BASE_BRANCH}"
fi

if [[ -d "${LANE_DIR}" ]]; then
  printf 'Worktree dir already exists: %s (skipping git worktree add)\n' "${LANE_DIR}"
else
  git worktree add "${LANE_DIR}" "${LANE_BRANCH}"
fi

LANE_LOOP_DIR="${LANE_DIR}/loop"
mkdir -p "${LANE_LOOP_DIR}"

# Copy the loop machinery verbatim (paths inside loop.sh/run_agent.py are
# resolved relative to SCRIPT_DIR/ROOT_DIR at runtime, so no rewriting needed).
for f in loop.sh env.sh run_agent.py preflight.py classify_provider_failure.py control.sh; do
  if [[ -f "${SCRIPT_DIR}/${f}" ]]; then
    cp "${SCRIPT_DIR}/${f}" "${LANE_LOOP_DIR}/${f}"
    chmod --reference="${SCRIPT_DIR}/${f}" "${LANE_LOOP_DIR}/${f}" 2>/dev/null || true
  fi
done
chmod +x "${LANE_LOOP_DIR}/loop.sh" 2>/dev/null || true
[[ -f "${LANE_LOOP_DIR}/control.sh" ]] && chmod +x "${LANE_LOOP_DIR}/control.sh"

# Lane-scoped PROMPT.md: base PROMPT.md plus an explicit scope lock at the top
# so this lane cannot silently pick up work owned by another lane.
LANE_LABEL="com.jm.${PROJECT_NAME}.${LANE_NAME}-lane"
{
  printf '# LANE SCOPE — %s\n\n' "${LANE_NAME}"
  printf 'This worktree is one lane of a parallel multi-lane autonomous setup.\n'
  printf 'Work ONLY within this scope. Do not touch pending feedback items owned\n'
  printf 'by other lanes, and do not edit `docs/feedback/INBOX.md` items outside\n'
  printf 'your scope (append-only status notes to your own item are fine).\n\n'
  printf '## Scope for this lane\n\n%s\n\n' "${SCOPE_DESC}"
  printf '**중요 — 재감사 방지 규칙:** 이번 사이클에서 처리할 INBOX 항목이 이미 이전 사이클에서 완료됐다고 판단되면, STATUS.md 업데이트 없이 즉시 다음 미완료 항목으로 넘어가라. "이미 완료됐음을 재확인"하는 문서 커밋을 반복하지 않는다. 할 일이 없으면 IDLE로 종료한다.\n\n'
  printf '**중요 — FAIL + 미커밋 변경 규칙:** preflight가 FAIL이고 git status에 수정된 파일이 있으면, 이번 사이클의 유일한 작업은 (1) 실패한 테스트를 수정하고 (2) 모든 수정 파일을 커밋하는 것이다. 새 INBOX 항목 작업을 시작하지 않는다. 미커밋 변경을 버리지 않는다 — 이전 사이클이 절반만 완료한 것을 마저 끝낸다.\n\n'
  printf '**중요 — 한 사이클 한 조각:** 큰 INBOX 항목(ComfyUI 에셋 생성, 전면 UI 개편 등)을 한 사이클에 다 끝내려 하지 마라. 사이클당 검증 가능한 최소 단위 하나만 완료하고 커밋한다. ComfyUI는 장면 1개 또는 에셋 1~3장만 생성·로그 반영·커밋. 큰 기능은 (a)/(b)/(c) 중 한 소항목만. 턴 한도 안에 커밋할 수 없으면 범위를 더 줄여라. 미커밋으로 턴을 다 쓰는 것은 금지.\n\n'
  printf '**TOKEN RULE (large files):** Never read_file a source file ≥80KB without offset+limit. Use search_files then read ≤80 lines around the match. Full-file reads stay in context for every remaining turn of this oneshot cycle.\n\n'
  printf '## Branch and push discipline\n\n'
  printf -- '- This lane commits and pushes ONLY to branch `%s`. Never push to\n' "${LANE_BRANCH}"
  printf '  `main`/`master` directly, never force-push.\n'
  printf -- '- A separate integration step periodically merges this branch into\n'
  printf '  the base branch after `make verify` passes.\n\n'
  printf -- '---\n\n'
  cat "${SCRIPT_DIR}/PROMPT.md"
} > "${LANE_LOOP_DIR}/PROMPT.md"

# Lane-scoped plist (distinct Label so launchd tracks it independently).
SRC_PLIST="$(find "${SCRIPT_DIR}" -maxdepth 1 -iname '*.plist' | head -1)"
if [[ -n "${SRC_PLIST}" ]]; then
  sed \
    -e "s#${ROOT_DIR}#${LANE_DIR}#g" \
    -e "s#com\.jm\.${PROJECT_NAME}\.autodev-loop#${LANE_LABEL}#g" \
    "${SRC_PLIST}" > "${LANE_LOOP_DIR}/${LANE_LABEL}.plist"
  printf '<key>LOOP_ROOT</key>\n' >> /dev/null # no-op, placeholder for readability
fi

printf 'Lane scaffolded: %s\n' "${LANE_DIR}"
printf '  branch:  %s\n' "${LANE_BRANCH}"
printf '  prompt:  %s\n' "${LANE_LOOP_DIR}/PROMPT.md"
if [[ -n "${SRC_PLIST}" ]]; then
  printf '  plist:   %s (copy to ~/Library/LaunchAgents/ and launchctl bootstrap to start)\n' \
    "${LANE_LOOP_DIR}/${LANE_LABEL}.plist"
fi
printf '\nNext steps:\n'
printf '  1. Review/edit %s\n' "${LANE_LOOP_DIR}/PROMPT.md"
printf '  2. cp %s ~/Library/LaunchAgents/\n' "${LANE_LOOP_DIR}/${LANE_LABEL}.plist"
printf '  3. launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/%s.plist\n' "${LANE_LABEL}"
