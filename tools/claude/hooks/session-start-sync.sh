#!/bin/bash
# SessionStart 훅 — 두 세션 조율 규약 "시작 전 git fetch + 최신 develop 반영" 자동화.
# 세션이 열릴 때 원격을 fetch하고 동기화 상태를 컨텍스트로 주입한다 (CLAUDE.md 세션 조율 절).
cd "$(dirname "$0")/../../.." || exit 0
git fetch -q origin 2>/dev/null
behind_dev=$(git rev-list --count HEAD..origin/develop 2>/dev/null || echo "?")
dirty=$(git status --porcelain 2>/dev/null | grep -cv keystore)
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"[세션 동기화] git fetch 완료 · origin/develop 대비 뒤처짐 %s커밋 · 미커밋(키스토어 제외) %s개. 뒤처졌으면 pull 먼저, 미커밋이 있으면 다른 세션이 남긴 것인지 확인."}}\n' "$behind_dev" "$dirty"
