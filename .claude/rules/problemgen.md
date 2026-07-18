---
paths:
  - "tools/problemgen/**"
  - "app/src/main/assets/problems_generated*.json"
---

# 문제 생성 파이프라인 규칙 (이 파일들을 만질 때 필수)

- 모든 템플릿의 정답은 **독립 브루트포스 솔버로 검증**돼야 한다 — 템플릿과 검증 함수는 짝.
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
