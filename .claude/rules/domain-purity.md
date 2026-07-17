---
paths:
  - "app/src/main/java/com/ddakpul/math/domain/**"
---

# Domain 계층 규칙 (이 파일들을 만질 때 필수)

- **`android.*`, `androidx.*` import 절대 금지** — 순수 Kotlin/JVM만. 의존 방향은
  Presentation/Data → Domain 단방향 (역방향 금지).
- UseCase는 단일 책임 + `operator fun invoke` 하나만 노출. 생성자 주입만.
- 성공/실패는 `Result` + `AppError`. 예외를 흐름 제어에 쓰지 않는다.
- **UseCase를 추가·수정하면 단위 테스트 동반 필수.** 특히 `RecommendNextProblemUseCase`는
  추천 규칙 1~8이 각각 테스트로 고정돼 있다 — 규칙을 바꾸면 테스트도, `CLAUDE.md`의 규칙 표도,
  `docs/PEDAGOGY.md`의 근거도 함께 갱신한다.
- 매직값 금지: 난이도 한계는 `Difficulty.MIN/MAX`, 수치는 상수·enum으로.
