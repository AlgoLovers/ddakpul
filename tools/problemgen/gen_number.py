"""수와 연산(NUMBER_OPERATION) 제너레이터 — 함수 1개 = 방법(family) 1개 = 문제 그룹.

실행 순서는 build.py의 GENERATORS 리스트가 정한다(rng 재현성). 여기선 정의만.
"""
from core import *  # noqa: F401,F403 — 공용 인프라(add·rng·헬퍼·상수)



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


# ── 35. 약수의 개수 (난4, 수와연산) ─────────────────────────────────────────
def gen_divisor_count():
    for num in [36, 48, 60, 72]:
        divisors = [d for d in range(1, num + 1) if num % d == 0]
        ans = len(divisors)
        # 검산: 소인수분해 지수 공식 (지수+1)들의 곱으로 개수를 독립 재계산해 완전열거와 대조
        m, formula, p = num, 1, 2
        while p * p <= m:
            e = 0
            while m % p == 0:
                m //= p
                e += 1
            formula *= e + 1
            p += 1
        if m > 1:
            formula *= 2
        assert formula == ans, f"divisor_count 검산 불일치: {ans} != {formula}"
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
            en={
                "statement": f"How many zeros are at the end of the number you get by multiplying all the numbers from 1 to {n} together?",
                "answer": _en_plural(z, "zero"),
                "distractors": [_en_plural(n // 5, "zero"), _en_plural(z + 1, "zero"), _en_plural(z - 1, "zero")],
                "explanation": f"A trailing zero comes from 10=2×5. The product has far more 2s than 5s, so 'how many times 5 is multiplied in' decides the number of zeros. Each multiple of 5 gives one 5 ({n}÷5={n // 5}), each multiple of 25 gives one more, … adding these up gives {z}.",
                "mistakes": [(_en_plural(n // 5, "zero"), "Counting only the multiples of 5 falls short. Multiples of 25 and 125 carry extra 5s.")],
                "detail": f"Precisely, (count of multiples of 5)+(count of multiples of 25)+(count of multiples of 125)+… = ⌊{n}/5⌋+⌊{n}/25⌋+… = {z}. 25=5×5 carries two 5s, so it is counted once more. The idea that '2s and 5s make 10s but 5 is the bottleneck' is a powerful tool used all across digit and divisor problems.",
            },
        )


# ── 64. 연속한 수의 합 (난3, 수와연산) ───────────────────────────────────────
def gen_consecutive_sum():
    for count, mid in [(3, 8), (5, 12), (3, 20), (5, 30)]:
        total = count * mid
        pattern = "□−1, □, □+1" if count == 3 else "□−2, □−1, □, □+1, □+2"
        # 검산: 가운데 mid 기준 연속 count개를 실제로 나열해 더한 값이 total인지 대조
        h = count // 2
        brute = sum(range(mid - h, mid + h + 1))
        assert mid - h >= 1 and brute == total, f"consecutive_sum 검산 불일치: {total} != {brute}"
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
        # 검산: 일의 자리만 exp번 실제로 곱해 가는 시뮬레이션으로 pow 결과와 대조
        sim = 1
        for _ in range(exp):
            sim = sim * base % 10
        assert sim == ans, f"units_cycle 검산 불일치: {ans} != {sim}"
        # 해설의 주기 논리 검산: 주기 안 위치의 값이 정답과 같아야
        assert cycle[(exp % period or period) - 1] == ans, f"units_cycle 주기 해설 불일치: {base}^{exp}"
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


# ── 71. 1부터 N까지의 합 — 가우스 (난4, 수와연산) ────────────────────────────
def gen_gauss_sum():
    for n in [10, 20, 50, 100]:
        ans = n * (n + 1) // 2
        # 검산: 1부터 n까지 실제로 다 더해 가우스 공식과 대조
        brute = sum(range(1, n + 1))
        assert brute == ans, f"gauss_sum 검산 불일치: {ans} != {brute}"
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
        # 검산: DP 완전탐색으로 최소 동전 수를 독립 계산해 그리디 결과와 대조
        dp = [0] + [amount + 1] * amount
        for v in range(1, amount + 1):
            for coin in coins:
                if coin <= v and dp[v - coin] + 1 < dp[v]:
                    dp[v] = dp[v - coin] + 1
        assert dp[amount] == cnt, f"change_coins 검산 불일치: {cnt} != {dp[amount]}"
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


# ── 80. 홀수의 합 = 제곱수 (난5, 수와연산) ───────────────────────────────────
def gen_odd_sum_square():
    for n in [5, 7, 10, 8]:
        last = 2 * n - 1
        ans = n * n
        # 검산: 홀수 1, 3, …, last를 실제로 나열해 개수와 합을 제곱 공식과 대조
        odds = list(range(1, last + 1, 2))
        assert len(odds) == n and sum(odds) == ans, f"odd_sum_square 검산 불일치: {ans} != {sum(odds)}"
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


# ── 82. 숫자 뒤집기 차 = 9의 배수 (난5, 수와연산) ────────────────────────────
def gen_reverse_diff():
    for tens, ones in [(7, 2), (8, 3), (5, 1), (9, 4)]:
        num = tens * 10 + ones
        rev = ones * 10 + tens
        ans = num - rev
        # 검산: 문자열 뒤집기로 rev를 독립 구성하고, 해설의 9×(자리 차) 공식과도 대조
        assert rev == int(str(num)[::-1]), f"reverse_diff 뒤집기 불일치: {num}"
        assert ans == 9 * (tens - ones), f"reverse_diff 검산 불일치: {ans} != {9 * (tens - ones)}"
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
        # 검산: 한 주기(1..period)를 완전열거 — 두 조건을 동시 만족하는 수는 정확히 하나(=ans)
        sols = [x for x in range(1, period + 1) if x % d1 == r1 and x % d2 == r2]
        assert sols == [ans], f"leftover_crt 검산 불일치: {ans} != {sols}"
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


# ── 87. 범위 안 배수 개수 (난4, 수와연산) ────────────────────────────────────
def gen_multiples_in_range():
    for limit, div in [(100, 7), (100, 3), (50, 4), (200, 9)]:
        ans = limit // div
        # 검산: 1..limit 완전열거로 배수를 직접 세어 몫 공식과 대조
        brute = sum(1 for x in range(1, limit + 1) if x % div == 0)
        assert brute == ans, f"multiples_in_range 검산 불일치: {ans} != {brute}"
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
        # 검산: 1..limit 완전열거 — 두 수로 모두 나누어떨어지는 수를 직접 세어 대조
        brute = sum(1 for x in range(1, limit + 1) if x % a == 0 and x % b == 0)
        assert brute == ans, f"common_mult_range 검산 불일치: {ans} != {brute}"
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


# ── 93. 백분율 — 전체의 일부 (난4, 수와연산) ────────────────────────────────
def gen_percent_of():
    for whole, pct in [(200, 15), (50, 30), (400, 25), (80, 60)]:
        assert (whole * pct) % 100 == 0
        ans = whole * pct // 100
        add(
            # 난이도 재조정(4→3, 2026-07 d1~5 스캔): 1단계 백분율 계산.
            "percentof", "NUMBER_OPERATION", 3, ["백분율", "전체의 일부"],
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


# ── 96. 약수의 합 (난5, 수와연산) ────────────────────────────────────────────
def gen_divisor_sum():
    for num in [12, 18, 28, 24]:
        divs = [x for x in range(1, num + 1) if num % x == 0]
        ans = sum(divs)
        # 검산: 시그마 공식 ∏(p^(e+1)−1)/(p−1)로 약수 합을 독립 재계산해 완전열거와 대조
        m, sig, p = num, 1, 2
        while p * p <= m:
            if m % p == 0:
                pk = 1
                while m % p == 0:
                    m //= p
                    pk *= p
                sig *= (pk * p - 1) // (p - 1)
            p += 1
        if m > 1:
            sig *= m + 1
        assert sig == ans, f"divisor_sum 검산 불일치: {ans} != {sig}"
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


# ── 102. 윤년 개수 (난5, 수와연산) ───────────────────────────────────────────
def gen_leap_year_count():
    for y1, y2 in [(2001, 2020), (1997, 2016), (2004, 2024), (2010, 2040)]:
        cnt = sum(1 for y in range(y1, y2 + 1) if (y % 4 == 0 and y % 100 != 0) or y % 400 == 0)
        # 검산: 구간 배수 산술(⌊/4⌋−⌊/100⌋+⌊/400⌋의 구간 차)로 해마다 판정과 독립 대조
        c4 = y2 // 4 - (y1 - 1) // 4
        c100 = y2 // 100 - (y1 - 1) // 100
        c400 = y2 // 400 - (y1 - 1) // 400
        assert c4 - c100 + c400 == cnt, f"leap_year_count 검산 불일치: {cnt} != {c4 - c100 + c400}"
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


# ── 107. 합이 일정할 때 곱 최대 (난5, 수와연산) ─────────────────────────────
def gen_max_product():
    for s in [10, 14, 20, 16]:
        a = s // 2
        b = s - a
        ans = a * b
        # 검산: 합이 s인 두 자연수 쌍을 완전열거해 곱의 최댓값과 대조
        brute = max(x * (s - x) for x in range(1, s))
        assert brute == ans, f"max_product 검산 불일치: {ans} != {brute}"
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


# ── 127. 나머지로 나누는 수 찾기 (난5, 수와연산) ────────────────────────────
def gen_divisor_from_remainder():
    for num, rem in [(100, 4), (58, 3), (86, 2), (75, 3)]:
        target = num - rem
        divs = [d for d in range(1, target + 1) if target % d == 0 and d > rem]
        cnt = len(divs)
        # 검산: 나누는 수 후보를 완전열거 — num을 실제로 나눠 나머지가 rem이 되는 수들과 대조
        brute = [d for d in range(rem + 1, num + 1) if num % d == rem]
        assert brute == divs and len(brute) == cnt, f"divisor_from_remainder 검산 불일치: {cnt} != {len(brute)}"
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


# ── 122. 책 읽고 남은 쪽 (난4, 수와연산) ─────────────────────────────────────
def gen_book_reading():
    for total, perday, days in [(300, 25, 8), (240, 30, 6), (500, 40, 10), (180, 20, 7)]:
        read = perday * days
        ans = total - read
        assert ans > 0
        add(
            # 난이도 재조정(4→2, 2026-07 d1~5 스캔): 300−25×8 — 발견 요소 0의 2단계 연산.
            "bookread", "NUMBER_OPERATION", 2, ["곱셈과 뺄셈", "남은 양"],
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


# ── 112. 최대공약수 — 똑같이 나눠담기 (난5, 수와연산) ────────────────────────
def gen_gcd_bags():
    for a, b, ia, ib in [(24, 36, "사과", "귤"), (18, 30, "빨간 구슬", "파란 구슬"), (40, 60, "사탕", "초콜릿"), (16, 24, "연필", "지우개")]:
        g = gcd(a, b)
        # 검산: 1..min(a,b) 완전열거로 공약수의 최댓값을 직접 찾아 gcd와 대조
        brute = max(k for k in range(1, min(a, b) + 1) if a % k == 0 and b % k == 0)
        assert brute == g, f"gcd_bags 검산 불일치: {g} != {brute}"
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


# ── 116. 소수 고르기 (난4, 수와연산) ─────────────────────────────────────────
def gen_prime_pick():
    def sd(x):
        for i in range(2, x):
            if x % i == 0:
                return i
        return x

    for prime, others in [(17, [15, 21, 27]), (23, [25, 33, 35]), (13, [9, 21, 25]), (29, [27, 33, 39])]:
        sm = sd(others[0])
        # 검산: 시도 나눗셈 완전열거 — 정답은 소수, 오답 셋은 모두 합성수여야
        assert prime > 1 and all(prime % i for i in range(2, prime)), f"prime_pick 검산 실패: {prime} 소수 아님"
        assert all(any(o % i == 0 for i in range(2, o)) for o in others), f"prime_pick 검산 실패: 합성수 아닌 오답 {others}"
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
        # 검산: gcd=g·lcm=lcm인 두 수 쌍을 완전탐색으로 실제 찾아, 모든 쌍의 곱이 ans인지 확인
        pairs = [(x, y) for x in range(1, lcm + 1) for y in range(x, lcm + 1)
                 if gcd(x, y) == g and x * y // gcd(x, y) == lcm]
        assert pairs and all(x * y == ans for x, y in pairs), f"gcd_lcm_product 검산 실패: g={g}, lcm={lcm}"
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


# ── 131. 세 수의 최대공약수 (난6, 수와연산) ─────────────────────────────────
def gen_gcd_three():
    for a, b, c in [(12, 18, 20), (24, 36, 20), (30, 45, 50), (16, 40, 28)]:
        ans = gcd(gcd(a, b), c)
        # 검산: 1..min 완전열거로 세 수 공통 약수의 최댓값을 직접 찾아 대조
        brute = max(d for d in range(1, min(a, b, c) + 1) if a % d == 0 and b % d == 0 and c % d == 0)
        assert brute == ans, f"gcd_three 검산 불일치: {ans} != {brute}"
        add(
            # 난이도 재조정(6→4, 2026-07 d6 감사): statement가 GCD 정의 제공, 소수 계산.
            "gcd3", "NUMBER_OPERATION", 4, ["최대공약수", "세 수"],
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


# ── 130. 거꾸로 생각하기 — 빠진 더하는 수 (난1, 수와연산) ────────────────────
def gen_missing_addend():
    for a, total in [(7, 15), (8, 20), (6, 13), (9, 16)]:
        ans = total - a
        # 검산: 0..total 완전열거 — □+a=total을 만족하는 수는 유일하게 ans여야
        sols = [x for x in range(total + 1) if x + a == total]
        assert sols == [ans], f"missing_addend 검산 불일치: {ans} != {sols}"
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
        # 검산: 가운데 수 후보를 완전열거 — 연속 세 수의 합이 total이 되는 수는 유일하게 mid
        sols = [m for m in range(1, total) if (m - 1) + m + (m + 1) == total]
        assert sols == [mid], f"consecutive_middle 검산 불일치: {mid} != {sols}"
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
        # 검산: limit 미만 완전열거로 k의 배수 최댓값을 직접 찾아 몫 공식과 대조
        brute = max(x for x in range(1, limit) if x % k == 0)
        assert brute == ans, f"multiple_condition 검산 불일치: {ans} != {brute}"
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


def gen_aliquot():
    # 진약수(자기 제외 약수)의 합 — 완전수/과잉수/부족수. 약수를 빠짐없이 찾는 사고.
    for n in [6, 28, 12, 8]:
        divs = [d for d in range(1, n) if n % d == 0]
        s = sum(divs)
        # 검산: 시그마 공식(소인수분해)으로 약수 전체 합을 독립 재계산 — 진약수 합은 σ(n)−n
        m, sig, p = n, 1, 2
        while p * p <= m:
            if m % p == 0:
                pk = 1
                while m % p == 0:
                    m //= p
                    pk *= p
                sig *= (pk * p - 1) // (p - 1)
            p += 1
        if m > 1:
            sig *= m + 1
        assert sig - n == s, f"aliquot 검산 불일치: {s} != {sig - n}"
        extra = f" 진약수 합이 자기 자신과 같으니 {n}{_eun(str(n))} '완전수'예요!" if s == n else ""
        extra_en = f" The proper divisors sum to the number itself, so {n} is a 'perfect number'!" if s == n else ""
        add(
            # 난이도 재조정(7→3, 2026-07 d7 감사): ≤28 약수 나열+덧셈 — 전략 없음.
            "aliquot", "NUMBER_OPERATION", 3, ["약수", "완전수"],
            f"어떤 수의 '진약수'는 자기 자신을 뺀 약수예요(예: 6의 진약수는 1, 2, 3). {n}의 진약수를 모두 더하면 얼마일까요?",
            str(s), [str(s + n), str(s + 1), str(s - 1)],
            f"{n}의 진약수는 {', '.join(map(str, divs))}이고, 모두 더하면 {'＋'.join(map(str, divs))}={s}예요.{extra}",
            [(str(s + n), "약수에 자기 자신까지 더하면 안 돼요. 진약수는 자기 자신을 빼요.")],
            detail="진약수(자기 제외 약수)의 합으로 수를 나눠요: 합＝자신이면 완전수(6, 28…), 합＞자신이면 과잉수, 합＜자신이면 부족수예요. 약수를 빠짐없이 찾으려면 1부터 짝을 지어(1과 n, 2와 n÷2…) 세는 게 확실해요.",
            en={
                "statement": f"The 'proper divisors' of a number are its divisors excluding itself (for example, the proper divisors of 6 are 1, 2, 3). What do you get when you add up all the proper divisors of {n}?",
                "answer": str(s),
                "distractors": [str(s + n), str(s + 1), str(s - 1)],
                "explanation": f"The proper divisors of {n} are {', '.join(map(str, divs))}, and adding them all gives {'+'.join(map(str, divs))}={s}.{extra_en}",
                "mistakes": [(str(s + n), "Don't add the number itself to its divisors. Proper divisors exclude the number itself.")],
                "detail": "You can sort numbers by the sum of their proper divisors (divisors excluding itself): if the sum equals the number it's a perfect number (6, 28…), if greater an abundant number, if less a deficient number. To find every divisor without missing any, pairing up from 1 (1 with n, 2 with n÷2…) is the reliable way.",
            },
        )


def gen_narcissistic():
    # 아름스트롱 수 — 각 자리 세제곱 합 = 자신. 자릿값과 거듭제곱을 함께 다루는 사고.
    narc = [153, 370, 371, 407]
    # 검산: 100~999 완전열거로 세 자리 아름스트롱 수를 전부 재발견 — 하드코딩 목록과 일치해야
    found = [x for x in range(100, 1000) if sum(int(c) ** 3 for c in str(x)) == x]
    assert found == narc, f"narcissistic 검산 불일치: {found} != {narc}"
    for i, t in enumerate(narc):
        ex = narc[(i + 1) % len(narc)]
        exd = [int(c) for c in str(ex)]
        td = [int(c) for c in str(t)]
        # 오답은 아름스트롱 수가 아니어야 한다(370·371처럼 이웃한 아름스트롱 수를 피한다).
        distractors = [str(x) for x in (t + 2, t - 2, t + 5, t - 5, t + 11) if x not in narc][:3]
        add(
            # 난이도 재조정(7→3, 2026-07 d7 감사): 규칙+예시를 statement가 다 줌 — 검산만.
            "narciss", "NUMBER_OPERATION", 3, ["자릿값", "세제곱 합"],
            f"각 자리 숫자를 세제곱해서 더하면 자기 자신이 되는 세 자리 수가 있어요. 예를 들어 {ex}＝{'＋'.join(f'{x}³' for x in exd)}＝{'＋'.join(str(x ** 3) for x in exd)}＝{ex} 처럼요. 이런 수가 몇 개 더 있는데, 다음 중 그런 수는 무엇일까요?",
            str(t), distractors,
            f"{t}의 각 자리 {', '.join(map(str, td))}을 세제곱해 더하면 {'＋'.join(str(x ** 3) for x in td)}＝{t}이라 자기 자신과 같아요. 나머지 보기는 세제곱 합이 자신과 달라요.",
            [(distractors[0], f"{distractors[0]}의 세제곱 합은 {sum(int(c) ** 3 for c in distractors[0])}(이)라 자기 자신과 달라요.")],
            detail="각 자리 숫자를 세제곱해 더한 값이 자기 자신과 같은 수를 '아름스트롱 수(수선화 수)'라고 해요. 세 자리에선 153, 370, 371, 407 넷뿐이에요. 자릿값과 거듭제곱을 함께 다루는 좋은 연습이에요.",
            en={
                "statement": f"There are three-digit numbers that equal the sum of the cubes of their own digits. For example, {ex} = {'+'.join(f'{x}³' for x in exd)} = {'+'.join(str(x ** 3) for x in exd)} = {ex}. There are a few more such numbers — which of the following is one?",
                "answer": str(t),
                "distractors": distractors,
                "explanation": f"Cubing the digits of {t}, namely {', '.join(map(str, td))}, and adding them gives {'+'.join(str(x ** 3) for x in td)}={t}, equal to the number itself. The other choices have a cube-sum different from themselves.",
                "mistakes": [(distractors[0], f"The cube-sum of {distractors[0]} is {sum(int(c) ** 3 for c in distractors[0])}, which differs from the number itself.")],
                "detail": "A number equal to the sum of the cubes of its digits is called an 'Armstrong number (narcissistic number)'. For three digits there are only four: 153, 370, 371, 407. It's good practice at handling place value and powers together.",
            },
        )


def gen_mod_power():
    # 거듭제곱의 나머지 = 나머지의 '주기'를 찾아 활용. 큰 지수도 규칙으로 손계산.
    for base, exp, m in [(2, 100, 7), (3, 50, 5), (7, 77, 10), (2, 64, 9)]:
        period = 1
        while pow(base, period, m) != 1:
            period += 1
        cyc = [pow(base, k, m) for k in range(1, period + 1)]
        pos = exp % period or period
        ans = cyc[pos - 1]
        # 검산: 곱셈을 exp번 실제 시뮬레이션한 나머지로 주기 논리와 대조
        sim = 1
        for _ in range(exp):
            sim = sim * base % m
        assert sim == ans, f"mod_power 검산 불일치: {ans} != {sim}"
        add(
            "modpow", "NUMBER_OPERATION", 8, ["거듭제곱", "나머지 주기"],
            f"{base}{_eul(str(base))} {exp}번 곱한 수(즉 {base}^{exp})를 {m}{_euro(str(m))} 나눈 나머지는 얼마일까요?",
            str(ans), _pick_distractors(ans, [(ans + 1) % m, (ans + 2) % m, (ans + m - 1) % m, (ans + 3) % m]),
            f"{base}을 거듭제곱하며 {m}으로 나눈 나머지는 {', '.join(map(str, cyc))} 가 반복돼요(주기 {period}). {exp}{_eul(str(exp))} {period}로 나눈 나머지는 {exp % period}(자리) → 주기의 {pos}번째 값 {ans}예요.",
            [(str((ans + 1) % m), "대충 어림하면 틀려요. 나머지의 반복 주기를 정확히 찾아 지수를 주기로 나눠요.")],
            detail="같은 수를 거듭 곱해 나눈 '나머지'는 반드시 일정하게 반복돼요(주기). 주기 길이로 지수를 나눈 나머지가 주기 안 몇 번째인지 알려줘요(0이면 주기의 끝). 큰 지수도 이 규칙이면 손으로 구할 수 있어요.",
            en={
                "statement": f"What is the remainder when {base} is multiplied by itself {exp} times (that is, {base}^{exp}) and divided by {m}?",
                "answer": str(ans),
                "distractors": [str(c) for c in _pick_distractors(ans, [(ans + 1) % m, (ans + 2) % m, (ans + m - 1) % m, (ans + 3) % m])],
                "explanation": f"The remainders of {base} raised to successive powers and divided by {m} repeat as {', '.join(map(str, cyc))} (period {period}). The remainder of {exp} divided by {period} is {exp % period} → the value at position {pos} in the cycle, {ans}.",
                "mistakes": [(str((ans + 1) % m), "Rough estimation gives the wrong answer. Find the exact repeating period of the remainders and divide the exponent by the period.")],
                "detail": "The 'remainder' of multiplying the same number over and over and dividing always repeats in a fixed cycle (period). The remainder of the exponent divided by the period length tells you which position within the cycle you land on (0 means the end of the cycle). Even huge exponents can be found by hand with this rule.",
            },
        )


def gen_lattice_paths():
    # 격자 최단 경로 수 = 오른쪽·위 이동을 섞는 조합.
    for w, h in [(3, 2), (2, 2), (3, 3), (4, 2)]:
        ans = comb(w + h, w)
        # 검산: 파스칼식 DP(각 꼭짓점까지 경로 수 누적)로 조합 공식과 다른 경로로 재계산
        dp = [[1] * (w + 1) for _ in range(h + 1)]
        for r in range(1, h + 1):
            for c in range(1, w + 1):
                dp[r][c] = dp[r - 1][c] + dp[r][c - 1]
        assert dp[h][w] == ans, f"lattice_paths 검산 불일치: {ans} != {dp[h][w]}"
        add(
            "lattice", "NUMBER_OPERATION", 8, ["조합", "최단 경로"],
            f"가로 {w}칸, 세로 {h}칸짜리 격자가 있어요. 왼쪽 아래 꼭짓점에서 오른쪽 위 꼭짓점까지 오른쪽 또는 위로만 갈 때, 서로 다른 최단 경로는 모두 몇 가지일까요?",
            f"{ans}가지", [f"{ans + 2}가지", f"{ans + 1}가지", f"{w * h}가지"],
            f"최단 경로는 오른쪽 {w}번, 위로 {h}번, 합쳐서 {w + h}번 움직이고 그 '순서'만 다른 거예요. {w + h}번 중 오른쪽 갈 {w}번을 고르는 조합이라 {w + h}C{w}={ans}가지예요.",
            [(f"{w * h}가지", "칸의 개수가 아니라, 이동 순서를 고르는 '조합'으로 세요.")],
            figure={"type": "GRID", "params": {"w": w, "h": h, "mark": 1}},
            detail="격자 최단 경로 수는 '오른쪽 R번·위 U번을 어떤 순서로 섞느냐'와 같아 조합 (R＋U)C(R)로 구해요. 각 경로가 R·U를 일렬로 배열한 것과 1:1 대응하기 때문이에요. 파스칼 삼각형으로 각 꼭짓점까지 경로 수를 채워 가도 돼요.",
            en={
                "statement": f"There is a grid {w} cells wide and {h} cells tall. Going only right or up from the bottom-left corner to the top-right corner, how many different shortest paths are there in all?",
                "answer": f"{ans} ways",
                "distractors": [f"{ans + 2} ways", f"{ans + 1} ways", f"{w * h} ways"],
                "explanation": f"A shortest path moves right {w} times and up {h} times, {w + h} moves in total, differing only in their 'order'. It's the number of ways to choose which {w} of the {w + h} moves go right, a combination, so C({w + h},{w})={ans} ways.",
                "mistakes": [(f"{w * h} ways", "Don't count the number of cells; count with a 'combination' that chooses the order of moves.")],
                "detail": "The number of shortest grid paths equals 'in what order you mix R rights and U ups', found by the combination C(R+U, R). This is because each path corresponds one-to-one with an arrangement of R's and U's in a row. You can also fill in the path count to each vertex using Pascal's triangle.",
            },
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
        # 검산: '세 무더기 최대한 균등 분할' 전략을 실제 시뮬레이션 — 최악의 무더기가 1개가 될 때까지
        sim, k = 0, n
        while k > 1:
            k = (k + 2) // 3
            sim += 1
        assert sim == w, f"coin_weighing 검산 불일치: {w} != {sim}"
        assert 3 ** w >= n > 3 ** (w - 1), f"coin_weighing 하한 검산 실패: n={n}"
        add(
            "weigh", "NUMBER_OPERATION", 8, ["3분할 전략", "최악의 경우"],
            f"똑같이 생긴 동전 {n}개 중에 딱 하나만 무거워요. 양팔 저울로 무게만 비교할 수 있을 때, 무거운 동전을 반드시 찾으려면 최소 몇 번 재야 할까요?",
            f"{w}번", [f"{c}번" for c in _pick_distractors(w, [w2, w + 1, w + 2, n, n - 1])],
            f"동전을 세 무더기로 나눠 두 무더기를 저울에 올리면 기울면 그쪽, 평형이면 안 올린 쪽 — 매번 후보가 3분의 1로 줄어요. {n}개는 3을 {w}번 곱해야 넘으니(3을 {w}번 곱하면 {3 ** w}≥{n}) {w}번이면 반드시 찾아요.",
            [(f"{w2}번", "두 무더기가 아니라 '세 무더기'로 나눠요. 저울은 한 번에 세 경우를 알려줘 3분의 1로 줄어요."), (f"{n - 1}번", "하나씩 다 재지 않아도 돼요. 3분할이면 훨씬 적어요.")],
            detail="양팔 저울은 한 번에 '왼쪽 무겁다/오른쪽 무겁다/평형' 세 가지를 알려줘 후보를 3분의 1로 줄여요. 그래서 최소 횟수는 '3을 몇 번 곱해야 개수를 넘느냐'(3^횟수 ≥ 개수)예요. 정보량을 최대로 담는 분할 전략의 대표 문제예요.",
            en={
                "statement": f"Among {n} identical-looking coins, exactly one is heavier. Using a balance scale that only compares weights, at least how many weighings do you need to be sure to find the heavy coin?",
                "answer": _en_plural(w, "weighing"),
                "distractors": [f"{c} weighings" for c in _pick_distractors(w, [w2, w + 1, w + 2, n, n - 1])],
                "explanation": f"Split the coins into three piles and put two of them on the scale: if it tips, the heavy one is on that side; if it balances, it's in the pile left off — each time the candidates shrink to a third. For {n} coins you must multiply 3 by itself {w} times to exceed them (3 multiplied {w} times is {3 ** w}≥{n}), so {w} weighings are guaranteed to find it.",
                "mistakes": [(f"{w2} weighings", "Split into 'three piles', not two. One weighing tells you three cases, shrinking to a third."), (f"{n - 1} weighings", "You don't have to weigh them one at a time. Splitting into three is far fewer.")],
                "detail": "A balance scale tells you three things at once — 'left heavier / right heavier / balanced' — shrinking the candidates to a third. So the minimum number of weighings is 'how many times you multiply 3 to exceed the count' (3^weighings ≥ count). It's a classic problem of a splitting strategy that packs in the most information.",
            },
        )


def gen_makesquare():
    # 완전제곱수로 만드는 최소 곱수 = 소인수분해에서 지수가 홀수인 소인수들의 곱. (수와연산 난6)
    # 난이도 재조정(난9→6, 2026-07 d9 감사): 진짜 정수론 통찰이나 수가 작고 표준 기법 — 심화 상단.
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
        # 검산: k=1부터 완전탐색 — n×k가 완전제곱수가 되는 최소 k가 res, 표시용 root도 정확해야
        brute = next(k for k in range(1, res + 1) if int((n * k) ** 0.5 + 0.5) ** 2 == n * k)
        assert brute == res, f"makesquare 검산 불일치: {res} != {brute}"
        assert root * root == n * res, f"makesquare 제곱근 표시 불일치: {root}² != {n * res}"
        add(
            "makesquare", "NUMBER_OPERATION", 6, ["소인수분해", "완전제곱수"],
            f"{n}에 자연수를 곱해서 어떤 수의 제곱(완전제곱수)이 되게 하려고 해요. 곱해야 하는 가장 작은 자연수는 무엇일까요?",
            str(res), [str(c) for c in _pick_distractors(res, [res + 1, res * 2, res + 2, res + 3])],
            f"{n} = {_prime_factor_str(n)}예요. 완전제곱수는 모든 소인수의 지수가 짝수여야 해요. 지수가 홀수인 소인수 "
            f"{', '.join(map(str, odd_primes))}를 하나씩 더 곱해 짝수로 맞추면 {n}×{res} = {n * res} = {root}²이에요.",
            [(str(res + 1), "필요 이상으로 곱했어요. 지수가 홀수인 소인수만 딱 한 번씩 더 곱하면 돼요.")],
            detail="완전제곱수는 소인수분해했을 때 모든 지수가 짝수인 수예요. 그래서 지수가 홀수인 소인수마다 하나씩 더 곱해 "
            "짝수로 만들면 가장 작은 곱수가 나와요. 소인수의 지수로 제곱수를 판별하는 정수론 문제예요.",
            en={
                "statement": f"You want to multiply {n} by a natural number to make it a perfect square (some number squared). What is the smallest natural number you must multiply by?",
                "answer": str(res),
                "distractors": [str(c) for c in _pick_distractors(res, [res + 1, res * 2, res + 2, res + 3])],
                "explanation": f"{n} = {_prime_factor_str(n)}. A perfect square must have every prime factor raised to an even exponent. "
                f"Multiplying in one more of each prime that has an odd exponent, {', '.join(map(str, odd_primes))}, evens them out: {n}×{res} = {n * res} = {root}².",
                "mistakes": [(str(res + 1), "You multiplied by more than needed. Multiply in each prime with an odd exponent exactly once more.")],
                "detail": "A perfect square is a number whose prime factorization has every exponent even. So multiplying in one more of each prime factor with an odd exponent makes them all even, giving the smallest multiplier. A number-theory problem that identifies squares by their prime exponents.",
            },
        )


def gen_sigma():
    # 진약수의 합(자기 제외). 완전수·부족수·과잉수 판별의 기초. (수와연산 난4)
    # 난이도 재조정(난10→4, 2026-07 d10 감사): 작은 수(12~28) 약수 나열·덧셈의
    # 약한 열거 — 비자명 정리 없음.
    for n in [28, 12, 24, 18]:
        divisors = [d for d in range(1, n) if n % d == 0]
        ans = sum(divisors)
        # 검산: 시그마 공식(소인수분해)으로 약수 전체 합을 독립 재계산 — 진약수 합은 σ(n)−n
        m, sig, p = n, 1, 2
        while p * p <= m:
            if m % p == 0:
                pk = 1
                while m % p == 0:
                    m //= p
                    pk *= p
                sig *= (pk * p - 1) // (p - 1)
            p += 1
        if m > 1:
            sig *= m + 1
        assert sig - n == ans, f"sigma 검산 불일치: {ans} != {sig - n}"
        div_str = " + ".join(map(str, divisors))
        note = " (자기 자신과 같아 '완전수'예요)" if ans == n else ""
        note_en = " (it equals the number itself, so it's a 'perfect number')" if ans == n else ""
        add(
            "sigma", "NUMBER_OPERATION", 4, ["약수", "진약수의 합"],
            f"{n}의 진약수(자기 자신 {n}{_eul(str(n))} 뺀 약수)를 모두 더하면 얼마일까요?",
            str(ans), [str(c) for c in _pick_distractors(ans, [ans + n, ans - 1, ans + 1, n])],
            f"{n}의 진약수는 {div_str}이에요. 모두 더하면 {ans}예요{note}.",
            [(str(ans + n), f"자기 자신 {n}{_eun(str(n))} 진약수가 아니에요(빼고 더해요).")],
            detail="자기 자신을 뺀 약수(진약수)의 합으로 수를 분류해요 — 합이 자신과 같으면 완전수(6, 28…), 작으면 부족수, "
            "크면 과잉수예요. 약수를 빠짐없이 찾아 더하는 정수론의 고전 주제예요.",
            en={
                "statement": f"What is the sum of all proper divisors of {n} (the divisors of {n} excluding {n} itself)?",
                "answer": str(ans),
                "distractors": [str(c) for c in _pick_distractors(ans, [ans + n, ans - 1, ans + 1, n])],
                "explanation": f"The proper divisors of {n} are {div_str}. Adding them all gives {ans}{note_en}.",
                "mistakes": [(str(ans + n), f"{n} itself is not a proper divisor (leave it out when adding).")],
                "detail": "We classify numbers by the sum of their divisors excluding themselves (the proper divisors) — if the sum equals the number it's a perfect number (6, 28…), if smaller a deficient number, if larger an abundant number. It's a classic number-theory topic of finding and adding every divisor.",
            },
        )


def gen_totient():
    # 오일러 피 함수 φ(n): n 이하에서 n과 서로소인 수의 개수 = n×∏(1−1/p). (수와연산 난5)
    # 난이도 재조정(난9→5, 2026-07 d9 감사): 작은 n의 서로소 열거/공식 대입 — sigma 동류.
    for n in [12, 20, 30, 36]:
        primes = sorted({p for p in range(2, n + 1) if n % p == 0 and all(p % q for q in range(2, p))})
        ans = sum(1 for k in range(1, n + 1) if gcd(k, n) == 1)
        # 검산: 오일러 곱 공식 φ(n)=n×∏(1−1/p)을 정수 연산으로 독립 재계산해 gcd 세기와 대조
        phi, m, p = n, n, 2
        while p * p <= m:
            if m % p == 0:
                phi = phi // p * (p - 1)
                while m % p == 0:
                    m //= p
            p += 1
        if m > 1:
            phi = phi // m * (m - 1)
        assert phi == ans, f"totient 검산 불일치: {ans} != {phi}"
        prod = "×".join([str(n)] + [f"(1−1/{p})" for p in primes])
        add(
            "totient", "NUMBER_OPERATION", 5, ["오일러 피 함수", "서로소 개수"],
            f"1부터 {n}까지의 자연수 중에서 {n}{_gwa(str(n))} 서로소인(공약수가 1뿐인) 수는 모두 몇 개일까요?",
            f"{ans}개", [f"{c}개" for c in _pick_distractors(ans, [n // 2, ans + 1, ans - 1, ans + 2])],
            f"{n}{_eun(str(n))} {_prime_factor_str(n)}이라, 각 소인수 {', '.join(map(str, primes))}의 배수를 걸러내요. "
            f"서로소 개수는 {prod} = {ans}개예요. (전체에서 소인수의 배수 비율만큼씩 덜어내는 곱셈이에요.)",
            [(f"{n // 2}개", "짝수만 빼면 안 돼요. 모든 소인수의 배수를 겹치지 않게 걸러야 해요."),
             (f"{ans + 1}개", "1은 모든 수와 서로소예요. 빠뜨리기 쉬우니 포함해서 세요.")],
            detail="오일러 피 함수 φ(n)은 'n 이하에서 n과 서로소인 수의 개수'예요. n의 서로 다른 소인수 p마다 (1−1/p)를 곱하면 구해져요 — "
            "전체 n개에서 각 소인수의 배수 비율을 곱으로 덜어내는 거예요(포함배제와 같은 원리). 약수·서로소를 다루는 정수론의 핵심 함수예요.",
            en={
                "statement": f"Among the natural numbers from 1 to {n}, how many are coprime to {n} (share only 1 as a common factor)?",
                "answer": f"{ans} numbers",
                "distractors": [f"{c} numbers" for c in _pick_distractors(ans, [n // 2, ans + 1, ans - 1, ans + 2])],
                "explanation": f"Since {n} = {_prime_factor_str(n)}, we sieve out the multiples of each prime factor {', '.join(map(str, primes))}. "
                f"The count of coprime numbers is {prod} = {ans}. (A product that removes the fraction of multiples of each prime factor from the whole.)",
                "mistakes": [(f"{n // 2} numbers", "Removing only the even numbers isn't enough. You must sieve out the multiples of every prime factor without double-counting."),
                             (f"{ans + 1} numbers", "1 is coprime to every number. It's easy to miss, so be sure to count it.")],
                "detail": "Euler's totient function φ(n) is 'the count of numbers up to n that are coprime to n'. For each distinct prime factor p of n, multiply by (1−1/p) — removing the fraction of multiples of each prime factor from the total n (the same idea as inclusion-exclusion). It's the core number-theory function for divisors and coprimality.",
            },
        )


def gen_lasttwo():
    # 큰 거듭제곱의 '끝 두 자리' = mod 100. 오일러 정리(base^φ(100)=base^40≡1)로 지수를 줄여 손계산. (수와연산 난10)
    for base, exp in [(3, 99), (7, 55), (13, 77), (17, 33)]:
        ans = pow(base, exp, 100)
        reduced = exp % 40 or 40
        # 검산: 곱셈을 exp번 실제 시뮬레이션(mod 100) + 해설의 오일러 축약 지수도 함께 대조
        sim = 1
        for _ in range(exp):
            sim = sim * base % 100
        assert sim == ans, f"lasttwo 검산 불일치: {ans} != {sim}"
        assert gcd(base, 100) == 1 and pow(base, reduced, 100) == ans, f"lasttwo 오일러 축약 불일치: {base}^{exp}"
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
            en={
                "statement": f"What are the last two digits of {base} multiplied {exp} times (that is, {base}^{exp})?",
                "answer": str(ans),
                "distractors": [str(c) for c in _pick_distractors(ans, [(ans + 1) % 100, (ans + 10) % 100, (ans * base) % 100, ans - 1])],
                "explanation": f"The last two digits are the remainder mod 100. {base} is coprime to 100, so by Euler's theorem {base}^40 ≡ 1 (mod 100) "
                f"(there are 40 numbers up to 100 coprime to 100, so φ(100)=40). So we reduce the exponent {exp} to its remainder {reduced} mod 40, and "
                f"{base}^{reduced} gives the last two digits {ans}.",
                "mistakes": [(str((ans + 1) % 100), "Don't look at just the last single digit — reduce the remainder mod 100 (two digits) using Euler's theorem.")],
                "detail": "The last two digits of a very large power are its remainder mod 100. If the base is coprime to 100, Euler's theorem gives base^40≡1 (mod 100), "
                "so you can reduce the exponent to its remainder mod 40 and compute by hand. It's a key number-theory tool using the cycle of powers in the world of remainders.",
            },
        )


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
        # 검산: 1..period 완전열거 — 세 조건을 동시 만족하는 수는 주기 안에 정확히 하나(=n)
        sols = [x for x in range(1, period + 1) if all(x % mm == rr for rr, mm in rem_mod)]
        assert sols == [n], f"crt3 검산 불일치: {n} != {sols}"
        # 해설의 전제(서로소) 검산: 세 나눗수는 쌍마다 서로소여야 주기가 곱이 된다
        assert all(gcd(rem_mod[i][1], rem_mod[j][1]) == 1 for i in range(3) for j in range(i + 1, 3)), f"crt3 서로소 전제 위반: {rem_mod}"
        conds_en = [f"{r} when divided by {m}" for r, m in rem_mod]
        cond_en = ", ".join(conds_en[:-1]) + ", and " + conds_en[-1]
        mods_en = ", ".join(str(m) for _, m in rem_mod)
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
            en={
                "statement": f"What is the smallest natural number that leaves {cond_en}?",
                "answer": str(n),
                "distractors": [str(c) for c in _pick_distractors(n, [n + period, n + rem_mod[0][1], n - rem_mod[0][1], n + 1])],
                "explanation": f"The three divisors {mods_en} are pairwise coprime, so numbers satisfying the conditions repeat every {period} (their product) — the Chinese Remainder Theorem. "
                f"Narrowing one condition at a time, the smallest such value is {n}.",
                "mistakes": [(str(n + period), "That's the next number satisfying the conditions. You need the smallest one."),
                             (str(n + rem_mod[0][1]), "Matching just one condition isn't enough. Find a number that satisfies all three at once.")],
                "detail": "When the remainders on division by several pairwise-coprime numbers are all fixed, exactly one number satisfying every condition exists in each period of 'the product of the divisors' (the Chinese Remainder Theorem). Narrowing condition by condition, you can find the smallest answer by hand. It's a system of simultaneous equations in the world of remainders.",
            },
        )


# ══ 천장 보충(2026-07, CEILING_SPECS §3.4·§3.5) + 중층 발견형 4종 신설 ══════════
# 아래 6 family는 전부 결정적 파라미터(rng 소비 없음) · 독립 브루트포스 검산 ·
# en= 짝(concepts 포함) 규약을 지킨다. GENERATORS 등록은 상위 세션이 말미 append로.


def gen_ternweight():
    # 양팔 저울과 추 1·3·9·27g — 물건 쪽에 놓을 추 찾기(균형 삼진법). (수와연산 난10)
    # CEILING_SPECS §3.4 구현. 발견형 근거: '물건 쪽 추=빼기' 전략은 힌트로만 스치고 어떤 추를
    # 어느 쪽에 놓는지는 온전히 탐색·발견해야 하며, 한쪽 접시 조합 나열로는 도달 불가능한 답이다.
    from itertools import product

    def choice_ko(ws):
        return f"{ws[0]}g 하나만" if len(ws) == 1 else prose_ko(ws)

    def prose_ko(ws):
        if len(ws) == 1:
            return f"{ws[0]}g"
        if len(ws) == 2:
            return f"{ws[0]}g과 {ws[1]}g"
        return ", ".join(f"{w}g" for w in ws)

    def choice_en(ws):
        return f"only the {ws[0]}g weight" if len(ws) == 1 else prose_en(ws)

    def prose_en(ws):
        if len(ws) == 1:
            return f"the {ws[0]}g weight"
        if len(ws) == 2:
            return f"{ws[0]}g and {ws[1]}g"
        return ", ".join(f"{w}g" for w in ws[:-1]) + f", and {ws[-1]}g"

    weights = (1, 3, 9, 27)
    none_ko = "없음(추를 물건 쪽에 안 놓아도 됨)"
    none_en = "none (no weight needs to go on the object's side)"
    for target, exp_obj, exp_opp, near_miss in [
        (5, (1, 3), (9,), (3,)),
        (14, (1, 3, 9), (27,), (3, 9)),
        (16, (3, 9), (1, 27), (9,)),
        (22, (9,), (1, 3, 27), (3, 9)),
    ]:
        # 독립 검산: 3⁴ 전수조사 — 균형 삼진법 표현의 유일성(−1=물건 쪽, +1=반대쪽, 0=안 씀)
        sols = [e for e in product([-1, 0, 1], repeat=4) if sum(ei * wi for ei, wi in zip(e, weights)) == target]
        assert len(sols) == 1, f"ternweight 표현 유일성 실패 N={target}"
        obj = tuple(w for e, w in zip(sols[0], weights) if e == -1)
        opp = tuple(w for e, w in zip(sols[0], weights) if e == 1)
        assert obj == exp_obj and opp == exp_opp, f"ternweight 스펙 불일치 N={target}: {obj}/{opp}"
        assert target + sum(obj) == sum(opp), f"ternweight 균형식 실패 N={target}"
        # 오답3('없음')의 근거 검산: 한쪽 접시 조합만으로는 target을 만들 수 없다
        assert all(sum(c * w for c, w in zip(bits, weights)) != target for bits in product([0, 1], repeat=4)), \
            f"ternweight 한쪽 접시로 가능 N={target}"
        obj_s, opp_s = sum(obj), sum(opp)
        add(
            "ternweight", "NUMBER_OPERATION", 10, ["삼진법 저울", "양쪽 접시 전략"],
            f"1g, 3g, 9g, 27g짜리 추가 하나씩 있어요. 양팔 저울의 두 접시 어느 쪽에든 추를 놓을 수 있어요 — "
            f"물건이 있는 접시에 추를 함께 놓아도 돼요. {target}g짜리 물건의 무게를 정확히 재려면, "
            f"물건과 같은 접시에 올려야 하는 추는 무엇일까요?",
            choice_ko(obj), [choice_ko(opp), choice_ko(near_miss), none_ko],
            f"① 추를 물건 반대쪽에만 놓아 보면 1, 3, 4(=1+3), 9, 10, 12, 13, 27, … 어떤 조합으로도 {target}g은 안 만들어져요. "
            f"② 발상의 전환 — 물건과 '같은' 접시에 놓은 추는 그만큼 무게를 빼는 셈이에요. "
            f"③ 반대쪽 접시에 {prose_ko(opp)}(합 {opp_s}g)을 올리면 물건 쪽이 {opp_s}−{target}={obj_s}g 모자라죠 — "
            f"그만큼을 물건 쪽 추 {prose_ko(obj)}(합 {obj_s}g)로 채워요. "
            f"④ 균형 검산: 물건 {target}g+{obj_s}g={opp_s}g — 양쪽이 똑같아요.",
            [(choice_ko(opp), "그 추들은 물건 '반대쪽' 접시에 놓는 거예요. 물건 쪽에 놓는 추는 무게를 '빼는' 역할을 해요."),
             (choice_ko(near_miss), "균형식을 세워 검산하세요. '물건+같은 쪽 추'와 '반대쪽 추'의 합이 정확히 같아야 해요."),
             (none_ko, f"추를 한쪽 접시에만 놓는 방법으로는 {target}g을 만들 수 없어요. 물건 쪽에도 추를 놓으면 '빼기'가 가능해져요.")],
            detail="추 하나마다 '반대쪽(더하기)/안 씀/물건 쪽(빼기)' 세 상태가 있어요. 1, 3, 9, 27은 이 세 상태의 조합으로 "
            "1g부터 40g까지 모든 무게를, 그것도 꼭 한 가지 방법으로 잴 수 있는 특별한 추예요 — 저울에 숨은 삼진법이죠. "
            "2g=3−1, 5g=9−3−1, 40g=27+9+3+1처럼 몇 개 더 실험해 보세요. 추를 한쪽에만 놓을 수 있다면 1, 2, 4, 8(이진법)이 같은 역할을 해요.",
            en={
                "concepts": ["Balanced ternary weights", "Two-pan strategy"],
                "statement": f"You have one weight each of 1g, 3g, 9g, and 27g. On a balance scale you may put weights on either pan — "
                             f"even on the same pan as the object. To weigh a {target}g object exactly, which weights must go on the same pan as the object?",
                "answer": choice_en(obj),
                "distractors": [choice_en(opp), choice_en(near_miss), none_en],
                "explanation": f"① Try weights only on the pan opposite the object: 1, 3, 4 (=1+3), 9, 10, 12, 13, 27, … — no combination makes {target}g. "
                               f"② The key discovery: a weight on the SAME pan as the object effectively subtracts its weight. "
                               f"③ Put {prose_en(opp)} (total {opp_s}g) on the opposite pan; the object's side is {opp_s}−{target}={obj_s}g short, "
                               f"so fill that with {prose_en(obj)} (total {obj_s}g) next to the object. "
                               f"④ Balance check: object {target}g + {obj_s}g = {opp_s}g — both sides equal.",
                "mistakes": [(choice_en(opp), "Those weights go on the pan OPPOSITE the object. Weights on the object's pan act as subtraction."),
                             (choice_en(near_miss), "Set up the balance equation to check: object + same-side weights must exactly equal the opposite-side weights."),
                             (none_en, f"No one-pan combination of these weights makes {target}g. Putting weights on the object's side unlocks 'subtraction'.")],
                "detail": "Each weight has three states — opposite pan (add), unused, or the object's pan (subtract). With 1, 3, 9, and 27, these three states weigh "
                          "every value from 1g to 40g, each in exactly one way: base three hiding inside a balance scale. Try a few more: 2g=3−1, 5g=9−3−1, "
                          "40g=27+9+3+1. If weights could go on one pan only, 1, 2, 4, 8 (base two) would play this role.",
            },
        )


def gen_threediv():
    # 약수가 정확히 3개인 수의 개수 — '소수의 제곱' 특성 역발견. (수와연산 난9)
    # CEILING_SPECS §3.5 구현. 발견형 근거: '소수의 제곱' 특성이 문제문에 없어 작은 사례에서
    # 귀납해야 하고, L≥200이면 전수 나열이 비현실적이라 특성 발견 없이는 셀 수 없다.
    from math import isqrt
    for limit, exp_ans, exp_sq, exp_mix in [(100, 4, 10, 6), (200, 6, 14, 9), (500, 8, 22, 12), (1000, 11, 31, 15)]:
        # 독립 검산 1: 체로 1..L 모든 수의 약수 개수를 전수 계산
        cnt = [0] * (limit + 1)
        for d in range(1, limit + 1):
            for m in range(d, limit + 1, d):
                cnt[m] += 1
        hits = [v for v in range(1, limit + 1) if cnt[v] == 3]
        ans = len(hits)
        # 독립 검산 2: '소수의 제곱' 특성으로 재계산 — 두 경로 일치 + 스펙 값 일치
        primes = [p for p in range(2, isqrt(limit) + 1) if all(p % q for q in range(2, p))]
        assert hits == [p * p for p in primes] and ans == exp_ans, f"threediv 검산 불일치 L={limit}"
        squares = isqrt(limit)  # 오답1: 제곱수 전부
        mix = ans + sum(1 for p in primes if p ** 3 <= limit)  # 오답2: 소수의 세제곱 혼입
        assert (squares, mix) == (exp_sq, exp_mix), f"threediv 오답 검산 불일치 L={limit}"
        plist = ", ".join(map(str, primes))
        sqlist = ", ".join(str(p * p) for p in primes)
        p_last = primes[-1]
        add(
            "threediv", "NUMBER_OPERATION", 9, ["약수의 개수", "소수의 제곱"],
            f"1부터 {limit}까지의 자연수 중에서 약수가 '정확히 3개'인 수는 모두 몇 개일까요?",
            f"{ans}개", [f"{squares}개", f"{mix}개", f"{ans - 1}개"],
            f"① 약수가 3개뿐인 수를 작은 것부터 실험으로 모아 봐요 — 4(1, 2, 4), 9(1, 3, 9), 25(1, 5, 25)… "
            f"② 공통점 발견: 모두 '소수의 제곱'이에요. 약수 개수가 홀수이려면 약수가 짝을 못 이루는 제곱수여야 하고, "
            f"그중 딱 3개(1, □, □²)가 되려면 1과 자기 자신 사이의 약수가 소수 하나뿐이어야 하거든요. "
            f"③ 이제 제곱이 {limit} 이하인 소수를 빠짐없이 세요: {plist} — 제곱하면 {sqlist}. 모두 {ans}개예요.",
            [(f"{squares}개", "제곱수라고 다 약수가 3개인 건 아니에요. 36의 약수는 9개죠. '소수'의 제곱만 정확히 3개예요."),
             (f"{mix}개", "소수의 세제곱(8, 27, …)은 약수가 4개(1, □, □², □³)예요. 3개가 아니에요."),
             (f"{ans - 1}개", f"경계 근처를 빠뜨렸어요 — {p_last}²={p_last * p_last}도 {limit} 이하라 세야 해요. "
                              f"제곱이 {limit}{_eul(limit)} 넘지 않는 소수를 끝까지 확인하세요.")],
            detail="찾은 수들의 약수를 직접 나열해 3개인지 검산해 보세요(예: 49→1, 7, 49). 일반화 — 약수가 정확히 5개인 수는 "
            "소수의 네제곱(16, 81, 625, …)이에요. 약수 개수는 소인수의 지수에 1을 더해 곱한 값이라, '개수 조건'에서 수의 "
            "생김새를 거꾸로 알아낼 수 있어요 — 개수를 세던 divcount의 정방향 계산을 뒤집은 눈이에요.",
            en={
                "concepts": ["Number of divisors", "Square of a prime"],
                "statement": f"Among the natural numbers from 1 to {limit}, how many have exactly 3 divisors?",
                "answer": _en_plural(ans, "number"),
                "distractors": [_en_plural(squares, "number"), _en_plural(mix, "number"), _en_plural(ans - 1, "number")],
                "explanation": f"① Collect numbers with exactly 3 divisors by experimenting from the smallest — 4 (1, 2, 4), 9 (1, 3, 9), 25 (1, 5, 25)… "
                               f"② Spot what they share: each is the square of a prime. An odd divisor count forces a perfect square (divisors normally pair up), "
                               f"and exactly 3 divisors (1, p, p²) means the only divisor between 1 and the number is a single prime p. "
                               f"③ So count every prime whose square is at most {limit}: {plist} — squaring gives {sqlist}. That's {ans} numbers.",
                "mistakes": [(_en_plural(squares, "number"), "Not every perfect square has 3 divisors — 36 has 9 of them. Only squares of PRIMES have exactly 3."),
                             (_en_plural(mix, "number"), "A prime cubed (8, 27, …) has 4 divisors (1, p, p², p³), not 3."),
                             (_en_plural(ans - 1, "number"), f"You missed the boundary — {p_last}²={p_last * p_last} is still at most {limit}. "
                                                             f"Count primes whose squares stay within {limit} to the very end.")],
                "detail": "Check by listing the divisors of each number you found (e.g., 49→1, 7, 49). Generalize — numbers with exactly 5 divisors are fourth powers "
                          "of primes (16, 81, 625, …). The divisor count is the product of (exponent+1) over the prime factorization, so a count condition reveals "
                          "the shape of a number in reverse — the divisor-counting you know, turned inside out.",
            },
        )


def gen_consecways():
    # 연속한 자연수 두 개 이상의 합으로 나타내는 방법의 수. (수와연산 난7)
    # 발견형 근거: 개수(k)별 분류·중단 조건(1+2+…+k>N)·홀짝 두 갈래 구조를 statement가 주지
    # 않고, 무작정 나열로는 '빠짐없음'(특히 64의 0가지)을 확신할 수 없어 구조 발견이 필수다.
    def run_str(a, b):
        return "+".join(str(x) for x in range(a, b + 1)) if b - a + 1 <= 4 else f"{a}+{a + 1}+…+{b}"

    for total, exp_ways, d_div, d_miss, d_odd in [
        (45, 5, 6, 4, 3),
        (81, 4, 5, 3, 2),
        (105, 7, 8, 6, 3),
        (64, 0, 7, 1, 2),
    ]:
        # 독립 검산 1: (시작, 길이) 완전탐색으로 모든 표현을 실제 수집
        ways = []
        for a in range(1, total):
            s, b = 0, a
            while s < total:
                s += b
                b += 1
            if s == total and b - a >= 2:
                ways.append((a, b - 1))
        # 독립 검산 2: 홀수 약수 공식과 대조 (방법 수 = 1 아닌 홀수 약수 개수)
        odd_divs = [d for d in range(3, total + 1, 2) if total % d == 0]
        assert len(ways) == exp_ways == len(odd_divs), f"consecways 검산 불일치 N={total}"
        assert d_div == sum(1 for d in range(1, total + 1) if total % d == 0), f"consecways 약수 오답 불일치 N={total}"
        kmax = 1
        while (kmax + 1) * (kmax + 2) // 2 <= total:
            kmax += 1
        if total != 64:
            assert d_odd == sum(1 for a, b in ways if (b - a + 1) % 2 == 1), f"consecways 홀수형 오답 불일치 N={total}"
            even_ex = next(run_str(a, b) for a, b in ways if (b - a + 1) % 2 == 0)
            chain = f"{total} = " + " = ".join(run_str(a, b) for a, b in ways)
            expl = (f"① '개수'를 기준으로 나눠 조사해요. 연속한 k개의 합은 (첫 수)×k+(0+1+…+(k−1))이니, "
                    f"{total}에서 0+1+…+(k−1)을 뺀 값이 k로 나누어떨어지면 성공이에요. "
                    f"② k=2, 3, …를 차례로 확인하되 1+2+…+k가 {total}{_eul(total)} 넘으면 멈춰요 — 마지막 후보는 k={kmax}예요. "
                    f"③ 성공한 표현: {chain} — 모두 {exp_ways}가지예요.")
            expl_en = (f"① Sort the search by 'how many terms'. A sum of k consecutive numbers is (first term)×k+(0+1+…+(k−1)), "
                       f"so subtract 0+1+…+(k−1) from {total} and check whether k divides what remains. "
                       f"② Try k=2, 3, … in turn, stopping once 1+2+…+k exceeds {total} — the last candidate is k={kmax}. "
                       f"③ The hits: {chain} — {exp_ways} ways in all.")
            answer_ko, answer_en = f"{exp_ways}가지", _en_plural(exp_ways, "way")
            mist = [(f"{d_div}가지", f"{total}의 약수 {d_div}개마다 방법이 하나씩 있다고 본 셈이에요. 방법과 짝을 이루는 건 1이 아닌 '홀수' 약수뿐이에요."),
                    (f"{d_miss}가지", f"한 가지를 빠뜨렸어요. 개수를 2개, 3개, …로 늘려 가며 1+2+…+개수가 {total}{_eul(total)} 넘을 때까지 빠짐없이 확인하세요."),
                    (f"{d_odd}가지", f"개수가 홀수인 경우(가운데 수가 딱 있는 경우)만 셌어요. {even_ex}처럼 개수가 짝수인 경우도 있어요.")]
            mist_en = [(_en_plural(d_div, "way"), f"That counts one way per divisor of {total} ({d_div} of them). Only the ODD divisors other than 1 pair up with a way."),
                       (_en_plural(d_miss, "way"), f"You missed one. Raise the term count 2, 3, … and check every case until 1+2+…+(count) exceeds {total}."),
                       (_en_plural(d_odd, "way"), f"You counted only odd-length runs (the ones with an exact middle term). Even-length runs like {even_ex} exist too.")]
            det = (f"방법의 수는 '1이 아닌 홀수 약수의 개수'와 정확히 같아요 — {total}의 1 아닌 홀수 약수는 "
                   f"{', '.join(map(str, odd_divs))}로 {exp_ways}개죠. 홀수 k개의 합은 '가운데 수×k'라 홀수 약수 k와 짝이 되고, "
                   f"짝수 k개의 합도 '(가운데 두 수의 합)×(k÷2)'에서 홀수 인수가 나와요. 그래서 홀수 약수가 1뿐인 2의 거듭제곱"
                   f"(2, 4, 8, 16, …)만 연속 합으로 나타낼 수 없는 특별한 수예요. 15=7+8=4+5+6=1+2+3+4+5로 규칙을 한 번 더 검산해 보세요.")
            det_en = (f"The number of ways exactly equals the count of odd divisors of {total} other than 1 — for {total} they are "
                      f"{', '.join(map(str, odd_divs))}, giving {exp_ways}. An odd-length run is 'middle term × k', pairing with the odd divisor k, "
                      f"and an even-length run gives an odd factor through '(sum of the middle two)×(k÷2)'. That's why powers of two (2, 4, 8, 16, …), "
                      f"whose only odd divisor is 1, are the only numbers that can't be written this way. Re-check the rule on 15=7+8=4+5+6=1+2+3+4+5.")
        else:
            expl = (f"① '개수'를 기준으로 나눠 조사해요. 연속한 k개의 합은 (첫 수)×k+(0+1+…+(k−1))이에요. "
                    f"② k=2부터 {kmax}까지(1+2+…+{kmax}={kmax * (kmax + 1) // 2}가 마지막 후보) 하나씩 확인하면 전부 어긋나요 — "
                    f"두 개짜리만 봐도 31+32=63, 32+33=65로 64를 건너뛰죠. "
                    f"③ 우연이 아니에요. 홀수 k개의 합은 '가운데 수×k'라 홀수 약수 k가 필요하고, 짝수 k개의 합은 "
                    f"'(가운데 두 수의 합)×(k÷2)'인데 가운데 두 수의 합이 홀수라 역시 홀수 약수가 필요해요. "
                    f"64=2×2×2×2×2×2에는 1 말고 홀수 약수가 없어서 단 한 가지도 없어요 — 0가지예요.")
            expl_en = (f"① Sort the search by 'how many terms': a sum of k consecutive numbers is (first term)×k+(0+1+…+(k−1)). "
                       f"② Checking k=2 through {kmax} (1+2+…+{kmax}={kmax * (kmax + 1) // 2} is the last candidate) fails every time — "
                       f"with two terms alone, 31+32=63 and 32+33=65 skip right past 64. "
                       f"③ It's no accident. An odd-length run is 'middle term × k', needing an odd divisor k, and an even-length run is "
                       f"'(sum of the middle two)×(k÷2)' where the middle two sum to an odd number — again an odd factor is needed. "
                       f"Since 64=2×2×2×2×2×2 has no odd divisor except 1, there is not a single way — 0 ways.")
            answer_ko, answer_en = "0가지(불가능)", "0 ways (impossible)"
            mist = [(f"{d_div}가지", "64의 약수 7개(1, 2, 4, …, 64)마다 방법이 있다고 본 셈이에요. 방법을 만드는 건 1이 아닌 '홀수' 약수뿐인데, 64에는 그런 약수가 없어요."),
                    (f"{d_miss}가지", "31+32=63, 32+33=65 — 어느 연속한 두 수의 합도 64가 되지 않아요. 연속한 두 수의 합은 언제나 홀수거든요."),
                    (f"{d_odd}가지", "예시의 9처럼 두어 가지쯤 있으리라는 어림이에요. 2의 거듭제곱은 연속 합으로 나타낼 수 없는 특별한 수예요.")]
            mist_en = [(_en_plural(d_div, "way"), "That counts one way per divisor of 64 (1, 2, 4, …, 64 — 7 of them). Only odd divisors other than 1 make ways, and 64 has none."),
                       (_en_plural(d_miss, "way"), "31+32=63 and 32+33=65 — no two consecutive numbers sum to 64. The sum of two consecutive numbers is always odd."),
                       (_en_plural(d_odd, "way"), "A guess that a couple of ways should exist, like for 9. Powers of two are the special numbers with no such representation.")]
            det = ("방법의 수는 '1이 아닌 홀수 약수의 개수'와 정확히 같아요 — 64는 그런 약수가 없어 0가지죠. 홀수 k개의 합은 "
                   "'가운데 수×k'라 홀수 약수 k와 짝이 되고, 짝수 k개의 합도 '(가운데 두 수의 합)×(k÷2)'에서 홀수 인수가 나와요. "
                   "그래서 2의 거듭제곱(2, 4, 8, 16, 32, 64, …)만 연속 합으로 나타낼 수 없어요. 15=7+8=4+5+6=1+2+3+4+5(홀수 약수 3, 5, 15)로 "
                   "규칙을 검산해 보세요.")
            det_en = ("The number of ways exactly equals the count of odd divisors other than 1 — 64 has none, hence 0 ways. An odd-length run is "
                      "'middle term × k', pairing with the odd divisor k, and an even-length run gives an odd factor through '(sum of the middle two)×(k÷2)'. "
                      "So the powers of two (2, 4, 8, 16, 32, 64, …) are the only numbers that can't be written this way. Check the rule on "
                      "15=7+8=4+5+6=1+2+3+4+5 (odd divisors 3, 5, 15).")
        add(
            "consecways", "NUMBER_OPERATION", 7, ["연속수의 합", "홀수 약수"],
            f"{total}{_eul(total)} 연속한 자연수 두 개 이상의 합으로 나타내려고 해요. 예를 들어 9는 4+5, 2+3+4의 "
            f"두 가지 방법으로 나타낼 수 있어요. {total}{_eun(total)} 모두 몇 가지 방법으로 나타낼 수 있을까요?",
            answer_ko, [m[0] for m in mist],
            expl, mist, detail=det,
            en={
                "concepts": ["Sums of consecutive numbers", "Odd divisors"],
                "statement": f"You want to write {total} as a sum of two or more consecutive natural numbers. For example, 9 can be "
                             f"written in exactly two ways: 4+5 and 2+3+4. In how many different ways can {total} be written like this?",
                "answer": answer_en,
                "distractors": [m[0] for m in mist_en],
                "explanation": expl_en,
                "mistakes": mist_en,
                "detail": det_en,
            },
        )


def gen_permsum():
    # 숫자 카드 네 장으로 만드는 네 자리 수 24개 '전부'의 합 — 자리별 대칭 세기. (수와연산 난7)
    # 발견형 근거: '각 숫자가 각 자리에 똑같이 6번씩 나타난다'는 대칭 전략을 statement가 주지
    # 않고, 24개를 직접 나열해 더하는 우회는 오래 걸리고 실수를 부르는 함정이다.
    from itertools import permutations
    for digits in [(1, 3, 5, 7), (2, 4, 6, 8), (1, 2, 3, 4), (3, 5, 7, 9)]:
        # 독립 검산 1: 24개 완전열거 합
        nums = sorted(int("".join(map(str, p))) for p in permutations(digits))
        total = sum(nums)
        ds = sum(digits)
        # 독립 검산 2·3: 대칭 공식·짝짓기 공식과 삼중 대조
        assert len(nums) == len(set(nums)) == 24 and total == ds * 6 * 1111, f"permsum 검산 불일치 {digits}"
        pair = nums[0] + nums[-1]
        assert total == pair * 12, f"permsum 짝짓기 검산 불일치 {digits}"
        d0, d1, d2, d3 = digits
        ds6 = ds * 6
        pairdig = digits[0] + digits[-1]
        cardtxt = ", ".join(map(str, digits))
        add(
            "permsum", "NUMBER_OPERATION", 7, ["자리값", "대칭으로 묶어 세기"],
            f"숫자 카드 {cardtxt}가 한 장씩 있어요. 네 장을 모두 한 번씩 써서 만들 수 있는 네 자리 수는 24개예요. "
            f"이 24개의 수를 '전부' 더하면 얼마일까요?",
            str(total), [str(ds * 1111), str(total // 2), str(total * 2)],
            f"① 24개를 하나하나 더하는 대신 '자리별'로 묶어 세요. ② 천의 자리에 {d0}{_iga(d0)} 오는 수는 남은 세 장을 "
            f"늘어놓는 3×2×1=6개예요 — 어느 숫자든, 어느 자리든 꼭 6번씩 나타나요. ③ 그래서 네 자리 각각의 숫자 합은 "
            f"({d0}+{d1}+{d2}+{d3})×6={ds6}으로 같고, 전체 합은 {ds6}×1000+{ds6}×100+{ds6}×10+{ds6}×1={ds6}×1111={total}이에요.",
            [(str(ds * 1111), "각 숫자가 각 자리에 '한 번씩'만 온다고 셌어요. 남은 세 장을 배열하는 3×2×1=6가지 각각에서 오니까 여섯 번씩이에요."),
             (str(total // 2), "각 자리 등장 횟수를 6번이 아니라 3번으로 셌어요. '남은 카드 3장'이 아니라 3장의 '배열 수'(6가지)만큼 나타나요."),
             (str(total * 2), f"가장 큰 수와 가장 작은 수처럼 합이 {pair}인 짝은 24÷2=12쌍이에요. 24쌍으로 세면 모든 수를 두 번씩 더한 셈이에요.")],
            detail=f"지름길 검산 — 가장 작은 {nums[0]}{_gwa(nums[0])} 가장 큰 {nums[-1]}처럼 '자리마다 합이 {pairdig}'인 두 수를 짝지으면 "
            f"24개가 합 {pair}인 12쌍으로 정확히 갈라져요: {pair}×12={total}. 전혀 다른 두 경로가 같은 값을 주면 답을 믿을 수 있죠. "
            f"이 '대칭으로 묶기'는 1부터 100까지 더한 가우스의 방법과 같은 눈이에요.",
            en={
                "concepts": ["Place value", "Counting by symmetry"],
                "statement": f"You have one card each of the digits {cardtxt}. Using all four cards once each, you can make 24 different "
                             f"four-digit numbers. What is the sum of ALL 24 of these numbers?",
                "answer": str(total),
                "distractors": [str(ds * 1111), str(total // 2), str(total * 2)],
                "explanation": f"① Instead of adding all 24 numbers one by one, count by place. ② The numbers with {d0} in the thousands place "
                               f"are the 3×2×1=6 arrangements of the other three cards — every digit lands in every place exactly 6 times. "
                               f"③ So each of the four places has digit total ({d0}+{d1}+{d2}+{d3})×6={ds6}, and the grand total is "
                               f"{ds6}×1000+{ds6}×100+{ds6}×10+{ds6}×1={ds6}×1111={total}.",
                "mistakes": [(str(ds * 1111), "You counted each digit landing in each place only once. It comes from all 3×2×1=6 arrangements of the remaining three cards — six times."),
                             (str(total // 2), "You counted 3 appearances per place instead of 6. It's not the '3 remaining cards' but the 6 ways to ARRANGE those 3 cards."),
                             (str(total * 2), f"Pairs like the smallest and largest sum to {pair}, but 24 numbers form 24÷2=12 pairs. Multiplying by 24 counts every number twice.")],
                "detail": f"Shortcut check — pair numbers whose digits sum to {pairdig} in every place, like the smallest {nums[0]} and the largest {nums[-1]}: "
                          f"the 24 numbers split into exactly 12 pairs, each summing to {pair}, and {pair}×12={total}. Two completely different routes giving "
                          f"the same value is how you learn to trust an answer. This 'pair up by symmetry' is the same eye as Gauss's trick for 1+…+100.",
            },
        )


def gen_magiccenter():
    # 3×3 마방진의 한가운데 칸 — 가운데를 지나는 네 줄 겹쳐 세기로 '가운데=평균' 강제성 발견. (수와연산 난6)
    # 발견형 근거: 배치 규칙도 '가운데=평균'도 statement에 없고(기준1), 시행착오 완성은 느린 데다
    # 완성해도 '반드시 그 수여야 하는' 근거를 주지 못한다 — 가로1·세로1·대각2 네 줄을 겹쳐 세는
    # 논법 발견이 결정적 경로다(기준2, josephus 선례). 수제 d5 '한 줄의 합' 문항의 발견형 윗층.
    from itertools import permutations
    losu = (2, 7, 6, 9, 5, 1, 4, 3, 8)  # 로 슈 방진 — 해설 검산용 완성 예시(등차 9수에 평행이동·배율)
    for nums, desc_ko, desc_en in [
        (tuple(range(1, 10)), "1부터 9까지의 수 아홉 개", "the numbers 1 through 9"),
        (tuple(range(3, 12)), "3부터 11까지의 수 아홉 개", "the numbers 3 through 11"),
        (tuple(range(2, 19, 2)), "2, 4, 6, …, 18의 짝수 아홉 개", "the nine even numbers 2, 4, 6, …, 18"),
        (tuple(range(7, 16)), "7부터 15까지의 수 아홉 개", "the numbers 7 through 15"),
    ]:
        total = sum(nums)
        line = total // 3
        assert line * 3 == total, f"magiccenter 줄합 실패 {nums}"
        # 독립 검산 1: 9! 전수조사 — 마방진은 정확히 8개(회전·반사)뿐이고 가운데는 한 값으로 강제된다
        centers, magic_cnt = set(), 0
        for p in permutations(nums):
            if p[0] + p[1] + p[2] != line or p[3] + p[4] + p[5] != line or p[6] + p[7] + p[8] != line:
                continue
            if p[0] + p[3] + p[6] != line or p[1] + p[4] + p[7] != line or p[2] + p[5] + p[8] != line:
                continue
            if p[0] + p[4] + p[8] != line or p[2] + p[4] + p[6] != line:
                continue
            centers.add(p[4])
            magic_cnt += 1
        assert magic_cnt == 8 and len(centers) == 1, f"magiccenter 전수조사 실패 {nums}"
        mid = centers.pop()
        # 독립 검산 2: 겹쳐 세기 공식(4×줄합=전체합+3×가운데)·중앙값과 대조
        assert 4 * line == total + 3 * mid and mid == sorted(nums)[4], f"magiccenter 공식 불일치 {nums}"
        # 해설의 완성 예시(로 슈의 등차 이미지)도 실제 마방진인지 검산
        step = nums[1] - nums[0]
        grid = [nums[0] + (v - 1) * step for v in losu]
        assert sorted(grid) == list(nums) and grid[4] == mid
        for i in range(3):
            assert sum(grid[3 * i:3 * i + 3]) == line and grid[i] + grid[i + 3] + grid[i + 6] == line
        assert grid[0] + grid[4] + grid[8] == line and grid[2] + grid[4] + grid[6] == line
        rows = f"[{grid[0]} {grid[1]} {grid[2]}] [{grid[3]} {grid[4]} {grid[5]}] [{grid[6]} {grid[7]} {grid[8]}]"
        add(
            "magiccenter", "NUMBER_OPERATION", 6, ["마방진", "겹쳐 세기"],
            f"{desc_ko}를 한 번씩 모두 써서 3×3 표의 아홉 칸을 채우려고 해요. 가로 세 줄, 세로 세 줄, 대각선 두 줄의 합이 "
            f"전부 같아야 해요(마방진). 이때 '한가운데 칸'에 반드시 들어가야 하는 수는 무엇일까요?",
            str(mid), [str(line), str(max(nums)), str(min(nums))],
            f"① 아홉 수의 합은 {total}이고, 가로 세 줄이 아홉 칸을 정확히 나눠 가지니 한 줄의 합은 {total}÷3={line}이에요. "
            f"② 한가운데 칸을 지나는 줄을 세어 봐요 — 가로 1줄, 세로 1줄, 대각선 2줄, 모두 4줄이에요(이렇게 많은 줄에 걸리는 칸은 가운데뿐이죠). "
            f"③ 이 네 줄을 전부 더하면 {line}×4={4 * line}인데, 여기엔 아홉 수 전체({total})에 가운데 수만 세 번 '더' 들어 있어요. "
            f"④ 그래서 가운데 수는 ({4 * line}−{total})÷3={mid} — 아홉 수의 한가운데 값(평균)이에요.",
            [(str(line), f"{line}{_eun(line)} 한 '줄'의 합이에요({total}÷3). 문제가 물은 건 한가운데 '칸'에 들어갈 수예요."),
             (str(max(nums)), "가장 큰 수는 한가운데에 못 와요. 가운데 칸은 네 줄에 동시에 쓰이는 자리라, 크기가 한가운데인 수(평균)여야 네 줄을 모두 맞출 수 있어요."),
             (str(min(nums)), "가장 작은 수도 마찬가지예요 — 가운데 칸은 가로·세로·대각선 네 줄에 모두 포함되는 특별한 자리라 아홉 수의 평균이 와야 해요.")],
            detail=f"'가운데 칸만 4줄에 걸린다'는 관찰이 심장이에요(모서리 칸은 3줄, 변의 가운데 칸은 2줄). 완성 예시로 검산해 보세요: "
            f"{rows} — 여덟 줄의 합이 전부 {line}이에요. 일반화 — 아홉 수가 같은 간격으로 커지기만 하면 가운데엔 언제나 "
            f"'다섯 번째 수(평균)'가 와요. 같은 겹쳐 세기 논법으로 네 모서리에는 어떤 수들이 올 수 있는지도 탐구해 보세요.",
            en={
                "concepts": ["Magic square", "Overlap counting"],
                "statement": f"You want to fill the nine cells of a 3×3 grid with {desc_en}, each used exactly once, so that the three rows, "
                             f"the three columns, and both diagonals all have the same sum (a magic square). What number MUST go in the very center cell?",
                "answer": str(mid),
                "distractors": [str(line), str(max(nums)), str(min(nums))],
                "explanation": f"① The nine numbers sum to {total}, and the three rows split the nine cells exactly, so each line sums to {total}÷3={line}. "
                               f"② Count the lines through the center cell — 1 row, 1 column, 2 diagonals: 4 lines (no other cell lies on that many). "
                               f"③ Adding those four lines gives {line}×4={4 * line}, which contains all nine numbers ({total}) plus the center counted 3 extra times. "
                               f"④ So the center is ({4 * line}−{total})÷3={mid} — the middle value (the average) of the nine numbers.",
                "mistakes": [(str(line), f"{line} is the sum of one LINE ({total}÷3). The question asks for the number in the center CELL."),
                             (str(max(nums)), "The largest number can't sit in the center. The center cell serves four lines at once, so it must be the middle-sized number (the average)."),
                             (str(min(nums)), "Same for the smallest — the center cell belongs to four lines (row, column, both diagonals), so the average of the nine numbers must go there.")],
                "detail": f"The heart of it: only the center lies on 4 lines (corners lie on 3, edge-centers on 2). Check with a finished example: "
                          f"{rows} — all eight lines sum to {line}. Generalize — whenever the nine numbers grow by equal steps, the center is always "
                          f"the fifth (average) value. With the same overlap-counting argument, explore which numbers can occupy the four corners.",
            },
        )


def gen_repunit():
    # 1을 이어 쓴 수의 제곱 — 자릿수 합이 정확히 n². (수와연산 난5)
    # 발견형 근거: 계산 방법을 statement가 주지 않고, 1이 6~8개인 수의 직접 곱셈은 실수 없이는
    # 비현실적이라 11×11=121, 111×111=12321 작은 사례에서 피라미드 패턴을 발견해야 한다(n=5가 진입 문항).
    for n in [5, 6, 7, 8]:
        rep = int("1" * n)
        # 독립 검산: 실제 큰 수 곱셈으로 자릿수 합·회문 구조·자리 개수를 모두 확인
        sq = rep * rep
        dsum = sum(int(c) for c in str(sq))
        updown = "".join(str(k) for k in range(1, n + 1)) + "".join(str(k) for k in range(n - 1, 0, -1))
        assert str(sq) == updown and dsum == n * n and len(str(sq)) == 2 * n - 1, f"repunit 검산 불일치 n={n}"
        add(
            "repunit", "NUMBER_OPERATION", 5, ["곱셈 패턴", "작은 사례로 규칙 찾기"],
            f"1을 {n}개 이어 쓴 수 {rep}{_eul(rep)} 자기 자신과 곱해요({rep}×{rep}). "
            f"그 결과의 각 자리 숫자를 모두 더하면 얼마일까요?",
            str(dsum), [str(n * (n + 1) // 2), str(2 * n - 1), str(n)],
            f"① 작은 사례부터 실험해요: 11×11=121, 111×111=12321, 1111×1111=1234321. "
            f"② 패턴 발견 — 1이 n개면 결과는 1부터 n까지 올라갔다가 다시 1로 내려오는 수예요. 그래서 {rep}×{rep}={sq}. "
            f"③ 왜 그럴까요? 세로셈으로 보면 {rep}{_eul(rep)} 한 칸씩 밀며 {n}번 더하는 셈이라, 가운데 자리엔 1이 {n}개, "
            f"양옆으로 갈수록 하나씩 적게 겹쳐요(1이 9개까지는 받아올림이 없어요). "
            f"④ 자릿수 합은 (1+2+…+{n - 1})을 두 번 더하고 꼭대기 {n}{_eul(n)} 더한 {n * (n - 1)}+{n}={dsum} — 신기하게도 {n}×{n}이에요.",
            [(str(n * (n + 1) // 2), f"올라가는 쪽 1+2+…+{n}만 더했어요. 꼭대기 {n}{_eul(n)} 지나 다시 1까지 '내려오는' 쪽도 더해야 해요."),
             (str(2 * n - 1), f"그건 결과의 자리 '개수'({2 * n - 1}자리)예요. 문제는 자리 숫자들의 '합'을 물었어요."),
             (str(n), f"그건 곱하기 전 수({rep})의 자릿수 합이에요. 제곱한 결과의 자릿수 합을 구해야 해요.")],
            detail=f"이 피라미드 패턴은 1이 9개일 때(111111111×111111111=12345678987654321)까지 이어지고, 10개부터는 받아올림이 생겨 "
            f"무너져요 — 규칙을 발견하면 '어디까지 통하는지'도 꼭 따져 보세요. 자릿수 합이 {n}×{n}인 건 겹침 횟수가 1, 2, …, {n}, …, 2, 1로 "
            f"늘었다 줄기 때문인데, 홀수를 차례로 더하면 제곱수가 되는 규칙(1+3+5+…)과 형제 같은 구조랍니다.",
            en={
                "concepts": ["Multiplication patterns", "Patterns from small cases"],
                "statement": f"Take {rep}, the number written with {n} ones in a row, and multiply it by itself ({rep}×{rep}). "
                             f"What is the sum of all the digits of the result?",
                "answer": str(dsum),
                "distractors": [str(n * (n + 1) // 2), str(2 * n - 1), str(n)],
                "explanation": f"① Experiment small: 11×11=121, 111×111=12321, 1111×1111=1234321. "
                               f"② The pattern — with n ones, the product climbs 1, 2, …, n and steps back down to 1. So {rep}×{rep}={sq}. "
                               f"③ Why: in column multiplication you add {rep} shifted over {n} times, so the middle column stacks {n} ones and "
                               f"each column outward stacks one fewer (no carrying up to nine ones). "
                               f"④ The digit sum is (1+2+…+{n - 1}) twice plus the peak {n}: {n * (n - 1)}+{n}={dsum} — amazingly, exactly {n}×{n}.",
                "mistakes": [(str(n * (n + 1) // 2), f"You added only the climb 1+2+…+{n}. The digits come back down past the peak {n} to 1 — add the way down too."),
                             (str(2 * n - 1), f"That's the NUMBER of digits ({2 * n - 1} digits). The question asks for the SUM of the digits."),
                             (str(n), f"That's the digit sum of {rep} before squaring. You need the digit sum of the square.")],
                "detail": f"The pyramid pattern survives up to nine ones (111111111×111111111=12345678987654321) and breaks at ten, when carrying begins — "
                          f"after finding a rule, always ask how far it holds. The digit sum being {n}×{n} comes from the overlap counts rising and falling "
                          f"1, 2, …, {n}, …, 2, 1 — a sibling of the rule that adding odd numbers in order (1+3+5+…) builds perfect squares.",
            },
        )
