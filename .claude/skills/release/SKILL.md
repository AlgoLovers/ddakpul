---
name: release
description: 딱풀 릴리스를 한 번에 처리한다 — 버전 올림·CHANGELOG·스토어 문구·서명 AAB 빌드/검증·GitHub Release까지. 사용자가 "릴리스 해줘", "새 버전 내보내줘", "스토어 올릴 준비" 등을 요청할 때. 규칙 전문은 docs/RELEASE.md.
disable-model-invocation: true
---

# /release — 딱풀 릴리스 오케스트레이션

`docs/RELEASE.md`의 절차를 그대로 실행한다. **실수가 나올 지점을 매번 같은 순서로 없애는 게 목적**이라
단계를 건너뛰지 않는다. Play Console 업로드/검토전송은 사람 몫(클로드는 콘솔 접근 불가) — 그 직전까지 처리한다.

## 절차

1. **사전 점검**
   - 브랜치·동기화 상태 확인, 워킹트리 깨끗(더티면 먼저 커밋/`/wrap-up`).
   - `./gradlew testDebugUnitTest` 그린 확인. UI를 건드렸으면 `/emu-qa`도 권장.
   - 릴리스에 나가면 안 되는 실험 기능이 섞여 있지 않은지 사용자에게 확인.

2. **버전 올림** (`version.properties`만 수정)
   - `VERSION_CODE`를 **반드시 +1**(재사용·하향 금지, 모든 트랙 공유). 건너뜀은 무해.
   - `VERSION_NAME`: 버그면 PATCH, 기능이면 MINOR, 첫 프로덕션이면 `1.0`. 애매하면 사용자에게 물어본다.

3. **내부 CHANGELOG** (`CHANGELOG.md`)
   - `git log <직전태그>..HEAD`를 읽어 이번 버전 섹션을 Keep a Changelog 형식으로 추가
     (Added/Changed/Fixed…, 날짜·versionCode 포함). 기술적·전체.

4. **스토어 문구** (`app/src/main/play/release-notes/{ko-KR,en-US}/default.txt`)
   - 커밋을 그대로 옮기지 말 것. **혜택 중심으로 2~4줄 재작성**, 사용자 언어.
   - **한국어 먼저 → 영어**. 각 파일 **500자(공백·줄바꿈 포함) 이내**를 반드시 검증
     (`wc -m`; 영어가 먼저 한도를 넘는다). 넘으면 항목을 묶거나 덜 중요한 걸 빼서 줄인다.

5. **빌드**: `./gradlew :app:bundleRelease` (R8 적용, 2~5분).
   - `keystore.properties`+업로드 키스토어(리포 루트, gitignore)가 없으면 디버그 키로 폴백되니
     **반드시 6의 서명 검증을 통과해야 산출물로 인정**.

6. **서명 검증(필수)**
   ```
   unzip -p app/build/outputs/bundle/release/app-release.aab META-INF/*.RSA | keytool -printcert | grep SHA1
   ```
   기대값 `7E:FA:C6:D9:6A:C0:BF:37:82:BE:D2:69:1E:65:FD:FF:BE:59:93:17` (CN=DdakPul). 다르면 중단.

7. **커밋 + 아카이브**
   - `version.properties`·`CHANGELOG.md`·release-notes 변경을 커밋·푸시(`chore(release): vN …`).
   - **자산 파일명에 버전 필수** — 다운로드 파일명이 그대로 노출되므로 업로드 전에 이름을 바꾼다.
     gh의 `파일#라벨` 문법은 표시용일 뿐 다운로드 파일명을 못 바꾼다(v0.5.0 때 실수 사례):
     `cp app/build/outputs/bundle/release/app-release.aab ddakpul-v<버전>-release.aab`.
   - `mapping.txt` 압축: `gzip -c app/build/outputs/mapping/release/mapping.txt > ddakpul-v<버전>-mapping.txt.gz`.
   - GitHub Release 생성(태그 `v<VERSION_NAME>`, 본문=CHANGELOG 섹션):
     ```
     gh release create v<VERSION_NAME> --repo AlgoLovers/ddakpul --target <브랜치> \
       --title "..." --notes "..." \
       ddakpul-v<버전>-release.aab ddakpul-v<버전>-mapping.txt.gz \
       docs/store/icon-512.png docs/store/feature-1024x500.png \
       docs/store/marketing/ss{1..5}.png docs/store/marketing/tab{1..3}.png
     ```
   - 이전 버전 릴리스가 아직 Play 미업로드였다면 정리(삭제/대체) 판단.

8. **사람에게 넘김**: 릴리스 링크 + "무엇을 어디에 올리나"(docs/RELEASE.md §3) + 붙여넣을 ko/en 스토어
   문구 + 트랙/단계적 출시 안내를 출력. 콘솔 업로드·검토 전송은 사용자가 한다.

## 주의

- 큰 파일(.aab/.apk) 텔레그램 첨부 금지(50MB 한계로 상주세션 먹통 전례). GitHub Release 링크만 전달.
- 업로드 키 분실 = 업데이트 영구 불가. 키스토어 2파일은 사람이 구글 드라이브 백업(2026-07 완료).
- 저수준 "AAB만 만들기"는 `/release-aab`. 이 스킬은 그 위의 전체 릴리스 흐름이다.
