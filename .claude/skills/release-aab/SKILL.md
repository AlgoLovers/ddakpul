---
name: release-aab
description: 서명 릴리스 AAB를 빌드하고 서명·버전을 검증하는 하위 절차. 전체 릴리스(버전 올림·CHANGELOG·태그)는 /release가 담당하고, 이 스킬은 "빌드+검증"만 한다. 사용자가 빌드 파일만 급히 원할 때 사용.
disable-model-invocation: true
---

# /release-aab — 서명 릴리스 번들 빌드+검증 (하위 절차)

전체 릴리스 흐름(버전 올림 → CHANGELOG → 스토어 문구 → 빌드 → 태그/아카이브)은 **`/release`**가
오케스트레이션한다(규칙 전문: `docs/RELEASE.md`). 이 스킬은 그중 "빌드와 서명 검증"만 떼어 낸
하위 절차다 — 버전을 바꾸지 않고, 태그도 만들지 않는다.

## 절차

1. **빌드 기준 확인**: 릴리스는 main에서 빌드한다(develop 미머지 변경 금지 — 필요하면 release PR
   먼저: develop→main PR 머지 후 main 체크아웃). 버전은 `version.properties`가 단일 원전
   (build.gradle.kts는 이 파일을 읽을 뿐). Play에 이미 올린 versionCode면 `/release`로 올리고 올 것.
2. **빌드**: `./gradlew -q :app:bundleRelease` (2~5분).
   `keystore.properties`+`ddakpul-upload.keystore`(리포 루트, gitignore)가 없으면 디버그 키로
   폴백되니 **반드시 서명 검증을 통과해야 산출물로 인정**.
3. **서명 검증** (필수):
   ```
   unzip -p app/build/outputs/bundle/release/app-release.aab META-INF/*.RSA | keytool -printcert | grep SHA1
   ```
   기대값: `7E:FA:C6:D9:6A:C0:BF:37:82:BE:D2:69:1E:65:FD:FF:BE:59:93:17` (CN=DdakPul, OU=AlgoLovers).
   다르면 업로드 금지하고 키스토어 위치부터 확인.
4. **보고**: 산출물 경로(`app/build/outputs/bundle/release/app-release.aab`)·크기·버전을 보고한다.
   배포(GitHub Release 업로드·바탕화면 복사 등)는 `/release` 7단계 또는 사용자 지시에 따른다.
   GitHub Release에 올릴 때는 **개명한 파일을 업로드**한다(`ddakpul-v<버전>-release.aab` —
   `파일#라벨` 문법은 표시용일 뿐 다운로드 파일명을 못 바꾼다).

## 주의

- 업로드 키 분실 = 앱 업데이트 불가. 키스토어 2파일은 사람이 구글 드라이브에 백업해둠(2026-07).
