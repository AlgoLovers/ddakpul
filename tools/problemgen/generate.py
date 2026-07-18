#!/usr/bin/env python3
"""딱풀 사고력 문제 생성기 (v1).

유형(아이디어)은 저작권 보호 대상이 아니므로, 고전 사고력 유형의 파라미터 템플릿으로
오리지널 문제를 생성하고 — 핵심 — 모든 문제의 정답을 독립적인 무차별 대입(brute force)으로
재검산한다. 검산에 실패하거나 해가 유일하지 않으면 그 문제는 버린다.

사용: python3 tools/problemgen/generate.py
출력: app/src/main/assets/problems_generated.json (+ 콘솔 통계)

docs/CONTENT_SOURCING.md 3단계(템플릿+생성+솔버 검증)의 1차 구현.
"""
import build  # noqa: F401 — 전체 파이프라인 실행(분할: core/gen_*/build)
