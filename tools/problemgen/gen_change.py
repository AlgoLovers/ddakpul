"""변화와 관계(CHANGE_RELATION) 제너레이터 — 함수 1개 = 방법(family) 1개 = 문제 그룹.

실행 순서는 build.py의 GENERATORS 리스트가 정한다(rng 재현성). 여기선 정의만.
"""
from core import *  # noqa: F401,F403 — 공용 인프라(add·rng·헬퍼·상수)



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
                    # 검산(age): 딸 나이 후보 전 범위 완전탐색으로 해를 재발견 — 조건 만족 해가 child 하나뿐인지
                    full = [c for c in range(1, 200) if k * c + t == m * (c + t)]
                    assert full == [child] and parent == k * child, f"age 검산 실패: {full} != [{child}]"
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
        # 검산(tree): 0m부터 끝까지 가로등 위치를 실제로 나열해 개수 세기(양 끝 포함)
        posts = list(range(0, length + 1, gap))
        assert length % gap == 0 and posts[-1] == length and len(posts) == g + 1, f"tree 검산 실패: {len(posts)}"
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
    # 검산(tree·원형): 둘레 위 심는 지점(0~둘레 직전)을 실제로 나열 — 끝이 곧 처음이라 간격 수 = 나무 수
    ring = list(range(0, length, gap))
    assert length % gap == 0 and len(ring) == g, f"tree 원형 검산 실패: {len(ring)}"
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
        # 검산(log): 한 번 자를 때마다 도막이 1개 늘어나는 과정을 실제로 시뮬레이션
        pcs, minutes = 1, 0
        while pcs < pieces:
            pcs += 1
            minutes += per
        assert minutes == ans, f"log 검산 실패: {minutes} != {ans}"
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


# ── 13. 반복 주기 (난2, 변화와관계) ──────────────────────────────────────────
def gen_cycle():
    for colors, n in [(COLORS3[0], 50), (COLORS3[1], 74), (COLORS3[0] + ["초록"], 90), (COLORS3[1] + ["분홍"], 66)]:
        k = len(colors)
        pos = (n - 1) % k
        ans = colors[pos]
        wrongs = [c for c in colors if c != ans][:2] + ["알 수 없다"]
        # 검산(cycle): 1번째부터 n번째까지 구슬을 실제로 하나씩 꿰어 n번째 색 확인
        idx = 0
        for _ in range(n):
            bead = colors[idx]
            idx = (idx + 1) % k
        assert bead == ans, f"cycle 검산 실패: {bead} != {ans}"
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
            en={
                "statement": f"There are {total_stones} go stones. Two players take turns removing 1 to {k} stones at a time, and whoever takes the last stone wins. To be sure of winning, how many stones should the first player take on the very first move?",
                "answer": _en_plural(ans, "stone"),
                "distractors": [_en_plural(k, "stone"), _en_plural(ans - 1, "stone"), _en_plural(ans + 2, "stone")],
                "explanation": f"The key is to leave your opponent a 'multiple of {k + 1}'. Then whatever number from 1 to {k} they take, you take the rest to make {k + 1} together, again leaving a multiple of {k + 1}. {total_stones} divided by {k + 1} leaves remainder {ans}, so taking {ans} first leaves {total_stones - ans} (a multiple of {k + 1}) and you are sure to win.",
                "mistakes": [(_en_plural(k, "stone"), "Grabbing the maximum blindly is wrong. The key is leaving your opponent a 'multiple'.")],
                "detail": f"Why is 'leaving a multiple of {k + 1}' a guaranteed win? If you leave that multiple, then when the opponent takes t stones (1 to {k}) you take {k + 1}−t, erasing exactly {k + 1} each round. So it goes multiple→multiple→…→0, and the last stone is always yours! Conversely, if the stone count starts as a multiple of {k + 1} (remainder 0), the first player loses. This method of 'answering the opponent's move to keep the sum constant' is called a symmetry strategy.",
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
        # 검산(subst): A 1개 = B k1개의 B 하나하나를 C k2개로 바꿔 가며 실제로 세기(반복 덧셈)
        c_total = 0
        for _ in range(k1):
            c_total += k2
        assert c_total == ans, f"subst 검산 실패: {c_total} != {ans}"
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


# ── 63. 최소공배수 — 동시 출발 (난4, 변화와관계) ─────────────────────────────
def gen_lcm_together():
    for a, b in [(4, 6), (6, 8), (9, 12), (10, 15)]:
        lcm = a * b // gcd(a, b)
        # 검산(lcmbus): 1분씩 시간을 흘려 두 배수가 처음 겹치는 시각을 직접 탐색
        t = 1
        while t % a != 0 or t % b != 0:
            t += 1
        assert t == lcm, f"lcmbus 검산 실패: {t} != {lcm}"
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


# ── 72. 비로 나누기 (난5, 변화와관계) ────────────────────────────────────────
def gen_ratio_share():
    for total, r1, r2 in [(20, 3, 2), (35, 4, 3), (24, 5, 1), (40, 3, 5)]:
        assert total % (r1 + r2) == 0
        unit = total // (r1 + r2)
        part = unit * r1
        add(
            # 난이도 재조정(5→4, 2026-07 d1~5 스캔): 2항 비는 ratio3보다 한 단계 아래.
            "ratioshare", "CHANGE_RELATION", 4, ["비", "단위량 먼저"],
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


# ── 78. N일 뒤 요일 — 나머지 (난4, 변화와관계) ───────────────────────────────
def gen_day_of_week():
    days = ["일", "월", "화", "수", "목", "금", "토"]
    days_en = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    for start, ahead in [(1, 100), (3, 50), (5, 30), (2, 365)]:
        end = (start + ahead) % 7
        # 검산(dow): 하루씩 ahead일을 실제로 세어 도착 요일 확인
        d = start
        for _ in range(ahead):
            d = (d + 1) % 7
        assert d == end, f"dow 검산 실패: {d} != {end}"
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
        # 검산(frog): 시뮬레이션과 별도로 '마지막 도약 먼저 빼기' 공식으로 재계산
        assert up > down and depth > up, f"frog 전제 위반: {depth}m/{up}m/{down}m"
        formula = (depth - up + net - 1) // net + 1
        assert formula == ans, f"frog 검산 실패: {formula} != {ans}"
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


# ── 84. 사각수 (난4, 변화와관계) ─────────────────────────────────────────────
def gen_square_numbers():
    for k in [5, 6, 7, 8]:
        ans = k * k
        # 검산(squarenum): 정사각형을 ㄱ자(홀수)씩 실제로 키워 가며 세기 — 1+3+5+…
        dots = 0
        for i in range(1, k + 1):
            dots += 2 * i - 1
        assert dots == ans, f"squarenum 검산 실패: {dots} != {ans}"
        add(
            # 난이도 재조정(4→2, 2026-07 d1~5 스캔): 규칙 n×n이 지문에 명시 — 발견 요소 없음.
            "squarenum", "CHANGE_RELATION", 2, ["규칙", "사각수"],
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
        # 검산(trinum): 1층부터 k층까지 실제로 한 층씩 더해 보기
        balls = 0
        for i in range(1, k + 1):
            balls += i
        assert balls == ans, f"trinum 검산 실패: {balls} != {ans}"
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
        # 검산(pow2): 한 번 접을 때마다 2배가 되는 과정을 실제로 n번 반복
        layers = 1
        for _ in range(n):
            layers *= 2
        assert layers == ans, f"pow2 검산 실패: {layers} != {ans}"
        add(
            # 난이도 재조정(6→3, 2026-07 d6 감사): 2^n 단일 거듭제곱.
            "pow2", "CHANGE_RELATION", 3, ["거듭제곱", "2배씩 커지기"],
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


# ── 92. 소금물 농도 (난6, 변화와관계) ────────────────────────────────────────
def gen_salt_concentration():
    for water, salt in [(90, 10), (80, 20), (150, 50), (85, 15)]:
        total = water + salt
        assert (salt * 100) % total == 0
        ans = salt * 100 // total
        add(
            # 난이도 재조정(6→3, 2026-07 d6 감사): 소금/전체 단일 나눗셈 — 기초 백분율.
            "concn", "CHANGE_RELATION", 3, ["농도", "비율"],
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
        # 검산(transfer): 처음 차이 dd를 전 범위 탐색 — give개 준 뒤 같아지는 dd를 재발견(유일성 포함)
        sols = [dd for dd in range(0, 10 * give + 1) if (100 + dd) - give == 100 + give]
        assert sols == [ans], f"transfer 검산 실패: {sols} != [{ans}]"
        en_item = {"구슬": "marbles", "사탕": "candies", "딱지": "cards", "스티커": "stickers"}[ctx]
        add(
            # 난이도 재조정(5→4, 2026-07 d1~5 스캔): '주면 차이가 2배로' 단일 통찰.
            "transfer", "CHANGE_RELATION", 4, ["차이 사고", "주고받기"],
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


# ── 104. 컵 쌓기 = 등차 (난4, 변화와관계) ────────────────────────────────────
def gen_stacking_cups():
    for base, add_each, n in [(10, 3, 5), (12, 4, 6), (8, 2, 10), (15, 5, 4)]:
        ans = base + add_each * (n - 1)
        # 검산(cups): 컵을 실제로 하나씩 포개며 높이 누적
        height = base
        for _ in range(n - 1):
            height += add_each
        assert height == ans, f"cups 검산 실패: {height} != {ans}"
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
        # 검산(numline): 앞으로·뒤로 뛰기를 rounds회 실제로 시뮬레이션
        pos = start
        for _ in range(rounds):
            pos += fwd
            pos -= back
        assert pos == ans, f"numline 검산 실패: {pos} != {ans}"
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
        # 검산(dblsale): 할인액을 각각 구해 빼는 다른 경로로 재계산 + 정수 나눗셈 버림 없음 확인
        assert price * (100 - d1) % 100 == 0 and after1 * (100 - d2) % 100 == 0, "dblsale 검산 실패: 버림 발생"
        step1 = price - price * d1 // 100
        step2 = step1 - step1 * d2 // 100
        assert step2 == ans, f"dblsale 검산 실패: {step2} != {ans}"
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


# ── 118. 소금물 섞기 = 가중평균 (난7, 변화와관계) ───────────────────────────
def gen_mixture():
    for w1, c1, w2, c2 in [(200, 10, 300, 20), (100, 20, 400, 10), (300, 10, 200, 20), (100, 8, 300, 16)]:
        salt = w1 * c1 // 100 + w2 * c2 // 100
        total = w1 + w2
        assert (salt * 100) % total == 0
        ans = salt * 100 // total
        add(
            # 난이도 재조정(7→5, 2026-07 d7 감사): 소금양 보존 가중평균 적용 — 다단계지만 공식 적용.
            "mixture", "CHANGE_RELATION", 5, ["농도", "섞기"],
            f"농도 {c1}%인 소금물 {w1}g과 농도 {c2}%인 소금물 {w2}g을 섞었어요. 섞은 소금물의 농도는 몇 %일까요?",
            f"{ans}%", [f"{(c1 + c2) // 2}%", f"{c1 + c2}%", f"{ans + 2}%"],
            f"섞을 때 변하지 않는 건 '소금의 양'이에요. 첫 소금물의 소금은 {w1}×{c1}÷100={w1 * c1 // 100}g, 둘째는 {w2}×{c2}÷100={w2 * c2 // 100}g. 합치면 소금 {salt}g, 전체 {total}g이니 농도 = {salt}÷{total}×100 = {ans}%예요.",
            [(f"{(c1 + c2) // 2}%", "두 농도의 평균이 아니에요 — 양이 다르면 많은 쪽으로 치우쳐요(가중평균).")],
            detail="섞기 문제의 열쇠는 '녹아 있는 양(소금·알코올)은 섞어도 총량이 그대로'라는 거예요. 각각의 양을 구해 더하고 전체로 다시 나누면 끝. 결국 농도의 '가중평균'이라 양이 많은 쪽 농도에 더 가까워져요.",
            en={
                "statement": f"You mix {w1} g of salt water at {c1}% concentration with {w2} g of salt water at {c2}% concentration. What is the concentration of the mixed salt water, in %?",
                "answer": f"{ans}%",
                "distractors": [f"{(c1 + c2) // 2}%", f"{c1 + c2}%", f"{ans + 2}%"],
                "explanation": f"What doesn't change when mixing is the 'amount of salt'. The first has {w1}×{c1}÷100={w1 * c1 // 100} g of salt, the second {w2}×{c2}÷100={w2 * c2 // 100} g. Together that's {salt} g of salt in {total} g total, so the concentration = {salt}÷{total}×100 = {ans}%.",
                "mistakes": [(f"{(c1 + c2) // 2}%", "It's not the average of the two concentrations — when the amounts differ it leans toward the larger side (a weighted average).")],
                "detail": "The key to mixing problems is that 'the dissolved amount (salt, alcohol) keeps the same total even when mixed'. Find each amount, add them, and divide by the whole. In the end it's a 'weighted average' of the concentrations, so it comes out closer to the concentration of whichever amount is larger.",
            },
        )


# ── 119. 등차수열 n번째 항 (난4, 변화와관계) ────────────────────────────────
def gen_arithmetic_nth():
    for first, diff, n in [(3, 4, 10), (5, 3, 8), (2, 5, 12), (10, 7, 6)]:
        ans = first + diff * (n - 1)
        # 검산(arithnth): 첫 항부터 n번째 항까지 실제로 하나씩 더해 가기
        x = first
        for _ in range(n - 1):
            x += diff
        assert x == ans, f"arithnth 검산 실패: {x} != {ans}"
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
        # 검산(geonth): 첫 항부터 n번째 항까지 실제로 하나씩 곱해 가기
        x = first
        for _ in range(n - 1):
            x *= ratio
        assert x == ans, f"geonth 검산 실패: {x} != {ans}"
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
        # 검산(clockgain): 하루씩 days일을 실제로 누적
        total = 0
        for _ in range(days):
            total += gain
        assert total == ans, f"clockgain 검산 실패: {total} != {ans}"
        add(
            # 난이도 재조정(6→3, 2026-07 d6 감사): 비율×날수 단일 곱셈.
            "clockgain", "CHANGE_RELATION", 3, ["비례", "누적"],
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


# ── 123. 기차가 사람을 지나가기 = 숨은 길이 (난5, 변화와관계) ────────────────
def gen_train_pass_person():
    for length, speed in [(120, 20), (150, 15), (200, 25), (100, 10)]:
        assert length % speed == 0
        ans = length // speed
        add(
            # 난이도 재조정(5→4, 2026-07 d1~5 스캔): train의 퇴화 케이스.
            "trainperson", "CHANGE_RELATION", 4, ["거속시", "숨은 길이"],
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


# ── 115. 피보나치 수열 (난5, 변화와관계) ────────────────────────────────────
def gen_fibonacci():
    for pair, count in [((1, 1), 7), ((2, 3), 6), ((1, 2), 7), ((3, 5), 6)]:
        seq = list(pair)
        while len(seq) < count:
            seq.append(seq[-1] + seq[-2])
        ans = seq[-1] + seq[-2]
        # 검산(fib): 항 잇기와 다른 경로 — 일반화 피보나치 닫힌꼴 a₁·F(count−1) + a₂·F(count)
        closed = pair[0] * _fib(count - 1) + pair[1] * _fib(count)
        assert closed == ans, f"fib 검산 실패: {closed} != {ans}"
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


# ── 136. 시간 계산 = 60진법 받아올림 (난3, 변화와관계) ──────────────────────
def gen_time_duration():
    for h, m, dh, dm in [(3, 40, 1, 50), (2, 20, 2, 55), (9, 45, 1, 30), (7, 50, 2, 20)]:
        tot = (h * 60 + m) + (dh * 60 + dm)
        eh, em = (tot // 60) % 24, tot % 60
        # 검산(timedur): 시작 시각부터 1분씩 실제로 세어 끝 시각 확인
        hh, mm = h, m
        for _ in range(dh * 60 + dm):
            mm += 1
            if mm == 60:
                mm = 0
                hh = (hh + 1) % 24
        assert (hh, mm) == (eh, em), f"timedur 검산 실패: {hh}:{mm} != {eh}:{em}"
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


# ── 138. 합과 차로 두 수 찾기 = 합차법 (난4, 변화와관계) ────────────────────
def gen_two_sum_diff():
    for s, diff in [(20, 4), (30, 6), (50, 10), (18, 2)]:
        big = (s + diff) // 2
        small = (s - diff) // 2
        # 검산(sumdiff): 합·차를 만족하는 두 수 쌍을 전 범위 완전탐색으로 재발견(유일성 포함)
        sols = [(x, y) for x in range(s + 1) for y in range(s + 1) if x + y == s and x - y == diff]
        assert sols == [(big, small)], f"sumdiff 검산 실패: {sols} != [({big}, {small})]"
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


# ── 132. 등차수열의 합 (난5, 변화와관계) ────────────────────────────────────
def gen_sum_arithmetic_series():
    for first, diff, n in [(2, 3, 10), (5, 2, 8), (1, 4, 12), (3, 5, 6)]:
        last = first + diff * (n - 1)
        ans = n * (first + last) // 2
        # 검산(arithsum): n개 항을 실제로 하나씩 더하고, 마지막 항이 last인지도 확인
        total, x = 0, first
        for _ in range(n):
            total += x
            x += diff
        assert total == ans and x - diff == last, f"arithsum 검산 실패: {total} != {ans}"
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
        # 검산(trans): 비교 그래프의 이행적 폐포를 만들어 '모두에게 지는' 사람을 독립 재계산
        beats = {a: {b}, b: {c}, c: {d}, d: set()}
        changed = True
        while changed:
            changed = False
            for x in names:
                for y in list(beats[x]):
                    if beats[y] - beats[x]:
                        beats[x] |= beats[y]
                        changed = True
        losers = [x for x in names if all(x in beats[y] for y in names if y != x)]
        assert losers == [d], f"trans 검산 실패: {losers} != [{d}]"
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
        # 검산(pattern): 구슬 n개를 실제로 순서대로 놓아 n번째 색 확인
        laid = []
        while len(laid) < n:
            laid.extend(pat)
        assert laid[n - 1] == color, f"pattern 검산 실패: {laid[n - 1]} != {color}"
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
        # 검산(iorule): 보여 준 쌍들만으로 규칙(×▲＋●)을 완전탐색 재발견 — 유일해야 문제가 성립
        rules = [(aa, bb) for aa in range(11) for bb in range(11) if all(aa * x + bb == a * x + b for x in inputs)]
        assert rules == [(a, b)], f"iorule 검산 실패: {rules} != [({a}, {b})]"
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


def gen_diophantine():
    # 일차부정방정식 자연수해 개수 — 두 값의 관계를 만족하는 (a,b) 조합을 빠짐없이 세기. (변화와관계 난8)
    for ua, ub, total in [(300, 500, 3800), (400, 300, 4300), (200, 700, 6500), (500, 600, 7100)]:
        sols = [(a, b) for a in range(1, total // ua + 1) for b in range(1, total // ub + 1) if ua * a + ub * b == total]
        ans = len(sols)
        # 검산(diophantine): 다른 경로(사탕 수만 훑으며 나머지 금액의 나눠떨어짐 확인)로 해집합 재구성
        sols2 = []
        aa = 1
        while ua * aa + ub <= total:
            rest = total - ua * aa
            if rest % ub == 0:
                sols2.append((aa, rest // ub))
            aa += 1
        assert sols2 == sols and len(sols2) == ans, f"diophantine 검산 실패: {sols2} != {sols}"
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
            en={
                "statement": f"You want to buy at least one candy costing {ua} won each and at least one chocolate costing {ub} won each, spending exactly {total} won. "
                f"How many (number of candies, number of chocolates) combinations are there in all?",
                "answer": f"{ans} ways",
                "distractors": [f"{c} ways" for c in _pick_distractors(ans, [ans + 1, ans + 2, ans - 1, ans + 3])],
                "explanation": f"If there are a candies and b chocolates, then {ua}×a + {ub}×b = {total}. Increasing one side (say the number of chocolates) by one at a time and keeping "
                f"only the cases where the rest is divisible by {ua}, you get (a,b) = {', '.join(f'({a},{b})' for a, b in sols)} — {ans} ways in all.",
                "mistakes": [(f"{ans + 1} ways", "Change one count one at a time and count only the cases that 'divide evenly'. It's easy to miss some or double-count."),
                             (f"{ans - 1 if ans > 1 else ans + 2} ways", "Check that you counted every case without omission, including both ends (when one side is at its minimum).")],
                "detail": "'Combining two kinds in whole-number quantities to hit a fixed value' is a linear Diophantine equation. Move one variable by 1 and the other moves the opposite way by its coefficient "
                "(here, as one goes up the other goes down regularly). So the solutions appear spaced at regular intervals, and counting every one between the two ends gives their number.",
            },
        )


def gen_unitprice():
    # 단가 비례 — 한 개 값을 구해 개수만큼 곱하기. (변화와관계 난2)
    for cnt0, price0, cnt1 in [(3, 600, 5), (4, 800, 7), (2, 500, 6), (5, 1500, 8)]:
        unit = price0 // cnt0
        ans = unit * cnt1
        # 검산(unitprice): 한 자루 값이 딱 떨어지는지 + 교차곱(비례식 cnt0:price0 = cnt1:ans)으로 재확인
        assert price0 % cnt0 == 0, f"unitprice 검산 실패: {price0}÷{cnt0} 안 떨어짐"
        assert ans * cnt0 == price0 * cnt1, f"unitprice 검산 실패: 교차곱 {ans * cnt0} != {price0 * cnt1}"
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


def gen_compose():
    # 함수(수 기계)를 여러 번 반복 적용. f(x)=ax+b를 d번. (변화와관계 난5)
    # 난이도 재조정(난9→5, 2026-07 d9 감사): 규칙을 statement가 그대로 주고 반복 계산만 —
    # 강등된 recur(d5)와 동일 패턴.
    for a, b, x0, d in [(2, 1, 1, 3), (2, 3, 1, 3), (3, 1, 2, 3), (2, 5, 0, 3)]:
        seq = [x0]
        x = x0
        for _ in range(d):
            x = a * x + b
            seq.append(x)
        ans = x
        steps = " → ".join(str(v) for v in seq)
        # 검산(compose): 반복 계산과 별도로 아핀 반복 닫힌꼴 aᵈ·x₀ + b(aᵈ−1)/(a−1)로 재계산
        assert a != 1, "compose 검산 실패: a=1이면 닫힌꼴 불가"
        closed = a ** d * x0 + b * (a ** d - 1) // (a - 1)
        assert closed == ans, f"compose 검산 실패: {closed} != {ans}"
        add(
            "compose", "CHANGE_RELATION", 5, ["함수 반복", "규칙 적용"],
            f"어떤 기계에 수를 넣으면 '{a}배 하고 {b}{_eul(str(b))} 더한' 수가 나와요. {x0}{_eul(str(x0))} 넣어 나온 수를 "
            f"다시 넣는 식으로, 이 기계에 모두 {d}번 통과시켰어요. 마지막에 나오는 수는 얼마일까요?",
            str(ans), [str(c) for c in _pick_distractors(ans, [a * ans, ans + b, seq[-2], ans + a])],
            f"기계를 한 번 통과할 때마다 '×{a}, +{b}'예요: {steps}. {d}번 통과한 마지막 값은 {ans}예요.",
            [(str(seq[-2]), "한 번 덜 돌렸어요. 정확히 {}번 반복한 값을 구하세요.".format(d))],
            detail="같은 규칙(함수)을 반복해서 적용하면 값이 규칙적으로 바뀌어요. 한 단계씩 차근차근 계산해 나가는 게 안전하고, "
            "이런 반복은 점화식·수열의 뿌리예요.",
            en={
                "statement": f"When you put a number into a machine, out comes 'times {a}, plus {b}'. Starting with {x0}, you feed each result back in, passing through the machine {d} times in all. What is the final number that comes out?",
                "answer": str(ans),
                "distractors": [str(c) for c in _pick_distractors(ans, [a * ans, ans + b, seq[-2], ans + a])],
                "explanation": f"Each pass through the machine is '×{a}, +{b}': {steps}. After {d} passes the final value is {ans}.",
                "mistakes": [(str(seq[-2]), f"You ran it one time too few. Find the value after exactly {d} repetitions.")],
                "detail": "Applying the same rule (function) over and over changes the value in a regular way. Working through it one step at a time is the safe approach, and this kind of repetition is the root of recurrence relations and sequences.",
            },
        )


def gen_recur():
    # 점화식 a_{n+1}=p·a_n+q의 특정 항. (변화와관계 난5)
    # 난이도 재조정(난10→5): 규칙을 '받아서' 4번 반복만 하는 문제라 통찰이 없다.
    # 같은 점화식을 '스스로 발견'하는 하노이(난7)·계단(난6)보다 반드시 낮아야 한다.
    for a1, p, q, t in [(1, 2, 3, 5), (2, 2, 1, 5), (1, 3, 1, 4), (2, 3, 1, 4)]:
        seq = [a1]
        a = a1
        for _ in range(t - 1):
            a = p * a + q
            seq.append(a)
        ans = a
        steps = ", ".join(str(v) for v in seq)
        # 검산(recur): 항 잇기와 별도로 닫힌꼴 p^(t−1)·a₁ + q(p^(t−1)−1)/(p−1)로 재계산
        assert p != 1, "recur 검산 실패: p=1이면 닫힌꼴 불가"
        closed = p ** (t - 1) * a1 + q * (p ** (t - 1) - 1) // (p - 1)
        assert closed == ans, f"recur 검산 실패: {closed} != {ans}"
        add(
            "recur", "CHANGE_RELATION", 5, ["점화식", "수열의 항"],
            f"수열의 첫째 항이 {a1}이고, 다음 항은 '앞 항의 {p}배에 {q}{_eul(str(q))} 더한' 값이에요. 이 수열의 {t}번째 항은 얼마일까요?",
            str(ans), [str(c) for c in _pick_distractors(ans, [p * ans + q, seq[-2], ans + q, ans - q])],
            f"규칙 '×{p}, +{q}'로 항을 이어 가요: {steps}. {t}번째 항은 {ans}예요.",
            [(str(seq[-2]), "한 항 덜 갔어요. {}번째 항까지 규칙을 적용하세요.".format(t)),
             (str(p * ans + q), "그건 {}번째(한 항 더 간) 값이에요.".format(t + 1))],
            detail="앞 항으로 다음 항을 정하는 규칙이 점화식이에요. 규칙을 한 항씩 적용해 원하는 항까지 이어 가면 돼요. "
            "이자·인구·알고리즘 등 '이전 상태로 다음을 정하는' 수많은 현상의 뼈대예요.",
            en={
                "statement": f"The first term of a sequence is {a1}, and each next term is 'the previous term times {p}, plus {q}'. What is the {t}th term of this sequence?",
                "answer": str(ans),
                "distractors": [str(c) for c in _pick_distractors(ans, [p * ans + q, seq[-2], ans + q, ans - q])],
                "explanation": f"Applying the rule '×{p}, +{q}' term by term: {steps}. The {t}th term is {ans}.",
                "mistakes": [(str(seq[-2]), f"You went one term short. Apply the rule up to the {t}th term."),
                             (str(p * ans + q), f"That's the {t + 1}th value (one term too far).")],
                "detail": "A recurrence is a rule that decides the next term from the previous one. Just apply the rule one term at a time until you reach the term you want. It's the backbone of countless phenomena — interest, populations, algorithms — that 'decide the next state from the previous one'.",
            },
        )


def gen_geosum():
    # 등비수열 합 1+2+4+…+2^(k-1) = 2^k − 1. 2배씩 커지는 수의 합 규칙. (변화와관계 난4)
    # 난이도 재조정(난8→4, 2026-07 d8 감사): 항 8~10개 직접 덧셈으로 끝 — cubesum(d4) 동류.
    for k in [8, 6, 10, 7]:
        last = 2 ** (k - 1)
        ans = 2 ** k - 1
        # 검산(geosum): 1부터 last까지 2배씩 커지는 항을 실제로 하나씩 더해 보기
        total, term = 0, 1
        while term <= last:
            total += term
            term *= 2
        assert total == ans, f"geosum 검산 실패: {total} != {ans}"
        add(
            "geosum", "CHANGE_RELATION", 4, ["등비수열", "합의 규칙"],
            f"1 + 2 + 4 + 8 + … 처럼 앞의 수의 2배씩 커지는 수를, 1부터 {last}까지 모두 더하면 합은 얼마일까요?",
            str(ans), [str(c) for c in _pick_distractors(ans, [2 ** k, last, ans + 1, ans - 1])],
            f"2배씩 커지는 수를 다 더하면 신기하게도 '마지막 수의 2배보다 1 작은 수'가 돼요. 마지막이 {last}이니 "
            f"{last}×2 − 1 = {2 ** k} − 1 = {ans}예요.",
            [(str(2 ** k), "마지막 수의 2배에서 1을 빼야 해요(딱 1 모자라요)."),
             (str(last), "마지막 한 항이 아니라 전부 더한 합이에요.")],
            detail="1+2+4+…+2^(k−1) = 2^k − 1이에요. 각 항이 그 앞까지의 합보다 1 큰 성질(1, 1+2=3, 1+2+4=7…)이라, "
            "합은 항상 다음 2의 거듭제곱보다 1 작아요. 이진법·배수 사고와 이어지는 등비수열 합의 기본이에요.",
            en={
                "statement": f"Adding numbers that keep doubling like 1 + 2 + 4 + 8 + …, from 1 up to {last}, what is the sum?",
                "answer": str(ans),
                "distractors": [str(c) for c in _pick_distractors(ans, [2 ** k, last, ans + 1, ans - 1])],
                "explanation": f"Adding up numbers that keep doubling gives, surprisingly, 'one less than twice the last number'. Since the last is {last}, "
                f"{last}×2 − 1 = {2 ** k} − 1 = {ans}.",
                "mistakes": [(str(2 ** k), "You must subtract 1 from twice the last number (it falls exactly 1 short)."),
                             (str(last), "It's the sum of all the terms, not just the last one.")],
                "detail": "1+2+4+…+2^(k−1) = 2^k − 1. Each term is 1 more than the sum before it (1, 1+2=3, 1+2+4=7…), "
                "so the sum is always 1 less than the next power of 2. It's the basis of geometric-series sums, connected to binary and multiple thinking.",
            },
        )


def gen_josephus():
    # 조세푸스 문제(2명마다 제거): 원으로 앉아 짝수 번째부터 빼면 마지막 생존자 = 2L+1 (n=2^m+L). (변화와관계 난9)
    for n in [7, 10, 13, 6]:
        power = 1 << (n.bit_length() - 1)  # n 이하 최대 2의 거듭제곱
        leftover = n - power
        ans = 2 * leftover + 1
        # 검산(josephus): 원탁 제거를 실제로 시뮬레이션 — 한 명 남기고(회전) 다음 사람 제거를 반복
        from collections import deque
        dq = deque(range(1, n + 1))
        while len(dq) > 1:
            dq.rotate(-1)
            dq.popleft()
        assert dq[0] == ans, f"josephus 검산 실패: {dq[0]} != {ans}"
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
            en={
                "statement": f"{n} people sit in a circle, numbered in order starting from 1. Keep number 1 and remove number 2, keep number 3 and remove number 4… "
                f"Skipping one person at a time as you go around removing them, which numbered person is the very last one left?",
                "answer": f"person {ans}",
                "distractors": [f"person {c}" for c in _pick_distractors(ans, [n, n - 1, ans + 2, 1])],
                "explanation": f"Write {n} as '{power} (a power of 2) + {leftover}'. When the count is exactly a power of 2, number 1 always survives. "
                f"After {leftover} removals have advanced past that point, the surviving seat is 2×{leftover}+1 = person {ans}.",
                "mistakes": [(f"person {n}", "The last number isn't the survivor. Recount the seat using the nearest power of 2."),
                             (f"person 1", "Number 1 only survives when the count is exactly a power of 2. The leftover people shift the surviving seat along.")],
                "detail": "This is the 'Josephus problem', removing every other person around a circle. Using the fact that when the count is a power of 2 the start (number 1) survives, split n = 2^m + L to get survivor = person 2L+1. A classic problem of generalizing a rule from the power-of-2 skeleton.",
            },
        )


def gen_prodsum():
    # 연속한 두 수의 곱의 합 1·2+2·3+…+n(n+1) = n(n+1)(n+2)/3. 이웃 항이 지워지는 텔레스코핑. (변화와관계 난7)
    for n in [5, 6, 4, 7]:
        ans = n * (n + 1) * (n + 2) // 3
        last = n * (n + 1)
        # 검산(prodsum): k(k+1) 항을 실제로 하나씩 더해 텔레스코핑 공식과 대조
        total = 0
        for k in range(1, n + 1):
            total += k * (k + 1)
        assert total == ans, f"prodsum 검산 실패: {total} != {ans}"
        terms = " + ".join(f"{k}×{k + 1}" for k in range(1, min(n, 3) + 1)) + (f" + … + {n}×{n + 1}" if n > 3 else "")
        add(
            # 난이도 재조정(7→4, 2026-07 d7 감사): 항 ≤7개 직접 덧셈으로 답 — fibsum/geosum 선례.
            "prodsum", "CHANGE_RELATION", 4, ["수열의 합", "규칙으로 한꺼번에"],
            f"{terms} 의 값은 얼마일까요?",
            str(ans), [str(c) for c in _pick_distractors(ans, [last, ans // 2, ans + last, n * (n + 1) // 2])],
            f"연속한 두 수의 곱을 더하는 합은 항이 늘어도 규칙이 있어요 — 1·2+2·3+…+n·(n+1) = n(n+1)(n+2)÷3. "
            f"여기선 {n}×{n + 1}×{n + 2}÷3 = {ans}예요. (각 항을 '3칸짜리 계단의 차이'로 바꾸면 이웃끼리 지워져 마지막만 남는 원리예요.)",
            [(str(last), "마지막 항 하나가 아니라 모든 항을 더한 값이에요."),
             (str(n * (n + 1) // 2), "1부터 더한 삼각수와 헷갈리지 마세요. 여기선 '두 수의 곱'을 더해요.")],
            detail="1·2+2·3+…+n(n+1)처럼 연속한 두 수의 곱을 더하면 n(n+1)(n+2)/3이 돼요. 각 항 k(k+1)을 "
            "[k(k+1)(k+2)−(k−1)k(k+1)]/3으로 바꾸면 앞뒤 항이 사슬처럼 지워지고(텔레스코핑) 맨 끝 n(n+1)(n+2)/3만 남기 때문이에요. "
            "많은 항을 규칙 하나로 한꺼번에 더하는 수열 합의 대표 문제예요.",
            en={
                "statement": f"What is the value of {terms}?",
                "answer": str(ans),
                "distractors": [str(c) for c in _pick_distractors(ans, [last, ans // 2, ans + last, n * (n + 1) // 2])],
                "explanation": f"A sum of products of two consecutive numbers follows a rule even as the terms grow — 1·2+2·3+…+n·(n+1) = n(n+1)(n+2)÷3. "
                               f"Here that's {n}×{n + 1}×{n + 2}÷3 = {ans}. (Rewriting each term as the 'difference of a 3-step staircase' makes neighbours cancel, leaving only the last.)",
                "mistakes": [(str(last), "This is the sum of all the terms, not just the last one."),
                             (str(n * (n + 1) // 2), "Don't confuse this with the triangular number summed from 1. Here you add 'products of two numbers'.")],
                "detail": "Adding products of two consecutive numbers like 1·2+2·3+…+n(n+1) gives n(n+1)(n+2)/3. Rewriting each term k(k+1) as "
                          "[k(k+1)(k+2)−(k−1)k(k+1)]/3 makes the terms cancel in a chain (telescoping), leaving only the final n(n+1)(n+2)/3. "
                          "It's a classic sequence-sum problem of adding many terms all at once with a single rule.",
            },
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
        # 검산(quadseq): 닫힌꼴과 별도로 계차를 규칙대로 늘려 가며 pos번째 항까지 실제로 이어 가기
        dd = diffs[1] - diffs[0]
        assert all(diffs[i + 1] - diffs[i] == dd for i in range(3)), f"quadseq 검산 실패: 계차 {diffs} 불규칙"
        t_val, d_cur = terms[-1], diffs[-1]
        for _ in range(pos - 5):
            d_cur += dd
            t_val += d_cur
        assert t_val == ans, f"quadseq 검산 실패: {t_val} != {ans}"
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
            en={
                "statement": f"A sequence continues as {terms[0]}, {terms[1]}, {terms[2]}, {terms[3]}, {terms[4]}, …. "
                f"Continuing this rule, what is the {pos}th number?",
                "answer": str(ans),
                "distractors": [str(c) for c in _pick_distractors(ans, [naive, ans + pos, ans - pos, terms[-1] + diffs[-1]])],
                "explanation": f"The differences between adjacent numbers (the first differences) are {diffs[0]}, {diffs[1]}, {diffs[2]}, {diffs[3]}, …, "
                f"increasing steadily by {diffs[1] - diffs[0]} (an arithmetic sequence; the difference of the differences is constant → a quadratic sequence). "
                f"The rule is {label}, so the {pos}th number is {ans}.",
                "mistakes": [(str(naive), "Don't treat the differences as 'constant'. The differences themselves grow steadily (arithmetic) — it's a quadratic sequence."),
                             (str(terms[-1] + diffs[-1]), "Don't stop at the 6th term; keep growing the differences by the rule and add all the way to the target term.")],
                "detail": "If the first differences (differences of adjacent terms) form an arithmetic sequence, the original sequence is expressed by a quadratic (an²+bn+c) — because the 'difference of the differences' is constant. "
                "After finding the rule of the differences from a few nearby terms, growing those differences and adding lets you find even far-away terms. It's a problem for training the eye to see the rule behind the rule.",
            },
        )


def gen_cubesum():
    # 세제곱의 합 1³+…+n³ = (1+2+…+n)² = (삼각수)². (변화와관계 난4)
    # 난이도 재조정(난10→4, 2026-07 d10 감사): n≤6이라 직접 덧셈이 더 쉬움 —
    # 항등식은 장식이고 실질은 계산. 관계 '발견'을 시키는 형태로 개편하면 승급 여지.
    for n in [4, 5, 6, 3]:
        tri = n * (n + 1) // 2
        ans = tri * tri
        sq_sum = n * (n + 1) * (2 * n + 1) // 6  # 제곱의 합(헷갈리기 쉬운 값)
        # 검산(cubesum): 세제곱을 실제로 하나씩 더해 (삼각수)² 항등식과 대조
        total = 0
        for i in range(1, n + 1):
            total += i * i * i
        assert total == ans, f"cubesum 검산 실패: {total} != {ans}"
        # n=3이면 "…+3³" 생략 기호가 마지막 항과 겹치는 퇴화 표기가 되므로 전체를 풀어쓴다.
        expr = "1³ + 2³ + 3³" if n == 3 else f"1³ + 2³ + 3³ + … + {n}³"
        add(
            "cubesum", "CHANGE_RELATION", 4, ["수열의 합", "숨은 관계 발견"],
            f"{expr} 의 값은 얼마일까요? (각 수를 세제곱해서 더해요)",
            str(ans), [str(c) for c in _pick_distractors(ans, [sq_sum, tri, n ** 3, ans - tri])],
            f"놀랍게도 세제곱의 합은 '1부터 그 수까지의 합(삼각수)'을 제곱한 것과 같아요. "
            f"1+2+…+{n} = {tri}이고, 그 제곱 {tri}² = {ans}이에요.",
            [(str(sq_sum), "그건 '제곱'의 합(1²+…+n²)이에요. 여기선 '세제곱'의 합이라 삼각수의 제곱이 돼요."),
             (str(tri), "삼각수 그 자체가 아니라, 삼각수를 '제곱'한 값이에요.")],
            detail="1³+2³+…+n³ = (1+2+…+n)² = (n(n+1)/2)²이에요. 세제곱을 하나씩 더한 값이 '합을 통째로 제곱한 값'과 같다는 "
            "아름다운 관계로, 그림(정사각형을 계단식으로 쌓기)으로도 증명돼요. 겉보기 다른 두 양의 숨은 관계를 발견하는 문제예요.",
            en={
                "statement": f"What is the value of {expr}? (cube each number and add them)",
                "answer": str(ans),
                "distractors": [str(c) for c in _pick_distractors(ans, [sq_sum, tri, n ** 3, ans - tri])],
                "explanation": f"Amazingly, the sum of the cubes equals the square of '1 plus 2 up to that number (the triangular number)'. "
                f"1+2+…+{n} = {tri}, and its square {tri}² = {ans}.",
                "mistakes": [(str(sq_sum), "That's the sum of the 'squares' (1²+…+n²). Here it's the sum of the 'cubes', which is the square of the triangular number."),
                             (str(tri), "It's not the triangular number itself, but the triangular number 'squared'.")],
                "detail": "1³+2³+…+n³ = (1+2+…+n)² = (n(n+1)/2)². It's the beautiful fact that adding the cubes one by one equals 'squaring the whole sum', "
                "which can even be proved with a picture (stacking squares in a staircase). It's a problem about discovering the hidden relationship between two seemingly different quantities.",
            },
        )


def gen_fibsum():
    # 피보나치 부분합 F1+…+Fn = F(n+2)−1. 합과 한 항의 숨은 관계. (변화와관계 난4)
    # 난이도 재조정(난9→4, 2026-07 d9 감사): 항 6~10개 직접 덧셈으로 끝(항등식 불필요) —
    # cubesum(d4) 동류.
    for n in [6, 8, 10, 7]:
        terms = [_fib(k) for k in range(1, 6)]
        total = sum(_fib(k) for k in range(1, n + 1))
        fplus2 = _fib(n + 2)
        # 검산(fibsum): 항을 자체 루프로 다시 만들며 부분합을 누적하고, F(n+2)−1 항등식과 대조
        x, y, total2 = 1, 1, 0
        for _ in range(n):
            total2 += x
            x, y = y, x + y
        assert total2 == total and y == fplus2 and total == fplus2 - 1, f"fibsum 검산 실패: {total2} != {total}"
        add(
            "fibsum", "CHANGE_RELATION", 4, ["피보나치", "합의 숨은 규칙"],
            f"{terms[0]}, {terms[1]}, {terms[2]}, {terms[3]}, {terms[4]}, … 처럼 앞의 두 수를 더해 만드는 "
            f"피보나치 수열이 있어요. 첫째 항부터 {n}째 항까지 모두 더하면 얼마일까요?",
            str(total), [str(c) for c in _pick_distractors(total, [fplus2, _fib(n + 1), total + 1, total - 1])],
            f"피보나치 수를 처음부터 더한 합에는 규칙이 있어요 — 첫째부터 n째까지의 합은 (n+2)째 항보다 딱 1 작아요. "
            f"{n + 2}째 항이 {fplus2}이니, 합은 {fplus2} − 1 = {total}이에요.",
            [(str(fplus2), "(n+2)째 항 자체가 아니라, 거기서 1을 뺀 값이 부분합이에요."),
             (str(_fib(n + 1)), "한 항 어긋났어요. 부분합은 (n+1)째가 아니라 (n+2)째 항에서 1을 뺀 값이에요.")],
            detail="피보나치 부분합 F1+F2+…+Fn = F(n+2)−1이에요. 각 항을 이웃 항의 차로 바꾸면(F(k) = F(k+2)−F(k+1)) 사슬처럼 지워져 "
            "맨 끝 F(n+2)−1만 남기 때문이에요(텔레스코핑). 수열의 합과 한 항 사이의 숨은 관계를 보는 문제예요.",
            en={
                "statement": f"There is a Fibonacci sequence {terms[0]}, {terms[1]}, {terms[2]}, {terms[3]}, {terms[4]}, …, where each number is the sum of the two before it. "
                f"What do you get when you add up all the terms from the 1st up to the {n}th?",
                "answer": str(total),
                "distractors": [str(c) for c in _pick_distractors(total, [fplus2, _fib(n + 1), total + 1, total - 1])],
                "explanation": f"The sum of Fibonacci numbers from the start follows a rule — the sum of the 1st through the nth term is exactly 1 less than the (n+2)th term. "
                f"The {n + 2}th term is {fplus2}, so the sum is {fplus2} − 1 = {total}.",
                "mistakes": [(str(fplus2), "Not the (n+2)th term itself — the partial sum is that value minus 1."),
                             (str(_fib(n + 1)), "Off by one term. The partial sum is the (n+2)th term minus 1, not the (n+1)th.")],
                "detail": "The Fibonacci partial sum F1+F2+…+Fn = F(n+2)−1. Rewriting each term as a difference of neighbors (F(k) = F(k+2)−F(k+1)) makes them cancel in a chain (telescoping), leaving only F(n+2)−1. A problem about the hidden relationship between a sum of terms and a single term.",
            },
        )


# ═══ 천장 보충(CEILING_SPECS 2026-07) + 신규 슬롯 — 변화와관계 7 family ═══════════
# 스펙 4(stampfrob·mergecandy·digitpos·cubesumfar) + 신규 설계 3(seqcommon·pyramidmax·funcinv).
# 전부 결정적 파라미터(랜덤 분기 없음) — 전역 rng/rng_en 소비 없음.


def gen_stampfrob():
    # 만들 수 없는 가장 큰 우편 요금 — 프로베니우스. '연속 a개 가능이면 종료' 정지 논법 발견. (변화와관계 난10, CEILING_SPECS 3.1)
    # 발견형 근거: 풀이법이 문제문에 없고, '가장 큰' 불가능 금액의 확정에는 정지 논법 발견이 필수라 유한 나열만으론 답을 못 정한다.
    for a, b in [(5, 8), (4, 7), (5, 7), (3, 8)]:
        # 검산(stampfrob) 경로1: DP로 가능/불가능 표를 만들어 최대 불가능 금액을 직접 탐색
        LIM = a * b + a + b
        ok = [False] * (LIM + 1)
        ok[0] = True
        for v in range(1, LIM + 1):
            ok[v] = (v >= a and ok[v - a]) or (v >= b and ok[v - b])
        assert all(ok[v] for v in range(a * b, LIM + 1)), f"stampfrob: {a},{b} 곱 이후에 불가능 금액 존재"
        impossible = [v for v in range(1, LIM + 1) if not ok[v]]
        ans = max(impossible)
        # 검산 경로2: 프로베니우스 폐형식 a·b−a−b와 대조 (서로소 확인 포함)
        assert gcd(a, b) == 1 and ans == a * b - a - b, f"stampfrob 검산 실패: {ans} != {a * b - a - b}"
        # 정지 논법 확인: 정답 바로 다음부터 a개 연속 가능 / 정답은 b장 몇 장을 빼도 a로 안 나눠짐
        assert all(ok[ans + 1 + i] for i in range(a)), f"stampfrob: {ans}+1부터 연속 {a}개 가능이 아님"
        assert all((ans - b * j) % a != 0 for j in range(ans // b + 1)), f"stampfrob: {ans}이 실은 가능"
        second = max(v for v in impossible if v != ans)  # 그다음으로 큰 불가능 금액(오답용)
        assert ok[ans + a], f"stampfrob: 오답 {ans + a}가 실은 불가능"
        add(
            "stampfrob", "CHANGE_RELATION", 10, ["동전·우표 문제", "나머지로 분류"],
            f"한 장에 {a}원짜리 우표와 {b}원짜리 우표가 아주 많이 있어요. 두 우표를 몇 장씩이든 자유롭게 붙일 수 있어요"
            f"(한 종류만 붙여도 되고, 안 붙이는 종류가 있어도 돼요). 이렇게 해서 만들 수 없는 우편 요금 중 가장 큰 금액은 얼마일까요?",
            f"{ans}원", [f"{a * b}원", f"{second}원", f"{ans + a}원"],
            f"작은 금액부터 '되는지/안 되는지' 표를 만들어요. 가능한 금액에 {a}원 우표 한 장을 더 붙이면 계속 가능하니, "
            f"연속 {a}개 금액이 가능해지는 순간 그 뒤는 전부 가능해요. 표를 채우면 {ans + 1}원부터 {ans + a}원까지 {a}개가 연속으로 가능해지고, "
            f"그 직전의 {ans}원은 {b}원 우표를 0장, 1장, 2장… 어떻게 잡아도 남는 금액이 {a}원 단위로 채워지지 않아 불가능 — "
            f"그래서 만들 수 없는 가장 큰 금액은 {ans}원이에요.",
            [(f"{a * b}원", f"두 값의 곱까지는 다 안 될 거라고 뭉뚱그렸어요. 작은 수부터 하나씩 확인하면 곱보다 훨씬 앞에서 끝나요."),
             (f"{second}원", "만들 수 없는 금액을 찾긴 했지만, 그보다 더 큰 불가능 금액이 남아 있는지 확인하지 않았어요."),
             (f"{ans + a}원", f"불가능한 금액에 {a}를 더하면 계속 불가능할 거라 착각했어요. 거꾸로예요 — 가능한 금액에 {a}를 더하면 계속 가능해요.")],
            detail=f"왜 '연속 {a}개'가 끝의 신호일까요? 가능한 금액에 {a}원을 더하면 계속 가능하니, 연속 {a}개가 가능해지는 순간 "
            f"모든 경우가 덮여 그 뒤는 영원히 가능해요 — 불가능 금액은 유한 개뿐이에요. 되돌아보기: {ans}원이 정말 불가능한지 "
            f"{b}원 우표 0장·1장·2장…으로 나눠 직접 확인해 보세요. 일반화: (3,5)나 (2,7) 같은 작은 짝으로 실험하면 규칙이 보여요 — "
            f"실은 이 값, 두 수의 곱에서 두 수를 뺀 것({a}×{b}−{a}−{b}={ans})과 같아요. 두 우표 값에 공약수가 있으면(예: 4와 6) "
            f"이야기가 완전히 달라진다는 것도 재미있는 갈래예요.",
            en={
                "concepts": ["coin and stamp problem", "classifying by remainders"],
                "statement": f"You have plenty of {a}-won stamps and {b}-won stamps. You may use any number of each kind "
                f"(including none of one kind). What is the largest postage amount that can NOT be made this way?",
                "answer": f"{ans} won",
                "distractors": [f"{a * b} won", f"{second} won", f"{ans + a} won"],
                "explanation": f"Make a table from small amounts up, marking 'possible / impossible'. Adding one {a}-won stamp to any possible amount keeps it possible, "
                f"so the moment {a} amounts in a row become possible, everything after is possible. Filling the table, the amounts {ans + 1} to {ans + a} won are {a} in a row possible, "
                f"and the amount just before, {ans} won, fails no matter how many {b}-won stamps (0, 1, 2, …) you try — the rest never fills up in steps of {a} won. "
                f"So the largest impossible amount is {ans} won.",
                "mistakes": [(f"{a * b} won", "Don't lump everything up to the product together as impossible. Checking from small amounts up, the impossibles end far before the product."),
                             (f"{second} won", "You found an impossible amount, but didn't check whether an even larger impossible amount remains."),
                             (f"{ans + a} won", f"You assumed adding {a} to an impossible amount stays impossible. It's the other way round — adding {a} to a POSSIBLE amount stays possible.")],
                "detail": f"Why is '{a} in a row' the stopping signal? Adding {a} won to a possible amount keeps it possible, so once {a} consecutive amounts work, "
                f"every case is covered and everything after works forever — only finitely many amounts are impossible. Check back: split {ans} won by 0, 1, 2, … stamps of {b} won "
                f"to confirm it really is impossible. Generalize: experimenting with small pairs like (3,5) or (2,7) reveals the rule — this value in fact equals the product minus both numbers "
                f"({a}×{b}−{a}−{b}={ans}). And if the two stamp values share a common factor (say 4 and 6), the story changes completely — a fun branch to explore.",
            },
        )


def gen_mergecandy():
    # 봉지 합치기 — 순서 무관 불변량(사탕 −1·봉지 −1). (변화와관계 난10, CEILING_SPECS 3.2)
    # 발견형 근거: '순서와 무관하다'는 사실 자체가 문제문에 없어 스스로 발견해야 하고, n≥25면 손 시뮬레이션이 비현실적이다.
    import random as _stdrandom  # 전역 rng/rng_en 금지 규약 — 시뮬레이션은 고정시드 별도 인스턴스만 사용
    for n in [40, 30, 25, 50]:
        S = n * (n + 1) // 2
        # 검산(mergecandy) 경로1: 무작위 순서 300회 시뮬레이션이 전부 같은 값 = 순서 무관 불변량
        outcomes = set()
        for t in range(300):
            r = _stdrandom.Random(1000 + t)
            bags = list(range(1, n + 1))
            while len(bags) > 1:
                i, j = r.sample(range(len(bags)), 2)
                merged = bags[i] + bags[j] - 1
                bags = [bags[idx] for idx in range(len(bags)) if idx not in (i, j)] + [merged]
            outcomes.add(bags[0])
        assert len(outcomes) == 1, f"mergecandy: n={n} 순서에 따라 결과가 달라짐 {outcomes}"
        ans = outcomes.pop()
        # 검산 경로2: 불변량 폐형식 S−(n−1)과 대조
        assert ans == S - (n - 1), f"mergecandy 검산 실패: {ans} != {S - (n - 1)}"
        add(
            "mergecandy", "CHANGE_RELATION", 10, ["불변량", "순서와 무관한 양"],
            f"사탕이 1개, 2개, 3개, …, {n}개 들어 있는 봉지 {n}개가 있어요. 두 봉지를 골라 하나로 합칠 때마다 사탕을 딱 1개 꺼내 먹어요. "
            f"어떤 순서로 합치든 봉지가 하나만 남을 때까지 반복하면, 마지막 봉지에는 사탕이 몇 개 남을까요?",
            f"{ans}개", [f"{S}개", f"{S - n}개", f"{S - (n - 2)}개"],
            f"봉지 3개(1, 2, 3개)로 실험하면 어떤 순서로 합쳐도 결과가 같아요. 비밀은 '변하지 않는 규칙' — 한 번 합칠 때마다 "
            f"봉지는 정확히 1개 줄고 사탕도 정확히 1개 줄어요. 봉지 {n}개가 1개가 되려면 꼭 {n}−1={n - 1}번 합쳐야 하니, "
            f"사탕은 처음 총합 1+2+…+{n}={S}개에서 {n - 1}개가 사라져 {S}−{n - 1}={ans}개 남아요. 순서는 결과에 아무 영향을 못 줘요.",
            [(f"{S}개", "합칠 때마다 1개씩 먹은 사탕을 빼지 않았어요. 사탕 총합은 합칠 때마다 정확히 1개씩 줄어요."),
             (f"{S - n}개", f"합침 횟수를 {n}회로 셌어요. 봉지 {n}개가 1개가 되려면 횟수는 {n}−1회예요(한 번 합칠 때마다 봉지가 딱 1개 줄어요)."),
             (f"{S - (n - 2)}개", f"합침 횟수를 한 번 적게 셌어요. 봉지 수 변화({n}→1)로 횟수를 다시 세어 보세요.")],
            detail=f"과정이 아무리 복잡해도 '매 단계 똑같이 변하는 양(불변량)'을 찾으면 한 번에 끝나요 — 여기선 '봉지 −1, 사탕 −1'이 그 불변 규칙이에요. "
            f"되돌아보기: 봉지 3개(1, 2, 3개)로 두 순서를 직접 해 보세요 — (1+2)−1=2를 3과 합치면 2+3−1=4, (2+3)−1=4를 1과 합치면 4+1−1=4로 똑같아요. "
            f"일반화: 합칠 때마다 사탕을 2개씩 먹는다면 답은 총합 − 2×({n}−1)이 돼요.",
            en={
                "concepts": ["invariants", "order-independent quantity"],
                "statement": f"There are {n} bags holding 1, 2, 3, …, {n} candies. Each time you merge two bags into one, you take out and eat exactly 1 candy. "
                f"If you repeat this in any order until a single bag remains, how many candies are left in it?",
                "answer": f"{ans} candies",
                "distractors": [f"{S} candies", f"{S - n} candies", f"{S - (n - 2)} candies"],
                "explanation": f"Experiment with 3 bags (1, 2, 3 candies): every merging order gives the same result. The secret is an unchanging rule — "
                f"each merge reduces the bags by exactly 1 and the candies by exactly 1. Turning {n} bags into 1 takes exactly {n}−1={n - 1} merges, "
                f"so from the initial total 1+2+…+{n}={S} candies, {n - 1} disappear, leaving {S}−{n - 1}={ans}. The order cannot affect the result.",
                "mistakes": [(f"{S} candies", "You didn't subtract the candy eaten at each merge. The total drops by exactly 1 per merge."),
                             (f"{S - n} candies", f"You counted {n} merges. Turning {n} bags into 1 takes {n}−1 merges (each merge reduces the bag count by exactly 1)."),
                             (f"{S - (n - 2)} candies", f"You counted one merge too few. Recount the merges from the change in bag count ({n}→1).")],
                "detail": f"However complicated the process, finding a quantity that changes the same way at every step (an invariant) finishes it in one stroke — here the invariant rule is 'bags −1, candies −1'. "
                f"Check back: try two orders with 3 bags (1, 2, 3 candies) — merge (1+2)−1=2 with 3 to get 2+3−1=4, or merge (2+3)−1=4 with 1 to get 4+1−1=4, the same. "
                f"Generalize: if you ate 2 candies per merge, the answer would be the total − 2×({n}−1).",
            },
        )


def gen_digitpos():
    # 이어 쓴 수 123456…의 k번째 자리 — 자릿수 블록 구조 발견. (변화와관계 난9, CEILING_SPECS 3.3)
    # 발견형 근거: 블록 분해 전략이 문제문에 없고, k≥500이면 수백 자리를 직접 쓰는 우회가 비현실적이다.
    ord_ko = {1: "첫째", 2: "둘째", 3: "셋째"}
    ord_en = {1: "1st", 2: "2nd", 3: "3rd"}
    # 오답 셋째 값(블록 경계 실수)은 스펙 표 그대로 — 블록을 빼먹거나 몫·나머지가 한 칸 밀린 계산값
    for k, w3 in [(100, 9), (500, 3), (1000, 7), (2026, 6)]:
        # 검산(digitpos) 경로1: 긴 수를 실제로 구성해 직접 인덱싱
        s = "".join(str(i) for i in range(1, 3000))
        ans = int(s[k - 1])
        # 검산 경로2: 자릿수 블록 산법으로 독립 재계산 후 대조
        rem, digits, start, prev = k, 1, 1, 0
        while rem > 9 * start * digits:
            rem -= 9 * start * digits
            prev += 9 * start * digits
            start *= 10
            digits += 1
        num = start + (rem - 1) // digits
        pos = (rem - 1) % digits + 1
        assert int(str(num)[pos - 1]) == ans, f"digitpos 검산 실패: k={k} 블록 산법 {num}/{pos} != {ans}"
        w1 = int(str(k)[0])  # k라는 '수'의 첫 자리(자리↔수 혼동)
        w2 = int(s[k - 2])   # k−1번째 자리(한 자리 어긋남)
        assert len({ans, w1, w2, w3}) == 4, f"digitpos: k={k} 보기 겹침 {ans},{w1},{w2},{w3}"
        q, rr = (rem - 1) // digits, (rem - 1) % digits + 1
        add(
            "digitpos", "CHANGE_RELATION", 9, ["자릿수 블록", "위치 계산"],
            f"자연수를 1부터 차례로 빈틈없이 이어 써서 긴 수를 만들어요: 123456789101112131415… "
            f"이렇게 쓸 때, 앞에서부터 {k}번째 자리에 오는 숫자는 무엇일까요?",
            str(ans), [str(w1), str(w2), str(w3)],
            f"자리를 블록으로 정리해요 — 한 자리 수 9개가 9자리, 두 자리 수 90개가 180자리(누적 189자리), "
            f"세 자리 수 900개가 2700자리(누적 2889자리)를 차지해요. {k}번째 자리는 누적 {prev}자리를 지나 "
            f"{digits}자리 수 블록의 {rem}번째 자리예요. {rem} = {digits}×{q} + {rr}이니 블록의 {q + 1}번째 수, "
            f"곧 {num}의 {ord_ko[pos]} 자리 — 답은 {ans}예요.",
            [(str(w1), f"{k}번째 '자리'와 {k}{'이' if _has_batchim(k) else ''}라는 '수'를 혼동했어요. 한 수가 여러 자리를 차지해요."),
             (str(w2), "한 자리 어긋났어요. 한 자리 수 9개·두 자리 수 90개가 차지하는 자리 수를 정확히 빼고 세요."),
             (str(w3), "9·189·2889 같은 블록 경계에서 나머지 계산이 한 칸 밀렸어요. 나머지가 0일 때를 조심하세요.")],
            detail=f"수는 하나씩 커지지만 '자리'는 자릿수만큼 뭉텅이로 늘어나요 — 이 어긋남을 블록 표(9·189·2889…)로 정리하는 게 열쇠예요. "
            f"되돌아보기: 찾아낸 수의 근방({num - 1}, {num}, {num + 1})을 직접 이어 써 보면 {k}번째 자리가 정말 {ans}인지 손으로 확인할 수 있어요. "
            f"일반화: 같은 표로 10000번째 자리도 즉시 구할 수 있어요 — 블록 경계에서 한 칸 밀리지 않게만 조심하세요.",
            en={
                "concepts": ["digit-count blocks", "position arithmetic"],
                "statement": f"Write the natural numbers in order without gaps to form one long string: 123456789101112131415… "
                f"What digit is in position {k} from the front?",
                "answer": str(ans),
                "distractors": [str(w1), str(w2), str(w3)],
                "explanation": f"Organize the positions into blocks — the 9 one-digit numbers take 9 positions, the 90 two-digit numbers take 180 (189 cumulative), "
                f"and the 900 three-digit numbers take 2700 (2889 cumulative). Position {k} falls past the first {prev} positions, "
                f"at position {rem} within the {digits}-digit block. Since {rem} = {digits}×{q} + {rr}, it lands on number {q + 1} of that block, "
                f"namely {num}, at its {ord_en[pos]} digit — the answer is {ans}.",
                "mistakes": [(str(w1), f"You confused position {k} (a 'place') with the number {k} itself. One number occupies several places."),
                             (str(w2), "Off by one place. Subtract exactly the places taken by the 9 one-digit and 90 two-digit numbers."),
                             (str(w3), "Your quotient-remainder slipped by one at a block boundary like 9, 189, or 2889. Watch out for the remainder-0 case.")],
                "detail": f"Numbers grow one at a time, but 'places' grow in chunks equal to the digit count — organizing that mismatch with the block table (9, 189, 2889, …) is the key. "
                f"Check back: write out the neighborhood of the found number ({num - 1}, {num}, {num + 1}) and confirm by hand that position {k} really is {ans}. "
                f"Generalize: the same table instantly gives the 10000th digit too — just don't slip by one at the block boundaries.",
            },
        )


def gen_cubesumfar():
    # 먼 항까지의 세제곱합 1³+…+n³ (n=12~25) — 직접 덧셈 봉쇄, (삼각수)² 관계 발견 강제. (변화와관계 난8, CEILING_SPECS 3.B2)
    # 발견형 근거: 항등식을 문제문에 주지 않고, n≥12에선 다섯 자리 수 덧셈 십수 회가 비현실적이라 관계 발견이 사실상 유일한 경로다.
    for n in [12, 15, 20, 25]:
        tri = n * (n + 1) // 2
        ans = tri * tri
        sq_sum = n * (n + 1) * (2 * n + 1) // 6  # 제곱합(혼동 오답)
        # 검산(cubesumfar): 세제곱을 정말 하나씩 다 더해 (삼각수)² 항등식과 대조
        direct = 0
        for i in range(1, n + 1):
            direct += i ** 3
        assert direct == ans, f"cubesumfar 검산 실패: {direct} != {ans}"
        assert len({ans, sq_sum, tri, n ** 3}) == 4, f"cubesumfar: n={n} 보기 겹침"
        add(
            "cubesumfar", "CHANGE_RELATION", 8, ["세제곱의 합", "숨은 관계 발견"],
            f"1³ + 2³ + 3³ + … + {n}³ 의 값은 얼마일까요? (각 수를 세제곱해 더한 값이에요 — 처음 몇 항의 합을 관찰하면 지름길이 보여요)",
            str(ans), [str(sq_sum), str(tri), str(n ** 3)],
            f"처음 몇 항을 직접 계산해요 — 1, 1+8=9, 9+27=36, 36+64=100. 어디서 본 수들이죠? 1=1², 9=3², 36=6², 100=10² — "
            f"모두 제곱수, 그것도 1, 3, 6, 10이라는 삼각수(1, 1+2, 1+2+3, …)의 제곱이에요! 한 항 더 확인하면 100+125=225=15²으로 규칙이 이어져요. "
            f"그러니 {n}까지의 합은 (1+2+…+{n})² = {tri}² = {ans}예요.",
            [(str(sq_sum), "그건 '제곱'의 합(1²+…+n²)이에요. 세제곱의 합은 전혀 다른 관계를 따라요."),
             (str(tri), f"1+2+…+{n}까지만 구하고 멈췄어요. 발견한 관계는 그 값을 '제곱'해요."),
             (str(n ** 3), "마지막 항 하나가 아니라 전부의 합이에요. 합은 마지막 항보다 훨씬 커요.")],
            detail=f"세제곱 k³은 k×k 정사각형을 k겹 쌓은 것 — 이를 ㄱ자(그노몬) 모양으로 펼쳐 붙이면 큰 정사각형이 계단식으로 자라나, "
            f"세제곱의 합 전체가 (1+2+…+n)² 정사각형과 정확히 포개져요. 되돌아보기: n=4로 검산하면 1+8+27+64=100=10²이에요. "
            f"일반화 도전: 홀수만의 세제곱합(1³+3³+5³+…)은 어떤 규칙을 따를까요? 직접 실험으로 찾아보세요.",
            en={
                "concepts": ["sum of cubes", "discovering hidden relationships"],
                "statement": f"What is the value of 1³ + 2³ + 3³ + … + {n}³? (Cube each number and add. Watching the first few partial sums reveals a shortcut.)",
                "answer": str(ans),
                "distractors": [str(sq_sum), str(tri), str(n ** 3)],
                "explanation": f"Compute the first few partial sums — 1, 1+8=9, 9+27=36, 36+64=100. Seen these before? 1=1², 9=3², 36=6², 100=10² — "
                f"all perfect squares, and of the triangular numbers 1, 3, 6, 10 (1, 1+2, 1+2+3, …) at that! One more term confirms it: 100+125=225=15². "
                f"So the sum up to {n} is (1+2+…+{n})² = {tri}² = {ans}.",
                "mistakes": [(str(sq_sum), "That's the sum of the 'squares' (1²+…+n²). The sum of cubes follows an entirely different relationship."),
                             (str(tri), f"You stopped at 1+2+…+{n}. The discovered relationship SQUARES that value."),
                             (str(n ** 3), "It's the sum of all the terms, not the last term alone. The sum is far larger than the last term.")],
                "detail": f"A cube k³ is a k×k square stacked k layers deep — unfolding it into an L-shaped gnomon and wrapping it on, the big square grows step by step, "
                f"so the whole sum of cubes tiles exactly the (1+2+…+n)² square. Check back: for n=4, 1+8+27+64=100=10². "
                f"A challenge to generalize: what rule does the sum of only the odd cubes (1³+3³+5³+…) follow? Find out by experiment.",
            },
        )


def gen_seqcommon():
    # 두 등차 패턴의 공통 항 — 공통 항 자체가 '간격 = 최소공배수'인 새 등차를 이룸을 발견. (변화와관계 난7, 신규 설계)
    # 발견형 근거: 공통 수를 찾는 방법이 문제문에 없고, k번째까지 직접 나열은 두 수열 합계 100항 이상이라 봉쇄 —
    # 공통 항의 간격이 (두 간격의 곱이 아니라) 최소공배수라는 구조 발견이 필수다.
    for a1, d1, a2, d2, k in [(2, 6, 8, 8, 15), (1, 4, 3, 6, 20), (5, 9, 2, 12, 12), (3, 10, 7, 4, 25)]:
        assert gcd(d1, d2) > 1, f"seqcommon: ({d1},{d2}) 곱≠최소공배수 함정이 죽어 있음"
        step = d1 * d2 // gcd(d1, d2)
        # 검산(seqcommon) 경로1: 두 수열을 대량 생성해 교집합에서 k번째를 직접 추출 + 간격 균일성 확인
        N = 3000
        common = sorted({a1 + d1 * i for i in range(N)} & {a2 + d2 * i for i in range(N)})[: k + 3]
        first = common[0]
        ans = common[k - 1]
        assert {common[i + 1] - common[i] for i in range(len(common) - 1)} == {step}, f"seqcommon: 간격이 lcm이 아님"
        assert ans == first + (k - 1) * step, f"seqcommon 검산 실패: {ans} != {first + (k - 1) * step}"
        # 검산 경로2: 작은 수부터 나머지 조건 두 개를 하나씩 검사하며 k번째까지 세기
        v, cnt = 0, 0
        while cnt < k:
            v += 1
            if v >= a1 and (v - a1) % d1 == 0 and v >= a2 and (v - a2) % d2 == 0:
                cnt += 1
        assert v == ans, f"seqcommon 검산 실패(경로2): {v} != {ans}"
        w1 = first + (k - 1) * d1 * d2   # 간격을 곱으로 착각
        w2 = first + k * step            # 한 항 더 건넘
        w3 = first + (k - 1) * (d1 + d2)  # 간격을 합으로 착각
        assert len({ans, w1, w2, w3}) == 4, f"seqcommon: 보기 겹침 {ans},{w1},{w2},{w3}"
        add(
            "seqcommon", "CHANGE_RELATION", 7, ["공통 항", "최소공배수 간격"],
            f"두 수 배열이 있어요. 배열 A는 {a1}에서 시작해 {d1}씩 커져요: {a1}, {a1 + d1}, {a1 + 2 * d1}, {a1 + 3 * d1}, … "
            f"배열 B는 {a2}에서 시작해 {d2}씩 커져요: {a2}, {a2 + d2}, {a2 + 2 * d2}, … "
            f"두 배열에 모두 나오는 수를 작은 것부터 차례로 찾을 때, {k}번째 수는 얼마일까요?",
            str(ans), [str(w1), str(w2), str(w3)],
            f"두 배열을 나란히 나열해 공통 수를 몇 개 찾아봐요 — {first}, {first + step}, {first + 2 * step}, … 간격이 {step}으로 일정해요. "
            f"우연이 아니에요: 공통 수에서 다음 공통 수로 가려면 A에서도 B에서도 '정확히 같은 거리'를 걸어야 하니, 그 거리는 "
            f"{d1}의 배수이면서 {d2}의 배수 — 곧 최소공배수 {step}이에요({d1}×{d2}={d1 * d2}가 아니에요!). "
            f"그래서 {k}번째 공통 수는 {first} + {k - 1}×{step} = {ans}예요.",
            [(str(w1), f"간격을 두 수의 곱 {d1}×{d2}={d1 * d2}로 잡았어요. 실제 간격은 최소공배수 {step}이에요 — 공통 수를 두세 개 직접 찾아 간격을 확인하세요."),
             (str(w2), f"첫 공통 수 {first}에서 {k}번째까지 가려면 간격을 {k}−1번만 건너요. 한 번 더 건넜어요."),
             (str(w3), f"간격을 {d1}+{d2}={d1 + d2}로 잡았어요. 두 배열이 다시 만나려면 각자 '같은 거리'를 가야 하니 합이 아니라 공배수예요.")],
            detail=f"두 등차 패턴의 공통 항은 그 자체로 새로운 등차 패턴이 돼요 — 간격은 두 간격의 최소공배수예요. "
            f"되돌아보기: {ans}가 정말 두 배열 모두에 있는지 확인해 보세요 — ({ans}−{a1})÷{d1}과 ({ans}−{a2})÷{d2}가 모두 나누어떨어져요. "
            f"일반화: 시작 수에 따라 공통 수가 하나도 없을 수도 있어요 — 예를 들어 짝수만 나오는 배열과 홀수만 나오는 배열은 영원히 안 만나요.",
            en={
                "concepts": ["common terms of sequences", "least-common-multiple gap"],
                "statement": f"There are two number sequences. Sequence A starts at {a1} and grows by {d1}: {a1}, {a1 + d1}, {a1 + 2 * d1}, {a1 + 3 * d1}, … "
                f"Sequence B starts at {a2} and grows by {d2}: {a2}, {a2 + d2}, {a2 + 2 * d2}, … "
                f"Listing the numbers that appear in both sequences from smallest to largest, what is the {k}th one?",
                "answer": str(ans),
                "distractors": [str(w1), str(w2), str(w3)],
                "explanation": f"List both sequences side by side and find a few common numbers — {first}, {first + step}, {first + 2 * step}, …: the gap is a steady {step}. "
                f"No accident: to get from one common number to the next you must walk 'exactly the same distance' in both A and B, so that distance is "
                f"a multiple of {d1} and of {d2} — the least common multiple, {step} (NOT {d1}×{d2}={d1 * d2}!). "
                f"So the {k}th common number is {first} + {k - 1}×{step} = {ans}.",
                "mistakes": [(str(w1), f"You took the gap to be the product {d1}×{d2}={d1 * d2}. The real gap is the least common multiple {step} — find two or three common numbers and check the gap."),
                             (str(w2), f"From the first common number {first}, reaching the {k}th takes only {k}−1 jumps of the gap. You jumped once too many."),
                             (str(w3), f"You took the gap to be {d1}+{d2}={d1 + d2}. To meet again, both sequences must each cover the SAME distance — a common multiple, not a sum.")],
                "detail": f"The common terms of two arithmetic patterns form a new arithmetic pattern of their own — with gap equal to the least common multiple of the two gaps. "
                f"Check back: confirm {ans} really is in both sequences — ({ans}−{a1})÷{d1} and ({ans}−{a2})÷{d2} both divide evenly. "
                f"Generalize: depending on the starting numbers there may be no common number at all — a sequence of only evens and a sequence of only odds never meet.",
            },
        )


def gen_pyramidmax():
    # 수 피라미드 바닥 배치 최적화 — 칸마다 꼭대기에 더해지는 횟수(1·4·6·4·1)가 다름을 발견. (변화와관계 난7, 신규 설계)
    # 발견형 근거: 배치 전략·기여 횟수가 문제문에 없고, 5!=120가지 전수 시도는 비현실적이라
    # '칸마다 꼭대기에 더해지는 횟수가 다르다'는 숨은 대응을 스스로 발견해야만 한다.
    from itertools import permutations as _perms

    def _top(row):
        while len(row) > 1:
            row = [x + y for x, y in zip(row, row[1:])]
        return row[0]

    W = [1, 4, 6, 4, 1]  # 각 바닥 칸이 꼭대기에 더해지는 횟수(경로 수)
    for vals, goal in [((1, 2, 3, 4, 5), "max"), ((1, 2, 3, 4, 5), "min"), ((2, 3, 4, 5, 6), "max"), ((1, 3, 5, 7, 9), "min")]:
        # 검산(pyramidmax) 경로1: 120가지 배치 전수 시도로 최적값을 직접 탐색
        tops = [_top(list(p)) for p in _perms(vals)]
        ans = max(tops) if goal == "max" else min(tops)
        # 검산 경로2: 가중치(1,4,6,4,1) 탐욕 배치를 실제로 쌓아 전수 결과와 대조
        a, b, c, d, e = sorted(vals)
        greedy = [b, d, e, c, a] if goal == "max" else [d, b, a, c, e]
        assert _top(greedy[:]) == ans == sum(w * v for w, v in zip(W, greedy)), f"pyramidmax 검산 실패: {goal} {vals}"
        if goal == "max":
            m1, m2, m3 = _top([a, b, c, d, e]), _top([a, b, e, c, d]), _top([e, a, b, c, d])
            why1 = "수를 그냥 크기 순서대로 놓고 쌓은 값이에요. 칸마다 꼭대기에 더해지는 횟수(1·4·6·4·1)가 달라서, 어디에 놓느냐가 결과를 바꿔요."
            why2 = "가장 큰 수를 가운데 둔 것까진 좋았지만, 그 양옆 칸도 4번씩 더해져요 — 다음으로 큰 수들을 양옆에 두어야 해요."
            why3 = "가장 큰 수를 양 끝에 두면 딱 1번밖에 안 더해져요. 여러 갈래로 겹쳐 올라가는 가운데 칸에 두어야 해요."
            ew1 = "This is the top when the numbers are simply placed in size order. Each cell is added into the top a different number of times (1·4·6·4·1), so placement changes the result."
            ew2 = "Putting the largest number in the middle was right, but the two cells beside it are also added 4 times each — the next-largest numbers must go there."
            ew3 = "Placed at an end, the largest number is added only once. It must go in the middle cell, whose copies pile up along many paths."
        else:
            m1, m2, m3 = _top([a, b, c, d, e]), _top([e, d, a, c, b]), _top([a, e, d, c, b])
            why1 = "수를 그냥 크기 순서대로 놓고 쌓은 값이에요. 배치에 따라 꼭대기가 달라져요 — 더 작게 만들 수 있어요."
            why2 = "가장 작은 수를 가운데 둔 것까진 좋았지만, 4번씩 더해지는 양옆 칸에도 작은 수들을 두어야 해요."
            why3 = "양 끝은 원래 1번씩만 더해지는 자리예요. 작은 수는 여러 번 더해지는 가운데 쪽에, 큰 수를 양 끝에 두어야 꼭대기가 작아져요."
            ew1 = "This is the top when the numbers are simply placed in size order. Placement changes the top — it can be made smaller."
            ew2 = "Putting the smallest number in the middle was right, but the small numbers must also fill the two cells beside it, which are added 4 times each."
            ew3 = "The end cells are only added once each anyway. Small numbers belong toward the middle where copies pile up, and the LARGE numbers at the ends, to shrink the top."
        assert len({ans, m1, m2, m3}) == 4, f"pyramidmax: 보기 겹침 {ans},{m1},{m2},{m3}"
        vtxt = ", ".join(str(v) for v in vals)
        goal_ko = "크게" if goal == "max" else "작게"
        mid, side1, side2, end1, end2 = (e, d, c, b, a) if goal == "max" else (a, b, c, d, e)
        add(
            "pyramidmax", "CHANGE_RELATION", 7, ["수 피라미드", "기여 횟수 발견"],
            f"수 피라미드는 위 칸이 바로 아래 두 칸의 합이에요. 맨 아랫줄이 다섯 칸인 피라미드의 아랫줄에 {vtxt}를 한 번씩만 알맞게 놓아, "
            f"꼭대기 수를 가장 {goal_ko} 만들려고 해요. 이때 꼭대기 수는 얼마일까요?",
            str(ans), [str(m1), str(m2), str(m3)],
            f"아랫줄 3칸짜리 미니 피라미드로 실험하면 꼭대기 = (왼쪽 끝) + 2×(가운데) + (오른쪽 끝) — 가운데 칸만 2번 더해져요. "
            f"같은 눈으로 보면 다섯 칸일 때 각 칸이 꼭대기에 더해지는 횟수는 왼쪽부터 1, 4, 6, 4, 1번이에요. "
            f"그러니 많이 더해지는 칸에 {'큰' if goal == 'max' else '작은'} 수를 — {mid}{_eul(mid)} 가운데(6번), {side1}{_gwa(side1)} {side2}{_eul(side2)} 그 양옆(4번씩), "
            f"{end1}{_gwa(end1)} {end2}{_eul(end2)} 양 끝(1번씩)에 놓으면 꼭대기는 6×{mid}+4×{side1}+4×{side2}+1×{end1}+1×{end2} = {ans}예요.",
            [(str(m1), why1), (str(m2), why2), (str(m3), why3)],
            detail=f"각 칸의 기여 횟수 1, 4, 6, 4, 1은 그 칸에서 꼭대기까지 올라가는 길의 수예요 — 한 층 오를 때마다 왼쪽 위·오른쪽 위 두 갈래가 생겨서, "
            f"아랫줄이 3칸이면 1, 2, 1 / 4칸이면 1, 3, 3, 1처럼 파스칼 삼각형의 줄과 똑같이 자라요. "
            f"되돌아보기: 최적 배치를 실제로 한 층씩 쌓아 꼭대기 {ans}{_eul(ans)} 확인하고, 크기 순서대로 놓은 배치({m1})와 비교해 보세요. "
            f"일반화: 아랫줄이 6칸이면 기여 횟수는 1, 5, 10, 10, 5, 1 — 같은 눈으로 어디에 무엇을 놓을지 정할 수 있어요.",
            en={
                "concepts": ["number pyramid", "discovering contribution counts"],
                "statement": f"In a number pyramid, each cell is the sum of the two cells directly below it. Place {vtxt} exactly once each in the five bottom cells "
                f"so that the top number is as {'large' if goal == 'max' else 'small'} as possible. What is that top number?",
                "answer": str(ans),
                "distractors": [str(m1), str(m2), str(m3)],
                "explanation": f"Experiment with a mini pyramid of 3 bottom cells: top = (left end) + 2×(middle) + (right end) — only the middle cell is added twice. "
                f"Seen the same way, with five cells the counts of how many times each cell is added into the top are 1, 4, 6, 4, 1 from the left. "
                f"So put the {'large' if goal == 'max' else 'small'} numbers where they are added most — {mid} in the middle (6 times), {side1} and {side2} beside it (4 times each), "
                f"{end1} and {end2} at the ends (once each): the top is 6×{mid}+4×{side1}+4×{side2}+1×{end1}+1×{end2} = {ans}.",
                "mistakes": [(str(m1), ew1), (str(m2), ew2), (str(m3), ew3)],
                "detail": f"The contribution counts 1, 4, 6, 4, 1 are the numbers of paths from each cell up to the top — every level up splits into upper-left and upper-right, "
                f"so they grow exactly like rows of Pascal's triangle (1, 2, 1 for 3 cells; 1, 3, 3, 1 for 4). "
                f"Check back: actually build the optimal arrangement level by level to confirm the top is {ans}, and compare with the size-order arrangement ({m1}). "
                f"Generalize: with 6 bottom cells the counts are 1, 5, 10, 10, 5, 1 — the same eye tells you where everything goes.",
            },
        )


def gen_funcinv():
    # 규칙이 숨겨진 함수 기계 역추적 — 곱 구조(n×(n+off)) 발견 후 출력→입력. (변화와관계 난6, 신규 설계)
    # 발견형 근거: 상자의 규칙이 문제문에 없어 여러 쌍 대조로 스스로 발견해야 하고('몇 배' 가설은 쌍마다 배율이 달라 무너짐),
    # 규칙 발견 없이는 출력→입력 역추적을 시작할 수조차 없다.
    from math import isqrt as _isqrt
    for off, pairs, out in [(1, [(2, 6), (3, 12), (5, 30)], 90), (1, [(3, 12), (6, 42), (8, 72)], 132),
                            (2, [(2, 8), (4, 24), (5, 35)], 80), (2, [(3, 15), (6, 48), (8, 80)], 120)]:
        (x1, y1), (x2, y2), (x3, y3) = pairs
        assert all(y == x * (x + off) for x, y in pairs), f"funcinv: 쌍이 규칙과 불일치 {pairs}"
        # 검산(funcinv) 경로1: '×a+b' 선형 규칙 완전탐색 — 세 쌍을 동시에 맞추는 선형 규칙이 없어야 곱 구조 발견이 강제됨
        linear = [(aa, bb) for aa in range(0, 30) for bb in range(-60, 61) if all(aa * x + bb == y for x, y in pairs)]
        assert linear == [], f"funcinv: 선형 규칙이 통함 {linear}"
        # 검산 경로2: 입력 후보 전 범위 완전탐색으로 답의 존재·유일성
        sols = [m for m in range(1, 500) if m * (m + off) == out]
        assert len(sols) == 1, f"funcinv: 해가 유일하지 않음 {sols}"
        ans = sols[0]
        # 검산 경로3: 정수 제곱근 근방 역산 — 다른 경로로 같은 답
        assert _isqrt(out) in (ans, ans + off) and ans * (ans + off) == out, f"funcinv 검산 실패: {ans}"
        r1 = y1 // x1
        assert y1 % x1 == 0 and out % r1 == 0, f"funcinv: ×배 함정 오답이 정수가 아님"
        w1, w2, w3 = out // r1, ans + off, ans - 1
        assert len({ans, w1, w2, w3}) == 4, f"funcinv: 보기 겹침 {ans},{w1},{w2},{w3}"
        add(
            "funcinv", "CHANGE_RELATION", 6, ["대응 규칙 발견", "거꾸로 추적"],
            f"마법 상자는 수를 넣으면 정해진 규칙으로 바꿔서 내보내요. {x1}{_eul(x1)} 넣으면 {y1}{_iga(y1)}, {x2}{_eul(x2)} 넣으면 {y2}{_iga(y2)}, "
            f"{x3}{_eul(x3)} 넣으면 {y3}{_iga(y3)} 나와요. 이 상자에서 {out}{_iga(out)} 나왔다면, 넣은 수는 얼마였을까요?",
            str(ans), [str(w1), str(w2), str(w3)],
            f"먼저 상자의 규칙부터 찾아야 해요. '몇 배' 가설은 무너져요 — {x1}→{y1}은 {r1}배지만 {x2}→{y2}는 {y2 // x2}배예요. "
            f"각 출력을 곱으로 쪼개 보면 {y1}={x1}×{x1 + off}, {y2}={x2}×{x2 + off}, {y3}={x3}×{x3 + off} — "
            f"넣은 수에 (넣은 수+{off}){_eul(off)} 곱하는 규칙이에요. 이제 거꾸로: {out}{_eul(out)} 차가 {off}인 두 수의 곱으로 나타내면 "
            f"{out}={ans}×{ans + off}. 넣은 수는 {ans}예요.",
            [(str(w1), f"첫 쌍({x1}→{y1})만 보고 '×{r1}' 규칙이라 여겨 {out}÷{r1}을 했어요. 다른 쌍에 대면 배율이 달라져요 — 규칙은 모든 쌍에 맞아야 해요."),
             (str(w2), f"{out}={ans}×{ans + off}까지 갔는데 큰 쪽 수를 답했어요. 상자에 '넣은' 수는 작은 쪽 {ans}예요 — {ans + off}{_eul(ans + off)} 넣으면 {(ans + off) * (ans + 2 * off)}{_iga((ans + off) * (ans + 2 * off))} 나와요."),
             (str(w3), f"거의 다 왔어요. 후보를 규칙에 다시 넣어 검산하세요 — {ans - 1}{_eul(ans - 1)} 넣으면 {(ans - 1) * (ans - 1 + off)}{_iga((ans - 1) * (ans - 1 + off))} 나오지, {out}{_iga(out)} 아니에요.")],
            detail=f"입력→출력 표에서 규칙을 찾을 땐 '몇 배'·'얼마 더하기' 같은 한 단계 가설이 모든 쌍에 맞는지 반드시 대조하고, 무너지면 "
            f"출력을 '입력과 관련된 두 수의 곱'으로 쪼개 보는 것이 강력한 다음 수예요. 규칙을 찾으면 거꾸로 가기는 곱 분해 — "
            f"차가 {off}인 두 수의 곱이 {out}{_iga(out)} 되는 짝은 {ans}×{ans + off} 하나뿐이라 답이 유일해요. "
            f"되돌아보기: 찾은 규칙이 보여 준 세 쌍 모두에 맞는지, 그리고 {ans}{_eul(ans)} 넣으면 정말 {out}{_iga(out)} 나오는지 검산하세요.",
            en={
                "concepts": ["discovering a mapping rule", "working backward"],
                "statement": f"A magic box changes any number you put in, always by the same fixed rule. Putting in {x1} gives {y1}, putting in {x2} gives {y2}, "
                f"and putting in {x3} gives {y3}. The box just put out {out} — what number was put in?",
                "answer": str(ans),
                "distractors": [str(w1), str(w2), str(w3)],
                "explanation": f"First discover the box's rule. The 'times what' guess collapses — {x1}→{y1} is ×{r1}, but {x2}→{y2} is ×{y2 // x2}. "
                f"Splitting each output into a product: {y1}={x1}×{x1 + off}, {y2}={x2}×{x2 + off}, {y3}={x3}×{x3 + off} — "
                f"the rule multiplies the input by (input+{off}). Now go backward: writing {out} as a product of two numbers differing by {off}, "
                f"{out}={ans}×{ans + off}. The number put in was {ans}.",
                "mistakes": [(str(w1), f"Looking only at the first pair ({x1}→{y1}) you took the rule as '×{r1}' and computed {out}÷{r1}. The other pairs give different multipliers — the rule must fit every pair."),
                             (str(w2), f"You reached {out}={ans}×{ans + off} but answered the larger number. The number PUT IN is the smaller one, {ans} — putting in {ans + off} would give {(ans + off) * (ans + 2 * off)}."),
                             (str(w3), f"So close — check the candidate by feeding it back through the rule: putting in {ans - 1} gives {(ans - 1) * (ans - 1 + off)}, not {out}.")],
                "detail": f"When hunting a rule in an input→output table, always test one-step guesses ('times what', 'plus what') against every pair; when they collapse, "
                f"splitting the output into a product of two numbers related to the input is a powerful next move. Once the rule is found, going backward is factoring — "
                f"only one pair of numbers differing by {off} multiplies to {out}, namely {ans}×{ans + off}, so the answer is unique. "
                f"Check back: confirm the rule fits all three shown pairs, and that putting in {ans} really gives {out}.",
            },
        )
