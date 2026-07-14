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
from math import comb, factorial, gcd
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


def add(family, area, diff, concepts, statement, answer_text, distractors, expl, mistakes=None, figure=None, detail=None):
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
    if detail:
        problem["detailedExplanation"] = detail
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
            detail=f"복면산은 '자릿값'으로 구조를 보면 확 쉬워져요. AB＋BA=(10A+B)+(10B+A)=11×(A+B) — 그래서 합이 항상 11의 배수({total}=11×{s})인 거예요. 일일이 대입하기 전에 이렇게 식으로 규칙을 찾으면 후보를 크게 줄일 수 있어요.",
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
            detail=f"'식 세우기'로도 풀 수 있어요. 토끼를 □마리라 하면 닭은 {total}−□마리, 다리는 4×□ + 2×({total}−□) = {legs}. 정리하면 2×□ = {legs}−{2 * total}, 그래서 □ = {rabbits}. '전부 닭이라 가정하기'와 '식 세우기'는 같은 계산을 다르게 적은 것뿐이에요. 나중에 배우는 연립방정식도 바로 이 생각이랍니다.",
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
            detail=f"과부족 문제의 핵심은 '남는 양 + 모자란 양 = 나눠 주는 방법의 차이 총합'이에요. 한 명당 {y}−{x}={y - x}개씩 더 주면, 전체로는 {a}(남던 것)+{b}(모자란 것)={a + b}개가 더 필요해지죠. 그래서 명수 = (남음+모자람)÷(한 명당 차이). 식으로 쓰면 {x}×명수+{a} = {y}×명수−{b} — 같은 이야기를 저울처럼 맞춘 거예요.",
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
                        detail=f"나이 문제의 열쇠는 '변하지 않는 것'이에요. 두 사람은 해마다 똑같이 나이를 먹으니 '나이 차이'는 절대 안 변해요. 지금 차이 {parent}−{child}={parent - child}살은 {t}년 뒤에도 그대로죠. 이 고정된 차이와 배수 관계를 함께 쓰면 방정식 없이도 풀려요.",
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
            detail="간격 문제는 '끝을 세는지'가 열쇠예요. ①양 끝 다 심기 → 개수=간격+1 ②한쪽 끝만 → 개수=간격 ③양 끝 다 빼기 → 개수=간격−1 ④원(둘레) → 개수=간격(끝이 곧 처음). 공식을 외우기보다 작은 그림을 그려 '끝을 어떻게 세나'만 확인하면 어떤 간격 문제든 풀려요.",
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
        detail="간격 문제는 '끝을 세는지'가 열쇠예요. ①양 끝 다 심기 → 개수=간격+1 ②한쪽 끝만 → 개수=간격 ③양 끝 다 빼기 → 개수=간격−1 ④원(둘레) → 개수=간격(끝이 곧 처음). 상황을 그림으로 그려 '끝을 어떻게 세나'만 확인하면 직선이든 원이든 헷갈리지 않아요.",
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
            detail=f"이건 '나무 심기'와 같은 간격 문제예요. 자르는 '횟수'는 생기는 '도막'보다 언제나 1 작아요(양 끝은 자를 필요가 없으니까). 울타리 기둥과 칸, 계단과 층처럼 '사이'를 세는 문제는 늘 이 1 차이를 조심해요. 그래서 {pieces}도막엔 {pieces - 1}번, {pieces - 1}×{per}={ans}분.",
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
            detail=f"서로를 향해 가면 둘 사이 거리가 매분 (두 속력의 합)만큼 줄어요. 그래서 만나는 시간 = 거리 ÷ 속력의 합 = {track}÷({va}+{vb})={t}분. 반대로 같은 방향으로 쫓아갈 땐 '속력의 차'로 나눠요. '합이냐 차냐'가 만나기·따라잡기 문제의 갈림길이에요.",
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
            detail=f"핵심은 '하루에 하는 양(일률)'이에요. 혼자 {a}일이면 하루에 1/{a}, 다른 친구는 1/{b}만큼 해요. 함께면 그 둘을 더한 만큼 하루에 하니, 걸리는 날 = 1÷(1/{a}+1/{b}) = {t}일. 전체를 최소공배수 칸으로 두면 분수 없이 같은 계산이 되죠. 물탱크 채우기·인쇄 속도도 다 이 '일률 더하기'랍니다.",
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
            detail=f"핵심은 '기차가 실제로 지나간 거리'예요. 다리 {bridge}m만이 아니라 기차 자신의 길이 {train_len}m까지 더한 {train_len + bridge}m를 지나야 꼬리까지 완전히 건너요. 그래서 시간 = ({train_len}+{bridge})÷{speed}={t}초. '터널을 완전히 빠져나오기'도 똑같이 자기 길이를 더해요.",
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
            detail=f"꼭대기는 아래 두 칸의 합이니 {top} = (왼쪽 {a}+□) + (오른쪽 □+{c}) = {a}+{c}+2×□. 여기서 거꾸로 되짚으면 □ = (꼭대기 − 양 끝의 합) ÷ 2 = ({top}−{a}−{c})÷2 = {b}. 결과에서 출발해 원인을 되짚는 '거꾸로 생각하기'는 미로·퍼즐에서 특히 강력해요.",
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
            detail=f"이건 그 유명한 '피보나치'예요. 마지막 걸음이 1칸이었다면 그 전엔 {n - 1}칸을, 2칸이었다면 {n - 2}칸을 오른 거예요. 두 경우가 겹치지 않으니 더해요: (n칸)=(n−1칸)+(n−2칸). 그래서 1,2,3,5,8,13…처럼 앞의 두 수를 더해 나가면 {n}칸은 {w}가지. 큰 문제를 '한 걸음 작은 문제들'로 쪼개 푸는 이 방법을 점화식이라고 해요.",
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
            detail=f"각 점의 방법 수 = 왼쪽 점 + 아래 점 — 이렇게 더해 나간 표가 바로 파스칼의 삼각형이에요. 사실 오른쪽으로 {w}번, 위로 {h}번 가는 순서를 정하는 문제라 C({w}+{h}, {w})로 한 번에도 구할 수 있어요. '격자 최단 경로 = 조합'이라는 걸 알면 큰 격자도 겁나지 않아요.",
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
            detail=f"반복되는 문제는 '나머지'가 열쇠예요. {k}개가 한 묶음이니 {n}번째가 묶음 안 어디인지는 {n}÷{k}의 나머지로 정해져요(나머지가 0이면 묶음의 맨 끝 {k}번째). 요일(7일), 시계(12시간), 달력이 모두 이 '나머지 세계'로 돌아가요 — 큰 수도 나머지만 보면 돼요.",
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
            detail=f"가운데 수를 기준으로 잡는 게 비결이에요. 위·아래가 각각 −7, +7이라 서로 상쇄돼 합=가운데×3이 돼요. 이렇게 '가운데를 기준으로' 놓으면 대칭인 항이 지워져 계산이 확 줄죠. 가로로 나란한 세 수(−1, +1)나 연속한 홀수도 똑같이 가운데×3이에요.",
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
            detail=f"평균 문제는 '합'으로 바꿔 생각해요. 처음 {n}명의 합은 {n}×{m}={n * m}점. 새 평균 {m + d}점이 되려면 {n + 1}명의 합이 {n + 1}×{m + d}={(n + 1) * (m + d)}점이어야 하니, 새 사람 점수 = 그 차이 = {newcomer}점. 새 사람은 자기 몫 {m + d}점에 더해 나머지 {n}명을 각각 {d}점씩 끌어올릴 몫까지 가져와야 해서 훨씬 높아요.",
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
            detail=f"'테두리 세기'는 겹치는 부분을 어떻게 처리하느냐가 전부예요. 다르게도 셀 수 있어요: 위·아래 줄에 {side}개씩({side}×2={side * 2}), 남은 양옆은 꼭짓점을 뺀 {side - 2}개씩(합 {(side - 2) * 2}). 더하면 {side * 2}+{(side - 2) * 2}={ans}개로 똑같죠. 겹침을 '빼거나' 아예 '겹치지 않게 나누거나' — 두 길의 답이 같은지 보면 든든해요.",
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
            detail=f"'차이'만 따로 떼어 보는 게 핵심이에요. 두 초의 길이 차는 매시간 (빨리 타는 속도 − 느리게 타는 속도)만큼 줄어요. 그래서 같아지는 시간 = 처음 차이 ÷ 속도 차. 이건 '따라잡기(만나기)'와 완전히 같은 구조예요 — 거리를 길이로, 속력을 타는 속도로 바꿨을 뿐이죠.",
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
            detail=f"거울은 좌우를 뒤집어요. 12시 방향(위)을 축으로 시계가 뒤집히면 시각은 '12 빼기 실제 시각'으로 보여요. 그래서 거울 속 {mirror}시 → 실제 {actual}시(12−{mirror}={actual}). 거꾸로 실제에서 거울 모습을 알 때도 똑같이 12에서 빼면 돼요. 대칭은 '축을 기준으로 되짚기'라고 기억하면 헷갈리지 않아요.",
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
            detail="가장 큰 수는 '큰 숫자를 높은 자리에' 놓으면 돼요. 백의 자리 1은 십의 자리 10, 일의 자리 100만큼의 값이라, 큰 숫자일수록 높은 자리에 있어야 이득이 커요. 가장 작은 수는 반대로 하면 되고요. 이렇게 '가장 좋은 걸 먼저 배치'하는 방법을 욕심쟁이(그리디) 방법이라고 해요.",
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
            detail=f"이웃한 수의 '차이'가 일정하면 등차예요. 규칙을 찾을 땐 늘 먼저 이웃 차이부터 적어 보세요 — 차이가 일정하면 등차, 차이가 '몇 배'면 등비, 차이의 차이가 일정하면 그 다음 단계 규칙이에요. n번째 수는 (첫 수)+(n−1)×(차이)로 한 번에 구할 수도 있어요.",
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
            detail=f"정사각형 하나는 변 4개지만, 옆에 붙이면 맞닿은 변 1개를 '공유'해요. 그래서 첫 칸은 4개, 다음부터는 3개씩만 늘어 총 {3 * n + 1}=3×{n}+1개. '공유하는 부분은 한 번만 센다'는 생각은 둘레·격자 세기에서 계속 쓰여요.",
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
            detail="윗옷을 정하는 '단계'와 아래옷을 정하는 '단계'가 서로 영향을 안 주니 곱해요(곱의 원리). 윗옷 하나마다 아래옷 전부가 다시 가능하거든요. 만약 '윗옷 또는 아래옷 하나만' 고르는 거였다면 더했겠죠(합의 원리). 곱이냐 합이냐는 늘 '그리고냐 또는이냐'로 판단해요.",
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
            detail=f"덧셈의 빈칸은 뺄셈으로 되돌리면 바로 보여요. □{ones}는 결과 {result}에서 {addend}를 뺀 {unknown}. 이렇게 '거꾸로 셈(역연산)'으로 미지수를 드러내는 건 방정식의 씨앗이에요. 자리마다 올림이 있었는지도 함께 확인하면 더 큰 벌레먹은셈도 풀 수 있어요.",
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
            detail="곱의 원리는 '각 단계의 선택이 서로 영향을 안 줄 때(그리고, and)' 써요. 반대로 '이것 또는 저것'처럼 동시에 못 일어나는 경우(또는, or)는 더해요(합의 원리). 곱할지 더할지는 '그리고냐 또는이냐'로 판단해요. 이 둘을 자유롭게 섞어 쓰는 게 경우의 수의 핵심이에요.",
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
            detail=f"낯선 기호는 '정의된 계산 순서를 그대로 따르기'가 전부예요. 예시({ea}{sym}{eb}={ev})로 규칙을 확인한 뒤 숫자만 바꿔 넣으면 되죠. 중·고등학교에서 배우는 '함수'도 바로 이 생각 — 넣으면 정해진 규칙대로 값이 나오는 상자예요. 새 기호에 겁먹지 말고 정의대로 따라가면 어떤 약속 연산도 풀려요.",
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
            detail="차이가 일정하지 않을 땐 '차이의 차이'를 봐요. 여기선 차이가 1씩 커지죠(계차수열). 이런 수는 삼각수(1,3,6,10…)처럼 도형이 한 줄씩 커지는 상황에서 자주 나와요. 한 단계 더 파고들어 '변화의 변화'를 보는 눈이 어려운 규칙을 뚫는 열쇠예요.",
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
            detail="'한 명만 진실'이 열쇠예요. 범인을 한 사람씩 가정하고, 그때 각자의 말이 참인지 세어 보세요. 진실을 말한 사람이 '정확히 한 명'이 되는 가정만 정답이에요. 이렇게 모든 경우를 표로 만들어 '조건에 맞는 하나'만 남기는 게 논리 퍼즐의 정석이에요.",
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
            detail=f"정삼각형 1개는 3개지만, 옆에 붙이면 맞닿는 한 변을 함께 써요. 그래서 첫 개는 3개, 다음부터는 2개씩만 늘어 3+2×({n}−1)={matches}개. '붙는 곳은 한 번만 센다'는 이 생각은 정사각형 잇기·도형 둘레에서 똑같이 쓰여요. 몇 곳이 공유되는지만 세면 끝이에요.",
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
            detail=f"이건 '{n}명 중 2명 고르기'(조합)와 똑같아요 — 그래서 항상 n×(n−1)÷2. 신기하게도 같은 계산이 '점 {n}개로 그을 수 있는 선분의 수', '팀 {n}개 리그전 경기 수'에도 그대로 쓰여요. '서로 다른 둘을 한 번씩 짝짓기'는 모두 이 공식이라, 문제가 달라 보여도 같은 뼈대라는 걸 알아채는 게 중요해요.",
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
            detail=f"두 주사위는 서로 구별되니 순서가 다르면 다른 경우예요. 6×6=36칸짜리 표를 그려 합이 {k}인 칸을 세면 빠짐이 없어요. 두 주사위 합의 분포는 7을 가운데로 좌우 대칭이라, 7에서 멀어질수록 경우가 줄어요 — 이 대칭을 알면 다 세지 않아도 개수를 가늠할 수 있어요.",
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
            detail=f"두 나눗셈 조건을 동시에 만족하는 수는 {a}와 {b}의 최소공배수({a * b // gcd(a, b)})마다 규칙적으로 반복돼요. 그래서 답을 하나 찾으면, 거기에 {a * b // gcd(a, b)}를 계속 더한 수들이 모두 답이에요. 이게 옛 중국 수학책에도 나오는 '중국인의 나머지 정리'의 기초 생각이랍니다.",
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
            detail=f"연속한 수의 합엔 예쁜 규칙이 있어요. 홀수 개(여기선 5개)면 합 = 가운데 수 × 개수. 그래서 합을 개수로 나누면 가운데(=평균)가 바로 나오죠 — 가운데 기준 −2,−1,0,+1,+2가 서로 지워지니까요. 짝수 개일 땐 가운데 두 수의 평균을 쓰면 돼요. 이 '대칭으로 묶기'가 연속수 문제의 열쇠예요.",
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
            detail=f"이게 바로 '비둘기집 원리'예요: 서랍(색)이 {c}칸인데 {c}+1={ans}짝을 넣으면 반드시 한 칸에 2짝이 겹쳐요. 규칙을 바꿔 '같은 색 3짝'을 원하면, 색마다 2짝까지 다를 수 있으니 2×{c}+1짝이 필요해요. 항상 '가장 운 나쁜 경우를 먼저 그린 뒤 +1'로 생각하면 이런 '확실히 보장' 문제는 다 풀려요.",
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
            detail=f"작은 조각은 '위치'로 종류가 갈려요: 꼭짓점(3면 칠해짐) 8개, 모서리(2면) 각 {n - 2}개씩 12줄, 면 안쪽(1면) 각 {(n - 2) ** 2}개씩 6면, 속(0면) {(n - 2) ** 3}개. 위치별로 나눠 세면 어떤 조건이 와도 빠짐없이 셀 수 있어요. 3D를 '겉·모서리·꼭짓점·속'으로 분해하는 눈이 공간 감각의 핵심이에요.",
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
            detail="약수 개수엔 지름길이 있어요. 소인수분해해서 각 지수에 1을 더해 곱하면 돼요. 예를 들어 12=2×2×3이니 (2+1)×(1+1)=6개. '2를 0~2개, 3을 0~1개 골라 곱하기'의 조합으로 보는 거예요. 큰 수도 이 방법이면 빠르게 셀 수 있어요.",
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
            detail=f"합과 차를 알 때는 '두 식을 더하거나 빼기'가 지름길이에요. 합＋차를 하면 작은 쪽이 지워져 큰 쪽의 2배가 나와요: ({s}+{d})÷2={tens}가 십의 자리. 이 '합차 방법'은 나이·개수·거리처럼 두 미지수가 얽힌 문제에 두루 통하는 강력한 도구예요.",
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
            detail=f"시계 한 바퀴 360도를 12칸으로 나누면 한 칸이 30도예요. 정각엔 분침이 12를, 시침이 {h}를 가리키니 {h}칸 = {ans}도. 단, 분침이 돌면 시침도 조금씩 따라 움직여요(1분에 0.5도) — 그래서 '몇 시 몇 분'의 각도는 시침의 이동까지 더해야 정확해요.",
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
            detail=f"직사각형 하나는 '세로선 2개 + 가로선 2개'로 정해져요. 세로선 {w + 1}개 중 2개, 가로선 {h + 1}개 중 2개를 고르는 조합이니 C({w + 1},2)×C({h + 1},2)={comb(w + 1, 2) * comb(h + 1, 2)}개. 하나하나 세는 대신 '무엇을 고르면 하나가 정해지는가'를 찾으면 경우의 수가 단순해져요.",
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
            detail=f"등차(일정하게 더하기)와 등비(일정하게 곱하기)를 구별하는 게 핵심이에요. 여기선 매번 ×{r}이니 등비죠. 등비는 처음엔 등차와 비슷해 보여도 곧 폭발적으로 커져요(2,4,8,16…). 접는 종이 두께나 소문 퍼지기처럼, '곱해지는 변화'는 우리 직관보다 훨씬 빨라요.",
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
            detail=f"두 수 a, b를 지우고 |a−b|를 적어도 전체 합의 '홀짝'은 안 변해요(a+b와 |a−b|는 홀짝이 같으니까). 그래서 마지막 수의 홀짝은 처음 1부터 {n}까지 합의 홀짝으로 이미 정해져 있어요. 이렇게 '과정이 변해도 안 변하는 값(불변량)'을 찾으면, 모든 경우를 따라가지 않고도 결과를 알 수 있어요 — 고학년 수학의 강력한 무기예요.",
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
            detail=f"{a}의 배수를 빼고 {b}의 배수도 빼면, 둘 다의 배수({lcm}의 배수)는 두 번 빠져요. 그래서 한 번 도로 더해요: {total_n}−{cnt_a}−{cnt_b}+{cnt_lcm}={ans}. 이 '겹친 건 도로 더한다'가 포함배제의 핵심이고, 벤 다이어그램으로 그리면 왜 그런지 눈에 보여요.",
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
            detail=f"왜 '{k + 1}의 배수 남기기'가 필승일까요? 내가 그 배수를 남기면, 상대가 t개(1~{k}) 가져갈 때 나는 {k + 1}−t개를 가져와 매 라운드 정확히 {k + 1}개씩 지울 수 있어요. 그러면 배수→배수→…→0이 되어 마지막 돌은 늘 내 차지! 반대로 처음부터 돌 수가 {k + 1}의 배수면(나머지 0) 먼저 두는 사람이 져요. 이렇게 '상대 수를 되받아 합을 일정하게 맞추는' 방법을 대칭 전략이라고 해요.",
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
            detail=f"n각형은 한 꼭짓점에서 대각선을 그으면 삼각형 (n-2)개로 나뉘어요. 그래서 내각의 합 = (n-2)×180 = ({n}-2)×180 = {total}도. 정다각형은 이걸 n으로 똑같이 나눠 한 내각이 {ans}도. 도형을 아는 조각(삼각형)으로 쪼개는 건 넓이·각도의 만능 열쇠예요.",
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
            detail=f"대각선은 '두 꼭짓점을 잇는 선분 중 변이 아닌 것'이에요. {n}개 꼭짓점에서 2개를 고르는 방법은 C({n},2)={n * (n - 1) // 2}가지, 그중 변 {n}개를 빼면 {n * (n - 1) // 2}−{n}={ans}개. 앞의 '한 꼭짓점 {n - 3}개씩 세고 2로 나누기'와 답이 같죠 — 세는 길이 달라도 같은 답이 나오는지 확인하는 습관이 실수를 줄여요.",
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
            detail=f"핵심은 '시침도 분마다 움직인다'예요. 시침은 60분에 30도, 즉 1분에 0.5도씩 나아가요. 그래서 {h}시 {m}분 시침은 {30 * h}+{m}×0.5={hour_pos}도. 분침은 1분에 6도라 {m}분엔 {m * 6}도. 두 각의 차가 사이 각이에요. 두 바늘의 '속도'를 알면 어떤 시각의 각도도 계산할 수 있어요.",
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
            detail=f"합이 정해진 두 수는 서로 가까울수록 곱이 커지고, 같을 때 최대예요(정사각형!). 가로+세로={half}로 고정이니 {half}÷2={side}씩 똑같이 나눈 정사각형이 넓이 최대 {best}㎠. 반대로 넓이가 정해졌을 땐 정사각형일 때 둘레가 최소예요. 이 '같을 때 극단'은 자연·경제 곳곳에 나타나는 원리랍니다.",
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
            detail=f"겉넓이는 '마주 보는 세 쌍'으로 봐요: 앞뒤({b}×{c}), 좌우({a}×{c}), 위아래({a}×{b}) 각 2개씩이라 2×({a * b}+{b * c}+{a * c})={ans}㎠. 부피(속을 채우는 칸 수)와 겉넓이(겉을 감싸는 넓이)를 헷갈리지 않는 게 중요해요 — 상자를 포장하는 종이가 겉넓이랍니다.",
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
            detail=f"정다각형이든 아니든 외각을 모두 더하면 항상 360도예요 — 다각형을 한 바퀴 도는 동안 방향이 총 한 바퀴(360도) 꺾이거든요. 그래서 정{n}각형은 360÷{n}={ans}도. 내각+외각=180이라 내각도 바로 나와요. '한 바퀴는 360'이라는 이 사실이 외각 문제의 전부예요.",
        )


# ── 49. 쌓기나무 개수 세기 (난5, 도형과측정) — 그림 필수 ─────────────────────
def gen_cube_stack():
    for w, d, heights in [
        (3, 1, [1, 2, 3]),
        (2, 2, [1, 1, 1, 2]),
        (2, 3, [1, 1, 1, 1, 1, 1]),
        (3, 2, [1, 2, 1, 2, 1, 2]),
        (3, 2, [2, 1, 2, 1, 2, 1]),
        (2, 2, [2, 2, 2, 1]),
        (3, 3, [1, 1, 1, 1, 2, 1, 1, 1, 1]),
        (2, 3, [2, 1, 1, 2, 1, 1]),
    ]:
        assert len(heights) == w * d
        ans = sum(heights)
        add(
            "cubestack", "SHAPE_MEASUREMENT", 5, ["쌓기나무", "공간 지각"],
            "그림처럼 쌓은 쌓기나무는 모두 몇 개일까요? (보이지 않는 뒤·아래 나무도 세어요)",
            f"{ans}개", [f"{ans - 1}개", f"{ans + 1}개", f"{max(1, ans - 2)}개"],
            f"기둥마다 몇 층인지 세어 더해요: {' + '.join(str(h) for h in heights)} = {ans}개. 앞 나무에 가려 안 보여도 아래는 채워져 있다고 봐요.",
            [(f"{max(1, ans - 2)}개", "앞이나 위에 가려 안 보이는 나무도 빠짐없이 세어요.")],
            figure={"type": "CUBE_STACK", "params": {"w": w, "d": d}, "heights": heights},
            detail=f"쌓기나무 개수는 '위에서 본 그림'의 각 칸에 적힌 층수를 모두 더한 값과 같아요. 앞·위에 가려 안 보여도 각 기둥의 높이만 알면 정확히 셀 수 있죠. 층수를 하나씩 더하면 {ans}개예요. 이렇게 '위에서 보기'로 생각하면 아무리 복잡해도 빠짐없이 셀 수 있어요.",
        )


# ── 49-b. 쌓기나무 개수 세기 (난2, 무료) — 작은 입체, 첫 경험용 그림 문제 ──────────
def gen_cube_stack_easy():
    for w, d, heights in [
        (2, 1, [1, 2]),
        (2, 2, [1, 1, 1, 1]),
        (3, 1, [1, 2, 1]),
        (2, 2, [2, 1, 1, 1]),
    ]:
        assert len(heights) == w * d
        ans = sum(heights)
        add(
            "cubestackeasy", "SHAPE_MEASUREMENT", 2, ["쌓기나무", "공간 지각"],
            "그림처럼 쌓은 쌓기나무는 모두 몇 개일까요? (뒤에 가려 안 보이는 나무도 세어요)",
            f"{ans}개", [f"{ans - 1}개", f"{ans + 1}개", f"{max(1, ans - 2)}개"],
            f"기둥마다 몇 층인지 세어 더해요: {' + '.join(str(h) for h in heights)} = {ans}개. 앞 나무에 가려 안 보여도 뒤·아래는 채워져 있어요.",
            [(f"{ans - 1}개", "앞에 가려 안 보이는 나무도 빠짐없이 세어요.")],
            figure={"type": "CUBE_STACK", "params": {"w": w, "d": d}, "heights": heights},
            detail=f"쌓기나무 개수는 '위에서 본 그림'의 각 칸에 적힌 층수를 모두 더한 값과 같아요. 앞·위에 가려 안 보여도 각 기둥의 높이만 알면 정확히 셀 수 있죠. 층수를 하나씩 더하면 {ans}개예요. 이렇게 '위에서 보기'로 생각하면 아무리 복잡해도 빠짐없이 셀 수 있어요.",
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
            detail="넓이는 '큰 도형에서 빈 부분 빼기'와 '여러 조각으로 나눠 더하기' — 두 방법으로 구할 수 있어요. 두 방법으로 각각 구해 답이 같은지 확인하면 실수를 잡을 수 있죠. 공식을 외우기보다 '어떻게 자르고 붙일까'를 떠올리는 게 도형 넓이의 핵심이에요. (삼각형=직사각형의 반, 평행사변형=한쪽을 잘라 붙이면 직사각형, 사다리꼴=뒤집어 붙이면 평행사변형의 반.)",
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
            detail="넓이는 '큰 도형에서 빈 부분 빼기'와 '여러 조각으로 나눠 더하기' — 두 방법으로 구할 수 있어요. 두 방법으로 각각 구해 답이 같은지 확인하면 실수를 잡을 수 있죠. 공식을 외우기보다 '어떻게 자르고 붙일까'를 떠올리는 게 도형 넓이의 핵심이에요. (삼각형=직사각형의 반, 평행사변형=한쪽을 잘라 붙이면 직사각형, 사다리꼴=뒤집어 붙이면 평행사변형의 반.)",
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
            detail="넓이는 '큰 도형에서 빈 부분 빼기'와 '여러 조각으로 나눠 더하기' — 두 방법으로 구할 수 있어요. 두 방법으로 각각 구해 답이 같은지 확인하면 실수를 잡을 수 있죠. 공식을 외우기보다 '어떻게 자르고 붙일까'를 떠올리는 게 도형 넓이의 핵심이에요. (삼각형=직사각형의 반, 평행사변형=한쪽을 잘라 붙이면 직사각형, 사다리꼴=뒤집어 붙이면 평행사변형의 반.)",
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
            detail="넓이는 '큰 도형에서 빈 부분 빼기'와 '여러 조각으로 나눠 더하기' — 두 방법으로 구할 수 있어요. 두 방법으로 각각 구해 답이 같은지 확인하면 실수를 잡을 수 있죠. 공식을 외우기보다 '어떻게 자르고 붙일까'를 떠올리는 게 도형 넓이의 핵심이에요. (삼각형=직사각형의 반, 평행사변형=한쪽을 잘라 붙이면 직사각형, 사다리꼴=뒤집어 붙이면 평행사변형의 반.)",
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
            detail="넓이는 '큰 도형에서 빈 부분 빼기'와 '여러 조각으로 나눠 더하기' — 두 방법으로 구할 수 있어요. 두 방법으로 각각 구해 답이 같은지 확인하면 실수를 잡을 수 있죠. 공식을 외우기보다 '어떻게 자르고 붙일까'를 떠올리는 게 도형 넓이의 핵심이에요. (삼각형=직사각형의 반, 평행사변형=한쪽을 잘라 붙이면 직사각형, 사다리꼴=뒤집어 붙이면 평행사변형의 반.)",
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
                detail=f"삼각형은 '밑변으로 가는 선 2개'를 고를 때마다 하나씩 생겨요. 그래서 선이 {lines}개면 삼각형 수 = {lines}개에서 2개 고르기 = {lines}×{lines - 1}÷2 = {ans}개. 선이 하나 늘 때마다 삼각형은 (선의 개수−1)개씩 늘어난답니다. 하나씩 세다 빠뜨리기 쉬우니, 이렇게 '2개 고르기'로 바꿔 세면 정확해요.",
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
            detail=f"전개도를 접을 때, 색칠한 면과 변을 맞대고 붙은 면은 90도로 꺾여 '옆면'이 돼요. 그래서 마주 보는 면은 붙어 있지 않은 면 중 하나({ans})예요. 요령: 일자로 늘어선 네 면에서는 '한 칸 건너뛴 면'끼리 마주 봐요. 머릿속으로 상자를 접기 어렵다면, 붙은 면(옆면)부터 하나씩 지워 나가면 남는 면이 정답이에요.",
        )
    assert idx >= 3, f"유효 전개도 부족({idx})"


# ── 53. 저난도 그림 보강 — 그림 문제가 초반부터 자주 나오도록(난1~3 도형 밀도↑) ─────
def gen_cube_stack_tiny():
    # 난1: 1줄(뒤 가림 없음) 아주 쉬운 개수 세기
    for w, d, heights in [
        (2, 1, [1, 1]),
        (3, 1, [1, 1, 1]),
        (2, 1, [2, 1]),
        (3, 1, [1, 2, 1]),
    ]:
        assert len(heights) == w * d
        ans = sum(heights)
        add(
            "cubetiny", "SHAPE_MEASUREMENT", 1, ["쌓기나무", "수 세기"],
            "그림처럼 놓인 쌓기나무는 모두 몇 개일까요?",
            f"{ans}개", [f"{ans - 1}개", f"{ans + 1}개", f"{ans + 2}개"],
            f"각 기둥이 몇 층인지 세어 더해요: {' + '.join(str(h) for h in heights)} = {ans}개.",
            figure={"type": "CUBE_STACK", "params": {"w": w, "d": d}, "heights": heights},
            detail=f"쌓기나무 개수는 '위에서 본 그림'의 각 칸에 적힌 층수를 모두 더한 값과 같아요. 앞·위에 가려 안 보여도 각 기둥의 높이만 알면 정확히 셀 수 있죠. 층수를 하나씩 더하면 {ans}개예요. 이렇게 '위에서 보기'로 생각하면 아무리 복잡해도 빠짐없이 셀 수 있어요.",
        )


def gen_grid_tiny():
    # 난1: 아주 작은 도형의 칸 세기
    for pts, detail in [
        ([(0, 0), (2, 0), (2, 1), (1, 1), (1, 2), (0, 2)], "2×2에서 빈 1칸을 빼면 3칸"),
        ([(0, 0), (3, 0), (3, 1), (1, 1), (1, 2), (0, 2)], "아래 3칸과 위 1칸을 더하면 4칸"),
        ([(0, 0), (2, 0), (2, 2), (1, 2), (1, 3), (0, 3)], "아래 2×2(4칸)와 위 1칸을 더하면 5칸"),
    ]:
        assert _shoelace2(pts) % 2 == 0
        area = _shoelace2(pts) // 2
        add(
            "gridtiny", "SHAPE_MEASUREMENT", 1, ["넓이", "칸 세기"],
            "색칠한 도형은 모눈 몇 칸일까요? (모눈 한 칸은 1㎠예요)",
            f"{area}㎠", [f"{area - 1}㎠", f"{area + 1}㎠", f"{area + 2}㎠"],
            f"칸을 하나씩 세어요. {detail} → {area}㎠.",
            figure=_grid_fig(pts),
            detail="넓이는 '큰 도형에서 빈 부분 빼기'와 '여러 조각으로 나눠 더하기' — 두 방법으로 구할 수 있어요. 두 방법으로 각각 구해 답이 같은지 확인하면 실수를 잡을 수 있죠. 공식을 외우기보다 '어떻게 자르고 붙일까'를 떠올리는 게 도형 넓이의 핵심이에요. (삼각형=직사각형의 반, 평행사변형=한쪽을 잘라 붙이면 직사각형, 사다리꼴=뒤집어 붙이면 평행사변형의 반.)",
        )


def gen_grid_area_easy():
    # 난2: 조금 큰 ㄱ자 넓이(칸 세기/직사각형 빼기)
    for pts, detail in [
        ([(0, 0), (4, 0), (4, 1), (1, 1), (1, 2), (0, 2)], "아래 4칸과 위 1칸을 더하면 5칸"),
        ([(0, 0), (3, 0), (3, 3), (2, 3), (2, 1), (0, 1)], "큰 부분과 세로 기둥으로 나눠 세어요"),
        ([(0, 0), (3, 0), (3, 2), (2, 2), (2, 3), (0, 3)], "3×3(9칸)에서 오른쪽 위 빈 1칸을 빼면 8칸"),
        ([(0, 0), (4, 0), (4, 2), (3, 2), (3, 1), (0, 1)], "아래 4칸과 오른쪽 위 1칸"),
    ]:
        assert _shoelace2(pts) % 2 == 0
        area = _shoelace2(pts) // 2
        add(
            "grideasy", "SHAPE_MEASUREMENT", 2, ["넓이", "칸 세기"],
            "색칠한 도형의 넓이는 몇 ㎠일까요? (모눈 한 칸은 1㎠예요)",
            f"{area}㎠", [f"{area - 1}㎠", f"{area + 1}㎠", f"{area + 2}㎠"],
            f"칸을 세거나 직사각형으로 나눠 구해요. {detail} → {area}㎠.",
            figure=_grid_fig(pts),
            detail="넓이는 '큰 도형에서 빈 부분 빼기'와 '여러 조각으로 나눠 더하기' — 두 방법으로 구할 수 있어요. 두 방법으로 각각 구해 답이 같은지 확인하면 실수를 잡을 수 있죠. 공식을 외우기보다 '어떻게 자르고 붙일까'를 떠올리는 게 도형 넓이의 핵심이에요. (삼각형=직사각형의 반, 평행사변형=한쪽을 잘라 붙이면 직사각형, 사다리꼴=뒤집어 붙이면 평행사변형의 반.)",
        )


def gen_cube_stack_mid():
    # 난3: 2×2/2×3 바닥 + 층 — 뒤·아래 가림이 있어 공간 지각 필요
    for w, d, heights in [
        (2, 2, [1, 2, 1, 2]),
        (2, 2, [2, 2, 1, 1]),
        (2, 3, [1, 1, 2, 1, 1, 1]),
        (3, 2, [1, 1, 1, 2, 1, 1]),
    ]:
        assert len(heights) == w * d
        ans = sum(heights)
        add(
            "cubemid", "SHAPE_MEASUREMENT", 3, ["쌓기나무", "공간 지각"],
            "그림처럼 쌓은 쌓기나무는 모두 몇 개일까요? (뒤·아래 안 보이는 나무도 세어요)",
            f"{ans}개", [f"{ans - 1}개", f"{ans + 1}개", f"{max(1, ans - 2)}개"],
            f"기둥마다 몇 층인지 세어 더해요: {' + '.join(str(h) for h in heights)} = {ans}개. 앞·위에 가려도 아래는 채워져 있어요.",
            [(f"{max(1, ans - 2)}개", "가려서 안 보이는 나무도 빠짐없이 세어요.")],
            figure={"type": "CUBE_STACK", "params": {"w": w, "d": d}, "heights": heights},
            detail=f"쌓기나무 개수는 '위에서 본 그림'의 각 칸에 적힌 층수를 모두 더한 값과 같아요. 앞·위에 가려 안 보여도 각 기둥의 높이만 알면 정확히 셀 수 있죠. 층수를 하나씩 더하면 {ans}개예요. 이렇게 '위에서 보기'로 생각하면 아무리 복잡해도 빠짐없이 셀 수 있어요.",
        )


# ── 54. 저울로 가짜 동전 찾기 (난6, 자료와가능성) — 3진 탐색 ────────────────────
def gen_coin_balance():
    for n in [8, 9, 12, 27]:
        k = 0
        while 3 ** k < n:
            k += 1
        # 검산: k번이면 3^k가지 구분 가능(≥n), k-1번이면 부족(<n).
        assert 3 ** k >= n and 3 ** (k - 1) < n
        add(
            "balance", "DATA_POSSIBILITY", 6, ["최소 횟수", "경우의 수", "저울"],
            f"똑같이 생긴 동전 {n}개 중 하나가 조금 가벼운 가짜예요. 양팔 저울만으로 가짜를 반드시 찾으려면 최소 몇 번 재야 할까요?",
            f"{k}번", [f"{k - 1}번", f"{k + 1}번", f"{n - 1}번"],
            f"저울 한 번의 결과는 '왼쪽이 무겁다·오른쪽이 무겁다·평형' 세 가지예요. 그래서 {k}번 재면 3×3×…={3 ** k}가지까지 구분할 수 있어요. 동전을 세 무더기로 나눠 두 무더기를 저울에 올리는 식으로 후보를 매번 1/3로 줄이면, {n}개는 {k}번이면 충분해요(한 번 덜 재면 {3 ** (k - 1)}가지뿐이라 부족).",
            [(f"{n - 1}번", "한 개씩 다 재 볼 필요는 없어요. 세 무더기로 나누면 훨씬 빨라요.")],
            detail=f"핵심은 '한 번의 정보량'이에요. 저울은 결과가 3가지라 3진법 탐색이 되고, k번이면 3^k가지를 가릴 수 있어요. 그래서 필요한 횟수는 3^k ≥ {n}을 만족하는 가장 작은 k. 만약 '가벼운지 무거운지도 모르는 가짜'라면 정보가 더 필요해 횟수가 늘어요. 이분탐색(2가지)보다 저울(3가지)이 더 빠른 이유죠.",
        )


# ── 55. 원순열 (난6, 자료와가능성) — 한 명 고정 ────────────────────────────────
def gen_circular_perm():
    for n in [4, 5, 6]:
        ans = factorial(n - 1)
        assert ans == factorial(n) // n
        add(
            "circperm", "DATA_POSSIBILITY", 6, ["원순열", "기준 고정"],
            f"{n}명이 둥근 탁자에 둘러앉는 방법은 모두 몇 가지일까요? (돌려서 같아지면 한 가지로 봐요)",
            f"{ans}가지", [f"{factorial(n)}가지", f"{ans * 2}가지", f"{ans - 1}가지"],
            f"둥근 탁자는 '돌리면 같은' 자리라서 한 명을 기준으로 콱 고정해요. 그러면 나머지 {n - 1}명을 한 줄로 세우는 것과 똑같아져 ({n}−1)! = {n - 1}×…×1 = {ans}가지예요. 한 줄({factorial(n)}가지)로 세면 {n}가지 회전을 중복으로 세게 돼요.",
            [(f"{factorial(n)}가지", "그건 한 줄로 세운 수예요. 원탁은 회전이 같으니 자리 수로 나눠요.")],
            detail=f"직선으로 세우면 {n}! = {factorial(n)}가지지만, 원탁에선 {n}가지 회전이 모두 '같은 배치'라 {n}으로 나눠 {factorial(n)}÷{n} = {ans}가지. 이렇게 '중복으로 센 만큼 나누기'는 경우의 수의 핵심 도구예요(목걸이처럼 뒤집기까지 같다고 보면 2로 한 번 더 나눠요).",
        )


# ── 56. 곱의 끝자리 0의 개수 (난7, 수와연산) — 5의 개수 ─────────────────────────
def gen_factorial_zeros():
    for n in [25, 30, 50, 100]:
        z, p = 0, 5
        while p <= n:
            z += n // p
            p *= 5
        # 검산: 실제 n!의 끝자리 0 개수와 일치.
        f = factorial(n)
        real = 0
        while f % 10 == 0:
            real += 1
            f //= 10
        assert real == z
        add(
            "factzero", "NUMBER_OPERATION", 7, ["끝자리 0", "소인수 5"],
            f"1부터 {n}까지 모든 수를 곱한 값의 끝에는 0이 몇 개 붙어 있을까요?",
            f"{z}개", [f"{n // 5}개", f"{z + 1}개", f"{z - 1}개"],
            f"끝자리 0은 10=2×5에서 생겨요. 곱에는 2가 5보다 훨씬 많으니 '5가 몇 번 곱해졌나'가 0의 개수를 정해요. 5의 배수마다 5가 하나씩({n}÷5={n // 5}개), 25의 배수는 5가 하나 더, … 이렇게 더하면 {z}개예요.",
            [(f"{n // 5}개", "5의 배수만 세면 부족해요. 25·125의 배수는 5를 더 품고 있어요.")],
            detail=f"정확히는 (5의 배수 수)+(25의 배수 수)+(125의 배수 수)+… = ⌊{n}/5⌋+⌊{n}/25⌋+… = {z}. 25=5×5는 5를 두 개 품으니 한 번 더 세는 거예요. '2와 5의 쌍이 10을 만드는데 5가 병목'이라는 생각은, 자릿수·약수 문제에서 두루 쓰이는 강력한 도구랍니다.",
        )


# ── 57. 격자 최단경로 — 장애물 회피 (난6, 도형과측정) — 그림 필수 ────────────────
def _grid_paths_avoiding(w, h, bx, by):
    # 격자점 (col 0..w, 화면행 0..h). 출발 (0,h) 왼쪽아래 → 도착 (w,0) 오른쪽위, 오른쪽·위로만.
    dp = [[0] * (h + 1) for _ in range(w + 1)]
    dp[0][h] = 1
    for c in range(w + 1):
        for r in range(h, -1, -1):
            if c == 0 and r == h:
                continue
            if (c, r) == (bx, by):
                dp[c][r] = 0
                continue
            left = dp[c - 1][r] if c > 0 else 0
            below = dp[c][r + 1] if r < h else 0
            dp[c][r] = left + below
    return dp[w][0]


def gen_grid_blocked():
    for w, h, bx, by in [(3, 3, 1, 1), (4, 2, 2, 1), (3, 2, 1, 1), (4, 3, 2, 1)]:
        assert (bx, by) not in [(0, h), (w, 0)]      # 출발·도착은 막지 않음
        total = comb(w + h, w)
        ans = _grid_paths_avoiding(w, h, bx, by)
        assert 0 < ans < total
        add(
            "gridblock", "SHAPE_MEASUREMENT", 6, ["최단 경로", "장애물", "경우의 수"],
            f"가로 {w}칸, 세로 {h}칸 바둑판 길에서 왼쪽 아래(●)에서 오른쪽 위(◯)까지 오른쪽·위로만 가요. 그런데 ✕ 표시된 교차점은 공사 중이라 지날 수 없어요. 갈 수 있는 가장 짧은 길은 모두 몇 가지일까요?",
            f"{ans}가지", [f"{total}가지", f"{ans - 1}가지", f"{ans + 2}가지"],
            f"막힌 곳이 없다면 최단 경로는 {total}가지예요. 각 교차점에 (왼쪽 점 수)+(아래 점 수)를 차례로 더해 가되, ✕ 교차점만 0으로 두고 지나가지 않게 하면 도착점이 {ans}가지가 돼요.",
            [(f"{total}가지", "그건 막힌 곳이 없을 때 수예요. ✕를 지나는 길을 빼야 해요.")],
            figure={"type": "GRID", "params": {"w": w, "h": h, "mark": 1, "blockX": bx, "blockY": by}},
            detail=f"두 방법으로 풀려요. ①전체({total}) − ✕를 지나는 길. ✕를 지나는 길 = (출발→✕)×(✕→도착)처럼 앞·뒤를 곱해요. ②각 교차점에 오는 길 수를 더해 나가되 ✕만 0. 두 방법의 답이 같은지 맞춰 보면 실수를 잡아요. '거쳐 가는 길 = 앞부분 × 뒷부분'은 경로 문제의 핵심 도구예요.",
        )


# ── 58. 저울 치환 — 단위 바꾸기 (난3, 변화와관계) ──────────────────────────────
def gen_balance_substitution():
    for a_name, b_name, c_name, k1, k2 in [
        ("사과", "귤", "감", 2, 3),
        ("공", "구슬", "알사탕", 3, 2),
        ("상자", "봉지", "낱개", 2, 4),
    ]:
        ans = k1 * k2
        add(
            "subst", "CHANGE_RELATION", 3, ["치환", "단위 바꾸기"],
            f"{a_name} 1개는 {b_name} {k1}개와 같고, {b_name} 1개는 {c_name} {k2}개와 같아요. 그러면 {a_name} 1개는 {c_name} 몇 개와 같을까요?",
            f"{ans}개", [f"{k1 + k2}개", f"{ans - 1}개", f"{ans + 2}개"],
            f"{a_name} 1개 = {b_name} {k1}개인데, 그 {b_name} 하나하나가 다시 {c_name} {k2}개예요. 그래서 {a_name} 1개 = {c_name} {k1}×{k2}={ans}개. 단위를 한 단계씩 바꿀 때마다 곱해 가면 돼요.",
            [(f"{k1 + k2}개", "더하는 게 아니라, 한 단계 바꿀 때마다 곱해야 해요.")],
            detail=f"'단위 바꾸기(치환)'는 곱으로 이어져요: {a_name}→{b_name}는 ×{k1}, {b_name}→{c_name}는 ×{k2}이니 {a_name}→{c_name}는 ×({k1}×{k2}). 환율이나 단위 변환(1시간=60분, 1분=60초 → 1시간=3600초)도 똑같은 원리예요.",
        )


# ── 59. 동전 조합 가짓수 (난4, 자료와가능성) — 체계적으로 세기 ──────────────────
def gen_coin_combinations():
    for amount, coins in [(1000, [500, 100]), (500, [100, 50]), (900, [500, 100]), (600, [100, 50])]:
        ways = [0] * (amount + 1)
        ways[0] = 1
        for c in coins:
            for m in range(c, amount + 1):
                ways[m] += ways[m - c]
        ans = ways[amount]
        assert ans >= 2
        add(
            "coincomb", "DATA_POSSIBILITY", 4, ["경우의 수", "동전 조합"],
            f"{coins[0]}원과 {coins[1]}원짜리 동전으로 {amount}원을 만들려고 해요. (동전은 얼마든지 써도 되고 안 써도 돼요.) 만드는 방법은 모두 몇 가지일까요?",
            f"{ans}가지", [f"{ans - 1}가지", f"{ans + 1}가지", f"{ans + 2}가지"],
            f"큰 동전({coins[0]}원)을 0개, 1개, 2개… 넣어 보고 나머지를 작은 동전({coins[1]}원)으로 딱 채울 수 있는지 세어요. 빠짐없이·겹치지 않게 세면 {ans}가지예요.",
            detail=f"{coins[0]}원을 몇 개 쓸지 정하면 나머지는 자동으로 정해져요. 그러니 {coins[0]}원 개수만 0,1,2…로 늘려 가며 {coins[1]}원으로 딱 떨어지는 경우만 세면 빠짐도 겹침도 없죠. '한 가지를 고정하고 나머지를 따지기'는 경우의 수의 기본기예요.",
        )


# ── 60. 최대 정사각형 타일 = 최대공약수 (난5, 도형과측정) — 그림 필수 ────────────
def gen_gcd_tiles():
    for a, b in [(6, 4), (9, 6), (8, 6), (10, 4)]:
        g = gcd(a, b)
        assert g > 1
        add(
            "gcdtile", "SHAPE_MEASUREMENT", 5, ["최대공약수", "타일 깔기"],
            f"가로 {a}칸, 세로 {b}칸인 직사각형 바닥에 똑같은 정사각형 타일을 빈틈·겹침 없이 깔려고 해요. 쓸 수 있는 '가장 큰' 정사각형 타일의 한 변은 몇 칸일까요?",
            f"{g}칸", [f"{min(a, b)}칸", f"{g - 1}칸", f"{g + 1}칸"],
            f"타일 한 변이 가로도 세로도 딱 나눠떨어져야 빈틈이 안 생겨요. 그런 수 중 가장 큰 것이 최대공약수예요. {a}와 {b}의 최대공약수는 {g}이니 가장 큰 타일은 한 변 {g}칸이에요.",
            [(f"{min(a, b)}칸", "짧은 변으로는 긴 변이 딱 안 나눠질 수 있어요. 두 변을 모두 나눠야 해요.")],
            figure={"type": "GRID", "params": {"w": a, "h": b}},
            detail=f"'두 수를 모두 나누는 가장 큰 수'가 최대공약수(GCD)예요. 이 타일이면 가로 {a}÷{g}={a // g}개, 세로 {b}÷{g}={b // g}개, 모두 {a // g * (b // g)}개가 필요해요. 거꾸로 '두 길이를 겹쳐 만드는 가장 작은 정사각형'은 최소공배수랍니다.",
        )


# ── 61. 수 가르기 경우의 수 (난1, 자료와가능성) — 빠짐없이 세기 ────────────────
def gen_number_split():
    for total in [5, 6, 7, 8]:
        ans = total // 2  # 두 접시 구분 안 함, 각 1개 이상
        add(
            "numsplit", "DATA_POSSIBILITY", 1, ["경우의 수", "가르기"],
            f"구슬 {total}개를 두 접시에 나눠 담으려고 해요. 접시마다 적어도 1개는 담고, 두 접시는 구분하지 않아요(1개·{total - 1}개와 {total - 1}개·1개는 같은 방법). 나누는 방법은 모두 몇 가지일까요?",
            f"{ans}가지", [f"{ans + 1}가지", f"{ans - 1}가지", f"{total - 1}가지"],
            f"작은 쪽을 1개부터 차례로 늘려 봐요: (1,{total - 1}), (2,{total - 2})… 두 접시를 구분하지 않으니 절반까지만 세면 돼요. 그래서 1부터 {ans}까지 {ans}가지예요.",
            [(f"{total - 1}가지", "두 접시를 구분하면 두 배가 되지만, 구분하지 않으니 절반만 세요.")],
            detail=f"'작은 쪽을 1,2,3…으로 늘려 가며 빠짐없이 세기'가 경우의 수의 기본이에요. 두 접시를 구분하면 (1,{total - 1})과 ({total - 1},1)이 다른 경우라 두 배가 되지만, 구분하지 않으면 절반. '구분하나 안 하나'를 늘 먼저 확인하는 게 핵심이에요.",
        )


# ── 62. 키 순서 추론 (난2, 자료와가능성) — 흩어진 비교를 한 줄로 ────────────────
def gen_height_order():
    for four in [rng.sample(NAMES, 4) for _ in range(3)]:
        p0, p1, p2, p3 = four  # 숨은 순서: p0 > p1 > p2 > p3
        # 힌트는 자연 순서가 아니게 섞어 제시(가운데→위→아래) — 이어 붙여야 풀림
        clues = f"{p1}{_eun(p1)} {p2}보다 크고, {p0}{_eun(p0)} {p1}보다 크며, {p2}{_eun(p2)} {p3}보다 커요."
        add(
            "htorder", "DATA_POSSIBILITY", 2, ["순서 세우기", "논리 추론"],
            f"네 사람의 키를 비교했어요. {clues} 넷 중 키가 가장 큰 사람은 누구일까요?",
            p0, [p1, p2, p3],
            f"힌트로 '누가 누구보다 큰지' 화살표를 이어 보면 {p0}→{p1}→{p2}→{p3} 순서가 나와요. 아무도 자기보다 크지 않은 {p0}{_iga(p0)} 가장 커요.",
            [(p1, "한 힌트만 보면 안 돼요. 모든 힌트를 이어 붙여 전체 순서를 만들어요.")],
            detail=f"순서 문제는 '한 줄로 세우기'가 핵심이에요. 흩어진 비교를 이어 붙이면 전체 순서가 하나로 정해져요({p0}>{p1}이고 {p1}>{p2}면 {p0}>{p2} — 추이성). 표나 화살표로 정리하면 헷갈리지 않아요. 등수·토너먼트도 같은 방법으로 풀려요.",
        )


# ── 63. 최소공배수 — 동시 출발 (난4, 변화와관계) ─────────────────────────────
def gen_lcm_together():
    for a, b in [(4, 6), (6, 8), (9, 12), (10, 15)]:
        lcm = a * b // gcd(a, b)
        add(
            "lcmbus", "CHANGE_RELATION", 4, ["최소공배수", "주기"],
            f"버스 두 대가 같은 정류장에서 동시에 출발했어요. 파란 버스는 {a}분마다, 빨간 버스는 {b}분마다 출발해요. 다음에 두 버스가 '다시 동시에' 출발하는 건 몇 분 뒤일까요?",
            f"{lcm}분", [f"{a + b}분", f"{lcm // 2}분", f"{lcm + a}분"],
            f"파란 버스가 출발하는 시각은 {a}, {a * 2}, {a * 3}…분처럼 {a}의 배수예요. 빨간 버스는 {b}, {b * 2}…분처럼 {b}의 배수고요. 두 버스가 함께 출발하려면 두 배수가 겹쳐야 하니 '공배수'를 찾고, 그중 가장 이른 시각이 '최소공배수'예요. {a}와 {b}의 최소공배수는 {lcm}이라 {lcm}분 뒤에 처음으로 다시 만나요.",
            [(f"{a + b}분", "두 시간을 더하는 게 아니라, 공통으로 겹치는 배수(최소공배수)를 찾아야 해요.")],
            detail=f"최소공배수는 두 수의 곱을 최대공약수로 나눠 빠르게 구해요: {a}×{b}÷{gcd(a, b)}={lcm}. 소인수분해로 '각 소수를 더 많이 나온 쪽만큼' 곱해도 같아요. 신호등·톱니바퀴·행성의 주기가 겹치는 순간이 모두 이 최소공배수예요.",
        )


# ── 64. 연속한 수의 합 (난3, 수와연산) ───────────────────────────────────────
def gen_consecutive_sum():
    for count, mid in [(3, 8), (5, 12), (3, 20), (5, 30)]:
        total = count * mid
        pattern = "□−1, □, □+1" if count == 3 else "□−2, □−1, □, □+1, □+2"
        add(
            "consec", "NUMBER_OPERATION", 3, ["연속한 수", "가운데 기준"],
            f"연속한 자연수 {count}개를 더했더니 {total}이 됐어요. 이 {count}개 중 '가운데' 수는 얼마일까요?",
            str(mid), [str(total // 2), str(mid - 1), str(mid + count)],
            f"연속한 수는 가운데를 기준으로 양쪽이 대칭이에요. 가운데를 □라 하면 {pattern}처럼 되죠. 그러면 −와 +가 서로 지워져서 합이 '가운데 × 개수'가 돼요. 그러니 가운데 = {total} ÷ {count} = {mid}이에요.",
            [(str(total // 2), f"2로 나누는 게 아니라, 개수({count})로 나눠야 가운데가 나와요.")],
            detail=f"'가운데 기준으로 대칭 상쇄'는 개수가 홀수일 때 특히 깔끔해요(가운데가 딱 하나). 짝수 개면 가운데가 두 수 사이라 합은 '가운데 두 수의 평균 × 개수'가 되고요. 이 눈은 1부터 100까지 더하기(가우스의 방법)로도 이어져요.",
        )


# ── 65. 비둘기집 원리 (난5, 자료와가능성) ────────────────────────────────────
def gen_pigeonhole():
    for names in [["빨강", "파랑", "노랑"], ["검정", "흰색"], ["빨강", "파랑", "노랑", "초록"], ["빨강", "노랑", "초록"]]:
        colors = len(names)
        ans = colors + 1
        colortxt = "·".join(names)
        add(
            "pigeon", "DATA_POSSIBILITY", 5, ["비둘기집 원리", "최악의 경우"],
            f"서랍 안에 {colortxt} 양말이 마구 섞여 있어요(각 색이 넉넉히 있어요). 불을 끄고 색을 안 보고 꺼낼 때, '같은 색 2짝'을 반드시 갖게 되려면 최소 몇 짝을 꺼내야 할까요?",
            f"{ans}짝", [f"{colors}짝", f"{ans + 1}짝", f"{ans + 2}짝"],
            f"'반드시'를 물으니 가장 운이 나쁜 경우를 생각해요. 최악이면 색깔마다 딱 한 짝씩 뽑혀 {colors}짝까진 전부 다른 색일 수 있어요. 하지만 한 짝을 '더' 꺼내면 이미 나온 {colors}가지 색 중 하나와 반드시 겹쳐요. 그래서 {colors}+1={ans}짝이면 같은 색 2짝이 확실해요.",
            [(f"{colors}짝", "그 수까진 모두 다른 색일 수 있어요. '반드시'가 되려면 한 짝 더 필요해요.")],
            detail=f"이게 '비둘기집 원리'예요: 비둘기(꺼낸 양말)가 집({colors}가지 색)보다 많으면 어느 한 집엔 둘 이상이 들어가요. '최악의 경우를 먼저 그리고 거기서 하나 더'가 핵심 기술이에요. 반에서 생일이 같은 달인 친구 찾기도 같은 원리예요.",
        )


# ── 66. 빠진 점수 — 평균 역산 (난3, 자료와가능성) ────────────────────────────
def gen_missing_score():
    for subjects, avg, known in [(4, 85, [80, 90, 88]), (5, 80, [75, 82, 78, 90]), (4, 90, [92, 88, 95]), (3, 70, [65, 72])]:
        total = subjects * avg
        missing = total - sum(known)
        add(
            "missscore", "DATA_POSSIBILITY", 3, ["평균", "합으로 역산"],
            f"{subjects}과목 시험의 평균이 {avg}점이에요. {len(known)}과목 점수는 {', '.join(map(str, known))}점이에요. 나머지 한 과목은 몇 점일까요?",
            f"{missing}점", [f"{avg}점", f"{missing - 5}점", f"{missing + 5}점"],
            f"평균을 '합'으로 바꿔 생각해요. {subjects}과목 평균이 {avg}점이면 총점은 {subjects}×{avg}={total}점이어야 해요. 이미 아는 {len(known)}과목 합이 {sum(known)}점이니, 나머지 한 과목 = {total}−{sum(known)}={missing}점이에요.",
            [(f"{avg}점", "평균 점수를 그대로 답하면 안 돼요. 총점에서 아는 점수를 빼야 해요.")],
            detail="평균 문제의 열쇠는 '평균 = 총합 ÷ 개수'를 거꾸로 쓰는 거예요. 총합 = 평균 × 개수. 총합만 손에 쥐면 빠진 값은 뺄셈 한 번이에요. '몇 점 더 받아야 평균이 X가 될까?'도 전부 이 총합 사고로 풀려요.",
        )


# ── 67. 거듭제곱의 일의 자리 (난6, 수와연산) ─────────────────────────────────
def gen_units_cycle():
    for base, exp in [(3, 100), (7, 50), (2, 40), (8, 33)]:
        ans = pow(base, exp, 10)
        cycle = []
        x = base % 10
        while x not in cycle:
            cycle.append(x)
            x = x * base % 10
        period = len(cycle)
        distractors = [str(d) for d in cycle if d != ans][:3]
        add(
            "unitcycle", "NUMBER_OPERATION", 6, ["일의 자리", "주기"],
            f"{base}을(를) {exp}번 곱한 수의 '일의 자리 숫자'는 무엇일까요?",
            str(ans), distractors,
            f"큰 수를 다 계산할 필요 없이 '일의 자리'만 따라가면 돼요. {base}의 거듭제곱은 일의 자리가 {', '.join(map(str, cycle))} 이렇게 {period}개씩 반복돼요(주기 {period}). {exp}번째가 주기 안 어디인지는 {exp}÷{period}의 나머지로 정해지고(나머지가 0이면 맨 끝), 그 자리 숫자가 {ans}예요.",
            [(distractors[0], "그 자리 숫자는 '몇 번째로 곱했나'에 따라 달라져요. 주기 안 위치를 정확히 세었는지 봐요.")],
            detail="거듭제곱의 일의 자리는 반드시 '주기'를 이뤄요(일의 자리는 0~9뿐이라 언젠가 반복). 그래서 지수를 주기로 나눈 '나머지'만 보면 끝이에요. 이 '주기+나머지'(modular) 사고는 요일·시계·달력 계산과 완전히 같은 도구예요.",
        )


# ── 68. 집합 — 둘 다 하는 사람 (난5, 자료와가능성) ───────────────────────────
def gen_set_both():
    for total, a, b, neither in [(30, 18, 15, 3), (40, 25, 20, 5), (25, 15, 14, 2), (35, 20, 22, 6)]:
        both = a + b - (total - neither)
        assert 0 < both <= min(a, b)
        add(
            "setboth", "DATA_POSSIBILITY", 5, ["집합", "포함배제"],
            f"어느 반 {total}명에게 물었어요. 축구를 좋아하는 사람 {a}명, 농구를 좋아하는 사람 {b}명, 둘 다 안 좋아하는 사람 {neither}명이에요. 축구와 농구를 '둘 다' 좋아하는 사람은 몇 명일까요?",
            f"{both}명", [f"{both - neither}명", f"{both + neither}명", f"{total - neither}명"],
            f"둘 다 안 하는 {neither}명을 빼면, 적어도 하나는 좋아하는 사람이 {total}−{neither}={total - neither}명이에요. 그런데 축구({a}) + 농구({b}) = {a + b}명으로 세면 '둘 다' 좋아하는 사람을 두 번 센 셈이에요. 그래서 두 번 센 만큼이 겹치는 사람: {a + b}−{total - neither}={both}명이에요.",
            [(f"{both - neither}명", "'둘 다 안 하는 사람'을 도로 반영하는 걸 빠뜨렸어요."), (f"{total - neither}명", "그건 '적어도 하나'를 좋아하는 사람 수예요.")],
            detail="이게 포함배제의 기본 그림이에요: (A 또는 B) = A + B − (A 그리고 B). 여기서 'A 또는 B'는 전체에서 '아무것도 안 함'을 뺀 수고요. 벤 다이어그램 두 원을 그려 '겹치는 부분을 두 번 세었으니 한 번 뺀다'만 기억하면 어떤 두 집합 문제도 풀려요.",
        )


# ── 69. 왕복 평균 속력 (난6, 변화와관계) ─────────────────────────────────────
def gen_round_trip():
    for va, vb in [(30, 60), (40, 60), (20, 30), (48, 16)]:
        avg = 2 * va * vb // (va + vb)
        assert 2 * va * vb % (va + vb) == 0
        dist = va * vb // gcd(va, vb)  # 편도 거리를 lcm으로 두면 시간이 정수로 딱 떨어짐
        add(
            "roundtrip", "CHANGE_RELATION", 6, ["평균 속력", "조화평균"],
            f"집에서 학교까지 갈 때는 시속 {va}km, 올 때는 시속 {vb}km로 갔어요. 왕복 '평균 속력'은 시속 몇 km일까요?",
            f"{avg}km", [f"{(va + vb) // 2}km", f"{va + vb}km", f"{avg - 5}km"],
            f"평균 속력은 '(전체 거리) ÷ (전체 시간)'이지, 두 속력의 산술평균이 아니에요. 편도 거리를 {dist}km라 두면 갈 때 {dist}÷{va}={dist // va}시간, 올 때 {dist}÷{vb}={dist // vb}시간. 왕복 거리 {2 * dist}km ÷ 전체 시간 {dist // va + dist // vb}시간 = {avg}km/h예요. 느린 쪽에 시간을 더 쓰니 단순 평균보다 낮아져요.",
            [(f"{(va + vb) // 2}km", "두 속력을 그냥 더해 반으로 나누면 안 돼요 — 느린 구간에 시간이 더 걸리거든요.")],
            detail="같은 '거리'를 다른 속력으로 갈 때의 평균은 산술평균이 아니라 조화평균(2ab/(a+b))이에요. 직관과 달리 늘 느린 쪽에 더 끌려가요. 반대로 같은 '시간'을 다른 속력으로 가면 그땐 산술평균이 맞고요 — '무엇이 같은가(거리냐 시간이냐)'를 먼저 보는 게 핵심이에요.",
        )


# ── 70. 악수/리그전 = C(n,2) (난5, 자료와가능성) ─────────────────────────────
def gen_handshake():
    for n in [5, 6, 8, 10]:
        ans = n * (n - 1) // 2
        add(
            "handshake", "DATA_POSSIBILITY", 5, ["경우의 수", "두 번 세고 나누기"],
            f"{n}명이 모여 서로 한 번씩 빠짐없이 악수를 해요. 악수는 모두 몇 번 일어날까요?",
            f"{ans}번", [f"{n * (n - 1)}번", f"{n * n}번", f"{ans - n + 1}번"],
            f"한 사람은 자기를 뺀 {n - 1}명과 악수해요. {n}명이 각자 {n - 1}번이면 {n}×{n - 1}={n * (n - 1)}번인데, 이러면 'A와 B의 악수'를 A쪽·B쪽에서 두 번 센 거예요. 그래서 2로 나눠요: {n * (n - 1)}÷2={ans}번.",
            [(f"{n * (n - 1)}번", "같은 악수를 두 사람이 각각 세서 두 번씩 세었어요. 2로 나눠야 해요.")],
            detail=f"이건 '{n}명 중 2명을 뽑는' 경우의 수 C({n},2)와 똑같아요. 두 개를 짝짓는 모든 문제(악수·리그전 경기·점끼리 잇는 선분·삼각형 개수)가 여기에 해당해요. '두 번 세고 2로 나누기'는 세기의 단골 기술이에요.",
        )


# ── 71. 1부터 N까지의 합 — 가우스 (난4, 수와연산) ────────────────────────────
def gen_gauss_sum():
    for n in [10, 20, 50, 100]:
        ans = n * (n + 1) // 2
        add(
            "gauss", "NUMBER_OPERATION", 4, ["연속 자연수 합", "짝지어 더하기"],
            f"1부터 {n}까지 모든 자연수를 더하면 얼마일까요?",
            str(ans), [str(n * n), str(ans + n), str(ans - n)],
            f"양 끝에서 짝을 지어 더해 봐요: 1+{n}={n + 1}, 2+{n - 1}={n + 1}, … 모든 짝의 합이 {n + 1}로 똑같아요. 짝은 모두 {n}÷2={n // 2}쌍이니 {n + 1}×{n // 2}={ans}이에요.",
            [(str(n * n), "제곱이 아니라, 양 끝을 짝지어 더한 값이에요.")],
            detail=f"어린 가우스가 찾았다는 방법이에요: 1+2+…+n = n×(n+1)÷2. 수를 거꾸로도 써서 위아래로 더하면 왜 그런지 한눈에 보여요(세로 합이 모두 n+1). 등차수열의 합은 전부 '(첫+끝)×개수÷2'로 통해요.",
        )


# ── 72. 비로 나누기 (난5, 변화와관계) ────────────────────────────────────────
def gen_ratio_share():
    for total, r1, r2 in [(20, 3, 2), (35, 4, 3), (24, 5, 1), (40, 3, 5)]:
        assert total % (r1 + r2) == 0
        unit = total // (r1 + r2)
        part = unit * r1
        add(
            "ratioshare", "CHANGE_RELATION", 5, ["비", "단위량 먼저"],
            f"구슬 {total}개를 형과 동생이 {r1}:{r2}로 나눠 가져요. 형이 갖는 구슬은 몇 개일까요?",
            f"{part}개", [f"{r1}개", f"{total // 2}개", f"{total - part}개"],
            f"비 {r1}:{r2}는 전체를 똑같은 묶음 {r1}+{r2}={r1 + r2}묶음으로 나눈 거예요. 한 묶음은 {total}÷{r1 + r2}={unit}개. 형은 그중 {r1}묶음을 가지니 {unit}×{r1}={part}개예요.",
            [(f"{total - part}개", "그건 동생 몫이에요."), (f"{total // 2}개", "비가 같지 않으면 절반이 아니에요. 묶음 수로 나눠요.")],
            detail="비 문제의 핵심은 '한 묶음(단위량)'을 먼저 구하는 거예요. 전체를 (비의 합)으로 나누면 한 묶음이 나오고, 각자는 자기 몫만큼 곱하면 끝. 이 '단위량 먼저' 사고는 축척·농도·환율에도 똑같이 통해요.",
        )


# ── 73. 분수로 전체 구하기 (난3, 수와연산) ───────────────────────────────────
def gen_fraction_whole():
    for part, num, den in [(12, 2, 5), (18, 3, 4), (20, 2, 5), (21, 3, 7)]:
        assert part % num == 0
        whole = part * den // num
        add(
            "fracwhole", "NUMBER_OPERATION", 3, ["분수", "부분과 전체"],
            f"어떤 통에 든 구슬의 {num}/{den}이 {part}개예요. 통에 든 구슬은 모두 몇 개일까요?",
            f"{whole}개", [f"{part * den}개", f"{part + den}개", f"{whole - part}개"],
            f"전체를 똑같이 {den}조각으로 나눈 것 중 {num}조각이 {part}개라는 뜻이에요. 그럼 1조각은 {part}÷{num}={part // num}개. 전체는 {den}조각이니 {part // num}×{den}={whole}개예요.",
            [(f"{part * den}개", "분모만 곱하면 안 돼요. 먼저 한 조각(÷분자)을 구해요.")],
            detail=f"부분·전체 문제는 '1조각(단위분수)'을 먼저 구하는 게 열쇠예요. {num}/{den}이 {part}면 1/{den}은 {part}÷{num}, 전체(={den}/{den})는 거기에 {den}배. 반대로 '전체의 {num}/{den}은?'은 전체를 {den}으로 나눠 {num}배 하면 돼요.",
        )


# ── 74. 토너먼트 경기 수 (난5, 자료와가능성) ─────────────────────────────────
def gen_tournament():
    for n in [8, 16, 32, 10]:
        ans = n - 1
        add(
            "tourney", "DATA_POSSIBILITY", 5, ["토너먼트", "사라지는 양 세기"],
            f"{n}명이 토너먼트(진 사람은 바로 탈락)로 경기해서 우승자 한 명을 가려요. 우승자가 정해질 때까지 경기는 모두 몇 번 열릴까요?",
            f"{ans}번", [f"{n}번", f"{n // 2}번", f"{ans - 1}번"],
            f"경기 수를 하나하나 세는 대신 '탈락자'에 주목해요. 한 경기가 열릴 때마다 딱 한 명이 탈락해요. 우승자 1명만 남기려면 나머지 {n}−1={ans}명이 전부 탈락해야 하니, 경기도 정확히 {ans}번이에요.",
            [(f"{n // 2}번", "1라운드 경기 수만 센 거예요. 모든 라운드를 합쳐야 해요.")],
            detail=f"'무엇이 하나씩 사라지는가'를 보면 복잡한 대진표를 안 그려도 돼요 — 경기 1번 = 탈락 1명이니 우승자 빼고 모두 탈락 = {n}−1번. 이 '변하는 양을 세는' 관점은 대진 방식이 바뀌어도 그대로 통해요.",
        )


# ── 75. 거스름돈 최소 동전 (난3, 수와연산) ───────────────────────────────────
def gen_change_coins():
    coins = [500, 100, 50, 10]
    for amount in [780, 640, 970, 850]:
        cnt = 0
        rem = amount
        breakdown = []
        for c in coins:
            k = rem // c
            if k:
                breakdown.append(f"{c}원 {k}개")
            cnt += k
            rem %= c
        add(
            "mincoin", "NUMBER_OPERATION", 3, ["거스름돈", "욕심쟁이 방법"],
            f"거스름돈 {amount}원을 500·100·50·10원 동전으로 거슬러 줄 때, 동전 개수를 '가장 적게' 하려면 모두 몇 개가 필요할까요?",
            f"{cnt}개", [f"{cnt + 1}개", f"{cnt - 1}개", f"{cnt + 2}개"],
            f"동전을 적게 쓰려면 '큰 동전부터' 최대한 많이 써요. {' + '.join(breakdown)} = 모두 {cnt}개예요.",
            [(f"{cnt + 1}개", "큰 동전부터 최대한 쓰면 개수를 더 줄일 수 있어요.")],
            detail="'큰 단위부터 최대한'이 욕심쟁이(그리디) 방법이에요. 우리 동전(500·100·50·10)은 이 방법이 늘 최소를 보장해요. 하지만 모든 체계가 그렇진 않아요 — 1·3·4원짜리라면 6원은 4+1+1(3개)보다 3+3(2개)이 적어, 큰 것부터가 최선이 아닐 수 있어요.",
        )


# ── 76. 비례식 — 레시피 (난4, 변화와관계) ────────────────────────────────────
def gen_recipe_ratio():
    for item, base_qty, base_ing, ing, unit, new_qty in [
        ("쿠키", 12, 3, "설탕", "스푼", 20),
        ("팬케이크", 4, 2, "우유", "컵", 10),
        ("주스", 2, 5, "오렌지", "개", 8),
        ("빵", 6, 4, "버터", "스푼", 15),
    ]:
        assert new_qty * base_ing % base_qty == 0
        ans = new_qty * base_ing // base_qty
        add(
            "recipe", "CHANGE_RELATION", 4, ["비례", "단위량"],
            f"{item} {base_qty}개를 만들려면 {ing} {base_ing}{unit}{_iga(unit)} 필요해요. 같은 맛으로 {item} {new_qty}개를 만들려면 {ing}{_eun(ing)} 몇 {unit} 필요할까요?",
            f"{ans}{unit}", [f"{base_ing + (new_qty - base_qty)}{unit}", f"{new_qty}{unit}", f"{ans + base_ing}{unit}"],
            f"먼저 {item} 1개당 {ing}이 얼마인지 봐요: {base_ing}÷{base_qty}. {item} {new_qty}개면 그 {new_qty}배니 {base_ing}×{new_qty}÷{base_qty}={ans}{unit}이에요. (비례식 {base_qty}:{base_ing}={new_qty}:□로 풀어도 □={ans}.)",
            [(f"{base_ing + (new_qty - base_qty)}{unit}", "개수 차이만큼 '더하는' 게 아니라, 몇 배인지(비율)로 늘려야 해요.")],
            detail="비례는 '한 개당 얼마(단위량)'를 구하면 다 풀려요. 또는 비례식 a:b=c:□에서 '바깥끼리 곱 = 안끼리 곱'(교차곱)으로 □를 구해도 돼요. 요리·지도 축척·환율·농도가 전부 이 비례 위에 있어요.",
        )


# ── 77. 정사각형 둘레 ↔ 넓이 (난3, 도형과측정) ──────────────────────────────
def gen_square_area():
    for side in [6, 8, 5, 9]:
        perim = side * 4
        area = side * side
        add(
            "sqarea", "SHAPE_MEASUREMENT", 3, ["정사각형", "둘레와 넓이"],
            f"둘레가 {perim}cm인 정사각형이 있어요. 이 정사각형의 넓이는 몇 ㎠일까요?",
            f"{area}㎠", [f"{perim}㎠", f"{side * 2}㎠", f"{area + side}㎠"],
            f"정사각형은 네 변이 모두 같아요. 둘레가 {perim}cm면 한 변은 {perim}÷4={side}cm. 넓이는 한 변을 두 번 곱하니 {side}×{side}={area}㎠예요.",
            [(f"{perim}㎠", "둘레와 넓이는 달라요. 먼저 한 변(÷4)을 구한 뒤 곱해요.")],
            detail=f"둘레는 '가장자리 길이(1차원)', 넓이는 '채운 칸(2차원)'이라 단위도 cm와 ㎠로 달라요. 둘레→한 변(÷4)→넓이(제곱) 순서가 핵심. 반대로 넓이 {area}에서 한 변은 곱해서 {area}가 되는 수({side})를 찾으면 돼요.",
        )


GENERATORS = [
    gen_number_split, gen_height_order,
    gen_lcm_together, gen_consecutive_sum, gen_pigeonhole, gen_missing_score,
    gen_units_cycle, gen_set_both, gen_round_trip,
    gen_handshake, gen_gauss_sum, gen_ratio_share, gen_fraction_whole,
    gen_tournament, gen_change_coins, gen_recipe_ratio, gen_square_area,
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
    # v4.6 확충 — 무료(난2) 작은 쌓기나무: 첫 경험용 그림 문제(무료 체험 비주얼 강화)
    gen_cube_stack_easy,
    # v4.7 확충 — 저난도 그림 밀도↑(난1~3): 그림 문제가 초반부터 자주 나오게
    gen_cube_stack_tiny, gen_grid_tiny, gen_grid_area_easy, gen_cube_stack_mid,
    # v4.3 확충 — 격자 넓이(GRID_POLYGON 그림 필수): 삼각형·평행사변형·사다리꼴·기울어진 도형
    gen_grid_area,
    # v4.4 확충 — 삼각형 개수 세기(TRIANGLE_FAN 그림 필수): 체계적 세기
    gen_shape_count,
    # v4.5 확충 — 주사위 전개도 마주 보는 면(CUBE_NET 그림 필수): 접기 시뮬로 검산
    gen_cube_net,
    # v4.8 확충 — 경시급(난6~7): 저울 3진탐색·원순열·팩토리얼 끝자리 0
    gen_coin_balance, gen_circular_perm, gen_factorial_zeros,
    # v4.9 확충 — 격자 최단경로 장애물 회피(GRID 그림 필수, 난6): DP 검산
    gen_grid_blocked,
    # v5.0 확충 — 콘텐츠 볼륨: 저울 치환·동전 조합·최대공약수 타일(그림)
    gen_balance_substitution, gen_coin_combinations, gen_gcd_tiles,
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
