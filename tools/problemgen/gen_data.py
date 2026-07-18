"""자료와 가능성(DATA_POSSIBILITY) 제너레이터 — 함수 1개 = 방법(family) 1개 = 문제 그룹.

실행 순서는 build.py의 GENERATORS 리스트가 정한다(rng 재현성). 여기선 정의만.
"""
from core import *  # noqa: F401,F403 — 공용 인프라(add·rng·헬퍼·상수)



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


# ── 30. 주사위 두 개 눈의 합 경우의 수 (난3, 자료와가능성) ────────────────────
def gen_dice_sum():
    from itertools import product
    for k in [5, 7, 9, 8]:
        cnt = sum(1 for a, b in product(range(1, 7), repeat=2) if a + b == k)
        unordered = sum(1 for a in range(1, 7) for b in range(a, 7) if a + b == k)
        ex_a = max(1, k - 6)
        ex_b = k - ex_a
        # 검산: 완전열거(cnt)를 닫힌 공식(6−|k−7|)·비순서 세기와 교차 확인
        assert cnt == 6 - abs(k - 7), "dicesum 검산 실패: 합 경우 수가 공식과 불일치"
        assert unordered * 2 - (1 if k % 2 == 0 and 1 <= k // 2 <= 6 else 0) == cnt, "dicesum 검산 실패: 순서 유무 세기 불일치"
        assert 1 <= ex_a <= 6 and 1 <= ex_b <= 6 and ex_a + ex_b == k, "dicesum 검산 실패: 예시 짝"
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
        parity_en = "odd" if total % 2 == 1 else "even"
        other_en = "even" if total % 2 == 1 else "odd"
        add(
            "parity", "DATA_POSSIBILITY", 7, ["불변량", "홀짝 보존"],
            f"칠판에 1부터 {n}까지의 수가 적혀 있어요. 매번 두 수를 지우고 대신 두 수의 차를 적어요. 이걸 계속 반복하면 마지막에 수 하나만 남아요. 이 수는 홀수일까요, 짝수일까요?",
            parity, [other, "지우는 순서에 따라 달라져요", "항상 0이에요"],
            f"두 수 a, b를 지우고 |a−b|를 적으면 전체 합은 (a+b)−|a−b|, 즉 작은 수의 2배만큼 줄어요 — 항상 짝수만큼! 그래서 '전체 합의 홀짝'은 절대 변하지 않아요(불변량). 1부터 {n}까지의 합은 {total}({parity})이니 마지막 한 수도 {parity}예요.",
            [("지우는 순서에 따라 달라져요", "신기하게도 순서와 상관없이 항상 같아요 — 처음 합의 홀짝으로 정해지는 불변량이에요.")],
            detail=f"두 수 a, b를 지우고 |a−b|를 적어도 전체 합의 '홀짝'은 안 변해요(a+b와 |a−b|는 홀짝이 같으니까). 그래서 마지막 수의 홀짝은 처음 1부터 {n}까지 합의 홀짝으로 이미 정해져 있어요. 이렇게 '과정이 변해도 안 변하는 값(불변량)'을 찾으면, 모든 경우를 따라가지 않고도 결과를 알 수 있어요 — 고학년 수학의 강력한 무기예요.",
            en={
                "statement": f"The numbers from 1 to {n} are written on a board. Each turn you erase two numbers and write their difference instead. Repeating this until only one number remains, is that number odd or even?",
                "answer": parity_en,
                "distractors": [other_en, "It depends on the order you erase them", "It's always 0"],
                "explanation": f"When you erase two numbers a, b and write |a−b|, the total sum drops by (a+b)−|a−b|, which is twice the smaller number — always an even amount! So the 'parity of the total sum' never changes (an invariant). The sum from 1 to {n} is {total} ({parity_en}), so the last remaining number is also {parity_en}.",
                "mistakes": [("It depends on the order you erase them", "Surprisingly it's always the same regardless of order — it's an invariant fixed by the parity of the starting sum.")],
                "detail": f"Even after you erase a, b and write |a−b|, the 'parity' of the total sum does not change (a+b and |a−b| have the same parity). So the parity of the last number is already fixed by the parity of the sum from 1 to {n}. Finding a 'value that stays unchanged even as the process changes (an invariant)' lets you know the result without following every case — a powerful weapon in higher math.",
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


# ── 61. 수 가르기 경우의 수 (난1, 자료와가능성) — 빠짐없이 세기 ────────────────
def gen_number_split():
    for total in [5, 6, 7, 8]:
        ans = total // 2  # 두 접시 구분 안 함, 각 1개 이상
        # 검산: 가르기 완전열거 — 순서 없는 (a, total−a) 짝을 실제로 나열해 세기
        chk_cnt = sum(1 for a in range(1, total) if a <= total - a)
        assert chk_cnt == ans, "numsplit 검산 실패"
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
    # 검산: 키 배정 완전열거 — 힌트 3개(p1>p2, p0>p1, p2>p3)를 만족하는 배정은 유일하고 p0가 1등
    from itertools import permutations
    valid = [h for h in permutations(range(4)) if h[1] > h[2] and h[0] > h[1] and h[2] > h[3]]
    assert len(valid) == 1 and valid[0][0] == max(valid[0]), "htorder 검산 실패"
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


# ── 65. 비둘기집 원리 (난5, 자료와가능성) ────────────────────────────────────
def gen_pigeonhole():
    for names in [["빨강", "파랑", "노랑"], ["검정", "흰색"], ["빨강", "파랑", "노랑", "초록"], ["빨강", "노랑", "초록"]]:
        colors = len(names)
        ans = colors + 1
        # 검산: 뽑기 결과 완전열거 — colors짝은 전부 다른 색이 가능(최악 반례), ans짝은 어떤 경우에도 같은 색 짝 존재
        from itertools import product
        assert any(len(set(pick)) == colors for pick in product(range(colors), repeat=colors)), "pigeon 검산 실패: 최악 반례 없음"
        assert all(len(set(pick)) < len(pick) for pick in product(range(colors), repeat=ans)), "pigeon 검산 실패: 중복 미보장"
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
        # 검산: 0~100점 전 후보 완전탐색 — 평균을 딱 맞추는 나머지 점수는 유일
        sols = [x for x in range(0, 101) if sum(known) + x == subjects * avg]
        assert len(known) == subjects - 1 and sols == [missing], "missscore 검산 실패"
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


# ── 70. 악수/리그전 = C(n,2) (난5, 자료와가능성) ─────────────────────────────
def gen_handshake():
    for n in [5, 6, 8, 10]:
        ans = n * (n - 1) // 2
        # 검산: 두 사람 짝 완전열거
        from itertools import combinations
        assert sum(1 for _ in combinations(range(n), 2)) == ans, "handshake 검산 실패"
        add(
            # 난이도 재조정(5→4, 2026-07 d1~5 스캔): league(d3)와 같은 C(n,2) 계열 — 층 정렬.
            "handshake", "DATA_POSSIBILITY", 4, ["경우의 수", "두 번 세고 나누기"],
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


# ── 74. 토너먼트 경기 수 (난5, 자료와가능성) ─────────────────────────────────
def gen_tournament():
    for n in [8, 16, 32, 10]:
        ans = n - 1
        # 검산: 경기 시뮬레이션 — 두 명이 겨뤄 패자만 탈락, 우승자 혼자 남을 때까지 실제로 세기
        alive = list(range(n))
        games = 0
        while len(alive) > 1:
            winner, _loser = alive.pop(), alive.pop()  # 한 경기 = 탈락 1명
            alive.append(winner)
            games += 1
        assert games == ans and len(alive) == 1, "tourney 검산 실패"
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


# ── 81. 순열 — 한 줄로 세우기 = n! (난5, 자료와가능성) ───────────────────────
def gen_permutation():
    for n, ctx in [(4, "책"), (5, "인형"), (6, "색연필"), (4, "컵")]:
        ans = factorial(n)
        # 검산: 줄 세우기 완전열거
        from itertools import permutations
        assert sum(1 for _ in permutations(range(n))) == ans, "perm 검산 실패"
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
        # 검산: 앞뒤 수열 완전열거
        from itertools import product
        assert sum(1 for _ in product("HT", repeat=n)) == ans, "coinflip 검산 실패"
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
        # 검산: 약수 짝 특성화와 교차 확인 — a는 target의 약수, 짝 b=target/a도 1~6
        assert cnt == sum(1 for d in range(1, 7) if target % d == 0 and 1 <= target // d <= 6), "diceprod 검산 실패"
        assert all(a * b == target and 1 <= a <= 6 and 1 <= b <= 6 for a, b in pairs), "diceprod 검산 실패: 짝 오류"
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


# ── 103. 목표 평균에 필요한 점수 (난4, 자료와가능성) ─────────────────────────
def gen_average_needed():
    for done, cur_avg, target_avg in [(3, 80, 85), (4, 75, 80), (2, 90, 88), (4, 82, 85)]:
        n = done + 1
        needed = n * target_avg - done * cur_avg
        # 검산: 0~150점 전 후보 완전탐색 — 목표 평균을 딱 맞추는 다음 점수는 유일
        sols = [x for x in range(0, 151) if done * cur_avg + x == n * target_avg]
        assert sols == [needed], "avgneed 검산 실패"
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


# ── 108. 선물 교환 = 방향 있는 짝 (난5, 자료와가능성) ───────────────────────
def gen_gift_exchange():
    for n in [4, 5, 6, 8]:
        ans = n * (n - 1)
        # 검산: (주는 사람, 받는 사람) 방향 있는 짝 완전열거
        from itertools import permutations
        assert sum(1 for _ in permutations(range(n), 2)) == ans, "gift 검산 실패"
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
    def _sim(k, src, aux, dst, pegs, log):
        """원반 k개를 src→dst로 옮기는 표준 해법을 실제로 실행하며 규칙 위반을 검사한다."""
        if k == 0:
            return
        _sim(k - 1, src, dst, aux, pegs, log)
        disk = pegs[src].pop()
        assert not pegs[dst] or pegs[dst][-1] > disk, "hanoi 검산 실패: 큰 원반 위 이동"
        pegs[dst].append(disk)
        log.append(disk)
        _sim(k - 1, aux, src, dst, pegs, log)

    for n in [3, 4, 5, 6]:
        ans = 2 ** n - 1
        # 검산: 실제 재귀 시뮬레이션 — 규칙을 지키며 전부 옮겨졌고 이동 수가 ans와 일치
        pegs = {0: list(range(n, 0, -1)), 1: [], 2: []}
        log = []
        _sim(n, 0, 1, 2, pegs, log)
        assert pegs[2] == list(range(n, 0, -1)) and not pegs[0] and not pegs[1] and len(log) == ans, "hanoi 검산 실패"
        add(
            "hanoi", "DATA_POSSIBILITY", 7, ["점화식", "최소 이동"],
            f"하노이탑: 크기가 다른 원반 {n}개가 기둥에 큰 것부터 쌓여 있어요. 한 번에 한 개씩, 큰 원반을 작은 원반 위에 놓지 않으면서 전부 옆 기둥으로 옮기려면 '최소' 몇 번 움직여야 할까요?",
            f"{ans}번", [f"{2 * n}번", f"{2 ** n}번", f"{ans - 2}번"],
            f"원반 {n}개를 옮기려면 먼저 위 {n - 1}개를 옆 기둥에 옮기고, 맨 아래 큰 원반 1개를 목표 기둥에 옮긴 뒤, 다시 {n - 1}개를 그 위에 얹어야 해요. 그래서 (n개) = 2×(n−1개) + 1. 1개는 1번, 2개는 3번, 3개는 7번… {n}개는 {ans}번이에요.",
            [(f"{2 ** n}번", "마지막에 1을 빼요 — 2를 {n}번 곱한 수에서 1 작은 값이에요.".replace("{n}", str(n)))],
            detail=f"하노이탑은 '큰 문제를 한 단계 작은 문제로 쪼개는(점화식)' 대표 예예요: T(n)=2·T(n−1)+1. 원반이 하나 늘 때마다 두 배+1로 폭발해서, 64개(전설의 탑)면 우주 나이보다 오래 걸려요. 재귀·분할정복 사고의 출발점이에요.",
            en={
                "statement": f"Tower of Hanoi: {n} disks of different sizes are stacked on a peg, largest at the bottom. Moving one disk at a time and never placing a larger disk on a smaller one, what is the 'minimum' number of moves to shift them all onto another peg?",
                "answer": _en_plural(ans, "move"),
                "distractors": [_en_plural(2 * n, "move"), _en_plural(2 ** n, "move"), _en_plural(ans - 2, "move")],
                "explanation": f"To move {n} disks, first move the top {n - 1} disks to another peg, move the single largest bottom disk to the target peg, then stack the {n - 1} disks back on top. So (n disks) = 2×(n−1 disks) + 1. 1 disk takes 1, 2 disks take 3, 3 disks take 7… {n} disks take {ans}.",
                "mistakes": [(_en_plural(2 ** n, "move"), f"Subtract 1 at the end — it's one less than 2 multiplied together {n} times.")],
                "detail": f"The Tower of Hanoi is the classic example of 'breaking a big problem into a problem one step smaller (a recurrence)': T(n)=2·T(n−1)+1. Each extra disk makes it explode by double+1, so 64 disks (the legendary tower) would take longer than the age of the universe. It's the starting point of recursive, divide-and-conquer thinking.",
            },
        )


# ── 126. 악수 수로 사람 수 역산 (난6, 자료와가능성) ─────────────────────────
def gen_handshake_reverse():
    for n in [10, 6, 8, 12]:
        total = n * (n - 1) // 2
        # 검산: 인원 수 전 후보 탐색 — 악수가 total번이 되는 m은 유일
        sols = [m for m in range(2, 100) if m * (m - 1) // 2 == total]
        assert sols == [n], "handrev 검산 실패"
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


# ── 111. 중앙값 (난4, 자료와가능성) ─────────────────────────────────────────
def gen_median():
    for nums in [[2, 8, 3, 9, 4], [12, 7, 20, 5, 9], [4, 1, 10, 2, 7, 8, 6], [30, 10, 45, 15, 20]]:
        s = sorted(nums)
        n = len(s)
        ans = s[n // 2]
        # 검산: 정렬에 기대지 않는 위치 확인 — ans보다 작은 값·큰 값이 정확히 절반씩
        assert n % 2 == 1 and len(set(nums)) == n, "median 검산 실패: 전제(홀수 개·서로 다름)"
        assert ans in nums and sum(1 for v in nums if v < ans) == n // 2 and sum(1 for v in nums if v > ans) == n // 2, "median 검산 실패"
        add(
            # 난이도 재조정(4→3, 2026-07 d1~5 스캔): 정렬 후 가운데 — 정의 적용.
            "median", "DATA_POSSIBILITY", 3, ["중앙값", "정렬"],
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


# ── 114. 콜라츠 추측 (난6, 자료와가능성) ────────────────────────────────────
def gen_collatz():
    for n in [6, 7, 9, 12]:
        steps = 0
        x = n
        while x != 1:
            x = x // 2 if x % 2 == 0 else 3 * x + 1
            steps += 1
        # 검산: 수열을 처음부터 다시 생성 — 정확히 steps번째에 '처음으로' 1 도달
        chk_seq = [n]
        while chk_seq[-1] != 1:
            assert len(chk_seq) <= 500, "collatz 검산 실패: 수렴 안 함"
            chk_seq.append(chk_seq[-1] // 2 if chk_seq[-1] % 2 == 0 else 3 * chk_seq[-1] + 1)
        assert len(chk_seq) - 1 == steps and 1 not in chk_seq[:-1], "collatz 검산 실패"
        add(
            # 난이도 재조정(6→4, 2026-07 d6 감사): 규칙 전문 제공, 시뮬레이션 실행뿐.
            "collatz", "DATA_POSSIBILITY", 4, ["규칙 따라가기", "콜라츠"],
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
        # 검산: 걸음 수열 완전열거 — 합이 n이 되는 1·2·3 수열을 실제로 나열해 세기
        from itertools import product
        chk_cnt = sum(1 for k in range(1, n + 1) for seq in product((1, 2, 3), repeat=k) if sum(seq) == n)
        assert chk_cnt == ans, "tribstairs 검산 실패"
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
        # 검산: 전구 상태 실제 토글 시뮬레이션
        bulbs = [False] * (n + 1)
        for person in range(1, n + 1):
            for pos in range(person, n + 1, person):
                bulbs[pos] = not bulbs[pos]
        assert sum(bulbs[1:]) == ans, "lights 검산 실패"
        add(
            "lights", "DATA_POSSIBILITY", 7, ["약수의 개수", "제곱수"],
            f"{n}개의 전구가 일렬로 있고 모두 꺼져 있어요. 1번 사람은 1의 배수 자리(전부), 2번 사람은 2의 배수 자리, … {n}번 사람은 {n}의 배수 자리 전구의 스위치를 눌러요(켜져 있으면 끄고, 꺼져 있으면 켜요). 모두 지나간 뒤 '켜져 있는' 전구는 몇 개일까요?",
            f"{ans}개", [f"{ans + 1}개", f"{n // 2}개", f"{ans - 1}개"],
            f"어떤 전구가 눌린 횟수 = 그 번호의 '약수의 개수'예요. 켜진 채로 남으려면 홀수 번 눌려야 하는데, 약수 개수가 홀수인 수는 '제곱수'뿐이에요(약수가 짝을 이루는데 제곱수만 √n×√n으로 짝이 없거든요). {n}까지의 제곱수는 1,4,9,…로 모두 {ans}개예요.",
            [(f"{n // 2}개", "절반이 아니에요 — 약수 개수가 홀수인 수(제곱수)만 켜져 있어요.")],
            detail=f"각 전구는 '자기 번호의 약수'인 사람들에게 눌려요. 약수는 보통 짝(12 → 1·12, 2·6, 3·4)을 이뤄 개수가 짝수인데, 제곱수만 √n이 자기 자신과 짝이라 홀수예요. 그래서 켜진 전구 = {n} 이하 제곱수 개수 = √{n}의 정수 부분 = {ans}개. 유명한 '전구 문제'랍니다.",
            en={
                "statement": f"There are {n} light bulbs in a row, all off. Person 1 presses the switches at positions that are multiples of 1 (all of them), person 2 at multiples of 2, … person {n} at multiples of {n} (turning off if on, on if off). After everyone has passed, how many bulbs are 'on'?",
                "answer": _en_plural(ans, "bulb"),
                "distractors": [_en_plural(ans + 1, "bulb"), _en_plural(n // 2, "bulb"), _en_plural(ans - 1, "bulb")],
                "explanation": f"The number of times a bulb is pressed = the 'number of divisors' of its number. To end up on, it must be pressed an odd number of times, and the only numbers with an odd number of divisors are 'perfect squares' (divisors pair up, but a square alone has √n×√n with no partner). The perfect squares up to {n} are 1, 4, 9, … — {ans} in all.",
                "mistakes": [(_en_plural(n // 2, "bulb"), "It's not half — only numbers with an odd number of divisors (perfect squares) stay on.")],
                "detail": f"Each bulb is pressed by the people who are 'divisors of its number'. Divisors usually come in pairs (12 → 1·12, 2·6, 3·4), giving an even count, but only a perfect square has √n paired with itself, giving an odd count. So the bulbs left on = the number of perfect squares up to {n} = the integer part of √{n} = {ans}. It's the famous 'lights problem'.",
            },
        )


# ── 129. 줄에서 위치로 인원 세기 (난2, 자료와가능성) ────────────────────────
def gen_position_count():
    for front, back in [(4, 3), (3, 5), (6, 2), (2, 4)]:
        ans = front + back - 1
        # 검산: 줄 길이 전 후보 탐색 — 앞에서 front번째이면서 뒤에서 back번째일 수 있는 인원은 유일
        sols = [tot for tot in range(1, 30) if any(p == front and tot - p + 1 == back for p in range(1, tot + 1))]
        assert sols == [ans], "position 검산 실패"
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


def gen_choose_two():
    # 순서 무관 2개 고르기(nC2) = 순서 있게 센 뒤 ÷2. 조합의 핵심 통찰.
    for names in [["딸기", "포도", "귤"], ["빨강", "파랑", "노랑", "초록"], ["가", "나", "다", "라", "마"], ["사과", "배", "감", "밤"]]:
        n = len(names)
        ans = n * (n - 1) // 2
        # 검산: 두 개 고르기 완전열거
        from itertools import combinations
        assert sum(1 for _ in combinations(names, 2)) == ans, "choose2 검산 실패"
        add(
            # 난이도 재조정(1→2 상향, 2026-07 d1~5 스캔): C(n,2)를 d1 유아층에 두는 건 과중
            # (같은 방법의 league가 d3). 유일한 상향 사례.
            "choose2", "DATA_POSSIBILITY", 2, ["조합", "순서 무관"],
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
        # 검산: 정렬에 기대지 않는 재확인 — 표 수는 모두 다르고, second보다 많은 항목은 정확히 1개
        assert len({v for _, v in data}) == len(data), "dataread 검산 실패: 표 수 동률"
        assert sum(1 for _, v in data if v > dict(data)[second]) == 1, "dataread 검산 실패"
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


def gen_stars_bars():
    # 같은 물건 N개를 몇 명에게 0개까지 허용해 나누는 방법 = 중복조합(별과 막대) C(N+k-1, k-1). (자료와가능성 난8)
    for total_items, kids in [(5, 3), (6, 3), (7, 3), (4, 2)]:
        ans = comb(total_items + kids - 1, kids - 1)
        wrong_no_zero = comb(total_items - 1, kids - 1) if total_items >= kids else 0  # 각자 1개 이상일 때(흔한 혼동)
        # 검산: 분배 완전열거 — 아이별로 받는 개수 튜플을 실제로 나열해 세기
        from itertools import product
        chk_cnt = sum(1 for dist in product(range(total_items + 1), repeat=kids) if sum(dist) == total_items)
        assert chk_cnt == ans, "starsbars 검산 실패"
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
            en={
                "statement": f"You hand out {total_items} identical candies to {kids} children with none left over. It's okay if some child gets none. "
                f"How many ways are there to hand them out in all?",
                "answer": f"{ans} ways",
                "distractors": [f"{c} ways" for c in _pick_distractors(ans, [wrong_no_zero, ans + 2, total_items * kids, ans + 1, ans - 1])],
                "explanation": f"Think of laying the {total_items} candies (●) in a row and inserting {kids - 1} dividers between them to split into {kids} groups. "
                f"Out of the {total_items + kids - 1} positions of ●'s and dividers combined, it's the number of ways to choose the {kids - 1} divider positions, a combination, so "
                f"C({total_items + kids - 1},{kids - 1})={ans} ways.",
                "mistakes": [(f"{wrong_no_zero} ways", "Since 'zero is allowed', it differs from the each-gets-at-least-one condition. Count by arranging candies and dividers together."),
                             (f"{total_items * kids} ways", "Not multiplication — count with the 'combination' of inserting dividers among the candies.")],
                "detail": "Ways to hand out identical objects to several people (zero allowed) are counted with 'stars and bars' — lay the N objects out as dots and insert one fewer divider than the number of people between them to split into groups. "
                "So it becomes the multiset combination C(N+k−1, k−1), choosing the divider positions among the (objects+dividers) positions. It's the classic tool for counting ways to distribute identical things.",
            },
        )


def gen_league():
    # 리그전(서로 한 번씩) 경기 수 = C(n,2). 중복(A-B=B-A)을 빼는 세기. (자료와가능성 난3)
    for n in [4, 5, 6, 7]:
        ans = n * (n - 1) // 2
        # 검산: 두 팀 짝 완전열거
        from itertools import combinations
        assert sum(1 for _ in combinations(range(n), 2)) == ans, "league 검산 실패"
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
        # 검산: 두 자리 수를 실제로 만들어 '서로 다른' 것만 세기
        from itertools import permutations
        made = {10 * a + b for a, b in permutations(cards, 2)}
        assert len(made) == ans and all(10 <= v <= 99 for v in made), "twodigit 검산 실패"
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
        # 검산: 두 날 짝 전부에서 차이의 최댓값을 직접 세기
        from itertools import combinations
        assert max(abs(x - y) for x, y in combinations(vals, 2)) == ans, "tablediff 검산 실패"
        add(
            # 난이도 재조정(3→2, 2026-07 d1~5 스캔): max−min 1단계 — dataread(d1)보다 쉬운 역전 해소.
            "tablediff", "DATA_POSSIBILITY", 2, ["자료 읽기", "최댓값·최솟값"],
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


def gen_electpair():
    # 반장·부반장 뽑기 = 순서 있는 2명 뽑기 nP2 = n(n−1). (자료와가능성 난4)
    for n in [4, 5, 6, 8]:
        ans = n * (n - 1)
        # 검산: (반장, 부반장) 순서 있는 짝 완전열거
        from itertools import permutations
        assert sum(1 for _ in permutations(range(n), 2)) == ans, "electpair 검산 실패"
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


def gen_knockout():
    # 토너먼트(지면 탈락) 우승까지 경기 수 = 참가자 − 1 (경기마다 한 명 탈락). (자료와가능성 난2)
    for n in [8, 4, 16, 6]:
        ans = n - 1
        # 검산: 경기 시뮬레이션 — 두 명이 겨뤄 패자만 탈락, 우승자 혼자 남을 때까지 실제로 세기
        alive = list(range(n))
        games = 0
        while len(alive) > 1:
            winner, _loser = alive.pop(), alive.pop()  # 한 경기 = 탈락 1명
            alive.append(winner)
            games += 1
        assert games == ans and len(alive) == 1, "knockout 검산 실패"
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


def gen_atleastprob():
    # 여사건: '적어도 한 개 앞면' = 1 − '모두 뒷면'. (자료와가능성 난6)
    # 난이도 재조정(난9→6, 2026-07 d9 감사): 여사건 전환은 진짜 전략이나 단일·표준 — 심화 상단.
    for n in [4, 3, 5, 2]:
        whole = 2 ** n
        ans = f"{whole - 1}/{whole}"
        # 검산: 표본공간 2^n 전수 나열 — '적어도 하나 앞면'의 분자·분모를 직접 세기
        from itertools import product
        space = list(product("HT", repeat=n))
        fav = sum(1 for o in space if "H" in o)
        assert len(space) == whole and fav == whole - 1 and gcd(fav, whole) == 1, "atleastprob 검산 실패"
        add(
            "atleastprob", "DATA_POSSIBILITY", 6, ["여사건", "적어도"],
            f"공정한 동전 {n}개를 동시에 던져요. 적어도 한 개는 앞면이 나올 확률은 얼마일까요?",
            ans, [f"1/{whole}", "1/2", f"{n}/{whole}"],
            f"'적어도 한 개 앞면'의 반대는 '모두 뒷면'이에요. 모두 뒷면일 확률은 (1/2)를 {n}번 곱한 1/{whole}이고, "
            f"1에서 빼면 {whole - 1}/{whole}이에요.",
            [(f"1/{whole}", "그건 '모두 뒷면'일 확률이에요. 구하려는 건 그 여사건(1−그 값)이에요.")],
            detail="'적어도 하나'는 반대(여사건) '하나도 없음'을 구해 1에서 빼는 게 훨씬 쉬워요. 모두 뒷면 확률 (1/2)^n을 "
            "1에서 빼면 답이에요. 여사건은 '적어도' 문제의 강력한 도구예요.",
            en={
                "statement": f"You toss {n} fair coins at the same time. What is the probability that at least one comes up heads?",
                "answer": ans,
                "distractors": [f"1/{whole}", "1/2", f"{n}/{whole}"],
                "explanation": f"The opposite of 'at least one heads' is 'all tails'. The probability of all tails is (1/2) multiplied {n} times, which is 1/{whole}; "
                f"subtracting from 1 gives {whole - 1}/{whole}.",
                "mistakes": [(f"1/{whole}", "That is the probability of 'all tails'. You want its complement (1 − that value).")],
                "detail": "For 'at least one', it's far easier to find the complement 'none at all' and subtract from 1. Subtracting the all-tails probability (1/2)^n from 1 gives the answer. The complement is a powerful tool for 'at least' problems.",
            },
        )


def gen_setpartition():
    # 서로 다른 n명을 비지 않은 두 팀으로(팀 구별 없이) 나누기 = 2^(n-1) − 1. (자료와가능성 난10)
    for n in [4, 5, 3, 6]:
        ans = 2 ** (n - 1) - 1
        whole = 2 ** n
        # 검산: 소속 배정 완전열거 — 비지 않은 이분할을 세고, 이름 없는 중복(2배)을 나눔
        from itertools import product
        chk_cnt = sum(1 for assign in product((0, 1), repeat=n) if 0 < sum(assign) < n)
        assert chk_cnt % 2 == 0 and chk_cnt // 2 == ans, "setpartition 검산 실패"
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
            en={
                "statement": f"You split {n} distinct people into two non-empty groups. When the two groups are not distinguished (no A/B labels), how many ways are there in all?",
                "answer": f"{ans} ways",
                "distractors": [f"{c} ways" for c in _pick_distractors(ans, [2 ** (n - 1), whole, ans + 1, ans - 1])],
                "explanation": f"Each person belongs to one of the two groups, giving {whole} ways, but subtract the 2 cases where one side is empty (everyone in one group), and divide by 2 because the two groups aren't distinguished → ({whole}−2)÷2 = {ans} ways.",
                "mistakes": [(f"{2 ** (n - 1)} ways", "You haven't yet removed the case where one side is completely empty. Take (total−2) and halve it.")],
                "detail": "The number of ways to split distinct items into two piles is 2^n (each item picks one of two places), minus the 2 'one side empty' cases, divided by 2 because the piles' names aren't distinguished — giving 2^(n−1)−1. It's counting that handles the double-counting of complementary pairs.",
            },
        )


def gen_barchart():
    # 막대그래프 읽기 — 둘째로 많은 값 찾기(자료를 크기 순으로 읽는 힘). (자료와가능성 난3)
    for vals in [[3, 5, 2, 6], [4, 7, 3, 8], [6, 2, 9, 5], [5, 10, 7, 4]]:
        ordered = sorted(vals, reverse=True)
        ans = ordered[1]
        # 검산: 정렬에 기대지 않는 재확인 — 막대 값은 모두 다르고 ans보다 큰 막대는 정확히 1개
        assert len(set(vals)) == len(vals), "barchart 검산 실패: 막대 동률"
        assert ans in vals and sum(1 for v in vals if v > ans) == 1, "barchart 검산 실패"
        add(
            # 난이도 재조정(3→2, 2026-07 d1~5 스캔): dataread(d1)와 동일 과제 + 막대 읽기.
            "barchart", "DATA_POSSIBILITY", 2, ["자료 읽기", "크기 순 비교"],
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
        # 검산: 평균의 정수성 + 편차 합 0 — 평균에서 벗어난 만큼의 합은 정확히 0이어야 함
        assert total % len(vals) == 0, "chartavg 검산 실패: 평균이 정수가 아님"
        assert sum(v - ans for v in vals) == 0, "chartavg 검산 실패"
        add(
            # 난이도 재조정(5→4, 2026-07 d1~5 스캔): avgbasic+막대 읽기 — avgchg(d4)보다 쉬움.
            "chartavg", "DATA_POSSIBILITY", 4, ["자료 읽기", "평균"],
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


def gen_necklace():
    # 염주(목걸이)순열 = (n−1)!/2 : 원순열에서 뒤집기까지 같게 본다. (자료와가능성 난8)
    for n in [4, 5, 6, 7]:
        circ = factorial(n - 1)
        ans = circ // 2
        # 검산: 순열 완전열거 — 회전·뒤집기 동치류의 대표(최소 튜플)를 모아 세기
        from itertools import permutations
        reps = set()
        for p in permutations(range(n)):
            variants = [p[r:] + p[:r] for r in range(n)]
            variants += [v[::-1] for v in variants]
            reps.add(min(variants))
        assert len(reps) == ans, "necklace 검산 실패"
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
            en={
                "statement": f"You thread {n} different beads on a string to make a necklace. Counting ones that become the same by rotating or flipping as one, "
                f"how many different necklaces are there?",
                "answer": f"{ans} ways",
                "distractors": [f"{c} ways" for c in _pick_distractors(ans, [circ, factorial(n), ans + 2, ans - 1])],
                "explanation": f"Threading in a straight line gives {n}! ways, but since it's circular, grouping the {n} rotations that match gives the circular permutation (n−1)!={circ} ways. "
                f"A necklace is the same when flipped too, so divide by 2 again: {circ}÷2={ans} ways.",
                "mistakes": [(f"{circ} ways", "A necklace becomes the same when 'flipped'. Divide the circular permutation by 2 once more.")],
                "detail": "Arrangements that become the same not only by rotation but also by flipping, like a necklace, are the circular permutation (n−1)! divided by 2 again, (n−1)!/2. "
                "It's a classic symmetry-counting problem where the more 'motions treated as the same' there are, the fewer the cases.",
            },
        )


def gen_passcode():
    # 반복 허용 비밀번호 경우의 수 = (숫자 종류)^(자리 수). (자료와가능성 난6)
    for base, dig in [(10, 3), (2, 5), (6, 3), (3, 4)]:
        ans = base ** dig
        # 검산: 비밀번호 완전열거
        from itertools import product
        assert sum(1 for _ in product(range(base), repeat=dig)) == ans, "passcode 검산 실패"
        add(
            # 난이도 재조정(6→4, 2026-07 d6 감사): 곱의 법칙 단일 지수화.
            "passcode", "DATA_POSSIBILITY", 4, ["곱의 법칙", "반복 허용"],
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


def gen_avgbasic():
    # 평균 = 합 ÷ 개수. (자료와가능성 난4)
    for vals in [[4, 6, 8, 10], [2, 4, 9, 5], [10, 20, 30, 40], [3, 7, 8, 6]]:
        total = sum(vals)
        ans = total // len(vals)
        # 검산: 평균의 정수성 + 편차 합 0 — 평균에서 벗어난 만큼의 합은 정확히 0이어야 함
        assert total % len(vals) == 0, "avgbasic 검산 실패: 평균이 정수가 아님"
        assert sum(v - ans for v in vals) == 0, "avgbasic 검산 실패"
        vs = ", ".join(str(v) for v in vals)
        add(
            # 난이도 재조정(4→2, 2026-07 d1~5 스캔): '더해서 나누기' 정의 적용 그 자체.
            "avgbasic", "DATA_POSSIBILITY", 2, ["평균", "합 나누기"],
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
        # 검산: 줄 세우기 완전열거
        from itertools import permutations
        assert sum(1 for _ in permutations(range(n))) == ans, "lineup 검산 실패"
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
        # 검산: 등장 횟수 직접 대조 — ans가 최다 등장이고 최다는 유일
        top = max(vals.count(v) for v in set(vals))
        assert vals.count(ans) == top, "mode 검산 실패"
        assert sum(1 for v in set(vals) if vals.count(v) == top) == 1, "mode 검산 실패: 최빈값 동률"
        add(
            # 난이도 재조정(4→2, 2026-07 d1~5 스캔): 가장 잦은 값 고르기 — 정의 적용.
            "mode", "DATA_POSSIBILITY", 2, ["최빈값", "자료 정리"],
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
        # 검산: 표본공간(공 하나하나) 전수 나열 + 기약분수 교차곱 확인
        balls = ["빨강"] * r + ["파랑"] * b
        fav = sum(1 for ball in balls if ball == "빨강")
        num, den = map(int, ans.split("/"))
        assert len(balls) == total and fav * den == num * total and gcd(num, den) == 1, "simpleprob 검산 실패"
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


def gen_derange():
    # 교란순열(완전순열) D(n): 아무도 제자리가 아닌 순열의 수. D(n)=(n−1)(D(n−1)+D(n−2)). (자료와가능성 난9)
    d = [1, 0]  # d[0]=D(0)=1, d[1]=D(1)=0
    for i in range(2, 12):
        d.append((i - 1) * (d[i - 1] + d[i - 2]))
    for n in [4, 5, 6, 3]:
        ans = d[n]
        allperm = factorial(n)
        # 검산: 순열 완전열거 — 제자리가 하나도 없는 순열을 직접 세기
        from itertools import permutations
        chk_cnt = sum(1 for p in permutations(range(n)) if all(p[i] != i for i in range(n)))
        assert chk_cnt == ans, "derange 검산 실패"
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
            en={
                "statement": f"{n} people each have their own name tag. All the tags are collected, shuffled, and handed back out one per person. "
                f"In how many ways does it happen that no one gets their own name tag?",
                "answer": _en_plural(ans, "way"),
                "distractors": [_en_plural(int(c), "way") for c in _pick_distractors(ans, [allperm, ans + 1, ans - 1, allperm - 1])],
                "explanation": f"The total number of ways {n} people can receive the tags is {n}!={allperm}. Removing the cases where 'at least one person gets their own' by inclusion-exclusion, "
                f"or using the rule D(n)=(n−1)×(D(n−1)+D(n−2)), gives D({n})={ans}.",
                "mistakes": [(_en_plural(allperm, "way"), f"That's the unrestricted total of all permutations ({n}!={allperm}). You must remove the 'no one in their own place' condition."),
                             (_en_plural(ans - 1, "way"), "It's easy to lose track of the plus/minus signs in inclusion-exclusion. Cross-check with the recurrence.")],
                "detail": "A permutation where no one ends up in their own place is called a 'derangement D(n)'. Removing the 'someone is in their own place' cases from the total n! by inclusion-exclusion gives D(n)=n!(1−1/1!+1/2!−…), and it also comes from the recurrence D(n)=(n−1)(D(n−1)+D(n−2)). A classic problem of counting by inverting an 'at least' condition.",
            },
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
        # 검산: 구슬 배열 완전열거 — 같은 색을 같은 기호로 두고 '서로 다른' 배열만 세기
        from itertools import permutations
        beads = [name for name, c in colors for _ in range(c)]
        assert len(set(permutations(beads))) == ans, "multiperm 검산 실패"
        desc = ", ".join(f"{name} 구슬 {c}개" for name, c in colors)
        denom = "×".join(f"{c}!" for _, c in colors)
        color_en = {"빨강": "red", "파랑": "blue", "노랑": "yellow"}
        desc_en = ", ".join(_en_plural(c, f"{color_en[name]} bead") for name, c in colors)
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
            en={
                "statement": f"You want to lay out {desc_en} in a row. When beads of the same color are not distinguished from each other, how many different arrangements are there in all?",
                "answer": f"{ans} ways",
                "distractors": [f"{c} ways" for c in _pick_distractors(ans, [factorial(total), ans + 2, ans * 2, total * total])],
                "explanation": f"With {total} beads in all, the total permutations placing them in positions is {total}!={factorial(total)} ways. But swapping same-colored beads gives the same arrangement, "
                f"so divide by the factorial of each color's count → {total}! ÷ ({denom}) = {ans} ways.",
                "mistakes": [(f"{factorial(total)} ways", "You counted same-colored beads as if they were different. You must divide out the swaps among same colors."),
                             (f"{ans * 2} ways", "The divisor is too small. Multiply the factorials of every color's count and divide by all of them.")],
                "detail": "The number of ways to arrange a mix with repeated items in a row is (total)! ÷ (product of the counts! of the identical items) — you count as if everything were different, "
                "then divide out the duplicates from swapping identical items among themselves. It's the classic tool for handling 'indistinguishable' items in permutations.",
            },
        )


def gen_catalan():
    # 카탈란 수 Cn = C(2n,n)/(n+1): 올바른 괄호 짝, 격자 경로, 이진트리 등을 세는 수. (자료와가능성 난10)
    for n in [3, 4, 5, 2]:
        whole = comb(2 * n, n)
        ans = whole // (n + 1)
        # 검산: 괄호열 완전열거 — 접두사에서 닫힘이 앞서지 않는 배열을 직접 세기
        from itertools import product
        chk_cnt = 0
        for seq in product((1, -1), repeat=2 * n):
            run = 0
            for step in seq:
                run += step
                if run < 0:
                    break
            else:
                if run == 0:
                    chk_cnt += 1
        assert chk_cnt == ans, "catalan 검산 실패"
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
            en={
                "statement": f"You place {n} opening brackets '(' and {n} closing brackets ')', {2 * n} in total, in a row. In how many ways can you arrange them so that, "
                f"counting from the left up to any position, the number of closing brackets never exceeds the number of opening brackets (a valid bracket matching)?",
                "answer": f"{ans} ways",
                "distractors": [f"{c} ways" for c in _pick_distractors(ans, [whole, whole // 2, ans + 2, ans * 2])],
                "explanation": f"With no constraint, choosing {n} of the {2 * n} positions for the opening brackets gives C({2 * n},{n}) = {whole} ways. Removing the 'invalid' "
                f"arrangements where a closing bracket gets ahead, by the reflection principle, leaves the Catalan number C{n} = {whole}÷{n + 1} = {ans} ways.",
                "mistakes": [(f"{whole} ways", "That's the total counting only the bracket positions. You have to filter by the condition 'a closing bracket must not get ahead'.")],
                "detail": "The Catalan number Cn = (2n)!/(n!(n+1)!) = C(2n,n)/(n+1) counts arrangements where 'the rule must not break partway' — valid bracket matchings, "
                "lattice paths below the diagonal, binary tree shapes. You find it by using the reflection principle to remove the rule-breaking cases from the total. It's the star sequence of combinatorics.",
            },
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
        # 검산: 합성(순서 구별) 완전열거 후 정렬 대표로 접기 — 분할 수·합성 수를 함께 확인
        from itertools import combinations
        seen = set()
        comp_cnt = 0
        for r2 in range(n):
            for cuts in combinations(range(1, n), r2):
                bounds = (0,) + cuts + (n,)
                seen.add(tuple(sorted(bounds[i + 1] - bounds[i] for i in range(len(bounds) - 1))))
                comp_cnt += 1
        assert comp_cnt == ordered, "partition 검산 실패: 합성 수"
        assert len(seen) == ans, "partition 검산 실패"
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
            en={
                "statement": f"In how many ways can {n} be written as a sum of natural numbers each at least 1? "
                f"Sums that differ only in the order of the addends count as the same (for example, 1+2 and 2+1 are the same).",
                "answer": f"{ans} ways",
                "distractors": [f"{c} ways" for c in _pick_distractors(ans, [ordered, ans + 1, ans - 1, n])],
                "explanation": f"Count without gaps or repeats by placing the largest part first. Starting from {n}={n} and breaking off one smaller piece at a time gives {ans} ways in all "
                f"(sums differing only in order count once).",
                "mistakes": [(f"{ordered} ways", "That's when order is 'distinguished' (e.g. 1+2 and 2+1 as different). Ignoring order gives far fewer."),
                             (f"{ans + 1} ways", "It's easy to miss some or count the same one twice. List systematically from the largest part to check.")],
                "detail": "The number of ways to break a natural number n into a sum of naturals ignoring order is called the 'partition number p(n)'. Unlike compositions, which distinguish order (2^(n−1) ways), count them by placing the largest part first so nothing is missed. With no neat closed formula, systematic listing is the key — a classic of number theory and combinatorics.",
            },
        )


# ── 139. 논리 소거 격자 — 누가 무엇을 좋아할까 (난3, 자료와가능성) ────────────────
def gen_logic_grid():
    # 발견형 자기검증: 정답 인물과 정답 항목의 짝은 어느 단서에도 직접 나오지 않는다 — 부정 단서
    # 두 개의 '결합'(소거)으로 셋째 인물이 먼저 확정되어야 나머지가 도미노로 풀린다(기준1 통과).
    # 긍정 단서가 하나도 없어 단순 조회로는 한 칸도 못 채운다(기준2 통과 — 입문 사고력).
    from itertools import permutations
    # (사람3, 항목3 ko, 항목3 en, 주제 ko, 주제 en, i, j, x, y)
    # 단서: 사람i≠항목x · 사람j≠항목x · 사람j≠항목y → 남은 사람k=항목x, 사람j=항목z, 사람i=항목y.
    scenarios = [
        (["민준", "서연", "지호"], ["사과", "귤", "배"], ["apples", "tangerines", "pears"], "과일", "fruit", 0, 1, 0, 1),
        (["하은", "도윤", "예린"], ["강아지", "고양이", "앵무새"], ["dogs", "cats", "parrots"], "동물", "animal", 0, 2, 1, 0),
        (["시우", "지아", "민준"], ["축구", "수영", "야구"], ["soccer", "swimming", "baseball"], "운동", "sport", 1, 2, 2, 0),
        (["서연", "지호", "하은"], ["빨간색", "파란색", "초록색"], ["red", "blue", "green"], "색깔", "color", 1, 2, 1, 0),
    ]
    for people, items, items_en, topic, topic_en, i, j, x, y in scenarios:
        k = 3 - i - j  # 항목 x의 주인(소거로 확정되는 사람)
        z = 3 - x - y  # 사람 j의 항목
        # 검산: 배정(순열) 완전열거 — 세 단서를 만족하는 배정이 정확히 1개이고 그 배정이 의도와 일치
        sols = [pm for pm in permutations(range(3)) if pm[i] != x and pm[j] != x and pm[j] != y]
        assert len(sols) == 1 and sols[0][i] == y and sols[0][k] == x and sols[0][j] == z, "logicgrid 검산 실패"
        final = {people[i]: items[y], people[j]: items[z], people[k]: items[x]}
        final_txt = ", ".join(f"{p}-{it}" for p, it in ((people[0], final[people[0]]), (people[1], final[people[1]]), (people[2], final[people[2]])))
        add(
            "logicgrid", "DATA_POSSIBILITY", 3, ["논리 소거", "단서 결합"],
            f"{people[0]}·{people[1]}·{people[2]}{_eun(people[2])} {items[0]}·{items[1]}·{items[2]}{_eul(items[2])} 서로 다르게 하나씩 좋아해요. "
            f"{people[i]}{_gwa(people[i])} {people[j]}{_eun(people[j])} 둘 다 {items[x]}{_eul(items[x])} 좋아하지 않아요. "
            f"{people[j]}{_eun(people[j])} {items[y]}도 좋아하지 않아요. {items[y]}{_eul(items[y])} 좋아하는 사람은 누구일까요?",
            people[i], [people[k], people[j], "알 수 없어요"],
            f"표를 그려 아닌 칸부터 지워요. {people[i]}{_gwa(people[i])} {people[j]} 둘 다 {items[x]}{_eul(items[x])} 좋아하지 않으니, "
            f"{items[x]}{_eun(items[x])} 남은 {people[k]}의 것이에요. 이제 {people[j]}{_eun(people[j])} {items[x]}도 {items[y]}도 아니니 "
            f"{items[z]}{_eul(items[z])} 좋아하고, 마지막 남은 {items[y]}{_iga(items[y])} {people[i]}의 것이에요. 답은 {people[i]}{_copula(people[i])}.",
            [(people[k], f"두 부정 단서를 결합하면 {people[k]}{_eun(people[k])} {items[x]}{_eul(items[x])} 좋아하는 사람으로 먼저 확정돼요. {items[y]}의 주인은 될 수 없어요."),
             (people[j], f"단서에 {people[j]}{_eun(people[j])} {items[y]}{_eul(items[y])} 좋아하지 않는다고 바로 나와 있어요. 단서를 끝까지 읽어요."),
             ("알 수 없어요", "단서 하나만 보면 모르지만, 세 단서를 한 표에 함께 표시하면 답이 하나로 정해져요.")],
            detail=f"'아니다'라는 단서도 훌륭한 정보예요. 사람×{topic} 표를 그리고 아닌 칸에 ×를 치면, 한 항목에 ×가 두 개 모이는 순간 남은 칸이 저절로 ○가 돼요(소거). "
            f"이 문제의 열쇠는 {items[x]} — 두 사람이 모두 아니라고 했으니 {people[k]}{_euro(people[k])} 확정되고, 그다음부터는 도미노처럼 풀려요. "
            f"되돌아보기: 완성한 표({final_txt})를 세 단서에 다시 대 보면 모두 들어맞아요.",
            en={
                "concepts": ["logical elimination", "combining clues"],
                "statement": f"Three children A, B, and C each like a different {topic_en} among {items_en[0]}, {items_en[1]}, and {items_en[2]}. "
                f"Neither {'ABC'[i]} nor {'ABC'[j]} likes {items_en[x]}. "
                f"{'ABC'[j]} does not like {items_en[y]} either. Who likes {items_en[y]}?",
                "answer": "ABC"[i],
                "distractors": ["ABC"[k], "ABC"[j], "It cannot be determined"],
                "explanation": f"Draw a grid and cross out what each child does NOT like. Both {'ABC'[i]} and {'ABC'[j]} rule out {items_en[x]}, "
                f"so {items_en[x]} must belong to the remaining child, {'ABC'[k]}. Now {'ABC'[j]} likes neither {items_en[x]} nor {items_en[y]}, "
                f"so {'ABC'[j]} likes {items_en[z]}, and the last one left, {items_en[y]}, belongs to {'ABC'[i]}. The answer is {'ABC'[i]}.",
                "mistakes": [("ABC"[k], f"Combining the two negative clues pins {'ABC'[k]} down as the one who likes {items_en[x]} — so {'ABC'[k]} cannot be the owner of {items_en[y]}."),
                             ("ABC"[j], f"A clue says outright that {'ABC'[j]} does not like {items_en[y]}. Read the clues to the end."),
                             ("It cannot be determined", "One clue alone is not enough, but marking all three clues on one grid pins the answer down to a single child.")],
                "detail": f"A 'not' clue is great information too. Draw a children-by-{topic_en} grid and put × where something is ruled out: the moment one item collects two ×'s, "
                f"the remaining cell becomes ○ by itself (elimination). The key here is {items_en[x]} — two children both ruled it out, so it must be {'ABC'[k]}'s, "
                f"and the rest falls like dominoes. Looking back: check the finished grid against all three clues and every one fits.",
            },
        )


# ── 140. 반드시 뽑히려면 — 최악의 경우 설계 (난3, 자료와가능성) ───────────────────
def gen_sure_pick():
    # 발견형 자기검증: '가장 운 나쁜 순서를 스스로 설계한다'는 전략이 문제문에 없고(기준1 통과),
    # 특정 색 보장은 운 좋은 나열로 우회 불가 — 다른 색이 전부 먼저 나오는 적대 순서를 상상해야 답이
    # 확정된다(기준2 통과). 비둘기집(pigeon d5, '아무 색이든 같은 짝')과 구조가 다르다:
    # 목표가 '정해진 색 k개'라 답이 (다른 색 전부)+k로, 색 가짓수가 아니라 나머지 개수가 지배한다.
    from itertools import combinations
    color_en = {"빨간": "red", "파란": "blue", "노란": "yellow", "초록": "green", "보라": "purple"}
    for colors, target, k in [
        ([("빨간", 4), ("파란", 5), ("노란", 3)], "빨간", 1),
        ([("빨간", 3), ("파란", 5), ("노란", 4)], "빨간", 2),
        ([("초록", 5), ("보라", 4)], "보라", 2),
        ([("빨간", 6), ("파란", 4), ("노란", 2)], "노란", 1),
    ]:
        total = sum(c for _, c in colors)
        tcnt = dict(colors)[target]
        others = total - tcnt
        ans = others + k
        assert k <= tcnt and len(colors) + 1 != k and ans not in (k, len(colors) + 1, total), "surepick 파라미터 오류"
        # 검산: 꺼내는 조합 완전열거 — (ans−1)개에는 목표 색이 k개 미만인 조합이 존재하고,
        # ans개면 어느 조합이든 k개 이상임을 공 하나하나 수준에서 확인(공식과 독립인 길).
        balls = [name for name, c in colors for _ in range(c)]
        assert any(sum(1 for idx in pick if balls[idx] == target) < k for pick in combinations(range(total), ans - 1)), "surepick 검산 실패: 최악 반례 없음"
        assert all(sum(1 for idx in pick if balls[idx] == target) >= k for pick in combinations(range(total), ans)), "surepick 검산 실패: 보장 미달"
        desc = ", ".join(f"{name} 구슬 {c}개" for name, c in colors)
        others_desc = ", ".join(f"{name} {c}개" for name, c in colors if name != target)
        desc_en = ", ".join(_en_plural(c, f"{color_en[name]} marble") for name, c in colors)
        others_en = ", ".join(_en_plural(c, color_en[name]) for name, c in colors if name != target)
        add(
            "surepick", "DATA_POSSIBILITY", 3, ["최악의 경우", "반드시 보장"],
            f"주머니에 {desc}가 들어 있어요. 안을 보지 않고 구슬을 한 개씩 꺼내요. 꺼낸 구슬 중에 {target} 구슬이 반드시 {k}개 있으려면, 최소 몇 개를 꺼내야 할까요?",
            f"{ans}개", [f"{k}개", f"{len(colors) + 1}개", f"{total}개"],
            f"'반드시'가 나오면 가장 운이 나쁜 경우를 내가 직접 만들어 봐요. 최악이면 {target} 구슬이 아닌 구슬({others_desc} — 모두 {others}개)만 계속 나올 수 있어요. "
            f"하지만 {others}개가 다 나온 다음부터는 주머니에 {target} 구슬뿐이에요. 그래서 {others}+{k}={ans}개를 꺼내면 어떤 순서로 나와도 {target} 구슬이 {k}개 이상 들어 있어요.",
            [(f"{k}개", f"운이 좋으면 {k}개 만에 나올 수도 있지만, '반드시'는 가장 운이 나쁜 순서에서도 되어야 해요."),
             (f"{len(colors) + 1}개", f"색깔 수보다 1개 많이 꺼내는 건 '아무 색이든 같은 색 두 개'를 보장하는 방법이에요. 정해진 색({target} 구슬)을 원할 때는 다른 색이 전부 먼저 나오는 최악을 생각해요."),
             (f"{total}개", f"전부 꺼내면 당연히 되지만 '최소'가 아니에요. {target} 구슬이 아닌 구슬은 {others}개뿐이라 {others}+{k}={ans}개면 충분해요.")],
            detail=f"핵심은 '운이 가장 나쁜 시나리오'를 스스로 설계하는 거예요 — 보장은 행운이 아니라 최악의 경우에서 증명돼요. 주의할 점: 답은 {target} 구슬이 몇 개인지({tcnt}개)가 아니라 "
            f"다른 색이 몇 개인지({others}개)로 정해져요. 목표 색이 많아도 다른 색이 많으면 더 여러 번 꺼내야 해요. 되돌아보기: {ans - 1}개만 꺼내면? 다른 색 {others}개에 {target} 구슬 {k - 1}개일 수 있어 "
            f"아직 {k}개가 보장되지 않아요. 일반화하면 필요한 수 = (다른 색 전부) + (원하는 개수)예요.",
            en={
                "concepts": ["worst case", "guaranteed outcome"],
                "statement": f"A bag holds {desc_en}. You draw marbles one at a time without looking inside. "
                f"What is the smallest number of marbles you must draw to be certain that you have at least {_en_plural(k, color_en[target] + ' marble')}?",
                "answer": _en_plural(ans, "marble"),
                "distractors": [_en_plural(k, "marble"), _en_plural(len(colors) + 1, "marble"), _en_plural(total, "marble")],
                "explanation": f"When you see 'certain', build the unluckiest case yourself. At worst, only non-{color_en[target]} marbles ({others_en} — {others} in all) keep coming out. "
                f"But once those {others} are gone, only {color_en[target]} marbles remain in the bag. So drawing {others}+{k}={ans} marbles guarantees at least {k} {color_en[target]} marble(s) in any order.",
                "mistakes": [(_en_plural(k, "marble"), f"With luck it could take only {k}, but 'certain' means it must work even in the unluckiest order."),
                             (_en_plural(len(colors) + 1, "marble"), f"Drawing one more than the number of colors guarantees 'some matching pair of ANY color'. To get a specific color ({color_en[target]}), imagine all the other colors coming out first."),
                             (_en_plural(total, "marble"), f"Drawing everything works, of course, but it isn't the minimum. There are only {others} non-{color_en[target]} marbles, so {others}+{k}={ans} draws are enough.")],
                "detail": f"The heart of this problem is designing the worst-case scenario yourself — a guarantee is proved in the worst case, not by luck. Note that the answer is set not by how many {color_en[target]} marbles there are ({tcnt}), "
                f"but by how many marbles of OTHER colors there are ({others}). Looking back: with only {ans - 1} draws you could have all {others} other marbles and just {k - 1} {color_en[target]} — not yet guaranteed. In general: draws needed = (all the others) + (how many you want).",
            },
        )


# ── 141. 어느 놀이가 유리할까 — 가능성의 비율 비교 (난5, 자료와가능성) ─────────────
def gen_fair_game():
    # 발견형 자기검증: 비교 방법(통분·공통 표)이 문제문에 없고(기준1 통과), '이기는 경우의 개수'
    # 비교라는 자연스러운 지름길이 네 벌 모두에서 함정이 되도록 두 놀이의 표본공간 크기를
    # 일부러 어긋나게 설계했다(기준2 통과 — 개수 우회가 오답으로 유도됨).
    from itertools import product
    die = list(range(1, 7))
    coin2 = [c for c in product("HT", repeat=2)]
    coin3 = [c for c in product("HT", repeat=3)]
    coin1 = ["H", "T"]
    tie_txt, unk_txt = "두 사람이 이길 가능성은 똑같아요", "누가 유리한지 알 수 없어요"
    scenarios = [
        (("민준", "서연"),
         "주사위 한 개를 굴려 6의 약수(1, 2, 3, 6)가 나오면", "rolls one die and wins if it shows a divisor of 6 (1, 2, 3, or 6)",
         die, lambda o: 6 % o == 0,
         "동전 두 개를 던져 적어도 한 개가 앞면이면", "tosses two coins and wins if at least one coin shows heads",
         coin2, lambda o: "H" in o, "B", "A", 4, 3),
        (("지호", "하은"),
         "주사위 한 개를 굴려 짝수가 나오면", "rolls one die and wins if it shows an even number",
         die, lambda o: o % 2 == 0,
         "동전 두 개를 던져 두 동전이 서로 다른 면이 나오면", "tosses two coins and wins if the two coins show different faces",
         coin2, lambda o: o[0] != o[1], "T", "A", 3, 2),
        (("도윤", "예린"),
         "동전 세 개를 던져 세 개가 모두 같은 면이 나오면", "tosses three coins and wins if all three show the same face",
         coin3, lambda o: len(set(o)) == 1,
         "주사위 한 개를 굴려 5 이상이 나오면", "rolls one die and wins if it shows 5 or more",
         die, lambda o: o >= 5, "B", "T", 2, 2),
        (("시우", "지아"),
         "동전 한 개를 던져 앞면이 나오면", "tosses one coin and wins if it shows heads",
         coin1, lambda o: o == "H",
         "주사위 한 개를 굴려 2 이하가 나오면", "rolls one die and wins if it shows 2 or less",
         die, lambda o: o <= 2, "A", "B", 1, 2)]
    for (na, nb), da, da_en, sa, pa, db, db_en, sb, pb, expected, trap, fav_a, fav_b in scenarios:
        size_a, size_b = len(sa), len(sb)
        assert sum(1 for o in sa if pa(o)) == fav_a and sum(1 for o in sb if pb(o)) == fav_b, "fairgame 파라미터 오류"
        common = size_a * size_b
        # 검산: 두 놀이를 '한 판씩 같이 벌인' 공통 표본공간(곱집합)을 통째로 나열해 칸 수로 직접 비교
        # — 분수 통분이라는 정답 경로와 달리 짝 (a, b)를 하나하나 세는 독립 경로.
        ca = sum(1 for a in sa for b in sb if pa(a))
        cb = sum(1 for a in sa for b in sb if pb(b))
        assert {"A": ca > cb, "B": cb > ca, "T": ca == cb}[expected], "fairgame 검산 실패: 공통 표 비교 불일치"
        assert ca == fav_a * size_b and cb == fav_b * size_a, "fairgame 검산 실패: 곱집합 세기"
        answer = {"A": na, "B": nb, "T": tie_txt}[expected]
        trap_choice = {"A": na, "B": nb, "T": tie_txt}[trap]
        conclusion = {"A": f"{na}의 가능성이 더 높아요", "B": f"{nb}의 가능성이 더 높아요", "T": "두 사람이 똑같아요"}[expected]
        wrongs = [c for c in [na, nb, tie_txt, unk_txt] if c != answer]
        mist = [(trap_choice, f"이기는 경우의 개수({fav_a}가지 대 {fav_b}가지)만 비교했어요. 두 놀이는 전체 경우 수({size_a}가지와 {size_b}가지)가 달라서, 개수가 아니라 전체에서 차지하는 비율로 비교해야 해요."),
                (unk_txt, "알 수 없지 않아요. 두 놀이의 경우를 각각 모두 나열하고 분수로 나타내면 정확히 비교할 수 있어요.")]
        for w in wrongs:
            if w != trap_choice and w != unk_txt:
                mist.append((w, f"{na}의 가능성은 {fav_a}/{size_a}, {nb}의 가능성은 {fav_b}/{size_b} — 통분하면 {ca}/{common} 대 {cb}/{common}이에요. 다시 비교해 보세요."))
        en_choice = {"A": "A", "B": "B", "T": "They are equally likely to win"}
        en_unk = "It cannot be determined"
        en_wrongs = [c for c in ["A", "B", en_choice["T"], en_unk] if c != en_choice[expected]]
        en_mist = [(en_choice[trap], f"You compared only the number of winning outcomes ({fav_a} vs {fav_b}). The two games have different total outcomes ({size_a} and {size_b}), so you must compare the fractions, not the counts."),
                   (en_unk, "It can be determined: list every outcome of each game and write the chances as fractions to compare them exactly.")]
        for w in en_wrongs:
            if w != en_choice[trap] and w != en_unk:
                en_mist.append((w, f"A's chance is {fav_a}/{size_a} and B's is {fav_b}/{size_b} — over a common denominator that's {ca}/{common} vs {cb}/{common}. Compare again."))
        add(
            "fairgame", "DATA_POSSIBILITY", 5, ["가능성 비교", "공정한 놀이"],
            f"{na}{_gwa(na)} {nb}{_iga(nb)} 각자 다른 놀이를 한 번씩 해요. {na}{_eun(na)} {da} 이기고, {nb}{_eun(nb)} {db} 이겨요. 누가 이길 가능성이 더 높을까요?",
            answer, wrongs,
            f"두 놀이의 경우를 각각 모두 나열해요. {na}{_eun(na)} 전체 {size_a}가지 중 {fav_a}가지에서 이겨요({fav_a}/{size_a}). {nb}{_eun(nb)} 전체 {size_b}가지 중 {fav_b}가지에서 이겨요({fav_b}/{size_b}). "
            f"분모가 달라 개수로는 비교할 수 없으니 통분해요: {ca}/{common} 대 {cb}/{common} — {conclusion}.",
            mist,
            detail=f"이길 가능성은 '이기는 경우의 개수'가 아니라 '전체에서 차지하는 비율'이에요. 판의 크기가 다른 두 놀이는 분모를 맞춰야 비교돼요. 두 놀이의 결과를 짝지은 {size_a}×{size_b}={common}칸 표를 그리면 "
            f"{na}{_iga(na)} 이기는 칸 {ca}개, {nb}{_iga(nb)} 이기는 칸 {cb}개로 한눈에 보여요 — 통분이 바로 이 표예요. 되돌아보기: 나열한 경우 수({fav_a}/{size_a}, {fav_b}/{size_b})를 빠짐없이 다시 세어 확인하세요. "
            f"일반화: 어떤 두 놀이든 공통 표(통분)로 비교할 수 있어요.",
            en={
                "concepts": ["comparing chances", "fair game"],
                "statement": f"A and B each play their own game of chance once. A {da_en}, and B {db_en}. Who is more likely to win?",
                "answer": en_choice[expected],
                "distractors": en_wrongs,
                "explanation": f"List every outcome of each game. A wins in {fav_a} of {size_a} outcomes ({fav_a}/{size_a}); B wins in {fav_b} of {size_b} outcomes ({fav_b}/{size_b}). "
                f"The denominators differ, so raw counts can't be compared — put them over a common denominator: {ca}/{common} vs {cb}/{common}. "
                + {"A": "A is more likely to win.", "B": "B is more likely to win.", "T": "They are equally likely."}[expected],
                "mistakes": en_mist,
                "detail": f"A winning chance is not 'how many winning outcomes' but 'what fraction of all outcomes'. Games with different-sized boards need a common denominator. Pairing the two games' results in a {size_a}×{size_b}={common}-cell table shows "
                f"{ca} cells where A wins and {cb} where B wins at a glance — that table IS the common denominator. Looking back: recount the listed outcomes ({fav_a}/{size_a}, {fav_b}/{size_b}) to make sure nothing is missed. Any two games can be compared this way.",
            },
        )


# ── 142. 찢어진 리그전 결과표 — 승수 합의 불변량 (난5, 자료와가능성) ───────────────
def gen_winsum():
    # 발견형 자기검증: '모든 팀의 승수 합 = 전체 경기 수'라는 불변량이 문제문에 없고(기준1 통과),
    # 개별 대진 결과가 하나도 주어지지 않아 경기 나열·조회로는 우회 불가 — 보존량 발견이 유일한
    # 통로다(기준2 통과). league(d3)는 경기 수 '세기'로 끝나지만, 여기선 그 수가 숨은 보존량으로 쓰인다.
    from itertools import combinations, product
    scenarios = [
        (["독수리", "호랑이", "돌고래", "늑대", "부엉이"], [3, 1, 2, 3]),
        (["사자", "여우", "곰", "매", "거북"], [4, 2, 0, 1]),
        (["토끼", "치타", "판다", "수달", "참새", "고래"], [4, 3, 1, 2, 1]),
        (["백조", "물개", "까치", "다람쥐", "순록"], [3, 2, 4, 1]),
    ]
    for names, known in scenarios:
        n = len(names)
        games = n * (n - 1) // 2
        ans = games - sum(known)
        losses = n - 1 - ans
        assert 0 <= ans <= n - 1 and len({ans, ans + 1, losses}) == 3, "winsum 파라미터 오류"
        # 검산: 전체 대진 결과 2^C(n,2)가지 완전열거 — 알려진 승수와 맞는 결과가 실제로 존재하고
        # (표가 실현 가능하고), 그 모든 결과에서 마지막 팀의 승수가 한 값뿐임을 직접 확인.
        pairs = list(combinations(range(n), 2))
        found = set()
        for bits in product((0, 1), repeat=len(pairs)):
            wins = [0] * n
            for (a, b), t in zip(pairs, bits):
                wins[a if t else b] += 1
            if wins[: n - 1] == known:
                found.add(wins[-1])
        assert found == {ans}, "winsum 검산 실패"
        last = names[-1]
        known_desc = ", ".join(f"{nm} {w}승 {n - 1 - w}패" for nm, w in zip(names, known))
        ks = sum(known)
        lsum = sum(n - 1 - w for w in known)
        last_en = "ABCDEF"[n - 1]
        known_en = ", ".join(f"Team {'ABCDEF'[t]}: {w} wins, {n - 1 - w} losses" for t, w in enumerate(known))
        add(
            "winsum", "DATA_POSSIBILITY", 5, ["리그전 결과표", "승수 합 불변량"],
            f"{n}개 팀({'·'.join(names)})이 서로 한 번씩 겨루는 리그전을 마쳤고, 비긴 경기는 없어요. 그런데 결과표에서 {last} 팀 줄이 찢어져 보이지 않아요. "
            f"남은 기록은 {known_desc}예요. {last} 팀은 몇 승을 했을까요?",
            f"{ans}승", ["알 수 없어요", f"{ans + 1}승", f"{losses}승"],
            f"비기는 경기가 없으니 한 경기가 끝날 때마다 꼭 '1승'이 하나씩 생겨요. 그래서 경기 내용과 상관없이 모든 팀의 승수를 더하면 전체 경기 수와 같아요. "
            f"{n}개 팀이 서로 한 번씩이면 경기는 {n}×({n}−1)÷2={games}경기이고, 보이는 {n - 1}개 팀의 승수 합이 {ks}승이니 {last} 팀은 {games}−{ks}={ans}승이에요.",
            [("알 수 없어요", "경기 하나하나의 결과를 몰라도 돼요. 경기마다 승이 꼭 1씩 생기니 '모든 팀의 승수 합 = 전체 경기 수'라는 숨은 규칙이 답을 하나로 정해요."),
             (f"{ans + 1}승", f"전체 경기 수가 한 끗 어긋났어요. {n}개 팀이 서로 한 번씩이면 {n}×({n}−1)÷2={games}경기 — 같은 경기를 두 번 세거나 빠뜨리지 않았는지 확인하세요."),
             (f"{losses}승", f"승과 패가 뒤바뀌었어요. {last} 팀은 {n - 1}경기를 했으니 {ans}승이면 {losses}패 — 물음은 승수예요.")],
            detail=f"표가 찢어져도 복원할 수 있는 건 '어떤 순서로 어떤 결과가 나왔든 변하지 않는 양'이 있기 때문이에요. 승의 총합은 경기마다 정확히 1씩 늘어나 언제나 경기 수와 같아요 — 이렇게 과정과 무관하게 "
            f"고정되는 양을 불변량이라고 해요. 되돌아보기: 패로도 검산할 수 있어요. 패의 총합도 {games}{_iga(games)} 되어야 하는데, 보이는 팀의 패 합 {lsum}에 {last} 팀의 {losses}패를 더하면 정확히 {games}{_iga(games)} 돼요. "
            f"일반화: 무승부가 있는 리그라면 승만으로는 안 되고 '승 + 무÷2'의 합 같은 새 불변량이 필요해요.",
            en={
                "concepts": ["round-robin table", "win-loss invariant"],
                "statement": f"{n} teams (A through {last_en}) finished a round-robin league in which every pair of teams played exactly once, and no game ended in a draw. Team {last_en}'s row of the results table is torn off. "
                f"The remaining records are: {known_en}. How many games did Team {last_en} win?",
                "answer": _en_plural(ans, "win"),
                "distractors": ["It cannot be determined", _en_plural(ans + 1, "win"), _en_plural(losses, "win")],
                "explanation": f"With no draws, every game that finishes produces exactly one 'win'. So no matter how the games went, all the teams' wins add up to the total number of games. "
                f"With {n} teams each playing each other once, that's {n}×({n}−1)÷2={games} games; the visible {n - 1} teams have {ks} wins in all, so Team {last_en} won {games}−{ks}={ans}.",
                "mistakes": [("It cannot be determined", "You don't need each game's result. Every game creates exactly one win, so the hidden rule 'sum of all wins = number of games' pins the answer down."),
                             (_en_plural(ans + 1, "win"), f"The total game count slipped by one. {n} teams each playing each other once gives {n}×({n}−1)÷2={games} games — check you didn't double-count or drop a game."),
                             (_en_plural(losses, "win"), f"Wins and losses got swapped. Team {last_en} played {n - 1} games, so {ans} wins means {losses} losses — the question asks for wins.")],
                "detail": f"The torn table can be restored because there is a quantity that never changes no matter how the games went: the total of wins grows by exactly 1 per game, so it always equals the number of games — such a quantity is called an invariant. "
                f"Looking back: you can double-check with losses too. The losses must also total {games}: the visible teams' {lsum} losses plus Team {last_en}'s {losses} losses is exactly {games}. "
                f"Generalizing: in a league that allows draws, wins alone aren't conserved — you'd need a new invariant like the total of 'wins + draws÷2'.",
            },
        )


# ── 143. 중단된 시합의 공정한 상금 나누기 — 미래의 경우 세기 (난7, 자료와가능성) ────
def gen_fair_split():
    # 발견형 자기검증: 분배 기준(우승 가능성 비례)은 문제문에 있지만 그 가능성을 '구하는 방법' —
    # 길이가 서로 다른 미래들을 같은 길이로 마저 진행한다고 상상해 동등하게 세는 전략 — 은 스스로
    # 발견해야 한다(기준1 통과). 남은 판 수가 두 사람에게 달라 단순 나열은 가능성이 다른 갈래를
    # 뒤섞기 쉽고, 두 판 더 필요한 (3,1,0)벌은 나열 우회가 사실상 불가하다(기준2 통과).
    from fractions import Fraction
    from itertools import product
    for (na, nb), goal, a, b, prize in [
        (("민준", "서연"), 3, 2, 1, 1200),
        (("지호", "하은"), 3, 2, 0, 1200),
        (("도윤", "예린"), 4, 3, 2, 1500),
        (("시우", "지아"), 3, 1, 0, 1600),
    ]:
        need_a, need_b = goal - a, goal - b
        length = need_a + need_b - 1  # 이만큼이면 반드시 승부가 난다
        tot = 2 ** length
        cnt = sum(1 for seq in product((0, 1), repeat=length) if sum(seq) >= need_a)
        assert prize * cnt % tot == 0, "fairsplit 파라미터 오류: 금액이 나누어떨어지지 않음"
        ans = prize * cnt // tot
        # 검산: 고정 길이 세기(정답 경로)와 독립으로, '이긴 사람이 나오면 즉시 멈추는' 실제 시합
        # 나무를 분수 확률로 재귀 계산해 몫이 일치하는지 확인.
        def _chance(x, y):
            if x == 0:
                return Fraction(1)
            if y == 0:
                return Fraction(0)
            return (_chance(x - 1, y) + _chance(x, y - 1)) / 2
        assert _chance(need_a, need_b) * prize == ans, "fairsplit 검산 실패: 게임나무 확률 불일치"
        prop = prize if b == 0 else prize * a // (a + b)
        wrongs = [f"{prop}원", f"{prize // 2}원", f"{prize - ans}원"]
        assert len({ans, prop, prize // 2, prize - ans}) == 4, "fairsplit 파라미터 오류: 보기 중복"
        prop_mis = (f"{prize}원", f"{na}{_iga(na)} 앞서고 있어도 시합은 아직 끝나지 않았어요. {nb}{_iga(nb)} 남은 판을 내리 이겨 역전할 가능성({tot}가지 중 {tot - cnt}가지)이 있는 만큼은 {nb}의 몫이에요.") if b == 0 else \
            (f"{prop}원", f"지금까지의 승수 {a}:{b}에 비례해 나눈 값이에요. 상금은 '이미 이긴 판 수'가 아니라 '남은 시합에서 우승할 가능성'에 비례해야 해요 — 뒤집힐 가능성까지 세어야 공정해요.")
        prop_mis_en = (f"{prize} won", f"Even though A is ahead, the match is not over. B could still win every remaining round ({tot - cnt} of the {tot} futures) — that much belongs to B.") if b == 0 else \
            (f"{prop} won", f"That splits by the current score {a}:{b}. The prize should follow each player's chance of winning the rest of the match — you must count the comeback futures too.")
        add(
            "fairsplit", "DATA_POSSIBILITY", 7, ["공정한 분배", "앞으로의 경우 세기"],
            f"{na}{_gwa(na)} {nb}{_iga(nb)} 구슬치기 시합을 해요. 한 판마다 두 사람이 이길 가능성은 똑같고, 먼저 {goal}판을 이기는 사람이 상금 {prize}원을 모두 갖기로 했어요. "
            f"그런데 {na}{_iga(na)} {a}판, {nb}{_iga(nb)} {b}판을 이긴 상태에서 시합이 중단되었고 다시 열 수 없게 되었어요. "
            f"두 사람은 '시합을 계속했다면 우승했을 가능성'에 비례해 상금을 나누기로 했어요. {na}{_iga(na)} 받을 금액은 얼마일까요?",
            f"{ans}원", wrongs,
            f"남은 시합을 상상해요. {na}{_eun(na)} {need_a}판, {nb}{_eun(nb)} {need_b}판만 더 이기면 우승이니, 앞으로 {length}판이면 반드시 승부가 나요. "
            f"이 {length}판을 (승부가 나더라도) 끝까지 다 한다고 가정하면 매 판 2갈래씩 모두 {tot}가지 미래가 똑같은 가능성으로 일어나요. "
            f"{na}{_iga(na)} 우승하는 미래는 {length}판 중 {need_a}판 이상 이기는 경우로 {cnt}가지예요({need_a}판을 못 채우면 남은 판을 {nb}{_iga(nb)} 다 가져가 {need_b}판이 되니까요). "
            f"그래서 {na}의 몫은 {prize}×{cnt}/{tot}={ans}원이에요.",
            [prop_mis,
             (f"{prize // 2}원", f"반반으로 나누면 {na}{_iga(na)} 이미 쌓아 둔 우세({a}승 대 {b}승)를 없는 셈 치는 거예요."),
             (f"{prize - ans}원", f"그건 {nb}의 몫이에요. 남은 미래 {tot}가지 중 {na}{_iga(na)} 우승하는 경우가 {cnt}가지로 더 많아요.")],
            detail=f"일찍 끝나는 미래(다음 한 판으로 끝)와 오래 가는 미래는 길이가 달라, 그대로 나열해 세면 가능성이 서로 다른 갈래를 같은 한 가지로 세게 돼요. 그래서 '승부가 나도 {length}판을 마저 한다'고 상상하는 것이 "
            f"열쇠예요 — 우승자는 바뀌지 않으면서 모든 갈래가 똑같은 가능성이 되거든요. 되돌아보기: 두 사람 몫을 더하면 {ans}+{prize - ans}={prize}원으로 상금 전체와 딱 맞아요. "
            f"이 '중단된 시합' 문제는 1654년 파스칼과 페르마가 편지를 주고받으며 풀었던, 확률이라는 수학이 태어난 바로 그 문제예요.",
            en={
                "concepts": ["fair division", "counting future outcomes"],
                "statement": f"A and B are playing a marble match. In each round the two are equally likely to win, and the first to win {goal} rounds takes the whole prize of {prize} won. "
                f"But the match was interrupted — with A having won {a} rounds and B {b} — and can never be resumed. "
                f"They agree to split the prize in proportion to each player's chance of winning had the match continued. How much should A receive?",
                "answer": f"{ans} won",
                "distractors": [f"{prop} won", f"{prize // 2} won", f"{prize - ans} won"],
                "explanation": f"Imagine the remaining rounds. A needs {need_a} more wins and B needs {need_b}, so {length} more rounds always settle it. "
                f"Pretend those {length} rounds are all played out (even after someone clinches): each round branches in 2, giving {tot} equally likely futures. "
                f"A becomes champion in the futures where A wins at least {need_a} of the {length} rounds — {cnt} of them (if A falls short, B takes enough rounds to reach {need_b}). "
                f"So A's share is {prize}×{cnt}/{tot}={ans} won.",
                "mistakes": [prop_mis_en,
                             (f"{prize // 2} won", f"Splitting half-and-half ignores the lead A has already built ({a} wins to {b})."),
                             (f"{prize - ans} won", f"That is B's share. Of the {tot} remaining futures, A wins in {cnt} — the majority.")],
                "detail": f"A future that ends early (one more round) and a long future have different lengths, so listing them as-is mixes branches of different likelihood. The key is to imagine playing all {length} rounds even after the match is decided — "
                f"the champion never changes, and every branch becomes equally likely. Looking back: the two shares add to {ans}+{prize - ans}={prize} won, exactly the whole prize. "
                f"This 'interrupted match' is the very problem Pascal and Fermat solved in their 1654 letters — the birth of probability.",
            },
        )


# ── 144. 지그재그 배열 세기 — 봉우리·골짜기 교대 (난8, 자료와가능성) ───────────────
def gen_zigzag():
    # 발견형 자기검증: 세기 전략이 문제문에 없고(기준1 통과), n≥6은 손 나열(720가지 이상)이
    # 불가능해 '최댓값은 봉우리에만 선다 → 양옆이 같은 꼴의 작은 문제'라는 구조 분해 발견이
    # 필수다(기준2 통과 — n=5가 진입 문항). CEILING_SPECS 3.10 명세 구현.
    from itertools import permutations
    expected = {5: 16, 6: 61, 7: 272, 8: 1385}
    for n in [5, 6, 7, 8]:
        # 검산: n! 순열 완전열거 필터 — 명세의 검산 완료 표(16·61·272·1385)와 독립 대조
        cnt = sum(1 for p in permutations(range(1, n + 1)) if all((p[i] < p[i + 1]) == (i % 2 == 0) for i in range(n - 1)))
        assert cnt == expected[n], "zigzag 검산 실패"
        ans = expected[n]
        half = factorial(n) // 2
        pw = 2 ** (n - 2)
        add(
            "zigzag", "DATA_POSSIBILITY", 8, ["교대 배열", "체계적 세기"],
            f"1부터 {n}까지의 수를 한 번씩 모두 써서 한 줄로 배열해요. 이웃한 수끼리 반드시 '작다, 크다, 작다, 크다, …'를 번갈아 만족해야 해요"
            f"(첫째 수 < 둘째 수 > 셋째 수 < 넷째 수 …). 이런 배열은 모두 몇 가지일까요?",
            f"{ans}가지", [f"{factorial(n)}가지", f"{half}가지", f"{pw}가지"],
            f"작은 수로 직접 실험해요: 3개면 132, 231의 2가지, 4개면 5가지예요. 나열하다 보면 규칙이 보여요 — 가장 큰 수 {n}{_eun(n)} 양옆보다 커야 하므로 "
            f"반드시 '봉우리'(둘째, 넷째, … 자리)에만 설 수 있어요. {n}{_eul(n)} 어느 봉우리에 놓을지 정하면 나머지 수들이 그 양옆에서 다시 같은 꼴의 작은 지그재그 문제로 "
            f"갈라져요. 작은 답을 차곡차곡 조립해 올라가면 {n}개일 때는 모두 {ans}가지예요.",
            [(f"{factorial(n)}가지", "조건 없이 전부 센 값이에요. '작다-크다' 교대 조건으로 걸러야 해요."),
             (f"{half}가지", "절반쯤 될 거라는 어림이에요. 조건은 자리마다 겹쳐 작동해서 훨씬 강하게 걸러요."),
             (f"{pw}가지", "자리마다 독립적으로 2가지씩 고를 수 있다고 본 어림이에요. 이미 쓴 수는 다시 못 쓰니 독립이 아니에요.")],
            detail=f"가장 큰 수는 반드시 봉우리에 서고, 그 수를 기준으로 배열이 두 개의 독립한 지그재그로 갈라져요 — 큰 문제를 같은 모양의 작은 문제로 쪼개는 눈이 이 문제의 심장이에요. "
            f"되돌아보기: 4개짜리를 직접 나열하면 1324, 1423, 2314, 2413, 3412의 5가지 — 조립 논리와 정확히 맞아요. "
            f"일반화: '크다-작다'로 시작하는 배열은 몇 가지일까요? 배열을 통째로 뒤집으면 1:1로 짝지어지니 똑같이 {ans}가지예요.",
            en={
                "concepts": ["alternating arrangement", "systematic counting"],
                "statement": f"Arrange the numbers 1 to {n} in a row, each used once, so that they strictly alternate 'up, down, up, down, …' "
                f"(1st < 2nd > 3rd < 4th …). How many such arrangements are there?",
                "answer": _en_plural(ans, "arrangement"),
                "distractors": [_en_plural(factorial(n), "arrangement"), _en_plural(half, "arrangement"), _en_plural(pw, "arrangement")],
                "explanation": f"Experiment small: with 3 numbers there are 2 (132, 231), with 4 there are 5. A rule emerges — the largest number {n} must be bigger than both neighbors, "
                f"so it can only stand on a 'peak' (2nd, 4th, … position). Once you fix which peak {n} takes, the remaining numbers split into two smaller zigzag problems of the same kind "
                f"on either side. Assembling the small answers upward gives {ans} arrangements for {n} numbers.",
                "mistakes": [(_en_plural(factorial(n), "arrangement"), "That counts everything with no condition. You must filter by the alternating 'up-down' condition."),
                             (_en_plural(half, "arrangement"), "That's a guess that about half survive. The conditions overlap position by position and filter far more strongly."),
                             (_en_plural(pw, "arrangement"), "That assumes an independent 2-way choice at each position. Numbers already used can't be reused, so the choices aren't independent.")],
                "detail": f"The largest number must stand on a peak, and it splits the arrangement into two independent zigzags — seeing how to break a big problem into same-shaped smaller ones is the heart of this problem. "
                f"Looking back: listing the 4-number case by hand gives exactly 1324, 1423, 2314, 2413, 3412 — five, matching the assembly logic. "
                f"Generalizing: how many arrangements start 'down, up, …'? Reversing each arrangement pairs them 1:1, so it's the same {ans}.",
            },
        )


# ── 145. 자기 지시 진술 — 거짓말쟁이는 몇 명일까 (난9, 자료와가능성) ───────────────
def gen_liarcount():
    # 발견형 자기검증: '거짓말쟁이 수 L을 통째로 가정하고 일치 조건을 세운다'는 전략이 문제문에
    # 없고(기준1 통과), 무작정 배정을 나열하면 2^n가지라 체계적 발견 없이는 확신에 도달할 수
    # 없다(기준2 통과). atleast형은 n 짝수만 사용(홀수는 해 없음 — 아래 assert가 지킨다).
    # CEILING_SPECS 3.9 명세 구현.
    from itertools import product
    for kind, n, expected, mid in [("exact", 5, 4, 3), ("exact", 6, 5, 3), ("atleast", 6, 3, 2), ("atleast", 8, 4, 3)]:
        assert kind == "exact" or n % 2 == 0, "liarcount 파라미터 오류: atleast형은 n 짝수만"
        # 검산: 2^n 배정 완전열거 — 모순 없는 배정이 정확히 1개이고 그 거짓말쟁이 수가 기대값과 일치
        sols, assign = [], None
        for bits in product((0, 1), repeat=n):  # 1 = 거짓말쟁이
            liars = sum(bits)
            if all(((liars == i) if kind == "exact" else (liars >= i)) == (bits[i - 1] == 0) for i in range(1, n + 1)):
                sols.append(liars)
                assign = bits
        assert len(sols) == 1 and sols[0] == expected, "liarcount 검산 실패"
        ans = sols[0]
        honest = [i for i in range(1, n + 1) if assign[i - 1] == 0]
        honest_txt = "·".join(f"{i}번" for i in honest)
        if kind == "exact":
            claim = f'i번 사람: "우리 {n}명 중 거짓말쟁이는 정확히 i명이다."'
            claim_en = '"Exactly i of us are liars"'
            step3 = (f"서로 다른 수를 말했으니 참말은 많아야 1명이에요. 전원 거짓(L={n})이면 '{n}명'이라고 말한 {n}번의 말이 참이 되어 모순이니, "
                     f"정직한 사람은 딱 1명이고 거짓말쟁이는 {n - 1}명 — 참말은 '{n - 1}명'을 말한 {honest_txt}뿐이에요. 그래서 {ans}명이에요.")
            step3_en = (f"They all claim different numbers, so at most 1 statement is true. If everyone lied (L={n}), person {n}'s claim of '{n}' would become true — a contradiction. "
                        f"So exactly 1 person is honest and {n - 1} are liars — the only true statement is person {n - 1}'s '{n - 1}'. The answer is {ans}.")
            mis0 = ("서로 다른 수를 말했으니 동시에 모두 참일 수는 없어요. 전원 정직은 첫 문장부터 모순이에요.",
                    "They all claim different numbers, so the statements can't all be true at once. Everyone honest breaks down at the very first sentence.")
            misn = (f"전원이 거짓말쟁이라면 '{n}명이 거짓말쟁이'라고 말한 {n}번의 말이 참이 되어 모순이에요.",
                    f"If everyone were a liar, person {n}'s claim that '{n} of us are liars' would be true — a contradiction.")
            look = (f"되돌아보기: {honest_txt}만 정직인 배정을 1번부터 {n}번까지 다시 읽으며 모순이 없는지 확인해요. 일반화: 진술을 '적어도 i명'으로 바꾸면 답이 절반({n}÷2)으로 내려가는데, "
                    f"인원이 홀수면 아예 답이 없어요 — 왜 그런지 생각해 보세요.")
            look_en = (f"Looking back: reread persons 1 through {n} under the assignment where only person {honest[0]} is honest and check there is no contradiction. Generalizing: with 'at least i' statements the answer drops to half, "
                       f"and with an odd number of people there is no answer at all — think about why.")
        else:
            claim = f'i번 사람: "우리 {n}명 중 거짓말쟁이는 적어도 i명이다."'
            claim_en = '"At least i of us are liars"'
            step3 = (f"'적어도 i명'은 i가 작을수록 참이 되기 쉬워요. 거짓말쟁이가 L명이라면 1번부터 L번까지의 말이 참, 그 뒤는 거짓이에요. 참말한 사람(정직)의 수는 {n}−L이어야 하니 "
                     f"L = {n}−L, 즉 L = {ans}명 — 앞 절반({honest_txt})이 정직, 뒤 절반이 거짓말쟁이일 때만 아귀가 맞아요.")
            step3_en = (f"'At least i' is easier to be true the smaller i is. If there are L liars, the statements of persons 1 through L are true and the rest are false. The number of true speakers (honest people) must be {n}−L, "
                        f"so L = {n}−L, that is L = {ans} — it only fits when the front half (persons 1–{ans}) are honest and the back half are liars.")
            mis0 = (f"전원이 정직하다면 '적어도 {n}명이 거짓말쟁이'라는 {n}번의 말도 참이어야 하는데, 거짓말쟁이가 0명이라 모순이에요.",
                    f"If everyone were honest, person {n}'s claim 'at least {n} of us are liars' would also have to be true — but there would be 0 liars, a contradiction.")
            misn = ("전원이 거짓말쟁이라면 '적어도 1명이 거짓말쟁이'라고 한 1번의 말이 참이 되어 모순이에요.",
                    "If everyone were a liar, person 1's claim 'at least 1 of us is a liar' would be true — a contradiction.")
            look = (f"되돌아보기: 1번~{ans}번 정직, {ans + 1}번~{n}번 거짓인 배정을 처음부터 재검증해요. 일반화: 인원이 홀수면 '참말한 수 = 정직한 수'가 절반으로 떨어지지 않아 "
                    f"모순 없는 배정이 아예 없어요 — 이 수수께끼는 짝수 인원에서만 성립해요.")
            look_en = (f"Looking back: verify the assignment (persons 1–{ans} honest, {ans + 1}–{n} liars) from the start. Generalizing: with an odd number of people, 'true statements = honest people' can't split in half, "
                       f"so no consistent assignment exists — this riddle only works with an even count.")
        add(
            "liarcount", "DATA_POSSIBILITY", 9, ["자기 지시 논리", "모순 없는 배정"],
            f"{n}명이 한 줄로 서 있어요. 각 사람은 언제나 진실만 말하거나 언제나 거짓만 말해요. 1번부터 {n}번까지 차례로 이렇게 말했어요 — {claim} "
            f"(1번은 1명, 2번은 2명, … {n}번은 {n}명이라고 말한 거예요.) 거짓말쟁이는 실제로 몇 명일까요?",
            f"{ans}명", [f"{n}명", "0명", f"{mid}명"],
            f"'누가' 거짓말쟁이인지 대신 '몇 명'인지를 통째로 가정해요. 거짓말쟁이 수를 L이라 하면 각 사람 말의 참/거짓이 자동으로 정해지고, "
            f"'참말한 사람 수 = 정직한 사람 수({n}−L)'라는 일치 조건이 L을 골라내요. {step3}",
            [(f"{n}명", misn[0]),
             ("0명", mis0[0]),
             (f"{mid}명", f"{mid}명으로 가정하고 각 사람의 말을 하나씩 참/거짓 판정해 보세요. 어딘가에서 '정직한 사람이 거짓을 말함' 같은 모순이 나와요.")],
            detail=f"이 문제의 묘미는 진술이 거짓말쟁이 '수' 자체를 가리키는 자기 지시 구조예요. 사람별로 따지면 얽혀서 풀리지 않지만, 수 L을 가정하는 순간 "
            f"모든 진술의 참/거짓이 한꺼번에 결정돼요 — 가정 하나로 전체를 판정하는 힘이에요. {look}",
            en={
                "concepts": ["self-referential logic", "consistent assignment"],
                "statement": f"{n} people stand in a row. Each one always tells the truth or always lies. From person 1 to person {n}, each says: {claim_en} "
                f"(person i says the number i — person 1 says 1, person 2 says 2, and so on). How many of them are actually liars?",
                "answer": _en_plural(ans, "liar"),
                "distractors": [_en_plural(n, "liar"), _en_plural(0, "liar"), _en_plural(mid, "liar")],
                "explanation": f"Instead of asking 'who' lies, assume 'how many' all at once. If there are L liars, the truth of every statement is decided automatically, "
                f"and the matching condition 'number of true speakers = number of honest people ({n}−L)' singles out L. {step3_en}",
                "mistakes": [(_en_plural(n, "liar"), misn[1]),
                             (_en_plural(0, "liar"), mis0[1]),
                             (_en_plural(mid, "liar"), f"Assume {mid} liars and judge each statement true or false one by one. Somewhere you'll hit a contradiction like 'an honest person telling a lie'.")],
                "detail": f"The charm of this problem is its self-reference: the statements point at the very number of liars. Person-by-person reasoning tangles up, but the moment you assume the number L, "
                f"the truth of every statement is decided at once — one assumption judges the whole row. {look_en}",
            },
        )


# ── 146. 파스칼 삼각형 줄의 홀수 개수 — 홀짝 자기닮음 (난10, 자료와가능성) ──────────
def gen_pascalodd():
    # 발견형 자기검증: 패턴 규칙이 문제문에 없고 색칠 실험→자기닮음 발견이 유일한 통로이며(기준1
    # 통과), 100번째 줄은 직접 구성이 불가능한 크기다(기준2 통과 — n=16이 진입 문항, 그마저 답
    # '2개'가 직관을 배신한다). CEILING_SPECS 3.8 명세 구현.
    for n, expected in [(16, 2), (15, 16), (100, 8), (63, 64)]:
        # 검산: 덧셈으로 줄을 직접 구성해 홀수를 세고(이항계수 공식을 쓰지 않는 길),
        # 독립 공식 2^(이진법 1의 개수)와 교차 대조.
        row = [1]
        for _ in range(n):
            row = [1] + [p + q for p, q in zip(row, row[1:])] + [1]
        odd = sum(1 for v in row if v % 2 == 1)
        bits = bin(n).count("1")
        assert odd == expected and odd == 2 ** bits and len(row) == n + 1, "pascalodd 검산 실패"
        ans = expected
        d1 = n if ans == n + 1 else n + 1  # 항 수·줄 번호 혼동(전부 홀수인 줄에서는 n으로)
        d2 = (n + 1) // 2
        binstr = bin(n)[2:]
        add(
            "pascalodd", "DATA_POSSIBILITY", 10, ["파스칼 삼각형", "홀짝 패턴"],
            f"수 삼각형을 만들어요. 맨 위 0번째 줄에는 1 하나만 있어요. 그 아래 줄부터는 양 끝에 1을 쓰고, 나머지 자리는 바로 위의 두 수를 더해 써요(파스칼 삼각형). "
            f"{n}번째 줄에 있는 {n + 1}개의 수 가운데 홀수는 모두 몇 개일까요?",
            f"{ans}개", [f"{d1}개", f"{d2}개", f"{bits}개"],
            f"처음 몇 줄을 직접 만들어 홀수 자리만 색칠해 봐요. 줄마다 홀수 개수를 세면 1, 2, 2, 4, 2, 4, 4, 8, 2, …로 언제나 '2를 몇 번 곱한 수'만 나와요. "
            f"언제 두 배가 되는지 줄 번호를 2씩 묶어(이진법으로) 적어 보면, 기록에 1이 하나 늘 때마다 홀수 개수가 정확히 두 배가 돼요. "
            f"{n}{_eul(n)} 이진법으로 쓰면 {binstr}(2) — 1이 {bits}개이니, 홀수는 2를 {bits}번 곱한 {ans}개예요.",
            [(f"{d1}개", "몇 '개'인지와 몇 '번째 줄'인지를 혼동했어요. 줄을 몇 개 그려 홀짝만 표시해 보세요."),
             (f"{d2}개", "홀짝이 반반일 거라는 어림이에요. 실제로는 훨씬 치우쳐요 — 홀수 개수는 항상 2를 몇 번 곱한 수예요."),
             (f"{bits}개", "그 수는 '2를 곱하는 횟수'예요. 답은 2를 그만큼 거듭 곱한 값이에요.")],
            detail=f"홀수 자리만 남기면 삼각형이 자기 자신을 닮은 세 조각으로 계속 갈라져요(시에르핀스키 삼각형) — 윗부분의 복사본 두 개가 아래 양쪽에 다시 나타나서, "
            f"줄 번호의 이진법 기록에 1이 하나 늘 때마다 홀수 자리가 정확히 두 배가 되기 때문이에요. 되돌아보기: 15번째 줄을 홀짝만으로 직접 만들어 보세요"
            f"(홀+홀=짝, 홀+짝=홀 규칙만 쓰면 금방이에요) — 정말 16개 전부가 홀수예요. 일반화: 홀수가 딱 2개뿐인 줄은? 2, 4, 8, 16, … 처럼 2를 거듭 곱한 번호의 줄이에요.",
            en={
                "concepts": ["Pascal's triangle", "parity pattern"],
                "statement": f"Build a number triangle: row 0 at the top is a single 1. In each row below, write 1 at both ends, and fill every other spot with the sum of the two numbers just above it (Pascal's triangle). "
                f"Among the {n + 1} numbers in row {n}, how many are odd?",
                "answer": _en_plural(ans, "odd number"),
                "distractors": [_en_plural(d1, "odd number"), _en_plural(d2, "odd number"), _en_plural(bits, "odd number")],
                "explanation": f"Build the first several rows and color only the odd entries. Counting odds per row gives 1, 2, 2, 4, 2, 4, 4, 8, 2, … — always a power of 2. "
                f"To see when it doubles, write the row number in base 2: each extra 1 in that record exactly doubles the count of odd entries. "
                f"{n} in binary is {binstr}, which has {bits} ones — so the count of odd entries is 2 multiplied {bits} times: {ans}.",
                "mistakes": [(_en_plural(d1, "odd number"), "You mixed up 'how many entries' with 'which row'. Draw a few rows and mark only odd/even."),
                             (_en_plural(d2, "odd number"), "That guesses odd and even split about half-and-half. In reality it's far more lopsided — the count of odds is always a power of 2."),
                             (_en_plural(bits, "odd number"), "That number is 'how many times to multiply by 2'. The answer is 2 multiplied that many times.")],
                "detail": f"Keep only the odd entries and the triangle keeps splitting into three self-similar copies of itself (the Sierpinski triangle) — two copies of the top part reappear at the bottom left and right, "
                f"which is why each extra 1 in the row number's binary record exactly doubles the odd entries. Looking back: build row 15 using only parity (odd+odd=even, odd+even=odd — it's quick) and see that all 16 entries really are odd. "
                f"Generalizing: which rows have exactly 2 odd entries? Rows 2, 4, 8, 16, … — the powers of 2.",
            },
        )
