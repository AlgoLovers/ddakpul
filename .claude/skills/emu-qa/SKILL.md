---
name: emu-qa
description: 에뮬레이터에 앱을 띄워 스크린샷으로 UI를 눈으로 검증하는 QA 루프. UI 변경 후, 스토어 스크린샷 제작, 실기기 버그 재현에 사용.
---

# /emu-qa — 에뮬레이터 스크린샷 QA 루프

Pillow 미리보기가 못 잡는 실제 화면 버그(레이아웃 잘림, 인셋, 렌더 누락)를 잡는다.
실례: 홈 '학습 시작' 라벨이 수직 패딩 때문에 안 보이던 버그를 이 루프로 발견·수정(2026-07).

## 부팅 (함정 주의)

```
export PATH="$PATH:$HOME/Library/Android/sdk/emulator:$HOME/Library/Android/sdk/platform-tools"
nohup emulator -avd Pixel_API_TiramisuPrivacySandbox -no-window -no-audio -no-boot-anim -no-snapshot -gpu host &
adb wait-for-device
adb shell 'while [ "$(getprop sys.boot_completed)" != "1" ]; do sleep 2; done'
adb shell settings put global window_animation_scale 0   # transition·animator도 0
```

- **`-gpu host` 필수** — swiftshader면 screencap이 흰 화면(8KB)만 뱉는다.
- 폰=`Pixel_API_TiramisuPrivacySandbox`(1080×1920, ~40초), 태블릿=`ddakpul_tablet`(1280×800).
  `tablet_pc` AVD는 QEMU 행으로 멈춤 — 쓰지 말 것.
- 에뮬 2대 동시 운용 시 모든 adb에 `-s emulator-5554/5556`.

## 루프

1. `./gradlew -q :app:assembleDebug` → `adb install -r app/build/outputs/apk/debug/app-debug.apk`
2. 실행: `adb shell am start -n com.ddakpul.math/.MainActivity`
3. 캡처: `adb exec-out screencap -p > shot.png` → Read로 눈 확인.
4. 조작: `adb shell uiautomator dump /sdcard/ui.xml` → text/bounds 파싱 → `input tap x y`.
   좌표 하드코딩보다 bounds 파싱이 안정적. 반복 풀이는 스크래치패드의 drive.py 패턴 재사용.
5. 문제 발견 → 코드 수정 → 1로.

## ⚠️ 테마 매트릭스 (UI 변경이면 필수 — docs/DESIGN.md)

- **라이트와 다크 둘 다 확인**: `adb shell cmd uimode night yes`(다크) / `no`(라이트).
  다크 한 번만 돌렸어도 잡혔을 "흰 배경+흰 글씨" 전면 사고가 실제로 있었다(2026-07).
- 레이아웃 분기가 다르면 **폰과 태블릿 둘 다** (태블릿 레일 분기는 Scaffold가 없어
  루트 도색·인셋 계열 사고가 태블릿에서만 났다).

## 함정 모음

- **assets JSON 교체 후엔 `adb shell pm clear com.ddakpul.math`** — `-r` 재설치만으론 재시딩 안 됨.
- 시스템 로케일이 영어라 첫 부팅은 영어 UI — 설정 탭에서 앱 내 언어 토글로 한국어 전환.
- PDF 검증 = 시스템 인쇄 미리보기 캡처(생성기를 그대로 렌더하므로 그게 진짜 출력물).
- 스토어 스크린샷은 알파 제거(PIL convert RGB) 후 `docs/store/screenshots/`에 저장.
- 끝나면 `adb emu kill`로 정리.
