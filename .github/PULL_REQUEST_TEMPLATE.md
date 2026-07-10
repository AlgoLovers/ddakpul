## 무엇을 / 왜

<!-- 이 PR이 관통하는 수직 슬라이스(한 기능)와 목적을 한 줄로 -->

## 변경 사항

-

## 체크리스트

- [ ] `./gradlew spotlessApply` 로 포맷 정리
- [ ] `./gradlew detekt` 통과
- [ ] `./gradlew testDebugUnitTest` 통과 (추천 알고리즘 변경 시 규칙별 테스트 추가)
- [ ] Domain 계층에 `android.*` import 없음
- [ ] 의존성 방향 Presentation/Data → Domain 유지
