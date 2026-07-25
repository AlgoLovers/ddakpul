# Changelog

딱풀의 주요 변경을 기록한다(개발자용·기술적). 형식은
[Keep a Changelog](https://keepachangelog.com/ko/1.1.0/), 버전은 [SemVer](https://semver.org/lang/ko/)를 따른다.

> 사용자에게 보이는 스토어 "새로운 기능" 문구는 여기가 아니라
> `app/src/main/play/release-notes/<locale>/default.txt`에 **따로**(간결·혜택 중심·각 500자 이내) 관리한다.
> 두 문서는 독자가 다르다 — 여기는 내가 보는 전체 기술 로그, 저기는 사용자가 보는 요약.

## [Unreleased]

## [0.3.11] - 2026-07-25 · versionCode 13
### Changed
- R8(코드 축소·난독화·최적화) 활성화. keep 규칙: 직렬화 DTO + sherpa JNI 경계(`com.k2fsa.sherpa.onnx.**`).
  앱 용량 50→41MB, Play Console 난독화/축소/최적화 경고 해소. 에뮬 전수 스모크 통과.
- 버전을 `version.properties` 단일 소스로 이관(build.gradle.kts 하드코딩 제거).

## [0.3.10] - 2026-07-24 · versionCode 12
### Removed
- "정답이 이상해요"(정답 오류 신고) 버튼·공유·문자열 — 정답은 솔버 검증이라 불필요.
### Changed
- "이 문제 별로예요" 제외 목록을 개발자 메일(고정 수신처)로 바로 보내도록 변경.
  무수집 원칙 유지(무서버·사용자 자발 전송, 보내는 값은 문제ID 등 품질 신호뿐).

## [0.3.9] - 2026-07-24 · versionCode 11
### Added
- 네이티브 디버그 심볼 옵션(`debugSymbolLevel=FULL`) — 단, native가 전부 서드파티 stripped라 실질 무효.
  (Play엔 미업로드, v0.3.10에 흡수)

---
0.3.8 이하의 개발 이력은 git 로그를 참조한다(`git log v0.3.8`).
