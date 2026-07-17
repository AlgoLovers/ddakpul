---
name: gen-problems
description: 문제은행 생성·검증·검수 파이프라인. 문제 추가/천장 확장/오류 문제 교체 때 사용 — 솔버 검증과 problem-auditor 검수를 통과해야 앱에 들어간다.
---

# /gen-problems — 문제 생성 파이프라인

원칙(CLAUDE.md): 문제는 사전 생성·앱 내장, 반드시 **사고력** 문제(계산 드릴·교과 정리 요구 금지),
천장을 올릴 때는 그 층을 4개 영역 모두 채운다.

## 절차

1. **슬롯 파악**: `app/src/main/assets/problems_generated.json`에서 영역×난이도 분포를 세어
   비거나 얇은 슬롯을 정한다.
2. **템플릿 작성/수정**: `tools/problemgen/generate.py`에 파라미터 템플릿 추가.
   - 정답은 반드시 **브루트포스 솔버로 검증** — 템플릿마다 독립 검증 함수를 짝으로 작성.
   - **이중언어 불변식**: 모든 문장 생성에 `en=` kwarg 짝, 랜덤 분기는 `rng_en` 규약
     (한/영이 같은 난수열을 쓰게) — 이걸 깨면 한/영 정답이 어긋난다.
   - `blocklist.txt`의 id는 영구 제외 — 생성 결과에 되살아나면 버그.
3. **도형 문제**: figure params를 쓰는 문제는 `tools/problemgen/preview_figures.py`로
   PNG를 뽑아 Read로 눈 검증(그림-문제-정답 일치). 앱 렌더러(ProblemFigureView)와
   PDF(drawFigure)가 같은 수학을 쓰므로 미리보기가 곧 검증이다.
4. **생성 실행**: `python3 tools/problemgen/generate.py` → ko/en JSON 두 파일 갱신 확인.
5. **검수 (필수)**: `problem-auditor` 서브에이전트에 신규/변경 그룹을 넘겨 감사받는다.
   치명 위반(사고력 원칙·이중언어)이 있으면 앱에 넣지 않는다.
6. **앱 반영**: assets 교체만으로는 기존 설치에 재시딩 안 됨 — 콘텐츠 버전/DB 마이그레이션
   정책 확인(data/local 시딩 코드). 에뮬 확인은 `pm clear` 후.
7. 단위 테스트(`testDebugUnitTest`) → /wrap-up으로 커밋.

## 경험칙

- 한 그룹 = 같은 개념·난이도의 숫자 변형 4~6문항 (추천 단위이자 재도전 풀).
- 보기(choices)에는 그럴듯한 오답(전형적 실수)을 넣고 mistakes에 그 오개념을 기록.
- 상위 난이도(8~10)는 경시급 추론 — 필요 지식은 초등 범위, 깊이는 추론으로 만든다.
