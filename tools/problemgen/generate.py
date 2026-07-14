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
from math import comb, gcd
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


def _has_batchim(word):
    """단어 끝소리에 받침이 있는지. 숫자는 한국어 읽기 기준(2·4·5·9로 끝나면 받침 없음)."""
    last = str(word)[-1]
    if last.isdigit():
        return int(last) not in (2, 4, 5, 9)
    if "가" <= last <= "힣":
        return (ord(last) - 0xAC00) % 28 != 0
    return True


def _is_rieul(word):
    """끝소리 받침이 ㄹ인지(일·칠·팔). '으로/로' 판단용."""
    last = str(word)[-1]
    if last.isdigit():
        return int(last) in (1, 7, 8)
    if "가" <= last <= "힣":
        return (ord(last) - 0xAC00) % 28 == 8
    return False


def _iga(w):
    return "이" if _has_batchim(w) else "가"


def _eul(w):
    return "을" if _has_batchim(w) else "를"


def _eun(w):
    return "은" if _has_batchim(w) else "는"


def _gwa(w):
    return "과" if _has_batchim(w) else "와"


def _euro(w):
    return "으로" if (_has_batchim(w) and not _is_rieul(w)) else "로"


def _copula(w):
    """서술격 조사 '예요/이에요'를 받침에 맞춰 고른다."""
    return "이에요" if _has_batchim(w) else "예요"


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
            f"(가나)는 10×가+나, 자리를 바꾼 (나가)는 10×나+가예요. 둘을 더하면 가와 나를 각각 11번씩 더한 셈이라 11×(가+나)가 돼요. {total}÷11={s}이니 가+나={s}예요.",
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
            f"전부 닭이라고 가정해 봐요. 그러면 다리는 2×{total}={2 * total}개인데 실제는 {legs}개로 {legs - 2 * total}개 더 많아요. 닭 한 마리를 토끼로 바꿀 때마다 다리가 2개씩 늘어나니, {legs - 2 * total}÷2={rabbits}마리가 토끼예요.",
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
            f"{x}개씩 줄 때는 {a}개가 남고, {y}개씩 줄 때는 {b}개가 모자라요 — 방법을 바꾸면 필요한 {fruit}이 {a}+{b}={a + b}개 차이 나는 거예요. 한 명당 {y - x}개씩 더 주기 때문이니, 친구 수는 {a + b}÷{y - x}={p}명이에요.",
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
                        f"표를 만들어 하나씩 확인해 봐요. 딸이 {child}살이면 어머니는 {k}배인 {parent}살이에요. {t}년 뒤에는 두 사람 모두 {t}살씩 늘어 딸 {child + t}살, 어머니 {parent + t}살 — 정확히 {m}배가 되니 조건에 딱 맞아요. 답은 {child}살.",
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
            f"작은 그림부터 그려 봐요. 간격이 1개면 가로등은 2개, 간격이 2개면 3개 — 가로등은 늘 간격보다 1개 많아요. 간격은 {length}÷{gap}={g}개이니 가로등은 {g}+1={g + 1}개예요.",
            [(f"{g}개", "간격 수와 가로등 수는 달라요. 맨 처음 것을 더해요.")],
        )
    # 둘레(원형) 변형 — 시작점과 끝점이 만나므로 간격 수 = 나무 수
    length, gap = 36, 6
    g = length // gap
    add(
        "tree", "CHANGE_RELATION", 3, ["간격 문제", "둘레는 다르다"],
        f"둘레가 {length}m인 원 모양 연못 둘레에 {gap}m 간격으로 나무를 심어요. 나무는 몇 그루 필요할까요?",
        f"{g}그루", [f"{g + 1}그루", f"{g - 1}그루", f"{g + 2}그루"],
        f"직선 길에서는 나무가 간격보다 1개 많지만, 원에서는 한 바퀴 돌면 마지막 나무가 곧 첫 나무예요. 그래서 간격 수와 나무 수가 똑같아요. 간격은 {length}÷{gap}={g}개이니 나무도 {g}그루예요.",
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
            f"작게 생각해 봐요. 2도막을 내려면 1번, 3도막은 2번 — 자르는 횟수는 언제나 도막 수보다 1 작아요. {pieces}도막이면 {pieces - 1}번 잘라야 하니 {pieces - 1}×{per}={ans}분이 걸려요.",
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
            f"서로 반대로 걸으면 두 사람이 걸은 거리를 합쳐 트랙 한 바퀴 {track}m가 되는 순간 처음 만나요. 1분마다 둘이 합쳐 {va}+{vb}={va + vb}m씩 걸으니, {track}÷{va + vb}={t}분 뒤에 만나요.",
            [(f"{t * 2}분", "속력을 더하지 않고 한 사람 속력만 쓴 건 아닌지 확인해요.")],
        )


# ── 8. 함께 일하기 (난4, 변화와관계) ─────────────────────────────────────────
def gen_work():
    for a, b in [(4, 12), (10, 15), (12, 24), (8, 24)]:
        if (a * b) % (a + b) != 0 or (a, b) == (6, 12):
            stats["rejected"] += 1
            continue
        t = a * b // (a + b)
        lcm = a * b // gcd(a, b)
        add(
            "work", "CHANGE_RELATION", 4, ["일의 양", "단위 시간 사고"],
            f"어떤 일을 혼자 하면 {rng.choice(NAMES)}은(는) {a}일, 다른 친구는 {b}일이 걸려요. 둘이 함께하면 며칠 만에 끝낼 수 있을까요?",
            f"{t}일", [f"{(a + b) // 2}일", f"{t + 2}일", f"{abs(b - a)}일"],
            f"일 전체를 {lcm}칸이라고 생각해 봐요. 한 사람은 하루에 {lcm}÷{a}={lcm // a}칸, 다른 친구는 {lcm}÷{b}={lcm // b}칸을 해요. 둘이 함께면 하루에 {lcm // a}+{lcm // b}={lcm // a + lcm // b}칸이니 {lcm}÷{lcm // a + lcm // b}={t}일 만에 끝나요.",
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
            f"기차 맨 앞을 기준으로 따라가 봐요. 맨 앞이 터널 {bridge}m를 다 지나도 아직 기차 몸통이 터널 안에 있어요. 맨 뒤까지 나오려면 기차 길이 {train_len}m를 더 가야 하니 모두 {bridge}+{train_len}={bridge + train_len}m를 달려요. 1초에 {speed}m씩 가니 {bridge + train_len}÷{speed}={t}초예요.",
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
            f"규칙을 따라 아래에서 위로 쌓아 봐요. 가운데 줄은 ({a}+□)와 (□+{c})이고, 꼭대기는 그 둘의 합이라 {a}+□+□+{c}가 돼요. 그러면 □ 두 개의 합은 {top}−{a}−{c}={top - a - c}이니, □={top - a - c}÷2={b}예요.",
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
            f"작은 계단부터 세어 봐요. 1칸은 1가지, 2칸은 2가지예요. 마지막 걸음이 1칸이었는지 2칸이었는지로 나누면 '{n}칸 방법 수 = {n - 1}칸 방법 수 + {n - 2}칸 방법 수'가 돼요. 1, 2, 3, 5, 8…로 쌓아 올리면 {n}칸은 {w}가지예요.",
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
            f"어느 갈림길이든 거기 오는 길은 왼쪽에서 오거나 아래에서 오는 것뿐이에요. 그래서 각 점에 (왼쪽 점의 수)+(아래 점의 수)를 차례로 적어 가면 돼요. 출발점 쪽 가장자리를 1로 채우고 끝까지 더해 가면 도착점은 {ans}가지예요.",
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
            f"{k}개가 한 묶음으로 계속 반복되니 {n}을 {k}로 나누는 게 열쇠예요. {n}÷{k}를 하면 몫이 {n // k}이고 나머지가 {n % k}이니, 완전한 묶음 뒤 {n % k if n % k else k}번째 구슬 차례예요. 묶음의 {n % k if n % k else k}번째는 {ans}색이에요.",
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
            f"달력에서 위아래로 붙은 수는 7씩 차이 나요. 세 수를 (가운데−7), 가운데, (가운데+7)로 쓰면 −7과 +7이 서로 지워져 합이 가운데×3이 돼요. {s}÷3={mid}이니 가운데 수는 {mid}예요.",
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
            f"평균 대신 총점으로 바꿔 생각해요. 원래 {n}명의 총점은 {n}×{m}={n * m}점이고, {n + 1}명이 평균 {m + d}점이 되려면 총점이 {n + 1}×{m + d}={(n + 1) * (m + d)}점이어야 해요. 그 차이 {(n + 1) * (m + d)}−{n * m}={newcomer}점이 새로 온 사람의 점수예요.",
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
            f"네 변에 {side}개씩 있다고 {side}×4={4 * side}개로 세면 함정에 빠져요. 네 꼭짓점의 돌은 두 변에 걸쳐 있어서 두 번씩 세어졌거든요. 두 번 센 4개를 빼면 {4 * side}−4={ans}개예요.",
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
            f"두 초의 길이 차이에 집중해 봐요. 처음 차이는 {l1}−{l2}={l1 - l2}cm인데, 1시간마다 긴 초가 {r1 - r2}cm씩 더 타서 차이가 그만큼 줄어요. {l1 - l2}÷{r1 - r2}={t}시간 뒤에 차이가 0이 되고, 그때 두 초 모두 {l1 - r1 * t}cm예요.",
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
            f"거울은 좌우만 뒤집으니 12와 6의 자리는 그대로예요. 거울 속에서 {mirror}시로 보이면 실제 바늘은 12를 기준으로 반대쪽, 즉 {actual}시에 있어요. 실제 시각과 거울 시각을 더하면 12가 된다({actual}+{mirror}=12)고 기억하면 쉬워요.",
            [(f"{mirror}시", "거울 속 그대로 읽었어요. 좌우가 뒤집혀 있어요.")],
            figure={"type": "CLOCK", "params": {"hour": mirror, "minute": 0}},
        )


# ── 19. 숫자 카드로 가장 큰 수 (난1, 수와연산) ───────────────────────────────
def gen_digit_cards():
    from itertools import permutations
    for cards in [[3, 7, 5], [2, 8, 4], [6, 1, 9], [4, 7, 2]]:
        nums = [int("".join(map(str, p))) for p in permutations(cards)]
        biggest = max(nums)
        # 검산: 서로 다른 숫자라 최대는 유일, 그리고 내림차순 배열과 같아야 함
        assert nums.count(biggest) == 1, "숫자카드 최대 유일성 실패"
        desc = sorted(cards, reverse=True)
        assert biggest == int("".join(map(str, desc))), "숫자카드 검산 실패"
        smallest = int("".join(map(str, sorted(cards))))
        asgiven = int("".join(map(str, cards)))
        s = str(biggest)
        swapped = int(s[0] + s[2] + s[1])
        cardtxt = ", ".join(str(c) for c in cards)
        add(
            "cards", "NUMBER_OPERATION", 1, ["자리값", "가장 큰 수 만들기"],
            f"숫자 카드 {cardtxt} 를 한 번씩 모두 써서 세 자리 수를 만들려고 해요. 만들 수 있는 가장 큰 수는 얼마일까요?",
            str(biggest), [str(smallest), str(asgiven), str(swapped)],
            f"가장 큰 수를 만들려면 큰 숫자를 높은 자리에 놓아야 해요. 백의 자리에 {desc[0]}, 십의 자리에 {desc[1]}, 일의 자리에 {desc[2]}을(를) 놓으면 {biggest}{_copula(biggest)}.",
            [(str(smallest), "그건 가장 작은 수예요. 큰 수는 큰 숫자를 앞자리에 놓아요.")],
        )


# ── 20. 커지는·줄어드는 규칙 다음 수 (난1, 변화와관계) ← 빈칸 셀 채우기 ────────
def gen_sequence_simple():
    for seq in [[2, 5, 8, 11], [3, 7, 11, 15], [30, 26, 22, 18], [1, 4, 7, 10]]:
        diffs = [seq[i + 1] - seq[i] for i in range(len(seq) - 1)]
        assert len(set(diffs)) == 1, "등차 검산 실패"
        d = diffs[0]
        nxt = seq[-1] + d
        seqtxt = ", ".join(str(x) for x in seq)
        grow = "커지고" if d > 0 else "작아지고"
        sign = "+" if d > 0 else "−"
        add(
            "seq1", "CHANGE_RELATION", 1, ["규칙 찾기", "일정하게 커지는 수"],
            f"규칙을 찾아보세요. {seqtxt}, □ — □에 들어갈 수는 얼마일까요?",
            str(nxt), [str(nxt + d), str(seq[-1]), str(nxt + 1)],
            f"이웃한 수의 차이를 살펴봐요. 매번 {abs(d)}씩 {grow} 있어요. 그러니 {seq[-1]} 다음은 {seq[-1]}{sign}{abs(d)}={nxt}{_copula(nxt)}.",
            [(str(seq[-1]), "마지막 수를 그대로 쓰면 안 돼요. 규칙만큼 더하거나 빼야 해요.")],
        )


# ── 21. 성냥개비 정사각형 잇기 (난1, 도형과측정) ─────────────────────────────
def gen_matchsticks():
    for n in [3, 4, 5, 6]:
        matches = 4
        for _ in range(n - 1):
            matches += 3  # 오른쪽에 하나 더 붙이면 왼쪽 변은 공유 → 3개만 추가
        assert matches == 3 * n + 1, "성냥개비 검산 실패"
        add(
            "match", "SHAPE_MEASUREMENT", 1, ["변 공유", "규칙 찾기"],
            f"성냥개비로 크기가 같은 정사각형을 한 줄로 이어 붙여 {n}개 만들려고 해요. 성냥개비는 모두 몇 개 필요할까요?",
            f"{matches}개", [f"{4 * n}개", f"{3 * n}개", f"{4 * n - 1}개"],
            f"정사각형 1개는 성냥 4개가 필요해요. 오른쪽에 하나씩 더 붙일 때는 왼쪽 변을 이미 쓰고 있어서 3개만 더 있으면 돼요. 그래서 {n}개면 4+3×{n - 1}={matches}개예요.",
            [(f"{4 * n}개", "정사각형마다 4개씩 세면 이웃끼리 붙은 변을 두 번 세게 돼요.")],
        )


# ── 22. 옷 짝짓기 경우의 수 (난1, 자료와가능성) ──────────────────────────────
def gen_outfits():
    from itertools import product
    for tops, bottoms in [(["빨강", "파랑", "노랑"], ["청바지", "검정바지"]),
                          (["티셔츠", "셔츠"], ["반바지", "긴바지", "치마"]),
                          (["흰색", "회색"], ["운동화", "구두"]),
                          (["노랑", "초록", "분홍"], ["긴치마", "짧은치마", "바지"])]:
        cnt = sum(1 for _ in product(tops, bottoms))
        n = len(tops) * len(bottoms)
        assert cnt == n, "옷 짝짓기 검산 실패"
        add(
            "outfit", "DATA_POSSIBILITY", 1, ["경우의 수", "빠짐없이 짝짓기"],
            f"윗옷 {len(tops)}가지({', '.join(tops)})와 아래옷 {len(bottoms)}가지({', '.join(bottoms)})가 있어요. 윗옷과 아래옷을 하나씩 골라 입는 방법은 모두 몇 가지일까요?",
            f"{n}가지", [f"{len(tops) + len(bottoms)}가지", f"{n - 1}가지", f"{n + 1}가지"],
            f"윗옷 하나를 고를 때마다 아래옷을 {len(bottoms)}가지로 짝지을 수 있어요. 윗옷이 {len(tops)}가지니까 {len(tops)}×{len(bottoms)}={n}가지예요. 표를 그려 하나씩 짝지어도 {n}가지가 나와요.",
            [(f"{len(tops) + len(bottoms)}가지", "더하는 게 아니라 곱해요. 윗옷마다 아래옷이 다시 여러 개 있어요.")],
        )


# ── 23. 벌레먹은셈 — 빠진 숫자 찾기 (난2, 수와연산) ──────────────────────────
def gen_broken_arithmetic():
    for tens, ones, addend in [(3, 7, 25), (5, 2, 36), (4, 8, 13), (6, 4, 19)]:
        unknown = 10 * tens + ones
        result = unknown + addend
        # 검산: □∈0~9 중 (10□+ones)+addend==result 를 만족하는 것이 유일하게 tens
        sols = [d for d in range(10) if (10 * d + ones) + addend == result]
        assert sols == [tens], "벌레먹은셈 검산 실패"
        add(
            "brokensum", "NUMBER_OPERATION", 2, ["벌레먹은셈", "자리값 거꾸로"],
            f"□{ones} + {addend} = {result}{_copula(result)}. □ 안에 들어갈 숫자는 무엇일까요? (□는 한 자리 숫자)",
            str(tens), [str((tens + 1) % 10), str(result // 10), str(max(0, tens - 1))],
            f"□{ones}{_eun(ones)} {result}에서 {addend}를 뺀 수예요. {result}−{addend}={unknown}이니 십의 자리 □는 {tens}{_copula(tens)}. 일의 자리 {ones}도 딱 맞죠.",
            [(str(result // 10), "합의 십의 자리를 그대로 답하면 안 돼요. 빼서 확인해요.")],
        )


# ── 24. 경우의 수 세기 — 곱의 원리 (난2, 자료와가능성) ───────────────────────
def gen_cases():
    from itertools import product
    scenarios = [
        ("동전 3개를 동시에 던질 때 나오는 경우(앞·뒤를 구별해요)", [["앞", "뒤"]] * 3),
        ("주사위 1개와 동전 1개를 함께 던질 때 나오는 경우", [[1, 2, 3, 4, 5, 6], ["앞", "뒤"]]),
        ("두 사람이 가위바위보를 한 판 할 때 나오는 경우(누가 무엇을 냈는지 구별해요)", [["가위", "바위", "보"]] * 2),
        ("김밥 3종류와 음료 2종류 중 하나씩 고르는 경우", [["김밥1", "김밥2", "김밥3"], ["음료1", "음료2"]]),
    ]
    for desc, spaces in scenarios:
        n = 1
        for s in spaces:
            n *= len(s)
        cnt = sum(1 for _ in product(*spaces))
        assert cnt == n, "경우의 수 검산 실패"
        wrong_sum = sum(len(s) for s in spaces)
        add(
            "cases", "DATA_POSSIBILITY", 2, ["경우의 수", "곱의 원리"],
            f"{desc}는 모두 몇 가지일까요?",
            f"{n}가지", [f"{wrong_sum}가지", f"{n - 1}가지", f"{n + 2}가지"],
            f"각 단계에서 갈라지는 경우의 수를 곱해요. {' × '.join(str(len(s)) for s in spaces)} = {n}가지예요. 빠짐없이 하나씩 나열해도 {n}가지가 나와요.",
            [(f"{wrong_sum}가지", "더하는 게 아니라 곱해요. 첫 경우마다 다음 경우가 다시 갈라져요.")],
        )


# ── 25. 약속 연산 — 새 기호 규칙 적용 (난3, 수와연산) ────────────────────────
def gen_custom_op():
    rules = [
        ("★", "가★나 = 가×나 − 나", lambda a, b: a * b - b, 5, 3),
        ("◆", "가◆나 = 가×나 + 가", lambda a, b: a * b + a, 4, 6),
        ("♥", "가♥나 = 가 + 나×2", lambda a, b: a + b * 2, 3, 5),
        ("▲", "가▲나 = 가×가 − 나", lambda a, b: a * a - b, 6, 4),
    ]
    for sym, desc, fn, qa, qb in rules:
        ea, eb = 2, 3  # 예시는 질문과 다른 수로
        ev = fn(ea, eb)
        ans = fn(qa, qb)
        assert ans > 0 and ev > 0, "약속연산 검산 실패"
        add(
            "promise", "NUMBER_OPERATION", 3, ["약속 연산", "규칙 이해와 적용"],
            f"새로운 약속을 정했어요. {desc} 예를 들어 {ea}{sym}{eb} = {ev}{_copula(ev)}. 그러면 {qa}{sym}{qb}{_eun(qb)} 얼마일까요?",
            str(ans), [str(qa * qb), str(ans + qb), str(ans - 2)],
            f"약속한 규칙에 가={qa}, 나={qb}를 그대로 넣어 계산하면 {ans}{_copula(ans)}. 예시({ea}{sym}{eb}={ev})와 똑같은 방법이에요. 낯선 기호라도 정의 순서대로 따라가면 돼요.",
            [(str(qa * qb), "두 수를 곱하기만 하고 약속의 나머지 규칙을 따르지 않았어요.")],
        )


# ── 26. 계차 수열 — 차이가 커지는 규칙 (난3, 변화와관계) ─────────────────────
def gen_sequence_advanced():
    for seq in [[1, 2, 4, 7, 11], [2, 3, 5, 8, 12], [1, 3, 6, 10, 15], [3, 4, 6, 9, 13]]:
        diffs = [seq[i + 1] - seq[i] for i in range(len(seq) - 1)]
        second = [diffs[i + 1] - diffs[i] for i in range(len(diffs) - 1)]
        assert len(set(second)) == 1 and second[0] == 1, "계차 검산 실패"
        nxt_diff = diffs[-1] + 1
        nxt = seq[-1] + nxt_diff
        seqtxt = ", ".join(str(x) for x in seq)
        difftxt = ", ".join(str(x) for x in diffs)
        add(
            "seq2", "CHANGE_RELATION", 3, ["계차 수열", "차이의 규칙"],
            f"규칙을 찾아보세요. {seqtxt}, □ — □에 들어갈 수는 얼마일까요?",
            str(nxt), [str(seq[-1] + diffs[-1]), str(nxt + 1), str(seq[-1])],
            f"이웃한 수의 차이를 적어 보면 {difftxt}로, 차이가 1씩 커지고 있어요. 그러니 다음 차이는 {nxt_diff}이고, {seq[-1]}+{nxt_diff}={nxt}{_copula(nxt)}.",
            [(str(seq[-1] + diffs[-1]), "차이가 그대로가 아니라 점점 커지고 있어요. 다음 차이를 1 더 크게 잡아요.")],
        )


# ── 27. 진실과 거짓 — 한 명만 참말 (난4, 자료와가능성) ───────────────────────
def gen_true_false():
    people = ["민준", "서연", "지호"]
    # 진술: "innocent"="나는 안 깼어" / ("accuse", j)="{people[j]}가 깼어"
    configs = [
        ["innocent", ("accuse", 0), "innocent"],
        [("accuse", 1), "innocent", "innocent"],
        ["innocent", "innocent", ("accuse", 0)],
        ["innocent", ("accuse", 2), "innocent"],
    ]

    def is_true(stmt, speaker, culprit):
        if stmt == "innocent":
            return culprit != speaker
        return culprit == stmt[1]

    for cfg in configs:
        good = [c for c in range(3) if sum(is_true(st, i, c) for i, st in enumerate(cfg)) == 1]
        if len(good) != 1:  # 참말하는 사람이 정확히 한 명이 되는 범인이 유일해야 함
            stats["rejected"] += 1
            continue
        culprit = good[0]
        texts = []
        for i, st in enumerate(cfg):
            if st == "innocent":
                texts.append(f'{people[i]}: "나는 안 깼어."')
            else:
                texts.append(f'{people[i]}: "{people[st[1]]}이(가) 깼어."')
        body = " / ".join(texts)
        add(
            "truthone", "DATA_POSSIBILITY", 4, ["진실과 거짓", "경우 따져보기"],
            f"꽃병이 깨졌어요. 세 사람 중 한 명만 진실을 말하고 나머지 둘은 거짓말을 해요. {body} 꽃병을 깬 사람은 누구일까요?",
            people[culprit], [people[(culprit + 1) % 3], people[(culprit + 2) % 3], "알 수 없다"],
            f"한 사람씩 '이 사람이 범인이라면?' 하고 가정해 진술들의 참·거짓을 세어 봐요. 참말한 사람이 정확히 한 명이 되는 경우는 {people[culprit]}이(가) 범인일 때뿐이에요. 그래서 답은 {people[culprit]}{_copula(people[culprit])}.",
            [("알 수 없다", "모든 경우를 하나씩 따져 보면 답은 하나로 정해져요.")],
        )


# ── 28. 성냥개비 정삼각형 잇기 (난2, 도형과측정) ─────────────────────────────
def gen_triangles_match():
    for n in [3, 4, 5, 6]:
        matches = 3
        for _ in range(n - 1):
            matches += 2  # 위아래로 번갈아 붙이면 맞닿은 한 변을 공유 → 2개만 추가
        assert matches == 2 * n + 1, "삼각형 성냥 검산 실패"
        add(
            "tri", "SHAPE_MEASUREMENT", 2, ["변 공유", "규칙 찾기"],
            f"성냥개비로 크기가 같은 정삼각형을 한 줄로 이어 붙여 {n}개 만들려고 해요(위아래로 번갈아 붙여요). 성냥개비는 모두 몇 개 필요할까요?",
            f"{matches}개", [f"{3 * n}개", f"{2 * n}개", f"{3 * n - 1}개"],
            f"정삼각형 1개는 성냥 3개예요. 다음 삼각형을 옆에 붙일 때는 맞닿는 한 변을 이미 쓰고 있어서 2개만 더 있으면 돼요. 그래서 {n}개면 3+2×{n - 1}={matches}개예요.",
            [(f"{3 * n}개", "삼각형마다 3개씩 세면 이웃끼리 맞닿은 변을 두 번 세게 돼요.")],
        )


# ── 29. 악수(리그전) 경우의 수 (난3, 자료와가능성) ───────────────────────────
def gen_handshake():
    from itertools import combinations
    for n in [4, 5, 6, 7]:
        cnt = sum(1 for _ in combinations(range(n), 2))
        assert cnt == n * (n - 1) // 2, "악수 검산 실패"
        add(
            "shake", "DATA_POSSIBILITY", 3, ["조합", "중복 없이 세기"],
            f"모임에 {n}명이 모였어요. 모두가 서로 한 번씩 빠짐없이 악수를 하면 악수는 모두 몇 번 일어날까요?",
            f"{cnt}번", [f"{n * (n - 1)}번", f"{n * n}번", f"{n}번"],
            f"한 사람은 자기를 뺀 {n - 1}명과 악수해요. {n}명이 각각 {n - 1}번이면 {n}×{n - 1}={n * (n - 1)}번인데, 이러면 'A와 B의 악수'를 A쪽·B쪽에서 두 번 센 거예요. 그래서 2로 나눈 {cnt}번이 정답이에요.",
            [(f"{n * (n - 1)}번", "A가 B와 한 악수와 B가 A와 한 악수는 같은 한 번이에요. 2로 나눠요.")],
        )


# ── 30. 주사위 두 개 눈의 합 경우의 수 (난3, 자료와가능성) ────────────────────
def gen_dice_sum():
    from itertools import product
    for k in [5, 7, 9, 8]:
        cnt = sum(1 for a, b in product(range(1, 7), repeat=2) if a + b == k)
        unordered = sum(1 for a in range(1, 7) for b in range(a, 7) if a + b == k)
        ex_a = max(1, k - 6)
        ex_b = k - ex_a
        add(
            "dicesum", "DATA_POSSIBILITY", 3, ["경우의 수", "순서 구별하기"],
            f"주사위 2개를 동시에 던져요. 나온 두 눈의 합이 {k}{_iga(k)} 되는 경우는 모두 몇 가지일까요? (두 주사위를 구별해요)",
            f"{cnt}가지", [f"{unordered}가지", f"{cnt - 1}가지", f"{cnt + 1}가지"],
            f"작은 눈부터 빠짐없이 짝지어 적어 봐요. 두 주사위를 구별하니 (첫째 {ex_a}, 둘째 {ex_b}){_gwa(ex_b)} (첫째 {ex_b}, 둘째 {ex_a})처럼 순서만 바뀐 것도 서로 다른 경우예요. 그렇게 세면 모두 {cnt}가지예요.",
            [(f"{unordered}가지", f"순서를 구별하지 않고 세었어요. (첫째 {ex_a}, 둘째 {ex_b}){_gwa(ex_b)} (첫째 {ex_b}, 둘째 {ex_a}){_eun(ex_a)} 서로 다른 경우예요.")],
        )


# ── 31. 나머지 조건을 함께 만족하는 수 (난4, 수와연산) ───────────────────────
def gen_remainder():
    for a, ra, b, rb in [(3, 2, 4, 1), (3, 1, 5, 2), (4, 3, 6, 1), (5, 2, 7, 3)]:
        sols = [x for x in range(10, 100) if x % a == ra and x % b == rb]
        assert sols, "나머지 조건 해 없음"
        ans = sols[0]  # 가장 작은 두 자리 수 (유일)
        step = a * b // gcd(a, b)
        nxt = ans + step
        add(
            "remain", "NUMBER_OPERATION", 4, ["나머지", "조건 함께 만족하기"],
            f"어떤 수를 {a}{_euro(a)} 나누면 {ra}{_iga(ra)} 남고, {b}{_euro(b)} 나누면 {rb}{_iga(rb)} 남아요. 이런 수 중에서 가장 작은 두 자리 수는 무엇일까요?",
            str(ans), [str(nxt), str(ans + 1), str(max(10, ans - 1))],
            f"두 조건을 동시에 만족해야 해요. {b}{_euro(b)} 나눈 나머지가 {rb}인 수를 작은 것부터 적으며 {a}{_euro(a)} 나눈 나머지가 {ra}인지 확인하면, 두 자리 수 중 처음 맞는 수가 {ans}{_copula(ans)}. ({ans}{_eul(ans)} {a}{_euro(a)} 나누면 나머지가 {ra}, {b}{_euro(b)} 나누면 나머지가 {rb}{_copula(rb)})",
            [(str(nxt), "그 수도 두 조건은 맞지만, 더 작은 두 자리 수가 있어요.")],
        )


# ── 32. 연속한 다섯 수의 합 (난3, 수와연산) ──────────────────────────────────
def gen_consecutive_sum():
    for s in [35, 60, 45, 80]:
        assert s % 5 == 0 and sum(range(s // 5 - 2, s // 5 + 3)) == s, "연속합 검산 실패"
        mid = s // 5
        largest = mid + 2
        add(
            "consec", "NUMBER_OPERATION", 3, ["연속하는 수", "가운데 수로 묶기"],
            f"연속한 다섯 개의 자연수를 더했더니 {s}{_iga(s)} 되었어요. 이 다섯 수 중에서 가장 큰 수는 무엇일까요?",
            str(largest), [str(mid), str(mid + 1), str(mid + 3)],
            f"연속한 다섯 수는 가운데 수를 중심으로 −2, −1, 0, +1, +2만큼 떨어져 있어요. 다 더하면 −와 +가 서로 지워져 가운데 수의 5배가 돼요. {s}÷5={mid}{_iga(mid)} 가운데 수이고, 가장 큰 수는 {mid}+2={largest}{_copula(largest)}.",
            [(str(mid), "그건 가운데 수예요. 가장 큰 수는 가운데보다 2 커요.")],
        )


# ── 33. 비둘기집 — 같은 색 한 켤레 보장 (난5, 자료와가능성) ─────────────────
def gen_pigeonhole():
    for colors in [["빨강", "파랑", "노랑"], ["빨강", "파랑", "노랑", "초록"],
                   ["검정", "흰색"], ["빨강", "주황", "노랑", "초록", "파랑"]]:
        c = len(colors)
        ans = c + 1  # 최악의 경우 색마다 1짝(c짝)까지 다 다를 수 있으니 한 짝 더
        add(
            "pigeon", "DATA_POSSIBILITY", 5, ["비둘기집", "최악의 경우"],
            f"서랍에 {c}가지 색({', '.join(colors)}) 양말이 잔뜩 섞여 있어요. 어두워서 색이 안 보일 때, 같은 색 한 켤레(2짝)를 확실히 꺼내려면 최소 몇 짝을 꺼내야 할까요?",
            f"{ans}짝", [f"{c}짝", f"{c * 2}짝", f"{ans + 1}짝"],
            f"운이 가장 나쁠 때를 생각해요. {c}짝을 꺼냈는데 공교롭게 색이 모두 다를 수도 있어요({c}가지니까). 하지만 한 짝만 더 꺼내면({ans}짝) 반드시 이미 나온 색과 겹쳐 한 켤레가 완성돼요. 그래서 {ans}짝이에요.",
            [(f"{c}짝", f"{c}짝이면 운 나쁘게 색이 다 다를 수 있어요. 한 짝을 더 꺼내야 확실해요.")],
        )


# ── 34. 색칠한 정육면체 자르기 (난5, 도형과측정) ─────────────────────────────
def gen_painted_cube():
    from itertools import product

    def count_faces(n, k):
        return sum(
            1 for x, y, z in product(range(n), repeat=3)
            if sum(1 for v in (x, y, z) if v in (0, n - 1)) == k
        )

    for n, k, label in [(3, 2, "정확히 두 면만 색칠된"), (4, 1, "정확히 한 면만 색칠된"),
                        (5, 2, "정확히 두 면만 색칠된"), (4, 0, "어느 면도 색칠되지 않은")]:
        ans = count_faces(n, k)
        if k == 2:
            assert ans == 12 * (n - 2), "색칠정육면체 검산 실패"
            expl = f"두 면이 칠해진 조각은 정육면체의 '모서리'에 있어요. 꼭짓점(세 면) 조각을 빼면 모서리마다 {n - 2}개씩, 모서리는 12개예요. 12×{n - 2}={ans}개예요."
        elif k == 1:
            assert ans == 6 * (n - 2) ** 2, "색칠정육면체 검산 실패"
            expl = f"한 면만 칠해진 조각은 각 면 안쪽에 모여 있어요. 한 면에 {n - 2}×{n - 2}={(n - 2) ** 2}개, 면은 6개예요. 6×{(n - 2) ** 2}={ans}개예요."
        else:
            assert ans == (n - 2) ** 3, "색칠정육면체 검산 실패"
            expl = f"어느 면도 안 칠해진 조각은 속에 숨은 덩어리예요. {n - 2}×{n - 2}×{n - 2}={ans}개예요."
        add(
            "cube", "SHAPE_MEASUREMENT", 5, ["쌓기나무", "공간 추론"],
            f"한 모서리가 {n}칸인 정육면체의 겉면을 모두 색칠한 뒤 1칸짜리 작은 정육면체로 잘랐어요. {label} 작은 정육면체는 몇 개일까요?",
            f"{ans}개", [f"{ans + 6}개", f"{n ** 3}개", f"{max(1, ans - 4)}개"],
            expl,
            [(f"{n ** 3}개", "전체 조각 수가 아니라, 조건에 맞는 조각만 세어야 해요.")],
        )


# ── 35. 약수의 개수 (난4, 수와연산) ─────────────────────────────────────────
def gen_divisor_count():
    for num in [36, 48, 60, 72]:
        divisors = [d for d in range(1, num + 1) if num % d == 0]
        ans = len(divisors)
        add(
            "divcount", "NUMBER_OPERATION", 4, ["약수", "짝지어 세기"],
            f"{num}의 약수는 모두 몇 개일까요?",
            f"{ans}개", [f"{ans - 2}개", f"{ans + 2}개", f"{ans + 1}개"],
            f"약수를 '작은 수 × 큰 수'로 짝지어 빠짐없이 찾아요. 1부터 순서대로 {num}{_eul(num)} 나누어떨어지게 하는 수를 적으면 {', '.join(map(str, divisors))} — 모두 {ans}개예요.",
            [(f"{ans + 1}개", "약수를 하나 빠뜨리거나 중복해 세지 않았는지 짝지어 확인해요.")],
        )


# ── 36. 두 자리 수 추리 — 두 조건 함께 (난5, 수와연산) ───────────────────────
def gen_number_riddle():
    for s, d in [(12, 2), (9, 3), (14, 2), (7, 3)]:
        sols = [10 * t + o for t in range(1, 10) for o in range(0, 10) if t + o == s and t - o == d]
        assert len(sols) == 1, "수 추리 유일성 실패"
        ans = sols[0]
        tens, ones = ans // 10, ans % 10
        reversed_num = 10 * ones + tens
        add(
            "riddle", "NUMBER_OPERATION", 5, ["연립 추론", "자리값"],
            f"어떤 두 자리 수가 있어요. 십의 자리 숫자와 일의 자리 숫자를 더하면 {s}, 그리고 십의 자리가 일의 자리보다 {d} 커요. 이 수는 무엇일까요?",
            str(ans), [str(reversed_num), str(ans + 1), str(ans - 1)],
            f"두 조건을 함께 써요. (십의 자리)+(일의 자리)={s}, (십의 자리)−(일의 자리)={d}. 두 식을 더하면 일의 자리끼리 지워져 십의 자리가 두 배가 되니, ({s}+{d})÷2={tens}{_iga(tens)} 십의 자리예요. 일의 자리는 {s}−{tens}={ones}이니 답은 {ans}{_copula(ans)}.",
            [(str(reversed_num), "십의 자리와 일의 자리를 바꿔 썼어요. 십의 자리가 더 큰 수예요.")],
        )


# ── 37. 시곗바늘 각도 (난4, 도형과측정) ─────────────────────────────────────
def gen_clock_angle():
    for h in [3, 5, 2, 4]:
        ans = 30 * h  # 한 칸 30도, h≤6이라 작은 쪽 각도 = 30h
        assert ans == min(30 * h, 360 - 30 * h), "시계 각도 검산 실패"
        add(
            "clockang", "SHAPE_MEASUREMENT", 4, ["각도", "시계 눈금"],
            f"시계가 {h}시 정각을 가리켜요. 시침과 분침이 이루는 작은 쪽 각도는 몇 도일까요?",
            f"{ans}도", [f"{ans + 30}도", f"{max(0, ans - 30)}도", f"{ans + 60}도"],
            f"시계 한 바퀴는 360도이고 숫자 칸은 12개니, 한 칸은 360÷12=30도예요. {h}시 정각이면 시침과 분침이 {h}칸 떨어져 있으니 {h}×30={ans}도예요.",
            [(f"{ans + 30}도", "한 칸이 30도예요. 떨어진 칸 수를 정확히 세었는지 확인해요.")],
            figure={"type": "CLOCK", "params": {"hour": h, "minute": 0}},
        )


# ── 38. 직사각형 개수 세기 (난4, 도형과측정) ────────────────────────────────
def gen_rectangle_count():
    for w, h in [(2, 2), (3, 2), (3, 3), (4, 2)]:
        ans = comb(w + 1, 2) * comb(h + 1, 2)
        add(
            "rectcount", "SHAPE_MEASUREMENT", 4, ["직사각형 세기", "체계적으로 세기"],
            f"가로 {w}칸, 세로 {h}칸으로 나뉜 직사각형 격자가 있어요. 이 격자 안에서 찾을 수 있는 크고 작은 직사각형은 모두 몇 개일까요?",
            f"{ans}개", [f"{w * h}개", f"{ans - 3}개", f"{ans + 3}개"],
            f"직사각형은 세로선 2개와 가로선 2개를 고르면 하나 정해져요. 세로선 {w + 1}개 중 2개 → {comb(w + 1, 2)}가지, 가로선 {h + 1}개 중 2개 → {comb(h + 1, 2)}가지. 곱하면 {comb(w + 1, 2)}×{comb(h + 1, 2)}={ans}개예요.",
            [(f"{w * h}개", "1칸짜리만 센 게 아니라, 여러 칸을 합친 큰 직사각형도 모두 세요.")],
            figure={"type": "GRID", "params": {"w": w, "h": h}},
        )


# ── 39. 등비수열 다음 수 (난4, 변화와관계) ──────────────────────────────────
def gen_geometric_seq():
    for seq in [[2, 6, 18, 54], [1, 3, 9, 27], [3, 6, 12, 24], [1, 4, 16, 64]]:
        ratios = [seq[i + 1] // seq[i] for i in range(len(seq) - 1)]
        assert len(set(ratios)) == 1 and all(seq[i] * ratios[0] == seq[i + 1] for i in range(len(seq) - 1)), "등비 검산 실패"
        r = ratios[0]
        nxt = seq[-1] * r
        seqtxt = ", ".join(str(x) for x in seq)
        add(
            "geoseq", "CHANGE_RELATION", 4, ["등비 규칙", "곱해지는 수"],
            f"규칙을 찾아보세요. {seqtxt}, □ — □에 들어갈 수는 얼마일까요?",
            str(nxt), [str(seq[-1] + (seq[-1] - seq[-2])), str(nxt + r), str(nxt + seq[-1])],
            f"이웃한 수가 몇 배로 커지는지 봐요. {seq[1]}÷{seq[0]}={r}, {seq[2]}÷{seq[1]}={r} — 매번 {r}배예요. 그러니 {seq[-1]} 다음은 {seq[-1]}×{r}={nxt}{_copula(nxt)}.",
            [(str(seq[-1] + (seq[-1] - seq[-2])), "일정하게 더해지는 게 아니라 일정하게 곱해지고 있어요(등비).")],
        )


# ── 40. 불변량 — 합의 홀짝 보존 (난7, 자료와가능성) ─────────────────────────
def gen_parity_invariant():
    for n in [10, 7, 8, 5]:
        total = n * (n + 1) // 2
        parity = "홀수" if total % 2 == 1 else "짝수"
        other = "짝수" if total % 2 == 1 else "홀수"
        # 검산: 임의의 지우기 순서를 여러 번 시뮬레이션 → 마지막 수의 홀짝이 항상 합의 홀짝과 같음
        sim = random.Random(n)
        for _ in range(30):
            nums = list(range(1, n + 1))
            while len(nums) > 1:
                i, j = sim.sample(range(len(nums)), 2)
                a, b = nums[i], nums[j]
                for idx in sorted((i, j), reverse=True):
                    nums.pop(idx)
                nums.append(abs(a - b))
            assert nums[0] % 2 == total % 2, "불변량 검산 실패"
        add(
            "parity", "DATA_POSSIBILITY", 7, ["불변량", "홀짝 보존"],
            f"칠판에 1부터 {n}까지의 수가 적혀 있어요. 매번 두 수를 지우고 대신 두 수의 차를 적어요. 이걸 계속 반복하면 마지막에 수 하나만 남아요. 이 수는 홀수일까요, 짝수일까요?",
            parity, [other, "지우는 순서에 따라 달라져요", "항상 0이에요"],
            f"두 수 a, b를 지우고 |a−b|를 적으면 전체 합은 (a+b)−|a−b|, 즉 작은 수의 2배만큼 줄어요 — 항상 짝수만큼! 그래서 '전체 합의 홀짝'은 절대 변하지 않아요(불변량). 1부터 {n}까지의 합은 {total}({parity})이니 마지막 한 수도 {parity}예요.",
            [("지우는 순서에 따라 달라져요", "신기하게도 순서와 상관없이 항상 같아요 — 처음 합의 홀짝으로 정해지는 불변량이에요.")],
        )


# ── 41. 포함배제 — 둘 다 아닌 수 (난6, 수와연산) ─────────────────────────────
def gen_inclusion_exclusion():
    for total_n, a, b in [(100, 3, 4), (100, 2, 5), (60, 4, 6), (50, 3, 5)]:
        lcm = a * b // gcd(a, b)
        cnt_a, cnt_b, cnt_lcm = total_n // a, total_n // b, total_n // lcm
        ans = total_n - cnt_a - cnt_b + cnt_lcm
        brute = sum(1 for x in range(1, total_n + 1) if x % a != 0 and x % b != 0)
        assert brute == ans, "포함배제 검산 실패"
        add(
            "incexc", "NUMBER_OPERATION", 6, ["포함배제", "중복 빼기"],
            f"1부터 {total_n}까지의 자연수 중에서 {a}{_euro(a)}도 {b}{_euro(b)}도 나누어떨어지지 않는 수는 모두 몇 개일까요?",
            f"{ans}개", [f"{total_n - cnt_a - cnt_b}개", f"{cnt_a + cnt_b}개", f"{ans + 2}개"],
            f"먼저 {a}의 배수 {cnt_a}개와 {b}의 배수 {cnt_b}개를 빼요. 그런데 {lcm}의 배수({cnt_lcm}개)는 양쪽에서 두 번 빠졌으니 한 번 도로 더해요. {total_n}−{cnt_a}−{cnt_b}+{cnt_lcm}={ans}개예요.",
            [(f"{total_n - cnt_a - cnt_b}개", f"{lcm}의 배수를 두 번 뺐어요 — 한 번 도로 더해야 해요(포함배제).")],
        )


# ── 42. 님 게임 — 배수 남기기 필승 (난7, 변화와관계) ─────────────────────────
def gen_nim():
    for total_stones, k in [(10, 3), (18, 4), (22, 5), (23, 4)]:
        win = [False] * (total_stones + 1)
        for s in range(1, total_stones + 1):
            win[s] = any(not win[s - t] for t in range(1, min(k, s) + 1))
        ans = total_stones % (k + 1)
        assert win[total_stones] and ans != 0 and not win[total_stones - ans], "님게임 검산 실패"
        add(
            "nim", "CHANGE_RELATION", 7, ["필승 전략", "배수 남기기"],
            f"바둑돌 {total_stones}개가 있어요. 두 사람이 번갈아 한 번에 1개~{k}개까지 가져가고, 마지막 돌을 가져가는 사람이 이겨요. 먼저 시작하는 사람이 반드시 이기려면 처음에 몇 개를 가져가야 할까요?",
            f"{ans}개", [f"{k}개", f"{ans - 1}개", f"{ans + 2}개"],
            f"핵심은 상대에게 '{k + 1}의 배수'를 남기는 거예요. 그러면 상대가 1~{k}개 중 몇 개를 가져가든 내가 합쳐서 {k + 1}개를 맞춰 다시 {k + 1}의 배수를 남길 수 있어요. {total_stones}÷{k + 1}의 나머지가 {ans}이니, 처음에 {ans}개를 가져가 {total_stones - ans}개({k + 1}의 배수)를 남기면 반드시 이겨요.",
            [(f"{k}개", "무작정 최대로 가져가면 안 돼요. 상대에게 '배수'를 남기는 게 핵심이에요.")],
        )


# ── 43. 정다각형 한 내각 (난4, 도형과측정) ──────────────────────────────────
def gen_polygon_angle():
    for n in [5, 6, 8, 10]:
        total = (n - 2) * 180
        assert total % n == 0
        ans = total // n
        add(
            "polyang", "SHAPE_MEASUREMENT", 4, ["다각형 내각", "정다각형"],
            f"정{n}각형의 한 내각의 크기는 몇 도일까요?",
            f"{ans}도", [f"{360 // n}도", f"{total}도", f"{180 - ans}도"],
            f"{n}각형의 내각의 합은 ({n}−2)×180={total}도예요. 정다각형은 내각이 모두 같으니 {n}{_euro(n)} 나눠요. {total}÷{n}={ans}도예요.",
            [(f"{360 // n}도", "그건 한 외각이에요. 내각은 180에서 외각을 뺀 값이에요.")],
            figure={"type": "POLYGON", "params": {"n": n}},
        )


# ── 44. 정다각형 대각선 개수 (난5, 도형과측정) ──────────────────────────────
def gen_polygon_diagonals():
    for n in [5, 6, 8, 10]:
        ans = n * (n - 3) // 2
        add(
            "polydiag", "SHAPE_MEASUREMENT", 5, ["대각선", "중복 없이 세기"],
            f"정{n}각형에 그을 수 있는 대각선은 모두 몇 개일까요?",
            f"{ans}개", [f"{n * (n - 3)}개", f"{n - 3}개", f"{n * (n - 1) // 2}개"],
            f"한 꼭짓점에서는 자기 자신과 양옆 두 꼭짓점(변)을 뺀 {n}−3={n - 3}개로 대각선을 그어요. 꼭짓점이 {n}개니 {n}×{n - 3}인데, 대각선 하나를 양쪽에서 두 번 셌으니 2로 나눠요. {n}×{n - 3}÷2={ans}개예요.",
            [(f"{n * (n - 3)}개", "대각선 하나를 양쪽 꼭짓점에서 두 번 셌어요. 2로 나눠요.")],
            figure={"type": "POLYGON", "params": {"n": n, "diagonals": 1}},
        )


# ── 45. 시곗바늘 각도 — 분까지 (난5, 도형과측정) ────────────────────────────
def gen_clock_minutes():
    for h, m in [(3, 30), (5, 30), (2, 30), (1, 30)]:
        hour_pos = 30 * h + m // 2
        diff = abs(hour_pos - 6 * m)
        ans = min(diff, 360 - diff)
        add(
            "clockmin", "SHAPE_MEASUREMENT", 5, ["각도", "시침의 이동"],
            f"{h}시 {m}분에 시침과 분침이 이루는 작은 쪽 각도는 몇 도일까요?",
            f"{ans}도", [f"{ans + 15}도", f"{ans + 30}도", f"{ans + 45}도"],
            f"분침은 {m}분에 숫자 6, 즉 180도 위치예요. 시침은 {h}시에서 {m}분이 더 지나 {30 * h}+{m // 2}={hour_pos}도에 있어요. 두 위치의 차 |{hour_pos}−180|={ans}도가 사이 각이에요.",
            [(f"{ans + 15}도", "분침이 움직인 만큼 시침도 조금 움직였다는 걸 빠뜨리지 않았는지 확인해요.")],
            figure={"type": "CLOCK", "params": {"hour": h, "minute": m}},
        )


# ── 46. 둘레 고정, 넓이 최대 (난5, 도형과측정) ──────────────────────────────
def gen_rect_area_max():
    for p in [20, 24, 16, 28]:
        half = p // 2
        best = max(a * (half - a) for a in range(1, half))
        assert p % 4 == 0 and best == (p // 4) ** 2
        side = p // 4
        add(
            "areamax", "SHAPE_MEASUREMENT", 5, ["둘레와 넓이", "합이 같을 때 곱 최대"],
            f"둘레가 {p}cm인 직사각형 중에서 넓이가 가장 클 때, 그 넓이는 몇 ㎠일까요? (가로·세로는 자연수)",
            f"{best}㎠", [f"{half}㎠", f"{best + side}㎠", f"{best - side}㎠"],
            f"둘레가 {p}면 가로+세로={p}÷2={half}{_euro(half)} 고정돼요. 두 수의 합이 일정할 때는 두 수가 같을수록 곱(넓이)이 커져요. 가로=세로={half}÷2={side}일 때 최대라, 넓이는 {side}×{side}={best}㎠예요.",
            [(f"{half}㎠", "가로+세로 값이 아니라 가로×세로(넓이)를 구해야 해요.")],
        )


# ── 47. 직육면체 겉넓이 (난6, 도형과측정) ───────────────────────────────────
def gen_cube_surface():
    for a, b, c in [(2, 3, 4), (3, 3, 3), (2, 2, 5), (1, 3, 4)]:
        ans = 2 * (a * b + b * c + a * c)
        volume = a * b * c
        add(
            "cubesurf", "SHAPE_MEASUREMENT", 6, ["겉넓이", "마주 보는 세 쌍"],
            f"1cm짜리 작은 정육면체를 빈틈없이 쌓아 가로 {a}칸, 세로 {b}칸, 높이 {c}칸인 직육면체를 만들었어요. 이 직육면체의 겉넓이는 몇 ㎠일까요?",
            f"{ans}㎠", [f"{volume}㎠", f"{a * b + b * c + a * c}㎠", f"{ans + 4}㎠"],
            f"직육면체는 마주 보는 면이 세 쌍이에요. 세 종류 면의 넓이는 {a}×{b}={a * b}, {b}×{c}={b * c}, {a}×{c}={a * c}. 각각 두 개씩이니 2×({a * b}+{b * c}+{a * c})={ans}㎠예요.",
            [(f"{volume}㎠", "그건 부피(쌓은 정육면체 개수)예요. 겉넓이는 바깥 면들의 넓이 합이에요.")],
        )


# ── 48. 정다각형 한 외각 (난4, 도형과측정) ──────────────────────────────────
def gen_polygon_exterior():
    for n in [5, 6, 8, 10]:
        assert 360 % n == 0
        ans = 360 // n
        add(
            "polyext", "SHAPE_MEASUREMENT", 4, ["외각", "정다각형"],
            f"정{n}각형의 한 외각의 크기는 몇 도일까요?",
            f"{ans}도", [f"{(n - 2) * 180 // n}도", "360도", f"{ans * 2}도"],
            f"정다각형의 외각을 모두 더하면 어떤 다각형이든 360도예요. 정{n}각형은 외각이 모두 같으니 360÷{n}={ans}도예요.",
            [(f"{(n - 2) * 180 // n}도", "그건 한 내각이에요. 외각은 360을 꼭짓점 수로 나눈 값이에요.")],
            figure={"type": "POLYGON", "params": {"n": n}},
        )


# ── 49. 쌓기나무 개수 세기 (난5, 도형과측정) — 그림 필수 ─────────────────────
def gen_cube_stack():
    for w, d, heights in [
        (3, 1, [1, 2, 3]),
        (2, 2, [1, 1, 1, 2]),
        (2, 3, [1, 1, 1, 1, 1, 1]),
        (3, 2, [1, 2, 1, 2, 1, 2]),
    ]:
        assert len(heights) == w * d
        ans = sum(heights)
        add(
            "cubestack", "SHAPE_MEASUREMENT", 5, ["쌓기나무", "공간 지각"],
            "그림처럼 쌓은 쌓기나무는 모두 몇 개일까요? (보이지 않는 뒤·아래 나무도 세어요)",
            f"{ans}개", [f"{ans - 1}개", f"{ans + 1}개", f"{max(1, ans - 2)}개"],
            f"기둥마다 몇 층인지 세어 모두 더해요. 각 칸의 높이를 합하면 {ans}개예요. 앞 나무에 가려 안 보여도 아래는 채워져 있다고 봐요.",
            [(f"{max(1, ans - 2)}개", "앞이나 위에 가려 안 보이는 나무도 빠짐없이 세어요.")],
            figure={"type": "CUBE_STACK", "params": {"w": w, "d": d}, "heights": heights},
        )


# ── 50. 격자 넓이 (도형과측정) — 그림 필수(GRID_POLYGON) ──────────────────────
def _shoelace2(pts):
    """다각형 넓이의 2배(정수)를 신발끈 공식으로. 좌표 오타 검산용."""
    s = 0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return abs(s)


def _grid_fig(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    flat = []
    for x, y in pts:
        flat += [x, y]
    return {"type": "GRID_POLYGON", "params": {"cols": max(xs), "rows": max(ys), "n": len(pts)}, "heights": flat}


def gen_grid_area():
    # (a) 난3·무료 — 직각 다각형(ㄱ자·계단): 칸 세기/직사각형 빼기
    for pts, detail in [
        ([(0, 0), (4, 0), (4, 2), (2, 2), (2, 4), (0, 4)], "큰 4×4 정사각형(16㎠)에서 빈 2×2(4㎠)를 빼요"),
        ([(0, 0), (5, 0), (5, 2), (3, 2), (3, 4), (0, 4)], "큰 5×4 직사각형(20㎠)에서 빈 2×2(4㎠)를 빼요"),
        ([(0, 0), (3, 0), (3, 3), (2, 3), (2, 5), (0, 5)], "너비 3칸 부분(3×3=9㎠)과 너비 2칸 부분(2×2=4㎠)으로 나눠 더해요"),
    ]:
        assert _shoelace2(pts) % 2 == 0
        area = _shoelace2(pts) // 2
        add(
            "gridrect", "SHAPE_MEASUREMENT", 3, ["넓이", "모눈"],
            "색칠한 도형의 넓이는 몇 ㎠일까요? (모눈 한 칸은 1㎠예요)",
            f"{area}㎠", [f"{area + 2}㎠", f"{area - 2}㎠", f"{area + 4}㎠"],
            f"칸을 세거나 직사각형으로 나눠 구해요. {detail} → {area}㎠.",
            figure=_grid_fig(pts),
        )
    # (b) 난4 — 직각삼각형: 밑변×높이÷2
    for b, h, pts in [
        (5, 4, [(0, 4), (5, 4), (0, 0)]),
        (6, 3, [(0, 3), (6, 3), (0, 0)]),
        (4, 4, [(4, 4), (4, 0), (0, 4)]),
        (6, 4, [(0, 4), (6, 4), (0, 0)]),
    ]:
        assert _shoelace2(pts) == b * h and (b * h) % 2 == 0
        area = b * h // 2
        add(
            "gridtri", "SHAPE_MEASUREMENT", 4, ["삼각형 넓이", "모눈"],
            "색칠한 삼각형의 넓이는 몇 ㎠일까요? (모눈 한 칸은 1㎠예요)",
            f"{area}㎠", [f"{b * h}㎠", f"{area + 2}㎠", f"{area - 2}㎠"],
            f"밑변 {b}칸, 높이 {h}칸인 직각삼각형이에요. 삼각형 넓이 = 밑변×높이÷2 = {b}×{h}÷2 = {area}㎠.",
            [(f"{b * h}㎠", "삼각형은 직사각형의 절반 — 밑변×높이를 꼭 2로 나눠요.")],
            figure=_grid_fig(pts),
        )
    # (c) 난5 — 평행사변형: 밑변×수직높이(기울어져도 동일)
    for base, height, pts in [
        (4, 4, [(0, 4), (4, 4), (6, 0), (2, 0)]),
        (5, 3, [(0, 3), (5, 3), (6, 0), (1, 0)]),
        (3, 4, [(1, 4), (4, 4), (6, 0), (3, 0)]),
        (4, 3, [(0, 3), (4, 3), (6, 0), (2, 0)]),
    ]:
        assert _shoelace2(pts) == 2 * base * height
        area = base * height
        xs = [p[0] for p in pts]
        boxw = max(xs) - min(xs)
        add(
            "gridpara", "SHAPE_MEASUREMENT", 5, ["평행사변형 넓이", "모눈"],
            "색칠한 평행사변형의 넓이는 몇 ㎠일까요? (모눈 한 칸은 1㎠예요)",
            f"{area}㎠", [f"{boxw * height}㎠", f"{area + 3}㎠", f"{area - 2}㎠"],
            f"평행사변형은 기울어져 있어도 넓이 = 밑변×높이예요. 밑변 {base}칸, 높이(수직) {height}칸 → {base}×{height} = {area}㎠.",
            [(f"{boxw * height}㎠", f"둘러싼 직사각형({boxw}×{height})이 아니라, 밑변×수직높이로 구해요.")],
            figure=_grid_fig(pts),
        )
    # (d) 난5 — 사다리꼴: (윗변+아랫변)×높이÷2
    # a=윗변(화면 위·작은 y쪽), bb=아랫변 — 렌더가 y-down이라 그림과 일치하도록 맞춤
    for a, bb, h, pts in [
        (4, 6, 3, [(0, 3), (6, 3), (5, 0), (1, 0)]),
        (2, 4, 4, [(0, 4), (4, 4), (3, 0), (1, 0)]),
        (2, 5, 4, [(0, 4), (5, 4), (4, 0), (2, 0)]),
    ]:
        assert _shoelace2(pts) == (a + bb) * h
        area = (a + bb) * h // 2
        add(
            "gridtrap", "SHAPE_MEASUREMENT", 5, ["사다리꼴 넓이", "모눈"],
            "색칠한 사다리꼴의 넓이는 몇 ㎠일까요? (모눈 한 칸은 1㎠예요)",
            f"{area}㎠", [f"{(a + bb) * h}㎠", f"{area + 3}㎠", f"{area - 2}㎠"],
            f"사다리꼴 넓이 = (윗변+아랫변)×높이÷2 = ({a}+{bb})×{h}÷2 = {area}㎠.",
            [(f"{(a + bb) * h}㎠", "(윗변+아랫변)×높이 다음에 꼭 ÷2 하세요.")],
            figure=_grid_fig(pts),
        )
    # (e) 난6 — 기울어진 도형: 둘러싼 직사각형 − 모서리 삼각형
    for pts in [
        [(2, 0), (5, 2), (3, 5), (0, 3)],
        [(1, 0), (4, 1), (3, 4), (0, 3)],
        [(3, 0), (5, 3), (2, 5), (0, 2)],
        [(2, 0), (4, 2), (2, 4), (0, 2)],
    ]:
        assert _shoelace2(pts) % 2 == 0
        area = _shoelace2(pts) // 2
        cols = max(p[0] for p in pts)
        rows = max(p[1] for p in pts)
        box = cols * rows
        tri = box - area
        add(
            "gridtilt", "SHAPE_MEASUREMENT", 6, ["넓이", "둘러싸기", "모눈"],
            "격자 위 기울어진 도형이에요. 색칠한 부분의 넓이는 몇 ㎠일까요? (모눈 한 칸은 1㎠예요)",
            f"{area}㎠", [f"{box}㎠", f"{area + 2}㎠", f"{area - 2}㎠"],
            f"칸에 딱 안 맞는 기울어진 도형은 '둘러싸기'로 풀어요. 감싸는 직사각형 {cols}×{rows}={box}㎠에서, 남는 네 모서리 직각삼각형 넓이 합 {tri}㎠를 빼요. {box}−{tri}={area}㎠.",
            [(f"{box}㎠", "둘러싼 직사각형에서 모서리 삼각형들을 빼야 도형의 넓이예요.")],
            figure=_grid_fig(pts),
        )


# ── 51. 삼각형 개수 세기 (도형과측정) — 그림 필수(TRIANGLE_FAN) ────────────────
def gen_shape_count():
    # family를 난이도별로 분리(id는 family+idx라 한 family가 여러 난이도에 걸치면 id가 충돌)
    for diff, ks, fam in [(4, [2, 3, 4], "trianglefan"), (6, [5, 6, 7], "trianglefanx")]:
        for k in ks:
            lines = k + 2                       # 밑변으로 가는 선(양옆 2 + 내부 k)
            ans = lines * (lines - 1) // 2       # 선 2개를 고를 때마다 삼각형 1개
            small = k + 1                        # 가장 작은 삼각형 개수
            add(
                fam, "SHAPE_MEASUREMENT", diff, ["삼각형 개수", "체계적 세기"],
                "그림에서 찾을 수 있는 삼각형은 모두 몇 개일까요? (작은 삼각형을 여러 개 합친 큰 삼각형도 세어요)",
                f"{ans}개", [f"{small}개", f"{ans - 2}개", f"{ans + 3}개"],
                f"꼭짓점에서 밑변으로 그은 선이 모두 {lines}개예요. 이 선들 중 2개를 고르면 그 사이에 삼각형이 하나씩 생겨요. "
                f"{lines}개에서 2개 고르기 = {lines}×{lines - 1}÷2 = {ans}개. (가장 작은 삼각형 {small}개부터 둘씩·셋씩 합친 것까지 빠짐없이.)",
                [(f"{small}개", "가장 작은 삼각형만 세지 말고, 여러 개를 합친 큰 삼각형도 빠짐없이 세어요.")],
                figure={"type": "TRIANGLE_FAN", "params": {"cevians": k}},
            )


# ── 52. 주사위(정육면체) 전개도 마주 보는 면 (도형과측정) — 그림 필수(CUBE_NET) ──
def _fold_normals(cells):
    """전개도 6칸을 실제로 접어 각 면의 바깥 법선벡터를 구한다(BFS 굴리기).
    유효한 전개도면 6개 법선이 ±x,±y,±z로 모두 다르다. cells: iterable of (c,r)."""
    from collections import deque
    cellset = set(cells)

    def neg(v):
        return (-v[0], -v[1], -v[2])

    start = next(iter(cellset))
    frames = {start: ((0, 0, 1), (1, 0, 0), (0, 1, 0))}  # (법선 n, 2D오른쪽→3D, 2D아래→3D)
    dq = deque([start])
    while dq:
        c, r = dq.popleft()
        n, er, ed = frames[(c, r)]
        for dc, dr, kind in [(1, 0, "R"), (-1, 0, "L"), (0, 1, "D"), (0, -1, "U")]:
            nb = (c + dc, r + dr)
            if nb in cellset and nb not in frames:
                if kind == "R":
                    frames[nb] = (er, neg(n), ed)
                elif kind == "L":
                    frames[nb] = (neg(er), n, ed)
                elif kind == "D":
                    frames[nb] = (ed, er, neg(n))
                else:
                    frames[nb] = (neg(ed), er, n)
                dq.append(nb)
    return {cell: f[0] for cell, f in frames.items()}


def gen_cube_net():
    # 후보 전개도 — 접기 시뮬로 유효성(법선 6개 모두 다름) 검증 후 사용
    candidates = [
        [(1, 0), (0, 1), (1, 1), (2, 1), (3, 1), (1, 2)],   # 십자
        [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (3, 2)],   # 계단(지그재그)
        [(0, 0), (0, 1), (1, 1), (2, 1), (3, 1), (3, 2)],   # 1-4-1 어긋난 T
        [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2), (1, 3)],   # 세로 십자 변형
    ]
    idx = 0
    for layout in candidates:
        normals = _fold_normals(layout)
        if len(set(normals.values())) != 6:
            continue                                        # 유효한 전개도가 아니면 건너뜀
        idx += 1
        vals = {cell: i + 1 for i, cell in enumerate(layout)}   # 순서대로 눈 1..6
        qcell = layout[2]                                   # 물어볼 면(색칠)
        qn = normals[qcell]
        opp_cell = next(c for c, n in normals.items() if n == tuple(-x for x in qn))
        ans = vals[opp_cell]
        q = vals[qcell]
        adj = [vals[c] for c in layout if c != qcell and (abs(c[0] - qcell[0]) + abs(c[1] - qcell[1])) == 1]
        # 오답은 전부 실제 면 눈(1~6): 붙은 면(옆면) 우선, 모자라면 다른 면으로 채움
        pool = []
        for v in adj + [vals[c] for c in layout]:
            if v != ans and str(v) not in pool:
                pool.append(str(v))
        cols = max(c for c, _ in layout) + 1
        rows = max(r for _, r in layout) + 1
        flat = []
        for c, r in layout:
            flat += [c, r, vals[(c, r)]]
        add(
            "cubenet", "SHAPE_MEASUREMENT", 5, ["전개도", "공간 지각"],
            "정육면체(주사위 모양) 상자의 전개도예요. 접어서 상자를 만들면, 색칠한 면과 마주 보는 면의 눈은 몇 개일까요?",
            f"{ans}", pool[:3],
            f"전개도를 머릿속으로 접어 보면, 색칠한 면(눈 {q}개)과 마주 보는 면은 눈 {ans}개예요. "
            f"색칠한 면과 변을 맞대고 붙어 있는 면({', '.join(str(a) for a in adj)})은 접으면 옆면이 되어 마주 보지 않아요.",
            [(f"{adj[0]}", "전개도에서 바로 붙어 있는 면은 접으면 옆면이에요 — 마주 보는 면이 아니에요.")],
            figure={"type": "CUBE_NET", "params": {"cols": cols, "rows": rows, "query": q}, "heights": flat},
        )
    assert idx >= 3, f"유효 전개도 부족({idx})"


GENERATORS = [
    gen_cryptarithm, gen_chicken_rabbit, gen_excess_deficit, gen_age, gen_trees,
    gen_log, gen_meeting, gen_work, gen_train, gen_pyramid, gen_stairs, gen_grid,
    gen_cycle, gen_calendar, gen_average, gen_border, gen_candle, gen_mirror,
    # v2 확충 — 난이도1 바닥 + 신규 아이디어(다양성)
    gen_digit_cards, gen_sequence_simple, gen_matchsticks, gen_outfits,
    gen_broken_arithmetic, gen_cases, gen_custom_op, gen_sequence_advanced,
    gen_true_false,
    # v2.1 확충 — 도형 난2·자료 난3 빈칸 + 수 감각 다양성
    gen_triangles_match, gen_handshake, gen_dice_sum, gen_remainder,
    gen_consecutive_sum,
    # v3 확충 — 유료(난4·5) 깊이: 비둘기집·색칠정육면체·약수개수·수 추리
    gen_pigeonhole, gen_painted_cube, gen_divisor_count, gen_number_riddle,
    # v3.1 확충 — 도형 난4 보강 + 등비 다양성
    gen_clock_angle, gen_rectangle_count, gen_geometric_seq,
    # v4 확충 — 경시급 난6·7(불변량·포함배제·님게임) + 도형 대량
    gen_parity_invariant, gen_inclusion_exclusion, gen_nim,
    gen_polygon_angle, gen_polygon_diagonals, gen_clock_minutes,
    gen_rect_area_max, gen_cube_surface,
    # v4.1 확충 — 도형 그림(POLYGON) 부착 + 외각
    gen_polygon_exterior,
    # v4.2 확충 — 쌓기나무(CUBE_STACK 입체 그림, 그림 필수)
    gen_cube_stack,
    # v4.3 확충 — 격자 넓이(GRID_POLYGON 그림 필수): 삼각형·평행사변형·사다리꼴·기울어진 도형
    gen_grid_area,
    # v4.4 확충 — 삼각형 개수 세기(TRIANGLE_FAN 그림 필수): 체계적 세기
    gen_shape_count,
    # v4.5 확충 — 주사위 전개도 마주 보는 면(CUBE_NET 그림 필수): 접기 시뮬로 검산
    gen_cube_net,
]

for g in GENERATORS:
    g()

# ── 전역 무결성 자체 검사 ─────────────────────────────────────────────────────
ids = [p["id"] for p in problems]
assert len(ids) == len(set(ids)), "id 중복"
for p in problems:
    assert len(p["choices"]) == 4 and len(set(p["choices"])) == 4, f"보기 오류: {p['id']}"
    assert 0 <= p["answerIndex"] < 4
    assert len(p["explanation"]) >= 20, f"풀이가 없거나 너무 짧음: {p['id']}"
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
