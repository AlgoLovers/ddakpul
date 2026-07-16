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
import re
from math import comb, factorial, gcd
from pathlib import Path

from concept_en import CONCEPT_EN  # 개념 태그 한→영 사전(리포트 노출용)

OUT = Path(__file__).resolve().parents[2] / "app/src/main/assets/problems_generated.json"
OUT_EN = Path(__file__).resolve().parents[2] / "app/src/main/assets/problems_generated_en.json"
rng = random.Random(20260710)  # 재현 가능하게 시드 고정
rng_en = random.Random(20260711)  # 영어 뱅크 전용 rng — 한국어 rng 순서를 건드리지 않아 KO 뱅크가 바이트 동일

NAMES = ["민준", "서연", "지호", "하은", "도윤", "예린", "시우", "지아"]
FRUITS = ["사과", "귤", "배", "감"]
COLORS3 = [["빨간", "노란", "파란"], ["초록", "보라", "주황"]]

problems = []
problems_en = []  # 다국어: add(en=...)로 영어가 제공된 계열만 여기 쌓인다
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


def _fix_number_copula(text):
    """숫자 바로 뒤 한국어 조사를 그 숫자 읽기의 받침에 맞춰 자동 교정.
    서술격(예요/이에요)·목적격(을/를)·주격(이/가)·보조사(은/는)·접속(과/와)·부사격(으로/로)을
    모두 다룬다. 예: '7예요'→'7이에요', '5을'→'5를', '43로'→'43으로'.
    조사 뒤에 공백·문장부호가 오는 진짜 조사만 고쳐, '가지'·'이에요'·'개' 같은 낱말은 건드리지 않는다."""
    if not text:
        return text
    text = re.sub(r"(\d+)(?:예요|이에요)", lambda m: m.group(1) + _copula(m.group(1)), text)
    pat = [("을", "를", _eul), ("이", "가", _iga), ("은", "는", _eun), ("과", "와", _gwa), ("으로", "로", _euro)]
    for a, b, fn in pat:
        text = re.sub(rf"(\d+)(?:{a}|{b})(?=[\s.,)])", lambda m, fn=fn: m.group(1) + fn(m.group(1)), text)
    return text


def _fix_en_grammar(text):
    """영어는 한국어 조사 교정이 필요 없다(복수형은 생성기에서 _en_plural로 처리). 자리표시자."""
    return text


def _en_plural(n, singular):
    """'1 path' / '2 paths'처럼 수에 맞는 단수·복수. (단순 규칙; 불규칙은 생성기에서 직접)"""
    return f"{n} {singular}" if n == 1 else f"{n} {singular}s"


def _emit(target, rnd, family, area, diff, concepts, statement, answer_text, distractors, expl, mistakes, figure, detail, fix):
    """한 문제를 만들어 target 리스트에 넣는다. rnd·fix(조사교정)만 언어별로 다르다."""
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
    rnd.shuffle(order)
    shuffled = [choices[i] for i in order]
    answer_index = shuffled.index(answer_text)
    idx = sum(1 for p in target if p["groupId"] == f"g-gen-{family}-{diff}") + 1
    problem = {
        "id": f"gen-{family}-{idx}",
        "area": area,
        "difficulty": diff,
        "groupId": f"g-gen-{family}-{diff}",
        "concepts": concepts,
        "statement": fix(statement),
        "choices": shuffled,
        "answerIndex": answer_index,
        "explanation": fix(expl),
        "mistakes": [
            {"choiceIndex": shuffled.index(text), "misconception": fix(why)}
            for text, why in (mistakes or [])
            if text in shuffled and shuffled.index(text) != answer_index
        ],
        "source": "generated:v1(template+brute-force-verified)",
    }
    if figure:
        problem["figure"] = figure
    if detail:
        problem["detailedExplanation"] = fix(detail)
    target.append(problem)


def add(family, area, diff, concepts, statement, answer_text, distractors, expl, mistakes=None, figure=None, detail=None, en=None):
    """정답 1 + 오답 3을 섞어 4지선다로 만든다. en={statement,answer,distractors,explanation,...}를 주면
    같은 수학(도형·정답구조)에서 영어 문제도 함께 만들어 problems_en에 넣는다(뱅크는 독립·rng도 별도)."""
    _emit(problems, rng, family, area, diff, concepts, statement, answer_text, distractors, expl, mistakes, figure, detail, _fix_number_copula)
    stats["generated"] += 1
    if en is not None:
        # 개념 태그는 사전으로 자동 번역(계열마다 따로 안 줘도 됨). 미등록 태그는 원문 유지.
        en_concepts = en.get("concepts") or [CONCEPT_EN.get(c, c) for c in concepts]
        _emit(
            problems_en, rng_en, family, area, diff,
            en_concepts, en["statement"], en["answer"], en["distractors"],
            en["explanation"], en.get("mistakes"), figure, en.get("detail"), _fix_en_grammar,
        )


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
            en={
                "statement": f"A two-digit number (AB) plus the number with its digits swapped (BA) adds up to {total}. What is A+B? (A and B are nonzero single digits.)",
                "answer": str(s),
                "distractors": distractors,
                "explanation": f"(AB) is 10×A+B, and the swapped number (BA) is 10×B+A. Adding them counts A and B eleven times each, which is 11×(A+B). {total}÷11={s}, so A+B={s}.",
                "mistakes": [(str(total // 10), "The sum of the two numbers is always a multiple of 11. Try dividing by 11.")],
                "detail": f"Cryptarithms get much easier when you see the structure through 'place value'. AB+BA=(10A+B)+(10B+A)=11×(A+B) — that's why the sum is always a multiple of 11 ({total}=11×{s}). Finding the rule as a formula like this, before plugging in numbers one by one, cuts down the candidates a lot.",
            },
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
            en={
                "statement": f"A yard has {total} chickens and rabbits altogether. Counting the legs gives {legs}. How many rabbits are there?",
                "answer": _en_plural(rabbits, "rabbit"),
                "distractors": [_en_plural(rabbits - 1, "rabbit"), _en_plural(rabbits + 1, "rabbit"), _en_plural(total - rabbits, "rabbit")],
                "explanation": f"Suppose they were all chickens. Then there would be 2×{total}={2 * total} legs, but there are actually {legs} — that's {legs - 2 * total} more. Each time you swap a chicken for a rabbit the legs go up by 2, so {legs - 2 * total}÷2={rabbits} are rabbits.",
                "mistakes": [(_en_plural(total - rabbits, "rabbit"), "That's the number of chickens. The question asked for the rabbits.")],
                "detail": f"You can also set up an equation. If there are □ rabbits, there are {total}−□ chickens, and the legs are 4×□ + 2×({total}−□) = {legs}. Simplifying, 2×□ = {legs}−{2 * total}, so □ = {rabbits}. 'Assume all are chickens' and 'set up an equation' are just two ways of writing the same calculation — the systems of equations you meet later are exactly this idea.",
            },
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
        fruit_en = {"사과": "apples", "귤": "tangerines", "배": "pears", "감": "persimmons"}[fruit]
        add(
            "excess", "NUMBER_OPERATION", 4, ["과부족", "차이로 나누기"],
            f"{name}이(가) 친구들에게 {fruit}을(를) 나눠 줘요. 한 명에게 {x}개씩 주면 {a}개가 남고, {y}개씩 주면 {b}개가 모자라요. 친구는 모두 몇 명일까요?",
            f"{p}명", [f"{p - 1}명", f"{p + 1}명", f"{a + b}명"],
            f"{x}개씩 줄 때는 {a}개가 남고, {y}개씩 줄 때는 {b}개가 모자라요 — 방법을 바꾸면 필요한 {fruit}이 {a}+{b}={a + b}개 차이 나는 거예요. 한 명당 {y - x}개씩 더 주기 때문이니, 친구 수는 {a + b}÷{y - x}={p}명이에요.",
            [(f"{a + b}명", f"{a + b}는 필요한 개수의 차이예요. 한 명당 차이 {y - x}개로 나눠요.")],
            detail=f"과부족 문제의 핵심은 '남는 양 + 모자란 양 = 나눠 주는 방법의 차이 총합'이에요. 한 명당 {y}−{x}={y - x}개씩 더 주면, 전체로는 {a}(남던 것)+{b}(모자란 것)={a + b}개가 더 필요해지죠. 그래서 명수 = (남음+모자람)÷(한 명당 차이). 식으로 쓰면 {x}×명수+{a} = {y}×명수−{b} — 같은 이야기를 저울처럼 맞춘 거예요.",
            en={
                "statement": f"A hands out {fruit_en} to some friends. Giving {x} each leaves {a} over, and giving {y} each falls {b} short. How many friends are there in all?",
                "answer": _en_plural(p, "friend"),
                "distractors": [_en_plural(p - 1, "friend"), _en_plural(p + 1, "friend"), _en_plural(a + b, "friend")],
                "explanation": f"Giving {x} each leaves {a} over, and giving {y} each falls {b} short — switching the plan changes the {fruit_en} needed by {a}+{b}={a + b}. That's because each friend gets {y - x} more, so the number of friends is {a + b}÷{y - x}={p}.",
                "mistakes": [(_en_plural(a + b, "friend"), f"{a + b} is the difference in the number needed. Divide by the per-friend difference of {y - x}.")],
                "detail": f"The key to excess-and-deficit problems is 'amount left over + amount short = total change between the two sharing plans'. Giving {y}−{x}={y - x} more to each friend needs {a} (was left over)+{b} (was short)={a + b} more in total. So (number of friends) = (over + short)÷(per-friend difference). Written as an equation, {x}×friends+{a} = {y}×friends−{b} — the same story balanced like a scale.",
            },
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
                        en={
                            "statement": f"The mother's age now is {k} times the daughter's age. In {t} years it will be {m} times. How old is the daughter now?",
                            "answer": f"{child} years old",
                            "distractors": [f"{child - 2} years old", f"{child + 2} years old", f"{parent} years old"],
                            "explanation": f"Make a table and check step by step. If the daughter is {child}, the mother is {k} times that, {parent}. In {t} years both grow by {t}: daughter {child + t}, mother {parent + t} — exactly {m} times, which fits perfectly. The answer is {child} years old.",
                            "mistakes": [(f"{parent} years old", "That's the mother's age right now.")],
                            "detail": f"The key to age problems is 'what does not change'. Both people age the same amount every year, so the 'age difference' never changes. Today's difference {parent}−{child}={parent - child} stays the same {t} years later. Using this fixed difference together with the multiple relationship solves it without any equation.",
                        },
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
            en={
                "statement": f"Along one side of a road {length} m long, streetlights are placed every {gap} m from the very start to the very end. How many streetlights are needed?",
                "answer": _en_plural(g + 1, "streetlight"),
                "distractors": [_en_plural(g, "streetlight"), _en_plural(g + 2, "streetlight"), _en_plural(g - 1, "streetlight")],
                "explanation": f"Draw a small picture first. With 1 gap you need 2 lights, with 2 gaps you need 3 — there is always one more light than gaps. The number of gaps is {length}÷{gap}={g}, so you need {g}+1={g + 1} lights.",
                "mistakes": [(_en_plural(g, "streetlight"), "The number of gaps and the number of lights differ. Add the very first one.")],
                "detail": "Interval problems hinge on 'do you count the ends?'. ① Both ends → count = gaps+1. ② Only one end → count = gaps. ③ Neither end → count = gaps−1. ④ A circle (loop) → count = gaps (the end is the start). Rather than memorizing formulas, draw a small picture and just check 'how are the ends counted' — then any interval problem works.",
            },
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
        en={
            "statement": f"Trees are planted every {gap} m around a round pond whose perimeter is {length} m. How many trees are needed?",
            "answer": _en_plural(g, "tree"),
            "distractors": [_en_plural(g + 1, "tree"), _en_plural(g - 1, "tree"), _en_plural(g + 2, "tree")],
            "explanation": f"On a straight road there is one more tree than gaps, but on a circle the last tree meets the first after one full loop. So the number of trees equals the number of gaps. The gaps are {length}÷{gap}={g}, so you need {g} trees.",
            "mistakes": [(_en_plural(g + 1, "tree"), "The +1 is only for a straight road. On a circle the last tree is the first tree!")],
            "detail": "Interval problems hinge on 'do you count the ends?'. ① Both ends → count = gaps+1. ② Only one end → count = gaps. ③ Neither end → count = gaps−1. ④ A circle (loop) → count = gaps (the end is the start). Draw the situation and just check 'how are the ends counted', and neither a line nor a circle will confuse you.",
        },
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
            en={
                "statement": f"You want to cut a long log into {pieces} pieces. If each cut takes {per} minutes, how many minutes does it take in all?",
                "answer": f"{ans} minutes",
                "distractors": [f"{pieces * per} minutes", f"{(pieces - 2) * per} minutes", f"{ans + per * 2} minutes"],
                "explanation": f"Think small. To get 2 pieces you cut once, for 3 pieces twice — the number of cuts is always one less than the number of pieces. For {pieces} pieces you cut {pieces - 1} times, so it takes {pieces - 1}×{per}={ans} minutes.",
                "mistakes": [(f"{pieces * per} minutes", "You don't cut once per piece — the last piece appears on its own.")],
                "detail": f"This is the same as the 'planting trees' interval problem. The number of 'cuts' is always one less than the 'pieces' made (the two ends need no cut). Anything that counts the 'gaps between' — fence posts and panels, stairs and floors — watch for this off-by-one. So {pieces} pieces need {pieces - 1} cuts, {pieces - 1}×{per}={ans} minutes.",
            },
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
            en={
                "statement": f"On a circular track {track} m around, A and B start from the same spot at the same time, walking in opposite directions. A walks {va} m per minute and B walks {vb} m per minute. After how many minutes do they first meet?",
                "answer": f"{t} minutes",
                "distractors": [f"{t * 2} minutes", f"{t + 1} minutes", f"{track // max(va, vb)} minutes"],
                "explanation": f"Walking in opposite directions, they first meet the moment their combined distance equals one full lap, {track} m. Together they cover {va}+{vb}={va + vb} m each minute, so they meet after {track}÷{va + vb}={t} minutes.",
                "mistakes": [(f"{t * 2} minutes", "Check whether you added the two speeds instead of using just one person's speed.")],
                "detail": f"When two people move toward each other, the distance between them shrinks by (the sum of the two speeds) every minute. So meeting time = distance ÷ sum of speeds = {track}÷({va}+{vb})={t} minutes. When chasing in the same direction, you divide by the 'difference' of the speeds instead. 'Sum or difference' is the fork between meeting and catching-up problems.",
            },
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
            en={
                "statement": f"A certain job takes A {a} days alone and another child {b} days alone. Working together, in how many days can they finish?",
                "answer": f"{t} days",
                "distractors": [f"{(a + b) // 2} days", f"{t + 2} days", f"{abs(b - a)} days"],
                "explanation": f"Think of the whole job as {lcm} parts. One person does {lcm}÷{a}={lcm // a} parts a day, the other does {lcm}÷{b}={lcm // b} parts a day. Together they do {lcm // a}+{lcm // b}={lcm // a + lcm // b} parts a day, so {lcm}÷{lcm // a + lcm // b}={t} days to finish.",
                "mistakes": [(f"{(a + b) // 2} days", "It's not the average. Working together must be faster than even the quicker person alone.")],
                "detail": f"The key is 'how much gets done in a day (the work rate)'. Alone in {a} days means 1/{a} per day, the other does 1/{b}. Together they do the sum each day, so days needed = 1÷(1/{a}+1/{b}) = {t} days. Setting the whole job as a least-common-multiple number of parts gives the same calculation without fractions. Filling a tank or printing speed are all this same 'adding of work rates'.",
            },
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
            en={
                "statement": f"A train {train_len}m long runs at {speed}m per second. How many seconds does it take to pass completely through a tunnel {bridge}m long (from the moment the front enters until the tail comes out)?",
                "answer": f"{t} seconds",
                "distractors": [f"{bridge // speed} seconds", f"{t + 5} seconds", f"{train_len // speed if train_len % speed == 0 else t - 3} seconds"],
                "explanation": f"Follow the front of the train. Even after the front has passed all {bridge}m of the tunnel, the body of the train is still inside. For the tail to come out too, the train must travel its own length {train_len}m more, so it covers {bridge}+{train_len}={bridge + train_len}m in all. At {speed}m per second, that is {bridge + train_len}÷{speed}={t} seconds.",
                "mistakes": [(f"{bridge // speed} seconds", f"You forgot the train's own length of {train_len}m.")],
                "detail": f"The key is 'the distance the train actually travels'. It must cover not just the {bridge}m tunnel but also its own length {train_len}m, a total of {train_len + bridge}m, before the tail is fully through. So time = ({train_len}+{bridge})÷{speed}={t} seconds. 'Coming completely out of a tunnel' adds the train's own length the same way.",
            },
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
            en={
                "statement": f"In a number pyramid, each cell is the sum of the two cells right below it. If the bottom row is [{a}, □, {c}] and the top is {top}, what is □?",
                "answer": str(b),
                "distractors": [str(b - 1), str(b + 1), str(top - a - c)],
                "explanation": f"Build upward by the rule. The middle row is ({a}+□) and (□+{c}), and the top is their sum, {a}+□+□+{c}. So the two □'s add up to {top}−{a}−{c}={top - a - c}, which means □={top - a - c}÷2={b}.",
                "mistakes": [(str(top - a - c), "That's the sum of the two □'s. Divide by 2.")],
                "detail": f"The top is the sum of the two cells below, so {top} = (left {a}+□) + (right □+{c}) = {a}+{c}+2×□. Tracing backward, □ = (top − sum of the ends) ÷ 2 = ({top}−{a}−{c})÷2 = {b}. Starting from the result and tracing back the cause — 'working backward' — is especially powerful in mazes and puzzles.",
            },
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
            en={
                "statement": f"There's a staircase of {n} steps, and you can climb 1 or 2 steps at a time. In how many different ways can you climb the staircase?",
                "answer": _en_plural(w, "way"),
                "distractors": [_en_plural(w - 1, "way"), _en_plural(w + 2, "way"), _en_plural(n * 2, "way")],
                "explanation": f"Count from small staircases. 1 step has 1 way, 2 steps have 2 ways. Splitting by whether the last move was 1 step or 2 steps gives 'ways for {n} steps = ways for {n - 1} steps + ways for {n - 2} steps'. Building up 1, 2, 3, 5, 8… gives {w} ways for {n} steps.",
                "mistakes": [(_en_plural(n * 2, "way"), "If listing them directly is hard, find the pattern starting from smaller staircases.")],
                "detail": f"This is the famous 'Fibonacci'. If the last move was 1 step, you had climbed {n - 1} steps before; if 2 steps, {n - 2} steps. The two cases don't overlap, so you add them: (n steps)=(n−1 steps)+(n−2 steps). So adding the previous two numbers as in 1,2,3,5,8,13… gives {w} ways for {n} steps. Breaking a big problem into 'one-step-smaller problems' like this is called a recurrence.",
            },
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
            en={
                "statement": f"There is a grid of paths {w} columns wide and {h} rows tall. How many shortest routes are there from the bottom-left corner to the top-right corner?",
                "answer": _en_plural(ans, "way"),
                "distractors": [_en_plural(ans - 2, "way"), _en_plural(ans + 2, "way"), _en_plural(w * h, "way")],
                "explanation": f"At any junction, the routes reaching it come only from the left or from below. So at each point write (number from the left)+(number from below) in turn. Fill the edges near the start with 1 and add across to the end: the finish has {ans} ways.",
                "mistakes": [(_en_plural(w * h, "way"), "You don't multiply the number of cells. Add up the route counts junction by junction.")],
                "detail": f"Route count at each point = the point on the left + the point below — this table you build up is exactly Pascal's triangle. In fact it is deciding the order of going right {w} times and up {h} times, so you can also get it at once as C({w}+{h}, {w}). Once you see 'shortest grid path = combinations', even a big grid isn't scary.",
            },
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
            en=(lambda cm, pg: {
                "statement": f"Beads in the order {' · '.join(cm.get(c, c) for c in colors)} are strung over and over. "
                             f"What color is the {n}th bead?",
                "answer": cm.get(ans, ans),
                "distractors": [cm.get(wrongs[0], wrongs[0]), cm.get(wrongs[1], wrongs[1]), "can’t tell"],
                "explanation": f"Since {k} beads repeat as one group, dividing {n} by {k} is the key. {n}÷{k} gives quotient {n // k} and "
                               f"remainder {n % k}, so it lands on bead #{pg} within a group — and #{pg} in the group is {cm.get(ans, ans)}.",
                "detail": f"For repeating problems, the remainder is the key. With {k} per group, where the {n}th lands is set by the remainder "
                          f"of {n}÷{k} (remainder 0 means the last, #{k}). Weekdays (7), clocks (12), and calendars all run on this 'remainder world'.",
            })({"빨간": "red", "노란": "yellow", "파란": "blue", "초록": "green", "보라": "purple", "주황": "orange", "분홍": "pink"},
               n % k if n % k else k),
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
            en={
                "statement": f"On a calendar, three numbers stacked vertically were chosen and their sum was {s}. What is the middle number?",
                "answer": str(mid),
                "distractors": [str(mid - 1), str(mid + 1), str(s // 2)],
                "explanation": f"On a calendar, numbers stacked vertically differ by 7. Writing the three as (middle−7), middle, (middle+7), the −7 and +7 cancel, so the sum is middle×3. {s}÷3={mid}, so the middle number is {mid}.",
                "mistakes": [(str(s // 2), "Don't divide by 2. The sum of the three is 3 times the middle number.")],
                "detail": f"The trick is to anchor on the middle number. The one above is −7 and the one below is +7, so they cancel and the sum = middle×3. Anchoring on the middle makes the symmetric terms vanish and shrinks the arithmetic. Three numbers in a horizontal row (−1, +1) or consecutive odd numbers work the same way: middle×3.",
            },
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
            en={
                "statement": f"{n} people had an average score of {m} points. When one more person joined, the average rose to {m + d} points. What was the new person's score?",
                "answer": f"{newcomer} points",
                "distractors": [f"{m + d} points", f"{m + 2 * d} points", f"{newcomer - d} points"],
                "explanation": f"Switch from averages to totals. The original total for {n} people is {n}×{m}={n * m} points, and for {n + 1} people to average {m + d} points the total must be {n + 1}×{m + d}={(n + 1) * (m + d)} points. That difference {(n + 1) * (m + d)}−{n * m}={newcomer} points is the new person's score.",
                "mistakes": [(f"{m + d} points", "Scoring just the new average won't raise the average — you have to pull everyone's average up.")],
                "detail": f"Average problems are easier as 'totals'. The first {n} people sum to {n}×{m}={n * m} points. For the new average {m + d} points the {n + 1} people must sum to {n + 1}×{m + d}={(n + 1) * (m + d)} points, so the new person's score = that difference = {newcomer} points. The newcomer must bring their own share of {m + d} points plus enough to lift each of the other {n} people by {d} points, so it is much higher.",
            },
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
            en={
                "statement": f"You want to lay go stones in a hollow square shape with {side} stones on each side, as in the picture. How many stones are needed in all?",
                "answer": f"{ans} stones",
                "distractors": [f"{4 * side} stones", f"{ans - 2} stones", f"{side * side} stones"],
                "explanation": f"Counting {side} on each of the four sides as {side}×4={4 * side} falls into a trap. The four corner stones each sit on two sides, so they get counted twice. Subtracting those 4 double-counted stones gives {4 * side}−4={ans}.",
                "mistakes": [(f"{4 * side} stones", "You counted the 4 corner stones twice."),
                             (f"{side * side} stones", "It's only the border, not a filled-in square.")],
                "detail": f"'Counting a border' is all about how you handle the overlaps. Another way: {side} on the top and bottom rows ({side}×2={side * 2}), then the two remaining sides have {side - 2} each without the corners (total {(side - 2) * 2}). Adding gives {side * 2}+{(side - 2) * 2}={ans} — the same. Either 'subtract' the overlap or split so there's 'no overlap' — seeing both roads give the same answer is reassuring.",
            },
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
            en={
                "statement": f"A {l1}cm candle burns {r1}cm each hour, and a {l2}cm candle burns {r2}cm each hour. If you light them at the same time, after how many hours will the two candles be the same length?",
                "answer": f"{t} hours",
                "distractors": [f"{t - 2} hours", f"{t + 2} hours", f"{l1 - l2} hours"],
                "explanation": f"Focus on the difference in length between the two candles. At the start the difference is {l1}−{l2}={l1 - l2}cm, and each hour the longer candle burns {r1 - r2}cm more, shrinking the difference by that much. After {l1 - l2}÷{r1 - r2}={t} hours the difference reaches 0, and at that moment both candles are {l1 - r1 * t}cm.",
                "mistakes": [(f"{l1 - l2} hours", f"You have to divide the difference of {l1 - l2}cm by 'the amount it shrinks each hour, {r1 - r2}cm'.")],
                "detail": "The key is looking at the 'difference' on its own. The gap between the two candle lengths shrinks each hour by (faster burn rate − slower burn rate). So the time to become equal = starting difference ÷ difference in rates. This is exactly the same structure as 'catching up (meeting)' — only distance becomes length and speed becomes burn rate.",
            },
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
            en={
                "statement": f"The picture shows a wall clock seen in a mirror (it looks like {mirror} o'clock). What is the actual time?",
                "answer": f"{actual} o'clock",
                "distractors": [f"{mirror} o'clock", f"{(actual + 6) % 12 or 12} o'clock", f"{(mirror + 1) % 12 or 12} o'clock"],
                "explanation": f"A mirror flips left and right only, so the 12 and 6 positions stay put. If it looks like {mirror} o'clock in the mirror, the real hand is on the opposite side of 12, at {actual} o'clock. It helps to remember that the real time and the mirror time add up to 12 ({actual}+{mirror}=12).",
                "mistakes": [(f"{mirror} o'clock", "You read it straight off the mirror. Left and right are flipped.")],
                "detail": f"A mirror flips left and right. When a clock is flipped about the 12 o'clock (top) axis, the time reads as '12 minus the real time'. So mirror {mirror} o'clock → real {actual} o'clock (12−{mirror}={actual}). To go the other way, from real to mirror, subtract from 12 the same way. Remember symmetry as 'tracing back across an axis' and you won't get confused.",
            },
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
            en={
                "statement": f"Using the number cards {cardtxt}, each exactly once, you make a three-digit number. "
                             f"What is the largest number you can make?",
                "answer": str(biggest),
                "distractors": [str(smallest), str(asgiven), str(swapped)],
                "explanation": f"To make the largest number, put bigger digits in higher places. Putting {desc[0]} in the hundreds, "
                               f"{desc[1]} in the tens, and {desc[2]} in the ones gives {biggest}.",
                "mistakes": [(str(smallest), "That’s the smallest number. For the largest, put big digits in the front places.")],
                "detail": "The largest number comes from placing bigger digits in higher place values — a digit in the hundreds place is "
                          "worth 100× its face value, so bigger digits should sit higher. The smallest is the reverse. Placing the best "
                          "option first like this is called the greedy method.",
            },
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
            en={
                "statement": f"Find the rule. {seqtxt}, □ — what number goes in the box?",
                "answer": str(nxt),
                "distractors": [str(nxt + d), str(seq[-1]), str(nxt + 1)],
                "explanation": f"Look at the gap between neighboring numbers. It goes {'up' if d > 0 else 'down'} by {abs(d)} each time, "
                               f"so after {seq[-1]} comes {seq[-1]} {sign} {abs(d)} = {nxt}.",
                "mistakes": [(str(seq[-1]), "Don’t just repeat the last number — add or subtract by the rule.")],
                "detail": "When the gap between neighbors stays constant, it’s an arithmetic sequence. Always write the gaps first: "
                          "a constant gap means arithmetic, a constant ratio means geometric. The nth term is (first) + (n−1)×(gap).",
            },
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
            figure={"type": "MATCHSTICK", "params": {"n": n}},
            detail=f"정사각형 하나는 변 4개지만, 옆에 붙이면 맞닿은 변 1개를 '공유'해요. 그래서 첫 칸은 4개, 다음부터는 3개씩만 늘어 총 {3 * n + 1}=3×{n}+1개. '공유하는 부분은 한 번만 센다'는 생각은 둘레·격자 세기에서 계속 쓰여요.",
            en={
                "statement": f"You join {n} equal squares in a row with matchsticks. How many matchsticks do you need in all?",
                "answer": _en_plural(matches, "matchstick"),
                "distractors": [_en_plural(4 * n, "matchstick"), _en_plural(3 * n, "matchstick"), _en_plural(4 * n - 1, "matchstick")],
                "explanation": f"One square needs 4 matchsticks. Each square you add on the right already shares its left side, so it only "
                               f"needs 3 more. So {n} squares need 4 + 3×{n - 1} = {matches}.",
                "mistakes": [(_en_plural(4 * n, "matchstick"), "Counting 4 per square double-counts the shared sides between neighbors.")],
                "detail": "A square has 4 sides, but joining one on the side shares 1 touching side. So the first cell needs 4 and each next "
                          "one adds only 3, giving 3n+1 in all. 'Count a shared part once' comes back again in perimeter and grid counting.",
            },
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
            en={
                "statement": f"There are {len(tops)} tops and {len(bottoms)} bottoms. Picking one top and one bottom, "
                             f"how many different outfits can you make?",
                "answer": _en_plural(n, "outfit"),
                "distractors": [_en_plural(len(tops) + len(bottoms), "outfit"), _en_plural(n - 1, "outfit"), _en_plural(n + 1, "outfit")],
                "explanation": f"For every top you can pair {len(bottoms)} bottoms, and there are {len(tops)} tops, "
                               f"so {len(tops)}×{len(bottoms)}={n}. Drawing a table and pairing them gives {n} as well.",
                "mistakes": [(_en_plural(len(tops) + len(bottoms), "outfit"), "Don’t add — multiply. Each top pairs with every bottom.")],
                "detail": "Choosing a top and choosing a bottom are independent steps, so you multiply (the multiplication principle) — "
                          "each top allows all the bottoms again. If it were 'just a top OR just a bottom', you’d add. Multiply vs. add = 'and' vs. 'or'.",
            },
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
            en={
                "statement": f"□{ones} + {addend} = {result}. What digit goes in the box? (□ is a single digit)",
                "answer": str(tens),
                "distractors": [str((tens + 1) % 10), str(result // 10), str(max(0, tens - 1))],
                "explanation": f"□{ones} is {result} minus {addend}. Since {result} − {addend} = {unknown}, the tens digit □ is {tens}. "
                               f"The ones digit {ones} matches too.",
                "mistakes": [(str(result // 10), "Don’t just answer the tens digit of the sum — subtract to check.")],
                "detail": f"A blank in an addition shows up right away when you undo it with subtraction. □{ones} is {result} minus "
                          f"{addend} = {unknown}. Revealing an unknown with the inverse operation is the seed of equations. Checking for "
                          "carries at each place lets you solve bigger puzzles too.",
            },
        )


# ── 24. 경우의 수 세기 — 곱의 원리 (난2, 자료와가능성) ───────────────────────
def gen_cases():
    from itertools import product
    scenarios = [
        ("동전 3개를 동시에 던질 때 나오는 경우(앞·뒤를 구별해요)", [["앞", "뒤"]] * 3,
         "tossing 3 coins at once (heads/tails distinguished)"),
        ("주사위 1개와 동전 1개를 함께 던질 때 나오는 경우", [[1, 2, 3, 4, 5, 6], ["앞", "뒤"]],
         "rolling one die and tossing one coin together"),
        ("두 사람이 가위바위보를 한 판 할 때 나오는 경우(누가 무엇을 냈는지 구별해요)", [["가위", "바위", "보"]] * 2,
         "two people playing one round of rock-paper-scissors (who threw what is distinguished)"),
        ("김밥 3종류와 음료 2종류 중 하나씩 고르는 경우", [["김밥1", "김밥2", "김밥3"], ["음료1", "음료2"]],
         "picking one of 3 kinds of sandwiches and one of 2 kinds of drinks"),
    ]
    for desc, spaces, en_desc in scenarios:
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
            en={
                "statement": f"How many different outcomes are there for {en_desc}?",
                "answer": _en_plural(n, "way"),
                "distractors": [_en_plural(wrong_sum, "way"), _en_plural(n - 1, "way"), _en_plural(n + 2, "way")],
                "explanation": f"Multiply the number of choices at each step: {' × '.join(str(len(s)) for s in spaces)} = {n}. "
                               f"Listing them all one by one also gives {n}.",
                "mistakes": [(_en_plural(wrong_sum, "way"), "Don’t add — multiply. Each first case branches into the next again.")],
                "detail": "The multiplication principle applies when each step’s choice doesn’t affect the others ('and'). By contrast, "
                          "mutually exclusive cases ('this or that', 'or') are added (the addition principle). Multiply vs. add = 'and' vs. 'or'. "
                          "Mixing the two freely is the heart of counting.",
            },
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
            en={
                "statement": f"Here's a new made-up rule: {desc.replace('가', 'a').replace('나', 'b')}. For example, {ea}{sym}{eb} = {ev}. So what is {qa}{sym}{qb}?",
                "answer": str(ans),
                "distractors": [str(qa * qb), str(ans + qb), str(ans - 2)],
                "explanation": f"Plug a={qa} and b={qb} straight into the rule to get {ans}. It's the same method as the example ({ea}{sym}{eb}={ev}). Even with an unfamiliar symbol, just follow the definition in order.",
                "mistakes": [(str(qa * qb), "You only multiplied the two numbers and skipped the rest of the rule.")],
                "detail": f"An unfamiliar symbol is all about 'following the defined order of operations exactly'. Check the rule with the example ({ea}{sym}{eb}={ev}), then swap in your numbers. The 'functions' you learn in later grades are exactly this idea — a box that gives a set output for what you put in. Don't fear a new symbol; follow the definition and any made-up operation works.",
            },
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
            en={
                "statement": f"Find the rule. {seqtxt}, □ — what number goes in the box?",
                "answer": str(nxt),
                "distractors": [str(seq[-1] + diffs[-1]), str(nxt + 1), str(seq[-1])],
                "explanation": f"Write the gaps between neighbors: {difftxt}. The gap grows by 1 each time, so the next gap is {nxt_diff}, "
                               f"and {seq[-1]}+{nxt_diff}={nxt}.",
                "mistakes": [(str(seq[-1] + diffs[-1]), "The gap isn’t constant — it’s growing. Take the next gap 1 larger.")],
                "detail": "When the gap isn’t constant, look at the 'gap of the gaps'. Here the gap grows by 1 each time (a difference "
                          "sequence). Such numbers show up in triangular numbers (1,3,6,10…) as a shape grows a row at a time. Seeing the "
                          "'change of the change' is the key to cracking harder rules.",
            },
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
        en_people = ["A", "B", "C"]
        en_texts = []
        for j, st2 in enumerate(cfg):
            if st2 == "innocent":
                en_texts.append(f'{en_people[j]}: "I did not break it."')
            else:
                en_texts.append(f'{en_people[j]}: "{en_people[st2[1]]} broke it."')
        en_body = " / ".join(en_texts)
        add(
            "truthone", "DATA_POSSIBILITY", 4, ["진실과 거짓", "경우 따져보기"],
            f"꽃병이 깨졌어요. 세 사람 중 한 명만 진실을 말하고 나머지 둘은 거짓말을 해요. {body} 꽃병을 깬 사람은 누구일까요?",
            people[culprit], [people[(culprit + 1) % 3], people[(culprit + 2) % 3], "알 수 없다"],
            f"한 사람씩 '이 사람이 범인이라면?' 하고 가정해 진술들의 참·거짓을 세어 봐요. 참말한 사람이 정확히 한 명이 되는 경우는 {people[culprit]}이(가) 범인일 때뿐이에요. 그래서 답은 {people[culprit]}{_copula(people[culprit])}.",
            [("알 수 없다", "모든 경우를 하나씩 따져 보면 답은 하나로 정해져요.")],
            detail="'한 명만 진실'이 열쇠예요. 범인을 한 사람씩 가정하고, 그때 각자의 말이 참인지 세어 보세요. 진실을 말한 사람이 '정확히 한 명'이 되는 가정만 정답이에요. 이렇게 모든 경우를 표로 만들어 '조건에 맞는 하나'만 남기는 게 논리 퍼즐의 정석이에요.",
            en={
                "statement": f"A vase got broken. Among the three people, only one tells the truth and the other two lie. {en_body} Who broke the vase?",
                "answer": en_people[culprit],
                "distractors": [en_people[(culprit + 1) % 3], en_people[(culprit + 2) % 3], "unknown"],
                "explanation": f"Take each person in turn and suppose 'what if this person did it?', then count how many statements come out true. The only case where exactly one person tells the truth is when {en_people[culprit]} is the culprit. So the answer is {en_people[culprit]}.",
                "mistakes": [("unknown", "Work through every case one by one and the answer is pinned down to a single person.")],
                "detail": "'Only one tells the truth' is the key. Suppose each person is the culprit and count whether each person's statement is true. Only the assumption that makes 'exactly one' person truthful is correct. Building a table of all cases and keeping just the 'one that fits the condition' is the classic way to crack logic puzzles.",
            },
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
            figure={"type": "MATCHSTICK", "params": {"n": n, "tri": 1}},
            detail=f"정삼각형 1개는 3개지만, 옆에 붙이면 맞닿는 한 변을 함께 써요. 그래서 첫 개는 3개, 다음부터는 2개씩만 늘어 3+2×({n}−1)={matches}개. '붙는 곳은 한 번만 센다'는 이 생각은 정사각형 잇기·도형 둘레에서 똑같이 쓰여요. 몇 곳이 공유되는지만 세면 끝이에요.",
            en={
                "statement": f"You join {n} equal equilateral triangles in a row with matchsticks (alternating up and down). "
                             f"How many matchsticks do you need in all?",
                "answer": _en_plural(matches, "matchstick"),
                "distractors": [_en_plural(3 * n, "matchstick"), _en_plural(2 * n, "matchstick"), _en_plural(3 * n - 1, "matchstick")],
                "explanation": f"One triangle needs 3 matchsticks. Each next triangle shares one touching side, so it needs only 2 more. "
                               f"So {n} triangles need 3 + 2×{n - 1} = {matches}.",
                "mistakes": [(_en_plural(3 * n, "matchstick"), "Counting 3 per triangle double-counts the shared sides between neighbors.")],
                "detail": "One triangle has 3 sides, but joining another shares one touching side. So the first needs 3 and each next adds only "
                          "2, giving 3+2×(n−1). 'Count a shared part once' also drives joining squares and figure perimeters.",
            },
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
            en={
                "statement": f"You roll 2 dice at the same time. In how many ways can the two faces add up to {k}? (the two dice are told apart)",
                "answer": _en_plural(cnt, "way"),
                "distractors": [_en_plural(unordered, "way"), _en_plural(cnt - 1, "way"), _en_plural(cnt + 1, "way")],
                "explanation": f"List the pairs in order starting from the smallest face. Since the two dice are told apart, (first {ex_a}, second {ex_b}) and (first {ex_b}, second {ex_a}) count as different cases. Counting that way gives {cnt} ways in all.",
                "mistakes": [(_en_plural(unordered, "way"), f"You counted without telling the order apart. (first {ex_a}, second {ex_b}) and (first {ex_b}, second {ex_a}) are different cases.")],
                "detail": f"The two dice are distinguishable, so a different order is a different case. Draw the 6×6=36-cell table and count the cells that sum to {k} — nothing gets missed. The distribution of the sum of two dice is symmetric about 7, so the farther from 7, the fewer the cases — knowing this symmetry lets you estimate the count without listing everything.",
            },
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
            en={
                "statement": f"A number leaves a remainder of {ra} when divided by {a}, and a remainder of {rb} when divided by {b}. What is the smallest two-digit number like this?",
                "answer": str(ans),
                "distractors": [str(nxt), str(ans + 1), str(max(10, ans - 1))],
                "explanation": f"Both conditions must hold at once. List numbers that leave remainder {rb} when divided by {b}, from smallest up, and check which also leave remainder {ra} when divided by {a}; the first two-digit number that works is {ans}. ({ans} divided by {a} leaves remainder {ra}, and divided by {b} leaves remainder {rb}.)",
                "mistakes": [(str(nxt), "That number also fits both conditions, but there is a smaller two-digit number.")],
                "detail": f"Numbers that satisfy both division conditions at once repeat regularly, every least common multiple of {a} and {b} ({a * b // gcd(a, b)}). So once you find one answer, adding {a * b // gcd(a, b)} to it again and again gives all the others. This is the basic idea behind the 'Chinese Remainder Theorem', which appears even in old Chinese math books.",
            },
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
        colors_en = ", ".join({"빨강": "red", "파랑": "blue", "노랑": "yellow", "초록": "green", "검정": "black", "흰색": "white"}[x] for x in colors)
        add(
            "pigeon", "DATA_POSSIBILITY", 5, ["비둘기집", "최악의 경우"],
            f"서랍에 {c}가지 색({', '.join(colors)}) 양말이 잔뜩 섞여 있어요. 어두워서 색이 안 보일 때, 같은 색 한 켤레(2짝)를 확실히 꺼내려면 최소 몇 짝을 꺼내야 할까요?",
            f"{ans}짝", [f"{c}짝", f"{c * 2}짝", f"{ans + 1}짝"],
            f"운이 가장 나쁠 때를 생각해요. {c}짝을 꺼냈는데 공교롭게 색이 모두 다를 수도 있어요({c}가지니까). 하지만 한 짝만 더 꺼내면({ans}짝) 반드시 이미 나온 색과 겹쳐 한 켤레가 완성돼요. 그래서 {ans}짝이에요.",
            [(f"{c}짝", f"{c}짝이면 운 나쁘게 색이 다 다를 수 있어요. 한 짝을 더 꺼내야 확실해요.")],
            detail=f"이게 바로 '비둘기집 원리'예요: 서랍(색)이 {c}칸인데 {c}+1={ans}짝을 넣으면 반드시 한 칸에 2짝이 겹쳐요. 규칙을 바꿔 '같은 색 3짝'을 원하면, 색마다 2짝까지 다를 수 있으니 2×{c}+1짝이 필요해요. 항상 '가장 운 나쁜 경우를 먼저 그린 뒤 +1'로 생각하면 이런 '확실히 보장' 문제는 다 풀려요.",
            en={
                "statement": f"A drawer has {c} colors of socks ({colors_en}) all jumbled together. In the dark where you can't see the colors, at least how many socks must you pull out to be sure of getting a matching pair (2 socks of the same color)?",
                "answer": _en_plural(ans, "sock"),
                "distractors": [_en_plural(c, "sock"), _en_plural(c * 2, "sock"), _en_plural(ans + 1, "sock")],
                "explanation": f"Think of the unluckiest case. You could pull {c} socks and happen to get all different colors (since there are {c} of them). But pulling just one more ({ans} socks) must match a color already out, completing a pair. So the answer is {ans} socks.",
                "mistakes": [(_en_plural(c, "sock"), f"With {c} socks you could unluckily get all different colors. You need one more sock to be sure.")],
                "detail": f"This is exactly the 'pigeonhole principle': with {c} drawers (colors), putting in {c}+1={ans} socks forces two into one drawer. Change the rule to '3 socks of the same color' and, since each color can differ up to 2 socks, you'd need 2×{c}+1 socks. Always thinking 'draw the worst case first, then +1' solves these 'guaranteed' problems.",
            },
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
        label_en = {
            "정확히 두 면만 색칠된": "with exactly two faces painted",
            "정확히 한 면만 색칠된": "with exactly one face painted",
            "어느 면도 색칠되지 않은": "with no face painted",
        }[label]
        if k == 2:
            expl_en = f"Pieces with two painted faces sit on the cube's 'edges'. Removing the corner (three-face) pieces leaves {n - 2} on each edge, and there are 12 edges. 12×{n - 2}={ans}."
        elif k == 1:
            expl_en = f"Pieces with only one painted face gather inside each face. Each face has {n - 2}×{n - 2}={(n - 2) ** 2}, and there are 6 faces. 6×{(n - 2) ** 2}={ans}."
        else:
            expl_en = f"Pieces with no painted face are the hidden block inside. {n - 2}×{n - 2}×{n - 2}={ans}."
        add(
            "cube", "SHAPE_MEASUREMENT", 5, ["쌓기나무", "공간 추론"],
            f"한 모서리가 {n}칸인 정육면체의 겉면을 모두 색칠한 뒤 1칸짜리 작은 정육면체로 잘랐어요. {label} 작은 정육면체는 몇 개일까요?",
            f"{ans}개", [f"{ans + 6}개", f"{n ** 3}개", f"{max(1, ans - 4)}개"],
            expl,
            [(f"{n ** 3}개", "전체 조각 수가 아니라, 조건에 맞는 조각만 세어야 해요.")],
            detail=f"작은 조각은 '위치'로 종류가 갈려요: 꼭짓점(3면 칠해짐) 8개, 모서리(2면) 각 {n - 2}개씩 12줄, 면 안쪽(1면) 각 {(n - 2) ** 2}개씩 6면, 속(0면) {(n - 2) ** 3}개. 위치별로 나눠 세면 어떤 조건이 와도 빠짐없이 셀 수 있어요. 3D를 '겉·모서리·꼭짓점·속'으로 분해하는 눈이 공간 감각의 핵심이에요.",
            en={
                "statement": f"You paint all the outer faces of a cube that is {n} cells along each edge, then cut it into unit (1-cell) cubes. How many of the small cubes {label_en} are there?",
                "answer": _en_plural(ans, "cube"),
                "distractors": [_en_plural(ans + 6, "cube"), _en_plural(n ** 3, "cube"), _en_plural(max(1, ans - 4), "cube")],
                "explanation": expl_en,
                "mistakes": [(_en_plural(n ** 3, "cube"), "Don't count the total number of pieces — count only the pieces that fit the condition.")],
                "detail": f"The small pieces split into kinds by 'position': 8 corners (three faces painted), {n - 2} on each of the 12 edges (two faces), {(n - 2) ** 2} inside each of the 6 faces (one face), and {(n - 2) ** 3} inside (no faces). Counting position by position lets you count without missing any, whatever the condition. Seeing 3D as 'surface, edge, corner, inside' is the heart of spatial sense.",
            },
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
            en={
                "statement": f"How many divisors does {num} have in all?",
                "answer": _en_plural(ans, "divisor"),
                "distractors": [_en_plural(ans - 2, "divisor"), _en_plural(ans + 2, "divisor"), _en_plural(ans + 1, "divisor")],
                "explanation": f"Find every divisor by pairing them as 'small × large'. Listing the numbers that divide {num} evenly, in order from 1, gives {', '.join(map(str, divisors))} — {ans} in all.",
                "mistakes": [(_en_plural(ans + 1, "divisor"), "Check by pairing that you didn't miss a divisor or count one twice.")],
                "detail": "There's a shortcut for the number of divisors. Factor into primes, add 1 to each exponent, and multiply. For example, 12=2×2×3, so (2+1)×(1+1)=6. You're viewing it as the combinations of 'pick 0-2 twos, pick 0-1 threes, and multiply'. This method counts large numbers quickly too.",
            },
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
            en={
                "statement": f"There is a two-digit number. Its tens digit and ones digit add up to {s}, and the tens digit is {d} more than the ones digit. What is the number?",
                "answer": str(ans),
                "distractors": [str(reversed_num), str(ans + 1), str(ans - 1)],
                "explanation": f"Use both clues together. (tens)+(ones)={s}, (tens)−(ones)={d}. Adding the two equations cancels the ones digit and leaves twice the tens digit, so ({s}+{d})÷2={tens} is the tens digit. The ones digit is {s}−{tens}={ones}, so the answer is {ans}.",
                "mistakes": [(str(reversed_num), "You swapped the tens and ones digits. The tens digit is the larger one.")],
                "detail": f"When you know a sum and a difference, 'adding or subtracting the two equations' is the shortcut. Sum + difference cancels the smaller part and leaves twice the larger: ({s}+{d})÷2={tens} as the tens digit. This 'sum-and-difference method' works widely for problems where two unknowns are tangled together — ages, counts, distances.",
            },
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
            en={
                "statement": f"A clock points exactly to {h} o'clock. What is the smaller angle formed by the hour hand and the minute hand, in degrees?",
                "answer": f"{ans}°",
                "distractors": [f"{ans + 30}°", f"{max(0, ans - 30)}°", f"{ans + 60}°"],
                "explanation": f"One full turn of a clock is 360° and there are 12 number marks, so each mark is 360÷12=30°. At exactly {h} o'clock the hour and minute hands are {h} marks apart, so {h}×30={ans}°.",
                "mistakes": [(f"{ans + 30}°", "Each mark is 30°. Check you counted the number of marks apart correctly.")],
                "detail": f"Splitting a clock's full 360° into 12 marks makes each mark 30°. On the hour the minute hand points at 12 and the hour hand at {h}, so {h} marks = {ans}°. But as the minute hand turns, the hour hand slowly follows it (0.5° per minute) — so for a 'so many hours and minutes' angle you must also add the hour hand's movement to be exact.",
            },
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
            en={
                "statement": f"There is a rectangular grid divided into {w} columns and {h} rows. How many rectangles of all sizes can you find inside this grid?",
                "answer": _en_plural(ans, "rectangle"),
                "distractors": [_en_plural(w * h, "rectangle"), _en_plural(ans - 3, "rectangle"), _en_plural(ans + 3, "rectangle")],
                "explanation": f"A rectangle is fixed once you pick 2 vertical lines and 2 horizontal lines. Choosing 2 of the {w + 1} vertical lines → {comb(w + 1, 2)} ways, and 2 of the {h + 1} horizontal lines → {comb(h + 1, 2)} ways. Multiplying gives {comb(w + 1, 2)}×{comb(h + 1, 2)}={ans}.",
                "mistakes": [(_en_plural(w * h, "rectangle"), "Don't count only the single squares — count every larger rectangle made of several squares too.")],
                "detail": f"One rectangle is fixed by '2 vertical lines + 2 horizontal lines'. It is choosing 2 of the {w + 1} vertical lines and 2 of the {h + 1} horizontal lines, so C({w + 1},2)×C({h + 1},2)={comb(w + 1, 2) * comb(h + 1, 2)}. Instead of counting one by one, finding 'what you pick to fix one' makes the counting simple.",
            },
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
            en={
                "statement": f"Find the rule. {seqtxt}, □ — what number goes in □?",
                "answer": str(nxt),
                "distractors": [str(seq[-1] + (seq[-1] - seq[-2])), str(nxt + r), str(nxt + seq[-1])],
                "explanation": f"Look at how many times each number grows. {seq[1]}÷{seq[0]}={r}, {seq[2]}÷{seq[1]}={r} — it is ×{r} every time. So after {seq[-1]} comes {seq[-1]}×{r}={nxt}.",
                "mistakes": [(str(seq[-1] + (seq[-1] - seq[-2])), "It is not a constant amount being added — a constant amount is being multiplied (geometric).")],
                "detail": f"The key is telling apart arithmetic (adding a constant) and geometric (multiplying by a constant). Here it is ×{r} every time, so it is geometric. A geometric sequence looks like an arithmetic one at first but soon explodes (2, 4, 8, 16…). Like the thickness of folded paper or a rumor spreading, 'multiplied change' is far faster than our intuition.",
            },
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
            en={
                "statement": f"Among the whole numbers from 1 to {total_n}, how many are divisible by neither {a} nor {b}?",
                "answer": _en_plural(ans, "number"),
                "distractors": [_en_plural(total_n - cnt_a - cnt_b, "number"), _en_plural(cnt_a + cnt_b, "number"), _en_plural(ans + 2, "number")],
                "explanation": f"First subtract the {cnt_a} multiples of {a} and the {cnt_b} multiples of {b}. But the multiples of {lcm} ({cnt_lcm} of them) were subtracted twice, so add them back once. {total_n}−{cnt_a}−{cnt_b}+{cnt_lcm}={ans}.",
                "mistakes": [(_en_plural(total_n - cnt_a - cnt_b, "number"), f"You subtracted the multiples of {lcm} twice — you have to add them back once (inclusion-exclusion).")],
                "detail": f"If you subtract the multiples of {a} and also the multiples of {b}, the numbers that are multiples of both (multiples of {lcm}) get subtracted twice. So add them back once: {total_n}−{cnt_a}−{cnt_b}+{cnt_lcm}={ans}. This 'add back what overlaps' is the heart of inclusion-exclusion, and drawing a Venn diagram shows you why.",
            },
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
            en={
                "statement": f"What is each interior angle of a regular {n}-gon, in degrees?",
                "answer": f"{ans}°",
                "distractors": [f"{360 // n}°", f"{total}°", f"{180 - ans}°"],
                "explanation": f"The interior angles of a {n}-gon add up to ({n}−2)×180={total}°. A regular polygon has all interior angles equal, so divide by {n}. {total}÷{n}={ans}°.",
                "mistakes": [(f"{360 // n}°", "That is one exterior angle. An interior angle is 180 minus the exterior angle.")],
                "detail": f"Drawing diagonals from one vertex splits an n-gon into (n−2) triangles. So the sum of the interior angles = (n−2)×180 = ({n}−2)×180 = {total}°. A regular polygon divides this equally by n, giving each interior angle {ans}°. Splitting a shape into pieces you know (triangles) is an all-purpose key for area and angles.",
            },
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
            en={
                "statement": f"How many diagonals can be drawn in a regular {n}-gon in all?",
                "answer": _en_plural(ans, "diagonal"),
                "distractors": [_en_plural(n * (n - 3), "diagonal"), _en_plural(n - 3, "diagonal"), _en_plural(n * (n - 1) // 2, "diagonal")],
                "explanation": f"From one vertex you draw diagonals to {n}−3={n - 3} vertices — every vertex except itself and its two neighbors (which make sides). With {n} vertices that gives {n}×{n - 3}, but each diagonal was counted twice, once from each end, so divide by 2. {n}×{n - 3}÷2={ans}.",
                "mistakes": [(_en_plural(n * (n - 3), "diagonal"), "You counted each diagonal twice, once at each of its two vertices. Divide by 2.")],
                "detail": f"A diagonal is 'a segment joining two vertices that is not a side'. Choosing 2 of the {n} vertices can be done in C({n},2)={n * (n - 1) // 2} ways, and taking away the {n} sides leaves {n * (n - 1) // 2}−{n}={ans}. That matches the earlier '{n - 3} from each vertex, then divide by 2' — building the habit of checking that different ways of counting give the same answer reduces mistakes.",
            },
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
            en={
                "statement": f"At {h}:{m:02d}, what is the smaller angle formed by the hour hand and the minute hand, in degrees?",
                "answer": f"{ans}°",
                "distractors": [f"{ans + 15}°", f"{ans + 30}°", f"{ans + 45}°"],
                "explanation": f"At {m} minutes the minute hand points at the 6, the 180° position. The hour hand has moved past {h} o'clock by {m} minutes, to {30 * h}+{m // 2}={hour_pos}°. The gap between the two positions, |{hour_pos}−180|={ans}°, is the angle between them.",
                "mistakes": [(f"{ans + 15}°", "Check you didn't forget that the hour hand also moved a little as the minute hand moved.")],
                "detail": f"The key is that 'the hour hand moves every minute too'. It moves 30° in 60 minutes, that is 0.5° per minute. So at {h}:{m:02d} the hour hand is at {30 * h}+{m}×0.5={hour_pos}°. The minute hand moves 6° per minute, so at {m} minutes it is at {m * 6}°. The difference between the two angles is the angle between them. Once you know each hand's 'speed', you can compute the angle at any time.",
            },
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
            en={
                "statement": f"Among rectangles with a perimeter of {p}cm, when the area is largest, what is that area in cm²? (the width and height are whole numbers)",
                "answer": f"{best}cm²",
                "distractors": [f"{half}cm²", f"{best + side}cm²", f"{best - side}cm²"],
                "explanation": f"With a perimeter of {p}, width+height={p}÷2={half} is fixed. When the sum of two numbers is fixed, the product (area) grows the closer the two are, so it is largest when width=height={half}÷2={side}. The area is then {side}×{side}={best}cm².",
                "mistakes": [(f"{half}cm²", "You need width×height (the area), not the value of width+height.")],
                "detail": f"Two numbers with a fixed sum have a larger product the closer they are, and the largest when equal (a square!). Since width+height={half} is fixed, the square split equally into {half}÷2={side} each has the maximum area {best}cm². Conversely, for a fixed area the perimeter is smallest when it is a square. This 'extreme when equal' is a principle that shows up all over nature and economics.",
            },
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
            figure={"type": "CUBE_STACK", "params": {"w": a, "d": b}, "heights": [c] * (a * b)},
            detail=f"겉넓이는 '마주 보는 세 쌍'으로 봐요: 앞뒤({b}×{c}), 좌우({a}×{c}), 위아래({a}×{b}) 각 2개씩이라 2×({a * b}+{b * c}+{a * c})={ans}㎠. 부피(속을 채우는 칸 수)와 겉넓이(겉을 감싸는 넓이)를 헷갈리지 않는 게 중요해요 — 상자를 포장하는 종이가 겉넓이랍니다.",
            en={
                "statement": f"Small 1cm cubes are stacked with no gaps to build a rectangular box that is {a} cubes wide, {b} cubes deep, and {c} cubes tall. What is the surface area of this box, in cm²?",
                "answer": f"{ans}cm²",
                "distractors": [f"{volume}cm²", f"{a * b + b * c + a * c}cm²", f"{ans + 4}cm²"],
                "explanation": f"A rectangular box has three pairs of opposite faces. The three kinds of faces have areas {a}×{b}={a * b}, {b}×{c}={b * c}, {a}×{c}={a * c}. There are two of each, so 2×({a * b}+{b * c}+{a * c})={ans}cm².",
                "mistakes": [(f"{volume}cm²", "That's the volume (the number of cubes stacked). Surface area is the sum of the areas of the outer faces.")],
                "detail": f"Think of surface area as 'three pairs of opposite faces': front-back ({b}×{c}), left-right ({a}×{c}), top-bottom ({a}×{b}), two of each, so 2×({a * b}+{b * c}+{a * c})={ans}cm². The key is not to confuse volume (the number of cells filling the inside) with surface area (the area wrapping the outside) — the paper that wraps a box is its surface area.",
            },
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
            en={
                "statement": f"What is each exterior angle of a regular {n}-gon, in degrees?",
                "answer": f"{ans}°",
                "distractors": [f"{(n - 2) * 180 // n}°", "360°", f"{ans * 2}°"],
                "explanation": f"For any polygon, all exterior angles add up to 360°. A regular {n}-gon has all exterior angles equal, so 360÷{n}={ans}°.",
                "mistakes": [(f"{(n - 2) * 180 // n}°", "That is one interior angle. An exterior angle is 360 divided by the number of vertices.")],
                "detail": f"Regular or not, all exterior angles of a polygon always add up to 360° — as you walk once around a polygon your direction turns one full turn (360°). So a regular {n}-gon has 360÷{n}={ans}°. Since interior+exterior=180, the interior angle comes right out too. The fact that 'one full turn is 360' is the whole of exterior-angle problems.",
            },
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
            en={
                "statement": "How many stacking blocks are there in the picture? (count the hidden blocks behind and below, too)",
                "answer": _en_plural(ans, "block"),
                "distractors": [_en_plural(ans - 1, "block"), _en_plural(ans + 1, "block"), _en_plural(max(1, ans - 2), "block")],
                "explanation": f"Count how many layers each column has and add them: {' + '.join(str(h) for h in heights)} = {ans}. Even hidden behind the front ones, the ones below are filled in.",
                "mistakes": [(_en_plural(max(1, ans - 2), "block"), "Count the blocks hidden behind or above the front ones too.")],
                "detail": f"The number of stacking blocks equals the sum of the layer counts written on each cell of the 'top-view'. Even hidden behind or above, knowing each column's height lets you count exactly. Adding the layer counts one by one gives {ans}. Thinking 'from the top' lets you count without missing any, no matter how complex.",
            },
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
            en={
                "statement": "How many stacking blocks are there in the picture? (count the ones hidden behind, too)",
                "answer": _en_plural(ans, "block"),
                "distractors": [_en_plural(ans - 1, "block"), _en_plural(ans + 1, "block"), _en_plural(max(1, ans - 2), "block")],
                "explanation": f"Add each column’s height: {' + '.join(str(h) for h in heights)} = {ans}. Even hidden behind the front ones, "
                               f"the back and bottom are filled in.",
                "mistakes": [(_en_plural(ans - 1, "block"), "Count the blocks hidden behind the front ones too.")],
                "detail": "The number of blocks equals the sum of the heights on each cell of the top-view. Even when some are hidden, "
                          "knowing each column’s height lets you count exactly. Thinking 'from the top' works no matter how complex.",
            },
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
            en={
                "statement": "What is the area of the shaded shape? (each grid cell is 1 cm²)",
                "answer": f"{area} cm²",
                "distractors": [f"{area + 2} cm²", f"{area - 2} cm²", f"{area + 4} cm²"],
                "explanation": f"Count the cells, or split into rectangles (or subtract an empty rectangle from a bigger one) → {area} cm².",
                "detail": "Area can be found two ways — 'subtract the empty part from a bigger shape' and 'split into pieces and add'. Getting the same answer both ways catches mistakes. More than memorizing formulas, the key is imagining how to cut and rearrange. (A triangle = half a rectangle; a parallelogram = a rectangle once you cut and move one side; a trapezoid = half a parallelogram when flipped and joined.)",
            },
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
            en={
                "statement": "What is the area of the shaded triangle, in cm²? (each grid square is 1 cm²)",
                "answer": f"{area}cm²",
                "distractors": [f"{b * h}cm²", f"{area + 2}cm²", f"{area - 2}cm²"],
                "explanation": f"It is a right triangle with base {b} squares and height {h} squares. Triangle area = base×height÷2 = {b}×{h}÷2 = {area}cm².",
                "mistakes": [(f"{b * h}cm²", "A triangle is half of a rectangle — be sure to divide base×height by 2.")],
                "detail": "Area can be found two ways — 'subtract the empty part from a bigger shape' and 'split it into pieces and add them up'. Finding it both ways and checking the answers match catches mistakes. Rather than memorizing formulas, the key to area is picturing 'how to cut and paste'. (Triangle = half a rectangle; parallelogram = cut off one side and paste it to make a rectangle; trapezoid = flip and paste to make half a parallelogram.)",
            },
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
            en={
                "statement": "What is the area of the shaded parallelogram, in cm²? (each grid square is 1 cm²)",
                "answer": f"{area}cm²",
                "distractors": [f"{boxw * height}cm²", f"{area + 3}cm²", f"{area - 2}cm²"],
                "explanation": f"A parallelogram's area = base×height even when it is slanted. Base {base} squares, (perpendicular) height {height} squares → {base}×{height} = {area}cm².",
                "mistakes": [(f"{boxw * height}cm²", f"Use base×perpendicular height, not the surrounding rectangle ({boxw}×{height}).")],
                "detail": "Area can be found two ways — 'subtract the empty part from a bigger shape' and 'split it into pieces and add them up'. Finding it both ways and checking the answers match catches mistakes. Rather than memorizing formulas, the key to area is picturing 'how to cut and paste'. (Triangle = half a rectangle; parallelogram = cut off one side and paste it to make a rectangle; trapezoid = flip and paste to make half a parallelogram.)",
            },
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
            en={
                "statement": "What is the area of the shaded trapezoid, in cm²? (each grid square is 1 cm²)",
                "answer": f"{area}cm²",
                "distractors": [f"{(a + bb) * h}cm²", f"{area + 3}cm²", f"{area - 2}cm²"],
                "explanation": f"Trapezoid area = (top side+bottom side)×height÷2 = ({a}+{bb})×{h}÷2 = {area}cm².",
                "mistakes": [(f"{(a + bb) * h}cm²", "After (top side+bottom side)×height, be sure to ÷2.")],
                "detail": "Area can be found two ways — 'subtract the empty part from a bigger shape' and 'split it into pieces and add them up'. Finding it both ways and checking the answers match catches mistakes. Rather than memorizing formulas, the key to area is picturing 'how to cut and paste'. (Triangle = half a rectangle; parallelogram = cut off one side and paste it to make a rectangle; trapezoid = flip and paste to make half a parallelogram.)",
            },
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
            en={
                "statement": "This is a tilted shape on a grid. What is the area of the shaded part, in cm²? (each grid square is 1 cm²)",
                "answer": f"{area}cm²",
                "distractors": [f"{box}cm²", f"{area + 2}cm²", f"{area - 2}cm²"],
                "explanation": f"For a tilted shape that doesn't fit the squares neatly, use 'boxing it in'. From the surrounding rectangle {cols}×{rows}={box}cm², subtract the total area of the four leftover right triangles at the corners, {tri}cm². {box}−{tri}={area}cm².",
                "mistakes": [(f"{box}cm²", "You have to subtract the corner triangles from the surrounding rectangle to get the shape's area.")],
                "detail": "Area can be found two ways — 'subtract the empty part from a bigger shape' and 'split it into pieces and add them up'. Finding it both ways and checking the answers match catches mistakes. Rather than memorizing formulas, the key to area is picturing 'how to cut and paste'. (Triangle = half a rectangle; parallelogram = cut off one side and paste it to make a rectangle; trapezoid = flip and paste to make half a parallelogram.)",
            },
        )


# ── 51. 삼각형 개수 세기 (도형과측정) — 그림 필수(TRIANGLE_FAN) ────────────────
def gen_shape_count():
    # family를 난이도별로 분리(id는 family+idx라 한 family가 여러 난이도에 걸치면 id가 충돌)
    for diff, ks, fam in [(4, [2, 3, 4], "trianglefan"), (6, [5, 6, 7], "trianglefanx")]:
        for k in ks:
            lines = k + 2                       # 밑변으로 가는 선(양옆 2 + 내부 k)
            ans = lines * (lines - 1) // 2       # 선 2개를 고를 때마다 삼각형 1개
            small = k + 1                        # 가장 작은 삼각형 개수
            # trianglefan(난4)·trianglefanx(난6) 둘 다 영어 뱅크에 넣는다(문항 구조가 같아 같은 영어 dict 재사용).
            en_fan = {
                "statement": "How many triangles can you find in the picture? (count larger triangles made of several small ones too)",
                "answer": _en_plural(ans, "triangle"),
                "distractors": [_en_plural(small, "triangle"), _en_plural(ans - 2, "triangle"), _en_plural(ans + 3, "triangle")],
                "explanation": f"There are {lines} lines drawn from the apex down to the base. Choosing any 2 of these lines makes exactly one triangle between them. "
                               f"Choosing 2 from {lines} = {lines}×{lines - 1}÷2 = {ans}. (From the {small} smallest triangles up to those made of two or three joined, none missed.)",
                "mistakes": [(_en_plural(small, "triangle"), "Don't count only the smallest triangles — count the larger ones made of several joined together too.")],
                "detail": f"A triangle appears each time you choose '2 lines going to the base'. So with {lines} lines the number of triangles = choosing 2 from {lines} = {lines}×{lines - 1}÷2 = {ans}. Each extra line adds (number of lines−1) more triangles. It's easy to miss some counting one by one, so recasting it as 'choose 2' keeps it accurate.",
            }
            add(
                fam, "SHAPE_MEASUREMENT", diff, ["삼각형 개수", "체계적 세기"],
                "그림에서 찾을 수 있는 삼각형은 모두 몇 개일까요? (작은 삼각형을 여러 개 합친 큰 삼각형도 세어요)",
                f"{ans}개", [f"{small}개", f"{ans - 2}개", f"{ans + 3}개"],
                f"꼭짓점에서 밑변으로 그은 선이 모두 {lines}개예요. 이 선들 중 2개를 고르면 그 사이에 삼각형이 하나씩 생겨요. "
                f"{lines}개에서 2개 고르기 = {lines}×{lines - 1}÷2 = {ans}개. (가장 작은 삼각형 {small}개부터 둘씩·셋씩 합친 것까지 빠짐없이.)",
                [(f"{small}개", "가장 작은 삼각형만 세지 말고, 여러 개를 합친 큰 삼각형도 빠짐없이 세어요.")],
                figure={"type": "TRIANGLE_FAN", "params": {"cevians": k}},
                detail=f"삼각형은 '밑변으로 가는 선 2개'를 고를 때마다 하나씩 생겨요. 그래서 선이 {lines}개면 삼각형 수 = {lines}개에서 2개 고르기 = {lines}×{lines - 1}÷2 = {ans}개. 선이 하나 늘 때마다 삼각형은 (선의 개수−1)개씩 늘어난답니다. 하나씩 세다 빠뜨리기 쉬우니, 이렇게 '2개 고르기'로 바꿔 세면 정확해요.",
                en=en_fan,
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
            en={
                "statement": "This is the net of a cube (dice-shaped) box. When you fold it into the box, how many pips are on the face opposite the shaded face?",
                "answer": f"{ans}",
                "distractors": pool[:3],
                "explanation": f"Folding the net up in your head, the face opposite the shaded face (which has {q} pips) has {ans} pips. "
                               f"The faces that share an edge with the shaded face ({', '.join(str(a) for a in adj)}) become side faces when folded, so they are not opposite it.",
                "mistakes": [(f"{adj[0]}", "A face directly attached in the net becomes a side face when folded — it is not the opposite face.")],
                "detail": f"When you fold the net, a face sharing an edge with the shaded face bends 90° and becomes a 'side face'. So the opposite face is one of the faces not attached to it ({ans}). Tip: in a straight row of four faces, faces 'one apart' are opposite each other. If folding the box in your head is hard, cross off the attached (side) faces one by one, and the face left over is the answer.",
            },
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
            en={
                "statement": "How many stacking blocks are there in the picture?",
                "answer": _en_plural(ans, "block"),
                "distractors": [_en_plural(ans - 1, "block"), _en_plural(ans + 1, "block"), _en_plural(ans + 2, "block")],
                "explanation": f"Count how many high each column is and add them: {' + '.join(str(h) for h in heights)} = {ans}.",
                "detail": "The number of blocks equals the sum of the heights on each cell of the top-view. Even when some are hidden "
                          "behind or below, knowing each column’s height lets you count exactly. Thinking 'from the top' always works.",
            },
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
            en={
                "statement": "How many grid cells is the shaded shape? (each cell is 1 cm²)",
                "answer": f"{area} cm²",
                "distractors": [f"{area - 1} cm²", f"{area + 1} cm²", f"{area + 2} cm²"],
                "explanation": f"Count the shaded cells one by one → {area} cm².",
                "detail": "Area can be found two ways — 'subtract the empty part from a bigger shape' and 'split into pieces and add'. "
                          "Getting the same answer both ways catches mistakes. More than memorizing formulas, the key is imagining how to cut and rearrange.",
            },
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
            en={
                "statement": "What is the area of the shaded shape? (each grid cell is 1 cm²)",
                "answer": f"{area} cm²",
                "distractors": [f"{area - 1} cm²", f"{area + 1} cm²", f"{area + 2} cm²"],
                "explanation": f"Count the cells, or split into rectangles → {area} cm².",
                "detail": "Area can be found two ways — 'subtract the empty part from a bigger shape' and 'split into pieces and add'. "
                          "Getting the same answer both ways catches mistakes. The key is imagining how to cut and rearrange, not memorizing formulas.",
            },
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
            en={
                "statement": "How many stacking blocks are there in all, stacked as in the picture? (count the hidden blocks behind and underneath too)",
                "answer": _en_plural(ans, "block"),
                "distractors": [_en_plural(ans - 1, "block"), _en_plural(ans + 1, "block"), _en_plural(max(1, ans - 2), "block")],
                "explanation": f"Count the height of each column and add: {' + '.join(str(h) for h in heights)} = {ans}. Even where the front or top hides them, the ones below are filled in.",
                "mistakes": [(_en_plural(max(1, ans - 2), "block"), "Count the hidden blocks you can't see too — don't skip any.")],
                "detail": f"The number of stacking blocks equals the sum of the column heights written on each cell of the 'top view'. Even when hidden behind or above, knowing each column's height lets you count exactly. Adding the heights one by one gives {ans}. Thinking 'from the top view' lets you count without missing any, no matter how complex.",
            },
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
            en={
                "statement": f"One of {n} identical-looking coins is a slightly lighter counterfeit. Using only a two-pan balance scale, what is the fewest number of weighings needed to be sure of finding the fake?",
                "answer": _en_plural(k, "weighing"),
                "distractors": [_en_plural(k - 1, "weighing"), _en_plural(k + 1, "weighing"), _en_plural(n - 1, "weighing")],
                "explanation": f"One weighing has three possible results: 'left side heavier, right side heavier, or balanced'. So with {k} weighings you can tell apart up to 3×3×…={3 ** k} cases. By splitting the coins into three piles and putting two of them on the scale, you cut the candidates to 1/3 each time, so {n} coins need only {k} weighings (one weighing fewer leaves only {3 ** (k - 1)} cases — not enough).",
                "mistakes": [(_en_plural(n - 1, "weighing"), "You don't need to weigh them one at a time. Splitting into three piles is much faster.")],
                "detail": f"The key is 'how much information one weighing gives'. A balance has 3 results, so it becomes a base-3 (ternary) search, and {k} weighings can distinguish 3^k cases. So the number needed is the smallest k with 3^k ≥ {n}. If the fake could be either lighter or heavier (unknown), you'd need more information and more weighings. That's why a balance (3 results) is faster than a binary search (2 results).",
            },
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
            en={
                "statement": f"In how many ways can {n} people sit around a round table? (arrangements that become the same after rotating count as one)",
                "answer": _en_plural(ans, "way"),
                "distractors": [_en_plural(factorial(n), "way"), _en_plural(ans * 2, "way"), _en_plural(ans - 1, "way")],
                "explanation": f"A round table has seats that are 'the same when rotated', so pin one person down as a reference. Then it becomes exactly like lining up the remaining {n - 1} people in a row: ({n}−1)! = {n - 1}×…×1 = {ans} ways. Counting them in a row ({factorial(n)} ways) would count the {n} rotations as duplicates.",
                "mistakes": [(_en_plural(factorial(n), "way"), "That's the count for a straight row. At a round table the rotations are the same, so divide by the number of seats.")],
                "detail": f"In a straight line it's {n}! = {factorial(n)} ways, but at a round table all {n} rotations are the 'same arrangement', so divide by {n}: {factorial(n)}÷{n} = {ans} ways. This 'divide by however much you overcounted' is a core tool of counting (if flips also count as the same, like a necklace, divide by 2 once more).",
            },
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
            en={
                "statement": f"On a grid road {w} squares wide and {h} squares tall, you go from the bottom-left (●) to the top-right (◯), moving only right and up. But the intersections marked ✕ are under construction and cannot be passed. How many different shortest paths are there?",
                "answer": _en_plural(ans, "way"),
                "distractors": [_en_plural(total, "way"), _en_plural(ans - 1, "way"), _en_plural(ans + 2, "way")],
                "explanation": f"With nothing blocked, there are {total} shortest paths. Adding (paths from the left)+(paths from below) at each intersection in turn, but keeping the ✕ intersections at 0 so they are never passed, the destination comes out to {ans}.",
                "mistakes": [(_en_plural(total, "way"), "That's the count with nothing blocked. You have to subtract the paths that go through ✕.")],
                "detail": f"You can solve it two ways. ① total ({total}) − paths through ✕. Paths through ✕ = (start→✕)×(✕→end), multiplying the front and back parts. ② add up the number of paths reaching each intersection, keeping only ✕ at 0. Checking that both ways give the same answer catches mistakes. 'Paths through a point = front part × back part' is a key tool for route problems.",
            },
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
            en={
                "statement": f"1 red block is worth {k1} blue blocks, and 1 blue block is worth {k2} green blocks. So 1 red block is worth how many green blocks?",
                "answer": _en_plural(ans, "green block"),
                "distractors": [_en_plural(k1 + k2, "green block"), _en_plural(ans - 1, "green block"), _en_plural(ans + 2, "green block")],
                "explanation": f"1 red block = {k1} blue blocks, and each of those blue blocks is again {k2} green blocks. So 1 red block = {k1}×{k2}={ans} green blocks. Multiply at each step as you change the unit.",
                "mistakes": [(_en_plural(k1 + k2, "green block"), "Don't add — multiply at each step of the change.")],
                "detail": f"Changing units (substitution) chains by multiplication: red→blue is ×{k1}, blue→green is ×{k2}, so red→green is ×({k1}×{k2}). Exchange rates and unit conversions (1 hour = 60 min, 1 min = 60 sec → 1 hour = 3600 sec) work the same way.",
            },
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
            en={
                "statement": f"You want to make {amount} using coins worth {coins[0]} and {coins[1]}. (You may use any number of each coin, or none.) How many ways are there in all?",
                "answer": _en_plural(ans, "way"),
                "distractors": [_en_plural(ans - 1, "way"), _en_plural(ans + 1, "way"), _en_plural(ans + 2, "way")],
                "explanation": f"Try using 0, 1, 2… of the bigger coin ({coins[0]}) and check whether the rest can be filled exactly with the smaller coin ({coins[1]}). Counting with no gaps and no overlaps gives {ans} ways.",
                "detail": f"Once you fix how many {coins[0]} coins to use, the rest is decided automatically. So just raise the number of {coins[0]} coins 0, 1, 2… and count only the cases that fill up exactly with {coins[1]} coins — no gaps, no overlaps. 'Fix one thing and work out the rest' is a basic skill of counting problems.",
            },
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
            en={
                "statement": f"You want to tile a rectangular floor {a} cells wide and {b} cells tall with identical square tiles, with no gaps or overlaps. How many cells is the side of the 'largest' square tile you can use?",
                "answer": _en_plural(g, "cell"),
                "distractors": [_en_plural(min(a, b), "cell"), _en_plural(g - 1, "cell"), _en_plural(g + 1, "cell")],
                "explanation": f"The tile's side has to divide both the width and the height exactly, or there will be gaps. The largest such number is the greatest common divisor. The GCD of {a} and {b} is {g}, so the largest tile has a side of {g} cells.",
                "mistakes": [(_en_plural(min(a, b), "cell"), "The shorter side may not divide the longer side exactly. It has to divide both sides.")],
                "detail": f"The 'largest number that divides both numbers' is the greatest common divisor (GCD). With this tile you need {a}÷{g}={a // g} across, {b}÷{g}={b // g} down, {a // g * (b // g)} in all. Conversely, 'the smallest square you make by overlapping two lengths' is the least common multiple.",
            },
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
            en={
                "statement": f"You split {total} beads onto two plates. Each plate gets at least 1, and the two plates are not "
                             f"distinguished (1 & {total - 1} is the same as {total - 1} & 1). How many ways are there?",
                "answer": _en_plural(ans, "way"),
                "distractors": [_en_plural(ans + 1, "way"), _en_plural(ans - 1, "way"), _en_plural(total - 1, "way")],
                "explanation": f"Raise the smaller side from 1: (1,{total - 1}), (2,{total - 2})… Since the plates aren’t distinguished, "
                               f"count only up to half. So 1 through {ans} — {ans} ways.",
                "mistakes": [(_en_plural(total - 1, "way"), "Distinguishing the plates would double it, but since they aren’t, count only half.")],
                "detail": "Raising the smaller side 1, 2, 3… and counting without omission is the basis of counting problems. Distinguishing "
                          "the two plates doubles it; not distinguishing halves it. Always check first: distinguished or not?",
            },
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
            en={
                "statement": "Four people’s heights were compared. B is taller than C, A is taller than B, and C is taller than D. "
                             "Who is the tallest of the four?",
                "answer": "A",
                "distractors": ["B", "C", "D"],
                "explanation": "Chain the 'taller than' hints into arrows: A→B→C→D. A, with no one above them, is the tallest.",
                "mistakes": [("B", "Don’t use just one hint — chain them all into the full order.")],
                "detail": "Order problems come down to 'lining everyone up'. Chaining scattered comparisons pins down one full order "
                          "(A>B and B>C means A>C — transitivity). Arrows or a table keep it straight. Rankings and tournaments work the same way.",
            },
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
            en={
                "statement": f"Two buses leave the same stop at the same time. The blue bus leaves every {a} minutes and the red bus every {b} minutes. After how many minutes will the two buses next leave 'together again'?",
                "answer": f"{lcm} minutes",
                "distractors": [f"{a + b} minutes", f"{lcm // 2} minutes", f"{lcm + a} minutes"],
                "explanation": f"The blue bus leaves at {a}, {a * 2}, {a * 3}… minutes — multiples of {a}. The red bus leaves at {b}, {b * 2}… minutes — multiples of {b}. For both to leave together, their multiples must overlap, so find a 'common multiple', and the earliest one is the 'least common multiple'. The least common multiple of {a} and {b} is {lcm}, so they first meet again after {lcm} minutes.",
                "mistakes": [(f"{a + b} minutes", "Don't add the two times — find the common multiple (least common multiple) where they overlap.")],
                "detail": f"Find the least common multiple quickly by dividing the product by the greatest common divisor: {a}×{b}÷{gcd(a, b)}={lcm}. Prime factorization (multiply each prime to whichever side has more of it) gives the same. Traffic lights, gears, and planetary periods all line up at this least common multiple.",
            },
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
            en={
                "statement": f"You add {count} consecutive whole numbers and get {total}. What is the 'middle' number of the {count}?",
                "answer": str(mid),
                "distractors": [str(total // 2), str(mid - 1), str(mid + count)],
                "explanation": f"Consecutive numbers are symmetric about the middle. Call the middle □; then they are {pattern}. The − and + "
                               f"cancel, so the sum equals 'middle × count'. So the middle = {total} ÷ {count} = {mid}.",
                "mistakes": [(str(total // 2), f"Divide by the count ({count}), not by 2, to get the middle.")],
                "detail": "'Symmetric cancellation about the middle' is cleanest with an odd count (one exact middle). With an even count the "
                          "middle sits between two numbers, so the sum is 'average of the middle two × count'. This eye also gives Gauss’s trick for 1+…+100.",
            },
        )


# ── 65. 비둘기집 원리 (난5, 자료와가능성) ────────────────────────────────────
def gen_pigeonhole():
    for names in [["빨강", "파랑", "노랑"], ["검정", "흰색"], ["빨강", "파랑", "노랑", "초록"], ["빨강", "노랑", "초록"]]:
        colors = len(names)
        ans = colors + 1
        colortxt = "·".join(names)
        colortxt_en = ", ".join({"빨강": "red", "파랑": "blue", "노랑": "yellow", "초록": "green", "검정": "black", "흰색": "white"}[x] for x in names)
        add(
            "pigeon", "DATA_POSSIBILITY", 5, ["비둘기집 원리", "최악의 경우"],
            f"서랍 안에 {colortxt} 양말이 마구 섞여 있어요(각 색이 넉넉히 있어요). 불을 끄고 색을 안 보고 꺼낼 때, '같은 색 2짝'을 반드시 갖게 되려면 최소 몇 짝을 꺼내야 할까요?",
            f"{ans}짝", [f"{colors}짝", f"{ans + 1}짝", f"{ans + 2}짝"],
            f"'반드시'를 물으니 가장 운이 나쁜 경우를 생각해요. 최악이면 색깔마다 딱 한 짝씩 뽑혀 {colors}짝까진 전부 다른 색일 수 있어요. 하지만 한 짝을 '더' 꺼내면 이미 나온 {colors}가지 색 중 하나와 반드시 겹쳐요. 그래서 {colors}+1={ans}짝이면 같은 색 2짝이 확실해요.",
            [(f"{colors}짝", "그 수까진 모두 다른 색일 수 있어요. '반드시'가 되려면 한 짝 더 필요해요.")],
            detail=f"이게 '비둘기집 원리'예요: 비둘기(꺼낸 양말)가 집({colors}가지 색)보다 많으면 어느 한 집엔 둘 이상이 들어가요. '최악의 경우를 먼저 그리고 거기서 하나 더'가 핵심 기술이에요. 반에서 생일이 같은 달인 친구 찾기도 같은 원리예요.",
            en={
                "statement": f"A drawer has {colortxt_en} socks all mixed together (plenty of each color). With the lights off, drawing without seeing the colors, at least how many socks must you pull out to be sure of getting 2 socks of the same color?",
                "answer": _en_plural(ans, "sock"),
                "distractors": [_en_plural(colors, "sock"), _en_plural(ans + 1, "sock"), _en_plural(ans + 2, "sock")],
                "explanation": f"Since it asks for 'certain', think of the unluckiest case. At worst you pull exactly one of each color, so up to {colors} socks could all be different colors. But pull one 'more' and it must match one of the {colors} colors already out. So {colors}+1={ans} socks guarantees 2 socks of the same color.",
                "mistakes": [(_en_plural(colors, "sock"), "Up to that number they could all be different colors. To make it 'certain' you need one more sock.")],
                "detail": f"This is the 'pigeonhole principle': if there are more pigeons (socks pulled) than holes ({colors} colors), some one hole must hold two or more. 'Picture the worst case first, then one more' is the key trick. Finding classmates born in the same month works by the same principle.",
            },
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
            en={
                "statement": f"A test of {subjects} subjects has an average of {avg} points. The {len(known)} known scores are {', '.join(map(str, known))}. How many points is the remaining subject?",
                "answer": f"{missing} points",
                "distractors": [f"{avg} points", f"{missing - 5} points", f"{missing + 5} points"],
                "explanation": f"Turn the average into a 'total'. If {subjects} subjects average {avg} points, the total must be {subjects}×{avg}={total} points. The {len(known)} known subjects sum to {sum(known)}, so the remaining subject = {total}−{sum(known)}={missing} points.",
                "mistakes": [(f"{avg} points", "Don't just give the average. Subtract the known scores from the total.")],
                "detail": "The key to average problems is using 'average = total ÷ count' in reverse: total = average × count. Once you hold the total, the missing value is a single subtraction. 'How many more points to make the average X?' is solved the same way through the total.",
            },
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
            en={
                "statement": f"What digit is in the 'ones place' of {base} raised to the power of {exp}?",
                "answer": str(ans),
                "distractors": distractors,
                "explanation": f"You don't need to compute the whole big number — just track the 'ones digit'. The powers of {base} have ones digits {', '.join(map(str, cycle))}, repeating every {period} (a cycle of length {period}). Which spot in the cycle the {exp}th power lands on is set by the remainder of {exp}÷{period} (if the remainder is 0, it is the last spot), and that digit is {ans}.",
                "mistakes": [(distractors[0], "That digit changes depending on 'which power it is'. Check that you counted the position within the cycle correctly.")],
                "detail": "The ones digit of a power always forms a 'cycle' (there are only the digits 0–9, so it must eventually repeat). So you only need the 'remainder' of the exponent divided by the cycle length. This 'cycle + remainder' (modular) thinking is exactly the same tool as day-of-week, clock, and calendar calculations.",
            },
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
            en={
                "statement": f"A class of {total} students was surveyed. {a} like soccer, {b} like basketball, and {neither} like neither. How many students like 'both' soccer and basketball?",
                "answer": _en_plural(both, "student"),
                "distractors": [_en_plural(both - neither, "student"), _en_plural(both + neither, "student"), _en_plural(total - neither, "student")],
                "explanation": f"Taking away the {neither} who like neither, the number who like at least one is {total}−{neither}={total - neither}. But counting soccer ({a}) + basketball ({b}) = {a + b} counts the 'both' people twice. So the overlap equals that double-count minus the rest: {a + b}−{total - neither}={both}.",
                "mistakes": [(_en_plural(both - neither, "student"), "You forgot to account back for the 'like neither' group."), (_en_plural(total - neither, "student"), "That's the number who like 'at least one'.")],
                "detail": "This is the basic picture of inclusion-exclusion: (A or B) = A + B − (A and B). Here 'A or B' is the whole minus 'none'. Draw two overlapping Venn circles and just remember 'the overlap got counted twice, so subtract it once' — and any two-set problem works out.",
            },
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
            en={
                "statement": f"Going from home to school you travel at {va} km/h, and coming back at {vb} km/h. What is the round-trip 'average speed', in km/h?",
                "answer": f"{avg} km/h",
                "distractors": [f"{(va + vb) // 2} km/h", f"{va + vb} km/h", f"{avg - 5} km/h"],
                "explanation": f"Average speed is '(total distance) ÷ (total time)', not the arithmetic mean of the two speeds. Taking the one-way distance as {dist} km, going takes {dist}÷{va}={dist // va} hours and coming back {dist}÷{vb}={dist // vb} hours. Round-trip distance {2 * dist} km ÷ total time {dist // va + dist // vb} hours = {avg} km/h. You spend more time on the slower leg, so it comes out lower than the plain average.",
                "mistakes": [(f"{(va + vb) // 2} km/h", "You can't just add the two speeds and halve them — the slower stretch takes more time.")],
                "detail": "The average when covering the same 'distance' at different speeds is not the arithmetic mean but the harmonic mean (2ab/(a+b)). Contrary to intuition it's always pulled toward the slower side. Conversely, covering the same 'time' at different speeds does give the arithmetic mean — the key is to first see 'what is the same (distance or time)'.",
            },
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
            en={
                "statement": f"{n} people gather and each pair shakes hands exactly once. How many handshakes happen in all?",
                "answer": _en_plural(ans, "handshake"),
                "distractors": [_en_plural(n * (n - 1), "handshake"), _en_plural(n * n, "handshake"), _en_plural(ans - n + 1, "handshake")],
                "explanation": f"Each person shakes hands with the {n - 1} others besides themselves. With {n} people each shaking {n - 1} times, that's {n}×{n - 1}={n * (n - 1)}, but this counts 'the handshake between A and B' twice — once from A's side, once from B's. So divide by 2: {n * (n - 1)}÷2={ans}.",
                "mistakes": [(_en_plural(n * (n - 1), "handshake"), "The same handshake got counted by both people, so it's counted twice. You have to divide by 2.")],
                "detail": f"This is exactly the number of ways to choose 2 people from {n}, C({n},2). Every problem that pairs two things (handshakes, round-robin games, line segments joining points, counting triangles) fits here. 'Count twice, then divide by 2' is a go-to counting trick.",
            },
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
            en={
                "statement": f"What do you get when you add up all the whole numbers from 1 to {n}?",
                "answer": str(ans),
                "distractors": [str(n * n), str(ans + n), str(ans - n)],
                "explanation": f"Pair the numbers from both ends and add: 1+{n}={n + 1}, 2+{n - 1}={n + 1}, … every pair sums to the same {n + 1}. There are {n}÷2={n // 2} pairs, so {n + 1}×{n // 2}={ans}.",
                "mistakes": [(str(n * n), "It's not a square — it's the value from pairing the two ends and adding.")],
                "detail": f"This is the method young Gauss is said to have found: 1+2+…+n = n×(n+1)÷2. Write the numbers backwards too and add them top to bottom, and you see why at a glance (every column sums to n+1). Every arithmetic-sequence sum works out to '(first+last)×count÷2'.",
            },
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
            en={
                "statement": f"{total} marbles are shared between child A and child B in the ratio {r1}:{r2}. How many marbles does A get?",
                "answer": f"{part} marbles",
                "distractors": [f"{r1} marbles", f"{total // 2} marbles", f"{total - part} marbles"],
                "explanation": f"The ratio {r1}:{r2} splits the whole into {r1}+{r2}={r1 + r2} equal groups. One group is {total}÷{r1 + r2}={unit} marbles. A takes {r1} of those groups, so {unit}×{r1}={part} marbles.",
                "mistakes": [(f"{total - part} marbles", "That's B's share."), (f"{total // 2} marbles", "It's not half unless the ratio is equal. Divide by the number of groups.")],
                "detail": "The key to ratio problems is finding 'one group (the unit amount)' first. Divide the whole by (the sum of the ratio) to get one group, then multiply by each share — done. This 'unit amount first' thinking works the same for scale, concentration, and exchange rates.",
            },
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
            en={
                "statement": f"{num}/{den} of the marbles in a jar is {part} marbles. How many marbles are in the jar in all?",
                "answer": _en_plural(whole, "marble"),
                "distractors": [_en_plural(part * den, "marble"), _en_plural(part + den, "marble"), _en_plural(whole - part, "marble")],
                "explanation": f"It means {num} of the {den} equal parts of the whole is {part} marbles. So one part is {part}÷{num}={part // num} marbles. The whole is {den} parts, so {part // num}×{den}={whole} marbles.",
                "mistakes": [(_en_plural(part * den, "marble"), "Don't just multiply by the denominator. First find one part (÷ the numerator).")],
                "detail": f"Part-and-whole problems hinge on finding 'one part (the unit fraction)' first. If {num}/{den} is {part}, then 1/{den} is {part}÷{num}, and the whole (={den}/{den}) is that times {den}. In reverse, 'what is {num}/{den} of the whole?' is: divide the whole by {den} and multiply by {num}.",
            },
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
            en={
                "statement": f"{n} players compete in a tournament (a loser is eliminated immediately) to decide a single champion. How many games are played in all before the champion is decided?",
                "answer": _en_plural(ans, "game"),
                "distractors": [_en_plural(n, "game"), _en_plural(n // 2, "game"), _en_plural(ans - 1, "game")],
                "explanation": f"Instead of counting games one by one, focus on the 'eliminated players'. Each game eliminates exactly one player. To leave just 1 champion, the other {n}−1={ans} players must all be eliminated, so there are exactly {ans} games.",
                "mistakes": [(_en_plural(n // 2, "game"), "That only counts the first-round games. You have to add up all the rounds.")],
                "detail": f"Looking at 'what disappears one at a time' means you don't need to draw the whole bracket — 1 game = 1 elimination, so everyone except the champion is eliminated = {n}−1 games. This 'count the changing quantity' viewpoint still works even if the tournament format changes.",
            },
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
            en={
                "statement": f"To give {amount} in change using coins worth 500, 100, 50, and 10, how many coins are needed to use the 'fewest' possible?",
                "answer": f"{cnt} coins",
                "distractors": [f"{cnt + 1} coins", f"{cnt - 1} coins", f"{cnt + 2} coins"],
                "explanation": f"To use as few coins as possible, use the biggest coins first, as many as you can — 500s, then 100s, then 50s, then 10s. Altogether that comes to {cnt} coins.",
                "mistakes": [(f"{cnt + 1} coins", "Using the biggest coins first as much as possible cuts the count down further.")],
                "detail": "'Biggest units first, as many as possible' is the greedy method. With our coin set (500, 100, 50, 10) it always guarantees the minimum. But not every system works that way — with 1, 3, and 4 coins, making 6 is fewer as 3+3 (2 coins) than as 4+1+1 (3 coins), so biggest-first isn't always best.",
            },
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
        en_item = {"쿠키": "cookies", "팬케이크": "pancakes", "주스": "cups of juice", "빵": "loaves of bread"}[item]
        en_item1 = {"쿠키": "cookie", "팬케이크": "pancake", "주스": "cup of juice", "빵": "loaf of bread"}[item]
        en_word = {"설탕": "spoon", "우유": "cup", "오렌지": "orange", "버터": "spoon"}[ing]
        en_amt = {
            "설탕": lambda q: f"{q} spoons of sugar",
            "우유": lambda q: f"{q} cups of milk",
            "오렌지": lambda q: _en_plural(q, "orange"),
            "버터": lambda q: f"{q} spoons of butter",
        }[ing]
        add(
            "recipe", "CHANGE_RELATION", 4, ["비례", "단위량"],
            f"{item} {base_qty}개를 만들려면 {ing} {base_ing}{unit}{_iga(unit)} 필요해요. 같은 맛으로 {item} {new_qty}개를 만들려면 {ing}{_eun(ing)} 몇 {unit} 필요할까요?",
            f"{ans}{unit}", [f"{base_ing + (new_qty - base_qty)}{unit}", f"{new_qty}{unit}", f"{ans + base_ing}{unit}"],
            f"먼저 {item} 1개당 {ing}이 얼마인지 봐요: {base_ing}÷{base_qty}. {item} {new_qty}개면 그 {new_qty}배니 {base_ing}×{new_qty}÷{base_qty}={ans}{unit}이에요. (비례식 {base_qty}:{base_ing}={new_qty}:□로 풀어도 □={ans}.)",
            [(f"{base_ing + (new_qty - base_qty)}{unit}", "개수 차이만큼 '더하는' 게 아니라, 몇 배인지(비율)로 늘려야 해요.")],
            detail="비례는 '한 개당 얼마(단위량)'를 구하면 다 풀려요. 또는 비례식 a:b=c:□에서 '바깥끼리 곱 = 안끼리 곱'(교차곱)으로 □를 구해도 돼요. 요리·지도 축척·환율·농도가 전부 이 비례 위에 있어요.",
            en={
                "statement": f"To make {base_qty} {en_item} you need {en_amt(base_ing)}. To make {new_qty} {en_item} with the same taste, how many {en_word}s do you need?",
                "answer": _en_plural(ans, en_word),
                "distractors": [_en_plural(base_ing + (new_qty - base_qty), en_word), _en_plural(new_qty, en_word), _en_plural(ans + base_ing, en_word)],
                "explanation": f"First find the amount for one {en_item1}: {base_ing}÷{base_qty}. For {new_qty} {en_item}, that is {new_qty} times as much, so {base_ing}×{new_qty}÷{base_qty}={ans} {en_word}s. (Solving the proportion {base_qty}:{base_ing}={new_qty}:□ also gives □={ans}.)",
                "mistakes": [(_en_plural(base_ing + (new_qty - base_qty), en_word), "Don't 'add' the difference in count — scale up by the ratio (how many times as much).")],
                "detail": "Proportion problems are all solved once you find 'how much per one (the unit amount)'. Or in a proportion a:b=c:□, find □ by 'product of the outers = product of the inners' (cross-multiplying). Cooking, map scales, exchange rates, and concentration all rest on this same proportion.",
            },
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
            en={
                "statement": f"A square has a perimeter of {perim} cm. What is the area of this square?",
                "answer": f"{area} cm²",
                "distractors": [f"{perim} cm²", f"{side * 2} cm²", f"{area + side} cm²"],
                "explanation": f"A square has four equal sides. With a perimeter of {perim} cm, one side is {perim}÷4={side} cm. The area is one side times itself, {side}×{side}={area} cm².",
                "mistakes": [(f"{perim} cm²", "Perimeter and area differ. First find one side (÷4), then square it.")],
                "detail": f"Perimeter is 'edge length (1-D)' and area is 'filled squares (2-D)', so even the units differ — cm versus cm². The order perimeter → one side (÷4) → area (square it) is the key. In reverse, from area {area} the side is the number that multiplied by itself gives {area} ({side}).",
            },
        )


# ── 78. N일 뒤 요일 — 나머지 (난4, 변화와관계) ───────────────────────────────
def gen_day_of_week():
    days = ["일", "월", "화", "수", "목", "금", "토"]
    days_en = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    for start, ahead in [(1, 100), (3, 50), (5, 30), (2, 365)]:
        end = (start + ahead) % 7
        add(
            "dow", "CHANGE_RELATION", 4, ["요일", "나머지"],
            f"오늘은 {days[start]}요일이에요. 오늘부터 {ahead}일 뒤는 무슨 요일일까요?",
            f"{days[end]}요일", [f"{days[(end + 1) % 7]}요일", f"{days[(end + 2) % 7]}요일", f"{days[(end + 4) % 7]}요일"],
            f"요일은 7일마다 똑같이 반복돼요. 그러니 {ahead}일 중 '7의 배수'만큼은 제자리로 돌아오고, {ahead}÷7의 나머지인 {ahead % 7}일만 더 가면 돼요. {days[start]}요일에서 {ahead % 7}일 뒤는 {days[end]}요일이에요.",
            [(f"{days[(end + 1) % 7]}요일", f"하루 차이로 어긋났어요. {ahead}÷7의 나머지({ahead % 7}일)를 정확히 세었는지 봐요.")],
            detail=f"'주기 7 + 나머지'는 요일 계산의 전부예요. {ahead}일 = 7×{ahead // 7} + {ahead % 7}이니, 7의 배수 부분은 무시하고 나머지 {ahead % 7}만 세면 끝. 1000일 뒤 같은 큰 수도 나머지만 보면 되고, 이 modular 사고는 시계·달력·거듭제곱 끝자리와 똑같아요.",
            en={
                "statement": f"Today is {days_en[start]}. What day of the week will it be {ahead} days from today?",
                "answer": days_en[end],
                "distractors": [days_en[(end + 1) % 7], days_en[(end + 2) % 7], days_en[(end + 4) % 7]],
                "explanation": f"The days of the week repeat every 7 days. So out of {ahead} days, whole multiples of 7 land back on the same day, and you only move forward the remainder of {ahead}÷7, which is {ahead % 7} days. {ahead % 7} days after {days_en[start]} is {days_en[end]}.",
                "mistakes": [(days_en[(end + 1) % 7], f"You're off by a day. Check that you counted the remainder of {ahead}÷7 ({ahead % 7} days) exactly.")],
                "detail": f"'A cycle of 7 plus a remainder' is all there is to day-of-week problems. {ahead} days = 7×{ahead // 7} + {ahead % 7}, so ignore the multiple-of-7 part and count only the remainder {ahead % 7}. Even a big number like 1000 days later needs only the remainder, and this modular thinking is the same as clocks, calendars, and the last digit of powers.",
            },
        )


# ── 79. 우물 안 개구리 — 마지막 날 함정 (난5, 변화와관계) ─────────────────────
def gen_frog_well():
    for depth, up, down in [(12, 4, 2), (15, 5, 2), (20, 6, 4), (9, 4, 1)]:
        net = up - down
        days = 0
        pos = 0
        while True:
            days += 1
            pos += up
            if pos >= depth:
                break
            pos -= down
        ans = days
        add(
            "frog", "CHANGE_RELATION", 5, ["따라잡기", "마지막 날 함정"],
            f"깊이 {depth}m 우물 바닥에 개구리가 있어요. 낮에는 {up}m 올라가고 밤에는 {down}m 미끄러져요. 개구리가 우물 밖으로 처음 나오는 건 며칠째 낮일까요?",
            f"{ans}일째", [f"{ans + 1}일째", f"{ans - 1}일째", f"{ans + 2}일째"],
            f"하루가 지나면 실제로는 {up}−{down}={net}m씩 오르지만, '밖으로 나오는 낮'에는 미끄러지지 않아요. 그래서 마지막 도약({up}m) 전까지, 즉 {depth - up}m까지만 {net}m씩 오르면 되죠. 하루하루 따라가 보면 {ans}일째 낮에 {up}m를 올라 {depth}m를 넘어서 탈출해요.",
            [(f"{ans + 1}일째", f"마지막 날 낮엔 미끄러지지 않아요 — 순증가({net}m)로만 계산하면 하루 더 걸리는 것처럼 보여요.")],
            detail="'며칠에 목표 도달'류는 마지막 한 걸음이 늘 예외예요. 순증가로 쭉 세다가 '처음 닿는 순간'은 미끄러지기 전이라는 걸 놓치면 하루가 어긋나요. 안전한 방법: 마지막 도약분을 먼저 빼고 남은 거리를 순증가로 나눈 뒤 1일을 더해요.",
            en={
                "statement": f"A frog is at the bottom of a well {depth}m deep. During the day it climbs {up}m, and at night it slips down {down}m. On the daytime of which day does the frog first get out of the well?",
                "answer": f"day {ans}",
                "distractors": [f"day {ans + 1}", f"day {ans - 1}", f"day {ans + 2}"],
                "explanation": f"Over a full day it really rises {up}−{down}={net}m, but on the 'day it climbs out' it doesn't slip back. So until that last leap ({up}m), it only needs to reach {depth - up}m, climbing {net}m at a time. Following day by day, on the daytime of day {ans} it climbs {up}m past {depth}m and escapes.",
                "mistakes": [(f"day {ans + 1}", f"On the final day it doesn't slip — counting only by the net gain ({net}m) makes it look like one extra day.")],
                "detail": "In 'how many days to reach the goal' problems, the last step is always the exception. If you keep counting by the net gain and forget that the 'first moment it reaches' is before the slip, you'll be off by a day. Safe method: subtract the last leap first, divide the remaining distance by the net gain, then add 1 day.",
            },
        )


# ── 80. 홀수의 합 = 제곱수 (난5, 수와연산) ───────────────────────────────────
def gen_odd_sum_square():
    for n in [5, 7, 10, 8]:
        last = 2 * n - 1
        ans = n * n
        add(
            "oddsum", "NUMBER_OPERATION", 5, ["홀수의 합", "제곱수"],
            f"1부터 시작하는 홀수 {n}개(1, 3, 5, …, {last})를 모두 더하면 얼마일까요?",
            str(ans), [str((n - 1) * (n - 1)), str(last * n), str(ans + n)],
            f"신기하게도 1부터 홀수를 차례로 더하면 항상 '제곱수'가 돼요: 1=1×1, 1+3=4=2×2, 1+3+5=9=3×3… 홀수 {n}개를 더하면 {n}×{n}={ans}이에요.",
            [(str(last * n), "가장 큰 홀수에 개수를 곱하는 게 아니라, 개수를 제곱해요.")],
            detail="왜 제곱이 될까요? 점을 ㄱ자로 하나씩 덧대 정사각형을 키워 보면 보여요 — 한 변이 늘 때마다 홀수 개(3,5,7…)씩 점이 늘어 언제나 정사각형(제곱수)을 이뤄요. '그림으로 왜 그런지'를 보면 공식이 살아 있는 지식이 돼요.",
            en={
                "statement": f"If you add up the first {n} odd numbers (1, 3, 5, …, {last}), what do you get?",
                "answer": str(ans),
                "distractors": [str((n - 1) * (n - 1)), str(last * n), str(ans + n)],
                "explanation": f"Amazingly, adding the odd numbers in order starting from 1 always gives a 'square number': 1=1×1, 1+3=4=2×2, 1+3+5=9=3×3… Adding {n} odd numbers gives {n}×{n}={ans}.",
                "mistakes": [(str(last * n), "Don't multiply the largest odd number by the count — square the count instead.")],
                "detail": "Why a square? Grow a square by adding dots in an L-shape one layer at a time and you'll see it — each time a side grows, an odd number of dots (3, 5, 7…) is added, always forming a square (a square number). Seeing 'why' as a picture turns the formula into living knowledge.",
            },
        )


# ── 81. 순열 — 한 줄로 세우기 = n! (난5, 자료와가능성) ───────────────────────
def gen_permutation():
    for n, ctx in [(4, "책"), (5, "인형"), (6, "색연필"), (4, "컵")]:
        ans = factorial(n)
        ctx_en = {"책": "book", "인형": "doll", "색연필": "colored pencil", "컵": "cup"}[ctx]
        add(
            "perm", "DATA_POSSIBILITY", 5, ["경우의 수", "순서 정하기"],
            f"서로 다른 {ctx} {n}개를 한 줄로 나란히 놓는 방법은 모두 몇 가지일까요?",
            f"{ans}가지", [f"{n * n}가지", f"{2 * n}가지", f"{ans + n}가지"],
            f"첫 자리에 올 수 있는 건 {n}가지. 그걸 정하면 둘째 자리는 남은 {n - 1}가지, 셋째는 {n - 2}가지… 자리마다 줄어드는 가짓수를 모두 곱해요: {'×'.join(str(k) for k in range(n, 0, -1))} = {ans}가지.",
            [(f"{n * n}가지", "n×n이 아니라, 자리마다 하나씩 줄어드는 가짓수를 1까지 곱해요.")],
            detail=f"이걸 '{n}의 계승({n}!)'이라 하고 {n}!={ans}예요. 순서를 정하는(줄 세우기·순위 매기기) 문제의 기본이에요. 몇 개만 골라 세우면 {n}부터 그 개수만큼만 곱하고요. '자리마다 남은 선택지를 곱한다'가 핵심 그림이에요.",
            en={
                "statement": f"In how many ways can you line up {n} different {ctx_en}s in a row?",
                "answer": _en_plural(ans, "way"),
                "distractors": [_en_plural(n * n, "way"), _en_plural(2 * n, "way"), _en_plural(ans + n, "way")],
                "explanation": f"The first spot can be any of {n}. Once that's fixed, the second spot has the remaining {n - 1}, the third {n - 2}… multiply the shrinking counts at each spot: {'×'.join(str(k) for k in range(n, 0, -1))} = {ans} ways.",
                "mistakes": [(_en_plural(n * n, "way"), "It's not n×n — multiply the counts that shrink by one at each spot, all the way down to 1.")],
                "detail": f"This is called '{n} factorial ({n}!)', and {n}!={ans}. It's the basis of problems about setting an order (lining up, ranking). If you only pick and arrange a few, you multiply starting from {n} for just that many terms. 'At each spot, multiply the remaining choices' is the key picture.",
            },
        )


# ── 82. 숫자 뒤집기 차 = 9의 배수 (난5, 수와연산) ────────────────────────────
def gen_reverse_diff():
    for tens, ones in [(7, 2), (8, 3), (5, 1), (9, 4)]:
        num = tens * 10 + ones
        rev = ones * 10 + tens
        ans = num - rev
        add(
            "revdiff", "NUMBER_OPERATION", 5, ["자리값", "불변의 규칙"],
            f"두 자리 수 {num}에서, 십의 자리와 일의 자리 숫자를 바꾼 수({rev})를 빼면 얼마일까요?",
            str(ans), [str(tens - ones), str(ans + 9), str(ans - 9)],
            f"자리값으로 풀어 봐요. {num} = {tens}×10 + {ones}, 바꾼 수 {rev} = {ones}×10 + {tens}. 빼면 (10−1)×({tens}−{ones}) = 9×{tens - ones} = {ans}이에요.",
            [(str(tens - ones), "두 숫자의 차만 답하면 안 돼요 — 그 차의 9배예요.")],
            detail="두 자리 수와 숫자를 바꾼 수의 차는 '항상 9의 배수'예요(정확히는 9×(두 숫자의 차)). 세 자리 수라면 처음·끝을 바꾼 차가 99의 배수고요. 자리값(10, 100…)의 차이가 만드는 이런 규칙은 마술 같은 숫자 퍼즐의 비밀이에요.",
            en={
                "statement": f"Take the two-digit number {num}. If you subtract the number with its tens and ones digits swapped ({rev}), what do you get?",
                "answer": str(ans),
                "distractors": [str(tens - ones), str(ans + 9), str(ans - 9)],
                "explanation": f"Solve with place value. {num} = {tens}×10 + {ones}, and the swapped number {rev} = {ones}×10 + {tens}. Subtracting gives (10−1)×({tens}−{ones}) = 9×{tens - ones} = {ans}.",
                "mistakes": [(str(tens - ones), "Don't just give the difference of the two digits — it's 9 times that difference.")],
                "detail": "The difference between a two-digit number and its digit-swapped version is 'always a multiple of 9' (exactly 9×(difference of the two digits)). For a three-digit number, swapping the first and last digits gives a multiple of 99. Rules like this, made by the differences in place value (10, 100…), are the secret behind magic-like number puzzles.",
            },
        )


# ── 83. 나머지 조건 맞추기 (난6, 수와연산) ───────────────────────────────────
def gen_leftover_crt():
    for d1, r1, d2, r2 in [(3, 2, 5, 3), (4, 3, 5, 2), (3, 1, 4, 3), (5, 4, 6, 5)]:
        n = 1
        while not (n % d1 == r1 and n % d2 == r2):
            n += 1
        ans = n
        period = d1 * d2 // gcd(d1, d2)
        add(
            "leftover", "NUMBER_OPERATION", 6, ["나머지", "조건 맞추기"],
            f"어떤 수를 {d1}씩 묶으면 {r1}개가 남고, {d2}씩 묶으면 {r2}개가 남아요. 이런 수 중에서 가장 작은 자연수는 무엇일까요?",
            str(ans), [str(ans + period), str(r1 + r2), str(ans - 1)],
            f"한 조건씩 좁혀 가요. {d2}씩 묶어 {r2}개 남는 수는 {r2}, {r2 + d2}, {r2 + 2 * d2}, …예요. 이 중 {d1}씩 묶어 {r1}개 남는 것을 찾으면 {ans}이에요.",
            [(str(r1 + r2), "두 나머지를 더하는 게 아니에요. 두 조건을 '동시에' 만족하는 수를 찾아요.")],
            detail=f"'여러 나머지 조건을 동시에'는 한 조건의 후보(등차수열)를 쭉 적고 다른 조건으로 거르는 게 기본이에요. 큰 수 쪽 조건부터 후보를 만들면 더 빨라요. 답들은 {d1}, {d2}의 최소공배수 {period}마다 반복돼서, 다음 답은 {ans}+{period}={ans + period}이에요.",
            en={
                "statement": f"When a certain number is grouped by {d1}s, {r1} are left over, and when grouped by {d2}s, {r2} are left over. What is the smallest whole number like this?",
                "answer": str(ans),
                "distractors": [str(ans + period), str(r1 + r2), str(ans - 1)],
                "explanation": f"Narrow it down one condition at a time. Numbers that leave {r2} when grouped by {d2}s are {r2}, {r2 + d2}, {r2 + 2 * d2}, …. Finding one among these that leaves {r1} when grouped by {d1}s gives {ans}.",
                "mistakes": [(str(r1 + r2), "You don't add the two remainders. Find a number that satisfies both conditions 'at the same time'.")],
                "detail": f"For 'several remainder conditions at once', the basic approach is to write out the candidates for one condition (an arithmetic sequence) and filter with the other. Starting the candidates from the condition with the larger divisor is faster. The answers repeat every {period}, the least common multiple of {d1} and {d2}, so the next answer is {ans}+{period}={ans + period}.",
            },
        )


# ── 84. 사각수 (난4, 변화와관계) ─────────────────────────────────────────────
def gen_square_numbers():
    for k in [5, 6, 7, 8]:
        ans = k * k
        add(
            "squarenum", "CHANGE_RELATION", 4, ["규칙", "사각수"],
            f"바둑돌을 정사각형 모양으로 놓아요. 1번째는 1개(1×1), 2번째는 4개(2×2), 3번째는 9개(3×3)… {k}번째 그림의 바둑돌은 몇 개일까요?",
            f"{ans}개", [f"{k * 2}개", f"{(k - 1) * (k - 1)}개", f"{ans + k}개"],
            f"규칙을 보면 n번째는 한 변이 n개인 정사각형이라 n×n개예요. 그러니 {k}번째는 {k}×{k}={ans}개예요.",
            [(f"{k * 2}개", "2배가 아니라, 한 변을 두 번 곱해요(정사각형이니까).")],
            detail="이런 수(1,4,9,16,25…)를 '사각수(제곱수)'라 해요. 이웃한 사각수의 차는 3,5,7,9…처럼 홀수로 늘어나요(정사각형을 ㄱ자로 키울 때 덧대는 점의 수). 그래서 '홀수를 차례로 더하면 제곱수'와도 이어져요. 점을 그림으로 배열하면 규칙이 눈에 보여요.",
            en={
                "statement": f"You lay out stones in square shapes. The 1st is 1 stone (1×1), the 2nd is 4 stones (2×2), the 3rd is 9 stones (3×3)… how many stones are in the {k}th picture?",
                "answer": _en_plural(ans, "stone"),
                "distractors": [_en_plural(k * 2, "stone"), _en_plural((k - 1) * (k - 1), "stone"), _en_plural(ans + k, "stone")],
                "explanation": f"By the rule, the nth picture is a square with n stones on each side, so n×n stones. So the {k}th is {k}×{k}={ans} stones.",
                "mistakes": [(_en_plural(k * 2, "stone"), "It is not doubling — multiply one side by itself (it is a square).")],
                "detail": "These numbers (1, 4, 9, 16, 25…) are called 'square numbers'. The gaps between neighboring square numbers grow by odd numbers 3, 5, 7, 9… (the dots added when you grow a square by an L-shape). That is why 'adding odd numbers in order gives a square number' connects here too. Arrange dots as a picture and the rule becomes visible.",
            },
        )


# ── 85. 삼각수 (난4, 변화와관계) ─────────────────────────────────────────────
def gen_triangular():
    for k in [5, 6, 8, 10]:
        ans = k * (k + 1) // 2
        add(
            "trinum", "CHANGE_RELATION", 4, ["규칙", "삼각수"],
            f"공을 삼각형으로 쌓아요. 1층은 1개, 2층까지는 1+2=3개, 3층까지는 1+2+3=6개… {k}층까지 쌓으면 공은 모두 몇 개일까요?",
            f"{ans}개", [f"{k * k}개", f"{ans - k}개", f"{k * (k + 1)}개"],
            f"{k}층까지면 1+2+3+…+{k}를 더하는 거예요. 양 끝을 짝지으면 (1+{k}), (2+{k - 1})…처럼 합이 {k + 1}인 짝이 생겨, {k}×({k}+1)÷2={ans}개예요.",
            [(f"{k * (k + 1)}개", "짝지어 더한 다음 ÷2 하는 걸 빠뜨렸어요.")],
            detail="이런 수(1,3,6,10,15…)를 '삼각수'라 해요. n번째 삼각수 = n×(n+1)÷2로 1부터 n까지의 합과 똑같아요(가우스의 방법). 삼각수 두 개를 이어 붙이면 직사각형이 되는 걸 그림으로 보면 왜 ÷2인지 보여요. 볼링핀·당구공 배열이 삼각수예요.",
            en={
                "statement": f"You stack balls into a triangle. Row 1 has 1 ball, up to row 2 has 1+2=3, up to row 3 has 1+2+3=6… stacking up to row {k}, how many balls are there in all?",
                "answer": _en_plural(ans, "ball"),
                "distractors": [_en_plural(k * k, "ball"), _en_plural(ans - k, "ball"), _en_plural(k * (k + 1), "ball")],
                "explanation": f"Up to row {k} means adding 1+2+3+…+{k}. Pairing the two ends gives (1+{k}), (2+{k - 1})… pairs that each add up to {k + 1}, so {k}×({k}+1)÷2={ans} balls.",
                "mistakes": [(_en_plural(k * (k + 1), "ball"), "You forgot to divide by 2 after pairing.")],
                "detail": "These numbers (1, 3, 6, 10, 15…) are called 'triangular numbers'. The nth triangular number = n×(n+1)÷2, exactly the sum from 1 to n (Gauss's trick). Joining two triangular numbers makes a rectangle — draw it and you see why the ÷2. Bowling pins and racked billiard balls form triangular numbers.",
            },
        )


# ── 86. 2배씩 커지기 = 거듭제곱 (난6, 변화와관계) ────────────────────────────
def gen_power_of_two():
    for n in [5, 8, 10, 6]:
        ans = 2 ** n
        add(
            "pow2", "CHANGE_RELATION", 6, ["거듭제곱", "2배씩 커지기"],
            f"종이를 반으로 접으면 두께가 2겹, 또 접으면 4겹, 또 접으면 8겹… 이렇게 {n}번 접으면 몇 겹이 될까요?",
            f"{ans}겹", [f"{2 * n}겹", f"{ans // 2}겹", f"{ans + 2}겹"],
            f"한 번 접을 때마다 겹이 '2배'가 돼요. 1번에 2겹, 2번에 4겹, 3번에 8겹… {n}번이면 2를 {n}번 곱한 값 = {ans}겹이에요.",
            [(f"{2 * n}겹", "2씩 더하는 게 아니라 2씩 곱해요. 접을 때마다 두 배!")],
            detail=f"'매번 2배'는 폭발적으로 커져요(2,4,8,16,32…). 겨우 {n}번 접었는데 {ans}겹! 실제로 종이를 7~8번 이상 접기 어려운 이유죠. 이 '2배씩(지수) 성장'은 세균 번식·소문 퍼지기·복리 이자에도 똑같이 나타나요.",
            en={
                "statement": f"Folding a sheet of paper in half makes it 2 layers thick, folding again makes 4, again makes 8… folding it {n} times like this, how many layers thick is it?",
                "answer": _en_plural(ans, "layer"),
                "distractors": [_en_plural(2 * n, "layer"), _en_plural(ans // 2, "layer"), _en_plural(ans + 2, "layer")],
                "explanation": f"Every fold 'doubles' the layers. 2 layers after 1 fold, 4 after 2, 8 after 3… so {n} folds is 2 multiplied {n} times = {ans} layers.",
                "mistakes": [(_en_plural(2 * n, "layer"), "You don't add 2 each time, you multiply by 2 — double with every fold!")],
                "detail": f"'Doubling every time' grows explosively (2,4,8,16,32…). Just {n} folds and it's {ans} layers! That's why it's hard to fold real paper more than 7 or 8 times. This 'doubling (exponential) growth' shows up the same way in bacteria multiplying, rumors spreading, and compound interest.",
            },
        )


# ── 87. 범위 안 배수 개수 (난4, 수와연산) ────────────────────────────────────
def gen_multiples_in_range():
    for limit, div in [(100, 7), (100, 3), (50, 4), (200, 9)]:
        ans = limit // div
        add(
            "multrange", "NUMBER_OPERATION", 4, ["배수", "개수 세기"],
            f"1부터 {limit}까지의 자연수 중에서 {div}의 배수는 모두 몇 개일까요?",
            f"{ans}개", [f"{ans + 1}개", f"{ans - 1}개", f"{ans + div}개"],
            f"{div}의 배수는 {div}×1, {div}×2, {div}×3, …이에요. {limit}을 넘지 않는 가장 큰 배수는 {div}×{ans}={div * ans}이니 {div}×1부터 {div}×{ans}까지 모두 {ans}개. 즉 {limit}÷{div}의 몫이에요.",
            [(f"{ans + 1}개", f"{div}×{ans + 1}={div * (ans + 1)}은 {limit}을 넘어요. 몫까지만 세요.")],
            detail=f"'범위 안 배수 개수'는 나눗셈의 몫이에요: {limit}÷{div}={ans}. 배수는 일정 간격({div})으로 놓이니 개수는 곧 '몇 칸 들어가나'죠. 시작이 1이 아니면 '큰 쪽 몫 − 작은 쪽 몫'으로 빼서 구하면 돼요.",
            en={
                "statement": f"Among the whole numbers from 1 to {limit}, how many are multiples of {div}?",
                "answer": _en_plural(ans, "multiple"),
                "distractors": [_en_plural(ans + 1, "multiple"), _en_plural(ans - 1, "multiple"), _en_plural(ans + div, "multiple")],
                "explanation": f"The multiples of {div} are {div}×1, {div}×2, {div}×3, …. The largest multiple not over {limit} is {div}×{ans}={div * ans}, so from {div}×1 to {div}×{ans} there are {ans} in all. That's the quotient of {limit}÷{div}.",
                "mistakes": [(_en_plural(ans + 1, "multiple"), f"{div}×{ans + 1}={div * (ans + 1)} is over {limit}. Count only up to the quotient.")],
                "detail": f"'How many multiples in a range' is a division quotient: {limit}÷{div}={ans}. Multiples sit at regular gaps ({div}), so the count is just 'how many fit'. If the range doesn't start at 1, find it by 'quotient of the top − quotient of the bottom'.",
            },
        )


# ── 88. 범위 안 공배수 개수 (난5, 수와연산) ──────────────────────────────────
def gen_common_mult_range():
    for limit, a, b in [(100, 3, 4), (100, 2, 5), (60, 3, 4), (200, 4, 6)]:
        lcm = a * b // gcd(a, b)
        ans = limit // lcm
        add(
            "commrange", "NUMBER_OPERATION", 5, ["공배수", "최소공배수"],
            f"1부터 {limit}까지의 자연수 중에서 {a}, {b} 두 수로 모두 나누어떨어지는 수는 몇 개일까요?",
            f"{ans}개", [f"{limit // a}개", f"{limit // b}개", f"{ans + 1}개"],
            f"{a}, {b} 두 수로 모두 나누어떨어지려면 두 수의 '공배수'여야 해요. 공배수는 최소공배수 {lcm}의 배수들이니, {limit}까지 {lcm}의 배수 개수 = {limit}÷{lcm}={ans}개예요.",
            [(f"{limit // a}개", f"그건 {a}의 배수 개수예요. 둘 다 나누어떨어지려면 공배수(최소공배수의 배수)를 세야 해요.")],
            detail=f"'A로도 B로도 나누어떨어짐' = A와 B의 공배수 = 최소공배수 {lcm}의 배수예요. 그래서 {limit}÷{lcm}만 세면 돼요. '적어도 하나로 나누어떨어짐'을 물으면 그땐 {a}의 배수 + {b}의 배수 − 공배수(포함배제)로 구하고요.",
            en={
                "statement": f"Among the whole numbers from 1 to {limit}, how many are divisible by both {a} and {b}?",
                "answer": _en_plural(ans, "number"),
                "distractors": [_en_plural(limit // a, "number"), _en_plural(limit // b, "number"), _en_plural(ans + 1, "number")],
                "explanation": f"To be divisible by both {a} and {b}, a number must be a 'common multiple' of the two. The common multiples are exactly the multiples of the least common multiple {lcm}, so the count up to {limit} is {limit}÷{lcm}={ans}.",
                "mistakes": [(_en_plural(limit // a, "number"), f"That's how many multiples of {a} there are. To be divisible by both, count the common multiples (the multiples of the least common multiple).")],
                "detail": f"'Divisible by both A and B' = a common multiple of A and B = a multiple of the least common multiple {lcm}. So you just count {limit}÷{lcm}. If it asked 'divisible by at least one', you'd use multiples of {a} + multiples of {b} − common multiples (inclusion-exclusion).",
            },
        )


# ── 89. 가중 평균 (난5, 자료와가능성) ────────────────────────────────────────
def gen_weighted_average():
    for n1, avg1, n2, avg2 in [(20, 80, 10, 89), (3, 70, 2, 95), (4, 85, 6, 75), (6, 90, 4, 70)]:
        total = n1 * avg1 + n2 * avg2
        assert total % (n1 + n2) == 0
        ans = total // (n1 + n2)
        add(
            "wavg", "DATA_POSSIBILITY", 5, ["평균", "가중 평균"],
            f"남학생 {n1}명의 평균이 {avg1}점, 여학생 {n2}명의 평균이 {avg2}점이에요. 반 전체({n1 + n2}명)의 평균은 몇 점일까요?",
            f"{ans}점", [f"{(avg1 + avg2) // 2}점", f"{ans + 3}점", f"{ans - 3}점"],
            f"두 평균을 그냥 더해 반으로 나누면 안 돼요(사람 수가 다르니까). '총점'으로 돌아가요: 남학생 {n1}×{avg1}={n1 * avg1}점, 여학생 {n2}×{avg2}={n2 * avg2}점. 전체 총점 {total}점을 전체 인원 {n1 + n2}명으로 나누면 {ans}점이에요.",
            [(f"{(avg1 + avg2) // 2}점", "두 평균의 평균이 아니에요 — 인원이 다르면 많은 쪽으로 치우쳐요.")],
            detail="여러 그룹의 전체 평균은 '가중 평균'이라 인원이 많은 쪽 평균에 더 가까워요. 늘 '총합 ÷ 전체 개수'로 돌아가면 안전해요. 두 그룹 인원이 같을 때만 단순 평균과 일치하고요. 타율·평점·물가지수가 다 가중 평균이에요.",
            en={
                "statement": f"The {n1} boys average {avg1} points and the {n2} girls average {avg2} points. What is the average for the whole class ({n1 + n2} students)?",
                "answer": _en_plural(ans, "point"),
                "distractors": [_en_plural((avg1 + avg2) // 2, "point"), _en_plural(ans + 3, "point"), _en_plural(ans - 3, "point")],
                "explanation": f"You can't just add the two averages and halve them (the group sizes differ). Go back to 'total points': boys {n1}×{avg1}={n1 * avg1} points, girls {n2}×{avg2}={n2 * avg2} points. Dividing the overall total {total} points by the total of {n1 + n2} students gives {ans} points.",
                "mistakes": [(_en_plural((avg1 + avg2) // 2, "point"), "It's not the average of the two averages — with different group sizes it leans toward the larger group.")],
                "detail": "The overall average of several groups is a 'weighted average', so it lands closer to the average of the larger group. Always going back to 'total sum ÷ total count' is safe. It equals the simple average only when the two groups are the same size. Batting averages, ratings, and price indexes are all weighted averages.",
            },
        )


# ── 90. 동전 여러 번 던지기 = 2^n (난4, 자료와가능성) ────────────────────────
def gen_coin_flips():
    for n in [3, 4, 5, 6]:
        ans = 2 ** n
        add(
            "coinflip", "DATA_POSSIBILITY", 4, ["경우의 수", "곱의 원리"],
            f"동전 하나를 {n}번 던져요. 나올 수 있는 앞뒤 결과(예: 앞-뒤-앞…)는 모두 몇 가지일까요?",
            f"{ans}가지", [f"{2 * n}가지", f"{ans - 1}가지", f"{ans + 1}가지"],
            f"한 번 던질 때마다 '앞' 또는 '뒤' 2가지예요. 던질 때마다 경우가 2배로 갈라지니 {n}번이면 2를 {n}번 곱한 {ans}가지예요.",
            [(f"{2 * n}가지", "2씩 더하는 게 아니라 매번 2배로 갈라져요(곱의 원리).")],
            detail=f"각 던지기가 서로 영향을 안 주니 2를 {n}번 곱해요(곱의 원리). '갈림길마다 몇 갈래인지 곱하기'는 경우의 수의 기본이에요. '앞면이 딱 2번' 같은 조건이면 그 안에서 자리를 고르는 조합으로 또 세면 되고요.",
            en={
                "statement": f"You flip one coin {n} times. How many possible heads/tails outcomes (e.g. heads-tails-heads…) are there in all?",
                "answer": _en_plural(ans, "way"),
                "distractors": [_en_plural(2 * n, "way"), _en_plural(ans - 1, "way"), _en_plural(ans + 1, "way")],
                "explanation": f"Each flip is one of 2 things — 'heads' or 'tails'. Every flip splits the cases into 2, so {n} flips give 2 multiplied {n} times, {ans} ways.",
                "mistakes": [(_en_plural(2 * n, "way"), "You don't add 2 each time — each flip splits into twice as many cases (the multiplication principle).")],
                "detail": f"Because each flip does not affect the others, multiply 2 a total of {n} times (the multiplication principle). 'At each fork, multiply by how many branches' is the basis of counting. For a condition like 'exactly 2 heads', you then count by choosing which positions with a combination.",
            },
        )


# ── 91. 주사위 두 개의 곱 (난5, 자료와가능성) ────────────────────────────────
def gen_dice_product():
    for target in [12, 6, 8, 24]:
        pairs = [(a, b) for a in range(1, 7) for b in range(1, 7) if a * b == target]
        cnt = len(pairs)
        add(
            "diceprod", "DATA_POSSIBILITY", 5, ["경우의 수", "곱"],
            f"주사위 두 개를 던져 나온 두 눈을 곱했더니 {target}이 됐어요. 이렇게 될 수 있는 경우(첫째 주사위, 둘째 주사위)는 모두 몇 가지일까요?",
            f"{cnt}가지", [f"{cnt - 1}가지", f"{cnt + 1}가지", f"{cnt + 2}가지"],
            f"두 주사위는 구별되니 순서가 다르면 다른 경우예요. 곱이 {target}이 되는 짝을 빠짐없이 찾으면 {', '.join(f'({a},{b})' for a, b in pairs)} — 모두 {cnt}가지예요.",
            [(f"{cnt - 1}가지", "순서가 다른 짝(예: (2,6)과 (6,2))을 빠뜨리지 않았는지 봐요.")],
            detail=f"두 주사위 문제는 6×6=36칸 표를 떠올리면 빠짐없이 셀 수 있어요. 곱이 {target}인 칸을 찾는 거죠. (a,b)와 (b,a)는 주사위를 구별하니 서로 다른 경우예요(단, a=b면 하나뿐). 곱셈표 감각이 있으면 약수 짝을 빠르게 찾아요.",
            en={
                "statement": f"You roll two dice and multiply the two numbers that come up, and the product is {target}. In how many ways (first die, second die) can this happen?",
                "answer": _en_plural(cnt, "way"),
                "distractors": [_en_plural(cnt - 1, "way"), _en_plural(cnt + 1, "way"), _en_plural(cnt + 2, "way")],
                "explanation": f"The two dice are distinct, so a different order is a different case. Finding every pair whose product is {target} gives {', '.join(f'({a},{b})' for a, b in pairs)} — {cnt} ways in all.",
                "mistakes": [(_en_plural(cnt - 1, "way"), "Check that you didn't miss a pair in the other order (e.g. (2,6) and (6,2)).")],
                "detail": f"For a two-dice problem, picturing the 6×6=36-cell table lets you count with nothing missed — you look for the cells whose product is {target}. (a,b) and (b,a) are different cases because the dice are distinct (but if a=b there is only one). A feel for the multiplication table helps you find divisor pairs quickly.",
            },
        )


# ── 92. 소금물 농도 (난6, 변화와관계) ────────────────────────────────────────
def gen_salt_concentration():
    for water, salt in [(90, 10), (80, 20), (150, 50), (85, 15)]:
        total = water + salt
        assert (salt * 100) % total == 0
        ans = salt * 100 // total
        add(
            "concn", "CHANGE_RELATION", 6, ["농도", "비율"],
            f"물 {water}g에 소금 {salt}g을 완전히 녹였어요. 이 소금물의 농도(진하기)는 몇 %일까요?",
            f"{ans}%", [f"{salt * 100 // water}%", f"{ans + 3}%", f"{ans - 3}%"],
            f"농도는 '소금물 전체 중 소금이 차지하는 비율'이에요. 소금물 전체는 물+소금 = {water}+{salt}={total}g. 그중 소금이 {salt}g이니 농도 = {salt}÷{total}×100 = {ans}%예요.",
            [(f"{salt * 100 // water}%", "물 무게가 아니라 '소금물 전체(물+소금)'로 나눠야 해요.")],
            detail="농도 = 소금 ÷ 소금물(물+소금) × 100. 분모가 '전체'라는 게 핵심이에요(물만 넣으면 틀려요). 물을 더 부으면 소금 양은 그대로인데 전체가 커져 농도가 낮아지고, 증발시키면 진해져요 — 소금 양을 고정해 두고 생각하면 쉬워요.",
            en={
                "statement": f"You fully dissolve {salt} g of salt in {water} g of water. What is the concentration (strength) of this salt water, in %?",
                "answer": f"{ans}%",
                "distractors": [f"{salt * 100 // water}%", f"{ans + 3}%", f"{ans - 3}%"],
                "explanation": f"Concentration is 'the fraction of the whole salt water that is salt'. The whole salt water is water+salt = {water}+{salt}={total} g. Of that, {salt} g is salt, so concentration = {salt}÷{total}×100 = {ans}%.",
                "mistakes": [(f"{salt * 100 // water}%", "You have to divide by the 'whole salt water (water+salt)', not by the weight of the water.")],
                "detail": "Concentration = salt ÷ salt water (water+salt) × 100. The key is that the denominator is the 'whole' (using just the water is wrong). Add more water and the amount of salt stays the same while the whole grows, so the concentration drops; evaporate it and it gets stronger — it's easy if you hold the amount of salt fixed.",
            },
        )


# ── 93. 백분율 — 전체의 일부 (난4, 수와연산) ────────────────────────────────
def gen_percent_of():
    for whole, pct in [(200, 15), (50, 30), (400, 25), (80, 60)]:
        assert (whole * pct) % 100 == 0
        ans = whole * pct // 100
        add(
            "percentof", "NUMBER_OPERATION", 4, ["백분율", "전체의 일부"],
            f"어느 학교 학생 {whole}명 중 {pct}%가 안경을 썼어요. 안경 쓴 학생은 몇 명일까요?",
            f"{ans}명", [f"{pct}명", f"{whole - ans}명", f"{ans + pct}명"],
            f"{pct}%는 '전체를 100으로 봤을 때 {pct}만큼'이라는 뜻이에요. 그러니 {whole}명의 {pct}% = {whole}×{pct}÷100 = {ans}명이에요. (또는 1%가 {whole}÷100={whole // 100 if whole % 100 == 0 else whole / 100:g}명이니 {pct}배 해도 {ans}.)",
            [(f"{pct}명", f"{pct}는 퍼센트(비율)예요. 전체 {whole}명에 곱해서 실제 인원을 구해요.")],
            detail=f"백분율은 '100분의 몇'이라는 비율이에요. 전체의 {pct}%는 전체를 100등분한 것 중 {pct}조각. 반대로 '{ans}명은 전체의 몇 %인가?'는 {ans}÷{whole}×100으로 거꾸로 구해요. 할인·이자·통계가 다 백분율 위에 있어요.",
            en={
                "statement": f"At a school, {pct}% of the {whole} students wear glasses. How many students wear glasses?",
                "answer": _en_plural(ans, "student"),
                "distractors": [_en_plural(pct, "student"), _en_plural(whole - ans, "student"), _en_plural(ans + pct, "student")],
                "explanation": f"{pct}% means '{pct} out of the whole seen as 100'. So {pct}% of {whole} = {whole}×{pct}÷100 = {ans}. (Or, since 1% is {whole}÷100={whole // 100 if whole % 100 == 0 else whole / 100:g}, multiplying by {pct} also gives {ans}.)",
                "mistakes": [(_en_plural(pct, "student"), f"{pct} is a percent (a ratio). Multiply it by the whole of {whole} to get the actual number of people.")],
                "detail": f"A percent is a ratio meaning 'so many out of 100'. {pct}% of the whole is {pct} slices when the whole is split into 100. Going the other way, '{ans} is what percent of the whole?' is found by {ans}÷{whole}×100. Discounts, interest, and statistics all rest on percentages.",
            },
        )


# ── 94. 톱니바퀴 = 반비례 (난5, 변화와관계) ─────────────────────────────────
def gen_gear_ratio():
    for t1, turns1, t2 in [(8, 3, 12), (10, 6, 15), (12, 5, 20), (9, 8, 6)]:
        assert (t1 * turns1) % t2 == 0
        turns2 = t1 * turns1 // t2
        add(
            "gear", "CHANGE_RELATION", 5, ["톱니바퀴", "반비례"],
            f"톱니 {t1}개인 바퀴와 톱니 {t2}개인 바퀴가 맞물려 돌아가요. 톱니 {t1}개 바퀴가 {turns1}바퀴 도는 동안, 톱니 {t2}개 바퀴는 몇 바퀴 돌까요?",
            f"{turns2}바퀴", [f"{turns1}바퀴", f"{turns1 * t2 // t1}바퀴", f"{turns2 - 1}바퀴"],
            f"맞물린 두 바퀴는 '지나간 톱니 수'가 똑같아요. 톱니 {t1}개 바퀴가 {turns1}바퀴 돌면 {t1}×{turns1}={t1 * turns1}개의 톱니가 지나가요. 상대 바퀴도 같은 {t1 * turns1}개가 지나가야 하니 {t1 * turns1}÷{t2}={turns2}바퀴. 톱니가 많은 바퀴는 천천히 돌죠.",
            [(f"{turns1}바퀴", "톱니 수가 다르면 회전수도 달라요. 지나간 톱니 수가 같다는 걸 이용해요.")],
            detail="맞물린 톱니바퀴는 '톱니수 × 회전수'가 일정해요(반비례). 톱니가 2배면 회전은 절반. 자전거 기어·시계 톱니가 다 이 원리예요. 반비례는 '두 양의 곱이 일정'으로 보면 늘 쉬워져요(속력×시간=거리 일정도 같은 결).",
            en={
                "statement": f"A wheel with {t1} teeth meshes with a wheel with {t2} teeth. While the {t1}-tooth wheel makes {turns1} turns, how many turns does the {t2}-tooth wheel make?",
                "answer": f"{turns2} turns",
                "distractors": [f"{turns1} turns", f"{turns1 * t2 // t1} turns", f"{turns2 - 1} turns"],
                "explanation": f"Two meshed wheels pass the exact same 'number of teeth'. When the {t1}-tooth wheel makes {turns1} turns, {t1}×{turns1}={t1 * turns1} teeth go by. The other wheel must pass the same {t1 * turns1} teeth, so {t1 * turns1}÷{t2}={turns2} turns. A wheel with more teeth turns more slowly.",
                "mistakes": [(f"{turns1} turns", "Different tooth counts mean different numbers of turns. Use the fact that the same number of teeth pass by.")],
                "detail": "For meshed gears, 'number of teeth × number of turns' stays constant (inverse proportion). Twice the teeth, half the turns. Bicycle gears and clock cogs all work this way. Inverse proportion always gets easier when you see it as 'the product of the two quantities stays constant' (speed×time=distance is the same idea).",
            },
        )


# ── 95. 시소 균형 = 모멘트 (난5, 변화와관계) ────────────────────────────────
def gen_seesaw():
    for w1, d1, w2 in [(30, 2, 20), (40, 3, 24), (20, 6, 30), (35, 4, 28)]:
        assert (w1 * d1) % w2 == 0
        d2 = w1 * d1 // w2
        add(
            "seesaw", "CHANGE_RELATION", 5, ["시소", "지렛대(반비례)"],
            f"시소의 받침점에서 {d1}m 떨어진 곳에 몸무게 {w1}kg인 형이 앉았어요. 몸무게 {w2}kg인 동생은 받침점에서 몇 m 떨어진 곳에 앉아야 시소가 수평이 될까요?",
            f"{d2}m", [f"{d1}m", f"{w2 * d1 // w1}m", f"{d2 + 1}m"],
            f"시소는 '무게 × 받침점까지의 거리'가 양쪽이 같을 때 균형을 이뤄요. 형 쪽은 {w1}×{d1}={w1 * d1}. 동생 쪽도 {w1 * d1}이 되어야 하니 {w1 * d1}÷{w2}={d2}m. 가벼운 사람이 더 멀리 앉아야 하죠.",
            [(f"{d1}m", "같은 거리에 앉으면 무거운 쪽으로 기울어요. 가벼우면 더 멀리 앉아요.")],
            detail="시소 균형의 비밀은 '무게 × 거리(모멘트)'가 양쪽 같아야 한다는 거예요. 그래서 무게와 거리는 반비례 — 몸무게가 절반이면 두 배 멀리. 지레·저울·병따개가 다 이 지렛대 원리예요.",
            en={
                "statement": f"On a seesaw, child A weighing {w1}kg sits {d1}m from the pivot. Child B weighs {w2}kg. How many metres from the pivot must B sit for the seesaw to balance?",
                "answer": f"{d2}m",
                "distractors": [f"{d1}m", f"{w2 * d1 // w1}m", f"{d2 + 1}m"],
                "explanation": f"A seesaw balances when 'weight × distance from the pivot' is the same on both sides. A's side is {w1}×{d1}={w1 * d1}. B's side must also be {w1 * d1}, so {w1 * d1}÷{w2}={d2}m. The lighter person has to sit farther out.",
                "mistakes": [(f"{d1}m", "Sitting at the same distance tips it toward the heavier side. The lighter one sits farther out.")],
                "detail": "The secret to seesaw balance is that 'weight × distance (the moment)' must be equal on both sides. So weight and distance are inversely proportional — half the weight, twice the distance. Levers, scales, and bottle openers all use this lever principle.",
            },
        )


# ── 96. 약수의 합 (난5, 수와연산) ────────────────────────────────────────────
def gen_divisor_sum():
    for num in [12, 18, 28, 24]:
        divs = [x for x in range(1, num + 1) if num % x == 0]
        ans = sum(divs)
        add(
            "divsum", "NUMBER_OPERATION", 5, ["약수", "약수의 합"],
            f"{num}의 약수를 모두 찾아 더하면 얼마일까요?",
            f"{ans}", [str(ans - num), str(ans + num), str(ans + 3)],
            f"약수를 '작은 수 × 큰 수' 짝으로 빠짐없이 찾아요: {num}의 약수는 {', '.join(map(str, divs))}. 모두 더하면 {' + '.join(map(str, divs))} = {ans}이에요.",
            [(str(ans - num), f"자기 자신({num})도 약수예요 — 빠뜨리지 마세요.")],
            detail=f"약수는 짝을 지어 찾으면 빠짐이 없어요(1×{num}, 2×…). 자기 자신을 뺀 약수의 합이 자신과 같으면 '완전수'(6=1+2+3), 자신보다 크면 '과잉수'라고 불러요. {num}이 어디에 속하는지 따져 보는 것도 재미있어요.",
            en={
                "statement": f"Find all the divisors of {num} and add them up. What is the sum?",
                "answer": f"{ans}",
                "distractors": [str(ans - num), str(ans + num), str(ans + 3)],
                "explanation": f"Find the divisors in 'small × large' pairs so none are missed: the divisors of {num} are {', '.join(map(str, divs))}. Adding them all gives {' + '.join(map(str, divs))} = {ans}.",
                "mistakes": [(str(ans - num), f"{num} itself is also a divisor — don't leave it out.")],
                "detail": f"Finding divisors in pairs (1×{num}, 2×…) means you miss none. If the sum of the divisors excluding the number itself equals the number, it's a 'perfect number' (6=1+2+3); if it's larger, an 'abundant number'. It's fun to work out where {num} falls.",
            },
        )


# ── 97. 시계 종소리 = 간격 함정 (난4, 변화와관계) ───────────────────────────
def gen_clock_strikes():
    for h1, sec1, h2 in [(4, 6, 7), (3, 4, 9), (5, 8, 11), (7, 12, 10)]:
        assert sec1 % (h1 - 1) == 0
        gap = sec1 // (h1 - 1)
        ans = (h2 - 1) * gap
        add(
            "clockstrike", "CHANGE_RELATION", 4, ["간격 사고", "시계 종"],
            f"벽시계가 {h1}시에 '{h1}번' 치는 데 {sec1}초가 걸려요. 그렇다면 {h2}시에 '{h2}번' 치는 데는 몇 초가 걸릴까요?",
            f"{ans}초", [f"{gap * h2}초", f"{ans - gap}초", f"{sec1}초"],
            f"함정은 '치는 횟수'가 아니라 '소리 사이 간격 수'예요. {h1}번 치면 사이 간격은 {h1}−1={h1 - 1}개. 그 {h1 - 1}개에 {sec1}초가 걸리니 간격 하나는 {sec1}÷{h1 - 1}={gap}초. {h2}번 치면 간격이 {h2}−1={h2 - 1}개니 {h2 - 1}×{gap}={ans}초예요.",
            [(f"{gap * h2}초", "횟수에 그대로 비례하지 않아요 — '사이 간격'의 수로 따져야 해요.")],
            detail="'종을 n번 친다'와 '간격이 n−1개다'의 차이가 핵심이에요(나무 심기·자르기와 같은 간격 함정). 첫 소리엔 시간이 안 걸리고, 소리와 소리 '사이'에만 시간이 흘러요. 이 1 차이를 놓치면 답이 어긋나요.",
            en={
                "statement": f"A wall clock takes {sec1} seconds to strike '{h1} times' at {h1} o'clock. Then how many seconds does it take to strike '{h2} times' at {h2} o'clock?",
                "answer": f"{ans} seconds",
                "distractors": [f"{gap * h2} seconds", f"{ans - gap} seconds", f"{sec1} seconds"],
                "explanation": f"The trap is not the 'number of strikes' but the 'number of gaps between sounds'. Striking {h1} times makes {h1}−1={h1 - 1} gaps. Those {h1 - 1} gaps take {sec1} seconds, so one gap is {sec1}÷{h1 - 1}={gap} seconds. Striking {h2} times makes {h2}−1={h2 - 1} gaps, so {h2 - 1}×{gap}={ans} seconds.",
                "mistakes": [(f"{gap * h2} seconds", "It is not directly proportional to the number of strikes — count the number of gaps in between.")],
                "detail": "The difference between 'strike n times' and 'there are n−1 gaps' is the key (the same interval trap as planting trees or cutting a log). The first sound takes no time; time passes only 'between' one sound and the next. Miss this off-by-one and your answer is wrong.",
            },
        )


# ── 98. 세 항의 비 (난5, 변화와관계) ─────────────────────────────────────────
def gen_ratio_three():
    for total, ra, rb, rc in [(60, 2, 3, 5), (48, 1, 2, 3), (70, 3, 4, 7), (36, 2, 2, 5)]:
        s = ra + rb + rc
        assert total % s == 0
        unit = total // s
        ans = unit * rc
        add(
            "ratio3", "CHANGE_RELATION", 5, ["비", "세 몫으로 나누기"],
            f"사탕 {total}개를 세 사람 A, B, C가 {ra}:{rb}:{rc}로 나눠 가져요. C가 갖는 사탕은 몇 개일까요?",
            f"{ans}개", [f"{rc}개", f"{unit * ra}개", f"{total // 3}개"],
            f"비 {ra}:{rb}:{rc}는 전체를 똑같은 묶음 {ra}+{rb}+{rc}={s}묶음으로 나눈 거예요. 한 묶음은 {total}÷{s}={unit}개. C는 {rc}묶음이니 {unit}×{rc}={ans}개예요.",
            [(f"{total // 3}개", "셋이 똑같이 나누는 게 아니에요. 비가 다르니 묶음 수로 나눠요.")],
            detail="세 항의 비도 방법은 같아요 — '한 묶음(단위량) = 전체 ÷ 비의 합'을 먼저 구하고 각자 몫만큼 곱하면 끝. 항이 몇 개든 통해요. 비는 '전체를 몇 조각으로, 각자 몇 조각'의 그림으로 보면 늘 쉬워요.",
            en={
                "statement": f"{total} candies are shared among three people A, B, C in the ratio {ra}:{rb}:{rc}. How many candies does C get?",
                "answer": f"{ans} candies",
                "distractors": [f"{rc} candies", f"{unit * ra} candies", f"{total // 3} candies"],
                "explanation": f"The ratio {ra}:{rb}:{rc} splits the whole into {ra}+{rb}+{rc}={s} equal groups. One group is {total}÷{s}={unit} candies. C has {rc} groups, so {unit}×{rc}={ans} candies.",
                "mistakes": [(f"{total // 3} candies", "The three don't split it equally. The ratios differ, so divide by the number of groups.")],
                "detail": "A three-term ratio uses the same method — find 'one group (the unit amount) = whole ÷ sum of the ratio' first, then multiply by each share. It works for any number of terms. Ratios are always easy when you picture 'the whole in so many slices, and how many slices each'.",
            },
        )


# ── 99. 주고받기 = 차이 사고 (난5, 변화와관계) ──────────────────────────────
def gen_marble_transfer():
    for give, ctx in [(3, "구슬"), (5, "사탕"), (4, "딱지"), (2, "스티커")]:
        ans = 2 * give
        en_item = {"구슬": "marbles", "사탕": "candies", "딱지": "cards", "스티커": "stickers"}[ctx]
        add(
            "transfer", "CHANGE_RELATION", 5, ["차이 사고", "주고받기"],
            f"형과 동생이 {ctx}{_eul(ctx)} 가지고 있어요. 형이 동생에게 {ctx} {give}개를 주면 둘의 개수가 똑같아진대요. 원래 형은 동생보다 {ctx}{_eul(ctx)} 몇 개 더 가지고 있었을까요?",
            f"{ans}개", [f"{give}개", f"{give * 3}개", f"{ans - 1}개"],
            f"형이 {give}개를 주면 형은 {give} 줄고 동생은 {give} 늘어요. 그러면 둘 사이 차이는 한 번에 {give}+{give}={ans}만큼 줄어요. 주고 나서 '같아졌다'(차이 0)니 원래 차이는 딱 그만큼인 {ans}개였어요.",
            [(f"{give}개", f"준 개수 그대로가 아니에요 — 주는 쪽은 줄고 받는 쪽은 늘어 차이는 {give}의 두 배만큼 줄어요.")],
            detail="주고받기는 '차이가 어떻게 변하나'를 보면 쉬워요. 한 명이 상대에게 k개를 주면 차이는 2k만큼 줄어요(주는 쪽 −k, 받는 쪽 +k). 반대로 '얼마를 줘야 같아질까?'는 차이의 절반을 주면 되고요. 전체 합은 주고받아도 안 변한다는 것도 함께 기억하면 든든해요.",
            en={
                "statement": f"Child A and child B each have some {en_item}. If A gives B {give} {en_item}, they end up with the same number. How many more {en_item} did A originally have than B?",
                "answer": f"{ans} {en_item}",
                "distractors": [f"{give} {en_item}", f"{give * 3} {en_item}", f"{ans - 1} {en_item}"],
                "explanation": f"When A gives away {give}, A goes down by {give} and B goes up by {give}. So the gap between them shrinks all at once by {give}+{give}={ans}. Since after giving they became 'equal' (gap 0), the original gap was exactly that much: {ans} {en_item}.",
                "mistakes": [(f"{give} {en_item}", f"It's not simply the number given — the giver loses and the receiver gains, so the gap shrinks by twice {give}.")],
                "detail": "Giving and taking is easy once you watch 'how the difference changes'. When one person gives k to the other, the difference shrinks by 2k (giver −k, receiver +k). Conversely, 'how much to give to make them equal?' is to give half the difference. It also helps to remember the total sum never changes with giving and taking.",
            },
        )


# ── 100. 똑같이 나누려면 최소 보충 (난4, 수와연산) ──────────────────────────
def gen_least_to_share():
    for candy, kids in [(20, 6), (30, 7), (15, 4), (50, 8)]:
        r = candy % kids
        ans = (kids - r) % kids
        assert 0 < ans < kids
        _cd = lambda k: f"{k} candy" if k == 1 else f"{k} candies"
        add(
            "leasttoshare", "NUMBER_OPERATION", 4, ["나머지", "최소 보충"],
            f"사탕 {candy}개를 친구 {kids}명에게 '똑같이' 나눠주려고 해요. 남거나 모자라지 않게 나누려면 사탕이 '최소' 몇 개 더 있어야 할까요?",
            f"{ans}개", [f"{r}개", f"{kids}개", f"{ans + kids}개"],
            f"{candy}÷{kids}를 하면 한 명당 {candy // kids}개씩, {r}개가 남아요. 남은 {r}개로는 {kids}명에게 하나씩 더 못 주니 {kids}개를 채워야 다 같이 하나씩 더 받아요. 그래서 {kids}−{r}={ans}개가 더 필요해요.",
            [(f"{r}개", f"그건 남는 개수예요. 모두에게 하나씩 더 주려면 {kids}−{r}만큼 채워야 해요.")],
            detail=f"'똑같이 나누기'는 나머지가 열쇠예요. 나머지가 {r}이면 다음 배수까지 {kids}−{r}={ans}만큼만 더하면 딱 떨어져요(모두 한 개씩 더). 반대로 '최소 몇 개 빼면 딱 떨어질까?'는 나머지 {r}개를 빼면 되고요. 배수와 나머지를 오가는 감각이에요.",
            en={
                "statement": f"You want to share {candy} candies 'equally' among {kids} friends. To share with none left over and none short, at least how many more candies do you need?",
                "answer": _cd(ans),
                "distractors": [_cd(r), _cd(kids), _cd(ans + kids)],
                "explanation": f"{candy}÷{kids} gives {candy // kids} each with {r} left over. The {r} left over aren't enough to give one more to all {kids} friends, so you need {kids} to fill up and everyone gets one more. That's why you need {kids}−{r}={ans} more.",
                "mistakes": [(_cd(r), f"That's the number left over. To give everyone one more, you must fill up by {kids}−{r}.")],
                "detail": f"For 'sharing equally', the remainder is the key. If the remainder is {r}, adding just {kids}−{r}={ans} reaches the next multiple and divides evenly (everyone one more). Going the other way, 'at least how many to take away to divide evenly?' is just removing the remainder of {r}. It's a feel for moving between multiples and remainders.",
            },
        )


# ── 101. 물탱크 채우기와 새기 = 순 일률 (난6, 변화와관계) ────────────────────
def gen_tank_fill_drain():
    for cap, fill, drain in [(60, 16, 4), (100, 25, 5), (48, 10, 4), (90, 21, 6)]:
        net = fill - drain
        assert cap % net == 0
        ans = cap // net
        add(
            "tank", "CHANGE_RELATION", 6, ["일률", "채우기와 빼기"],
            f"빈 물탱크(용량 {cap}L)에 물을 넣는 관은 1분에 {fill}L를 채우고, 동시에 새는 구멍으로 1분에 {drain}L가 빠져나가요. 탱크가 가득 차는 데 몇 분이 걸릴까요?",
            f"{ans}분", [f"{cap // fill}분", f"{cap // drain}분", f"{ans + 2}분"],
            f"채우기와 빼기가 동시에 일어나니 '1분에 실제로 늘어나는 양'을 봐요: {fill}−{drain}={net}L씩 늘어요. 용량 {cap}L를 이 속도로 채우니 {cap}÷{net}={ans}분이 걸려요.",
            [(f"{cap // fill}분", "새는 물을 빼먹었어요. 실제로 늘어나는 양은 (넣는 양 − 새는 양)이에요.")],
            detail="'동시에 반대로 작용'하는 문제는 순수 증가량(넣기 − 빼기)으로 바꾸면 간단해져요. 새는 양이 넣는 양보다 크면 영영 못 채우고, 같으면 그대로예요. 일 문제(하나는 만들고 하나는 부수는)도 똑같은 '순 일률'로 풀려요.",
            en={
                "statement": f"An empty water tank (capacity {cap} L) has an inflow pipe that fills {fill} L per minute, while at the same time a leak drains {drain} L per minute. How many minutes does it take for the tank to fill up?",
                "answer": _en_plural(ans, "minute"),
                "distractors": [_en_plural(cap // fill, "minute"), _en_plural(cap // drain, "minute"), _en_plural(ans + 2, "minute")],
                "explanation": f"Since filling and draining happen at the same time, look at 'how much actually builds up each minute': {fill}−{drain}={net} L more per minute. Filling the {cap} L capacity at this rate takes {cap}÷{net}={ans} minutes.",
                "mistakes": [(_en_plural(cap // fill, "minute"), "You left out the leaking water. The amount that actually builds up is (inflow − leak).")],
                "detail": "Problems with 'opposite actions happening at once' get simple when you switch to the net gain (inflow − leak). If the leak is bigger than the inflow it never fills; if they're equal it stays put. Work problems (one builds while another tears down) solve with the same 'net rate'.",
            },
        )


# ── 102. 윤년 개수 (난5, 수와연산) ───────────────────────────────────────────
def gen_leap_year_count():
    for y1, y2 in [(2001, 2020), (1997, 2016), (2004, 2024), (2010, 2040)]:
        cnt = sum(1 for y in range(y1, y2 + 1) if (y % 4 == 0 and y % 100 != 0) or y % 400 == 0)
        add(
            "leapyear", "NUMBER_OPERATION", 5, ["배수", "윤년 규칙"],
            f"{y1}년부터 {y2}년까지 중에서 윤년(2월이 29일까지 있는 해)은 모두 몇 번일까요? 윤년은 4로 나누어떨어지는 해예요(단, 100으로 나누어떨어지면 제외, 400으로 나누어떨어지면 다시 윤년).",
            f"{cnt}번", [f"{cnt + 1}번", f"{cnt - 1}번", f"{cnt + 2}번"],
            f"윤년은 기본적으로 4의 배수 해예요. {y1}~{y2} 사이에서 4의 배수 해를 세면 {cnt}번이에요(이 구간엔 100·400 예외로 달라지는 해가 없어요).",
            [(f"{cnt + 1}번", "4의 배수를 셀 때 시작·끝 해를 잘못 포함했을 수 있어요.")],
            detail="윤년 규칙은 '4의 배수 → 윤년, 단 100의 배수는 제외, 400의 배수는 다시 윤년'이에요(2000년은 윤년, 1900년은 아님). 지구가 태양을 도는 데 정확히 365일이 아니라 약 365.25일이라, 4년마다 하루를 더해 맞추는 거예요. 이런 '배수 규칙'은 나머지로 판정해요.",
            en={
                "statement": f"From {y1} to {y2}, how many leap years (years where February has 29 days) are there? A leap year is a year divisible by 4 (except that a year divisible by 100 is not a leap year, but a year divisible by 400 is a leap year again).",
                "answer": _en_plural(cnt, "leap year"),
                "distractors": [_en_plural(cnt + 1, "leap year"), _en_plural(cnt - 1, "leap year"), _en_plural(cnt + 2, "leap year")],
                "explanation": f"A leap year is basically a year that's a multiple of 4. Counting the multiples of 4 between {y1} and {y2} gives {cnt} (this range has no years shifted by the 100/400 exceptions).",
                "mistakes": [(_en_plural(cnt + 1, "leap year"), "When counting the multiples of 4, you may have wrongly included the start or end year.")],
                "detail": "The leap-year rule is 'multiple of 4 → leap year, except a multiple of 100 is not, but a multiple of 400 is again' (2000 was a leap year, 1900 was not). Because Earth takes about 365.25 days — not exactly 365 — to orbit the Sun, we add a day every 4 years to keep in step. A 'multiple rule' like this is decided using remainders.",
            },
        )


# ── 103. 목표 평균에 필요한 점수 (난4, 자료와가능성) ─────────────────────────
def gen_average_needed():
    for done, cur_avg, target_avg in [(3, 80, 85), (4, 75, 80), (2, 90, 88), (4, 82, 85)]:
        n = done + 1
        needed = n * target_avg - done * cur_avg
        add(
            "avgneed", "DATA_POSSIBILITY", 4, ["평균", "총합 사고"],
            f"지금까지 {done}과목 시험을 봐서 평균이 {cur_avg}점이에요. 한 과목을 더 봐서 {n}과목 평균을 {target_avg}점으로 만들려면, 다음 과목에서 몇 점을 받아야 할까요?",
            f"{needed}점", [f"{target_avg}점", f"{needed - 5}점", f"{needed + 5}점"],
            f"평균을 '총합'으로 바꿔요. {n}과목 평균 {target_avg}점이 되려면 총점이 {n}×{target_avg}={n * target_avg}점이어야 해요. 지금까지 {done}과목 총점은 {done}×{cur_avg}={done * cur_avg}점이니, 다음 과목은 {n * target_avg}−{done * cur_avg}={needed}점 받아야 해요.",
            [(f"{target_avg}점", f"목표 평균({target_avg}점)만 받아선 평균이 안 올라가요 — 지난 과목들 몫까지 끌어올려야 해요.")],
            detail="'목표 평균을 위해 필요한 값'은 (목표 총합) − (지금 총합)이에요. 목표보다 지금 평균이 낮으면 목표보다 더 높은 점수가 필요하고, 이미 높으면 목표보다 낮아도 돼요. 평균 문제는 늘 '총합'으로 돌아가면 안전해요.",
            en={
                "statement": f"So far you have taken {done} subject exams with an average of {cur_avg} points. To take one more subject and make the {n}-subject average {target_avg} points, what score do you need on the next subject?",
                "answer": f"{needed} points",
                "distractors": [f"{target_avg} points", f"{needed - 5} points", f"{needed + 5} points"],
                "explanation": f"Turn the average into a 'total'. For the {n}-subject average to be {target_avg}, the total must be {n}×{target_avg}={n * target_avg} points. Your total so far over {done} subjects is {done}×{cur_avg}={done * cur_avg} points, so the next subject needs {n * target_avg}−{done * cur_avg}={needed} points.",
                "mistakes": [(f"{target_avg} points", f"Just scoring the target average ({target_avg} points) won't raise your average — you have to make up for the earlier subjects too.")],
                "detail": "The 'value needed to reach a target average' is (target total) − (current total). If your current average is below the target, you need a score above the target; if it is already high, a lower score is fine. With average problems it is always safe to go back to the 'total'.",
            },
        )


# ── 104. 컵 쌓기 = 등차 (난4, 변화와관계) ────────────────────────────────────
def gen_stacking_cups():
    for base, add_each, n in [(10, 3, 5), (12, 4, 6), (8, 2, 10), (15, 5, 4)]:
        ans = base + add_each * (n - 1)
        add(
            "cups", "CHANGE_RELATION", 4, ["등차", "규칙 세우기"],
            f"컵 하나의 높이는 {base}cm예요. 똑같은 컵을 하나씩 포개면 겹치는 만큼 빼고 {add_each}cm씩만 높아져요. 컵 {n}개를 포개면 전체 높이는 몇 cm일까요?",
            f"{ans}cm", [f"{base * n}cm", f"{base + add_each * n}cm", f"{ans - add_each}cm"],
            f"첫 컵은 {base}cm. 두 번째부터는 {add_each}cm씩만 더해져요. 컵이 {n}개면 처음 {base}에 {add_each}씩 {n}−1={n - 1}번 더하니 {base}+{add_each}×{n - 1}={ans}cm예요.",
            [(f"{base * n}cm", f"컵마다 {base}cm씩 곱하면 안 돼요 — 겹치니까 두 번째부터는 {add_each}cm씩만 늘어요.")],
            detail=f"'처음 값 + 일정하게 더하기'가 등차수열이에요. n번째 = 첫 값 + (n−1)×(매번 더하는 양). 함정은 '몇 번 더하나' — {n}개면 {n}−1번만 더해요(첫 컵엔 안 더함). 계단·나무 심기와 같은 '간격' 감각이에요.",
            en={
                "statement": f"One cup is {base} cm tall. Stacking identical cups one at a time, each new cup raises the height by only {add_each} cm (the overlap is subtracted). Stacking {n} cups, what is the total height in cm?",
                "answer": f"{ans} cm",
                "distractors": [f"{base * n} cm", f"{base + add_each * n} cm", f"{ans - add_each} cm"],
                "explanation": f"The first cup is {base} cm. From the second on, each adds only {add_each} cm. With {n} cups you add {add_each} a total of {n}−1={n - 1} times onto the first {base}, so {base}+{add_each}×{n - 1}={ans} cm.",
                "mistakes": [(f"{base * n} cm", f"Don't multiply {base} cm by every cup — because they overlap, from the second cup on the height grows by only {add_each} cm.")],
                "detail": f"'A starting value plus adding a constant' is an arithmetic sequence. The nth = first value + (n−1)×(the amount added each time). The trap is 'how many times you add' — with {n} cups you add only {n}−1 times (nothing is added for the first cup). It is the same 'interval' sense as stairs and planting trees.",
            },
        )


# ── 105. 수직선 뛰기 = 순 변화량 (난4, 변화와관계) ──────────────────────────
def gen_number_line_jump():
    for start, fwd, back, rounds in [(0, 5, 2, 4), (0, 4, 1, 6), (10, 3, 5, 3), (0, 6, 2, 5)]:
        ans = start + (fwd - back) * rounds
        add(
            "numline", "CHANGE_RELATION", 4, ["규칙", "반복 변화"],
            f"수직선의 {start}에서 개구리가 뛰어요. 앞으로 {fwd}칸 갔다가 뒤로 {back}칸 오는 걸 한 번으로 쳐서, 이걸 {rounds}번 반복하면 개구리는 어디에 있을까요?",
            str(ans), [str(start + fwd * rounds), str(ans + fwd), str(start + (fwd - back) * (rounds - 1))],
            f"한 번 반복하면 실제로는 앞으로 {fwd}−{back}={fwd - back}칸씩 나아가요. {rounds}번 반복하면 {fwd - back}×{rounds}={(fwd - back) * rounds}칸 나아가니, {start}에서 출발해 {ans}에 도착해요.",
            [(str(start + fwd * rounds), "뒤로 오는 것도 세어야 해요 — 한 번에 순수하게 나아가는 건 (앞−뒤)칸이에요.")],
            detail="'앞으로 갔다 뒤로'를 반복하면 한 번당 순 이동은 (앞−뒤)예요. 이 순이동에 횟수를 곱하면 끝. 뒤로가 앞으로보다 크면 오히려 뒷걸음질치고요. 우물 개구리·따라잡기와 같은 '순 변화량' 사고예요.",
            en={
                "statement": f"A frog jumps from {start} on a number line. Going forward {fwd} steps then back {back} steps counts as one round; repeating this {rounds} times, where is the frog?",
                "answer": str(ans),
                "distractors": [str(start + fwd * rounds), str(ans + fwd), str(start + (fwd - back) * (rounds - 1))],
                "explanation": f"One round actually advances {fwd}−{back}={fwd - back} steps. Repeating {rounds} times advances {fwd - back}×{rounds}={(fwd - back) * rounds} steps, so starting from {start} the frog ends at {ans}.",
                "mistakes": [(str(start + fwd * rounds), "You have to count the steps back too — one round nets (forward − back) steps.")],
                "detail": "Repeating 'go forward then back' nets (forward − back) per round. Multiply that net move by the number of rounds and you're done. If back is bigger than forward, it actually moves backward. It is the same 'net change' thinking as the frog in the well or catching-up problems.",
            },
        )


# ── 106. 연속 할인 = 곱셈 (난6, 변화와관계) ─────────────────────────────────
def gen_double_discount():
    for price, d1, d2 in [(10000, 20, 10), (20000, 30, 20), (5000, 10, 10), (8000, 25, 20)]:
        after1 = price * (100 - d1) // 100
        ans = after1 * (100 - d2) // 100
        naive = price * (100 - d1 - d2) // 100
        add(
            "dblsale", "CHANGE_RELATION", 6, ["백분율", "연속 할인"],
            f"{price}원짜리 물건을 {d1}% 할인한 뒤, 그 가격에서 다시 {d2}%를 더 할인했어요. 최종 가격은 얼마일까요?",
            f"{ans}원", [f"{naive}원", f"{after1}원", f"{ans - 500}원"],
            f"할인은 '남은 가격에' 차례로 적용돼요. 먼저 {d1}% 할인하면 {100 - d1}%가 남아 {price}×{100 - d1}÷100={after1}원. 여기서 다시 {d2}% 할인하면 {after1}×{100 - d2}÷100={ans}원이에요.",
            [(f"{naive}원", f"두 할인율을 더해서({d1}+{d2}={d1 + d2}%) 한 번에 빼면 안 돼요 — 두 번째 할인은 '이미 깎인 가격'에 적용돼요.")],
            detail=f"연속 할인은 '더하기'가 아니라 '곱하기'예요. {d1}% 뒤 {d2}%는 {100 - d1}%의 {100 - d2}%라, {d1}+{d2}%를 한 번에 빼는 것보다 덜 깎여요(그래서 {naive}원이 아니라 {ans}원). 이자·인구 증가율을 연속으로 적용할 때도 똑같이 곱셈으로 이어져요.",
            en={
                "statement": f"An item costs {price} coins. It is discounted by {d1}%, then from that price discounted by a further {d2}%. What is the final price?",
                "answer": _en_plural(ans, "coin"),
                "distractors": [_en_plural(naive, "coin"), _en_plural(after1, "coin"), _en_plural(ans - 500, "coin")],
                "explanation": f"Discounts apply one after another 'to the remaining price'. First a {d1}% discount leaves {100 - d1}%, so {price}×{100 - d1}÷100={after1} coins. Discounting that by another {d2}% gives {after1}×{100 - d2}÷100={ans} coins.",
                "mistakes": [(_en_plural(naive, "coin"), f"You can't add the two discount rates ({d1}+{d2}={d1 + d2}%) and take them off at once — the second discount applies to the 'already reduced price'.")],
                "detail": f"Successive discounts 'multiply', they don't 'add'. {d1}% then {d2}% is {100 - d2}% of {100 - d1}%, so it takes off less than subtracting {d1}+{d2}% at once (that's why it's {ans} coins, not {naive} coins). Applying interest or population-growth rates one after another chains the same way, by multiplication.",
            },
        )


# ── 107. 합이 일정할 때 곱 최대 (난5, 수와연산) ─────────────────────────────
def gen_max_product():
    for s in [10, 14, 20, 16]:
        a = s // 2
        b = s - a
        ans = a * b
        add(
            "maxprod", "NUMBER_OPERATION", 5, ["합이 일정", "곱 최대"],
            f"두 자연수를 더하면 {s}가 돼요. 이 두 수의 '곱'이 가장 클 때, 그 곱은 얼마일까요?",
            f"{ans}", [str(s - 1), str(ans - 1), str(a * b + a)],
            f"합이 정해진 두 수는 서로 '가까울수록' 곱이 커져요. {s}를 최대한 똑같이 둘로 나누면 {a}와 {b}. 그때 곱이 최대인 {a}×{b}={ans}예요. (1×{s - 1}={s - 1}처럼 벌어지면 곱이 작아져요.)",
            [(str(s - 1), "양 끝(1과 큰 수)으로 벌리면 곱이 가장 작아요. 가운데로 모아야 최대예요.")],
            detail="'합이 일정할 때 곱은 두 수가 같을 때 최대'예요 — 같은 둘레에서 정사각형이 넓이가 최대인 것과 똑같은 원리(가로+세로 일정 → 정사각형이 최대 넓이). 반대로 '곱이 일정할 때 합은 두 수가 같을 때 최소'고요. 자연·경제 곳곳의 '균형이 최적' 현상이에요.",
            en={
                "statement": f"Two whole numbers add up to {s}. When their 'product' is as large as possible, what is that product?",
                "answer": f"{ans}",
                "distractors": [str(s - 1), str(ans - 1), str(a * b + a)],
                "explanation": f"For two numbers with a fixed sum, the closer they are to each other, the larger the product. Splitting {s} as evenly as possible gives {a} and {b}, and that's when the product is largest: {a}×{b}={ans}. (Spread them apart, like 1×{s - 1}={s - 1}, and the product shrinks.)",
                "mistakes": [(str(s - 1), "Spreading to the extremes (1 and a big number) gives the smallest product. Gather them toward the middle for the largest.")],
                "detail": "'When the sum is fixed, the product is largest when the two numbers are equal' — the same principle as a square having the largest area for a fixed perimeter (width + height fixed → the square has the largest area). Conversely, 'when the product is fixed, the sum is smallest when the two numbers are equal'. It's the 'balance is optimal' pattern found all over nature and the economy.",
            },
        )


# ── 108. 선물 교환 = 방향 있는 짝 (난5, 자료와가능성) ───────────────────────
def gen_gift_exchange():
    for n in [4, 5, 6, 8]:
        ans = n * (n - 1)
        add(
            "gift", "DATA_POSSIBILITY", 5, ["경우의 수", "순서 있는 짝"],
            f"{n}명이 서로에게 선물을 하나씩 보내요(자기 자신에겐 안 보내요). 오가는 선물은 모두 몇 개일까요?",
            f"{ans}개", [f"{n * (n - 1) // 2}개", f"{n}개", f"{ans + n}개"],
            f"한 사람은 자기를 뺀 {n - 1}명에게 선물을 보내요. {n}명이 각자 {n - 1}개씩 보내니 {n}×{n - 1}={ans}개예요. 악수와 달리 '주는 것'과 '받는 것'은 방향이 달라서 두 번 세지 않고 그대로 곱해요.",
            [(f"{n * (n - 1) // 2}개", "이건 악수(한 번)가 아니라 '보내는 방향'이 있는 선물이에요 — 2로 나누지 않아요.")],
            detail=f"방향이 있으면(A→B와 B→A가 다르면) {n}×({n}−1)로 그대로, 방향이 없으면(악수처럼 A-B 한 번) ÷2 해요. '순서(방향)를 구별하나?'가 세기의 갈림길이고, 이 차이가 곧 순열과 조합의 차이예요.",
            en={
                "statement": f"{n} people each send one gift to every other person (nobody sends to themselves). How many gifts are sent in all?",
                "answer": _en_plural(ans, "gift"),
                "distractors": [_en_plural(n * (n - 1) // 2, "gift"), _en_plural(n, "gift"), _en_plural(ans + n, "gift")],
                "explanation": f"Each person sends a gift to the {n - 1} others besides themselves. With {n} people each sending {n - 1}, that's {n}×{n - 1}={ans} gifts. Unlike a handshake, 'giving' and 'receiving' have a direction, so you don't count twice — you just multiply.",
                "mistakes": [(_en_plural(n * (n - 1) // 2, "gift"), "This isn't a handshake (counted once) — a gift has a direction of sending, so you don't divide by 2.")],
                "detail": f"When there's a direction (A→B differs from B→A), it's just {n}×({n}−1); when there's no direction (like a handshake A-B once), you divide by 2. 'Does order (direction) matter?' is the fork in counting, and that difference is exactly the difference between permutations and combinations.",
            },
        )


# ── 109. 하노이탑 = 점화식 (난7, 자료와가능성) ──────────────────────────────
def gen_hanoi():
    for n in [3, 4, 5, 6]:
        ans = 2 ** n - 1
        add(
            "hanoi", "DATA_POSSIBILITY", 7, ["점화식", "최소 이동"],
            f"하노이탑: 크기가 다른 원반 {n}개가 기둥에 큰 것부터 쌓여 있어요. 한 번에 한 개씩, 큰 원반을 작은 원반 위에 놓지 않으면서 전부 옆 기둥으로 옮기려면 '최소' 몇 번 움직여야 할까요?",
            f"{ans}번", [f"{2 * n}번", f"{2 ** n}번", f"{ans - 2}번"],
            f"원반 {n}개를 옮기려면 먼저 위 {n - 1}개를 옆 기둥에 옮기고, 맨 아래 큰 원반 1개를 목표 기둥에 옮긴 뒤, 다시 {n - 1}개를 그 위에 얹어야 해요. 그래서 (n개) = 2×(n−1개) + 1. 1개는 1번, 2개는 3번, 3개는 7번… {n}개는 {ans}번이에요.",
            [(f"{2 ** n}번", "마지막에 1을 빼요 — 2를 {n}번 곱한 수에서 1 작은 값이에요.".replace("{n}", str(n)))],
            detail=f"하노이탑은 '큰 문제를 한 단계 작은 문제로 쪼개는(점화식)' 대표 예예요: T(n)=2·T(n−1)+1. 원반이 하나 늘 때마다 두 배+1로 폭발해서, 64개(전설의 탑)면 우주 나이보다 오래 걸려요. 재귀·분할정복 사고의 출발점이에요.",
        )


# ── 124. 거꾸로 연산 (난4, 수와연산) ─────────────────────────────────────────
def gen_reverse_operation():
    for mul, add_n, result in [(3, 5, 26), (4, 2, 30), (2, 7, 19), (5, 3, 43)]:
        start = (result - add_n) // mul
        assert start * mul + add_n == result and start > 1
        add(
            "reverseop", "NUMBER_OPERATION", 4, ["거꾸로 풀기", "역연산"],
            f"어떤 수에 {mul}을 곱하고 {add_n}을 더했더니 {result}가 됐어요. 처음 수는 얼마일까요?",
            str(start), [str(result - add_n), str(start + 2), str(start - 1)],
            f"거꾸로 되짚어요. 마지막에 {add_n}을 더했으니 먼저 {add_n}을 빼면 {result}−{add_n}={result - add_n}. 그 전에 {mul}을 곱했으니 {mul}로 나누면 {result - add_n}÷{mul}={start}이에요. (검산: {start}×{mul}+{add_n}={result}.)",
            [(str(result - add_n), "빼기까지만 하고 멈췄어요 — 곱한 것도 거꾸로 나눠야 해요.")],
            detail=f"'거꾸로' 풀 땐 연산 순서를 뒤집고 반대 연산을 써요: 더하기↔빼기, 곱하기↔나누기. 마지막 연산부터 반대로 풀면 처음 수가 나와요. 이건 방정식({mul}×□+{add_n}={result})을 푸는 것과 똑같아요.",
            en={
                "statement": f"A number is multiplied by {mul} and then {add_n} is added, giving {result}. What was the starting number?",
                "answer": str(start),
                "distractors": [str(result - add_n), str(start + 2), str(start - 1)],
                "explanation": f"Work backwards. Since {add_n} was added last, subtract {add_n} first: {result}−{add_n}={result - add_n}. Since {mul} was multiplied before that, divide by {mul}: {result - add_n}÷{mul}={start}. (Check: {start}×{mul}+{add_n}={result}.)",
                "mistakes": [(str(result - add_n), "You stopped after just subtracting — you also have to undo the multiplication by dividing.")],
                "detail": f"To solve 'backwards', reverse the order of operations and use the opposite operation: add↔subtract, multiply↔divide. Undo from the last operation first and you get the starting number. This is exactly the same as solving the equation ({mul}×□+{add_n}={result}).",
            },
        )


# ── 125. 닮음 넓이비 (난7, 도형과측정) ──────────────────────────────────────
def gen_similar_area_ratio():
    for r1, r2, area1 in [(2, 3, 8), (1, 2, 5), (3, 4, 18), (2, 5, 12)]:
        assert (area1 * r2 * r2) % (r1 * r1) == 0
        area2 = area1 * r2 * r2 // (r1 * r1)
        add(
            "simarea", "SHAPE_MEASUREMENT", 7, ["닮음", "넓이비"],
            f"두 도형이 서로 닮았고 닮음비(대응 변의 길이 비)가 {r1}:{r2}예요. 작은 도형의 넓이가 {area1}㎠일 때, 큰 도형의 넓이는 몇 ㎠일까요?",
            f"{area2}㎠", [f"{area1 * r2 // r1}㎠", f"{area1 * (r2 - r1)}㎠", f"{area2 + area1}㎠"],
            f"길이가 {r1}:{r2}로 닮으면 넓이는 그 '제곱'인 {r1}²:{r2}² = {r1 * r1}:{r2 * r2}로 커져요(가로도 세로도 늘어나니까). 작은 넓이 {area1}에 {r2 * r2}/{r1 * r1}을 곱하면 {area2}㎠예요.",
            [(f"{area1 * r2 // r1}㎠", f"넓이는 길이 비({r1}:{r2}) 그대로가 아니라 '제곱' 비로 커져요.")],
            detail="닮음에서 길이가 k배면 넓이는 k²배, 부피는 k³배예요(차원마다 하나씩 곱해지니까). 지도 축척이 2배면 넓이는 4배, 인형이 3배 크면 무게(부피)는 27배. 이 '차원의 제곱·세제곱'은 실생활에서 자주 헷갈리는 부분이에요.",
        )


# ── 126. 악수 수로 사람 수 역산 (난6, 자료와가능성) ─────────────────────────
def gen_handshake_reverse():
    for n in [10, 6, 8, 12]:
        total = n * (n - 1) // 2
        add(
            "handrev", "DATA_POSSIBILITY", 6, ["역산", "경우의 수"],
            f"어떤 모임에서 사람들이 서로 한 번씩 빠짐없이 악수했더니 악수가 모두 {total}번 일어났어요. 이 모임에는 몇 명이 있었을까요?",
            f"{n}명", [f"{total // 2}명", f"{n + 2}명", f"{n - 1}명"],
            f"n명이 악수하면 n×(n−1)÷2번이에요. 거꾸로 '몇 명이면 {total}번일까?'를 찾아요. 곱해서 {total * 2}(={total}×2)가 되는 연이은 두 수(n과 n−1)를 찾으면 {n}×{n - 1}={n * (n - 1)}이니 {n}명이에요.",
            [(f"{total // 2}명", "악수 수를 2로 나눈 게 사람 수가 아니에요 — n×(n−1)÷2 꼴을 거꾸로 풀어야 해요.")],
            detail=f"'결과에서 사람 수를 역산'하는 문제예요. n×(n−1)=2×(악수 수)를 만족하는 '연이은 두 자연수'를 찾으면 돼요({total}번이면 n×(n−1)={total * 2}). 곱이 그 값이 되는 이웃한 두 수를 어림해 찾는 감각이 핵심이에요.",
            en={
                "statement": f"At a gathering everyone shook hands with each other exactly once, and there were {total} handshakes in all. How many people were at the gathering?",
                "answer": f"{n} people",
                "distractors": [f"{total // 2} people", f"{n + 2} people", f"{n - 1} people"],
                "explanation": f"With n people there are n×(n−1)÷2 handshakes. Work backwards to find 'how many people give {total}'. Look for two consecutive numbers (n and n−1) whose product is {total * 2}(={total}×2): {n}×{n - 1}={n * (n - 1)}, so {n} people.",
                "mistakes": [(f"{total // 2} people", "Halving the number of handshakes is not the number of people — you have to undo the n×(n−1)÷2 form.")],
                "detail": f"This is a problem of 'working the number of people back from the result'. Find the 'two consecutive whole numbers' with n×(n−1)=2×(handshakes) ({total} handshakes means n×(n−1)={total * 2}). The knack is estimating the two neighbouring numbers whose product hits that value.",
            },
        )


# ── 127. 나머지로 나누는 수 찾기 (난5, 수와연산) ────────────────────────────
def gen_divisor_from_remainder():
    for num, rem in [(100, 4), (58, 3), (86, 2), (75, 3)]:
        target = num - rem
        divs = [d for d in range(1, target + 1) if target % d == 0 and d > rem]
        cnt = len(divs)
        add(
            "divrem", "NUMBER_OPERATION", 5, ["나머지", "약수 추론"],
            f"{num}을 어떤 수로 나누었더니 나머지가 {rem}이었어요. 나누는 수가 될 수 있는 수는 모두 몇 가지일까요? (나누는 수는 나머지 {rem}보다 커야 해요.)",
            f"{cnt}가지", [f"{cnt + 1}가지", f"{cnt - 1}가지", f"{cnt + 2}가지"],
            f"'{num}을 나눠 {rem} 남는다'는 건 {num}−{rem}={target}이 그 수로 딱 나누어떨어진다는 뜻이에요. 그러니 나누는 수는 {target}의 약수 중 나머지 {rem}보다 큰 수들: {', '.join(map(str, divs))} — 모두 {cnt}가지예요.",
            [(f"{cnt + 1}가지", f"나누는 수는 나머지 {rem}보다 커야 해요. 조건에 맞는 약수만 세요.")],
            detail=f"'나눠서 나머지가 r'이면 (원래 수 − r)이 그 수로 나누어떨어져요 — 나누는 수는 (원래 수 − r)의 약수예요. 단 나머지는 나누는 수보다 작아야 하니 나누는 수 > r. 이 두 조건(약수 + r보다 큼)으로 거르는 게 핵심이에요.",
            en={
                "statement": f"When {num} is divided by some number, the remainder is {rem}. How many possible values are there for the divisor? (The divisor must be larger than the remainder {rem}.)",
                "answer": _en_plural(cnt, "value"),
                "distractors": [_en_plural(cnt + 1, "value"), _en_plural(cnt - 1, "value"), _en_plural(cnt + 2, "value")],
                "explanation": f"'{num} divided leaves a remainder of {rem}' means {num}−{rem}={target} is exactly divisible by that number. So the divisor is one of the divisors of {target} that is larger than the remainder {rem}: {', '.join(map(str, divs))} — that's {cnt} in all.",
                "mistakes": [(_en_plural(cnt + 1, "value"), f"The divisor must be larger than the remainder {rem}. Count only the divisors that meet the condition.")],
                "detail": "If dividing leaves remainder r, then (original number − r) is divisible by that number — so the divisor is a divisor of (original number − r). But the remainder must be smaller than the divisor, so divisor > r. Filtering by these two conditions (a divisor, and larger than r) is the key.",
            },
        )


# ── 128. 격자 대각선이 지나는 칸 = m+n−gcd (난7, 도형과측정) ─────────────────
def gen_diagonal_cells():
    for m, n in [(6, 4), (5, 3), (8, 6), (4, 2)]:
        ans = m + n - gcd(m, n)
        add(
            "diagcells", "SHAPE_MEASUREMENT", 7, ["격자", "최대공약수"],
            f"가로 {m}칸, 세로 {n}칸인 직사각형 모눈이 있어요. 한 꼭짓점에서 대각선 반대편 꼭짓점까지 곧게 선을 그으면, 이 선이 지나가는 모눈 칸은 모두 몇 칸일까요?",
            f"{ans}칸", [f"{m + n}칸", f"{m * n}칸", f"{ans - 1}칸"],
            f"대각선이 지나는 칸 수엔 공식이 있어요: 가로 + 세로 − (가로와 세로의 최대공약수) = {m}+{n}−{gcd(m, n)}={ans}칸. 최대공약수를 빼는 건, 대각선이 격자의 '점'을 지날 때 두 칸을 한 번에 건너뛰기 때문이에요.",
            [(f"{m + n}칸", f"대각선이 격자 점을 지나며 칸을 건너뛰어요 — 최대공약수({gcd(m, n)})만큼 빼야 해요.")],
            figure={"type": "GRID", "params": {"w": m, "h": n, "diag": 1}},
            detail="m×n 격자의 대각선이 지나는 칸 수 = m + n − gcd(m,n)이에요. 대각선은 세로선을 넘고 가로선을 넘으며 칸을 하나씩 늘리는데, 격자 점(두 선이 겹치는 곳)을 지날 땐 한꺼번에 넘어 한 칸만 늘어요. 그 겹치는 횟수 때문에 gcd를 빼요.",
        )


# ── 118. 소금물 섞기 = 가중평균 (난7, 변화와관계) ───────────────────────────
def gen_mixture():
    for w1, c1, w2, c2 in [(200, 10, 300, 20), (100, 20, 400, 10), (300, 10, 200, 20), (100, 8, 300, 16)]:
        salt = w1 * c1 // 100 + w2 * c2 // 100
        total = w1 + w2
        assert (salt * 100) % total == 0
        ans = salt * 100 // total
        add(
            "mixture", "CHANGE_RELATION", 7, ["농도", "섞기"],
            f"농도 {c1}%인 소금물 {w1}g과 농도 {c2}%인 소금물 {w2}g을 섞었어요. 섞은 소금물의 농도는 몇 %일까요?",
            f"{ans}%", [f"{(c1 + c2) // 2}%", f"{c1 + c2}%", f"{ans + 2}%"],
            f"섞을 때 변하지 않는 건 '소금의 양'이에요. 첫 소금물의 소금은 {w1}×{c1}÷100={w1 * c1 // 100}g, 둘째는 {w2}×{c2}÷100={w2 * c2 // 100}g. 합치면 소금 {salt}g, 전체 {total}g이니 농도 = {salt}÷{total}×100 = {ans}%예요.",
            [(f"{(c1 + c2) // 2}%", "두 농도의 평균이 아니에요 — 양이 다르면 많은 쪽으로 치우쳐요(가중평균).")],
            detail="섞기 문제의 열쇠는 '녹아 있는 양(소금·알코올)은 섞어도 총량이 그대로'라는 거예요. 각각의 양을 구해 더하고 전체로 다시 나누면 끝. 결국 농도의 '가중평균'이라 양이 많은 쪽 농도에 더 가까워져요.",
        )


# ── 119. 등차수열 n번째 항 (난4, 변화와관계) ────────────────────────────────
def gen_arithmetic_nth():
    for first, diff, n in [(3, 4, 10), (5, 3, 8), (2, 5, 12), (10, 7, 6)]:
        ans = first + diff * (n - 1)
        add(
            "arithnth", "CHANGE_RELATION", 4, ["등차수열", "n번째 항"],
            f"규칙적으로 커지는 수예요: {first}, {first + diff}, {first + 2 * diff}, {first + 3 * diff}, … 이렇게 계속될 때 {n}번째 수는 얼마일까요?",
            str(ans), [str(first + diff * n), str(ans - diff), str(first * n)],
            f"이웃한 수의 차이가 항상 {diff}인 등차수열이에요. 첫 수 {first}에서 {diff}씩 더하는데, {n}번째까지는 {diff}를 {n}−1={n - 1}번 더해요. 그래서 {first}+{diff}×{n - 1}={ans}이에요.",
            [(str(first + diff * n), f"{diff}를 {n}번이 아니라 {n}−1번 더해요(첫 수엔 안 더함).")],
            detail="등차수열의 n번째 항 = (첫 항) + (n−1)×(공차)예요. 함정은 '몇 번 더하나' — n번째면 n−1번. 하나씩 안 세고 공식으로 100번째, 1000번째도 바로 구해요. 컵 쌓기·계단·나무 심기가 다 같은 '간격' 구조예요.",
            en={
                "statement": f"A number pattern that grows regularly: {first}, {first + diff}, {first + 2 * diff}, {first + 3 * diff}, … Continuing like this, what is the {n}th number?",
                "answer": str(ans),
                "distractors": [str(first + diff * n), str(ans - diff), str(first * n)],
                "explanation": f"This is an arithmetic sequence where neighbors always differ by {diff}. Starting from the first number {first}, you add {diff} each step, and to reach the {n}th number you add {diff} {n}−1={n - 1} times. So {first}+{diff}×{n - 1}={ans}.",
                "mistakes": [(str(first + diff * n), f"Add {diff} {n}−1 times, not {n} times (nothing is added to the first number).")],
                "detail": "The nth term of an arithmetic sequence = (first term) + (n−1)×(common difference). The trap is 'how many times you add' — for the nth term, n−1 times. Instead of counting one by one, the formula gives the 100th or 1000th term at once. Stacking cups, stairs, and planting trees all share this same 'interval' structure.",
            },
        )


# ── 120. 등비수열 n번째 항 (난5, 변화와관계) ────────────────────────────────
def gen_geometric_nth():
    for first, ratio, n in [(2, 2, 6), (1, 3, 5), (3, 2, 5), (1, 2, 8)]:
        ans = first * ratio ** (n - 1)
        add(
            "geonth", "CHANGE_RELATION", 5, ["등비수열", "n번째 항"],
            f"매번 {ratio}배로 커지는 수예요: {first}, {first * ratio}, {first * ratio * ratio}, … 이렇게 계속될 때 {n}번째 수는 얼마일까요?",
            str(ans), [str(first * ratio * n), str(ans * ratio), str(ans // ratio)],
            f"이웃한 수가 {ratio}배씩 커지는 등비수열이에요. 첫 수 {first}에 {ratio}를 {n}−1={n - 1}번 곱해요. {first}×{ratio}를 {n - 1}번 = {ans}이에요.",
            [(str(ans // ratio), f"한 번 덜 곱했어요 — {n}번째는 {ratio}를 {n}−1번 곱해요.")],
            detail="등비수열의 n번째 항 = (첫 항)×(공비)^(n−1)이에요. 등차가 '일정하게 더하기'라면 등비는 '일정하게 곱하기' — 곱이라 훨씬 빨리 커져요(2,4,8,16…). 세균 번식·복리·종이접기가 다 등비예요.",
            en={
                "statement": f"Here is a sequence that grows by a factor of {ratio} each time: {first}, {first * ratio}, {first * ratio * ratio}, … If it keeps going like this, what is the {n}th number?",
                "answer": str(ans),
                "distractors": [str(first * ratio * n), str(ans * ratio), str(ans // ratio)],
                "explanation": f"This is a geometric sequence where each number is {ratio} times the one before. Start from the first number {first} and multiply by {ratio} a total of {n}−1={n - 1} times: {first}×{ratio} done {n - 1} times = {ans}.",
                "mistakes": [(str(ans // ratio), f"You multiplied one time too few — the {n}th number multiplies by {ratio} {n}−1 times.")],
                "detail": "The nth term of a geometric sequence = (first term)×(common ratio)^(n−1). If an arithmetic sequence is 'adding a fixed amount', a geometric one is 'multiplying by a fixed amount' — because it multiplies, it grows much faster (2,4,8,16…). Bacteria growth, compound interest, and paper folding are all geometric.",
            },
        )


# ── 121. 하루에 빨라지는 시계 = 누적 비례 (난6, 변화와관계) ──────────────────
def gen_clock_gain():
    for gain, days in [(3, 10), (2, 15), (5, 8), (4, 12)]:
        ans = gain * days
        add(
            "clockgain", "CHANGE_RELATION", 6, ["비례", "누적"],
            f"어떤 시계는 하루에 {gain}분씩 빨라져요. 정확한 시각에 맞춰 둔 뒤 {days}일이 지나면, 이 시계는 실제 시각보다 몇 분 빨라져 있을까요?",
            f"{ans}분", [f"{gain + days}분", f"{gain * days // 2}분", f"{ans + gain}분"],
            f"하루에 {gain}분씩 '쌓여요'. {days}일이면 {gain}×{days}={ans}분 빨라져요. 매일 같은 양이 더해지니 곱셈으로 한 번에 구해요.",
            [(f"{gain + days}분", "더하는 게 아니라, 매일 쌓이는 양이라 곱해요.")],
            detail=f"'매일 일정하게 쌓이는' 문제는 (하루치)×(날수)로 구해요 — 비례 관계죠. 반대로 '며칠 뒤 정확히 60분 빨라질까?'는 60÷{gain}로 거꾸로 구하면 돼요.",
            en={
                "statement": f"A certain clock gains {gain} minutes every day. After it is set to the exact time, how many minutes ahead of the real time is it {days} days later?",
                "answer": _en_plural(ans, "minute"),
                "distractors": [_en_plural(gain + days, "minute"), _en_plural(gain * days // 2, "minute"), _en_plural(ans + gain, "minute")],
                "explanation": f"It 'piles up' {gain} minutes a day. Over {days} days that's {gain}×{days}={ans} minutes ahead. The same amount is added each day, so you get it in one step by multiplying.",
                "mistakes": [(_en_plural(gain + days, "minute"), "You don't add — it's an amount that piles up each day, so you multiply.")],
                "detail": f"Problems where something 'piles up steadily each day' are (amount per day)×(number of days) — a proportional relationship. Going the other way, 'after how many days will it be exactly 60 minutes ahead?' is found in reverse as 60÷{gain}.",
            },
        )


# ── 122. 책 읽고 남은 쪽 (난4, 수와연산) ─────────────────────────────────────
def gen_book_reading():
    for total, perday, days in [(300, 25, 8), (240, 30, 6), (500, 40, 10), (180, 20, 7)]:
        read = perday * days
        ans = total - read
        assert ans > 0
        add(
            "bookread", "NUMBER_OPERATION", 4, ["곱셈과 뺄셈", "남은 양"],
            f"{total}쪽짜리 책을 매일 {perday}쪽씩 읽어요. {days}일 동안 읽으면 몇 쪽이 남을까요?",
            f"{ans}쪽", [f"{read}쪽", f"{total - perday}쪽", f"{ans - perday}쪽"],
            f"먼저 {days}일 동안 읽은 양을 구해요: {perday}×{days}={read}쪽. 전체 {total}쪽에서 읽은 {read}쪽을 빼면 {total}−{read}={ans}쪽이 남아요.",
            [(f"{read}쪽", "그건 '읽은' 양이에요. 전체에서 빼야 '남은' 양이 나와요.")],
            detail="'매일 같은 양 × 날수'로 읽은 양을 구하고 전체에서 빼면 남은 양이에요(곱셈 다음 뺄셈). 거꾸로 '며칠이면 다 읽을까?'는 전체 ÷ 하루치로 구하고, 딱 안 나눠떨어지면 마지막 날을 하나 더해요.",
            en={
                "statement": f"You read a {total}-page book, {perday} pages every day. After reading for {days} days, how many pages are left?",
                "answer": _en_plural(ans, "page"),
                "distractors": [_en_plural(read, "page"), _en_plural(total - perday, "page"), _en_plural(ans - perday, "page")],
                "explanation": f"First find how much you read over {days} days: {perday}×{days}={read} pages. Subtracting the {read} pages read from the total of {total} leaves {total}−{read}={ans} pages.",
                "mistakes": [(_en_plural(read, "page"), "That's the amount you 'read'. Subtract it from the total to get the amount 'left'.")],
                "detail": "Find the amount read with 'same amount each day × number of days', then subtract from the total for the amount left (multiply, then subtract). Going the other way, 'how many days to finish?' is total ÷ daily amount, and if it doesn't divide evenly, add one more day at the end.",
            },
        )


# ── 123. 기차가 사람을 지나가기 = 숨은 길이 (난5, 변화와관계) ────────────────
def gen_train_pass_person():
    for length, speed in [(120, 20), (150, 15), (200, 25), (100, 10)]:
        assert length % speed == 0
        ans = length // speed
        add(
            "trainperson", "CHANGE_RELATION", 5, ["거속시", "숨은 길이"],
            f"길이 {length}m인 기차가 초속 {speed}m로 달려요. 선로 옆에 서 있는 사람 한 명을 완전히 지나치는 데 몇 초가 걸릴까요?",
            f"{ans}초", [f"{length}초", f"{ans * 2}초", f"{ans - 1}초"],
            f"사람은 크기가 거의 없으니, 기차가 '자기 길이만큼' 지나가면 사람을 완전히 지나친 거예요. 그러니 기차는 {length}m를 가야 하고, 초속 {speed}m이니 {length}÷{speed}={ans}초 걸려요.",
            [(f"{length}초", f"{length}는 거리(m)예요. 시간은 거리÷속력이에요.")],
            detail="'기차가 무언가를 지나가는' 문제는 '실제로 이동한 거리'를 정확히 잡는 게 전부예요. 점 같은 사람은 기차 길이만큼, 다리·터널은 (기차 길이 + 다리 길이)만큼. 시간 = 거리 ÷ 속력. 무엇을 지나가느냐에 따라 '거리'만 달라져요.",
            en={
                "statement": f"A train {length}m long runs at {speed}m per second. How many seconds does it take to pass completely by one person standing beside the track?",
                "answer": f"{ans} seconds",
                "distractors": [f"{length} seconds", f"{ans * 2} seconds", f"{ans - 1} seconds"],
                "explanation": f"A person takes up almost no space, so once the train has gone by 'its own length' it has completely passed the person. The train must travel {length}m, and at {speed}m per second that takes {length}÷{speed}={ans} seconds.",
                "mistakes": [(f"{length} seconds", f"{length} is a distance (m). Time is distance ÷ speed.")],
                "detail": "In 'a train passing something' problems, everything comes down to pinning down 'the distance actually travelled'. For a point-like person it's the train's length; for a bridge or tunnel it's (train length + bridge length). Time = distance ÷ speed. Only the 'distance' changes with what is being passed.",
            },
        )


# ── 111. 중앙값 (난4, 자료와가능성) ─────────────────────────────────────────
def gen_median():
    for nums in [[2, 8, 3, 9, 4], [12, 7, 20, 5, 9], [4, 1, 10, 2, 7, 8, 6], [30, 10, 45, 15, 20]]:
        s = sorted(nums)
        n = len(s)
        ans = s[n // 2]
        add(
            "median", "DATA_POSSIBILITY", 4, ["중앙값", "정렬"],
            f"다음 수들의 '중앙값'(크기 순으로 늘어놓았을 때 한가운데 오는 수)을 구하세요: {', '.join(map(str, nums))}.",
            str(ans), [str(sum(nums) // n), str(max(nums)), str(min(nums))],
            f"중앙값은 '크기 순으로 줄 세운 뒤 한가운데'예요. 정렬하면 {', '.join(map(str, s))}. {n}개의 한가운데({n // 2 + 1}번째)는 {ans}이에요. (평균과 달리 아주 크거나 작은 값에 덜 흔들려요.)",
            [(str(sum(nums) // n), "그건 평균이에요. 중앙값은 '정렬 후 한가운데' 값이에요.")],
            detail="중앙값은 자료를 순서대로 놓고 딱 가운데 값을 고르는 거예요(개수가 짝수면 가운데 두 값의 평균). 평균은 극단값 하나에 크게 흔들리지만 중앙값은 안 흔들려서, 소득·집값처럼 한쪽으로 치우친 자료의 '대표값'으로 더 자주 써요.",
            en={
                "statement": f"Find the 'median' (the number that comes right in the middle when the numbers are lined up in order of size) of these numbers: {', '.join(map(str, nums))}.",
                "answer": str(ans),
                "distractors": [str(sum(nums) // n), str(max(nums)), str(min(nums))],
                "explanation": f"The median is 'the middle after lining everything up in order of size'. Sorted, they are {', '.join(map(str, s))}. The middle of {n} numbers (position {n // 2 + 1}) is {ans}. (Unlike the average, it is barely swayed by very large or small values.)",
                "mistakes": [(str(sum(nums) // n), "That's the average. The median is the 'middle after sorting' value.")],
                "detail": "The median is found by putting the data in order and taking the exact middle value (if the count is even, the average of the two middle values). The average is thrown off a lot by a single extreme value, but the median isn't, so it is used more often as the 'representative value' for lopsided data like incomes or house prices.",
            },
        )


# ── 112. 최대공약수 — 똑같이 나눠담기 (난5, 수와연산) ────────────────────────
def gen_gcd_bags():
    for a, b, ia, ib in [(24, 36, "사과", "귤"), (18, 30, "빨간 구슬", "파란 구슬"), (40, 60, "사탕", "초콜릿"), (16, 24, "연필", "지우개")]:
        g = gcd(a, b)
        _item_en = {"사과": "apples", "귤": "tangerines", "빨간 구슬": "red marbles", "파란 구슬": "blue marbles", "사탕": "candies", "초콜릿": "chocolates", "연필": "pencils", "지우개": "erasers"}
        ia_en, ib_en = _item_en[ia], _item_en[ib]
        add(
            "gcdbags", "NUMBER_OPERATION", 5, ["최대공약수", "똑같이 나눠담기"],
            f"{ia} {a}개와 {ib} {b}개를 여러 봉지에 '남김없이 똑같이' 나눠 담으려고 해요(모든 봉지의 구성이 같아야 해요). 최대한 '많은' 봉지에 담으려면 봉지는 몇 개가 필요할까요?",
            f"{g}개", [f"{a}개", f"{a * b // g}개", f"{g // 2}개"],
            f"봉지 수는 {a}과 {b}를 '둘 다 남김없이' 나눠야 하니 두 수의 공약수여야 해요. 가장 많은 봉지를 만들려면 그중 가장 큰 '최대공약수'를 골라요. {a}와 {b}의 최대공약수는 {g}이니 {g}개 봉지(한 봉지에 {ia} {a // g}개, {ib} {b // g}개)예요.",
            [(f"{a}개", "봉지마다 똑같이 담아야 해요 — 두 수의 공약수(최대공약수)만큼만 만들 수 있어요.")],
            detail="'여러 종류를 똑같이, 최대한 많은 묶음으로' = 최대공약수예요. 반대로 '두 주기가 처음 겹치는 순간'이나 '두 길이로 정사각형 만들기'는 최소공배수고요. 나눠담기=GCD, 함께맞추기=LCM으로 기억하면 헷갈리지 않아요.",
            en={
                "statement": f"You want to split {a} {ia_en} and {b} {ib_en} into several bags 'equally with none left over' (every bag must have the same contents). To make as 'many' bags as possible, how many bags do you need?",
                "answer": _en_plural(g, "bag"),
                "distractors": [_en_plural(a, "bag"), _en_plural(a * b // g, "bag"), _en_plural(g // 2, "bag")],
                "explanation": f"The number of bags must divide both {a} and {b} with nothing left over, so it must be a common divisor of the two numbers. To make the most bags, pick the largest one — the 'greatest common divisor'. The GCD of {a} and {b} is {g}, so {g} bags (each bag holds {a // g} {ia_en} and {b // g} {ib_en}).",
                "mistakes": [(_en_plural(a, "bag"), "Every bag must hold the same amount — you can only make as many bags as a common divisor (the greatest common divisor) of the two numbers.")],
                "detail": "'Splitting several kinds equally into as many groups as possible' = greatest common divisor. Conversely, 'the first moment two cycles line up' or 'making a square from two lengths' is the least common multiple. Remember: splitting into bags = GCD, lining up together = LCM, and you won't mix them up.",
            },
        )


# ── 113. 최소공배수 — 정사각형 만들기 (난5, 도형과측정) ─────────────────────
def gen_lcm_square():
    for w, h in [(6, 4), (8, 12), (9, 6), (10, 15)]:
        lcm = w * h // gcd(w, h)
        add(
            "lcmsquare", "SHAPE_MEASUREMENT", 5, ["최소공배수", "정사각형 만들기"],
            f"가로 {w}cm, 세로 {h}cm인 직사각형 타일을 빈틈없이 이어 붙여 '정사각형'을 만들려고 해요. 만들 수 있는 '가장 작은' 정사각형의 한 변은 몇 cm일까요?",
            f"{lcm}cm", [f"{w * h}cm", f"{w + h}cm", f"{gcd(w, h)}cm"],
            f"정사각형의 한 변은 가로 {w}로도, 세로 {h}로도 딱 나누어떨어져야 타일이 맞아요. 그런 수 중 '가장 작은' 것이 최소공배수예요. {w}와 {h}의 최소공배수는 {lcm}이니 한 변 {lcm}cm 정사각형(타일 {lcm // w}×{lcm // h}={lcm // w * (lcm // h)}장)이에요.",
            [(f"{w * h}cm", "가로×세로가 아니에요 — 두 변으로 모두 나누어떨어지는 가장 작은 수(최소공배수)예요.")],
            detail=f"'두 길이로 정사각형(둘 다의 배수)' = 최소공배수. '두 개수를 똑같이 나눠담기(둘 다의 약수)' = 최대공약수. 방향이 반대죠 — 배수로 커지느냐, 약수로 나누느냐. {w}×{h}÷최대공약수={lcm}로도 구할 수 있어요.",
            en={
                "statement": f"You want to join rectangular tiles {w}cm wide and {h}cm tall with no gaps to make a 'square'. How many cm is the side of the 'smallest' square you can make?",
                "answer": f"{lcm}cm",
                "distractors": [f"{w * h}cm", f"{w + h}cm", f"{gcd(w, h)}cm"],
                "explanation": f"The square's side must be divisible by both the width {w} and the height {h} for the tiles to fit. The 'smallest' such number is the least common multiple. The LCM of {w} and {h} is {lcm}, so it is a square with side {lcm}cm ({lcm // w}×{lcm // h}={lcm // w * (lcm // h)} tiles).",
                "mistakes": [(f"{w * h}cm", "It is not width×height — it is the smallest number divisible by both sides (the least common multiple).")],
                "detail": f"'A square from two lengths (a multiple of both)' = least common multiple. 'Splitting two counts equally into bags (a divisor of both)' = greatest common divisor. The directions are opposite — growing by multiples, or splitting by divisors. You can also find it as {w}×{h}÷(GCD)={lcm}.",
            },
        )


# ── 114. 콜라츠 추측 (난6, 자료와가능성) ────────────────────────────────────
def gen_collatz():
    for n in [6, 7, 9, 12]:
        steps = 0
        x = n
        while x != 1:
            x = x // 2 if x % 2 == 0 else 3 * x + 1
            steps += 1
        add(
            "collatz", "DATA_POSSIBILITY", 6, ["규칙 따라가기", "콜라츠"],
            f"어떤 수에 규칙을 반복해요: 짝수면 2로 나누고, 홀수면 3을 곱한 뒤 1을 더해요. {n}에서 시작하면 '1'이 될 때까지 규칙을 몇 번 적용해야 할까요?",
            f"{steps}번", [f"{steps - 1}번", f"{steps + 1}번", f"{steps + 2}번"],
            f"직접 따라가 봐요: {n}에서 규칙(짝수→÷2, 홀수→×3+1)을 적용하면 {steps}번 만에 1에 도착해요. 규칙은 단순하지만 커졌다 작아졌다 하는 길이 재미있어요.",
            [(f"{steps - 1}번", "1이 '되는' 그 단계까지 빠짐없이 세었는지 확인해요.")],
            detail="이건 '콜라츠 추측'이라는 유명한 문제예요 — 어떤 자연수로 시작해도 결국 1이 된다고 믿지만, 아직 아무도 '증명'하지 못했어요! 규칙은 초등학생도 알지만 답은 수학자도 모르는, 단순함 속 신비예요.",
            en={
                "statement": f"You repeat a rule on a number: if it's even, divide by 2; if it's odd, multiply by 3 and add 1. Starting from {n}, how many times do you apply the rule until it becomes '1'?",
                "answer": _en_plural(steps, "time"),
                "distractors": [_en_plural(steps - 1, "time"), _en_plural(steps + 1, "time"), _en_plural(steps + 2, "time")],
                "explanation": f"Just follow it through: applying the rule (even→÷2, odd→×3+1) from {n} reaches 1 in {steps} times. The rule is simple, but the path that grows and shrinks is fun to watch.",
                "mistakes": [(_en_plural(steps - 1, "time"), "Check that you counted every step right up to the one that 'becomes' 1.")],
                "detail": "This is the famous 'Collatz conjecture' — people believe that no matter which whole number you start from you eventually reach 1, but nobody has yet 'proved' it! A rule even a grade-schooler can follow, yet an answer even mathematicians don't know — mystery inside simplicity.",
            },
        )


# ── 115. 피보나치 수열 (난5, 변화와관계) ────────────────────────────────────
def gen_fibonacci():
    for pair, count in [((1, 1), 7), ((2, 3), 6), ((1, 2), 7), ((3, 5), 6)]:
        seq = list(pair)
        while len(seq) < count:
            seq.append(seq[-1] + seq[-2])
        ans = seq[-1] + seq[-2]
        add(
            "fib", "CHANGE_RELATION", 5, ["규칙", "앞 두 수의 합"],
            f"규칙을 찾아 □에 들어갈 수를 구하세요: {', '.join(map(str, seq))}, □",
            str(ans), [str(seq[-1] * 2), str(ans + 1), str(seq[-1] + 1)],
            f"이웃한 수의 관계를 봐요: {seq[0]}+{seq[1]}={seq[2]}, {seq[1]}+{seq[2]}={seq[3]}… '앞의 두 수를 더하면 다음 수'예요. 그러니 □ = {seq[-2]}+{seq[-1]} = {ans}이에요.",
            [(str(seq[-1] * 2), "마지막 수의 2배가 아니라, '앞의 두 수의 합'이에요.")],
            detail="이런 수열을 '피보나치 수열'이라 해요(1,1,2,3,5,8,13,…). 앞의 두 수를 더해 다음을 만들죠. 신기하게 해바라기 씨앗·솔방울·꽃잎 수에서 이 수들이 자주 나타나고, 이웃한 두 수의 비는 '황금비'에 점점 가까워져요.",
            en={
                "statement": f"Find the rule and work out the number that goes in the □: {', '.join(map(str, seq))}, □",
                "answer": str(ans),
                "distractors": [str(seq[-1] * 2), str(ans + 1), str(seq[-1] + 1)],
                "explanation": f"Look at how neighbouring numbers relate: {seq[0]}+{seq[1]}={seq[2]}, {seq[1]}+{seq[2]}={seq[3]}… 'add the two numbers before to get the next'. So □ = {seq[-2]}+{seq[-1]} = {ans}.",
                "mistakes": [(str(seq[-1] * 2), "It's not double the last number, but 'the sum of the two before it'.")],
                "detail": "A sequence like this is called a 'Fibonacci sequence' (1,1,2,3,5,8,13,…). Each next number is the sum of the two before. Remarkably, these numbers show up often in sunflower seeds, pinecones, and petal counts, and the ratio of neighbouring numbers gets closer and closer to the 'golden ratio'.",
            },
        )


# ── 116. 소수 고르기 (난4, 수와연산) ─────────────────────────────────────────
def gen_prime_pick():
    def sd(x):
        for i in range(2, x):
            if x % i == 0:
                return i
        return x

    for prime, others in [(17, [15, 21, 27]), (23, [25, 33, 35]), (13, [9, 21, 25]), (29, [27, 33, 39])]:
        sm = sd(others[0])
        add(
            "primepick", "NUMBER_OPERATION", 4, ["소수", "약수 판별"],
            f"다음 네 수 중에서 '소수'(1과 자기 자신으로만 나누어떨어지는 수)는 무엇일까요? {prime}, {others[0]}, {others[1]}, {others[2]}",
            str(prime), [str(others[0]), str(others[1]), str(others[2])],
            f"소수는 약수가 1과 자기 자신, 딱 둘뿐인 수예요. 나머지 수들은 다른 약수가 더 있어요(예: {others[0]}={sm}×{others[0] // sm}). {prime}은 1과 {prime} 말고는 나누어떨어지지 않으니 소수예요.",
            [(str(others[0]), "그 수는 1과 자신 말고도 약수가 있어 소수가 아니에요.")],
            detail="소수는 '더 이상 쪼갤 수 없는 수의 원자'예요 — 모든 자연수는 소수들의 곱으로 딱 한 가지로 나타나요(소인수분해). 2,3,5,7,11,13,17,…처럼 불규칙하게 나타나고 끝없이 많다는 게 오래전에 증명됐어요.",
            en={
                "statement": f"Which of these four numbers is a 'prime' (a number divisible only by 1 and itself)? {prime}, {others[0]}, {others[1]}, {others[2]}",
                "answer": str(prime),
                "distractors": [str(others[0]), str(others[1]), str(others[2])],
                "explanation": f"A prime has exactly two divisors, 1 and itself. The other numbers have more divisors (e.g. {others[0]}={sm}×{others[0] // sm}). {prime} is divisible by nothing except 1 and {prime}, so it is prime.",
                "mistakes": [(str(others[0]), "That number has divisors besides 1 and itself, so it is not prime.")],
                "detail": "Primes are 'the atoms of numbers that can't be split further' — every whole number is written as a product of primes in exactly one way (prime factorization). They appear irregularly like 2,3,5,7,11,13,17,… and it was proven long ago that there are infinitely many.",
            },
        )


# ── 117. 최대공약수 × 최소공배수 = 두 수의 곱 (난6, 수와연산) ────────────────
def gen_gcd_lcm_product():
    for g, lcm in [(4, 24), (6, 36), (5, 30), (8, 40)]:
        ans = g * lcm
        add(
            "gcdlcm", "NUMBER_OPERATION", 6, ["최대공약수", "최소공배수 관계"],
            f"두 자연수의 최대공약수가 {g}, 최소공배수가 {lcm}이에요. 이 두 수를 '곱하면' 얼마일까요?",
            str(ans), [str(g + lcm), str(lcm), str(ans // 2)],
            f"신기한 관계가 있어요: '두 수의 곱 = 최대공약수 × 최소공배수'. 그래서 두 수를 몰라도 곱은 바로 나와요: {g}×{lcm}={ans}이에요.",
            [(str(g + lcm), "더하는 게 아니라, 최대공약수와 최소공배수를 '곱해요'.")],
            detail="어떤 두 수든 '두 수의 곱 = 최대공약수 × 최소공배수'가 늘 성립해요. 최대공약수는 공통 부분, 최소공배수는 그 공통 부분에 각자 남은 부분을 곱한 것이라 둘을 곱하면 두 수의 곱이 되거든요. 한쪽을 알면 다른 쪽을 바로 구할 수 있어요(LCM=곱÷GCD).",
            en={
                "statement": f"Two whole numbers have a greatest common divisor of {g} and a least common multiple of {lcm}. What do you get if you 'multiply' these two numbers?",
                "answer": str(ans),
                "distractors": [str(g + lcm), str(lcm), str(ans // 2)],
                "explanation": f"There is a neat relationship: 'the product of two numbers = their GCD × their LCM'. So even without knowing the two numbers, the product comes right out: {g}×{lcm}={ans}.",
                "mistakes": [(str(g + lcm), "Don't add — 'multiply' the greatest common divisor and the least common multiple.")],
                "detail": "For any two numbers, 'the product of the two numbers = GCD × LCM' always holds. The GCD is the shared part, and the LCM is that shared part times each number's leftover part, so multiplying them gives the product of the two numbers. Knowing one lets you find the other right away (LCM = product ÷ GCD).",
            },
        )


# ── 110. 비스듬한 격자 도형 넓이 (난7·그림, 도형과측정) — 경시급, 도형측정×난7 빈칸 채움 ─
def gen_grid_area_hard():
    # 기울어진 정사각형들(변 벡터 (a,b) → 넓이 a²+b²). 둘러싼 정사각형 − 네 모서리 삼각형.
    for pts in [
        [(1, 0), (4, 1), (3, 4), (0, 3)],  # (3,1) → 넓이 10
        [(2, 0), (5, 2), (3, 5), (0, 3)],  # (3,2) → 넓이 13
        [(1, 0), (5, 1), (4, 5), (0, 4)],  # (4,1) → 넓이 17
        [(0, 3), (3, 0), (6, 3), (3, 6)],  # 마름모 → 넓이 18
    ]:
        assert _shoelace2(pts) % 2 == 0
        area = _shoelace2(pts) // 2
        add(
            "gridhard", "SHAPE_MEASUREMENT", 7, ["넓이", "둘러싸고 빼기"],
            "색칠한 도형의 넓이는 몇 ㎠일까요? (모눈 한 칸은 1㎠예요)",
            f"{area}㎠", [f"{area + 2}㎠", f"{area - 2}㎠", f"{area + 4}㎠"],
            f"비스듬한 도형은 '딱 둘러싼 정사각형'을 그린 뒤 바깥으로 남는 직각삼각형들을 빼면 정확해요. 둘러싼 정사각형에서 네 모서리 삼각형(각각 밑변×높이÷2)을 빼면 {area}㎠. (격자점을 잇는 도형이라 아래 심화의 '피크의 정리'로도 구할 수 있어요.)",
            [(f"{area + 2}㎠", "비스듬한 변의 칸을 대충 세면 안 돼요 — 둘러싼 정사각형에서 모서리 직각삼각형을 정확히 빼요.")],
            figure=_grid_fig(pts),
            detail="비스듬히 놓인 도형의 넓이는 '둘러싼 직사각형 − 모서리 직각삼각형들'로 정확히 구해요. 격자점을 잇는 도형이라면 '피크의 정리'가 강력해요: 넓이 = (도형 안쪽 격자점 수) + (경계 위 격자점 수)÷2 − 1. 점만 세면 넓이가 나오죠. 두 방법으로 각각 구해 답이 같은지 확인하면 실수가 없어요.",
        )


# ── 135. 합과 곱으로 두 수 찾기 (난6, 수와연산) ─────────────────────────────
def gen_sum_product_pair():
    for s, p in [(7, 12), (9, 20), (10, 21), (8, 15)]:
        disc = s * s - 4 * p
        r = int(disc ** 0.5)
        assert r * r == disc
        x = (s - r) // 2
        y = (s + r) // 2
        assert x + y == s and x * y == p and x > 0
        add(
            "sumprod", "NUMBER_OPERATION", 6, ["연립 추론", "합과 곱"],
            f"두 자연수를 더하면 {s}, 곱하면 {p}예요. 두 수 중 '더 큰' 수는 무엇일까요?",
            str(y), [str(x), str(s), str(y + 1)],
            f"합이 {s}가 되는 짝(1과 {s - 1}, 2와 {s - 2}, …)을 하나씩 곱해 보면 {x}×{y}={p}인 짝을 만나요. 그중 큰 수는 {y}예요.",
            [(str(x), "그건 두 수 중 작은 쪽이에요. '더 큰' 수를 골라요.")],
            detail="'합과 곱을 아는 두 수 찾기'는 합이 되는 짝을 차례로 곱해 보는 게 기본이에요. 사실 이 두 수는 x²−(합)x+(곱)=0의 두 해 — 중학교에서 배울 이차방정식의 씨앗이죠. 합이 정해졌을 때 곱이 클수록 두 수가 가깝다는 것도 함께 보면 재미있어요.",
            en={
                "statement": f"Two whole numbers add up to {s} and multiply to {p}. What is the 'bigger' of the two numbers?",
                "answer": str(y),
                "distractors": [str(x), str(s), str(y + 1)],
                "explanation": f"Multiply out the pairs that sum to {s} (1 and {s - 1}, 2 and {s - 2}, …) one by one, and you meet the pair {x}×{y}={p}. The bigger of those is {y}.",
                "mistakes": [(str(x), "That's the smaller of the two numbers. Pick the 'bigger' one.")],
                "detail": "'Finding two numbers from their sum and product' is basically multiplying out the pairs that make the sum, one after another. In fact these two numbers are the two solutions of x²−(sum)x+(product)=0 — the seed of the quadratic equation you will learn in middle school. It is also fun to notice that for a fixed sum, a larger product means the two numbers are closer together.",
            },
        )


# ── 136. 시간 계산 = 60진법 받아올림 (난3, 변화와관계) ──────────────────────
def gen_time_duration():
    for h, m, dh, dm in [(3, 40, 1, 50), (2, 20, 2, 55), (9, 45, 1, 30), (7, 50, 2, 20)]:
        tot = (h * 60 + m) + (dh * 60 + dm)
        eh, em = (tot // 60) % 24, tot % 60
        add(
            "timedur", "CHANGE_RELATION", 3, ["시간 계산", "60 받아올림"],
            f"어떤 일을 {h}시 {m}분에 시작해서 {dh}시간 {dm}분 동안 했어요. 끝난 시각은 몇 시 몇 분일까요?",
            f"{eh}시 {em}분", [f"{h + dh}시 {m + dm}분", f"{(eh + 1) % 24}시 {em}분", f"{eh}시 {(em + 10) % 60}분"],
            f"분끼리, 시끼리 더하되 분이 60을 넘으면 1시간으로 올려요. 분: {m}+{dm}={m + dm}분 → {(m + dm) // 60}시간 {(m + dm) % 60}분. 시: {h}+{dh}+{(m + dm) // 60}={h + dh + (m + dm) // 60}시. 그래서 {eh}시 {em}분이에요.",
            [(f"{h + dh}시 {m + dm}분", "분을 그냥 이어 붙이면 안 돼요 — 60분이 넘으면 1시간으로 받아올려요.")],
            detail="시간 계산은 '60진법'이라 분이 60을 넘으면 시로 올려요(10진법 받아올림과 같은데 넘는 기준만 60). 거꾸로 '몇 시간 몇 분 전'은 60을 빌려 내림하고요. 시계가 한 바퀴 도는 것도 같은 나머지 감각이에요.",
            en={
                "statement": f"You start a task at {h}:{m:02d} and work for {_en_plural(dh, 'hour')} {_en_plural(dm, 'minute')}. What time does it end?",
                "answer": f"{eh}:{em:02d}",
                "distractors": [f"{h + dh}:{m + dm:02d}", f"{(eh + 1) % 24}:{em:02d}", f"{eh}:{(em + 10) % 60:02d}"],
                "explanation": f"Add minutes to minutes and hours to hours, carrying 1 hour whenever the minutes pass 60. Minutes: {m}+{dm}={m + dm} → {(m + dm) // 60} hour {(m + dm) % 60} min. Hours: {h}+{dh}+{(m + dm) // 60}={h + dh + (m + dm) // 60}. So it ends at {eh}:{em:02d}.",
                "mistakes": [(f"{h + dh}:{m + dm:02d}", "Don't just stick the minutes together — carry to 1 hour once they pass 60.")],
                "detail": "Time is 'base 60', so when the minutes pass 60 you carry into hours (just like base-10 carrying, but the threshold is 60). Going backward, 'X hours Y minutes earlier' borrows 60 the same way. A clock going once around is the same remainder sense.",
            },
        )


# ── 137. 격자 속 정사각형 개수 = 제곱수의 합 (난6, 도형과측정) ───────────────
def gen_squares_in_grid():
    for k in [2, 3, 4, 5]:
        ans = k * (k + 1) * (2 * k + 1) // 6
        add(
            "gridsquares", "SHAPE_MEASUREMENT", 6, ["세기", "제곱수 합"],
            f"{k}×{k} 크기의 모눈종이(작은 정사각형 {k * k}개)가 있어요. 이 안에서 찾을 수 있는 크기가 다른 모든 '정사각형'(1×1, 2×2, …)은 모두 몇 개일까요?",
            f"{ans}개", [f"{k * k}개", f"{ans + 1}개", f"{k * k * k}개"],
            f"크기별로 나눠 세요. 1×1은 {k}×{k}={k * k}개, 2×2는 {k - 1}×{k - 1}={(k - 1) ** 2}개… 큰 정사각형일수록 놓을 자리가 줄어요. 다 더하면 1²+2²+…+{k}²={ans}개예요.",
            [(f"{k * k}개", "1×1짜리 작은 칸만 센 거예요 — 2×2, 3×3처럼 큰 정사각형도 세요.")],
            figure={"type": "GRID", "params": {"w": k, "h": k}},
            detail="n×n 격자 속 정사각형 개수 = 1²+2²+…+n²이에요(크기 s×s는 (n−s+1)²자리). 이 '제곱수의 합'엔 n(n+1)(2n+1)÷6 공식도 있어요. 직사각형까지 세면 또 달라지죠 — '무엇을 세는가'를 정확히 하는 게 세기의 핵심이에요.",
            en={
                "statement": f"You have a {k}×{k} grid of paper ({k * k} small squares). How many 'squares' of all different sizes (1×1, 2×2, …) can you find inside it?",
                "answer": _en_plural(ans, "square"),
                "distractors": [_en_plural(k * k, "square"), _en_plural(ans + 1, "square"), _en_plural(k * k * k, "square")],
                "explanation": f"Count size by size. There are {k}×{k}={k * k} of the 1×1 squares, {k - 1}×{k - 1}={(k - 1) ** 2} of the 2×2 squares… the bigger the square, the fewer places it fits. Adding them all up: 1²+2²+…+{k}²={ans}.",
                "mistakes": [(_en_plural(k * k, "square"), "You only counted the small 1×1 cells — count the bigger squares like 2×2 and 3×3 too.")],
                "detail": "The number of squares in an n×n grid = 1²+2²+…+n² (a size s×s square has (n−s+1)² positions). This 'sum of squares' even has a formula, n(n+1)(2n+1)÷6. Counting rectangles too gives a different answer — being exact about 'what you are counting' is the heart of counting.",
            },
        )


# ── 138. 합과 차로 두 수 찾기 = 합차법 (난4, 변화와관계) ────────────────────
def gen_two_sum_diff():
    for s, diff in [(20, 4), (30, 6), (50, 10), (18, 2)]:
        big = (s + diff) // 2
        small = (s - diff) // 2
        add(
            "sumdiff", "CHANGE_RELATION", 4, ["합과 차", "합차법"],
            f"두 수의 합이 {s}, 차가 {diff}예요. 두 수 중 '큰' 수는 무엇일까요?",
            str(big), [str(small), str(s // 2), str(big + diff)],
            f"합과 차를 알 땐 '더하고 빼기'가 지름길이에요. 합({s})에 차({diff})를 더하면 큰 수의 2배가 돼요: ({s}+{diff})÷2={big}. (작은 수는 ({s}−{diff})÷2={small}.) 큰 수는 {big}이에요.",
            [(str(s // 2), "두 수가 같지 않으니 절반이 아니에요 — 합에 차를 더해 2로 나눠요.")],
            detail="합차법: 큰 수 = (합+차)÷2, 작은 수 = (합−차)÷2. 합과 차를 막대 두 개로 그리면 차만큼 삐져나온 부분을 맞춰 생각할 수 있어요. 나이·개수·거리처럼 두 미지수가 '합과 차'로 주어지면 늘 통해요.",
            en={
                "statement": f"Two numbers have a sum of {s} and a difference of {diff}. What is the 'bigger' of the two numbers?",
                "answer": str(big),
                "distractors": [str(small), str(s // 2), str(big + diff)],
                "explanation": f"When you know the sum and the difference, 'add then halve' is the shortcut. Adding the difference ({diff}) to the sum ({s}) gives twice the bigger number: ({s}+{diff})÷2={big}. (The smaller is ({s}−{diff})÷2={small}.) The bigger number is {big}.",
                "mistakes": [(str(s // 2), "The two numbers are not equal, so it is not just half — add the difference to the sum, then divide by 2.")],
                "detail": "The sum-and-difference method: bigger = (sum+difference)÷2, smaller = (sum−difference)÷2. Draw the sum and difference as two bars and you can line up the part that sticks out by the difference. Whenever two unknowns are given by their 'sum and difference' — ages, counts, distances — this always works.",
            },
        )


# ── 131. 세 수의 최대공약수 (난6, 수와연산) ─────────────────────────────────
def gen_gcd_three():
    for a, b, c in [(12, 18, 20), (24, 36, 20), (30, 45, 50), (16, 40, 28)]:
        ans = gcd(gcd(a, b), c)
        add(
            "gcd3", "NUMBER_OPERATION", 6, ["최대공약수", "세 수"],
            f"{a}, {b}, {c} 세 수의 최대공약수(세 수를 모두 나누어떨어지게 하는 가장 큰 수)는 무엇일까요?",
            str(ans), [str(gcd(a, b)), str(ans + 1), str(min(a, b, c))],
            f"세 수의 최대공약수는 '두 개씩 차례로' 구하면 돼요. 먼저 {a}와 {b}의 최대공약수는 {gcd(a, b)}. 그 결과와 {c}의 최대공약수를 구하면 {ans}이에요.",
            [(str(gcd(a, b)), f"{a}, {b}만 본 게 아니라 {c}까지 모두 나누어떨어지는 수여야 해요.")],
            detail="세 수 이상의 최대공약수는 두 개씩 짝지어 차례로 구하거나, 각 수를 소인수분해해 '공통으로 든 소수를 가장 적게 나온 만큼' 곱해 구해요. 최소공배수는 반대로 '가장 많이 나온 만큼'이고요.",
            en={
                "statement": f"What is the greatest common divisor of the three numbers {a}, {b}, {c} (the largest number that divides all three evenly)?",
                "answer": str(ans),
                "distractors": [str(gcd(a, b)), str(ans + 1), str(min(a, b, c))],
                "explanation": f"Find the GCD of three numbers 'two at a time'. First, the GCD of {a} and {b} is {gcd(a, b)}. Taking the GCD of that result and {c} gives {ans}.",
                "mistakes": [(str(gcd(a, b)), f"It has to divide {c} evenly too, not just {a} and {b}.")],
                "detail": "The GCD of three or more numbers is found by pairing them two at a time in turn, or by prime-factorizing each number and multiplying 'the common primes, each to the smallest power it appears'. The LCM is the opposite — 'to the largest power each appears'.",
            },
        )


# ── 132. 등차수열의 합 (난5, 변화와관계) ────────────────────────────────────
def gen_sum_arithmetic_series():
    for first, diff, n in [(2, 3, 10), (5, 2, 8), (1, 4, 12), (3, 5, 6)]:
        last = first + diff * (n - 1)
        ans = n * (first + last) // 2
        add(
            "arithsum", "CHANGE_RELATION", 5, ["등차수열 합", "짝지어 더하기"],
            f"등차수열 {first}, {first + diff}, {first + 2 * diff}, … 의 첫 {n}개 항을 모두 더하면 얼마일까요? (마지막 {n}번째 항은 {last}예요.)",
            str(ans), [str(n * first), str(first + last), str(ans + diff)],
            f"양 끝을 짝지어요: (첫 항 {first} + 끝 항 {last}) = {first + last}. 이런 짝이 항 {n}개에 대해 {n}÷2쌍만큼 생기니 합 = (첫+끝)×개수÷2 = ({first}+{last})×{n}÷2 = {ans}이에요.",
            [(str(first + last), "그건 첫 항과 끝 항의 합이에요 — 개수를 곱하고 2로 나눠야 전체 합이에요.")],
            detail="등차수열의 합 = (첫 항 + 끝 항) × 항의 수 ÷ 2예요. 가우스가 1~100을 순식간에 더한 방법(양 끝 짝짓기)과 똑같아요. 짝의 합이 모두 같다는 대칭이 핵심이라, 항이 홀수 개여도 '가운데 항 × 개수'로 같은 결과가 나와요.",
            en={
                "statement": f"For the arithmetic sequence {first}, {first + diff}, {first + 2 * diff}, …, what do you get if you add up the first {n} terms? (The last, {n}th term is {last}.)",
                "answer": str(ans),
                "distractors": [str(n * first), str(first + last), str(ans + diff)],
                "explanation": f"Pair the two ends: (first term {first} + last term {last}) = {first + last}. There are {n}÷2 such pairs among the {n} terms, so the sum = (first+last)×count÷2 = ({first}+{last})×{n}÷2 = {ans}.",
                "mistakes": [(str(first + last), "That's the sum of the first and last terms — multiply by the count and divide by 2 for the whole sum.")],
                "detail": "The sum of an arithmetic sequence = (first term + last term) × number of terms ÷ 2. It's the same method Gauss used to add 1 to 100 in a flash (pairing the two ends). The symmetry — every pair summing to the same value — is the key, so even with an odd number of terms 'middle term × count' gives the same result.",
            },
        )


# ── 133. 1·2·3칸 계단 = 트리보나치 (난6, 자료와가능성) ──────────────────────
def gen_tribonacci_stairs():
    for n in [5, 6, 7, 4]:
        ways = [0] * (n + 1)
        ways[0] = 1
        for i in range(1, n + 1):
            for step in (1, 2, 3):
                if i - step >= 0:
                    ways[i] += ways[i - step]
        ans = ways[n]
        add(
            "tribstairs", "DATA_POSSIBILITY", 6, ["경우 나누어 세기", "점화식"],
            f"한 번에 1칸, 2칸, 또는 3칸씩 오를 수 있는 {n}칸 계단이 있어요. 오르는 서로 다른 방법은 모두 몇 가지일까요?",
            f"{ans}가지", [f"{ans - 1}가지", f"{ans + 2}가지", f"{2 ** (n - 1)}가지"],
            f"마지막 걸음이 1칸·2칸·3칸이었는지로 나눠요. 그러면 '{n}칸 방법 = {n - 1}칸 + {n - 2}칸 + {n - 3}칸 방법'이에요(앞 세 개의 합!). 1칸 1, 2칸 2, 3칸 4부터 차례로 쌓으면 {n}칸은 {ans}가지예요.",
            [(f"{ans - 1}가지", "마지막 걸음을 1·2·3칸 세 경우로 빠짐없이 나눴는지 확인해요.")],
            detail="1·2칸이면 피보나치, 1·2·3칸이면 '앞 세 수의 합'(트리보나치)이에요. 큰 문제를 '마지막 한 걸음'으로 쪼개 작은 문제들의 합으로 만드는 점화식이 핵심. 오를 수 있는 칸 종류가 늘면 더할 항도 그만큼 늘어요.",
            en={
                "statement": f"There is a staircase of {n} steps, and you can go up 1, 2, or 3 steps at a time. How many different ways are there to climb it?",
                "answer": _en_plural(ans, "way"),
                "distractors": [_en_plural(ans - 1, "way"), _en_plural(ans + 2, "way"), _en_plural(2 ** (n - 1), "way")],
                "explanation": f"Split by whether the last move was 1, 2, or 3 steps. Then 'ways for {n} steps = ways for {n - 1} + {n - 2} + {n - 3} steps' (the sum of the previous three!). Building up from 1 step: 1, 2 steps: 2, 3 steps: 4, and so on, {n} steps gives {ans} ways.",
                "mistakes": [(_en_plural(ans - 1, "way"), "Check that you split the last move into all three cases of 1, 2, and 3 steps.")],
                "detail": "With 1·2 steps it's Fibonacci; with 1·2·3 steps it's 'the sum of the previous three' (tribonacci). The key is a recurrence that breaks a big problem into the sum of smaller ones by the 'last single move'. As the kinds of steps you can climb increase, so do the terms you add.",
            },
        )


# ── 134. 전구 문제 = 제곱수 (난7, 자료와가능성) ─────────────────────────────
def gen_toggle_lights():
    for n in [10, 25, 16, 36]:
        ans = int(n ** 0.5)
        add(
            "lights", "DATA_POSSIBILITY", 7, ["약수의 개수", "제곱수"],
            f"{n}개의 전구가 일렬로 있고 모두 꺼져 있어요. 1번 사람은 1의 배수 자리(전부), 2번 사람은 2의 배수 자리, … {n}번 사람은 {n}의 배수 자리 전구의 스위치를 눌러요(켜져 있으면 끄고, 꺼져 있으면 켜요). 모두 지나간 뒤 '켜져 있는' 전구는 몇 개일까요?",
            f"{ans}개", [f"{ans + 1}개", f"{n // 2}개", f"{ans - 1}개"],
            f"어떤 전구가 눌린 횟수 = 그 번호의 '약수의 개수'예요. 켜진 채로 남으려면 홀수 번 눌려야 하는데, 약수 개수가 홀수인 수는 '제곱수'뿐이에요(약수가 짝을 이루는데 제곱수만 √n×√n으로 짝이 없거든요). {n}까지의 제곱수는 1,4,9,…로 모두 {ans}개예요.",
            [(f"{n // 2}개", "절반이 아니에요 — 약수 개수가 홀수인 수(제곱수)만 켜져 있어요.")],
            detail=f"각 전구는 '자기 번호의 약수'인 사람들에게 눌려요. 약수는 보통 짝(12 → 1·12, 2·6, 3·4)을 이뤄 개수가 짝수인데, 제곱수만 √n이 자기 자신과 짝이라 홀수예요. 그래서 켜진 전구 = {n} 이하 제곱수 개수 = √{n}의 정수 부분 = {ans}개. 유명한 '전구 문제'랍니다.",
        )


# ── 129. 줄에서 위치로 인원 세기 (난2, 자료와가능성) ────────────────────────
def gen_position_count():
    for front, back in [(4, 3), (3, 5), (6, 2), (2, 4)]:
        ans = front + back - 1
        add(
            "position", "DATA_POSSIBILITY", 2, ["위치 사고", "간격"],
            f"아이들이 한 줄로 서 있어요. 민수는 앞에서 {front}번째이고, 동시에 뒤에서 {back}번째예요. 줄에 서 있는 아이는 모두 몇 명일까요?",
            f"{ans}명", [f"{front + back}명", f"{ans - 1}명", f"{front + back + 1}명"],
            f"민수를 두 번 세지 않게 조심해요. 앞에서 {front}번째면 민수 앞에 {front - 1}명, 뒤에서 {back}번째면 민수 뒤에 {back - 1}명. 앞({front - 1}) + 민수(1) + 뒤({back - 1}) = {ans}명이에요. (또는 {front}+{back}−1={ans}, 겹치는 민수를 한 번 빼요.)",
            [(f"{front + back}명", f"{front}+{back}로 세면 민수를 두 번 센 거예요 — 한 번 빼야 해요.")],
            detail="'앞에서 몇째 + 뒤에서 몇째'로 전체를 셀 땐 그 사람을 양쪽에서 한 번씩, 두 번 세게 돼요. 그래서 −1을 해요. 나무 심기·자르기처럼 '겹치거나 사이를 세는' 문제의 한 갈래예요. 동그라미를 그려 보면 확실해져요.",
            en={
                "statement": f"Children stand in a line. One child is {front}th from the front and, at the same time, {back}th from the "
                             f"back. How many children are in the line?",
                "answer": f"{ans} children",
                "distractors": [f"{front + back} children", f"{ans - 1} children", f"{front + back + 1} children"],
                "explanation": f"Be careful not to count that child twice. {front}th from the front means {front - 1} in front; {back}th from "
                               f"the back means {back - 1} behind. Front({front - 1}) + the child(1) + behind({back - 1}) = {ans}. "
                               f"(Or {front}+{back}−1={ans}, subtracting the doubly-counted child once.)",
                "mistakes": [(f"{front + back} children", f"Counting {front}+{back} counts that child twice — subtract one.")],
                "detail": "When you total using 'Nth from the front + Mth from the back', that person gets counted once from each side — "
                          "twice. So subtract 1. It’s a cousin of tree-planting and cutting problems ('overlaps or gaps'). Drawing dots makes it clear.",
            },
        )


# ── 130. 거꾸로 생각하기 — 빠진 더하는 수 (난1, 수와연산) ────────────────────
def gen_missing_addend():
    for a, total in [(7, 15), (8, 20), (6, 13), (9, 16)]:
        ans = total - a
        add(
            "addend", "NUMBER_OPERATION", 1, ["거꾸로 생각하기", "가르기"],
            f"어떤 수에 {a}을 더했더니 {total}이 됐어요. 처음 수는 얼마일까요?",
            str(ans), [str(total), str(total + a), str(ans - 1)],
            f"거꾸로 생각해요. {a}을 더해서 {total}이 됐으니 {total}에서 {a}을 도로 빼면 처음 수가 나와요: {total}−{a}={ans}이에요. (검산: {ans}+{a}={total}.)",
            [(str(total), f"그건 더한 뒤의 수예요. {a}을 도로 빼야 처음 수예요.")],
            detail=f"'□ + {a} = {total}'에서 □를 찾는 건 더하기를 거꾸로(빼기로) 되짚는 거예요. 더하기↔빼기는 서로 반대라, 한쪽을 알면 다른 쪽으로 되돌릴 수 있어요. 이 '거꾸로 생각하기'가 나중에 방정식의 바탕이 돼요.",
            en={
                "statement": f"Some number plus {a} makes {total}. What was the starting number?",
                "answer": str(ans),
                "distractors": [str(total), str(total + a), str(ans - 1)],
                "explanation": f"Think backwards. Adding {a} gave {total}, so subtract {a} back from {total} to get the start: "
                               f"{total} − {a} = {ans}. (Check: {ans} + {a} = {total}.)",
                "mistakes": [(str(total), f"That’s the number after adding. Subtract {a} back to get the starting number.")],
                "detail": f"Finding □ in '□ + {a} = {total}' means undoing the addition with subtraction. Adding and subtracting are "
                          "opposites, so knowing one lets you reverse the other. This 'think backwards' idea is the foundation of equations later.",
            },
        )


# ── v3 확충 — 입문(난1~2) 사고력 바닥 보강: 깔때기 입구가 가장 얇아 여기부터 ──────────
def gen_transitivity():
    # 이행성(A>B>C>D) 순서 추론 — 계산 없이 '이어서 비교'하는 논리. 실제 지식 지름길 없게 이름/중립 상황.
    scenes = [
        ("달리기 시합", "빨랐어요", "가장 느린", ["지호", "민수", "서연", "하은"], "a race", "was faster", "is the slowest"),
        ("줄넘기 대회", "많이 넘었어요", "가장 적게 넘은", ["윤아", "도윤", "시우", "예은"], "a jump-rope contest", "jumped more", "jumped the fewest"),
        ("멀리뛰기", "멀리 뛰었어요", "가장 가까이 뛴", ["준우", "하린", "은우", "다인"], "the long jump", "jumped farther", "jumped the shortest"),
        ("블록 높이 쌓기", "높이 쌓았어요", "가장 낮게 쌓은", ["소율", "건우", "나윤", "시윤"], "a block-stacking game", "stacked higher", "stacked the lowest"),
    ]
    for ctx, verb, ask, names, en_ctx, en_comp, en_super in scenes:
        a, b, c, d = names
        ea, eb, ec, ed = "A", "B", "C", "D"
        add(
            "trans", "CHANGE_RELATION", 1, ["순서 추론", "이행성"],
            f"{ctx}에서 {a}{_iga(a)} {b}보다, {b}{_iga(b)} {c}보다, {c}{_iga(c)} {d}보다 {verb}. {ask} 사람은 누구일까요?",
            d, [a, b, c],
            f"이어서 순서를 세우면 {a} → {b} → {c} → {d} 예요. 맨 끝인 {d}{_iga(d)} {ask.replace('가장 ', '')} 사람이라 답은 {d}{_copula(d)}.",
            [(a, f"{a}{_eun(a)} 제일 잘한 쪽이라 정반대예요.")],
            detail="'A가 B보다, B가 C보다 ~' 처럼 이어지는 비교는 한 줄로 순서를 세우면 한눈에 보여요(A→B→C→D). 이렇게 이어서 비교하는 생각(이행성)은 키 재기·시합 등수·수의 대소 비교에서 계속 쓰여요.",
            en={
                "statement": f"In {en_ctx}, {ea} {en_comp} than {eb}, {eb} {en_comp} than {ec}, and {ec} {en_comp} than {ed}. Who {en_super}?",
                "answer": ed,
                "distractors": [ea, eb, ec],
                "explanation": f"Line them up in order: {ea} → {eb} → {ec} → {ed}. The one at the very end, {ed}, is the one who {en_super}.",
                "mistakes": [(ea, f"{ea} is the best one — the exact opposite.")],
                "detail": "A chain of comparisons like 'A beats B, B beats C…' becomes clear when you line everyone up in one order "
                          "(A→B→C→D). This chained comparison (transitivity) comes up in heights, rankings, and comparing numbers.",
            },
        )


def gen_repeating_pattern():
    # 반복 무늬의 n번째 — 주기와 나머지 개념(계산 아님, 규칙 발견).
    palette = ["빨강", "파랑", "노랑", "초록"]
    cases = [(["빨강", "파랑"], 10), (["빨강", "파랑", "노랑"], 11), (["노랑", "초록", "빨강"], 14), (["파랑", "노랑"], 15)]
    for pat, n in cases:
        p = len(pat)
        r = n % p  # 묶음(주기) 안에서 몇 번째인지 — 나머지 0이면 맨 끝
        position = r if r != 0 else p
        color = pat[position - 1]
        others = [c for c in palette if c != color][:3]
        where = f"나머지는 0, 곧 한 묶음의 맨 끝({p}번째)" if r == 0 else f"나머지는 {r}, 곧 한 묶음의 {r}번째"
        add(
            "pattern", "CHANGE_RELATION", 1, ["반복 규칙", "주기와 나머지"],
            f"구슬을 {' - '.join(pat)} 순서로 반복해서 놓아요: {' - '.join(pat + pat)} - … 이렇게요. {n}번째 구슬의 색은 무엇일까요?",
            color, others,
            f"색 {p}개가 반복되니 {p}개마다 처음으로 돌아와요. {n}{_eul(str(n))} {p}{_euro(str(p))} 나누면 {where}인 {color}{_copula(color)}.",
            [(pat[-1], "무늬의 마지막 색이 아니라, 몇 번째 자리(나머지)인지를 따져야 해요.")],
            detail="반복 무늬는 '한 묶음(주기)'이 몇 개인지부터 세요. 그 수로 나눈 '나머지'가 묶음 안에서 몇 번째인지 알려줘요(나머지가 0이면 묶음의 맨 끝). 주기 규칙은 요일·시계·달력에서도 똑같이 쓰여요.",
            en=(lambda cmap: {
                "statement": f"Beads are placed repeating in the order {' - '.join(cmap[c] for c in pat)}: "
                             f"{' - '.join(cmap[c] for c in pat + pat)} - … . What color is the {n}th bead?",
                "answer": cmap[color],
                "distractors": [cmap[c] for c in others],
                "explanation": f"The {p} colors repeat, so they return to the start every {p}. Dividing {n} by {p}, "
                               + (f"the remainder is 0 — the last in a group (position {p})" if r == 0
                                  else f"the remainder is {r} — position {r} in a group")
                               + f", which is {cmap[color]}.",
                "mistakes": [(cmap[pat[-1]], "It’s not the last color of the pattern — work out which position (the remainder) it is.")],
                "detail": "For a repeating pattern, first count how many are in one group (the period). The remainder after dividing by "
                          "that number tells you the position within the group (remainder 0 means the last). The same idea drives weekdays, clocks, and calendars.",
            })({"빨강": "red", "파랑": "blue", "노랑": "yellow", "초록": "green"}),
        )


def gen_io_rule():
    # 입력→출력 대응 규칙 찾기(×▲+●). 여러 쌍에서 공통 규칙을 발견하는 사고력.
    cases = [(2, 1, [1, 2, 3], 5), (3, 1, [1, 2, 3], 4), (2, 2, [1, 2, 3], 5), (1, 5, [2, 3, 4], 6)]
    for a, b, inputs, q in cases:
        pairs = ", ".join(f"{x} → {a * x + b}" for x in inputs)
        ans = a * q + b
        rule = f"×{a}" + (f"＋{b}" if b else "")
        add(
            "iorule", "CHANGE_RELATION", 2, ["대응 규칙", "규칙 찾기"],
            f"마법 상자에 수를 넣으면 정해진 규칙으로 바뀌어 나와요. {pairs} 처럼요. 그럼 {q}{_eul(str(q))} 넣으면 무엇이 나올까요?",
            str(ans), [str(ans + 1), str(ans - 1), str(a * q if b else ans + a)],
            f"넣은 수와 나온 수를 비교하면 규칙은 (넣은 수){rule} 예요. 세 쌍 모두 맞아요. 그러니 {q}{rule.replace('×', '×').replace('＋', '＋')} = {ans}{_copula(ans)}.",
            [(str(a * q) if b else str(ans + a), "곱하기만 하고 더하는 걸 빼먹었어요." if b else "규칙을 다시 확인해요.")],
            detail="입력→출력 표에서 규칙을 찾을 땐 ①차이가 일정한가(더하기) ②몇 배인가(곱하기) ③곱하고 더했나(×▲＋●) 순서로 확인해요. 여러 쌍에서 '모두' 맞는 규칙이 진짜 규칙이에요 — 한 쌍만 보고 정하면 틀리기 쉬워요.",
            en=(lambda er: {
                "statement": f"A magic box changes a number by a fixed rule, like {pairs}. So if you put in {q}, what comes out?",
                "answer": str(ans),
                "distractors": [str(ans + 1), str(ans - 1), str(a * q if b else ans + a)],
                "explanation": f"Comparing inputs and outputs, the rule is (input){er}. All three pairs fit, so {q}{er} = {ans}.",
                "mistakes": [(str(a * q) if b else str(ans + a), "You multiplied but forgot to add." if b else "Check the rule again.")],
                "detail": "To find a rule in an input→output table, check in order: ① is the difference constant (add)? ② how many times "
                          "bigger (multiply)? ③ multiply then add (×▲+●)? The real rule fits every pair — deciding from just one is risky.",
            })(f"×{a}" + (f"+{b}" if b else "")),
        )


def gen_midpoint():
    # 수직선 한가운데 수 = 두 수의 평균 감각(계산보다 '가운데' 개념).
    for a, b in [(4, 12), (6, 14), (10, 20), (8, 18)]:
        mid = (a + b) // 2
        assert (a + b) % 2 == 0, "가운데 수가 정수여야"
        add(
            "midpt", "NUMBER_OPERATION", 2, ["수직선", "중간값"],
            f"수직선 위에 {a}{_gwa(str(a))} {b}{_iga(str(b))} 있어요. 두 수의 정확히 한가운데에 있는 수는 얼마일까요?",
            str(mid), [str(mid + 1), str(mid - 1), str(a + b)],
            f"한가운데 수는 {a}에서 {b}까지 거리({b - a})의 절반만큼 떨어져 있어요. {a}에서 {(b - a) // 2}만큼 가면 {mid}, {b}에서 {(b - a) // 2}만큼 와도 {mid} — 양쪽에서 똑같이 {(b - a) // 2}칸이라 답은 {mid}{_copula(mid)}.",
            [(str(a + b), "두 수를 더하기만 하면 안 돼요. 한가운데는 더한 뒤 절반이에요.")],
            detail="두 수의 '한가운데'는 두 수의 합을 반으로 나눈 값(평균)이에요. 수직선에서 양 끝에서 같은 칸만큼 떨어진 자리를 찾는 것과 같아요. 이 '가운데=평균' 감각은 나중에 평균·대칭·중점에서 계속 쓰여요.",
            en={
                "statement": f"On a number line, {a} and {b} are marked. What number lies exactly halfway between them?",
                "answer": str(mid),
                "distractors": [str(mid + 1), str(mid - 1), str(a + b)],
                "explanation": f"The halfway number sits half of the distance ({b - a}) from each end. Going {(b - a) // 2} up from {a} gives "
                               f"{mid}, and coming {(b - a) // 2} down from {b} also gives {mid} — same steps from both sides, so {mid}.",
                "mistakes": [(str(a + b), "Don’t just add the two numbers. The middle is the sum, then halved.")],
                "detail": "The 'halfway' point of two numbers is their sum halved (their average). On a number line it’s the spot equally far "
                          "from both ends. This 'middle = average' sense returns in averages, symmetry, and midpoints.",
            },
        )


def gen_consecutive_middle():
    # 연속하는 세 수의 합 = 가운데 수 × 3 (양옆 −1·+1 상쇄). 계산이 아닌 구조 통찰.
    for mid in [7, 10, 6, 12]:
        total = 3 * mid
        add(
            "consecmid", "NUMBER_OPERATION", 2, ["연속수", "합과 가운데"],
            f"연속하는 세 수를 더했더니 {total}{_iga(str(total))} 됐어요. 이 세 수의 가운데 수는 얼마일까요?",
            str(mid), [str(mid + 1), str(mid - 1), str(total // 2)],
            f"연속하는 세 수는 (가운데−1), 가운데, (가운데＋1)이라 더하면 −1과 ＋1이 없어져 '가운데 수의 3배'가 돼요. 그래서 가운데 수는 {total}÷3＝{mid}{_copula(mid)}.",
            [(str(total // 2), "둘이 아니라 셋으로 나눠요. 세 수의 합이니까요.")],
            detail="연속하는 세 수의 합은 언제나 '가운데 수 × 3'이에요(양옆의 −1, ＋1이 서로 상쇄되니까). 그래서 합을 3으로 나누면 바로 가운데 수가 나와요. 연속수의 이 성질은 합·평균 문제에서 계속 쓰여요.",
            en={
                "statement": f"Three consecutive numbers add up to {total}. What is the middle one?",
                "answer": str(mid),
                "distractors": [str(mid + 1), str(mid - 1), str(total // 2)],
                "explanation": f"Three consecutive numbers are (middle−1), middle, (middle+1). Adding them, the −1 and +1 cancel, giving "
                               f"3× the middle. So the middle is {total}÷3 = {mid}.",
                "mistakes": [(str(total // 2), "Divide by 3, not 2 — it’s the sum of three numbers.")],
                "detail": "The sum of three consecutive numbers is always 'the middle × 3' (the −1 and +1 on the sides cancel). So dividing "
                          "the sum by 3 gives the middle directly. This property of consecutive numbers keeps helping in sum and average problems.",
            },
        )


def gen_multiple_condition():
    # 조건(어떤 수보다 작은)을 만족하는 최대 배수 — 배수 감각 + 조건 따지기.
    for limit, k in [(30, 5), (40, 7), (25, 4), (50, 8)]:
        ans = ((limit - 1) // k) * k
        add(
            "multcond", "NUMBER_OPERATION", 1, ["배수", "조건 따지기"],
            f"{limit}보다 작은 수 중에서 {k}{_euro(str(k))} 나누어떨어지는(={k}단에 나오는) 가장 큰 수는 얼마일까요?",
            str(ans), [str(ans + k), str(ans - k), str(limit)],
            f"{k}단 수를 크기 순으로 떠올려요: … {ans - k}, {ans}, {ans + k}. 이 중 {limit}보다 작은 가장 큰 수는 {ans}예요({ans + k}{_eun(str(ans + k))} {limit}보다 크거나 같아 안 돼요).",
            [(str(ans + k), f"{ans + k}{_eun(str(ans + k))} {limit}보다 작지 않아요. 조건을 넘겼어요."), (str(limit), f"{limit}{_eun(str(limit))} {k}로 나누어떨어지지 않을 수 있어요. {k}단 수여야 해요.")],
            detail=f"'○보다 작은 △의 배수 중 가장 큰 수'는 △단(배수)을 순서대로 떠올리며 조건 경계 바로 아래를 찾는 거예요. {limit}÷{k}의 몫만큼 {k}를 곱하면 한 번에 나오기도 해요. 조건(부등호)과 배수를 함께 따지는 연습이에요.",
            en={
                "statement": f"Among numbers less than {limit}, what is the largest one divisible by {k} (a multiple of {k})?",
                "answer": str(ans),
                "distractors": [str(ans + k), str(ans - k), str(limit)],
                "explanation": f"List the multiples of {k} in order: … {ans - k}, {ans}, {ans + k}. The largest one under {limit} is "
                               f"{ans} ({ans + k} is {limit} or more, so it’s out).",
                "mistakes": [(str(ans + k), f"{ans + k} is not less than {limit} — it breaks the condition."),
                             (str(limit), f"{limit} may not be divisible by {k}; it has to be a multiple of {k}.")],
                "detail": f"'The largest multiple of △ under ○' means listing △’s multiples and finding the one just below the boundary. "
                          f"Multiplying {k} by the quotient of {limit}÷{k} gives it in one step. It practices combining a condition (inequality) with multiples.",
            },
        )


def gen_choose_two():
    # 순서 무관 2개 고르기(nC2) = 순서 있게 센 뒤 ÷2. 조합의 핵심 통찰.
    for names in [["딸기", "포도", "귤"], ["빨강", "파랑", "노랑", "초록"], ["가", "나", "다", "라", "마"], ["사과", "배", "감", "밤"]]:
        n = len(names)
        ans = n * (n - 1) // 2
        add(
            "choose2", "DATA_POSSIBILITY", 1, ["조합", "순서 무관"],
            f"서로 다른 {n}가지({', '.join(names)}) 중에서 2가지를 고르려고 해요. 고르는 순서는 상관없어요({names[0]}·{names[1]} = {names[1]}·{names[0]}). 고르는 방법은 모두 몇 가지일까요?",
            f"{ans}가지", [f"{n * (n - 1)}가지", f"{ans + 1}가지", f"{ans - 1}가지"],
            f"한 개를 먼저 고르는 방법 {n}가지, 남은 것 중 하나 더 {n - 1}가지 → {n}×{n - 1}={n * (n - 1)}가지. 그런데 순서를 안 따지니 ({names[0]},{names[1]})와 ({names[1]},{names[0]})가 같아 2로 나눠요: {n * (n - 1)}÷2={ans}가지예요.",
            [(f"{n * (n - 1)}가지", "순서를 따지면 그 수지만, 순서 상관없으니 절반(÷2)이에요.")],
            detail="'순서 상관없이 2개 고르기'는 순서 있게 센 뒤(첫째×둘째) 2로 나눠요 — 같은 짝을 두 번 세지 않으려는 거예요. 이 생각은 악수·경기 수·짝짓기에서 똑같이 쓰여요.",
            en=(lambda el: {
                "statement": f"You pick 2 from {n} different things ({', '.join(el)}). Order doesn’t matter "
                             f"({el[0]}·{el[1]} = {el[1]}·{el[0]}). How many ways are there?",
                "answer": _en_plural(ans, "way"),
                "distractors": [_en_plural(n * (n - 1), "way"), _en_plural(ans + 1, "way"), _en_plural(ans - 1, "way")],
                "explanation": f"Pick the first in {n} ways and one more from the rest in {n - 1} ways → {n}×{n - 1}={n * (n - 1)}. "
                               f"But since order doesn’t matter, ({el[0]},{el[1]}) and ({el[1]},{el[0]}) are the same, so ÷2: "
                               f"{n * (n - 1)}÷2={ans}.",
                "mistakes": [(_en_plural(n * (n - 1), "way"), "That counts order; since order doesn’t matter, it’s half (÷2).")],
                "detail": "'Choosing 2 without order' means counting with order (first×second) then dividing by 2 — so you don’t count the "
                          "same pair twice. The same idea drives handshakes, number of games, and pairing.",
            })(list("ABCDE")[:n]),
        )


def gen_data_read():
    # 자료를 큰 순서로 세워 '몇 번째'를 찾기 — 1등에만 눈이 가는 걸 넘어서는 해석력.
    surveys = [
        ("좋아하는 과일", [("사과", 5), ("바나나", 3), ("포도", 7), ("귤", 2)]),
        ("좋아하는 운동", [("축구", 8), ("농구", 4), ("수영", 6), ("야구", 3)]),
        ("기르고 싶은 동물", [("강아지", 9), ("고양이", 5), ("햄스터", 2), ("금붕어", 4)]),
        ("좋아하는 색깔", [("빨강", 4), ("파랑", 7), ("노랑", 3), ("초록", 5)]),
    ]
    for topic, data in surveys:
        s = sorted(data, key=lambda x: -x[1])
        second = s[1][0]
        add(
            "dataread", "DATA_POSSIBILITY", 1, ["자료 해석", "순서 비교"],
            f"우리 반 친구들에게 {topic}{_eul(topic)} 물었어요. {', '.join(f'{k} {v}명' for k, v in data)}. 두 번째로 많이 나온 것은 무엇일까요?",
            second, [s[0][0], s[2][0], s[3][0]],
            f"많은 순서대로 줄을 세우면 {' > '.join(f'{k}({v})' for k, v in s)} 예요. 두 번째는 {second}{_copula(second)}.",
            [(s[0][0], "그건 가장 많은 것(1번째)이에요. 두 번째를 찾아야 해요.")],
            detail="자료에서 '몇 번째로 많은지'를 물으면 큰 순서대로 줄을 세우는 게 가장 확실해요. 가장 큰 것(1등)에 눈이 먼저 가지만, 순서를 정리하면 2등·3등도 헷갈리지 않아요.",
            en=(lambda lab: {
                "statement": "In our class we took a survey. The counts were "
                             + ", ".join(f"{lab[k]}: {v}" for k, v in data)
                             + ". Which one had the second most?",
                "answer": lab[second],
                "distractors": [lab[s[0][0]], lab[s[2][0]], lab[s[3][0]]],
                "explanation": "Line them up from most to least: " + " > ".join(f"{lab[k]}({v})" for k, v in s)
                               + f". The second is {lab[second]}.",
                "mistakes": [(lab[s[0][0]], "That’s the most (1st). You need the second.")],
                "detail": "When asked 'which is the Nth most', lining the data up from largest to smallest is the surest way. Your eye jumps "
                          "to the biggest (1st), but sorting keeps 2nd and 3rd from getting confused.",
            })({k: chr(65 + i) for i, (k, _) in enumerate(data)}),
        )


def gen_aliquot():
    # 진약수(자기 제외 약수)의 합 — 완전수/과잉수/부족수. 약수를 빠짐없이 찾는 사고.
    for n in [6, 28, 12, 8]:
        divs = [d for d in range(1, n) if n % d == 0]
        s = sum(divs)
        extra = f" 진약수 합이 자기 자신과 같으니 {n}{_eun(str(n))} '완전수'예요!" if s == n else ""
        add(
            "aliquot", "NUMBER_OPERATION", 7, ["약수", "완전수"],
            f"어떤 수의 '진약수'는 자기 자신을 뺀 약수예요(예: 6의 진약수는 1, 2, 3). {n}의 진약수를 모두 더하면 얼마일까요?",
            str(s), [str(s + n), str(s + 1), str(s - 1)],
            f"{n}의 진약수는 {', '.join(map(str, divs))}이고, 모두 더하면 {'＋'.join(map(str, divs))}={s}예요.{extra}",
            [(str(s + n), "약수에 자기 자신까지 더하면 안 돼요. 진약수는 자기 자신을 빼요.")],
            detail="진약수(자기 제외 약수)의 합으로 수를 나눠요: 합＝자신이면 완전수(6, 28…), 합＞자신이면 과잉수, 합＜자신이면 부족수예요. 약수를 빠짐없이 찾으려면 1부터 짝을 지어(1과 n, 2와 n÷2…) 세는 게 확실해요.",
        )


def gen_narcissistic():
    # 아름스트롱 수 — 각 자리 세제곱 합 = 자신. 자릿값과 거듭제곱을 함께 다루는 사고.
    narc = [153, 370, 371, 407]
    for i, t in enumerate(narc):
        ex = narc[(i + 1) % len(narc)]
        exd = [int(c) for c in str(ex)]
        td = [int(c) for c in str(t)]
        # 오답은 아름스트롱 수가 아니어야 한다(370·371처럼 이웃한 아름스트롱 수를 피한다).
        distractors = [str(x) for x in (t + 2, t - 2, t + 5, t - 5, t + 11) if x not in narc][:3]
        add(
            "narciss", "NUMBER_OPERATION", 7, ["자릿값", "세제곱 합"],
            f"각 자리 숫자를 세제곱해서 더하면 자기 자신이 되는 세 자리 수가 있어요. 예를 들어 {ex}＝{'＋'.join(f'{x}³' for x in exd)}＝{'＋'.join(str(x ** 3) for x in exd)}＝{ex} 처럼요. 이런 수가 몇 개 더 있는데, 다음 중 그런 수는 무엇일까요?",
            str(t), distractors,
            f"{t}의 각 자리 {', '.join(map(str, td))}을 세제곱해 더하면 {'＋'.join(str(x ** 3) for x in td)}＝{t}이라 자기 자신과 같아요. 나머지 보기는 세제곱 합이 자신과 달라요.",
            [(distractors[0], f"{distractors[0]}의 세제곱 합은 {sum(int(c) ** 3 for c in distractors[0])}(이)라 자기 자신과 달라요.")],
            detail="각 자리 숫자를 세제곱해 더한 값이 자기 자신과 같은 수를 '아름스트롱 수(수선화 수)'라고 해요. 세 자리에선 153, 370, 371, 407 넷뿐이에요. 자릿값과 거듭제곱을 함께 다루는 좋은 연습이에요.",
        )


def _pick_distractors(answer, cands):
    """정답과 다르고 서로 다른 오답 3개를 후보에서 고른다(문자열)."""
    out = []
    for c in cands:
        s = str(c)
        if c != answer and c > 0 and s not in out:
            out.append(s)
        if len(out) == 3:
            break
    return out


def gen_mod_power():
    # 거듭제곱의 나머지 = 나머지의 '주기'를 찾아 활용. 큰 지수도 규칙으로 손계산.
    for base, exp, m in [(2, 100, 7), (3, 50, 5), (7, 77, 10), (2, 64, 9)]:
        period = 1
        while pow(base, period, m) != 1:
            period += 1
        cyc = [pow(base, k, m) for k in range(1, period + 1)]
        pos = exp % period or period
        ans = cyc[pos - 1]
        add(
            "modpow", "NUMBER_OPERATION", 8, ["거듭제곱", "나머지 주기"],
            f"{base}{_eul(str(base))} {exp}번 곱한 수(즉 {base}^{exp})를 {m}{_euro(str(m))} 나눈 나머지는 얼마일까요?",
            str(ans), _pick_distractors(ans, [(ans + 1) % m, (ans + 2) % m, (ans + m - 1) % m, (ans + 3) % m]),
            f"{base}을 거듭제곱하며 {m}으로 나눈 나머지는 {', '.join(map(str, cyc))} 가 반복돼요(주기 {period}). {exp}{_eul(str(exp))} {period}로 나눈 나머지는 {exp % period}(자리) → 주기의 {pos}번째 값 {ans}예요.",
            [(str((ans + 1) % m), "대충 어림하면 틀려요. 나머지의 반복 주기를 정확히 찾아 지수를 주기로 나눠요.")],
            detail="같은 수를 거듭 곱해 나눈 '나머지'는 반드시 일정하게 반복돼요(주기). 주기 길이로 지수를 나눈 나머지가 주기 안 몇 번째인지 알려줘요(0이면 주기의 끝). 큰 지수도 이 규칙이면 손으로 구할 수 있어요.",
        )


def gen_lattice_paths():
    # 격자 최단 경로 수 = 오른쪽·위 이동을 섞는 조합.
    for w, h in [(3, 2), (2, 2), (3, 3), (4, 2)]:
        ans = comb(w + h, w)
        add(
            "lattice", "NUMBER_OPERATION", 8, ["조합", "최단 경로"],
            f"가로 {w}칸, 세로 {h}칸짜리 격자가 있어요. 왼쪽 아래 꼭짓점에서 오른쪽 위 꼭짓점까지 오른쪽 또는 위로만 갈 때, 서로 다른 최단 경로는 모두 몇 가지일까요?",
            f"{ans}가지", [f"{ans + 2}가지", f"{ans + 1}가지", f"{w * h}가지"],
            f"최단 경로는 오른쪽 {w}번, 위로 {h}번, 합쳐서 {w + h}번 움직이고 그 '순서'만 다른 거예요. {w + h}번 중 오른쪽 갈 {w}번을 고르는 조합이라 {w + h}C{w}={ans}가지예요.",
            [(f"{w * h}가지", "칸의 개수가 아니라, 이동 순서를 고르는 '조합'으로 세요.")],
            figure={"type": "GRID", "params": {"w": w, "h": h, "mark": 1}},
            detail="격자 최단 경로 수는 '오른쪽 R번·위 U번을 어떤 순서로 섞느냐'와 같아 조합 (R＋U)C(R)로 구해요. 각 경로가 R·U를 일렬로 배열한 것과 1:1 대응하기 때문이에요. 파스칼 삼각형으로 각 꼭짓점까지 경로 수를 채워 가도 돼요.",
        )


def gen_coin_weighing():
    # 가짜(무거운) 동전 찾기 최소 저울질 = 3분할 전략(3^n ≥ 개수).
    for n in [9, 27, 8, 3]:
        w, cap = 0, 1
        while cap < n:
            cap *= 3
            w += 1
        w2, cap2 = 0, 1
        while cap2 < n:
            cap2 *= 2
            w2 += 1
        add(
            "weigh", "NUMBER_OPERATION", 8, ["3분할 전략", "최악의 경우"],
            f"똑같이 생긴 동전 {n}개 중에 딱 하나만 무거워요. 양팔 저울로 무게만 비교할 수 있을 때, 무거운 동전을 반드시 찾으려면 최소 몇 번 재야 할까요?",
            f"{w}번", [f"{c}번" for c in _pick_distractors(w, [w2, w + 1, w + 2, n, n - 1])],
            f"동전을 세 무더기로 나눠 두 무더기를 저울에 올리면 기울면 그쪽, 평형이면 안 올린 쪽 — 매번 후보가 3분의 1로 줄어요. {n}개는 3을 {w}번 곱해야 넘으니(3을 {w}번 곱하면 {3 ** w}≥{n}) {w}번이면 반드시 찾아요.",
            [(f"{w2}번", "두 무더기가 아니라 '세 무더기'로 나눠요. 저울은 한 번에 세 경우를 알려줘 3분의 1로 줄어요."), (f"{n - 1}번", "하나씩 다 재지 않아도 돼요. 3분할이면 훨씬 적어요.")],
            detail="양팔 저울은 한 번에 '왼쪽 무겁다/오른쪽 무겁다/평형' 세 가지를 알려줘 후보를 3분의 1로 줄여요. 그래서 최소 횟수는 '3을 몇 번 곱해야 개수를 넘느냐'(3^횟수 ≥ 개수)예요. 정보량을 최대로 담는 분할 전략의 대표 문제예요.",
        )


def gen_diophantine():
    # 일차부정방정식 자연수해 개수 — 두 값의 관계를 만족하는 (a,b) 조합을 빠짐없이 세기. (변화와관계 난8)
    for ua, ub, total in [(300, 500, 3800), (400, 300, 4300), (200, 700, 6500), (500, 600, 7100)]:
        sols = [(a, b) for a in range(1, total // ua + 1) for b in range(1, total // ub + 1) if ua * a + ub * b == total]
        ans = len(sols)
        add(
            "diophantine", "CHANGE_RELATION", 8, ["일차부정방정식", "빠짐없이 경우 세기"],
            f"한 개 {ua}원짜리 사탕과 한 개 {ub}원짜리 초콜릿을 각각 1개 이상 사서 정확히 {total}원을 쓰려고 해요. "
            f"(사탕 수, 초콜릿 수) 조합은 모두 몇 가지일까요?",
            f"{ans}가지", [f"{c}가지" for c in _pick_distractors(ans, [ans + 1, ans + 2, ans - 1, ans + 3])],
            f"사탕을 a개, 초콜릿을 b개라 하면 {ua}×a + {ub}×b = {total}이에요. 한쪽(예: 초콜릿 수)을 1개씩 늘려 가며 "
            f"나머지가 {ua}{_euro(str(ua))} 나누어떨어지는 경우만 남기면 (a,b) = {', '.join(f'({a},{b})' for a, b in sols)} — 모두 {ans}가지예요.",
            [(f"{ans + 1}가지", "한쪽 개수를 하나씩 바꿔 가며 '딱 나누어떨어지는' 경우만 세요. 빠뜨리거나 겹치기 쉬워요."),
             (f"{ans - 1 if ans > 1 else ans + 2}가지", "양 끝(한쪽이 최소일 때)까지 포함해 빠짐없이 세었는지 확인하세요.")],
            detail="'두 종류를 정수 개수로 조합해 정해진 값을 맞춘다'는 일차부정방정식이에요. 한 변수를 1씩 움직이면 다른 변수는 계수만큼 반대로 움직여요("
            "여기선 한쪽이 늘면 다른 쪽이 규칙적으로 줄어요). 그래서 해는 일정 간격으로 띄엄띄엄 나타나고, 양 끝 사이를 빠짐없이 세면 개수를 구할 수 있어요.",
        )


def gen_painted_cube_faces():
    # 겉면을 칠한 n×n×n 정육면체를 단위정육면체로 자를 때, 정확히 두 면만 칠해진 개수 = 모서리 12개 × (n-2). (도형과측정 난8)
    for n in [4, 5, 3, 6]:
        two = 12 * (n - 2)
        three = 8               # 꼭짓점(세 면)
        one = 6 * (n - 2) ** 2  # 면 안쪽(한 면)
        add(
            "paintcube", "SHAPE_MEASUREMENT", 8, ["공간 감각", "위치로 나누어 세기"],
            f"겉면을 모두 빨갛게 칠한 {n}×{n}×{n} 정육면체를 1×1×1 작은 정육면체 {n ** 3}개로 잘랐어요. "
            f"정확히 '두 면'만 빨간 작은 정육면체는 몇 개일까요?",
            f"{two}개", [f"{c}개" for c in _pick_distractors(two, [three, (n - 2) ** 3, one, two + 12, two - 12 if two > 12 else two + 6])],
            f"작은 정육면체가 칠해진 면 수는 놓인 '위치'로 정해져요. 세 면=꼭짓점 8개, 두 면=모서리(꼭짓점 뺀 부분), 한 면=각 면 안쪽. "
            f"두 면은 모서리 12개마다 꼭짓점을 뺀 {n - 2}개씩이라 12×{n - 2}={two}개예요.",
            [(f"{three}개", "세 면 칠해진 건 꼭짓점 8개예요. '두 면'은 모서리 위(꼭짓점 제외)를 세요."),
             (f"{(n - 2) ** 3}개", "그건 아예 안 칠해진(속) 정육면체 수예요. 두 면은 모서리 위에 있어요.")],
            detail="정육면체를 자르면 작은 정육면체는 놓인 위치에 따라 칠해진 면 수가 정해져요 — 꼭짓점=세 면(8개 고정), 모서리 위=두 면, "
            "면 안쪽=한 면, 완전히 속=0면. '두 면'은 모서리 12개 각각에서 양 끝 꼭짓점을 뺀 (n−2)개씩이라 12(n−2)예요. 위치로 나누어 세는 공간 감각 문제예요.",
        )


def gen_stars_bars():
    # 같은 물건 N개를 몇 명에게 0개까지 허용해 나누는 방법 = 중복조합(별과 막대) C(N+k-1, k-1). (자료와가능성 난8)
    for total_items, kids in [(5, 3), (6, 3), (7, 3), (4, 2)]:
        ans = comb(total_items + kids - 1, kids - 1)
        wrong_no_zero = comb(total_items - 1, kids - 1) if total_items >= kids else 0  # 각자 1개 이상일 때(흔한 혼동)
        add(
            "starsbars", "DATA_POSSIBILITY", 8, ["중복조합", "같은 것 나누기"],
            f"똑같은 사탕 {total_items}개를 {kids}명의 아이에게 남김없이 나눠 줘요. 한 개도 못 받는 아이가 있어도 돼요. "
            f"나눠 주는 방법은 모두 몇 가지일까요?",
            f"{ans}가지", [f"{c}가지" for c in _pick_distractors(ans, [wrong_no_zero, ans + 2, total_items * kids, ans + 1, ans - 1])],
            f"사탕 {total_items}개(●)를 한 줄로 놓고 사이에 칸막이({kids - 1}개)를 꽂아 {kids}묶음으로 나눈다고 생각해요. "
            f"●와 칸막이 합 {total_items + kids - 1}자리 중 칸막이 {kids - 1}자리를 고르는 조합이라 "
            f"{total_items + kids - 1}C{kids - 1}={ans}가지예요.",
            [(f"{wrong_no_zero}가지", "'0개 가능'이라 각자 최소 1개 조건과 달라요. 사탕과 칸막이를 함께 배열해 세요."),
             (f"{total_items * kids}가지", "곱셈이 아니라, 사탕 사이에 칸막이를 꽂는 '조합'으로 세요.")],
            detail="같은 물건을 여러 사람에게 (0개 허용) 나누는 방법은 '별과 막대'로 세요 — 물건 N개를 점으로 늘어놓고 사람 수보다 하나 적은 칸막이를 그 사이에 꽂아 묶음으로 가르는 거예요. "
            "그래서 (물건+칸막이)자리 중 칸막이 자리를 고르는 중복조합 C(N+k−1, k−1)이 돼요. 같은 것을 나누는 경우의 수의 대표 도구예요.",
        )


def gen_league():
    # 리그전(서로 한 번씩) 경기 수 = C(n,2). 중복(A-B=B-A)을 빼는 세기. (자료와가능성 난3)
    for n in [4, 5, 6, 7]:
        ans = n * (n - 1) // 2
        add(
            "league", "DATA_POSSIBILITY", 3, ["경우의 수", "중복 빼기"],
            f"{n}개 팀이 서로 한 번씩 경기를 해요. 모두 몇 경기를 하게 될까요?",
            f"{ans}경기", [f"{c}경기" for c in _pick_distractors(ans, [n * (n - 1), n - 1, ans + n, ans - 1])],
            f"한 팀이 나머지 {n - 1}팀과 한 번씩 하니 {n}×{n - 1}={n * (n - 1)}처럼 보이지만, 'A와 B' 경기와 'B와 A' 경기는 "
            f"같은 한 경기예요. 그래서 2로 나눠 {n * (n - 1)}÷2={ans}경기예요.",
            [(f"{n * (n - 1)}경기", "같은 경기를 두 번 세었어요. A-B와 B-A는 한 경기라 2로 나눠요.")],
            detail="서로 한 번씩 맞붙는 리그전 경기 수는 팀 중 2팀을 고르는 조합 C(n,2)=n(n−1)/2예요. 각 팀이 (n−1)경기씩 하지만 "
            "한 경기를 두 팀이 함께 세므로 2로 나눠요. 짝을 '순서 없이' 고르는 세기의 기본이에요.",
            en={
                "statement": f"{n} teams each play every other team once. How many games are played in all?",
                "answer": f"{ans} games",
                "distractors": [f"{c} games" for c in _pick_distractors(ans, [n * (n - 1), n - 1, ans + n, ans - 1])],
                "explanation": f"Each team plays the other {n - 1} teams once, which looks like {n}×{n - 1}={n * (n - 1)}. But "
                               f"'A vs B' and 'B vs A' are the same single game, so divide by 2: {n * (n - 1)}÷2={ans} games.",
                "mistakes": [(f"{n * (n - 1)} games", "You counted each game twice. A-B and B-A are one game, so divide by 2.")],
                "detail": "The number of games in a round-robin where everyone plays everyone once equals the ways to choose 2 teams, "
                          "C(n,2)=n(n−1)/2. Each team plays (n−1) games, but every game is shared by two teams, so divide by 2. "
                          "This is the basis of counting unordered pairs.",
            },
        )


def gen_twodigit():
    # 서로 다른 숫자 카드로 만드는 두 자리 수 개수 = nP2 = n(n−1). (자료와가능성 난3)
    for cards in [[1, 2, 3, 4], [2, 3, 5], [1, 3, 5, 7], [4, 6, 8]]:
        n = len(cards)
        ans = n * (n - 1)
        card_str = ", ".join(map(str, cards))
        add(
            "twodigit", "DATA_POSSIBILITY", 3, ["경우의 수", "자리별로 세기"],
            f"숫자 카드 {card_str} 가 있어요. 이 중 두 장을 뽑아 두 자리 수를 만들 때, 만들 수 있는 서로 다른 두 자리 수는 모두 몇 개일까요?",
            f"{ans}개", [f"{c}개" for c in _pick_distractors(ans, [n * n, n, ans + 2, ans - 2])],
            f"십의 자리에 올 수 있는 카드가 {n}가지, 그 각각에 대해 일의 자리엔 남은 {n - 1}가지가 와요. "
            f"곱하면 {n}×{n - 1}={ans}개예요.",
            [(f"{n * n}개", "같은 카드를 십·일의 자리에 두 번 쓸 순 없어요. 일의 자리는 한 장 적은 {}가지예요.".format(n - 1))],
            detail="서로 다른 카드로 두 자리 수를 만드는 경우의 수는 순서가 있는 뽑기(순열) nP2 = n×(n−1)이에요. "
            "십의 자리를 정하면 일의 자리는 한 장이 빠져 한 가지 줄어들어요. 자리마다 경우를 곱하는 곱의 법칙 문제예요.",
            en={
                "statement": f"You have the number cards {card_str}. Picking two of them to form a two-digit number, how many "
                             f"different two-digit numbers can you make?",
                "answer": f"{ans} numbers",
                "distractors": [f"{c} numbers" for c in _pick_distractors(ans, [n * n, n, ans + 2, ans - 2])],
                "explanation": f"The tens place can be any of {n} cards, and for each of those the ones place is one of the "
                               f"remaining {n - 1} cards. Multiply: {n}×{n - 1}={ans} numbers.",
                "mistakes": [(f"{n * n} numbers", "You can't use the same card in both the tens and ones place. The ones place has "
                                                  "one fewer card: {} choices.".format(n - 1))],
                "detail": "The number of two-digit numbers from distinct cards is an ordered pick (a permutation), nP2 = n×(n−1). "
                          "Once the tens digit is set, the ones place has one fewer card. It's a multiplication-rule problem where "
                          "you multiply the choices at each place.",
            },
        )


def gen_tablediff():
    # 표(요일별 값)에서 최댓값−최솟값. 자료 읽고 비교하기. (자료와가능성 난3)
    for a, b, c, d in [(3, 5, 2, 6), (4, 7, 1, 5), (8, 3, 6, 2), (5, 9, 4, 7)]:
        vals = [a, b, c, d]
        ans = max(vals) - min(vals)
        add(
            "tablediff", "DATA_POSSIBILITY", 3, ["자료 읽기", "최댓값·최솟값"],
            f"월·화·수·목요일에 읽은 책이 각각 {a}권, {b}권, {c}권, {d}권이에요. 가장 많이 읽은 날과 가장 적게 읽은 날의 "
            f"책 수 차이는 몇 권일까요?",
            f"{ans}권", [f"{v}권" for v in _pick_distractors(ans, [max(vals), sum(vals), ans + 1, ans - 1])],
            f"가장 많이 읽은 날은 {max(vals)}권, 가장 적게 읽은 날은 {min(vals)}권이에요. 차이는 {max(vals)}−{min(vals)}={ans}권이에요.",
            [(f"{max(vals)}권", "가장 큰 값만 답하면 안 돼요. 가장 큰 값에서 가장 작은 값을 빼요."),
             (f"{sum(vals)}권", "다 더하는 게 아니라, 최댓값과 최솟값의 '차이'를 구해요.")],
            detail="여러 자료에서 '가장 많은 것과 가장 적은 것의 차이(범위)'는 최댓값에서 최솟값을 빼요. 표나 그래프를 읽고 "
            "가장 크고 작은 값을 정확히 집어내는 자료 해석의 기본이에요.",
            en={
                "statement": f"On Monday, Tuesday, Wednesday, and Thursday, the books read were {a}, {b}, {c}, and {d}. What is the "
                             f"difference between the most-read day and the least-read day?",
                "answer": f"{ans} books",
                "distractors": [f"{v} books" for v in _pick_distractors(ans, [max(vals), sum(vals), ans + 1, ans - 1])],
                "explanation": f"The most-read day is {max(vals)} books and the least-read day is {min(vals)} books. The difference is "
                               f"{max(vals)}−{min(vals)}={ans} books.",
                "mistakes": [(f"{max(vals)} books", "Don't just give the largest value. Subtract the smallest from the largest."),
                             (f"{sum(vals)} books", "Don't add them all — find the 'difference' between the largest and smallest.")],
                "detail": "The 'difference between the most and the least (the range)' is the maximum minus the minimum. Reading a table "
                          "or graph and pinpointing the largest and smallest values exactly is the basis of data interpretation.",
            },
        )


def gen_unitprice():
    # 단가 비례 — 한 개 값을 구해 개수만큼 곱하기. (변화와관계 난2)
    for cnt0, price0, cnt1 in [(3, 600, 5), (4, 800, 7), (2, 500, 6), (5, 1500, 8)]:
        unit = price0 // cnt0
        ans = unit * cnt1
        add(
            "unitprice", "CHANGE_RELATION", 2, ["비례 관계", "한 개 값 구하기"],
            f"연필 {cnt0}자루가 {price0}원이에요. 같은 연필 {cnt1}자루는 얼마일까요?",
            f"{ans}원", [f"{c}원" for c in _pick_distractors(ans, [ans + unit, ans - unit, price0 + cnt1 * unit, ans + 2 * unit])],
            f"먼저 한 자루 값을 구해요 — {price0}÷{cnt0}={unit}원. {cnt1}자루는 {unit}×{cnt1}={ans}원이에요.",
            [(f"{ans + unit}원", "자루 수를 하나 더 세었는지 확인하세요. 한 자루 값 × 자루 수예요.")],
            detail="개수가 늘면 값도 같은 비율로 느는 '비례'예요. 먼저 한 개(단위량)의 값을 구하고, 필요한 개수만큼 곱하면 돼요. "
            "'한 개 값 구하기'는 비례 문제를 푸는 가장 튼튼한 방법이에요.",
            en={
                "statement": f"{cnt0} pencils cost {price0} coins. How much do {cnt1} of the same pencils cost?",
                "answer": f"{ans} coins",
                "distractors": [f"{c} coins" for c in _pick_distractors(ans, [ans + unit, ans - unit, price0 + cnt1 * unit, ans + 2 * unit])],
                "explanation": f"First find the price of one pencil — {price0}÷{cnt0}={unit} coins. Then {cnt1} pencils cost "
                               f"{unit}×{cnt1}={ans} coins.",
                "mistakes": [(f"{ans + unit} coins", "Check you didn’t count one pencil too many. It’s (price of one) × (number of pencils).")],
                "detail": "When the count grows, the cost grows in the same ratio — that’s proportion. Find the price of one (the unit "
                          "amount) first, then multiply by how many you need. 'Find the unit price' is the sturdiest way to do proportion problems.",
            },
        )


def gen_rectdiag():
    # 직사각형 대각선 = √(가로²+세로²). 피타고라스 입문(정수 결과). (도형과측정 난4)
    for a, b in [(3, 4), (6, 8), (5, 12), (8, 15)]:
        sq = a * a + b * b
        ans = int(sq ** 0.5)
        add(
            "rectdiag", "SHAPE_MEASUREMENT", 4, ["피타고라스", "대각선"],
            f"가로 {a}cm, 세로 {b}cm인 직사각형의 대각선(맞은편 꼭짓점을 잇는 선)의 길이는 몇 cm일까요?",
            f"{ans}cm", [f"{c}cm" for c in _pick_distractors(ans, [a + b, ans + 1, ans - 1, a + b - 1])],
            f"대각선은 가로·세로를 두 변으로 하는 직각삼각형의 빗변이에요. 가로²+세로² = {a}²+{b}² = {sq}이고, "
            f"그 제곱근이 {ans}cm예요(피타고라스 정리).",
            [(f"{a + b}cm", "가로와 세로를 그냥 더하면 안 돼요. 각각 제곱해 더한 뒤 제곱근을 씌워요.")],
            detail="직각삼각형에서 빗변² = 두 변²의 합이에요(피타고라스 정리). 직사각형의 대각선은 가로·세로를 두 변으로 하는 "
            "빗변이라 √(가로²+세로²)로 구해요. 길이를 좌표·제곱으로 다루는 측정의 핵심 도구예요.",
            en={
                "statement": f"A rectangle is {a} cm wide and {b} cm tall. How long is its diagonal (the line joining opposite corners), in cm?",
                "answer": f"{ans}cm",
                "distractors": [f"{c}cm" for c in _pick_distractors(ans, [a + b, ans + 1, ans - 1, a + b - 1])],
                "explanation": f"The diagonal is the hypotenuse of a right triangle whose two legs are the width and height. width²+height² = {a}²+{b}² = {sq}, and its square root is {ans} cm (the Pythagorean theorem).",
                "mistakes": [(f"{a + b}cm", "You can't just add the width and height. Square each, add them, then take the square root.")],
                "detail": "In a right triangle, hypotenuse² = the sum of the two legs² (the Pythagorean theorem). A rectangle's diagonal is the hypotenuse whose legs are the width and height, so it is √(width²+height²). It's a core measurement tool for handling length with coordinates and squares.",
            },
        )


def gen_electpair():
    # 반장·부반장 뽑기 = 순서 있는 2명 뽑기 nP2 = n(n−1). (자료와가능성 난4)
    for n in [4, 5, 6, 8]:
        ans = n * (n - 1)
        add(
            "electpair", "DATA_POSSIBILITY", 4, ["경우의 수", "순서 있는 뽑기"],
            f"{n}명 중에서 반장 1명과 부반장 1명을 뽑아요. 한 사람이 둘 다 할 수는 없어요. 뽑는 방법은 모두 몇 가지일까요?",
            f"{ans}가지", [f"{c}가지" for c in _pick_distractors(ans, [n * n, n * (n - 1) // 2, n, ans + 2])],
            f"반장은 {n}명 중 누구나 될 수 있어 {n}가지, 부반장은 남은 {n - 1}명 중 뽑으니 {n - 1}가지예요. "
            f"곱하면 {n}×{n - 1} = {ans}가지예요.",
            [(f"{n * (n - 1) // 2}가지", "반장과 부반장은 서로 다른 자리라 순서를 구별해요. 2로 나누면 안 돼요."),
             (f"{n * n}가지", "한 사람이 두 자리를 겸할 순 없어요. 부반장은 한 명 적은 {}가지예요.".format(n - 1))],
            detail="반장·부반장처럼 뽑은 뒤 '자리(순서)가 구별되는' 선택은 순열 nP2 = n×(n−1)이에요. 두 명을 그냥 '대표'로 "
            "뽑는 조합(÷2)과 달리, 자리가 다르면 순서를 구별해 나누지 않아요.",
            en={
                "statement": f"From {n} people you pick 1 class president and 1 vice president. One person cannot hold both. How many ways are there in all?",
                "answer": _en_plural(ans, "way"),
                "distractors": [f"{c} ways" for c in _pick_distractors(ans, [n * n, n * (n - 1) // 2, n, ans + 2])],
                "explanation": f"The president can be any of the {n} people, so {n} ways; the vice president is picked from the remaining {n - 1}, so {n - 1} ways. Multiplying, {n}×{n - 1} = {ans} ways.",
                "mistakes": [(f"{n * (n - 1) // 2} ways", "The president and vice president are different posts, so order matters. Don't divide by 2."),
                             (f"{n * n} ways", "One person can't hold both posts. The vice president has one fewer — {} ways.".format(n - 1))],
                "detail": "A choice where the 'posts (order) are distinguished' after picking — like president and vice president — is a permutation nP2 = n×(n−1). Unlike a combination that just picks two 'representatives' (÷2), when the posts differ you keep the order and do not divide.",
            },
        )


def gen_foldcut():
    # 종이를 반으로 접고 구멍을 뚫으면, 펼쳤을 때 구멍 = 구멍 수 × 2^(접은 횟수). 대칭 사고. (도형과측정 난1)
    for folds, h in [(1, 1), (1, 2), (1, 3), (2, 1)]:
        layers = 2 ** folds
        ans = h * layers
        add(
            "foldcut", "SHAPE_MEASUREMENT", 1, ["대칭", "겹쳐서 세기"],
            f"색종이를 반으로 {folds}번 접은 다음, 겹친 채로 구멍을 {h}개 뚫었어요. 종이를 다시 펼치면 구멍은 모두 몇 개일까요?",
            f"{ans}개", [f"{c}개" for c in _pick_distractors(ans, [h, h + folds, ans + 1, h * folds])],
            f"반으로 {folds}번 접으면 종이가 {layers}겹으로 겹쳐요. 구멍 하나를 뚫으면 {layers}장이 한꺼번에 뚫려 "
            f"펼치면 {layers}개가 돼요. 구멍이 {h}개니까 {h}×{layers} = {ans}개예요.",
            [(f"{h}개", "접힌 채로 뚫으면 겹친 장수만큼 구멍이 생겨요. 펼치면 늘어나요."),
             (f"{h + folds}개", "접은 '횟수'를 더하는 게 아니라, 겹친 '장수'만큼 곱해요.")],
            detail="반으로 한 번 접으면 2겹, 두 번 접으면 4겹처럼 접을 때마다 겹이 2배가 돼요. 겹친 채 뚫은 구멍은 펼치면 "
            "겹친 장수만큼 늘어나요(대칭으로 생겨요). 접기와 대칭을 잇는 공간 사고의 첫걸음이에요.",
            en={
                "statement": f"You fold a sheet of paper in half {folds} time(s), then punch {h} hole(s) through the folded layers. "
                             f"When you unfold it, how many holes are there in all?",
                "answer": _en_plural(ans, "hole"),
                "distractors": [_en_plural(c, "hole") for c in _pick_distractors(ans, [h, h + folds, ans + 1, h * folds])],
                "explanation": f"Folding in half {folds} time(s) stacks the paper into {layers} layers. One punch goes through all "
                               f"{layers} at once, so it becomes {layers} holes. With {h} hole(s) punched, that’s {h}×{layers} = {ans}.",
                "mistakes": [(_en_plural(h, "hole"), "Punching through folds makes as many holes as stacked layers — they multiply when unfolded."),
                             (_en_plural(h + folds, "hole"), "Don’t add the number of folds — multiply by the number of stacked layers.")],
                "detail": "Folding in half once makes 2 layers, twice makes 4 — each fold doubles the layers. A hole punched through folds "
                          "multiplies into that many holes when unfolded (they appear symmetrically). A first step in linking folding and symmetry.",
            },
        )


def gen_knockout():
    # 토너먼트(지면 탈락) 우승까지 경기 수 = 참가자 − 1 (경기마다 한 명 탈락). (자료와가능성 난2)
    for n in [8, 4, 16, 6]:
        ans = n - 1
        add(
            "knockout", "DATA_POSSIBILITY", 2, ["거꾸로 생각하기", "탈락으로 세기"],
            f"{n}명이 토너먼트로 우승자를 가려요. 한 번 지면 바로 탈락할 때, 우승자가 정해질 때까지 모두 몇 경기를 "
            f"해야 할까요?",
            f"{ans}경기", [f"{c}경기" for c in _pick_distractors(ans, [n, n // 2, n - 2, ans + 1])],
            f"우승자 한 명만 남으려면 나머지 {ans}명이 모두 탈락해야 해요. 한 경기에 딱 한 명씩 탈락하니, "
            f"필요한 경기는 {n}−1 = {ans}경기예요.",
            [(f"{n // 2}경기", "첫 판만 센 거예요. 우승할 때까지 모든 판을 세야 해요."),
             (f"{n}경기", "탈락해야 할 사람은 우승자를 뺀 {}명이에요. 그만큼만 경기해요.".format(ans))],
            detail="'경기 수'를 직접 세는 대신 '탈락하는 사람 수'로 바꿔 생각하면 쉬워요. 우승자 1명을 뺀 나머지가 다 탈락해야 "
            "하고 경기마다 딱 한 명이 지므로, 경기 수는 언제나 (참가자−1)이에요. 거꾸로 보는 사고의 힘이에요.",
            en={
                "statement": f"{n} players compete in a knockout tournament. Once you lose, you’re out. How many games are played "
                             f"before a champion is decided?",
                "answer": _en_plural(ans, "game"),
                "distractors": [_en_plural(c, "game") for c in _pick_distractors(ans, [n, n // 2, n - 2, ans + 1])],
                "explanation": f"For one champion to remain, the other {ans} players must all be eliminated. Each game knocks out exactly "
                               f"one, so {n}−1 = {ans} games.",
                "mistakes": [(_en_plural(n // 2, "game"), "That’s only the first round. Count every game up to the win."),
                             (_en_plural(n, "game"), f"Only {ans} need to be eliminated (everyone but the champion) — that many games.")],
                "detail": "Instead of counting games directly, switch to counting who is eliminated — everyone but the one champion must be "
                          "knocked out, and each game eliminates exactly one, so it’s always (players − 1). The power of thinking in reverse.",
            },
        )


def gen_makesquare():
    # 완전제곱수로 만드는 최소 곱수 = 소인수분해에서 지수가 홀수인 소인수들의 곱. (수와연산 난9)
    for n in [72, 48, 50, 12]:
        m, res, p = n, 1, 2
        odd_primes = []
        while p * p <= m:
            e = 0
            while m % p == 0:
                m //= p
                e += 1
            if e % 2:
                res *= p
                odd_primes.append(p)
            p += 1
        if m > 1:
            res *= m
            odd_primes.append(m)
        root = int((n * res) ** 0.5)
        add(
            "makesquare", "NUMBER_OPERATION", 9, ["소인수분해", "완전제곱수"],
            f"{n}에 자연수를 곱해서 어떤 수의 제곱(완전제곱수)이 되게 하려고 해요. 곱해야 하는 가장 작은 자연수는 무엇일까요?",
            str(res), [str(c) for c in _pick_distractors(res, [res + 1, res * 2, res + 2, res + 3])],
            f"{n} = {_prime_factor_str(n)}예요. 완전제곱수는 모든 소인수의 지수가 짝수여야 해요. 지수가 홀수인 소인수 "
            f"{', '.join(map(str, odd_primes))}를 하나씩 더 곱해 짝수로 맞추면 {n}×{res} = {n * res} = {root}²이에요.",
            [(str(res + 1), "필요 이상으로 곱했어요. 지수가 홀수인 소인수만 딱 한 번씩 더 곱하면 돼요.")],
            detail="완전제곱수는 소인수분해했을 때 모든 지수가 짝수인 수예요. 그래서 지수가 홀수인 소인수마다 하나씩 더 곱해 "
            "짝수로 만들면 가장 작은 곱수가 나와요. 소인수의 지수로 제곱수를 판별하는 정수론 문제예요.",
        )


def gen_compose():
    # 함수(수 기계)를 여러 번 반복 적용. f(x)=ax+b를 d번. (변화와관계 난9)
    for a, b, x0, d in [(2, 1, 1, 3), (2, 3, 1, 3), (3, 1, 2, 3), (2, 5, 0, 3)]:
        seq = [x0]
        x = x0
        for _ in range(d):
            x = a * x + b
            seq.append(x)
        ans = x
        steps = " → ".join(str(v) for v in seq)
        add(
            "compose", "CHANGE_RELATION", 9, ["함수 반복", "규칙 적용"],
            f"어떤 기계에 수를 넣으면 '{a}배 하고 {b}{_eul(str(b))} 더한' 수가 나와요. {x0}{_eul(str(x0))} 넣어 나온 수를 "
            f"다시 넣는 식으로, 이 기계에 모두 {d}번 통과시켰어요. 마지막에 나오는 수는 얼마일까요?",
            str(ans), [str(c) for c in _pick_distractors(ans, [a * ans, ans + b, seq[-2], ans + a])],
            f"기계를 한 번 통과할 때마다 '×{a}, +{b}'예요: {steps}. {d}번 통과한 마지막 값은 {ans}예요.",
            [(str(seq[-2]), "한 번 덜 돌렸어요. 정확히 {}번 반복한 값을 구하세요.".format(d))],
            detail="같은 규칙(함수)을 반복해서 적용하면 값이 규칙적으로 바뀌어요. 한 단계씩 차근차근 계산해 나가는 게 안전하고, "
            "이런 반복은 점화식·수열의 뿌리예요.",
        )


def gen_euler():
    # 오일러 공식으로 모서리 역산: 꼭짓점−모서리+면=2 → 모서리 = 꼭짓점+면−2. (도형과측정 난9)
    for v, f in [(12, 20), (8, 6), (6, 8), (20, 12)]:
        ans = v + f - 2
        add(
            "euler", "SHAPE_MEASUREMENT", 9, ["오일러 공식", "다면체"],
            f"어떤 볼록 다면체의 꼭짓점이 {v}개, 면이 {f}개예요. 이 다면체의 모서리는 모두 몇 개일까요?",
            f"{ans}개", [f"{c}개" for c in _pick_distractors(ans, [v + f, v * f // 4, ans + 2, ans - 2])],
            f"볼록 다면체는 항상 '꼭짓점 − 모서리 + 면 = 2'(오일러 공식)를 만족해요. 모서리로 정리하면 "
            f"모서리 = 꼭짓점 + 면 − 2 = {v} + {f} − 2 = {ans}개예요.",
            [(f"{v + f}개", "−2를 빼먹었어요. 오일러 공식은 꼭짓점+면−2가 모서리예요.")],
            detail="볼록 다면체에서는 꼭짓점(V)−모서리(E)+면(F)=2가 항상 성립해요(오일러 공식). 셋 중 둘을 알면 나머지를 "
            "바로 구할 수 있어요. 공간 도형을 잇는 아름다운 규칙이에요.",
        )


def gen_atleastprob():
    # 여사건: '적어도 한 개 앞면' = 1 − '모두 뒷면'. (자료와가능성 난9)
    for n in [4, 3, 5, 2]:
        whole = 2 ** n
        ans = f"{whole - 1}/{whole}"
        add(
            "atleastprob", "DATA_POSSIBILITY", 9, ["여사건", "적어도"],
            f"공정한 동전 {n}개를 동시에 던져요. 적어도 한 개는 앞면이 나올 확률은 얼마일까요?",
            ans, [f"1/{whole}", "1/2", f"{n}/{whole}"],
            f"'적어도 한 개 앞면'의 반대는 '모두 뒷면'이에요. 모두 뒷면일 확률은 (1/2)를 {n}번 곱한 1/{whole}이고, "
            f"1에서 빼면 {whole - 1}/{whole}이에요.",
            [(f"1/{whole}", "그건 '모두 뒷면'일 확률이에요. 구하려는 건 그 여사건(1−그 값)이에요.")],
            detail="'적어도 하나'는 반대(여사건) '하나도 없음'을 구해 1에서 빼는 게 훨씬 쉬워요. 모두 뒷면 확률 (1/2)^n을 "
            "1에서 빼면 답이에요. 여사건은 '적어도' 문제의 강력한 도구예요.",
        )


def gen_sigma():
    # 진약수의 합(자기 제외). 완전수·부족수·과잉수 판별의 기초. (수와연산 난10)
    for n in [28, 12, 24, 18]:
        divisors = [d for d in range(1, n) if n % d == 0]
        ans = sum(divisors)
        div_str = " + ".join(map(str, divisors))
        note = " (자기 자신과 같아 '완전수'예요)" if ans == n else ""
        add(
            "sigma", "NUMBER_OPERATION", 10, ["약수", "진약수의 합"],
            f"{n}의 진약수(자기 자신 {n}{_eul(str(n))} 뺀 약수)를 모두 더하면 얼마일까요?",
            str(ans), [str(c) for c in _pick_distractors(ans, [ans + n, ans - 1, ans + 1, n])],
            f"{n}의 진약수는 {div_str}이에요. 모두 더하면 {ans}예요{note}.",
            [(str(ans + n), f"자기 자신 {n}{_eun(str(n))} 진약수가 아니에요(빼고 더해요).")],
            detail="자기 자신을 뺀 약수(진약수)의 합으로 수를 분류해요 — 합이 자신과 같으면 완전수(6, 28…), 작으면 부족수, "
            "크면 과잉수예요. 약수를 빠짐없이 찾아 더하는 정수론의 고전 주제예요.",
        )


def gen_recur():
    # 점화식 a_{n+1}=p·a_n+q의 특정 항. (변화와관계 난10)
    for a1, p, q, t in [(1, 2, 3, 5), (2, 2, 1, 5), (1, 3, 1, 4), (2, 3, 1, 4)]:
        seq = [a1]
        a = a1
        for _ in range(t - 1):
            a = p * a + q
            seq.append(a)
        ans = a
        steps = ", ".join(str(v) for v in seq)
        add(
            "recur", "CHANGE_RELATION", 10, ["점화식", "수열의 항"],
            f"수열의 첫째 항이 {a1}이고, 다음 항은 '앞 항의 {p}배에 {q}{_eul(str(q))} 더한' 값이에요. 이 수열의 {t}번째 항은 얼마일까요?",
            str(ans), [str(c) for c in _pick_distractors(ans, [p * ans + q, seq[-2], ans + q, ans - q])],
            f"규칙 '×{p}, +{q}'로 항을 이어 가요: {steps}. {t}번째 항은 {ans}예요.",
            [(str(seq[-2]), "한 항 덜 갔어요. {}번째 항까지 규칙을 적용하세요.".format(t)),
             (str(p * ans + q), "그건 {}번째(한 항 더 간) 값이에요.".format(t + 1))],
            detail="앞 항으로 다음 항을 정하는 규칙이 점화식이에요. 규칙을 한 항씩 적용해 원하는 항까지 이어 가면 돼요. "
            "이자·인구·알고리즘 등 '이전 상태로 다음을 정하는' 수많은 현상의 뼈대예요.",
        )


def gen_conevolume():
    # 뿔의 부피 = 밑넓이 × 높이 ÷ 3 (같은 밑면·높이 기둥의 1/3). (도형과측정 난10)
    for base, h in [(12, 5), (9, 4), (18, 7), (6, 10)]:
        ans = base * h // 3
        add(
            "conevolume", "SHAPE_MEASUREMENT", 10, ["뿔의 부피", "기둥의 3분의 1"],
            f"밑면의 넓이가 {base}cm², 높이가 {h}cm인 뿔(각뿔·원뿔)의 부피는 몇 cm³일까요?",
            f"{ans}cm³", [f"{c}cm³" for c in _pick_distractors(ans, [base * h, base * h // 2, ans + 2, ans - 2])],
            f"뿔의 부피는 밑면과 높이가 같은 기둥의 딱 3분의 1이에요. 밑넓이 × 높이 ÷ 3 = {base} × {h} ÷ 3 = {ans}cm³예요.",
            [(f"{base * h}cm³", "그건 같은 밑면·높이 '기둥'의 부피예요. 뿔은 그 3분의 1이라 ÷3 해요.")],
            detail="같은 밑넓이·높이라면 뿔의 부피는 기둥의 정확히 1/3이에요. 그래서 (밑넓이×높이)÷3으로 구해요. "
            "물을 부어 옮기면 세 번에 꽉 차는 걸로도 확인되는 입체 측정의 핵심이에요.",
        )


def gen_setpartition():
    # 서로 다른 n명을 비지 않은 두 팀으로(팀 구별 없이) 나누기 = 2^(n-1) − 1. (자료와가능성 난10)
    for n in [4, 5, 3, 6]:
        ans = 2 ** (n - 1) - 1
        whole = 2 ** n
        add(
            "setpartition", "DATA_POSSIBILITY", 10, ["집합 나누기", "여집합 중복"],
            f"서로 다른 {n}명을 비어 있지 않은 두 모둠으로 나눠요. 두 모둠을 구별하지 않을 때(A·B 이름 없음), "
            f"나누는 방법은 모두 몇 가지일까요?",
            f"{ans}가지", [f"{c}가지" for c in _pick_distractors(ans, [2 ** (n - 1), whole, ans + 1, ans - 1])],
            f"각 사람이 두 모둠 중 하나에 속하니 {whole}가지지만, 한쪽이 비는 2가지(전부 한 모둠)를 빼고, 두 모둠을 "
            f"구별하지 않아 2로 나눠요 → ({whole}−2)÷2 = {ans}가지예요.",
            [(f"{2 ** (n - 1)}가지", "한쪽이 텅 비는 경우를 아직 안 뺐어요. (전체−2)를 반으로 나눠요.")],
            detail="서로 다른 것을 두 묶음으로 가르는 수는, 각자가 두 곳 중 하나를 고르는 2^n에서 '한쪽이 빈' 2가지를 빼고 "
            "묶음의 이름을 구별하지 않아 2로 나눈 2^(n−1)−1이에요. 여집합 쌍의 중복을 다루는 세기예요.",
        )


def gen_barchart():
    # 막대그래프 읽기 — 둘째로 많은 값 찾기(자료를 크기 순으로 읽는 힘). (자료와가능성 난3)
    for vals in [[3, 5, 2, 6], [4, 7, 3, 8], [6, 2, 9, 5], [5, 10, 7, 4]]:
        ordered = sorted(vals, reverse=True)
        ans = ordered[1]
        add(
            "barchart", "DATA_POSSIBILITY", 3, ["자료 읽기", "크기 순 비교"],
            "아래 그래프는 가·나·다·라 네 반이 모은 화분 수예요. 둘째로 많이 모은 반은 화분을 몇 개 모았을까요?",
            f"{ans}개", [f"{c}개" for c in _pick_distractors(ans, [ordered[0], ordered[2], min(vals), ans + 1])],
            f"막대를 높은 순으로 읽으면 {ordered[0]}, {ordered[1]}, {ordered[2]}, {ordered[3]}이에요. 가장 높은 막대는 "
            f"{ordered[0]}개이고, 그다음(둘째)이 {ans}개예요.",
            [(f"{ordered[0]}개", "그건 '가장' 많은 반이에요. 그다음(둘째)으로 높은 막대를 읽어요."),
             (f"{min(vals)}개", "가장 적은 게 아니라 둘째로 '많은' 것을 찾아요.")],
            figure={"type": "BAR_CHART", "heights": vals, "params": {"highlight": -1}},
            detail="막대그래프는 막대의 높이로 크기를 한눈에 비교해요. '둘째로 많은 것'은 가장 높은 막대를 뺀 나머지 중 가장 "
            "높은 것이에요. 자료를 크기 순으로 정리해 읽는 연습이에요.",
            en={
                "statement": "The graph below shows the number of flowerpots collected by classes A, B, C, and D. How many flowerpots did the class with the second-most collect?",
                "answer": f"{ans} flowerpots",
                "distractors": [f"{c} flowerpots" for c in _pick_distractors(ans, [ordered[0], ordered[2], min(vals), ans + 1])],
                "explanation": f"Reading the bars from tallest to shortest gives {ordered[0]}, {ordered[1]}, {ordered[2]}, {ordered[3]}. The tallest bar is {ordered[0]}, and the next one (the second) is {ans}.",
                "mistakes": [(f"{ordered[0]} flowerpots", "That's the class with the 'most'. Read the next-tallest (second) bar."),
                             (f"{min(vals)} flowerpots", "You want the second-'most', not the fewest.")],
                "detail": "A bar chart compares sizes at a glance by bar height. The 'second-most' is the tallest of the rest after removing the tallest bar. It's practice at reading data sorted by size.",
            },
        )


def gen_chartavg():
    # 막대그래프를 읽어 평균 구하기(자료 읽기 + 평균). (자료와가능성 난5)
    for vals in [[4, 6, 8, 10], [3, 5, 9, 7], [8, 4, 6, 10], [5, 11, 7, 9]]:
        total = sum(vals)
        ans = total // len(vals)
        add(
            "chartavg", "DATA_POSSIBILITY", 5, ["자료 읽기", "평균"],
            "아래 그래프는 가·나·다·라 네 모둠이 캔 감자 수예요. 네 모둠이 캔 감자의 평균은 몇 개일까요?",
            f"{ans}개", [f"{c}개" for c in _pick_distractors(ans, [total, max(vals), ans + 1, ans - 1])],
            f"막대 값을 모두 읽어 더하면 {'+'.join(map(str, vals))}={total}개예요. 모둠이 4개니 평균은 {total}÷4={ans}개예요.",
            [(f"{total}개", "합만 구하면 안 돼요. 모둠 수(4)로 나눠야 평균이에요."),
             (f"{max(vals)}개", "가장 높은 막대가 아니라, 전체를 고르게 나눈 값이 평균이에요.")],
            figure={"type": "BAR_CHART", "heights": vals, "params": {"highlight": -1}},
            detail="막대그래프에서 평균은 모든 막대 값을 더해 막대 개수로 나눠요. 그래프를 정확히 읽어 수로 옮긴 뒤 계산하는, "
            "자료 해석과 평균을 잇는 문제예요.",
            en={
                "statement": "The graph below shows the number of potatoes dug up by four groups A, B, C, and D. What is the average number of potatoes the four groups dug up?",
                "answer": f"{ans} potatoes",
                "distractors": [f"{c} potatoes" for c in _pick_distractors(ans, [total, max(vals), ans + 1, ans - 1])],
                "explanation": f"Reading all the bar values and adding them gives {'+'.join(map(str, vals))}={total} potatoes. There are 4 groups, so the average is {total}÷4={ans} potatoes.",
                "mistakes": [(f"{total} potatoes", "Don't stop at the sum. Divide by the number of groups (4) to get the average."),
                             (f"{max(vals)} potatoes", "The average isn't the tallest bar — it's the value when the total is shared out evenly.")],
                "detail": "In a bar chart, the average is found by adding all the bar values and dividing by the number of bars. You read the graph accurately, turn it into numbers, then compute — a problem connecting data interpretation with averages.",
            },
        )


def gen_diagregions():
    # 볼록 n각형의 대각선이 내부를 나누는 조각(영역) 수 = 1 + 대각선수 + 교점수. (도형과측정 난10)
    for n in [6, 7, 5, 8]:
        diag = n * (n - 3) // 2
        cross = comb(n, 4)
        ans = 1 + diag + cross
        add(
            "diagregions", "SHAPE_MEASUREMENT", 10, ["오일러 공식", "영역 세기"],
            f"볼록 {n}각형의 대각선을 모두 그었어요. 어느 세 대각선도 내부의 한 점에서 만나지 않는다면, 대각선들이 "
            f"다각형 내부를 모두 몇 개의 조각(영역)으로 나눌까요?",
            f"{ans}조각", [f"{c}조각" for c in _pick_distractors(ans, [cross, diag, ans - 1, ans + 2])],
            f"처음엔 다각형 1조각이에요. 대각선을 하나 그을 때마다 '그 선이 지나는 교점 수 + 1'만큼 조각이 늘어요. "
            f"모두 합치면 1 + (대각선 {diag}개) + (교점 {cross}개) = {ans}조각이에요.",
            [(f"{cross}조각", "그건 대각선끼리 만나는 '교점' 수예요. 조각 수는 1 + 대각선 + 교점이에요."),
             (f"{diag}조각", "그건 대각선의 '개수'예요. 조각은 더 많아요(교점에서 갈라지니까).")],
            figure={"type": "POLYGON", "params": {"n": n, "diagonals": 1}},
            detail="대각선이 나누는 조각 수는 오일러 공식(꼭짓점−변+면=2)으로 세요 — 꼭짓점=원래 n개+교점 C(n,4)개, 변은 각 "
            "대각선·변이 교점마다 쪼개진 수예요. 정리하면 조각 수 = 1 + n(n−3)/2 + C(n,4). 교점 세기(C(n,4))에서 한 걸음 더 나간 문제예요.",
        )


def gen_geosum():
    # 등비수열 합 1+2+4+…+2^(k-1) = 2^k − 1. 2배씩 커지는 수의 합 규칙. (변화와관계 난8)
    for k in [8, 6, 10, 7]:
        last = 2 ** (k - 1)
        ans = 2 ** k - 1
        add(
            "geosum", "CHANGE_RELATION", 8, ["등비수열", "합의 규칙"],
            f"1 + 2 + 4 + 8 + … 처럼 앞의 수의 2배씩 커지는 수를, 1부터 {last}까지 모두 더하면 합은 얼마일까요?",
            str(ans), [str(c) for c in _pick_distractors(ans, [2 ** k, last, ans + 1, ans - 1])],
            f"2배씩 커지는 수를 다 더하면 신기하게도 '마지막 수의 2배보다 1 작은 수'가 돼요. 마지막이 {last}이니 "
            f"{last}×2 − 1 = {2 ** k} − 1 = {ans}예요.",
            [(str(2 ** k), "마지막 수의 2배에서 1을 빼야 해요(딱 1 모자라요)."),
             (str(last), "마지막 한 항이 아니라 전부 더한 합이에요.")],
            detail="1+2+4+…+2^(k−1) = 2^k − 1이에요. 각 항이 그 앞까지의 합보다 1 큰 성질(1, 1+2=3, 1+2+4=7…)이라, "
            "합은 항상 다음 2의 거듭제곱보다 1 작아요. 이진법·배수 사고와 이어지는 등비수열 합의 기본이에요.",
        )


def gen_dist3d():
    # 공간에서 원점부터 (x,y,z)까지 거리 = √(x²+y²+z²). (도형과측정 난8)
    for x, y, z in [(2, 3, 6), (1, 2, 2), (2, 6, 9), (6, 6, 7)]:
        sq = x * x + y * y + z * z
        ans = int(sq ** 0.5)
        add(
            "dist3d", "SHAPE_MEASUREMENT", 8, ["공간 좌표", "피타고라스"],
            f"공간에서 점 (0, 0, 0)부터 점 ({x}, {y}, {z})까지의 거리는 얼마일까요?",
            str(ans), [str(c) for c in _pick_distractors(ans, [x + y + z, ans + 1, ans - 1, x + y])],
            f"공간에서 거리는 √(가로²+세로²+높이²)로 구해요(피타고라스의 공간판). "
            f"√({x}²+{y}²+{z}²) = √{sq} = {ans}예요.",
            [(str(x + y + z), "좌표를 그냥 더하면 안 돼요. 각각 제곱해 더한 뒤 제곱근을 씌워요.")],
            detail="평면의 거리 √(x²+y²)를 공간으로 넓히면 √(x²+y²+z²)예요. 직육면체의 대각선을 두 번의 피타고라스로 구하는 것과 "
            "같아요. 좌표와 길이를 잇는 공간 측정의 핵심이에요.",
        )


def gen_necklace():
    # 염주(목걸이)순열 = (n−1)!/2 : 원순열에서 뒤집기까지 같게 본다. (자료와가능성 난8)
    for n in [4, 5, 6, 7]:
        circ = factorial(n - 1)
        ans = circ // 2
        add(
            "necklace", "DATA_POSSIBILITY", 8, ["염주순열", "회전·대칭 겹침"],
            f"서로 다른 구슬 {n}개를 실에 꿰어 목걸이를 만들어요. 돌리거나 뒤집어서 같아지는 것은 한 가지로 볼 때, "
            f"서로 다른 목걸이는 몇 가지일까요?",
            f"{ans}가지", [f"{c}가지" for c in _pick_distractors(ans, [circ, factorial(n), ans + 2, ans - 1])],
            f"한 줄로 꿰면 {n}!가지지만, 원형이라 돌려서 같은 {n}가지를 묶으면 원순열 (n−1)!={circ}가지예요. "
            f"목걸이는 뒤집어도 같으니 다시 2로 나눠 {circ}÷2={ans}가지예요.",
            [(f"{circ}가지", "목걸이는 '뒤집으면' 같아져요. 원순열에서 2로 한 번 더 나눠요.")],
            detail="목걸이(염주)처럼 회전뿐 아니라 뒤집기로도 같아지는 배열은 원순열 (n−1)!을 다시 2로 나눈 (n−1)!/2예요. "
            "'같다고 보는 움직임'이 많을수록 경우의 수가 줄어드는 대칭 세기의 대표 문제예요.",
        )


def gen_boxsurface():
    # 직육면체 겉넓이 = 2(ab+bc+ca). (도형과측정 난6)
    for a, b, c in [(3, 4, 5), (2, 3, 4), (5, 5, 2), (1, 4, 6)]:
        ans = 2 * (a * b + b * c + c * a)
        add(
            "boxsurface", "SHAPE_MEASUREMENT", 6, ["겉넓이", "면 세기"],
            f"가로 {a}cm, 세로 {b}cm, 높이 {c}cm인 직육면체의 겉넓이는 몇 cm²일까요?",
            f"{ans}cm²", [f"{v}cm²" for v in _pick_distractors(ans, [a * b * c, a * b + b * c + c * a, ans + 4, ans - 4])],
            f"직육면체는 마주 보는 면이 세 쌍이에요. 한 쌍씩 넓이는 {a}×{b}, {b}×{c}, {c}×{a}이고, 각각 2개씩이라 "
            f"2×({a * b}+{b * c}+{c * a}) = {ans}cm²예요.",
            [(f"{a * b * c}cm²", "그건 부피예요(가로×세로×높이). 겉넓이는 여섯 면의 넓이 합이에요."),
             (f"{a * b + b * c + c * a}cm²", "세 면만 더했어요. 마주 보는 면까지 각각 2개씩이라 ×2 해요.")],
            detail="직육면체 겉넓이는 마주 보는 세 쌍의 면 넓이를 더한 2(ab+bc+ca)예요. 부피(abc)와 헷갈리지 않고, "
            "면을 빠짐없이 세는 게 핵심이에요.",
            en={
                "statement": f"What is the surface area of a rectangular box that is {a}cm wide, {b}cm deep, and {c}cm tall, in cm²?",
                "answer": f"{ans}cm²",
                "distractors": [f"{v}cm²" for v in _pick_distractors(ans, [a * b * c, a * b + b * c + c * a, ans + 4, ans - 4])],
                "explanation": f"A rectangular box has three pairs of opposite faces. Each pair has area {a}×{b}, {b}×{c}, {c}×{a}, and there are two of each, so 2×({a * b}+{b * c}+{c * a}) = {ans}cm².",
                "mistakes": [(f"{a * b * c}cm²", "That's the volume (width×depth×height). Surface area is the sum of the areas of the six faces."),
                             (f"{a * b + b * c + c * a}cm²", "You added only three faces. With the opposite faces there are two of each, so ×2.")],
                "detail": "A rectangular box's surface area is 2(ab+bc+ca), the sum of the areas of its three pairs of opposite faces. The key is not to confuse it with volume (abc) and to count every face without missing any.",
            },
        )


def gen_passcode():
    # 반복 허용 비밀번호 경우의 수 = (숫자 종류)^(자리 수). (자료와가능성 난6)
    for base, dig in [(10, 3), (2, 5), (6, 3), (3, 4)]:
        ans = base ** dig
        add(
            "passcode", "DATA_POSSIBILITY", 6, ["곱의 법칙", "반복 허용"],
            f"0부터 {base - 1}까지 {base}가지 숫자로 {dig}자리 비밀번호를 만들어요. 같은 숫자를 여러 번 써도 될 때, "
            f"만들 수 있는 비밀번호는 모두 몇 가지일까요?",
            f"{ans}가지", [f"{c}가지" for c in _pick_distractors(ans, [base * dig, base ** (dig - 1), ans + base, ans - base])],
            f"각 자리마다 {base}가지 숫자가 올 수 있고, 자리가 {dig}개니까 {base}를 {dig}번 곱해요 → "
            f"{'×'.join([str(base)] * dig)} = {ans}가지예요.",
            [(f"{base * dig}가지", "자리 수만큼 '더하는' 게 아니라 '곱해요'. 각 자리가 독립이라 곱의 법칙이에요.")],
            detail="각 자리를 독립적으로 채우고 반복을 허용하면 (선택 가지)^(자리 수)예요. 자리마다 곱하는 곱의 법칙의 대표 예로, "
            "암호·번호판 경우의 수가 왜 폭발하는지 보여줘요.",
            en={
                "statement": f"You make a {dig}-digit passcode from the {base} digits 0 to {base - 1}. If you may reuse the same digit multiple times, how many passcodes can you make in all?",
                "answer": f"{ans} ways",
                "distractors": [f"{c} ways" for c in _pick_distractors(ans, [base * dig, base ** (dig - 1), ans + base, ans - base])],
                "explanation": f"Each position can hold {base} digits, and there are {dig} positions, so multiply {base} by itself {dig} times → {'×'.join([str(base)] * dig)} = {ans} ways.",
                "mistakes": [(f"{base * dig} ways", "You don't 'add' one per position, you 'multiply'. Each position is independent, so it's the product (multiplication) rule.")],
                "detail": "Filling each position independently with repetition allowed gives (choices)^(positions). It's the flagship example of the product rule — multiplying position by position — and shows why the number of passcodes or license plates explodes.",
            },
        )


def gen_symaxis():
    # 정n각형의 대칭축 개수 = n. (도형과측정 난3)
    for n in [3, 4, 5, 6]:
        ans = n
        name = {3: "정삼각형", 4: "정사각형", 5: "정오각형", 6: "정육각형"}[n]
        add(
            "symaxis", "SHAPE_MEASUREMENT", 3, ["선대칭", "대칭축"],
            f"{name}은 선대칭 도형이에요. 접었을 때 완전히 겹치게 하는 대칭축은 모두 몇 개일까요?",
            f"{ans}개", [f"{c}개" for c in _pick_distractors(ans, [1, 2, n + 1, n - 1])],
            f"{name}은 각 꼭짓점(또는 변의 한가운데)을 지나는 대칭축을 가져요. 그 수는 변의 수와 같은 {ans}개예요.",
            [("1개", "대칭축이 하나만 있는 게 아니에요. 여러 방향으로 접어도 겹쳐요."),
             (f"{n - 1}개", "정{}각형의 대칭축은 변의 수와 같아요. 하나 빠뜨리지 않았는지 세어 보세요.".format(n))],
            figure={"type": "POLYGON", "params": {"n": n}},
            detail="정n각형은 n개의 대칭축을 가져요. 홀수각형은 각 꼭짓점과 마주 보는 변의 중점을 잇고, 짝수각형은 마주 보는 "
            "꼭짓점끼리·변끼리를 이어요. 어느 쪽이든 축의 수는 변의 수 n과 같아요.",
            en={
                "statement": f"{('An equilateral triangle', 'A square', 'A regular pentagon', 'A regular hexagon')[n - 3]} is a line-symmetric shape. How many axes of symmetry make it overlap completely when folded?",
                "answer": f"{ans} axes",
                "distractors": [f"{c} " + ("axis" if c == "1" else "axes") for c in _pick_distractors(ans, [1, 2, n + 1, n - 1])],
                "explanation": f"{('An equilateral triangle', 'A square', 'A regular pentagon', 'A regular hexagon')[n - 3]} has an axis of symmetry through each vertex (or the midpoint of each side). Their number equals the number of sides, {ans}.",
                "mistakes": [("1 axis", "There isn't just one axis of symmetry — it overlaps when folded in several directions."),
                             (f"{n - 1} axes", "A regular polygon's axes of symmetry equal the number of sides. Check you didn't miss one.")],
                "detail": "A regular n-gon has n axes of symmetry. An odd-sided one joins each vertex to the midpoint of the opposite side; an even-sided one joins opposite vertices and opposite side midpoints. Either way, the number of axes equals the number of sides, n.",
            },
        )


def gen_rectperim():
    # 직사각형 둘레 = 2×(가로+세로). 측정. (도형과측정 난4)
    for a, b in [(7, 4), (9, 5), (6, 6), (8, 3)]:
        ans = 2 * (a + b)
        add(
            "rectperim", "SHAPE_MEASUREMENT", 4, ["둘레", "측정"],
            f"가로 {a}cm, 세로 {b}cm인 직사각형이 있어요. 이 직사각형의 둘레는 몇 cm일까요?",
            f"{ans}cm", [f"{c}cm" for c in _pick_distractors(ans, [a * b, a + b, ans + 2, ans - 2])],
            f"직사각형은 가로 두 변, 세로 두 변이에요. 둘레 = (가로+세로)×2 = ({a}+{b})×2 = {ans}cm예요.",
            [(f"{a * b}cm", "그건 넓이예요(가로×세로). 둘레는 네 변의 길이를 더해요."),
             (f"{a + b}cm", "가로와 세로를 한 번씩만 더했어요. 각각 두 변씩이라 ×2 해요.")],
            detail="직사각형 둘레는 네 변의 합이에요. 마주 보는 변이 같으니 (가로+세로)를 구해 2배 하면 돼요. 넓이(가로×세로)와 "
            "헷갈리지 않는 게 핵심이에요.",
            en={
                "statement": f"A rectangle is {a} cm wide and {b} cm tall. What is its perimeter, in cm?",
                "answer": f"{ans}cm",
                "distractors": [f"{c}cm" for c in _pick_distractors(ans, [a * b, a + b, ans + 2, ans - 2])],
                "explanation": f"A rectangle has two width sides and two height sides. Perimeter = (width+height)×2 = ({a}+{b})×2 = {ans} cm.",
                "mistakes": [(f"{a * b}cm", "That is the area (width×height). The perimeter adds up the lengths of the four sides."),
                             (f"{a + b}cm", "You added the width and height only once. There are two of each side, so multiply by 2.")],
                "detail": "A rectangle's perimeter is the sum of its four sides. Since opposite sides are equal, find (width+height) and double it. The key is not to mix it up with the area (width×height).",
            },
        )


def gen_interiorangle():
    # 정n각형 한 내각 = (n−2)×180 ÷ n. (도형과측정 난4)
    for n in [5, 6, 8, 10]:
        ans = (n - 2) * 180 // n
        total = (n - 2) * 180
        add(
            "interiorangle", "SHAPE_MEASUREMENT", 4, ["다각형 내각", "각도"],
            f"정{n}각형의 한 내각의 크기는 몇 도일까요? (모든 각이 같아요)",
            f"{ans}도", [f"{c}도" for c in _pick_distractors(ans, [total // (n - 1), ans + 10, ans - 10, 180 - ans])],
            f"n각형의 내각의 합은 (n−2)×180이에요. 정{n}각형은 {n}−2={n - 2}, ×180 = {total}도이고, 각이 {n}개로 같으니 "
            f"{total}÷{n} = {ans}도예요.",
            [(f"{180 - ans}도", "한 내각을 직접 구해요. 내각의 합을 각 개수로 나눠요.")],
            figure={"type": "POLYGON", "params": {"n": n}},
            detail="다각형의 내각의 합은 삼각형으로 쪼갠 개수(n−2)에 180°를 곱해 구해요. 정다각형은 모든 각이 같으니 그 합을 "
            "각의 개수로 나누면 한 내각이 나와요.",
            en={
                "statement": f"What is each interior angle of a regular {n}-gon, in degrees? (all angles are equal)",
                "answer": f"{ans}°",
                "distractors": [f"{c}°" for c in _pick_distractors(ans, [total // (n - 1), ans + 10, ans - 10, 180 - ans])],
                "explanation": f"The interior angles of an n-gon add up to (n−2)×180. For a regular {n}-gon that is {n}−2={n - 2}, ×180 = {total}°, and since the {n} angles are equal, {total}÷{n} = {ans}°.",
                "mistakes": [(f"{180 - ans}°", "Find one interior angle directly. Divide the sum of the interior angles by the number of angles.")],
                "detail": "The sum of a polygon's interior angles is found by multiplying 180° by the number of triangles it splits into (n−2). In a regular polygon all angles are equal, so dividing that sum by the number of angles gives one interior angle.",
            },
        )


def gen_prismparts():
    # 각기둥의 모서리 수 = 밑면 변수 × 3. (도형과측정 난4)
    for n in [5, 6, 4, 8]:
        ans = 3 * n
        add(
            "prismparts", "SHAPE_MEASUREMENT", 4, ["입체도형", "모서리 세기"],
            f"밑면이 {n}각형인 각기둥이 있어요. 이 각기둥의 모서리는 모두 몇 개일까요?",
            f"{ans}개", [f"{c}개" for c in _pick_distractors(ans, [2 * n, n + 2, ans + 2, ans - 2])],
            f"각기둥은 위·아래 밑면에 {n}개씩 모서리가 있고, 두 밑면을 잇는 기둥 모서리가 {n}개 더 있어요. "
            f"{n}+{n}+{n} = {n}×3 = {ans}개예요.",
            [(f"{2 * n}개", "그건 꼭짓점 수예요(위·아래 {}개씩). 모서리는 밑면 두 개 + 기둥이라 3배예요.".format(n)),
             (f"{n + 2}개", "그건 면의 수예요(옆면 {}개 + 밑면 2개). 모서리를 세요.".format(n))],
            detail="n각기둥은 밑면(위·아래) 모서리가 n개씩 2n개, 두 밑면을 잇는 옆 모서리가 n개라 모두 3n개예요. "
            "꼭짓점(2n)·면(n+2)과 구분해 세는 공간 감각 문제예요.",
            en={
                "statement": f"A prism has a {n}-gon as its base. How many edges does this prism have in all?",
                "answer": f"{ans} edges",
                "distractors": [f"{c} edges" for c in _pick_distractors(ans, [2 * n, n + 2, ans + 2, ans - 2])],
                "explanation": f"A prism has {n} edges on each of the top and bottom bases, plus {n} more edges connecting the two bases. {n}+{n}+{n} = {n}×3 = {ans}.",
                "mistakes": [(f"{2 * n} edges", f"That is the number of vertices ({n} on the top and bottom each). Edges are the two bases plus the connecting pillars, so 3 times as many."),
                             (f"{n + 2} edges", f"That is the number of faces ({n} side faces + 2 bases). Count the edges instead.")],
                "detail": "A prism with an n-gon base has n edges on each base (2n in all) and n side edges connecting the two bases, for 3n edges in total. It's a spatial-sense problem about counting edges apart from vertices (2n) and faces (n+2).",
            },
        )


def gen_triangleangle():
    # 삼각형 세 각의 합은 180° — 두 각으로 나머지 구하기. (도형과측정 난4)
    for a, b in [(50, 70), (40, 65), (90, 35), (72, 53)]:
        ans = 180 - a - b
        add(
            "triangleangle", "SHAPE_MEASUREMENT", 4, ["삼각형 내각", "각도"],
            f"삼각형의 세 각 중 두 각이 각각 {a}도와 {b}도예요. 나머지 한 각은 몇 도일까요?",
            f"{ans}도", [f"{c}도" for c in _pick_distractors(ans, [a + b, 180 - a, ans + 10, ans - 10])],
            f"삼각형 세 각의 합은 항상 180도예요. 그래서 나머지 각 = 180 − {a} − {b} = {ans}도예요.",
            [(f"{a + b}도", "두 각을 더하기만 하면 안 돼요. 180도에서 두 각을 빼요.")],
            detail="삼각형 세 각의 합은 언제나 180°예요. 두 각을 알면 180에서 빼서 나머지 각을 구해요. 도형 각도 문제의 가장 기본 규칙이에요.",
            en={
                "statement": f"Two of a triangle's three angles are {a}° and {b}°. What is the remaining angle, in degrees?",
                "answer": f"{ans}°",
                "distractors": [f"{c}°" for c in _pick_distractors(ans, [a + b, 180 - a, ans + 10, ans - 10])],
                "explanation": f"The three angles of a triangle always add up to 180°. So the remaining angle = 180 − {a} − {b} = {ans}°.",
                "mistakes": [(f"{a + b}°", "Don't just add the two angles. Subtract the two angles from 180°.")],
                "detail": "The three angles of a triangle always add up to 180°. Knowing two, subtract from 180 to find the remaining angle. It's the most basic rule of shape-angle problems.",
            },
        )


def gen_avgbasic():
    # 평균 = 합 ÷ 개수. (자료와가능성 난4)
    for vals in [[4, 6, 8, 10], [2, 4, 9, 5], [10, 20, 30, 40], [3, 7, 8, 6]]:
        total = sum(vals)
        ans = total // len(vals)
        vs = ", ".join(str(v) for v in vals)
        add(
            "avgbasic", "DATA_POSSIBILITY", 4, ["평균", "합 나누기"],
            f"네 번의 점수가 {vs}이에요. 이 점수들의 평균은 얼마일까요?",
            str(ans), [str(c) for c in _pick_distractors(ans, [total, max(vals), ans + 1, ans - 1])],
            f"평균은 모두 더해 개수로 나눠요. {vs}을 더하면 {total}, 4로 나누면 {ans}예요.",
            [(str(total), "합만 구하면 안 돼요. 개수로 나눠야 평균이에요."),
             (str(max(vals)), "가장 큰 값이 아니라, 전체를 고르게 나눈 값이 평균이에요.")],
            detail="평균은 여러 값을 '고르게 나눈' 대푯값으로, 모두 더해 개수로 나눠요. 자료를 하나의 수로 요약하는 통계의 기본이에요.",
            en={
                "statement": f"Four scores are {vs}. What is the average of these scores?",
                "answer": str(ans),
                "distractors": [str(c) for c in _pick_distractors(ans, [total, max(vals), ans + 1, ans - 1])],
                "explanation": f"To find the average, add everything up and divide by the count. {vs} add up to {total}, and dividing by 4 gives {ans}.",
                "mistakes": [(str(total), "Don't stop at the sum. You have to divide by the count to get the average."),
                             (str(max(vals)), "It isn't the largest value — the average is the value that spreads everything out evenly.")],
                "detail": "The average is a representative value that 'spreads things out evenly': add up all the values and divide by the count. It's the basis of statistics — summarizing data into a single number.",
            },
        )


def gen_lineup():
    # n명을 한 줄로 세우는 방법 = n!. (자료와가능성 난4)
    for n in [3, 4, 5, 6]:
        ans = factorial(n)
        add(
            "lineup", "DATA_POSSIBILITY", 4, ["경우의 수", "순서 세기"],
            f"서로 다른 {n}명이 한 줄로 서는 방법은 모두 몇 가지일까요?",
            f"{ans}가지", [f"{c}가지" for c in _pick_distractors(ans, [n * n, factorial(n - 1), n * (n - 1), ans + n])],
            f"맨 앞에 설 사람이 {n}가지, 그다음 자리는 남은 {n - 1}가지, 그다음 {n - 2}가지… 이렇게 곱하면 "
            f"{'×'.join(str(k) for k in range(n, 0, -1))} = {ans}가지예요.",
            [(f"{n * n}가지", "자리마다 사람이 '한 명씩 줄어들어요'. 같은 수를 곱하는 게 아니라 {}×{}×…예요.".format(n, n - 1))],
            detail="서로 다른 것을 한 줄로 배열하는 방법의 수는 n! = n×(n−1)×…×1이에요. 앞자리부터 채울 때 쓸 수 있는 것이 "
            "하나씩 줄어들기 때문이에요. 순서가 있는 세기(순열)의 기본이에요.",
            en={
                "statement": f"In how many different ways can {n} different people stand in a single line?",
                "answer": _en_plural(ans, "way"),
                "distractors": [f"{c} ways" for c in _pick_distractors(ans, [n * n, factorial(n - 1), n * (n - 1), ans + n])],
                "explanation": f"The person at the front has {n} ways, the next spot has the remaining {n - 1}, then {n - 2}… Multiplying these, {'×'.join(str(k) for k in range(n, 0, -1))} = {ans} ways.",
                "mistakes": [(f"{n * n} ways", "The people available 'drop by one' at each spot. You aren't multiplying the same number — it's {}×{}×…".format(n, n - 1))],
                "detail": "The number of ways to arrange distinct things in a line is n! = n×(n−1)×…×1, because what is left to place drops by one as you fill from the front. It is the basis of ordered counting (permutations).",
            },
        )


def gen_mode():
    # 최빈값 — 가장 자주 나온 값. (자료와가능성 난4)
    for vals in [[3, 5, 3, 7, 3, 5], [2, 2, 4, 6, 2], [8, 1, 8, 3, 8, 1], [5, 9, 5, 5, 2]]:
        ans = max(set(vals), key=vals.count)
        vs = ", ".join(str(v) for v in vals)
        second = sorted(set(vals), key=vals.count)[-2]
        add(
            "mode", "DATA_POSSIBILITY", 4, ["최빈값", "자료 정리"],
            f"자료 {vs} 가 있어요. 가장 많이 나온 수(최빈값)는 무엇일까요?",
            str(ans), [str(c) for c in _pick_distractors(ans, [second, max(vals), min(vals), ans + 1])],
            f"각 수가 몇 번 나왔는지 세어 봐요. {ans}이(가) {vals.count(ans)}번으로 가장 많이 나왔으니 최빈값은 {ans}이에요.",
            [(str(max(vals)), "가장 '큰' 수가 아니라 가장 '자주 나온' 수가 최빈값이에요.")],
            detail="최빈값은 자료에서 가장 자주 나타나는 값이에요. 평균·중앙값과 함께 자료를 대표하는 값 중 하나로, 개수를 "
            "세어 가장 많은 것을 찾으면 돼요.",
            en={
                "statement": f"You have the data {vs}. What is the number that appears most often (the mode)?",
                "answer": str(ans),
                "distractors": [str(c) for c in _pick_distractors(ans, [second, max(vals), min(vals), ans + 1])],
                "explanation": f"Count how many times each number appears. {ans} appears {vals.count(ans)} times — the most — so the mode is {ans}.",
                "mistakes": [(str(max(vals)), "The mode is not the 'largest' number but the one that appears most 'often'.")],
                "detail": "The mode is the value that appears most often in the data. Along with the average and median, it is one of the values that represent a data set; just count and pick whichever occurs the most.",
            },
        )


def gen_simpleprob():
    # 간단한 확률 = (해당 경우) ÷ (전체). 기약분수. (자료와가능성 난4)
    def _frac(num, den):
        g = gcd(num, den) or 1
        return f"{num // g}/{den // g}"
    for r, b in [(3, 2), (2, 4), (4, 6), (5, 3)]:
        total = r + b
        ans = _frac(r, total)
        cands = [_frac(b, total), f"{r}/{b}", _frac(r + 1, total), _frac(r, total + 1)]
        distract = []
        for c in cands:
            if c != ans and c not in distract:
                distract.append(c)
        add(
            "simpleprob", "DATA_POSSIBILITY", 4, ["확률", "부분과 전체"],
            f"주머니에 빨간 공 {r}개와 파란 공 {b}개가 있어요. 눈을 감고 공 하나를 꺼낼 때, 빨간 공이 나올 확률은 얼마일까요?",
            ans, distract[:3],
            f"전체 공은 {r}+{b}={total}개, 그중 빨간 공이 {r}개예요. 확률은 (빨간 공)÷(전체) = {r}/{total}"
            + (f" = {ans}" if ans != f"{r}/{total}" else "") + "예요.",
            [(f"{r}/{b}", "분모는 파란 공 수가 아니라 '전체' 공 수예요.")],
            detail="확률은 (원하는 경우의 수)÷(전체 경우의 수)예요. 여기선 빨간 공 수를 전체 공 수로 나눠요. 분모를 '전체'로 "
            "두는 것과 기약분수로 나타내는 게 핵심이에요.",
            en={
                "statement": f"A bag holds {r} red balls and {b} blue balls. With your eyes closed you take out one ball. What is the probability of getting a red ball?",
                "answer": ans,
                "distractors": distract[:3],
                "explanation": f"There are {r}+{b}={total} balls in all, of which {r} are red. The probability is (red balls)÷(all balls) = {r}/{total}"
                + (f" = {ans}" if ans != f"{r}/{total}" else "") + ".",
                "mistakes": [(f"{r}/{b}", "The denominator isn't the number of blue balls — it's the number of 'all' balls.")],
                "detail": "Probability is (favorable cases)÷(total cases). Here you divide the number of red balls by the total number of balls. The keys are putting 'all' in the denominator and giving the answer as a fully reduced fraction.",
            },
        )


def _prime_factor_str(n):
    """n의 소인수분해를 '2²×3' 형태 문자열로. (해설용)"""
    sup = {1: "", 2: "²", 3: "³", 4: "⁴", 5: "⁵"}
    parts, m, p = [], n, 2
    while p * p <= m:
        e = 0
        while m % p == 0:
            m //= p
            e += 1
        if e:
            parts.append(f"{p}{sup.get(e, '^' + str(e))}")
        p += 1
    if m > 1:
        parts.append(str(m))
    return "×".join(parts)


def gen_totient():
    # 오일러 피 함수 φ(n): n 이하에서 n과 서로소인 수의 개수 = n×∏(1−1/p). (수와연산 난9)
    for n in [12, 20, 30, 36]:
        primes = sorted({p for p in range(2, n + 1) if n % p == 0 and all(p % q for q in range(2, p))})
        ans = sum(1 for k in range(1, n + 1) if gcd(k, n) == 1)
        prod = "×".join([str(n)] + [f"(1−1/{p})" for p in primes])
        add(
            "totient", "NUMBER_OPERATION", 9, ["오일러 피 함수", "서로소 개수"],
            f"1부터 {n}까지의 자연수 중에서 {n}{_gwa(str(n))} 서로소인(공약수가 1뿐인) 수는 모두 몇 개일까요?",
            f"{ans}개", [f"{c}개" for c in _pick_distractors(ans, [n // 2, ans + 1, ans - 1, ans + 2])],
            f"{n}{_eun(str(n))} {_prime_factor_str(n)}이라, 각 소인수 {', '.join(map(str, primes))}의 배수를 걸러내요. "
            f"서로소 개수는 {prod} = {ans}개예요. (전체에서 소인수의 배수 비율만큼씩 덜어내는 곱셈이에요.)",
            [(f"{n // 2}개", "짝수만 빼면 안 돼요. 모든 소인수의 배수를 겹치지 않게 걸러야 해요."),
             (f"{ans + 1}개", "1은 모든 수와 서로소예요. 빠뜨리기 쉬우니 포함해서 세요.")],
            detail="오일러 피 함수 φ(n)은 'n 이하에서 n과 서로소인 수의 개수'예요. n의 서로 다른 소인수 p마다 (1−1/p)를 곱하면 구해져요 — "
            "전체 n개에서 각 소인수의 배수 비율을 곱으로 덜어내는 거예요(포함배제와 같은 원리). 약수·서로소를 다루는 정수론의 핵심 함수예요.",
        )


def gen_josephus():
    # 조세푸스 문제(2명마다 제거): 원으로 앉아 짝수 번째부터 빼면 마지막 생존자 = 2L+1 (n=2^m+L). (변화와관계 난9)
    for n in [7, 10, 13, 6]:
        power = 1 << (n.bit_length() - 1)  # n 이하 최대 2의 거듭제곱
        leftover = n - power
        ans = 2 * leftover + 1
        add(
            "josephus", "CHANGE_RELATION", 9, ["2의 거듭제곱", "규칙 찾아 일반화"],
            f"{n}명이 동그랗게 둘러앉아 1번부터 차례로 번호를 붙였어요. 1번은 남기고 2번을 빼고, 3번은 남기고 4번을 빼고… "
            f"이렇게 한 사람씩 건너뛰며 원을 돌며 빼낼 때, 맨 마지막까지 남는 사람은 몇 번일까요?",
            f"{ans}번", [f"{c}번" for c in _pick_distractors(ans, [n, n - 1, ans + 2, 1])],
            f"{n}명을 '{power}(2의 거듭제곱) + {leftover}'으로 봐요. 인원이 딱 2의 거듭제곱이면 항상 1번이 살아남아요. "
            f"남는 {leftover}명만큼 제거가 진행된 뒤라, 살아남는 자리는 2×{leftover}+1 = {ans}번이에요.",
            [(f"{n}번", "마지막 번호가 남는 게 아니에요. 2의 거듭제곱을 기준으로 자리를 다시 세요."),
             (f"1번", "인원이 2의 거듭제곱일 때만 1번이 살아남아요. 남는 인원만큼 자리가 밀려요.")],
            detail="원을 돌며 한 명씩 건너뛰어 제거하는 '조세푸스 문제'예요. 인원이 2의 거듭제곱이면 시작(1번)이 살아남는 성질을 이용해, "
            "n=2^m+L로 쪼개면 생존자는 2L+1번이 돼요. 2의 거듭제곱이라는 뼈대에서 규칙을 일반화하는 대표 문제예요.",
        )


def gen_spacediag():
    # 직육면체 대각선이 지나는 단위정육면체 수 = a+b+c − gcd쌍합 + gcd(a,b,c) (포함배제, 3차원). (도형과측정 난9)
    for a, b, c in [(2, 3, 4), (3, 4, 5), (2, 4, 6), (4, 6, 8)]:
        ans = a + b + c - gcd(a, b) - gcd(b, c) - gcd(c, a) + gcd(gcd(a, b), c)
        naive = a + b + c
        add(
            "spacediag", "SHAPE_MEASUREMENT", 9, ["포함배제", "공간 대각선"],
            f"작은 정육면체 {a * b * c}개를 가로 {a}칸·세로 {b}칸·높이 {c}칸으로 빈틈없이 쌓아 직육면체를 만들었어요. "
            f"한 꼭짓점에서 가장 먼 반대쪽 꼭짓점까지 속을 관통하는 대각선을 그으면, 이 대각선은 작은 정육면체 몇 개를 지날까요?",
            f"{ans}개", [f"{c2}개" for c2 in _pick_distractors(ans, [naive, ans + 1, ans - 1, naive - 1])],
            f"대각선은 가로·세로·높이 칸막이를 넘을 때마다 새 정육면체로 들어가요. 칸막이는 {a}+{b}+{c}={naive}번이지만, "
            f"두 칸막이를 '동시에' 넘는 모서리(gcd만큼)는 한 번만 세야 하고, 세 칸막이를 동시에 넘는 꼭짓점은 다시 더해요. "
            f"{naive} − ({gcd(a, b)}+{gcd(b, c)}+{gcd(c, a)}) + {gcd(gcd(a, b), c)} = {ans}개예요.",
            [(f"{naive}개", "가로+세로+높이만 더하면 안 돼요. 모서리·꼭짓점에서 겹쳐 지나는 곳을 빼고 더해야 해요(포함배제)."),
             (f"{ans - 1}개", "시작하는 첫 칸도 한 개로 세요. 넘는 칸막이 수와 지나는 칸 수를 헷갈리기 쉬워요.")],
            detail="대각선이 지나는 단위정육면체 수는 3차원 포함배제로 세요 — 세 방향 칸막이를 넘는 횟수 (a+b+c)에서, 두 방향 칸막이를 동시에 넘는 모서리(gcd(a,b) 등)를 빼고, "
            "세 방향을 동시에 넘는 꼭짓점(gcd(a,b,c))을 다시 더해요. 2차원(a+b−gcd)을 공간으로 확장한 아름다운 정수·기하 문제예요.",
        )


def gen_derange():
    # 교란순열(완전순열) D(n): 아무도 제자리가 아닌 순열의 수. D(n)=(n−1)(D(n−1)+D(n−2)). (자료와가능성 난9)
    d = [1, 0]  # d[0]=D(0)=1, d[1]=D(1)=0
    for i in range(2, 12):
        d.append((i - 1) * (d[i - 1] + d[i - 2]))
    for n in [4, 5, 6, 3]:
        ans = d[n]
        allperm = factorial(n)
        add(
            "derange", "DATA_POSSIBILITY", 9, ["교란순열", "포함배제"],
            f"{n}명이 각자 자기 이름표를 하나씩 갖고 있다가, 전부 걷어 섞은 뒤 다시 한 개씩 나눠 가졌어요. "
            f"아무도 자기 이름표를 받지 않는 경우는 모두 몇 가지일까요?",
            f"{ans}가지", [f"{c}가지" for c in _pick_distractors(ans, [allperm, ans + 1, ans - 1, allperm - 1])],
            f"{n}명이 이름표를 나눠 갖는 전체 경우는 {n}!={allperm}가지예요. 여기서 '적어도 한 명은 자기 것을 받는' 경우를 "
            f"빼는 포함배제로 세거나, 규칙 D(n)=(n−1)×(D(n−1)+D(n−2))을 쓰면 D({n})={ans}가지예요.",
            [(f"{allperm}가지", f"그건 제한 없는 전체 순열({n}!={allperm})이에요. '아무도 제자리 아님' 조건을 빼야 해요."),
             (f"{ans - 1}가지", "포함배제에서 더하고 빼는 부호를 놓치기 쉬워요. 점화식으로 교차검증하세요.")],
            detail="아무도 제자리에 오지 않는 순열을 '교란순열(완전순열) D(n)'이라 해요. 전체 n!에서 '누군가는 제자리인' 경우를 포함배제로 덜어내면 "
            "D(n)=n!(1−1/1!+1/2!−…)이 되고, 점화식 D(n)=(n−1)(D(n−1)+D(n−2))로도 구해요. '적어도' 조건을 뒤집어 세는 대표 문제예요.",
        )


def gen_prodsum():
    # 연속한 두 수의 곱의 합 1·2+2·3+…+n(n+1) = n(n+1)(n+2)/3. 이웃 항이 지워지는 텔레스코핑. (변화와관계 난7)
    for n in [5, 6, 4, 7]:
        ans = n * (n + 1) * (n + 2) // 3
        last = n * (n + 1)
        terms = " + ".join(f"{k}×{k + 1}" for k in range(1, min(n, 3) + 1)) + (f" + … + {n}×{n + 1}" if n > 3 else "")
        add(
            "prodsum", "CHANGE_RELATION", 7, ["수열의 합", "규칙으로 한꺼번에"],
            f"{terms} 의 값은 얼마일까요?",
            str(ans), [str(c) for c in _pick_distractors(ans, [last, ans // 2, ans + last, n * (n + 1) // 2])],
            f"연속한 두 수의 곱을 더하는 합은 항이 늘어도 규칙이 있어요 — 1·2+2·3+…+n·(n+1) = n(n+1)(n+2)÷3. "
            f"여기선 {n}×{n + 1}×{n + 2}÷3 = {ans}예요. (각 항을 '3칸짜리 계단의 차이'로 바꾸면 이웃끼리 지워져 마지막만 남는 원리예요.)",
            [(str(last), "마지막 항 하나가 아니라 모든 항을 더한 값이에요."),
             (str(n * (n + 1) // 2), "1부터 더한 삼각수와 헷갈리지 마세요. 여기선 '두 수의 곱'을 더해요.")],
            detail="1·2+2·3+…+n(n+1)처럼 연속한 두 수의 곱을 더하면 n(n+1)(n+2)/3이 돼요. 각 항 k(k+1)을 "
            "[k(k+1)(k+2)−(k−1)k(k+1)]/3으로 바꾸면 앞뒤 항이 사슬처럼 지워지고(텔레스코핑) 맨 끝 n(n+1)(n+2)/3만 남기 때문이에요. "
            "많은 항을 규칙 하나로 한꺼번에 더하는 수열 합의 대표 문제예요.",
        )


def gen_quadseq():
    # 계차(이웃 차이)가 등차인 2차 수열의 n번째 항 — '규칙의 규칙'을 찾아 멀리 있는 항 구하기. (변화와관계 난8)
    cases = [
        ("n×n＋1", lambda k: k * k + 1, 10),
        ("n×(n＋1)", lambda k: k * (k + 1), 10),
        ("n×(n＋2)", lambda k: k * (k + 2), 9),
        ("2×n×n−1", lambda k: 2 * k * k - 1, 8),
    ]
    for label, f, pos in cases:
        terms = [f(k) for k in range(1, 6)]
        diffs = [terms[i + 1] - terms[i] for i in range(4)]
        ans = f(pos)
        naive = terms[-1] + (pos - 5) * diffs[-1]  # 계차가 일정하다고 착각한 값(대표 오답)
        add(
            "quadseq", "CHANGE_RELATION", 8, ["계차수열", "규칙의 규칙"],
            f"어떤 수열이 {terms[0]}, {terms[1]}, {terms[2]}, {terms[3]}, {terms[4]}, … 로 이어져요. "
            f"이 규칙을 이어 가면 {pos}번째 수는 얼마일까요?",
            str(ans), [str(c) for c in _pick_distractors(ans, [naive, ans + pos, ans - pos, terms[-1] + diffs[-1]])],
            f"이웃한 두 수의 차(계차)가 {diffs[0]}, {diffs[1]}, {diffs[2]}, {diffs[3]}, … 처럼 "
            f"{diffs[1] - diffs[0]}씩 일정하게 커지는 등차예요(계차의 계차가 일정 → 2차 수열). "
            f"규칙은 {label}이라, {pos}번째 수는 {ans}예요.",
            [(str(naive), "계차가 '일정하다'고 보면 안 돼요. 계차 자체가 일정하게 커지는(등차) 2차 수열이에요."),
             (str(terms[-1] + diffs[-1]), "6번째까지만 가지 말고, 계차를 규칙대로 늘려 가며 목표 항까지 끝까지 더하세요.")],
            detail="계차(이웃 항의 차)가 등차수열이면 원래 수열은 2차식(an²+bn+c)으로 표현돼요 — '계차의 계차'가 일정하기 때문이에요. "
            "가까운 몇 항으로 계차의 규칙을 잡은 뒤, 그 계차를 늘려 가며 더하면 멀리 있는 항도 구할 수 있어요. 규칙의 규칙을 보는 눈을 기르는 문제예요.",
        )


def gen_polyhedron():
    # 정다면체의 모서리 수 = (면 수 × 한 면의 변 수) ÷ 2 (모서리는 두 면이 공유). 오일러 공식으로 꼭짓점도. (도형과측정 난8)
    for name, faces, sides in [("정십이면체", 12, 5), ("정이십면체", 20, 3), ("정팔면체", 8, 3), ("정사면체", 4, 3)]:
        edges = faces * sides // 2
        verts = edges - faces + 2
        add(
            "polyhedron", "SHAPE_MEASUREMENT", 8, ["공간 도형", "모서리는 두 면이 공유"],
            f"면이 {faces}개이고 각 면이 정{sides}각형인 볼록 다면체({name})가 있어요. 이 다면체의 모서리(edge)는 모두 몇 개일까요?",
            f"{edges}개", [f"{c}개" for c in _pick_distractors(edges, [faces * sides, faces + sides, edges + 2, verts])],
            f"각 면은 변이 {sides}개라 변을 모두 세면 {faces}×{sides}={faces * sides}개예요. 그런데 모서리 하나는 "
            f"이웃한 두 면이 함께 쓰므로 정확히 두 번씩 세어졌어요. 그래서 2로 나눠 {faces * sides}÷2={edges}개예요. "
            f"(오일러 공식 꼭짓점−모서리+면=2로 확인하면 꼭짓점은 {verts}개.)",
            [(f"{faces * sides}개", f"변을 센 {faces}×{sides}는 모서리를 '두 번씩' 센 값이에요. 2로 나눠야 해요."),
             (f"{verts}개", "그건 꼭짓점 수예요. 모서리는 (면×변)÷2로 구해요.")],
            detail="다면체의 모서리 수는 (면 수×한 면의 변 수)÷2예요 — 모서리 하나를 이웃한 두 면이 공유해 두 번 세어지기 때문이에요. "
            "꼭짓점은 오일러 공식(꼭짓점−모서리+면=2)으로 구해요. '겹쳐 세고 나누기'와 오일러 공식을 잇는 공간 도형의 대표 문제예요.",
        )


def gen_multiperm():
    # 같은 것이 있는 순열: 전체 순열 total!을 같은 것끼리의 팩토리얼로 나눔. (자료와가능성 난8)
    palette = [
        [("빨강", 2), ("파랑", 3)],
        [("빨강", 3), ("파랑", 3)],
        [("빨강", 2), ("파랑", 2), ("노랑", 1)],
        [("빨강", 4), ("파랑", 2)],
    ]
    for colors in palette:
        total = sum(c for _, c in colors)
        ans = factorial(total)
        for _, c in colors:
            ans //= factorial(c)
        desc = ", ".join(f"{name} 구슬 {c}개" for name, c in colors)
        denom = "×".join(f"{c}!" for _, c in colors)
        add(
            "multiperm", "DATA_POSSIBILITY", 8, ["같은 것이 있는 순열", "중복 나누기"],
            f"{desc}를 한 줄로 늘어놓으려고 해요. 같은 색 구슬끼리는 서로 구별하지 않을 때, 서로 다른 배열은 모두 몇 가지일까요?",
            f"{ans}가지", [f"{c}가지" for c in _pick_distractors(ans, [factorial(total), ans + 2, ans * 2, total * total])],
            f"구슬이 모두 {total}개라 자리에 놓는 전체 순열은 {total}!={factorial(total)}가지예요. 하지만 같은 색끼리 자리를 "
            f"바꿔도 같은 배열이라, 각 색 개수의 팩토리얼로 나눠요 → {total}! ÷ ({denom}) = {ans}가지예요.",
            [(f"{factorial(total)}가지", "같은 색 구슬을 서로 다른 것처럼 셌어요. 같은 색끼리 바꾼 경우를 나눠 줘야 해요."),
             (f"{ans * 2}가지", "나누는 값이 모자라요. 모든 색의 개수 팩토리얼을 빠짐없이 곱해 나누세요.")],
            detail="같은 것이 섞인 것을 일렬로 배열하는 경우의 수는 (전체)! ÷ (같은 것끼리의 개수!들의 곱)이에요 — 전체를 다 다르다고 보고 센 뒤, "
            "같은 것끼리 자리만 바꾼 중복을 나눠 없애는 거예요. 순열에서 '구별되지 않음'을 다루는 대표 도구예요.",
        )


def gen_lasttwo():
    # 큰 거듭제곱의 '끝 두 자리' = mod 100. 오일러 정리(base^φ(100)=base^40≡1)로 지수를 줄여 손계산. (수와연산 난10)
    for base, exp in [(3, 99), (7, 55), (13, 77), (17, 33)]:
        ans = pow(base, exp, 100)
        reduced = exp % 40 or 40
        add(
            "lasttwo", "NUMBER_OPERATION", 10, ["오일러 정리", "나머지로 거듭제곱"],
            f"{base}{_eul(str(base))} {exp}번 곱한 수(즉 {base}^{exp})의 끝 두 자리 수는 무엇일까요?",
            str(ans), [str(c) for c in _pick_distractors(ans, [(ans + 1) % 100, (ans + 10) % 100, (ans * base) % 100, ans - 1])],
            f"끝 두 자리는 100으로 나눈 나머지예요. {base}{_eun(str(base))} 100과 서로소라, 오일러 정리로 {base}^40 ≡ 1 (mod 100)이에요"
            f"(100 이하 100과 서로소인 수가 40개라 φ(100)=40). 그래서 지수 {exp}{_eul(str(exp))} 40으로 나눈 나머지 {reduced}만 남겨 "
            f"{base}^{reduced} = 끝 두 자리 {ans}로 구해요.",
            [(str((ans + 1) % 100), "끝 자리 하나만 보지 말고, 100으로 나눈 나머지(두 자리)를 오일러 정리로 줄여 구하세요.")],
            detail="아주 큰 거듭제곱의 끝 두 자리는 100으로 나눈 나머지예요. 밑이 100과 서로소면 오일러 정리로 base^40≡1(mod 100)이라, "
            "지수를 40으로 나눈 나머지까지 줄여 손으로 계산할 수 있어요. 나머지 세계에서 거듭제곱의 주기를 쓰는 정수론의 핵심 도구예요.",
        )


def gen_cubesum():
    # 세제곱의 합 1³+…+n³ = (1+2+…+n)² = (삼각수)². 합과 삼각수 제곱의 관계 발견. (변화와관계 난10)
    for n in [4, 5, 6, 3]:
        tri = n * (n + 1) // 2
        ans = tri * tri
        sq_sum = n * (n + 1) * (2 * n + 1) // 6  # 제곱의 합(헷갈리기 쉬운 값)
        add(
            "cubesum", "CHANGE_RELATION", 10, ["수열의 합", "숨은 관계 발견"],
            f"1³ + 2³ + 3³ + … + {n}³ 의 값은 얼마일까요? (각 수를 세제곱해서 더해요)",
            str(ans), [str(c) for c in _pick_distractors(ans, [sq_sum, tri, n ** 3, ans - tri])],
            f"놀랍게도 세제곱의 합은 '1부터 그 수까지의 합(삼각수)'을 제곱한 것과 같아요. "
            f"1+2+…+{n} = {tri}이고, 그 제곱 {tri}² = {ans}이에요.",
            [(str(sq_sum), "그건 '제곱'의 합(1²+…+n²)이에요. 여기선 '세제곱'의 합이라 삼각수의 제곱이 돼요."),
             (str(tri), "삼각수 그 자체가 아니라, 삼각수를 '제곱'한 값이에요.")],
            detail="1³+2³+…+n³ = (1+2+…+n)² = (n(n+1)/2)²이에요. 세제곱을 하나씩 더한 값이 '합을 통째로 제곱한 값'과 같다는 "
            "아름다운 관계로, 그림(정사각형을 계단식으로 쌓기)으로도 증명돼요. 겉보기 다른 두 양의 숨은 관계를 발견하는 문제예요.",
        )


def gen_pick():
    # 픽의 정리: 격자 다각형 넓이 = 내부 격자점 + 둘레 격자점÷2 − 1. (도형과측정 난10)
    for inner, boundary in [(4, 6), (5, 8), (0, 4), (6, 10)]:
        ans = inner + boundary // 2 - 1
        add(
            "pick", "SHAPE_MEASUREMENT", 10, ["픽의 정리", "격자점으로 넓이"],
            f"모눈종이의 격자점을 꼭짓점으로 하는 다각형이 있어요. 다각형 '내부'에 있는 격자점이 {inner}개, "
            f"'둘레(변)' 위에 있는 격자점이 {boundary}개예요. 이 다각형의 넓이는 얼마일까요? (모눈 한 칸 넓이는 1)",
            str(ans), [str(c) for c in _pick_distractors(ans, [inner + boundary, inner + boundary // 2, ans + 1, ans + 2])],
            f"픽의 정리를 쓰면 넓이 = (내부 격자점) + (둘레 격자점)÷2 − 1 이에요. "
            f"= {inner} + {boundary}÷2 − 1 = {inner} + {boundary // 2} − 1 = {ans}예요.",
            [(str(inner + boundary), "내부와 둘레 점을 그냥 더하면 안 돼요. 둘레는 반만 세고 1을 빼는 게 픽의 정리예요."),
             (str(inner + boundary // 2), "마지막에 −1을 빼먹었어요. 넓이 = 내부 + 둘레÷2 − 1 이에요.")],
            detail="픽의 정리는 격자점 위 다각형의 넓이를 '내부 격자점 수 + 둘레 격자점 수÷2 − 1'로 구해요. 자로 재지 않고 점만 세어 넓이를 "
            "정확히 얻는 놀라운 정리로, 삼각형으로 쪼개 더해도 성립함을 보일 수 있어요. 측정과 세기를 잇는 기하의 보석이에요.",
        )


def gen_catalan():
    # 카탈란 수 Cn = C(2n,n)/(n+1): 올바른 괄호 짝, 격자 경로, 이진트리 등을 세는 수. (자료와가능성 난10)
    for n in [3, 4, 5, 2]:
        whole = comb(2 * n, n)
        ans = whole // (n + 1)
        add(
            "catalan", "DATA_POSSIBILITY", 10, ["카탈란 수", "올바른 배열 세기"],
            f"여는 괄호 '(' {n}개와 닫는 괄호 ')' {n}개, 모두 {2 * n}개를 한 줄로 놓아요. 왼쪽에서부터 어느 자리까지 세어도 "
            f"닫는 괄호 수가 여는 괄호 수를 넘지 않도록(올바른 괄호 짝) 배열하는 방법은 몇 가지일까요?",
            f"{ans}가지", [f"{c}가지" for c in _pick_distractors(ans, [whole, whole // 2, ans + 2, ans * 2])],
            f"제약 없이 {2 * n}자리 중 여는 괄호 {n}자리를 고르면 {2 * n}C{n} = {whole}가지예요. 여기서 중간에 닫는 괄호가 "
            f"앞서는 '잘못된' 배열을 반사 원리로 빼면, 카탈란 수 C{n} = {whole}÷{n + 1} = {ans}가지만 남아요.",
            [(f"{whole}가지", "괄호 위치만 고른 전체 경우예요. '닫는 괄호가 앞서면 안 됨' 조건으로 걸러야 해요.")],
            detail="카탈란 수 Cn = (2n)!/(n!(n+1)!) = C(2n,n)/(n+1)은 올바른 괄호 짝, 격자 대각선 아래 경로, 이진트리 모양처럼 "
            "'중간에 규칙이 깨지면 안 되는' 배열을 세는 수예요. 전체에서 규칙을 어긴 경우를 반사 원리로 덜어내 구해요. 조합론의 스타 수열이에요.",
        )


def _fib(k):
    a, b = 1, 1
    for _ in range(k - 1):
        a, b = b, a + b
    return a


def gen_crt3():
    # 중국인의 나머지 정리: 세 서로소 수로 나눈 나머지가 정해진 가장 작은 자연수. (수와연산 난9)
    for rem_mod in [[(2, 3), (3, 5), (2, 7)], [(1, 3), (2, 4), (3, 5)], [(2, 5), (1, 6), (4, 7)], [(1, 2), (2, 3), (4, 5)]]:
        n, step = 0, 1
        for r, m in rem_mod:
            while n % m != r:
                n += step
            step *= m
        cond = ", ".join(f"{m}{_euro(str(m))} 나누면 {r}" for r, m in rem_mod)
        period = 1
        for _, m in rem_mod:
            period *= m
        add(
            "crt3", "NUMBER_OPERATION", 9, ["중국인의 나머지 정리", "조건 좁혀 가기"],
            f"{cond}{_iga(str(rem_mod[-1][0]))} 남는 가장 작은 자연수는 무엇일까요?",
            str(n), [str(c) for c in _pick_distractors(n, [n + period, n + rem_mod[0][1], n - rem_mod[0][1], n + 1])],
            f"세 나눗수 {', '.join(str(m) for _, m in rem_mod)}{_eun(str(rem_mod[-1][1]))} 서로소라, 조건을 만족하는 수는 "
            f"곱 {period}마다 되풀이돼요(중국인의 나머지 정리). 한 조건씩 좁혀 가면 그중 가장 작은 값은 {n}이에요.",
            [(str(n + period), "조건을 만족하는 다음 수예요. '가장 작은' 자연수를 찾아야 해요."),
             (str(n + rem_mod[0][1]), "한 조건만 맞추면 안 돼요. 세 조건을 동시에 만족하는 수를 찾으세요.")],
            detail="서로소인 여러 수로 나눈 나머지가 모두 정해지면, 그 조건을 동시에 만족하는 수는 '나눗수들의 곱'을 주기로 반드시 하나씩 존재해요"
            "(중국인의 나머지 정리). 한 조건씩 겹쳐 좁히면 가장 작은 답을 손으로 찾을 수 있어요. 나머지 세계의 연립방정식이에요.",
        )


def gen_fibsum():
    # 피보나치 부분합 F1+…+Fn = F(n+2)−1. 합과 한 항의 숨은 관계. (변화와관계 난9)
    for n in [6, 8, 10, 7]:
        terms = [_fib(k) for k in range(1, 6)]
        total = sum(_fib(k) for k in range(1, n + 1))
        fplus2 = _fib(n + 2)
        add(
            "fibsum", "CHANGE_RELATION", 9, ["피보나치", "합의 숨은 규칙"],
            f"{terms[0]}, {terms[1]}, {terms[2]}, {terms[3]}, {terms[4]}, … 처럼 앞의 두 수를 더해 만드는 "
            f"피보나치 수열이 있어요. 첫째 항부터 {n}째 항까지 모두 더하면 얼마일까요?",
            str(total), [str(c) for c in _pick_distractors(total, [fplus2, _fib(n + 1), total + 1, total - 1])],
            f"피보나치 수를 처음부터 더한 합에는 규칙이 있어요 — 첫째부터 n째까지의 합은 (n+2)째 항보다 딱 1 작아요. "
            f"{n + 2}째 항이 {fplus2}이니, 합은 {fplus2} − 1 = {total}이에요.",
            [(str(fplus2), "(n+2)째 항 자체가 아니라, 거기서 1을 뺀 값이 부분합이에요."),
             (str(_fib(n + 1)), "한 항 어긋났어요. 부분합은 (n+1)째가 아니라 (n+2)째 항에서 1을 뺀 값이에요.")],
            detail="피보나치 부분합 F1+F2+…+Fn = F(n+2)−1이에요. 각 항을 이웃 항의 차로 바꾸면(F(k) = F(k+2)−F(k+1)) 사슬처럼 지워져 "
            "맨 끝 F(n+2)−1만 남기 때문이에요(텔레스코핑). 수열의 합과 한 항 사이의 숨은 관계를 보는 문제예요.",
        )


def gen_diagcross():
    # 볼록 n각형 대각선의 내부 교점 수 = C(n,4) (어느 세 대각선도 한 점에서 만나지 않을 때). (도형과측정 난9)
    for n in [6, 7, 8, 5]:
        ans = comb(n, 4)
        diags = n * (n - 3) // 2
        add(
            "diagcross", "SHAPE_MEASUREMENT", 9, ["조합으로 세기", "대각선 교점"],
            f"볼록 {n}각형의 대각선을 모두 그었어요. 어느 세 대각선도 내부의 한 점에서 겹쳐 만나지 않는다면, "
            f"대각선끼리 다각형 내부에서 생기는 교점은 모두 몇 개일까요?",
            f"{ans}개", [f"{c}개" for c in _pick_distractors(ans, [diags, comb(n, 3), comb(n, 2), ans + 2])],
            f"내부 교점 하나는 꼭짓점 4개를 고르면 정확히 하나 정해져요 — 그 네 점이 만드는 사각형의 두 대각선이 만나는 점이에요. "
            f"그래서 교점 수는 꼭짓점 {n}개 중 4개를 고르는 조합 {n}C4 = {ans}개예요.",
            [(str(diags) + "개", "그건 대각선의 '개수'예요. 교점은 꼭짓점 4개를 고르는 조합으로 세요."),
             (f"{comb(n, 3)}개", "3개가 아니라 4개를 골라야 교점 하나가 정해져요(사각형의 두 대각선).")],
            figure={"type": "POLYGON", "params": {"n": n, "diagonals": 1}},
            detail="볼록 다각형에서 (어느 세 대각선도 한 점에 모이지 않으면) 내부 교점 하나는 꼭짓점 4개와 1:1로 대응해요 — 네 점이 만드는 사각형의 "
            "두 대각선 교점이 딱 하나이기 때문이에요. 그래서 교점 수 = C(n,4). 도형 세기를 조합으로 바꾸는 대표 문제예요.",
        )


def gen_partition():
    # 자연수의 분할 p(n): n을 자연수의 합으로 나타내기(순서 무시). (자료와가능성 난9)
    def part(k, mx):
        if k == 0:
            return 1
        return sum(part(k - j, j) for j in range(min(k, mx), 0, -1))
    for n in [5, 6, 7, 4]:
        ans = part(n, n)
        ordered = 2 ** (n - 1)  # 순서를 구별하면(합성) 2^(n-1) — 흔한 혼동
        add(
            "partition", "DATA_POSSIBILITY", 9, ["자연수의 분할", "순서 무시 세기"],
            f"{n}{_eul(str(n))} 1 이상의 자연수의 합으로 나타내는 방법은 모두 몇 가지일까요? "
            f"더하는 순서만 다른 것은 같은 것으로 봐요(예: 1+2와 2+1은 같음).",
            f"{ans}가지", [f"{c}가지" for c in _pick_distractors(ans, [ordered, ans + 1, ans - 1, n])],
            f"큰 수부터 차례로 놓아 빠짐없이·겹치지 않게 세요. {n}={n}부터 시작해 한 조각씩 잘게 쪼개 가면 모두 {ans}가지예요"
            f"(순서만 다른 건 한 가지로).",
            [(f"{ordered}가지", "그건 순서를 '구별'했을 때(예: 1+2와 2+1을 다르게)예요. 순서를 무시하면 훨씬 적어요."),
             (f"{ans + 1}가지", "빠뜨리거나 같은 걸 두 번 세기 쉬워요. 큰 수부터 체계적으로 나열해 확인하세요.")],
            detail="자연수 n을 순서 무시하고 자연수의 합으로 쪼개는 가짓수를 '분할수 p(n)'이라 해요. 순서를 구별하는 '합성'(2^(n−1)가지)과 달리, "
            "큰 조각부터 놓는 규칙으로 빠짐없이 세요. 딱 떨어지는 공식이 없어 체계적 나열이 핵심인 정수·조합의 고전이에요.",
        )


GENERATORS = [
    gen_crt3, gen_fibsum, gen_diagcross, gen_partition,
    gen_league, gen_twodigit, gen_tablediff, gen_unitprice,
    gen_rectperim, gen_interiorangle, gen_prismparts, gen_triangleangle,
    gen_avgbasic, gen_lineup, gen_mode, gen_simpleprob,
    gen_geosum, gen_dist3d, gen_necklace, gen_boxsurface, gen_passcode, gen_symaxis,
    gen_rectdiag, gen_electpair,
    gen_diagregions, gen_barchart, gen_chartavg,
    gen_foldcut, gen_knockout,
    gen_makesquare, gen_compose, gen_euler, gen_atleastprob,
    gen_sigma, gen_recur, gen_conevolume, gen_setpartition,
    gen_lasttwo, gen_cubesum, gen_pick, gen_catalan,
    gen_totient, gen_josephus, gen_spacediag, gen_derange, gen_prodsum,
    gen_quadseq, gen_polyhedron, gen_multiperm,
    gen_diophantine, gen_painted_cube_faces, gen_stars_bars,
    gen_transitivity, gen_repeating_pattern, gen_io_rule,
    gen_midpoint, gen_consecutive_middle, gen_multiple_condition,
    gen_choose_two, gen_data_read,
    gen_aliquot, gen_narcissistic,
    gen_mod_power, gen_lattice_paths, gen_coin_weighing,
    gen_number_split, gen_height_order, gen_position_count, gen_missing_addend,
    gen_lcm_together, gen_consecutive_sum, gen_pigeonhole, gen_missing_score,
    gen_units_cycle, gen_set_both, gen_round_trip,
    gen_handshake, gen_gauss_sum, gen_ratio_share, gen_fraction_whole,
    gen_tournament, gen_change_coins, gen_recipe_ratio, gen_square_area,
    gen_day_of_week, gen_frog_well, gen_odd_sum_square, gen_permutation,
    gen_reverse_diff, gen_leftover_crt, gen_square_numbers, gen_triangular,
    gen_power_of_two, gen_multiples_in_range, gen_common_mult_range, gen_weighted_average,
    gen_coin_flips, gen_dice_product, gen_salt_concentration, gen_percent_of,
    gen_gear_ratio, gen_seesaw, gen_divisor_sum, gen_clock_strikes,
    gen_ratio_three, gen_marble_transfer, gen_least_to_share, gen_tank_fill_drain,
    gen_leap_year_count, gen_average_needed, gen_stacking_cups, gen_number_line_jump,
    gen_double_discount, gen_max_product, gen_gift_exchange, gen_hanoi,
    gen_grid_area_hard,
    gen_median, gen_gcd_bags, gen_lcm_square, gen_collatz,
    gen_fibonacci, gen_prime_pick, gen_gcd_lcm_product,
    gen_mixture, gen_arithmetic_nth, gen_geometric_nth,
    gen_clock_gain, gen_book_reading, gen_train_pass_person,
    gen_reverse_operation, gen_similar_area_ratio, gen_handshake_reverse,
    gen_divisor_from_remainder, gen_diagonal_cells,
    gen_gcd_three, gen_sum_arithmetic_series, gen_tribonacci_stairs, gen_toggle_lights,
    gen_sum_product_pair, gen_time_duration, gen_squares_in_grid, gen_two_sum_diff,
    gen_cryptarithm, gen_chicken_rabbit, gen_excess_deficit, gen_age, gen_trees,
    gen_log, gen_meeting, gen_work, gen_train, gen_pyramid, gen_stairs, gen_grid,
    gen_cycle, gen_calendar, gen_average, gen_border, gen_candle, gen_mirror,
    # v2 확충 — 난이도1 바닥 + 신규 아이디어(다양성)
    gen_digit_cards, gen_sequence_simple, gen_matchsticks, gen_outfits,
    gen_broken_arithmetic, gen_cases, gen_custom_op, gen_sequence_advanced,
    gen_true_false,
    # v2.1 확충 — 도형 난2·자료 난3 빈칸 + 수 감각 다양성
    # (gen_handshake·gen_consecutive_sum·gen_pigeonhole는 v5 신규판이 같은 이름으로 재정의 →
    #  중복 등록 제거. 여기선 등록하지 않고 아래 v5 블록의 등록 하나만 남긴다.)
    gen_triangles_match, gen_dice_sum, gen_remainder,
    # v3 확충 — 유료(난4·5) 깊이: 색칠정육면체·약수개수·수 추리
    gen_painted_cube, gen_divisor_count, gen_number_riddle,
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
problems_en = [p for p in problems_en if p["id"] not in blocked]
if blocked:
    print(f"블록리스트 제외: {before - len(problems)}문항 (등록 {len(blocked)}건)")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"version": 1, "problems": problems}, ensure_ascii=False, indent=1), encoding="utf-8")

# 영어 뱅크 — add(en=...)로 변환된 계열만. 아직 변환 중이라 부분 뱅크.
OUT_EN.write_text(json.dumps({"version": 1, "lang": "en", "problems": problems_en}, ensure_ascii=False, indent=1), encoding="utf-8")
en_cov = len({p["groupId"].replace("g-gen-", "").rsplit("-", 1)[0] for p in problems_en})
print(f"영어 뱅크: {len(problems_en)}문항 · {en_cov}계열 → {OUT_EN.name}")

by_diff = {}
for p in problems:
    by_diff[p["difficulty"]] = by_diff.get(p["difficulty"], 0) + 1
print(f"생성 {stats['generated']}문항 / 기각 {stats['rejected']} / 그룹 {len(groups)}개")
print(f"난이도 분포: {dict(sorted(by_diff.items()))}")
print(f"→ {OUT}")
