---
paths:
  - "tools/problemgen/**"
  - "app/src/main/assets/problems_generated*.json"
---

# 문제 생성 파이프라인 규칙 (이 파일들을 만질 때 필수)

구조(2026-07 분할): `core.py`(공용 인프라) · `gen_number/change/shape/data.py`(영역별 제너레이터)
· `build.py`(GENERATORS 실행→게이트→저장) · `generate.py`(진입점 shim) · `checks.py`(품질 게이트).

- **GENERATORS 순서 = rng 소비 순서 = 산출 재현성.** 항목은 끝에 추가만, 재배치 금지.
- **CI가 결정성을 강제한다**: 재생성 산출이 커밋본과 0-diff여야 머지된다. 생성기를 고치면
  반드시 재생성해서 JSON을 함께 커밋할 것.
- 모든 템플릿의 정답은 **독립 브루트포스 솔버로 검증**돼야 한다 — 템플릿과 검증 함수는 짝.
  검산 없는 제너레이터는 `보고6`에 잡힌다(백로그 축소 방향으로만).
- 난이도 순서 제약은 `difficulty_constraints.json`에 기계 검증으로 축적한다
  ('적용만 < 발견' 원칙 — recur 강등 사례의 재발 방지 장치).
- **다양성 = 서로 다른 유형(method) 수**(문제 수 아님). checks.py 게이트5가 개념·정답·문장이
  모두 유사한 '사실상 중복' 유형쌍을 빌드 실패시킨다(오늘의 cubesurf=boxsurface 재발 방지).
  의도된 형제(난이도 사다리 등)는 정답 겹침이 낮아 자동 통과 — 정말 형제인데 막히면
  `duplicate_allowlist.json`에, 정말 중복이면 `blocklist.txt`에. 얇은 유형 칸은 `보고8b` 참조.
- **이중언어 불변식**: 문장 생성에는 `en=` kwarg 짝, 랜덤 분기는 `rng_en` 규약(한/영 동일 난수열).
  ko/en JSON은 같은 id 집합·같은 정답이어야 하며, 이게 깨지면 치명 버그다.
- `blocklist.txt`의 id는 영구 제외 — 재생성 후에도 부활하면 안 된다.
- 문제는 반드시 **사고력** 유형: 계산 드릴, 초등 범위 밖 정리·공식(피타고라스 등) 요구 금지.
  판별과 상세 절차는 `/gen-problems` 스킬, 검수는 `problem-auditor` 에이전트.
- figure 파라미터를 바꾸면 `preview_figures.py`로 PNG를 뽑아 눈으로 검증한다
  (앱 렌더러·PDF가 같은 수학을 공유하므로 미리보기 = 검증).
- **계층 코드는 `generate.py`가 `codes.py`로 자동 주입**한다(재생성해도 code 안 사라짐).
  `method_codes.json`은 안정 레지스트리 — 기존 방법 코드 불변, 신규 family만 append.
  JSON을 손으로 고칠 땐 `difficulty`·`groupId`·`code`(DD·SS 세그먼트)를 함께 맞춰야 한다.
- assets JSON 교체는 기존 설치에 자동 재시딩되지 않는다 — 내용이 바뀌면
  `AssetProblemSource.CONTENT_VERSION`을 +1(문항 수 불변이어도). 문제 id는 유지해 학습 기록 보존.
