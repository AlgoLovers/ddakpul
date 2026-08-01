# RELEASE.md — 딱풀 릴리스 플레이북

릴리스에서 **실수가 나올 수 있는 지점을 시스템으로 없애기 위한** 문서. 실제 실행은
`/release` 스킬이 이 절차를 그대로 수행한다(수동으로 하면 빠뜨린다). 근거·조사 출처는 맨 아래.

---

## 1. 버저닝 철칙 (어기면 업로드 거부되거나 크래시)

버전은 **`version.properties` 한 파일에서만** 관리한다(build.gradle.kts는 이 파일을 읽을 뿐).

- **`VERSION_CODE`** — 단조증가 정수. **Play에 올리는 빌드마다 +1. 절대 재사용·하향 금지.**
  - 번호 공간은 **모든 트랙(내부·비공개·프로덕션)이 공유**한다. 트랙별 카운터가 아니다.
    → 비공개에 13을 썼으면 프로덕션은 14 이상이어야 한다. **중간 건너뜀(예: 10→13)은 무해.**
  - "새 업로드 = +1, 예외 없음"만 지키면 절대 안 꼬인다.
- **`VERSION_NAME`** — 사용자에게 보이는 SemVer. 기능=MINOR, 버그=PATCH.
  공개 출시 전엔 `0.x`, **첫 프로덕션 출시 때 `1.0`**. VERSION_CODE와 독립적으로 움직인다.

## 2. 릴리스 절차 (= `/release` 스킬이 자동 수행)

1. **사전 점검**: 브랜치 최신·트리 깨끗(`/wrap-up` 상태)·`./gradlew testDebugUnitTest` 그린.
2. **버전 올림**: `version.properties`의 `VERSION_CODE +1`, `VERSION_NAME`은 변경 성격대로.
3. **내부 CHANGELOG**: 지난 태그 이후 커밋에서 `CHANGELOG.md`에 이번 버전 섹션 추가(기술적·전체).
4. **스토어 문구**: `app/src/main/play/release-notes/{ko-KR,en-US}/default.txt` 갱신
   (혜택 중심·**각 500자 이내**·한국어 먼저 쓰고 영어로 — 영어가 먼저 한도를 넘는다).
5. **빌드**: `./gradlew :app:bundleRelease`.
6. **서명 검증(필수)**: AAB 서명 SHA1이 업로드 키와 일치해야 산출물로 인정.
   기대값 `7E:FA:C6:D9:6A:C0:BF:37:82:BE:D2:69:1E:65:FD:FF:BE:59:93:17` (CN=DdakPul).
   불일치면 업로드 금지 → 키스토어 위치부터 확인.
7. **아카이브(GitHub Release가 원장)**: 태그 `v<VERSION_NAME>`, 자산 = **AAB + `mapping.txt.gz`**.
   본문 = CHANGELOG 해당 섹션. (`.aab`/키스토어는 git 커밋 금지 — 릴리스 자산으로만.)
   **자산 파일명에 버전을 반드시 포함**: `ddakpul-v<버전>-release.aab` ·
   `ddakpul-v<버전>-mapping.txt.gz` (디버그 APK 릴리스도 `ddakpul-<태그>-debug.apk` 식).
   다운로드 파일명은 업로드한 파일의 실제 이름을 그대로 따르므로 **업로드 전에 `cp`로 개명**한다 —
   gh의 `파일#라벨` 문법은 릴리스 페이지 표시용일 뿐 다운로드 파일명을 바꾸지 못한다(v0.5.0 실수 사례).
8. **콘솔 업로드(사람)**: 아래 3의 목록대로 올리고, 스토어 문구 붙여넣고, 프로덕션은 단계적 출시.

## 3. 무엇을 어디에 올리나 (Play Console)

| 파일 | 위치 | 콘솔 위치 |
|---|---|---|
| `app-release.aab` | GitHub Release 자산 | 트랙 → 앱 번들 |
| `icon-512.png` (512²) | `docs/store/` | 등록정보 → 앱 아이콘 |
| `feature-1024x500.png` | `docs/store/` | 등록정보 → 그래픽 이미지 |
| `ss1~5.png` (1080×1920) | `docs/store/marketing/` | 등록정보 → 휴대전화 |
| `tab1~3.png` (2160×1215) | `docs/store/marketing/` | 등록정보 → 7·10인치 태블릿 |
| ko/en 스토어 문구 | `app/src/main/play/release-notes/` | 출시 → 새로운 기능 |

`mapping.txt`는 AAB에 자동 포함돼 Play가 알아서 쓴다. GitHub 아카이브는 오프라인 retrace·타 크래시리포터 대비 보험.

## 4. Play 트랙 전략

`내부 테스트(빠른 QA) → 비공개 테스트(개인계정 필수 게이트: 테스터 12명 × 14일 연속) → 프로덕션`.
프로덕션은 **단계적 출시**(예: 5%→20%→50%→100%)로, 각 단계에서 크래시/vitals 확인, 이상 시
**롤아웃 중단(Halt)**. 트랙이 여럿이면 Play는 사용자에게 **가장 높은 versionCode**를 제공한다.

## 5. 알려진 잔여 경고 (전부 비차단·무해 — 없애려 애쓰지 말 것)

- **네이티브 디버그 심볼 없음**: TTS(sherpa-onnx) 등 서드파티 native가 **stripped로 배포**돼 심볼이
  없다. `debugSymbolLevel`로도 못 넣는다. 딱풀 본체는 순수 Kotlin이라 크래시는 항상 해독됨 → 무해.
- **"AGP 9.0으로 업그레이드" 권고**: AGP 정식 9.0 출시 전이라 지금은 불가. 정보성.

## 6. 나중에 (릴리스가 잦아지면 승격)

- **CI 먼저**(푸시마다 빌드+테스트+detekt) → 이후 **CD**(Gradle Play Publisher로 트랙 자동 업로드).
  키스토어는 base64 GitHub Secret. 지금은 수동 업로드가 정상 스테디스테이트.
- CHANGELOG 완전 자동화가 필요해지면 **git-cliff**(단일 바이너리) 또는 **release-please**(PR→태그→릴리스).
  현재는 `/release` 스킬(클로드)이 그 역할을 하니 불필요.

---

### 근거 / 참고
- Android 공식 버저닝: https://developer.android.com/studio/publish/versioning
- versionCode는 트랙 공유(사례): https://github.com/fastlane/fastlane/issues/6791
- Keep a Changelog: https://keepachangelog.com/ko/1.1.0/ · SemVer: https://semver.org/lang/ko/
- Play 단계적 출시: https://support.google.com/googleplay/android-developer/answer/6346149
- 크래시 역난독화(버전별·소급불가): https://support.google.com/googleplay/android-developer/answer/9848633
- Gradle Play Publisher: https://github.com/Triple-T/gradle-play-publisher
