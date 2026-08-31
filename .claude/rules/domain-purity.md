---
paths:
  - "app/src/main/java/com/ddakpul/math/domain/**"
---

# Domain 계층 규칙 (이 파일들을 만질 때 필수)

- **`android.*`, `androidx.*` import 절대 금지** — 순수 Kotlin/JVM만. 의존 방향은
  Presentation/Data → Domain 단방향 (역방향 금지).
- **domain은 `core`·`data`·`presentation`·`ui` 어느 것도 import하지 않는다.** 공용 타입이
  필요하면 `domain/common`에 둔다(`AppResult`·`AppError`·`MILLIS_PER_DAY`·`toPercentInt`).
- **시간을 직접 읽지 않는다** — `System.currentTimeMillis()`·`TimeZone.getDefault()` 금지.
  UseCase는 시각을 파라미터(`nowMillis`·`zoneOffsetMillis`)로 받아 순수 함수로 남는다.
  주입이 필요한 계층(화면·저장소)은 `domain/time/Clock`을 쓴다.
- 위 규칙들은 `ArchitectureRulesTest`가 소스 트리를 읽어 강제한다 — 어기면 테스트가 깨진다.
- UseCase는 단일 책임 + `operator fun invoke` 하나만 노출. 생성자 주입만.
- 성공/실패는 `Result` + `AppError`. 예외를 흐름 제어에 쓰지 않는다.
- **UseCase를 추가·수정하면 단위 테스트 동반 필수.** 특히 `RecommendNextProblemUseCase`는
  추천 규칙 1~8이 각각 테스트로 고정돼 있다 — 규칙을 바꾸면 테스트도, `CLAUDE.md`의 규칙 표도,
  `docs/PEDAGOGY.md`의 근거도 함께 갱신한다.
- 매직값 금지: 난이도 한계는 `Difficulty.MIN/MAX`, 수치는 상수·enum으로.
