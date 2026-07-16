#!/usr/bin/env python3
"""다국어(i18n) 개념 증명(POC).

핵심 아이디어: 문제의 '수학'(숫자·정답·오답·도형)은 언어무관이고, '문장'(지문·해설·오답노트)만
언어별로 갈린다. 그래서 생성기를 '수학을 만드는 부분(spec)' + '언어별 문장 렌더러'로 나누면
한국어·영어 문제은행이 같은 수학에서 자동으로 함께 나온다(영원히 동기화).

이 POC는 이름·화폐가 없는 순수 수학 계열 2개로 한/영 문제를 동시에 뽑아 패턴과 품질을 보여준다.
실제 도입 시엔 generate.py의 각 gen_*를 이 구조(spec → 언어팩)로 옮기면 된다.
"""
import json
from math import comb


# ── 언어별 작은 문법 헬퍼 (영어는 한국어 조사 대신 a/an·복수·서수 정도만 필요) ──
def en_ordinal(k):
    return {1: "1st", 2: "2nd", 3: "3rd"}.get(k, f"{k}th")


def en_ngon(n):
    return {3: "equilateral triangle", 4: "square"}.get(n, f"regular {n}-gon")


# ── 계열 1: 정n각형 한 내각 (수학 = 언어무관) ──────────────────────────────
def spec_interior_angle(n):
    total = (n - 2) * 180
    ans = total // n
    return {
        "family": "interiorangle", "area": "SHAPE_MEASUREMENT", "difficulty": 4,
        "n": n, "total": total, "answer": ans,
        "distractors": [total // (n - 1), ans + 10, 180 - ans],
        "figure": {"type": "POLYGON", "params": {"n": n}},
    }


PROSE_INTERIOR = {
    "ko": lambda s: {
        "statement": f"정{s['n']}각형의 한 내각의 크기는 몇 도일까요? (모든 각이 같아요)",
        "answer": f"{s['answer']}도",
        "distractors": [f"{d}도" for d in s["distractors"]],
        "explanation": f"n각형의 내각의 합은 (n−2)×180이에요. 정{s['n']}각형은 {s['n']}−2={s['n'] - 2}, "
                       f"×180={s['total']}이고, 각이 {s['n']}개로 같으니 {s['total']}÷{s['n']}={s['answer']}도예요.",
    },
    "en": lambda s: {
        "statement": f"What is the measure of one interior angle of a {en_ngon(s['n'])}? (all angles are equal)",
        "answer": f"{s['answer']}°",
        "distractors": [f"{d}°" for d in s["distractors"]],
        "explanation": f"The interior angles of an n-gon add up to (n−2)×180. For a {en_ngon(s['n'])}, "
                       f"that is ({s['n']}−2)×180={s['total']}, and since all {s['n']} angles are equal, "
                       f"{s['total']}÷{s['n']}={s['answer']}°.",
    },
}


# ── 계열 2: 격자 최단 경로 (조합) ────────────────────────────────────────
def spec_lattice(w, h):
    ans = comb(w + h, w)
    return {
        "family": "lattice", "area": "NUMBER_OPERATION", "difficulty": 8,
        "w": w, "h": h, "answer": ans, "distractors": [ans + 1, ans + 2, w * h],
        "figure": {"type": "GRID", "params": {"w": w, "h": h, "mark": 1}},
    }


PROSE_LATTICE = {
    "ko": lambda s: {
        "statement": f"가로 {s['w']}칸, 세로 {s['h']}칸짜리 격자가 있어요. 왼쪽 아래에서 오른쪽 위 꼭짓점까지 "
                     f"오른쪽 또는 위로만 갈 때, 서로 다른 최단 경로는 모두 몇 가지일까요?",
        "answer": f"{s['answer']}가지",
        "distractors": [f"{d}가지" for d in s["distractors"]],
        "explanation": f"오른쪽으로 {s['w']}번, 위로 {s['h']}번, 합쳐서 {s['w'] + s['h']}번 움직이고 순서만 달라요. "
                       f"{s['w'] + s['h']}번 중 오른쪽 갈 {s['w']}번을 고르는 조합이라 {comb(s['w'] + s['h'], s['w'])}가지예요.",
    },
    "en": lambda s: {
        "statement": f"A grid is {s['w']} columns wide and {s['h']} rows tall. Moving only right or up from the "
                     f"bottom-left corner to the top-right corner, how many different shortest paths are there?",
        "answer": f"{s['answer']} paths",
        "distractors": [f"{d} paths" for d in s["distractors"]],
        "explanation": f"A shortest path makes {s['w']} moves right and {s['h']} moves up — {s['w'] + s['h']} moves in "
                       f"all, differing only in order. Choosing which {s['w']} of the {s['w'] + s['h']} moves go right "
                       f"gives C({s['w'] + s['h']},{s['w']})={s['answer']}.",
    },
}


def build(spec, prose_pack, lang):
    p = prose_pack[lang](spec)
    return {
        "family": spec["family"], "area": spec["area"], "difficulty": spec["difficulty"],
        "lang": lang, "statement": p["statement"],
        "choices": [p["answer"], *p["distractors"]], "answer": p["answer"],
        "explanation": p["explanation"], "figure": spec["figure"],
    }


def main():
    out = []
    for n in [5, 6, 8]:
        s = spec_interior_angle(n)
        for lang in ("ko", "en"):
            out.append(build(s, PROSE_INTERIOR, lang))
    for w, h in [(3, 2), (4, 2)]:
        s = spec_lattice(w, h)
        for lang in ("ko", "en"):
            out.append(build(s, PROSE_LATTICE, lang))
    json.dump(out, open("/tmp/ddakpul-i18n-poc.json", "w"), ensure_ascii=False, indent=2)
    # 사람이 보기 좋게 한/영 나란히
    for i in range(0, len(out), 2):
        ko, en = out[i], out[i + 1]
        print(f"[{ko['family']} · Lv.{ko['difficulty']}]  figure={ko['figure']['type']}")
        print(f"  KO: {ko['statement']}")
        print(f"      정답 {ko['answer']} · 보기 {ko['choices']}")
        print(f"  EN: {en['statement']}")
        print(f"      answer {en['answer']} · choices {en['choices']}")
        print()


if __name__ == "__main__":
    main()
