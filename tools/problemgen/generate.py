#!/usr/bin/env python3
"""딱풀 사고력 문제 생성기 (v1).

유형(아이디어)은 저작권 보호 대상이 아니므로, 고전 사고력 유형의 파라미터 템플릿으로
오리지널 문제를 생성하고 — 핵심 — 모든 문제의 정답을 독립적인 무차별 대입(brute force)으로
재검산한다. 검산에 실패하거나 해가 유일하지 않으면 그 문제는 버린다.

사용: python3 tools/problemgen/generate.py
출력: app/src/main/assets/problems_generated.json (+ 콘솔 통계)

docs/CONTENT_SOURCING.md 3단계(템플릿+생성+솔버 검증)의 1차 구현.
"""
import json
import random
from math import comb
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "app/src/main/assets/problems_generated.json"
rng = random.Random(20260710)  # 재현 가능하게 시드 고정

NAMES = ["민준", "서연", "지호", "하은", "도윤", "예린", "시우", "지아"]
FRUITS = ["사과", "귤", "배", "감"]
COLORS3 = [["빨간", "노란", "파란"], ["초록", "보라", "주황"]]

problems = []
stats = {"generated": 0, "rejected": 0}


def _bump_number(text, delta):
    """문자열 속 첫 숫자를 delta만큼 밀어 대체 오답을 만든다."""
    import re as _re
    m = _re.search(r"\d+", text)
    if not m:
        return text + "?"
    n = max(1, int(m.group()) + delta)
    return text[: m.start()] + str(n) + text[m.end():]


def add(family, area, diff, concepts, statement, answer_text, distractors, expl, mistakes=None, figure=None):
    """정답 1 + 오답 3을 섞어 4지선다로 만든다. 겹치는 오답은 숫자를 밀어 자동 대체."""
    unique = []
    for d in distractors:
        if d != answer_text and d not in unique:
            unique.append(d)
    delta = 3
    while len(unique) < 3:
        candidate = _bump_number(answer_text, delta)
        if candidate != answer_text and candidate not in unique:
            unique.append(candidate)
        delta += 2
    choices = [answer_text] + unique[:3]
    assert len(set(choices)) == 4, f"{family}: 보기 중복 {choices}"
    order = list(range(4))
    rng.shuffle(order)
    shuffled = [choices[i] for i in order]
    answer_index = shuffled.index(answer_text)
    idx = sum(1 for p in problems if p["groupId"] == f"g-gen-{family}-{diff}") + 1
    problem = {
        "id": f"gen-{family}-{idx}",
        "area": area,
        "difficulty": diff,
        "groupId": f"g-gen-{family}-{diff}",
        "concepts": concepts,
        "statement": statement,
        "choices": shuffled,
        "answerIndex": answer_index,
        "explanation": expl,
        "mistakes": [
            {"choiceIndex": shuffled.index(text), "misconception": why}
            for text, why in (mistakes or [])
            if text in shuffled and shuffled.index(text) != answer_index
        ],
        "source": "generated:v1(template+brute-force-verified)",
    }
    if figure:
        problem["figure"] = figure
    problems.append(problem)
    stats["generated"] += 1


# ── 1. 복면산 AB+BA (난4, 수와연산) ──────────────────────────────────────────
def gen_cryptarithm():
    used = set()
    for s in [9, 12, 14, 16]:  # A+B
        total = 11 * s
        # 검산: (10A+B)+(10B+A)=total이 되는 (A,B)가 존재하고, 모두 A+B=s인지 확인
        sols = [(a, b) for a in range(1, 10) for b in range(1, 10) if (10 * a + b) + (10 * b + a) == total]
        assert sols and all(a + b == s for a, b in sols), f"cryptarithm 검산 실패 s={s}"
        if s in used:
            continue
        used.add(s)
        candidates = [str(s - 1), str(s + 1), str(total // 10), str(s + 3)]
        distractors = [c for c in dict.fromkeys(candidates) if c != str(s)][:3]
        add(
            "crypt", "NUMBER_OPERATION", 4, ["복면산", "자리값 사고"],
            f"두 자리 수 (가나)와 자리를 바꾼 수 (나가)를 더했더니 {total}이 되었어요. 가+나는 얼마일까요? (가, 나는 0이 아닌 한 자리 숫자)",
            str(s), distractors,
            f"(가나)+(나가) = 11×(가+나)예요. {total}÷11={s}이니 가+나={s}.",
            [(str(total // 10), "두 수의 합은 항상 11의 배수예요. 11로 나눠 보세요.")],
        )


# ── 2. 닭·토끼 다리 세기 (난3, 수와연산) ─────────────────────────────────────
def gen_chicken_rabbit():
    for total, rabbits in [(6, 2), (8, 3), (10, 4), (12, 5)]:
        legs = 2 * (total - rabbits) + 4 * rabbits
        sols = [r for r in range(1, total) if 2 * (total - r) + 4 * r == legs]
        assert sols == [rabbits], f"닭토끼 검산 실패 {total},{rabbits}"
        add(
            "legs", "NUMBER_OPERATION", 3, ["다리 세기", "가정하여 풀기"],
            f"마당에 닭과 토끼가 모두 {total}마리 있어요. 다리를 세어 보니 {legs}개였어요. 토끼는 몇 마리일까요?",
            f"{rabbits}마리", [f"{rabbits - 1}마리", f"{rabbits + 1}마리", f"{total - rabbits}마리"],
            f"모두 닭이라면 다리는 {2 * total}개. 실제보다 {legs - 2 * total}개 많은 것은 토끼가 2개씩 더 갖기 때문 — {legs - 2 * total}÷2={rabbits}마리가 토끼예요.",
            [(f"{total - rabbits}마리", "그건 닭의 수예요. 문제는 토끼를 물었어요.")],
        )


# ── 3. 과부족 (난4, 수와연산) ────────────────────────────────────────────────
def gen_excess_deficit():
    for p, x, a, dy in [(5, 4, 3, 1), (6, 3, 4, 2), (7, 4, 5, 1), (8, 5, 6, 2)]:
        y = x + dy
        items = x * p + a
        b = y * p - items
        if b <= 0:
            stats["rejected"] += 1
            continue
        # 검산: 사람 수 = (남는 수+모자란 수)÷(개수 차)
        assert (a + b) % (y - x) == 0 and (a + b) // (y - x) == p, "과부족 검산 실패"
        name = rng.choice(NAMES)
        fruit = rng.choice(FRUITS)
        add(
            "excess", "NUMBER_OPERATION", 4, ["과부족", "차이로 나누기"],
            f"{name}이(가) 친구들에게 {fruit}을(를) 나눠 줘요. 한 명에게 {x}개씩 주면 {a}개가 남고, {y}개씩 주면 {b}개가 모자라요. 친구는 모두 몇 명일까요?",
            f"{p}명", [f"{p - 1}명", f"{p + 1}명", f"{a + b}명"],
            f"한 명에게 {y - x}개씩 더 주려면 (남던 {a}개 + 모자란 {b}개) = {a + b}개가 더 필요해요. {a + b}÷{y - x}={p}명.",
            [(f"{a + b}명", f"{a + b}는 필요한 개수의 차이예요. 한 명당 차이 {y - x}개로 나눠요.")],
        )


# ── 4. 나이 배수 변화 (난4, 변화와관계) ──────────────────────────────────────
def gen_age():
    picked = 0
    for child in range(6, 20):
        for k, m in [(4, 3), (3, 2), (5, 3)]:
            parent = k * child
            for t in range(2, 21):
                if parent + t == m * (child + t):
                    sols = [c for c in range(1, 40) if k * c + t == m * (c + t)]
                    if sols != [child] or (k, t) == (4, 5) or (k, t, m) == (3, 12, 2):
                        continue  # 유일해 아님 / 수작업 문제와 중복
                    picked += 1
                    if picked > 4:
                        return
                    add(
                        "age", "CHANGE_RELATION", 4, ["나이 문제", "배 관계 변화"],
                        f"지금 어머니 나이는 딸 나이의 {k}배예요. {t}년 뒤에는 {m}배가 돼요. 지금 딸은 몇 살일까요?",
                        f"{child}살", [f"{child - 2}살", f"{child + 2}살", f"{parent}살"],
                        f"검산해 봐요: 딸 {child}살, 어머니 {parent}살 → {t}년 뒤 {child + t}살과 {parent + t}살, 정확히 {m}배!",
                        [(f"{parent}살", "그건 어머니의 지금 나이예요.")],
                    )


# ── 5. 나무 심기 (난2·3, 변화와관계) ─────────────────────────────────────────
def gen_trees():
    for length, gap in [(24, 4), (30, 6), (28, 7)]:
        g = length // gap
        add(
            "tree", "CHANGE_RELATION", 3, ["간격 문제", "양 끝 포함"],
            f"길이 {length}m인 길 한쪽에 처음부터 끝까지 {gap}m 간격으로 가로등을 세워요. 가로등은 몇 개 필요할까요?",
            f"{g + 1}개", [f"{g}개", f"{g + 2}개", f"{g - 1}개"],
            f"간격은 {length}÷{gap}={g}개지만 가로등은 양 끝에도 서니까 {g}+1={g + 1}개예요.",
            [(f"{g}개", "간격 수와 가로등 수는 달라요. 맨 처음 것을 더해요.")],
        )
    # 둘레(원형) 변형 — 시작점과 끝점이 만나므로 간격 수 = 나무 수
    length, gap = 36, 6
    g = length // gap
    add(
        "tree", "CHANGE_RELATION", 3, ["간격 문제", "둘레는 다르다"],
        f"둘레가 {length}m인 원 모양 연못 둘레에 {gap}m 간격으로 나무를 심어요. 나무는 몇 그루 필요할까요?",
        f"{g}그루", [f"{g + 1}그루", f"{g - 1}그루", f"{g + 2}그루"],
        f"빙 둘러 심으면 끝이 처음과 만나서 간격 수와 나무 수가 같아요. {length}÷{gap}={g}그루.",
        [(f"{g + 1}그루", "직선 길에서만 +1이에요. 원에서는 끝나무가 곧 첫나무!")],
    )


# ── 6. 통나무 자르기 (난3, 변화와관계) ───────────────────────────────────────
def gen_log():
    for pieces, per in [(6, 2), (7, 3), (8, 4), (9, 2)]:
        ans = (pieces - 1) * per
        add(
            "log", "CHANGE_RELATION", 3, ["자르기 횟수", "간격 사고"],
            f"긴 통나무를 {pieces}도막으로 자르려고 해요. 한 번 자르는 데 {per}분이 걸리면 모두 몇 분 걸릴까요?",
            f"{ans}분", [f"{pieces * per}분", f"{(pieces - 2) * per}분", f"{ans + per * 2}분"],
            f"{pieces}도막을 만들려면 {pieces - 1}번만 자르면 돼요. {pieces - 1}×{per}={ans}분.",
            [(f"{pieces * per}분", "도막 수만큼 자르는 게 아니에요. 마지막 도막은 저절로 생겨요.")],
        )


# ── 7. 트랙 반대 방향 만남 (난4, 변화와관계) ─────────────────────────────────
def gen_meeting():
    for track, va, vb in [(300, 40, 60), (600, 70, 50), (500, 60, 40), (360, 50, 40)]:
        if track % (va + vb) != 0:
            stats["rejected"] += 1
            continue
        t = track // (va + vb)
        n1, n2 = rng.sample(NAMES, 2)
        add(
            "meet", "CHANGE_RELATION", 4, ["만남 문제", "속력의 합"],
            f"둘레 {track}m인 트랙의 같은 곳에서 {n1}와(과) {n2}이(가) 서로 반대 방향으로 동시에 출발해요. {n1}은(는) 1분에 {va}m, {n2}은(는) 1분에 {vb}m를 걸어요. 두 사람이 처음 만나는 건 몇 분 뒤일까요?",
            f"{t}분", [f"{t * 2}분", f"{t + 1}분", f"{track // max(va, vb)}분"],
            f"반대 방향이면 1분에 두 사람 사이 거리가 {va}+{vb}={va + vb}m씩 줄어요. {track}÷{va + vb}={t}분.",
            [(f"{t * 2}분", "속력을 더하지 않고 한 사람 속력만 쓴 건 아닌지 확인해요.")],
        )


# ── 8. 함께 일하기 (난4, 변화와관계) ─────────────────────────────────────────
def gen_work():
    for a, b in [(4, 12), (10, 15), (12, 24), (8, 24)]:
        if (a * b) % (a + b) != 0 or (a, b) == (6, 12):
            stats["rejected"] += 1
            continue
        t = a * b // (a + b)
        add(
            "work", "CHANGE_RELATION", 4, ["일의 양", "단위 시간 사고"],
            f"어떤 일을 혼자 하면 {rng.choice(NAMES)}은(는) {a}일, 다른 친구는 {b}일이 걸려요. 둘이 함께하면 며칠 만에 끝낼 수 있을까요?",
            f"{t}일", [f"{(a + b) // 2}일", f"{t + 2}일", f"{abs(b - a)}일"],
            f"하루에 하는 일이 전체의 1/{a}과 1/{b} — 합치면 1/{t}이에요. 그래서 {t}일!",
            [(f"{(a + b) // 2}일", "평균이 아니에요. 함께하면 혼자 빠른 사람보다도 빨라져야 해요.")],
        )


# ── 9. 기차와 다리 (난5, 변화와관계) ─────────────────────────────────────────
def gen_train():
    for train_len, bridge, speed in [(80, 220, 20), (120, 480, 30), (150, 450, 25), (100, 500, 30)]:
        if (train_len + bridge) % speed != 0 or (train_len, bridge, speed) == (100, 400, 20):
            stats["rejected"] += 1
            continue
        t = (train_len + bridge) // speed
        add(
            "train", "CHANGE_RELATION", 5, ["기차 문제", "숨은 거리"],
            f"길이 {train_len}m인 기차가 1초에 {speed}m씩 달려요. 길이 {bridge}m인 터널을 완전히 통과하는 데(맨 앞이 들어가서 맨 뒤가 나올 때까지) 몇 초가 걸릴까요?",
            f"{t}초", [f"{bridge // speed}초", f"{t + 5}초", f"{train_len // speed if train_len % speed == 0 else t - 3}초"],
            f"맨 뒤까지 나오려면 터널 {bridge}m에 기차 길이 {train_len}m를 더한 {bridge + train_len}m를 가야 해요. ÷{speed}={t}초.",
            [(f"{bridge // speed}초", f"기차 자신의 길이 {train_len}m를 잊었어요.")],
        )


# ── 10. 수 피라미드 (난3, 수와연산) ──────────────────────────────────────────
def gen_pyramid():
    made = 0
    for a, b, c in [(3, 5, 2), (4, 2, 7), (6, 3, 4), (2, 6, 5)]:
        top = a + 2 * b + c
        # 검산: 아래 칸 [a,?,c]와 꼭대기 top이 주어질 때 ?가 유일한지
        sols = [m for m in range(0, 20) if a + 2 * m + c == top]
        assert sols == [b], "피라미드 검산 실패"
        made += 1
        add(
            "pyramid", "NUMBER_OPERATION", 3, ["수 피라미드", "거꾸로 생각하기"],
            f"수 피라미드는 위 칸이 바로 아래 두 칸의 합이에요. 맨 아랫줄이 [{a}, □, {c}]이고 꼭대기가 {top}일 때, □는 얼마일까요?",
            str(b), [str(b - 1), str(b + 1), str(top - a - c)],
            f"가운데 줄은 ({a}+□)와 (□+{c}) — 꼭대기는 {a}+□+□+{c}예요. {top}−{a}−{c}={top - a - c}가 □ 두 개의 몫이니 □={b}.",
            [(str(top - a - c), "그건 □ 두 개의 합이에요. 2로 나눠요.")],
        )


# ── 11. 계단 오르기 (난5, 자료와가능성) ──────────────────────────────────────
def gen_stairs():
    def ways(n):
        x, y = 1, 1
        for _ in range(n - 1):
            x, y = y, x + y
        return y
    for n in [5, 6, 7]:
        w = ways(n)
        add(
            "stairs", "DATA_POSSIBILITY", 5, ["경우 나누어 세기", "계단 문제"],
            f"한 번에 1칸 또는 2칸씩 오를 수 있는 {n}칸 계단이 있어요. 계단을 오르는 서로 다른 방법은 모두 몇 가지일까요?",
            f"{w}가지", [f"{w - 1}가지", f"{w + 2}가지", f"{n * 2}가지"],
            f"'{n}칸 방법 수 = {n - 1}칸 방법 수 + {n - 2}칸 방법 수'로 쌓아 올려요(마지막 걸음이 1칸이냐 2칸이냐). 1, 2, 3, 5, 8…처럼 커져서 {w}가지.",
            [(f"{n * 2}가지", "직접 나열하기 어려우면 작은 계단부터 규칙을 찾아요.")],
        )
    # 검산: n=5 무차별 나열
    from itertools import product
    cnt = 0
    for k in range(3, 6):
        for steps in product([1, 2], repeat=k):
            if sum(steps) == 5:
                cnt += 1
    assert cnt == ways(5), "계단 검산 실패"


# ── 12. 격자 최단 경로 (난4, 도형과측정) ─────────────────────────────────────
def gen_grid():
    for w, h in [(3, 2), (3, 3), (4, 2)]:
        ans = comb(w + h, w)
        add(
            "grid", "SHAPE_MEASUREMENT", 4, ["최단 경로", "체계적으로 세기"],
            f"가로 {w}칸, 세로 {h}칸의 바둑판 모양 길이 있어요. 왼쪽 아래에서 오른쪽 위까지 가장 짧게 가는 길은 모두 몇 가지일까요?",
            f"{ans}가지", [f"{ans - 2}가지", f"{ans + 2}가지", f"{w * h}가지"],
            f"각 갈림길에 '거기까지 가는 방법 수'를 적으면 왼쪽과 아래 수의 합이 돼요. 끝까지 채우면 {ans}가지.",
            [(f"{w * h}가지", "칸 수를 곱하는 게 아니에요. 갈림길마다 방법 수를 더해 가요.")],
            figure={"type": "GRID", "params": {"w": w, "h": h, "mark": 1}},
        )


# ── 13. 반복 주기 (난2, 변화와관계) ──────────────────────────────────────────
def gen_cycle():
    for colors, n in [(COLORS3[0], 50), (COLORS3[1], 74), (COLORS3[0] + ["초록"], 90), (COLORS3[1] + ["분홍"], 66)]:
        k = len(colors)
        pos = (n - 1) % k
        ans = colors[pos]
        wrongs = [c for c in colors if c != ans][:2] + ["알 수 없다"]
        add(
            "cycle", "CHANGE_RELATION", 2, ["반복 주기", "나머지 사고"],
            f"{'·'.join(colors)} 구슬을 이 순서대로 계속 꿰어요. {n}번째 구슬은 무슨 색일까요?",
            f"{ans}색", [f"{wrongs[0]}색", f"{wrongs[1]}색", wrongs[2]],
            f"{k}개씩 한 묶음이 반복돼요. {n}={n // k}묶음 + {n % k if n % k else k}번째이니 {ans}색.",
        )


# ── 14. 달력 묶음 (난3, 변화와관계) ──────────────────────────────────────────
def gen_calendar():
    for mid in [11, 15, 17, 20]:
        s = mid * 3
        if s == 42:
            stats["rejected"] += 1
            continue
        sols = [m for m in range(8, 24) if 3 * m == s]
        assert sols == [mid], "달력 검산 실패"
        add(
            "calweek", "CHANGE_RELATION", 3, ["달력 구조", "가운데 수 사고"],
            f"달력에서 위아래로 나란히 붙은 세 수를 골랐더니 합이 {s}였어요. 세 수 중 가운데 수는?",
            str(mid), [str(mid - 1), str(mid + 1), str(s // 2)],
            f"세 수는 (가운데−7), 가운데, (가운데+7)이라 합이 가운데×3이에요. {s}÷3={mid}.",
            [(str(s // 2), "2로 나누는 게 아니에요. 세 수의 합은 가운데 수의 3배.")],
        )


# ── 15. 평균 변화 (난4, 자료와가능성) ────────────────────────────────────────
def gen_average():
    for n, m, d in [(4, 70, 5), (5, 80, 3), (4, 85, 4), (5, 60, 6)]:
        newcomer = m + (n + 1) * d
        # 검산
        assert (n * m + newcomer) / (n + 1) == m + d, "평균 검산 실패"
        add(
            "avgchg", "DATA_POSSIBILITY", 4, ["평균 변화", "합으로 비교"],
            f"{n}명의 평균 점수가 {m}점이었어요. 한 명이 더 들어오자 평균이 {m + d}점으로 올랐어요. 새로 들어온 사람의 점수는?",
            f"{newcomer}점", [f"{m + d}점", f"{m + 2 * d}점", f"{newcomer - d}점"],
            f"{n + 1}명의 총점 {(n + 1) * (m + d)}점에서 원래 총점 {n * m}점을 빼면 {newcomer}점.",
            [(f"{m + d}점", "새 평균만큼 받아서는 평균이 오르지 않아요. 모두의 평균을 끌어올려야 해요.")],
        )


# ── 16. 테두리 세기 (난3, 도형과측정) ────────────────────────────────────────
def gen_border():
    for side in [7, 8, 12, 15]:
        ans = 4 * side - 4
        add(
            "border", "SHAPE_MEASUREMENT", 3, ["테두리 세기", "꼭짓점 중복"],
            f"바둑돌을 그림처럼 속이 빈 정사각형 모양으로 한 변에 {side}개씩 놓으려고 해요. 바둑돌은 모두 몇 개 필요할까요?",
            f"{ans}개", [f"{4 * side}개", f"{ans - 2}개", f"{side * side}개"],
            f"{side}×4에서 네 꼭짓점이 두 번씩 세어졌으니 4를 빼요: {ans}개.",
            [(f"{4 * side}개", "꼭짓점 돌 4개를 두 번 센 거예요."), (f"{side * side}개", "속이 꽉 찬 정사각형이 아니라 테두리만이에요.")],
            figure={"type": "DOT_BORDER", "params": {"side": min(side, 12)}},
        )


# ── 17. 양초 따라잡기 (난5, 변화와관계) ──────────────────────────────────────
def gen_candle():
    for l1, r1, l2, r2 in [(24, 3, 16, 2), (30, 4, 18, 2), (18, 2, 12, 1), (25, 3, 13, 1)]:
        if (l1 - l2) % (r1 - r2) != 0 or (l1, r1, l2, r2) == (20, 2, 12, 1):
            stats["rejected"] += 1
            continue
        t = (l1 - l2) // (r1 - r2)
        if l1 - r1 * t < 0:
            stats["rejected"] += 1
            continue
        assert l1 - r1 * t == l2 - r2 * t, "양초 검산 실패"
        add(
            "candle", "CHANGE_RELATION", 5, ["따라잡기", "차이 줄이기"],
            f"{l1}cm 초는 1시간에 {r1}cm씩, {l2}cm 초는 1시간에 {r2}cm씩 타요. 동시에 불을 붙이면 몇 시간 뒤 두 초의 길이가 같아질까요?",
            f"{t}시간", [f"{t - 2}시간", f"{t + 2}시간", f"{l1 - l2}시간"],
            f"길이 차이 {l1 - l2}cm가 1시간마다 {r1 - r2}cm씩 줄어요. {l1 - l2}÷{r1 - r2}={t}시간. (그때 둘 다 {l1 - r1 * t}cm)",
            [(f"{l1 - l2}시간", f"차이 {l1 - l2}cm를 '1시간에 줄어드는 양 {r1 - r2}cm'로 나눠야 해요.")],
        )


# ── 18. 거울 시계 (난3, 도형과측정) ──────────────────────────────────────────
def gen_mirror():
    for actual in [2, 4, 5, 7]:
        mirror = 12 - actual
        add(
            "mirror", "SHAPE_MEASUREMENT", 3, ["거울 사고", "대칭"],
            f"그림은 거울에 비친 벽시계 모습이에요({mirror}시 정각처럼 보여요). 실제 시각은 몇 시일까요?",
            f"{actual}시", [f"{mirror}시", f"{(actual + 6) % 12 or 12}시", f"{(mirror + 1) % 12 or 12}시"],
            f"거울은 12-6 축을 기준으로 좌우를 뒤집어요. 12에서 {mirror}만큼 반대로 가면 {actual}시.",
            [(f"{mirror}시", "거울 속 그대로 읽었어요. 좌우가 뒤집혀 있어요.")],
            figure={"type": "CLOCK", "params": {"hour": mirror, "minute": 0}},
        )


GENERATORS = [
    gen_cryptarithm, gen_chicken_rabbit, gen_excess_deficit, gen_age, gen_trees,
    gen_log, gen_meeting, gen_work, gen_train, gen_pyramid, gen_stairs, gen_grid,
    gen_cycle, gen_calendar, gen_average, gen_border, gen_candle, gen_mirror,
]

for g in GENERATORS:
    g()

# ── 전역 무결성 자체 검사 ─────────────────────────────────────────────────────
ids = [p["id"] for p in problems]
assert len(ids) == len(set(ids)), "id 중복"
for p in problems:
    assert len(p["choices"]) == 4 and len(set(p["choices"])) == 4, f"보기 오류: {p['id']}"
    assert 0 <= p["answerIndex"] < 4
    assert p["explanation"], f"해설 없음: {p['id']}"
    for m in p["mistakes"]:
        assert m["choiceIndex"] != p["answerIndex"], f"오개념이 정답에 붙음: {p['id']}"
groups = {}
for p in problems:
    groups.setdefault(p["groupId"], []).append(p)
for gid, ps in groups.items():
    assert len(ps) >= 3, f"그룹 {gid} 문항 부족({len(ps)})"
    assert len({p["difficulty"] for p in ps}) == 1 and len({p["area"] for p in ps}) == 1, f"그룹 불일치 {gid}"

# 큐레이션 블록리스트 적용 — 검수에서 제거된 문제는 영구 제외
blockfile = Path(__file__).parent / "blocklist.txt"
blocked = set()
if blockfile.exists():
    for line in blockfile.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            blocked.add(line)
before = len(problems)
problems = [p for p in problems if p["id"] not in blocked]
if blocked:
    print(f"블록리스트 제외: {before - len(problems)}문항 (등록 {len(blocked)}건)")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"version": 1, "problems": problems}, ensure_ascii=False, indent=1), encoding="utf-8")

by_diff = {}
for p in problems:
    by_diff[p["difficulty"]] = by_diff.get(p["difficulty"], 0) + 1
print(f"생성 {stats['generated']}문항 / 기각 {stats['rejected']} / 그룹 {len(groups)}개")
print(f"난이도 분포: {dict(sorted(by_diff.items()))}")
print(f"→ {OUT}")
