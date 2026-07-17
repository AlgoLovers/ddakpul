#!/usr/bin/env python3
"""Pretendard 가변 폰트를 앱 실제 사용 글자로 서브셋 → app/src/main/res/font/pretendard.ttf

한글 폰트는 통째로 넣으면 무겁다(6.7MB). 앱에 등장하는 글자만 남기면 ≈0.4MB로 줄고,
사용자 입력 텍스트가 없으므로(모든 한글이 우리 콘텐츠) 누락이 없다. 빠진 글자는 시스템 폰트로 대체.

⚠️ 문제은행(problems_generated*.json)이나 문자열을 바꾸면 이 스크립트를 다시 돌려 폰트를 갱신한다.
전제: PretendardVariable.ttf를 원본으로 두고(대용량이라 저장소 미포함), fonttools 설치.

사용: python3 tools/fonts/subset.py <PretendardVariable.ttf 경로>
"""
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "app/src/main/res/font/pretendard.ttf")


def collect_charset():
    chars = set()
    for p in [
        "app/src/main/res/values/strings.xml",
        "app/src/main/res/values-en/strings.xml",
    ]:
        chars |= set(open(os.path.join(ROOT, p), encoding="utf-8").read())
    for p in [
        "app/src/main/assets/problems_generated.json",
        "app/src/main/assets/problems_generated_en.json",
    ]:
        chars |= set(json.dumps(json.load(open(os.path.join(ROOT, p))), ensure_ascii=False))
    for f in glob.glob(os.path.join(ROOT, "app/src/main/java/**/seed/ProblemCatalog*.kt"), recursive=True):
        chars |= set(open(f, encoding="utf-8").read())
    chars |= set("".join(chr(c) for c in range(0x20, 0x7F)))  # ASCII
    chars |= set("℃㎠㎡㎤°±×÷≤≥≠→←↔·…！？，．：；（）［］「」『』“”‘’％＋－＝　0123456789")
    chars |= set("".join(chr(c) for c in range(0x1100, 0x1200)))  # 한글 자모
    return "".join(sorted(chars))


def main():
    if len(sys.argv) < 2:
        sys.exit("사용: python3 tools/fonts/subset.py <PretendardVariable.ttf>")
    src = sys.argv[1]
    charset_file = os.path.join(os.path.dirname(__file__), "_charset.txt")
    open(charset_file, "w", encoding="utf-8").write(collect_charset())
    subprocess.run(
        [
            sys.executable, "-m", "fontTools.subset", src,
            f"--text-file={charset_file}", f"--output-file={OUT}",
            "--layout-features=*", "--notdef-glyph", "--notdef-outline", "--recommended-glyphs",
        ],
        check=True,
    )
    print(f"→ {OUT}  ({os.path.getsize(OUT) // 1024} KB)")


if __name__ == "__main__":
    main()
