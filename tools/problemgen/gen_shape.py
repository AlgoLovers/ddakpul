"""도형과 측정(SHAPE_MEASUREMENT) 제너레이터 — 함수 1개 = 방법(family) 1개 = 문제 그룹.

실행 순서는 build.py의 GENERATORS 리스트가 정한다(rng 재현성). 여기선 정의만.
"""
from core import *  # noqa: F401,F403 — 공용 인프라(add·rng·헬퍼·상수)


# ── 검산 전용 헬퍼 — 순수 결정론 계산만, rng를 절대 소비하지 않는다 ────────────────
def _seg_intersection(p1, p2, p3, p4):
    """선분 p1p2와 p3p4의 내부 교점(양 끝점 제외). 없으면 None. 분수 좌표면 오차 0."""
    dx1, dy1 = p2[0] - p1[0], p2[1] - p1[1]
    dx2, dy2 = p4[0] - p3[0], p4[1] - p3[1]
    den = dx1 * dy2 - dy1 * dx2
    if den == 0:
        return None
    t = ((p3[0] - p1[0]) * dy2 - (p3[1] - p1[1]) * dx2) / den
    u = ((p3[0] - p1[0]) * dy1 - (p3[1] - p1[1]) * dx1) / den
    if 0 < t < 1 and 0 < u < 1:
        return (p1[0] + t * dx1, p1[1] + t * dy1)
    return None


def _convex_diag_geometry(n):
    """일반 위치 볼록 n각형(포물선 위 점 — 어느 세 대각선도 한 점에서 안 만남)에
    대각선을 전부 긋고 (내부 교점 수, 내부 영역 수)를 실제 선분 교차 계산으로 센다.
    diagcross·diagregions 검산용 — 조합 공식과 완전히 독립인 기하 경로."""
    from fractions import Fraction

    ts = [0, 1, 3, 7, 12, 20, 30, 45][:n]
    pts = [(Fraction(t), Fraction(t * t)) for t in ts]
    diags = [(i, j) for i in range(n) for j in range(i + 1, n) if (j - i) not in (1, n - 1)]
    on_diag = {d: set() for d in diags}
    points = set()
    for a in range(len(diags)):
        for b in range(a + 1, len(diags)):
            i1, j1 = diags[a]
            i2, j2 = diags[b]
            if len({i1, j1, i2, j2}) < 4:
                continue  # 꼭짓점을 공유하는 두 대각선은 볼록 다각형 내부에서 안 만남
            p = _seg_intersection(pts[i1], pts[j1], pts[i2], pts[j2])
            if p is not None:
                points.add(p)
                on_diag[diags[a]].add(p)
                on_diag[diags[b]].add(p)
    # 평면 그래프 V−E+F=2 → 내부 영역 = E−V+1 (변·대각선을 교점에서 실제로 쪼갠 조각 수로)
    v_cnt = n + len(points)
    e_cnt = n + sum(len(ps) + 1 for ps in on_diag.values())
    return len(points), e_cnt - v_cnt + 1


def _lattice_triangle_stats(tri):
    """격자 삼각형의 (내부 격자점, 둘레 격자점, 넓이×2)를 좌표 순회로 직접 센다.
    pick 검산용 — 픽의 정리를 쓰지 않는 독립 경로(내부는 부호 판정, 둘레는 gcd)."""
    (x1, y1), (x2, y2), (x3, y3) = tri
    area2 = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
    boundary = sum(gcd(abs(qx - px), abs(qy - py)) for (px, py), (qx, qy) in zip(tri, tri[1:] + tri[:1]))
    inner = 0
    for px in range(min(x1, x2, x3), max(x1, x2, x3) + 1):
        for py in range(min(y1, y2, y3), max(y1, y2, y3) + 1):
            s1 = (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)
            s2 = (x3 - x2) * (py - y2) - (y3 - y2) * (px - x2)
            s3 = (x1 - x3) * (py - y3) - (y1 - y3) * (px - x3)
            if (s1 > 0 and s2 > 0 and s3 > 0) or (s1 < 0 and s2 < 0 and s3 < 0):
                inner += 1
    return inner, boundary, area2


# ── 12. 격자 최단 경로 (난4, 도형과측정) ─────────────────────────────────────
def gen_grid():
    for w, h in [(3, 2), (3, 3), (4, 2)]:
        ans = comb(w + h, w)

        # 검산: 오른쪽/위 이동을 실제로 전부 걸어 보는 완전열거(DFS)와 대조
        def _walk(x, y):
            if (x, y) == (w, h):
                return 1
            return (_walk(x + 1, y) if x < w else 0) + (_walk(x, y + 1) if y < h else 0)

        assert _walk(0, 0) == ans, f"grid 검산실패: {w}x{h}"
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


# ── 16. 테두리 세기 (난3, 도형과측정) ────────────────────────────────────────
def gen_border():
    for side in [7, 8, 12, 15]:
        ans = 4 * side - 4
        # 검산: side×side 칸을 전부 훑어 테두리 칸만 세는 셀 단위 완전열거와 대조
        edge_cnt = sum(1 for x in range(side) for y in range(side) if x in (0, side - 1) or y in (0, side - 1))
        assert edge_cnt == ans, f"border 검산실패: side={side}"
        add(
            "border", "SHAPE_MEASUREMENT", 3, ["테두리 세기", "꼭짓점 중복"],
            f"바둑돌을 그림처럼 속이 빈 정사각형 모양으로 한 변에 {side}개씩 놓으려고 해요. 바둑돌은 모두 몇 개 필요할까요?",
            f"{ans}개", [f"{4 * side}개", f"{ans - 2}개", f"{side * side}개"],
            f"네 변에 {side}개씩 있다고 {side}×4={4 * side}개로 세면 함정에 빠져요. 네 꼭짓점의 돌은 두 변에 걸쳐 있어서 두 번씩 세어졌거든요. 두 번 센 4개를 빼면 {4 * side}−4={ans}개예요.",
            [(f"{4 * side}개", "꼭짓점 돌 4개를 두 번 센 거예요."), (f"{side * side}개", "속이 꽉 찬 정사각형이 아니라 테두리만이에요.")],
            # 그림-지문 일치 필수: 렌더러(ProblemFigureView·preview)는 side 20까지 지원 —
            # 과거 min(side,12) 캡이 border-4(한 변 15)에서 그림(12)≠지문(15) 버그를 만들었다.
            figure={"type": "DOT_BORDER", "params": {"side": side}},
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


# ── 18. 거울 시계 (난3, 도형과측정) ──────────────────────────────────────────
def gen_mirror():
    for actual in [2, 4, 5, 7]:
        mirror = 12 - actual
        # 검산: 좌우 반전을 각도로 시뮬레이션 — 실제 시침각을 12(위) 축 기준으로 반사하면
        # 거울 속 시각(mirror시)이 그대로 나와야 한다
        m_ang = (-30 * actual) % 360
        assert m_ang % 30 == 0 and (m_ang // 30 or 12) == mirror, f"mirror 검산실패: actual={actual}"
        assert mirror != actual, f"mirror 검산실패: 거울상과 실제가 같음(actual={actual})"
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
        # 검산: 세로선 2개·가로선 2개의 모든 조합을 실제로 나열해 세는 완전열거와 대조
        rect_cnt = sum(
            1
            for x1 in range(w + 1) for x2 in range(x1 + 1, w + 1)
            for y1 in range(h + 1) for y2 in range(y1 + 1, h + 1)
        )
        assert rect_cnt == ans, f"rectcount 검산실패: {w}x{h}"
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
        # 검산: 꼭짓점 쌍을 전부 나열하고 변(이웃 쌍)만 뺀 완전열거와 대조
        diag_cnt = sum(1 for i in range(n) for j in range(i + 1, n) if (j - i) not in (1, n - 1))
        assert diag_cnt == ans, f"polydiag 검산실패: n={n}"
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
        # 검산: 두 바늘의 속도(시침 0.5도/분·분침 6도/분)로 사이각을 독립 시뮬레이션
        assert m % 2 == 0, f"clockmin 검산실패: 홀수 분({m})은 시침각이 정수가 아님"
        sim = abs(((h % 12) * 30 + m * 0.5) - m * 6.0)
        sim = min(sim, 360.0 - sim)
        assert abs(sim - ans) < 1e-9 and 0 <= ans <= 180, f"clockmin 검산실패: {h}시 {m}분"
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
    from itertools import product

    for a, b, c in [(2, 3, 4), (3, 3, 3), (2, 2, 5), (1, 3, 4)]:
        ans = 2 * (a * b + b * c + a * c)
        volume = a * b * c
        # 검산: 단위정육면체 좌표를 전부 돌며 바깥에 노출된 면을 직접 세는 열거와 대조
        exposed = sum(
            1
            for x, y, z in product(range(a), range(b), range(c))
            for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
            if not (0 <= x + dx < a and 0 <= y + dy < b and 0 <= z + dz < c)
        )
        assert exposed == ans, f"cubesurf 검산실패: {a}x{b}x{c}"
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
            # 난이도 재조정(5→4, 2026-07 d1~5 스캔): 쌓기나무 사다리(d1→2→3)에서 d5는 과대.
            "cubestack", "SHAPE_MEASUREMENT", 4, ["쌓기나무", "공간 지각"],
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
            # 검산: 밑변으로 가는 선 2개 조합을 실제로 전부 나열해 세고(완전열거),
            # 최소 삼각형 수(이웃한 선 쌍)도 함께 대조
            pairs = [(i, j) for i in range(lines) for j in range(i + 1, lines)]
            assert len(pairs) == ans, f"{fam} 검산실패: k={k}"
            assert sum(1 for i, j in pairs if j == i + 1) == small, f"{fam} 검산실패(최소 삼각형): k={k}"
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


# ── 77. 정사각형 둘레 ↔ 넓이 (난3, 도형과측정) ──────────────────────────────
def gen_square_area():
    for side in [6, 8, 5, 9]:
        perim = side * 4
        area = side * side
        # 검산: 둘레→한 변 나눗셈이 정확한지 확인하고, 넓이를 셀 단위 마스크로 재계산
        assert perim % 4 == 0, f"sqarea 검산실패: 둘레 {perim}이 4의 배수가 아님"
        cells = {(x, y) for x in range(perim // 4) for y in range(perim // 4)}
        assert len(cells) == area, f"sqarea 검산실패: side={side}"
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


# ── 125. 닮음 넓이비 (난7, 도형과측정) ──────────────────────────────────────
def gen_similar_area_ratio():
    for r1, r2, area1 in [(2, 3, 8), (1, 2, 5), (3, 4, 18), (2, 5, 12)]:
        assert (area1 * r2 * r2) % (r1 * r1) == 0
        area2 = area1 * r2 * r2 // (r1 * r1)
        add(
            # 난이도 재조정(7→5, 2026-07 d7 감사): 넓이비=길이비² 1스텝 적용 — 발견 없음.
            "simarea", "SHAPE_MEASUREMENT", 5, ["닮음", "넓이비"],
            f"두 도형이 서로 닮았고 닮음비(대응 변의 길이 비)가 {r1}:{r2}예요. 작은 도형의 넓이가 {area1}㎠일 때, 큰 도형의 넓이는 몇 ㎠일까요?",
            f"{area2}㎠", [f"{area1 * r2 // r1}㎠", f"{area1 * (r2 - r1)}㎠", f"{area2 + area1}㎠"],
            f"길이가 {r1}:{r2}로 닮으면 넓이는 그 '제곱'인 {r1}²:{r2}² = {r1 * r1}:{r2 * r2}로 커져요(가로도 세로도 늘어나니까). 작은 넓이 {area1}에 {r2 * r2}/{r1 * r1}을 곱하면 {area2}㎠예요.",
            [(f"{area1 * r2 // r1}㎠", f"넓이는 길이 비({r1}:{r2}) 그대로가 아니라 '제곱' 비로 커져요.")],
            detail="닮음에서 길이가 k배면 넓이는 k²배, 부피는 k³배예요(차원마다 하나씩 곱해지니까). 지도 축척이 2배면 넓이는 4배, 인형이 3배 크면 무게(부피)는 27배. 이 '차원의 제곱·세제곱'은 실생활에서 자주 헷갈리는 부분이에요.",
            en={
                "statement": f"Two shapes are similar, with a similarity ratio (ratio of corresponding side lengths) of {r1}:{r2}. If the smaller shape has area {area1} cm², what is the area of the larger shape, in cm²?",
                "answer": f"{area2}cm²",
                "distractors": [f"{area1 * r2 // r1}cm²", f"{area1 * (r2 - r1)}cm²", f"{area2 + area1}cm²"],
                "explanation": f"When lengths are similar in the ratio {r1}:{r2}, areas grow by the 'square' of that, {r1}²:{r2}² = {r1 * r1}:{r2 * r2} (because both width and height stretch). Multiplying the small area {area1} by {r2 * r2}/{r1 * r1} gives {area2}cm².",
                "mistakes": [(f"{area1 * r2 // r1}cm²", f"Area doesn't grow by the length ratio ({r1}:{r2}) directly but by the 'squared' ratio.")],
                "detail": "In similar figures, if length is k times, area is k² times and volume is k³ times (one factor per dimension). If a map's scale doubles, area becomes 4 times; if a doll is 3 times bigger, its weight (volume) is 27 times. This 'square and cube of dimensions' is a spot people often get confused about in real life.",
            },
        )


# ── 128. 격자 대각선이 지나는 칸 = m+n−gcd (난7, 도형과측정) ─────────────────
def gen_diagonal_cells():
    for m, n in [(6, 4), (5, 3), (8, 6), (4, 2)]:
        ans = m + n - gcd(m, n)
        # 검산: 대각선의 매개변수 t 구간을 정수 산술(공통분모 m·n)로 비교해
        # 지나는 칸을 완전열거 — 칸 (i,j)를 지남 ⇔ 열린 구간 (i·n,(i+1)·n)∩(j·m,(j+1)·m) ≠ ∅
        cell_cnt = sum(
            1 for i in range(m) for j in range(n)
            if max(i * n, j * m) < min((i + 1) * n, (j + 1) * m)
        )
        assert cell_cnt == ans, f"diagcells 검산실패: {m}x{n}"
        add(
            "diagcells", "SHAPE_MEASUREMENT", 7, ["격자", "최대공약수"],
            f"가로 {m}칸, 세로 {n}칸인 직사각형 모눈이 있어요. 한 꼭짓점에서 대각선 반대편 꼭짓점까지 곧게 선을 그으면, 이 선이 지나가는 모눈 칸은 모두 몇 칸일까요?",
            f"{ans}칸", [f"{m + n}칸", f"{m * n}칸", f"{ans - 1}칸"],
            f"대각선이 지나는 칸 수엔 공식이 있어요: 가로 + 세로 − (가로와 세로의 최대공약수) = {m}+{n}−{gcd(m, n)}={ans}칸. 최대공약수를 빼는 건, 대각선이 격자의 '점'을 지날 때 두 칸을 한 번에 건너뛰기 때문이에요.",
            [(f"{m + n}칸", f"대각선이 격자 점을 지나며 칸을 건너뛰어요 — 최대공약수({gcd(m, n)})만큼 빼야 해요.")],
            figure={"type": "GRID", "params": {"w": m, "h": n, "diag": 1}},
            detail="m×n 격자의 대각선이 지나는 칸 수 = m + n − gcd(m,n)이에요. 대각선은 세로선을 넘고 가로선을 넘으며 칸을 하나씩 늘리는데, 격자 점(두 선이 겹치는 곳)을 지날 땐 한꺼번에 넘어 한 칸만 늘어요. 그 겹치는 횟수 때문에 gcd를 빼요.",
            en={
                "statement": f"There is a rectangular grid {m} cells wide and {n} cells tall. If you draw a straight line from one corner to the opposite corner, how many grid cells does the line pass through in all?",
                "answer": _en_plural(ans, "cell"),
                "distractors": [_en_plural(m + n, "cell"), _en_plural(m * n, "cell"), _en_plural(ans - 1, "cell")],
                "explanation": f"There's a formula for the number of cells a diagonal passes through: width + height − (gcd of width and height) = {m}+{n}−{gcd(m, n)}={ans}. You subtract the gcd because when the diagonal passes through a grid 'point' it skips into two cells at once.",
                "mistakes": [(_en_plural(m + n, "cell"), f"The diagonal passes through grid points and skips cells — you have to subtract the gcd ({gcd(m, n)}).")],
                "detail": "The number of cells a diagonal of an m×n grid passes through = m + n − gcd(m,n). The diagonal adds one cell each time it crosses a vertical or a horizontal line, but when it passes through a grid point (where two lines meet) it crosses both at once and adds only one cell. Because of those overlaps you subtract the gcd.",
            },
        )


# ── 113. 최소공배수 — 정사각형 만들기 (난5, 도형과측정) ─────────────────────
def gen_lcm_square():
    for w, h in [(6, 4), (8, 12), (9, 6), (10, 15)]:
        lcm = w * h // gcd(w, h)
        # 검산: 1부터 차례로 훑어 두 변 모두로 나누어떨어지는 가장 작은 수를 직접 찾아 대조
        smallest = next(s for s in range(1, w * h + 1) if s % w == 0 and s % h == 0)
        assert smallest == lcm, f"lcmsquare 검산실패: {w}x{h}"
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
            en={
                "statement": "What is the area of the shaded shape, in cm²? (each grid square is 1 cm²)",
                "answer": f"{area}cm²",
                "distractors": [f"{area + 2}cm²", f"{area - 2}cm²", f"{area + 4}cm²"],
                "explanation": f"For a slanted shape, draw the 'tightest surrounding square' and then subtract the right triangles left outside — that's exact. Subtracting the four corner triangles (each base×height÷2) from the surrounding square gives {area}cm². (Since it joins grid points, you can also use 'Pick's theorem' from the deeper note below.)",
                "mistakes": [(f"{area + 2}cm²", "Don't roughly count the cells along a slanted edge — precisely subtract the corner right triangles from the surrounding square.")],
                "detail": "The area of a slanted shape is found exactly by 'surrounding rectangle − corner right triangles'. For a shape that joins grid points, 'Pick's theorem' is powerful: area = (interior grid points) + (boundary grid points)÷2 − 1. Just counting points gives the area. Finding it both ways and checking that the answers match leaves no room for mistakes.",
            },
        )


# ── 137. 격자 속 정사각형 개수 = 제곱수의 합 (난6, 도형과측정) ───────────────
def gen_squares_in_grid():
    for k in [2, 3, 4, 5]:
        ans = k * (k + 1) * (2 * k + 1) // 6
        # 검산: 크기 s×s 정사각형이 놓일 왼쪽 위 자리를 전부 나열해 세는 완전열거와 대조
        sq_cnt = sum(1 for s in range(1, k + 1) for x in range(k - s + 1) for y in range(k - s + 1))
        assert sq_cnt == ans, f"gridsquares 검산실패: k={k}"
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


def gen_painted_cube_faces():
    # 겉면을 칠한 n×n×n 정육면체를 단위정육면체로 자를 때, 정확히 두 면만 칠해진 개수 = 모서리 12개 × (n-2). (도형과측정 난8)
    from itertools import product

    for n in [4, 5, 3, 6]:
        two = 12 * (n - 2)
        three = 8               # 꼭짓점(세 면)
        one = 6 * (n - 2) ** 2  # 면 안쪽(한 면)
        # 검산: n³개 좌표를 전부 돌며 극단 좌표(0, n−1) 개수 = 칠해진 면 수로 직접 분류
        by_faces = {kk: 0 for kk in range(4)}
        for x, y, z in product(range(n), repeat=3):
            by_faces[sum(1 for v in (x, y, z) if v in (0, n - 1))] += 1
        assert by_faces[2] == two and by_faces[3] == three and by_faces[1] == one, f"paintcube 검산실패: n={n}"
        assert sum(by_faces.values()) == n ** 3, f"paintcube 검산실패(전체 조각 수): n={n}"
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
            en={
                "statement": f"A {n}×{n}×{n} cube with its whole surface painted red is cut into {n ** 3} small 1×1×1 cubes. "
                f"How many small cubes have exactly 'two faces' red?",
                "answer": _en_plural(two, "cube"),
                "distractors": [_en_plural(int(c), "cube") for c in _pick_distractors(two, [three, (n - 2) ** 3, one, two + 12, two - 12 if two > 12 else two + 6])],
                "explanation": f"The number of painted faces on a small cube is set by its 'position'. Three faces = the 8 corners, two faces = the edges (minus the corners), one face = the inside of each face. "
                f"Two faces means {n - 2} per edge after removing the corners, across 12 edges, so 12×{n - 2}={two} cubes.",
                "mistakes": [(_en_plural(three, "cube"), "The ones painted on three faces are the 8 corners. For 'two faces', count along the edges (excluding corners)."),
                             (_en_plural((n - 2) ** 3, "cube"), "That's the number of completely unpainted (interior) cubes. The two-face ones lie along the edges.")],
                "detail": "When you cut a cube, each small cube's number of painted faces is set by its position — corner = three faces (fixed 8), on an edge = two faces, "
                "inside a face = one face, fully interior = 0 faces. 'Two faces' is (n−2) per edge after removing the two end corners, across 12 edges, so 12(n−2). It's a spatial-reasoning problem of counting by position.",
            },
        )


def gen_rectdiag():
    # 직사각형 대각선 = √(가로²+세로²). 피타고라스 입문(정수 결과). (도형과측정 난4)
    for a, b in [(3, 4), (6, 8), (5, 12), (8, 15)]:
        sq = a * a + b * b
        ans = int(sq ** 0.5)
        # 검산: int(√)의 절단 오류 방지 — 제곱 복원 + 삼각부등식으로 빗변 범위 확인
        assert ans * ans == sq, f"rectdiag 검산실패: {a}x{b}는 완전제곱 빗변이 아님"
        assert max(a, b) < ans < a + b, f"rectdiag 검산실패(삼각부등식): {a}x{b}"
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


def gen_foldcut():
    # 종이를 반으로 접고 구멍을 뚫으면, 펼쳤을 때 구멍 = 구멍 수 × 2^(접은 횟수). 대칭 사고. (도형과측정 난1)
    for folds, h in [(1, 1), (1, 2), (1, 3), (2, 1)]:
        layers = 2 ** folds
        ans = h * layers
        # 검산: 띠를 2^folds 조각으로 보고 반 접기를 실제로 시뮬레이션 —
        # 겹친 채 뚫으면 서로 다른 조각(위치)에 겹친 장수만큼 구멍이 나야 한다
        strip = [[i] for i in range(2 ** folds)]
        for _ in range(folds):
            strip = [strip[i] + strip[len(strip) - 1 - i][::-1] for i in range(len(strip) // 2)]
        assert len(strip) == 1 and len(set(strip[0])) == len(strip[0]), f"foldcut 검산실패: folds={folds}"
        assert h * len(strip[0]) == ans, f"foldcut 검산실패: folds={folds}, h={h}"
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


def gen_euler():
    # 오일러 공식으로 모서리 역산: 꼭짓점−모서리+면=2 → 모서리 = 꼭짓점+면−2. (도형과측정 난5)
    # 난이도 재조정(난9→5, 2026-07 d9 감사): V·F를 주고 공식 대입 뺄셈 1회 — pick(d5) 동류.
    for v, f in [(12, 20), (8, 6), (6, 8), (20, 12)]:
        ans = v + f - 2
        # 검산: (V,F)에 해당하는 실제 정다면체 구조(한 면의 변 수·꼭짓점 차수)로
        # 모서리를 면 쪽(F×변÷2)·꼭짓점 쪽(V×차수÷2) 두 경로에서 독립 재계산
        solids = {(12, 20): (3, 5), (8, 6): (4, 3), (6, 8): (3, 4), (20, 12): (5, 3)}
        assert (v, f) in solids, f"euler 검산실패: ({v},{f}) 다면체 구조 미등록"
        face_sides, vert_deg = solids[(v, f)]
        assert f * face_sides // 2 == ans and v * vert_deg // 2 == ans, f"euler 검산실패: V={v}, F={f}"
        add(
            "euler", "SHAPE_MEASUREMENT", 5, ["오일러 공식", "다면체"],
            f"어떤 볼록 다면체의 꼭짓점이 {v}개, 면이 {f}개예요. 이 다면체의 모서리는 모두 몇 개일까요?",
            f"{ans}개", [f"{c}개" for c in _pick_distractors(ans, [v + f, v * f // 4, ans + 2, ans - 2])],
            f"볼록 다면체는 항상 '꼭짓점 − 모서리 + 면 = 2'(오일러 공식)를 만족해요. 모서리로 정리하면 "
            f"모서리 = 꼭짓점 + 면 − 2 = {v} + {f} − 2 = {ans}개예요.",
            [(f"{v + f}개", "−2를 빼먹었어요. 오일러 공식은 꼭짓점+면−2가 모서리예요.")],
            detail="볼록 다면체에서는 꼭짓점(V)−모서리(E)+면(F)=2가 항상 성립해요(오일러 공식). 셋 중 둘을 알면 나머지를 "
            "바로 구할 수 있어요. 공간 도형을 잇는 아름다운 규칙이에요.",
            en={
                "statement": f"A convex polyhedron has {v} vertices and {f} faces. How many edges does this polyhedron have in all?",
                "answer": f"{ans} edges",
                "distractors": [f"{c} edges" for c in _pick_distractors(ans, [v + f, v * f // 4, ans + 2, ans - 2])],
                "explanation": f"A convex polyhedron always satisfies 'vertices − edges + faces = 2' (Euler's formula). Rearranging for edges: "
                f"edges = vertices + faces − 2 = {v} + {f} − 2 = {ans}.",
                "mistakes": [(f"{v + f} edges", "You forgot to subtract 2. Euler's formula gives edges = vertices + faces − 2.")],
                "detail": "In a convex polyhedron, vertices (V) − edges (E) + faces (F) = 2 always holds (Euler's formula). Knowing two of the three gives the last one right away. A beautiful rule tying solid figures together.",
            },
        )


def gen_conevolume():
    # 뿔의 부피 = 밑넓이 × 높이 ÷ 3 (같은 밑면·높이 기둥의 1/3). (도형과측정 난3)
    # 난이도 재조정(난10→3, 2026-07 d10 감사): 공식을 문제에 명시하고 곱1·나눗1만 하는
    # 적용형 — '스스로 발견'이 없어 경시급 부적격.
    for base, h in [(12, 5), (9, 4), (18, 7), (6, 10)]:
        ans = base * h // 3
        # 검산: ÷3이 정확히 떨어지는 파라미터인지(절단 오류 방지) 곱으로 복원해 확인
        assert (base * h) % 3 == 0 and ans * 3 == base * h and ans > 0, f"conevolume 검산실패: base={base}, h={h}"
        add(
            "conevolume", "SHAPE_MEASUREMENT", 3, ["뿔의 부피", "기둥의 3분의 1"],
            f"밑면의 넓이가 {base}cm², 높이가 {h}cm인 뿔(각뿔·원뿔)의 부피는 몇 cm³일까요?",
            f"{ans}cm³", [f"{c}cm³" for c in _pick_distractors(ans, [base * h, base * h // 2, ans + 2, ans - 2])],
            f"뿔의 부피는 밑면과 높이가 같은 기둥의 딱 3분의 1이에요. 밑넓이 × 높이 ÷ 3 = {base} × {h} ÷ 3 = {ans}cm³예요.",
            [(f"{base * h}cm³", "그건 같은 밑면·높이 '기둥'의 부피예요. 뿔은 그 3분의 1이라 ÷3 해요.")],
            detail="같은 밑넓이·높이라면 뿔의 부피는 기둥의 정확히 1/3이에요. 그래서 (밑넓이×높이)÷3으로 구해요. "
            "물을 부어 옮기면 세 번에 꽉 차는 걸로도 확인되는 입체 측정의 핵심이에요.",
            en={
                "statement": f"A cone or pyramid has a base area of {base} cm² and a height of {h} cm. What is its volume, in cm³?",
                "answer": f"{ans}cm³",
                "distractors": [f"{c}cm³" for c in _pick_distractors(ans, [base * h, base * h // 2, ans + 2, ans - 2])],
                "explanation": f"A cone or pyramid's volume is exactly one third of the prism with the same base and height. Base area × height ÷ 3 = {base} × {h} ÷ 3 = {ans}cm³.",
                "mistakes": [(f"{base * h}cm³", "That's the volume of the 'prism' with the same base and height. A cone/pyramid is one third of it, so ÷3.")],
                "detail": "For the same base area and height, a cone/pyramid's volume is exactly 1/3 of the prism's. So you find it with (base area × height)÷3. It's a key fact of solid measurement — pouring water shows it fills up in exactly three pours.",
            },
        )


def gen_diagregions():
    # 볼록 n각형의 대각선이 내부를 나누는 조각(영역) 수 = 1 + 대각선수 + 교점수. (도형과측정 난10)
    for n in [6, 7, 5, 8]:
        diag = n * (n - 3) // 2
        cross = comb(n, 4)
        ans = 1 + diag + cross
        # 검산: 일반 위치 볼록 n각형(포물선 위 점)에서 분수 연산 선분 교차로
        # 교점·영역 수를 실제 재산출 — 공식이 아닌 진짜 기하 계산과 대조
        real_cross, real_regions = _convex_diag_geometry(n)
        assert real_cross == cross, f"diagregions 검산실패(교점): n={n}"
        assert real_regions == ans, f"diagregions 검산실패(영역): n={n}"
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
            en={
                "statement": f"All the diagonals of a convex {n}-gon are drawn. If no three diagonals meet at a single interior point, into how many pieces (regions) do the diagonals divide the interior of the polygon?",
                "answer": f"{ans} regions",
                "distractors": [f"{c} regions" for c in _pick_distractors(ans, [cross, diag, ans - 1, ans + 2])],
                "explanation": f"You start with 1 piece (the polygon). Each time you draw a diagonal, the number of pieces grows by 'the number of crossing points it passes + 1'. Adding it all up: 1 + ({diag} diagonals) + ({cross} crossing points) = {ans} regions.",
                "mistakes": [(f"{cross} regions", "That's the number of 'crossing points' where diagonals meet. The number of pieces is 1 + diagonals + crossing points."),
                             (f"{diag} regions", "That's the 'number' of diagonals. There are more pieces than that (they split apart at the crossing points).")],
                "detail": "The number of pieces the diagonals make is counted with Euler's formula (vertices − edges + faces = 2) — vertices = the original n plus C(n,4) crossing points, and edges = the number of pieces each diagonal and side is cut into at the crossings. Simplified, the number of pieces = 1 + n(n−3)/2 + C(n,4). It's one step beyond counting crossing points (C(n,4)).",
            },
        )


def gen_dist3d():
    # 공간에서 원점부터 (x,y,z)까지 거리 = √(x²+y²+z²). (도형과측정 난4)
    # 난이도 재조정(난8→4, 2026-07 d8 감사): 공식 대입 1회(완전제곱 설계) — conevolume 동류.
    # ⚠️ 피타고라스(초등 범위 밖 정리) 의존 — rectdiag 제거 선례와 같은 원칙 위반 소지,
    # 블록리스트 후보로 사용자 결정 대기.
    for x, y, z in [(2, 3, 6), (1, 2, 2), (2, 6, 9), (6, 6, 7)]:
        sq = x * x + y * y + z * z
        ans = int(sq ** 0.5)
        # 검산: int(√)의 절단 오류 방지 — 제곱 복원 + 최대 좌표와 좌표 합 사이 범위 확인
        assert ans * ans == sq, f"dist3d 검산실패: ({x},{y},{z})는 완전제곱 거리가 아님"
        assert max(x, y, z) < ans < x + y + z, f"dist3d 검산실패(범위): ({x},{y},{z})"
        add(
            "dist3d", "SHAPE_MEASUREMENT", 4, ["공간 좌표", "피타고라스"],
            f"공간에서 점 (0, 0, 0)부터 점 ({x}, {y}, {z})까지의 거리는 얼마일까요?",
            str(ans), [str(c) for c in _pick_distractors(ans, [x + y + z, ans + 1, ans - 1, x + y])],
            f"공간에서 거리는 √(가로²+세로²+높이²)로 구해요(피타고라스의 공간판). "
            f"√({x}²+{y}²+{z}²) = √{sq} = {ans}예요.",
            [(str(x + y + z), "좌표를 그냥 더하면 안 돼요. 각각 제곱해 더한 뒤 제곱근을 씌워요.")],
            detail="평면의 거리 √(x²+y²)를 공간으로 넓히면 √(x²+y²+z²)예요. 직육면체의 대각선을 두 번의 피타고라스로 구하는 것과 "
            "같아요. 좌표와 길이를 잇는 공간 측정의 핵심이에요.",
            en={
                "statement": f"In space, what is the distance from the point (0, 0, 0) to the point ({x}, {y}, {z})?",
                "answer": str(ans),
                "distractors": [str(c) for c in _pick_distractors(ans, [x + y + z, ans + 1, ans - 1, x + y])],
                "explanation": f"In space, distance is found by √(width²+depth²+height²) (the spatial version of Pythagoras). "
                f"√({x}²+{y}²+{z}²) = √{sq} = {ans}.",
                "mistakes": [(str(x + y + z), "You can't just add the coordinates. Square each, add them, then take the square root.")],
                "detail": "Extending the planar distance √(x²+y²) into space gives √(x²+y²+z²). It's the same as finding a rectangular box's diagonal with two applications of Pythagoras. "
                "It's the heart of spatial measurement, linking coordinates and length.",
            },
        )


def gen_boxsurface():
    # 직육면체 겉넓이 = 2(ab+bc+ca). (도형과측정 난6)
    from itertools import product

    for a, b, c in [(3, 4, 5), (2, 3, 4), (5, 5, 2), (1, 4, 6)]:
        ans = 2 * (a * b + b * c + c * a)
        # 검산: 단위정육면체 좌표를 전부 돌며 바깥에 노출된 면을 직접 세는 열거와 대조
        exposed = sum(
            1
            for x, y, z in product(range(a), range(b), range(c))
            for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
            if not (0 <= x + dx < a and 0 <= y + dy < b and 0 <= z + dz < c)
        )
        assert exposed == ans, f"boxsurface 검산실패: {a}x{b}x{c}"
        add(
            # 난이도 재조정(6→4, 2026-07 d6 감사): 2(ab+bc+ca) 공식 적용.
            "boxsurface", "SHAPE_MEASUREMENT", 4, ["겉넓이", "면 세기"],
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


def gen_symaxis():
    # 정n각형의 대칭축 개수 = n. (도형과측정 난3)
    for n in [3, 4, 5, 6]:
        ans = n
        name = {3: "정삼각형", 4: "정사각형", 5: "정오각형", 6: "정육각형"}[n]
        # 검산: 원 위 정n각형(꼭짓점 위치 2k, 단위 π/n)의 후보 반사축 2n개를 전부 돌며
        # 반사 p→(ax−p)가 꼭짓점 집합을 보존하는 축만 실제로 세는 완전열거와 대조
        vset = {(2 * k) % (2 * n) for k in range(n)}
        axis_cnt = sum(1 for ax in range(2 * n) if all((ax - p) % (2 * n) in vset for p in vset))
        assert axis_cnt == ans, f"symaxis 검산실패: n={n}"
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
        # 검산: 네 꼭짓점 좌표를 실제로 한 바퀴 걸으며 변 길이를 더하는 경로 합과 대조
        corners = [(0, 0), (a, 0), (a, b), (0, b)]
        walk = sum(abs(x2 - x1) + abs(y2 - y1) for (x1, y1), (x2, y2) in zip(corners, corners[1:] + corners[:1]))
        assert walk == ans, f"rectperim 검산실패: {a}x{b}"
        add(
            # 난이도 재조정(4→2, 2026-07 d1~5 스캔): (가로+세로)×2 공식 1단계 — sqarea(d3)보다
            # 쉬운데 위에 있던 역전 해소.
            "rectperim", "SHAPE_MEASUREMENT", 2, ["둘레", "측정"],
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
        # 검산: 외각 경로(한 내각 = 180 − 360/n)로 독립 재계산 + 나눗셈 정확성 확인
        assert total % n == 0 and 360 % n == 0, f"interiorangle 검산실패: n={n} 각도가 정수가 아님"
        assert ans == 180 - 360 // n, f"interiorangle 검산실패: n={n}"
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
        # 검산: 꼭짓점 (i, 층)으로 각기둥 그래프를 실제로 만들어 모서리를 집합으로 세고,
        # V−E+F=2(오일러 공식)로 교차 확인
        edge_set = {frozenset(((i, lv), ((i + 1) % n, lv))) for lv in (0, 1) for i in range(n)}
        edge_set |= {frozenset(((i, 0), (i, 1))) for i in range(n)}
        assert len(edge_set) == ans, f"prismparts 검산실패: n={n}"
        assert 2 * n - len(edge_set) + (n + 2) == 2, f"prismparts 검산실패(오일러): n={n}"
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
    import math

    for a, b in [(50, 70), (40, 65), (90, 35), (72, 53)]:
        ans = 180 - a - b
        # 검산: 밑변 (0,0)-(1,0) 위에 각 a·b로 두 반직선을 실제로 작도해 교점 C를 구하고,
        # C에서 잰 각이 답과 일치하는지 좌표 기하로 독립 확인
        assert 0 < ans < 180, f"triangleangle 검산실패: {a}도+{b}도로는 삼각형 불가"
        ra, rb = math.radians(a), math.radians(b)
        da, db = (math.cos(ra), math.sin(ra)), (-math.cos(rb), math.sin(rb))
        t = db[1] / (da[0] * db[1] - da[1] * db[0])
        cx, cy = t * da[0], t * da[1]
        va, vb = (-cx, -cy), (1 - cx, -cy)
        cosc = (va[0] * vb[0] + va[1] * vb[1]) / (math.hypot(*va) * math.hypot(*vb))
        measured = math.degrees(math.acos(max(-1.0, min(1.0, cosc))))
        assert abs(measured - ans) < 1e-6, f"triangleangle 검산실패: {a}도·{b}도"
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


def gen_spacediag():
    # 직육면체 대각선이 지나는 단위정육면체 수 = a+b+c − gcd쌍합 + gcd(a,b,c) (포함배제, 3차원). (도형과측정 난9)
    for a, b, c in [(2, 3, 4), (3, 4, 5), (2, 4, 6), (4, 6, 8)]:
        ans = a + b + c - gcd(a, b) - gcd(b, c) - gcd(c, a) + gcd(gcd(a, b), c)
        naive = a + b + c
        # 검산: 단위정육면체 (i,j,k)를 전부 돌며 대각선의 t 구간(공통분모 abc 정수 산술)이
        # 그 칸 내부를 실제로 지나는지 완전열거로 대조 — 포함배제 공식과 독립인 경로
        pass_cnt = sum(
            1
            for i in range(a) for j in range(b) for k in range(c)
            if max(i * b * c, j * a * c, k * a * b) < min((i + 1) * b * c, (j + 1) * a * c, (k + 1) * a * b)
        )
        assert pass_cnt == ans, f"spacediag 검산실패: {a}x{b}x{c}"
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
            en={
                "statement": f"You stack {a * b * c} small cubes into a rectangular box, {a} wide, {b} deep, and {c} tall, with no gaps. "
                f"If you draw the diagonal that runs through the inside from one corner to the farthest opposite corner, how many small cubes does this diagonal pass through?",
                "answer": f"{ans} small cubes",
                "distractors": [f"{c2} small cubes" for c2 in _pick_distractors(ans, [naive, ans + 1, ans - 1, naive - 1])],
                "explanation": f"The diagonal enters a new cube each time it crosses a partition in the width, depth, or height direction. There are {a}+{b}+{c}={naive} crossings, "
                f"but an edge where two partitions are crossed 'at once' (as many as their gcd) must be counted only once, and a corner where three are crossed at once is added back. "
                f"{naive} − ({gcd(a, b)}+{gcd(b, c)}+{gcd(c, a)}) + {gcd(gcd(a, b), c)} = {ans}.",
                "mistakes": [(f"{naive} small cubes", "You can't just add width+depth+height. You must subtract and add back the places where crossings overlap at edges and corners (inclusion-exclusion)."),
                             (f"{ans - 1} small cubes", "Count the very first cube too. It's easy to confuse the number of partitions crossed with the number of cubes passed through.")],
                "detail": "The number of unit cubes a diagonal passes through is counted by 3D inclusion-exclusion — from the crossings in all three directions (a+b+c), subtract the edges where two directions are crossed at once (gcd(a,b), etc.), then add back the corners where all three are crossed at once (gcd(a,b,c)). A beautiful number-and-geometry problem extending the 2D case (a+b−gcd) into space.",
            },
        )


def gen_polyhedron():
    # 정다면체의 모서리 수 = (면 수 × 한 면의 변 수) ÷ 2 (모서리는 두 면이 공유). 오일러 공식으로 꼭짓점도. (도형과측정 난8)
    for name, faces, sides in [("정십이면체", 12, 5), ("정이십면체", 20, 3), ("정팔면체", 8, 3), ("정사면체", 4, 3)]:
        edges = faces * sides // 2
        verts = edges - faces + 2
        # 검산: 실제 정다면체의 꼭짓점 수·꼭짓점 차수로 모서리·꼭짓점을 독립 재계산
        # (모서리 = V×차수÷2 — 면 쪽 세기와 다른 경로)
        vdata = {"정십이면체": (20, 3), "정이십면체": (12, 5), "정팔면체": (6, 4), "정사면체": (4, 3)}
        assert name in vdata, f"polyhedron 검산실패: {name} 구조 미등록"
        vk, dk = vdata[name]
        assert (faces * sides) % 2 == 0, f"polyhedron 검산실패: {name} 변 총수가 홀수"
        assert edges == vk * dk // 2 and verts == vk, f"polyhedron 검산실패: {name}"
        name_en = {"정십이면체": "regular dodecahedron", "정이십면체": "regular icosahedron", "정팔면체": "regular octahedron", "정사면체": "regular tetrahedron"}[name]
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
            en={
                "statement": f"There is a convex polyhedron ({name_en}) with {faces} faces, each face a regular {sides}-gon. How many edges does this polyhedron have in all?",
                "answer": f"{edges} edges",
                "distractors": [f"{c} edges" for c in _pick_distractors(edges, [faces * sides, faces + sides, edges + 2, verts])],
                "explanation": f"Each face has {sides} sides, so counting all the sides gives {faces}×{sides}={faces * sides}. But each edge is shared by two neighboring faces, "
                f"so it was counted exactly twice. Dividing by 2, {faces * sides}÷2={edges} edges. "
                f"(Checking with Euler's formula vertices−edges+faces=2, there are {verts} vertices.)",
                "mistakes": [(f"{faces * sides} edges", f"Counting the sides, {faces}×{sides} counts each edge 'twice'. You must divide by 2."),
                             (f"{verts} edges", "That's the number of vertices. Edges are (faces×sides)÷2.")],
                "detail": "A polyhedron's number of edges is (number of faces × sides per face)÷2 — because each edge is shared by two neighboring faces and thus counted twice. "
                "Vertices are found by Euler's formula (vertices−edges+faces=2). It's a classic solid-geometry problem linking 'over-count and divide' with Euler's formula.",
            },
        )


def gen_pick():
    # 픽의 정리: 격자 다각형 넓이 = 내부 격자점 + 둘레 격자점÷2 − 1. (도형과측정 난5)
    # 난이도 재조정(난10→5, 2026-07 d10 감사): I·B를 문제가 주고 공식 한 줄 대입 —
    # recur(적용형, d5)와 동일 계급. 점 세기부터 시키는 발견형으로 개편하면 승급 여지.
    # 검산 증인: (내부, 둘레) 격자점 수를 실제로 실현하는 격자 삼각형 — 점을 직접 세어 확인
    witness = {(4, 6): ((0, 0), (4, 2), (2, 4)), (5, 8): ((0, 0), (4, 0), (2, 4)),
               (0, 4): ((0, 0), (2, 0), (1, 1)), (6, 10): ((0, 0), (5, 0), (0, 4))}
    for inner, boundary in [(4, 6), (5, 8), (0, 4), (6, 10)]:
        ans = inner + boundary // 2 - 1
        # 검산: 증인 삼각형의 내부/둘레 격자점을 좌표 순회로 직접 세고,
        # 신발끈 넓이가 공식 값과 일치하는지 독립 확인(픽의 정리 실증)
        assert boundary % 2 == 0, f"pick 검산실패: 둘레 점 수가 홀수({boundary})"
        assert (inner, boundary) in witness, f"pick 검산실패: ({inner},{boundary}) 증인 다각형 미등록"
        wi, wb, warea2 = _lattice_triangle_stats(witness[(inner, boundary)])
        assert (wi, wb) == (inner, boundary), f"pick 검산실패: 증인 격자점 ({wi},{wb})≠({inner},{boundary})"
        assert warea2 == 2 * ans, f"pick 검산실패: 증인 넓이 {warea2}/2 ≠ {ans}"
        add(
            "pick", "SHAPE_MEASUREMENT", 5, ["픽의 정리", "격자점으로 넓이"],
            f"모눈종이의 격자점을 꼭짓점으로 하는 다각형이 있어요. 다각형 '내부'에 있는 격자점이 {inner}개, "
            f"'둘레(변)' 위에 있는 격자점이 {boundary}개예요. 이 다각형의 넓이는 얼마일까요? (모눈 한 칸 넓이는 1)",
            str(ans), [str(c) for c in _pick_distractors(ans, [inner + boundary, inner + boundary // 2, ans + 1, ans + 2])],
            f"픽의 정리를 쓰면 넓이 = (내부 격자점) + (둘레 격자점)÷2 − 1 이에요. "
            f"= {inner} + {boundary}÷2 − 1 = {inner} + {boundary // 2} − 1 = {ans}예요.",
            [(str(inner + boundary), "내부와 둘레 점을 그냥 더하면 안 돼요. 둘레는 반만 세고 1을 빼는 게 픽의 정리예요."),
             (str(inner + boundary // 2), "마지막에 −1을 빼먹었어요. 넓이 = 내부 + 둘레÷2 − 1 이에요.")],
            detail="픽의 정리는 격자점 위 다각형의 넓이를 '내부 격자점 수 + 둘레 격자점 수÷2 − 1'로 구해요. 자로 재지 않고 점만 세어 넓이를 "
            "정확히 얻는 놀라운 정리로, 삼각형으로 쪼개 더해도 성립함을 보일 수 있어요. 측정과 세기를 잇는 기하의 보석이에요.",
            en={
                "statement": f"A polygon has its vertices on the lattice points of grid paper. There are {inner} lattice points 'inside' the polygon and "
                f"{boundary} lattice points on its 'boundary (edges)'. What is the area of this polygon? (each grid square has area 1)",
                "answer": str(ans),
                "distractors": [str(c) for c in _pick_distractors(ans, [inner + boundary, inner + boundary // 2, ans + 1, ans + 2])],
                "explanation": f"By Pick's theorem, area = (interior lattice points) + (boundary lattice points)÷2 − 1. "
                f"= {inner} + {boundary}÷2 − 1 = {inner} + {boundary // 2} − 1 = {ans}.",
                "mistakes": [(str(inner + boundary), "You can't just add the interior and boundary points. Pick's theorem counts the boundary as half and subtracts 1."),
                             (str(inner + boundary // 2), "You forgot to subtract 1 at the end. Area = interior + boundary÷2 − 1.")],
                "detail": "Pick's theorem finds the area of a polygon on lattice points as 'number of interior lattice points + number of boundary lattice points÷2 − 1'. "
                "It's a remarkable theorem that gives the exact area by just counting points without measuring, and it can be shown to hold by splitting into triangles and adding. It's a gem of geometry connecting measurement and counting.",
            },
        )


def gen_diagcross():
    # 볼록 n각형 대각선의 내부 교점 수 = C(n,4) (어느 세 대각선도 한 점에서 만나지 않을 때). (도형과측정 난9)
    for n in [6, 7, 8, 5]:
        ans = comb(n, 4)
        diags = n * (n - 3) // 2
        # 검산: 일반 위치 볼록 n각형(포물선 위 점)에서 대각선 쌍의 교점을 분수 연산
        # 선분 교차로 실제 전부 계산해 세는 완전열거와 대조 — C(n,4) 공식과 독립인 경로
        real_cross, _ = _convex_diag_geometry(n)
        assert real_cross == ans, f"diagcross 검산실패: n={n}"
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
            en={
                "statement": f"You draw all the diagonals of a convex {n}-gon. If no three diagonals meet at a single interior point, "
                f"how many interior intersection points do the diagonals make inside the polygon?",
                "answer": f"{ans} points",
                "distractors": [f"{c} points" for c in _pick_distractors(ans, [diags, comb(n, 3), comb(n, 2), ans + 2])],
                "explanation": f"Each interior intersection point is fixed by choosing exactly 4 vertices — it's where the two diagonals of the quadrilateral those four points form cross. "
                f"So the number of points is the number of ways to choose 4 of the {n} vertices, C({n},4) = {ans}.",
                "mistakes": [(f"{diags} points", "That's the number of diagonals. Count intersection points by choosing 4 vertices."),
                             (f"{comb(n, 3)} points", "Choosing 3 won't fix a point; you need 4 (the two diagonals of a quadrilateral).")],
                "detail": "In a convex polygon (when no three diagonals meet at one point) each interior intersection point corresponds one-to-one with a choice of 4 vertices — because those four points make a quadrilateral with exactly one crossing of its two diagonals. So the number of points = C(n,4). A classic problem of turning a geometric count into a combination.",
            },
        )


# ═══ 2026-07 천장 보충(CEILING_SPECS §3.6·3.7·3.B1) + 신규 슬롯 3(d7·d6·d5) ═══
# 전부 파일 끝 append — 기존 코드 무수정. 헬퍼는 순수 결정론 계산만, rng를 절대 소비하지 않는다.


def _tri_lattice_triangles(n):
    """변 n 삼각 격자의 격자선 정삼각형을 '꼭짓점 3개 조합 완전열거'로 센다(△, ▽ 분리).
    tricount 검산용 — 크기별 행 합산 공식과 완전히 독립인 경로. 격자 계량 d²=dc²−dc·dr+dr²(정수)로
    등변을 판정하고, 세 변이 모두 격자선 방향(dc=0·dr=0·dc=dr)인 것만 남긴다."""
    from itertools import combinations

    pts = [(r, c) for r in range(n + 1) for c in range(r + 1)]

    def d2(a, b):
        dr, dc = b[0] - a[0], b[1] - a[1]
        return dc * dc - dc * dr + dr * dr

    def grid_dir(a, b):
        dr, dc = b[0] - a[0], b[1] - a[1]
        return dc == 0 or dr == 0 or dc == dr

    up = down = 0
    for a, b, c in combinations(pts, 3):
        if not (d2(a, b) == d2(b, c) == d2(a, c) and grid_dir(a, b) and grid_dir(b, c) and grid_dir(a, c)):
            continue
        rows = sorted((a[0], b[0], c[0]))
        if rows[0] == rows[1]:      # 수평 변이 위 → 꼭짓점이 아래 = ▽
            down += 1
        else:                       # 수평 변이 아래 → 꼭짓점이 위 = △
            up += 1
    return up, down


def _billiard_bounces(p, q):
    """p×q 당구대 45° 반사 시뮬레이션 — 1스텝 1튕김을 hit 플래그로 보장(코너 도달 시 종료).
    billiard 검산용 — 약분 공식(p/g+q/g−2)과 독립인 걸음 단위 완전 시뮬레이션."""
    x = y = 0
    dx = dy = 1
    bounces = 0
    corners = {(0, 0), (p, 0), (0, q), (p, q)}
    for _ in range(4 * p * q + 10):
        x += dx
        y += dy
        if (x, y) in corners:
            return bounces, (x, y)
        hit = False
        if x in (0, p):
            dx = -dx
            hit = True
        if y in (0, q):
            dy = -dy
            hit = True
        if hit:
            bounces += 1
    raise AssertionError(f"billiard 시뮬 발산: {p}x{q}")


def _lattice_polygon_stats(pts):
    """단순 격자 다각형의 (넓이×2, 내부 격자점, 둘레 격자점)을 좌표 완전열거로 직접 센다.
    pickfig 검산용 — 단순성(비자기교차) 확인 + 신발끈 + 반직선 내부판정 + gcd 둘레점의
    네 경로를 상호 대조하고, 픽의 정리(A2=2I+B−2)로 삼중 검산한다."""
    from fractions import Fraction

    n = len(pts)
    assert len(set(pts)) == n, "꼭짓점 중복"
    es = list(zip(pts, pts[1:] + pts[:1]))
    for i in range(n):
        for j in range(i + 1, n):
            if j == (i + 1) % n or i == (j + 1) % n:
                continue  # 이웃 변은 꼭짓점만 공유
            assert _seg_intersection(*es[i], *es[j]) is None, f"변 교차: {i},{j}"
    area2 = abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in es))
    b_gcd = sum(gcd(abs(x2 - x1), abs(y2 - y1)) for (x1, y1), (x2, y2) in es)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    inner = b_enum = 0
    for px in range(min(xs), max(xs) + 1):
        for py in range(min(ys), max(ys) + 1):
            on_edge = any(
                (x2 - x1) * (py - y1) == (y2 - y1) * (px - x1)
                and min(x1, x2) <= px <= max(x1, x2) and min(y1, y2) <= py <= max(y1, y2)
                for (x1, y1), (x2, y2) in es
            )
            if on_edge:
                b_enum += 1
                continue
            crossings = 0
            for (x1, y1), (x2, y2) in es:
                if (y1 > py) != (y2 > py):
                    xint = Fraction(x1) + Fraction(py - y1, y2 - y1) * (x2 - x1)
                    if px < xint:
                        crossings += 1
            inner += crossings % 2
    assert b_enum == b_gcd, f"둘레점 두 경로 불일치: {b_enum}≠{b_gcd}"
    assert area2 == 2 * inner + b_gcd - 2, f"픽 검산 실패: A2={area2} I={inner} B={b_gcd}"
    return area2, inner, b_gcd


def _views_max_cubes(front, side):
    """앞(열별)·옆(줄별) 실루엣이 정확히 일치하는 모든 쌓기 배치를 완전열거해 최대 개수를 찾는다.
    cubeviews 검산용 — 칸별 min(앞,옆) 규칙과 독립인 전수조사(배치 존재성도 함께 확인)."""
    from itertools import product

    w, d = len(front), len(side)
    max_h = max(max(front), max(side))
    best, feasible = -1, 0
    for hs in product(range(max_h + 1), repeat=w * d):
        grid = [hs[r * w:(r + 1) * w] for r in range(d)]
        if all(max(grid[r][c] for r in range(d)) == front[c] for c in range(w)) and \
           all(max(grid[r]) == side[r] for r in range(d)):
            feasible += 1
            best = max(best, sum(hs))
    assert feasible > 0, f"cubeviews 실현 불가능한 실루엣: {front}/{side}"
    return best


def _stair_polygon(heights):
    """계단 폴리오미노(열 높이 비증가)의 꼭짓점 목록(화면좌표 y-아래)을 만든다. 그림·검산 공용."""
    w, h = len(heights), max(heights)
    pts = []
    x = 0
    while x < w:
        run_h = heights[x]
        x2 = x
        while x2 < w and heights[x2] == run_h:
            x2 += 1
        pts += [(x, h - run_h), (x2, h - run_h)]
        x = x2
    pts += [(w, h), (0, h)]
    return pts


def _stair_cell_stats(heights):
    """계단 폴리오미노의 (둘레, 넓이)를 셀 단위 완전열거로 직접 센다 — 이웃 없는 변만 둘레.
    stairperim 검산용 — 2(W+H) 통찰·다각형 좌표와 완전히 독립인 경로."""
    w, h = len(heights), max(heights)
    cells = {(x, y) for x in range(w) for y in range(h - heights[x], h)}
    perim = sum(
        1
        for (x, y) in cells
        for nb in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
        if nb not in cells
    )
    return perim, len(cells)


def _fold_cut_pieces(folds, cuts):
    """테이프를 반으로 folds번 접고 cuts번 자르는 과정을 겹 단위로 실제 시뮬레이션한다.
    foldpieces 검산용 — 각 겹의 (원좌표 원점, 방향)을 추적해 펼친 테이프의 잘린 점을 전부
    모아 '서로 다른 점 수 + 1'로 조각을 센다. c·2^k+1 규칙과 독립인 경로(정수 산술)."""
    total = (2 ** folds) * (cuts + 1)
    layers = [(0, 1)]                  # (원좌표 원점 o, 방향 d): 접힌 위치 p → 원좌표 o + d·p
    ell = total
    for _ in range(folds):
        layers = [(o, d) for o, d in layers] + [(o + d * ell, -d) for o, d in layers]
        ell //= 2
    assert len(layers) == 2 ** folds
    points = set()
    for t in range(1, cuts + 1):       # 접힌 길이 ell = cuts+1 → t=1..cuts는 내부·서로 다른 위치
        for o, d in layers:
            pt = o + d * t
            assert 0 < pt < total, "잘린 점이 테이프 밖"
            points.add(pt)
    return len(points) + 1


# ── 141. 삼각 격자의 정삼각형 총수 (난10, 도형과측정) — CEILING_SPECS §3.6 ─────────
# 발견형 자기검증: 방향(△/▽)×크기 이중 분류 전략이 문제문에 없고(기준1), n≥5는 그림 손 세기가
# 반드시 빠뜨리는 규모라 구조 발견이 필수다(기준2 — n=4가 진입 문항). 삼각 격자 렌더러가 없어
# 서술 출제(줄별 개수 명시로 보완) — TRI_GRID 렌더러 신설은 별도 슬라이스.
def gen_tricount():
    def tno(m):  # m번째 삼각수
        return m * (m + 1) // 2

    for n in [4, 5, 6, 7]:
        ups = [tno(n - k + 1) for k in range(1, n + 1)]            # △: 크기 1..n
        downs = [tno(n - 2 * k + 1) for k in range(1, n // 2 + 1)]  # ▽: 크기 k는 n≥2k일 때만
        up, down = sum(ups), sum(downs)
        ans = up + down
        # 검산: 격자점 3개 조합 완전열거(독립 경로) + 폐형식 ⌊n(n+2)(2n+1)/8⌋ 삼중 대조
        enum_up, enum_down = _tri_lattice_triangles(n)
        assert (enum_up, enum_down) == (up, down), f"tricount 검산실패: n={n} ({enum_up},{enum_down})≠({up},{down})"
        assert ans == n * (n + 2) * (2 * n + 1) // 8, f"tricount 검산실패(폐형식): n={n}"
        ups_str = "+".join(str(u) for u in ups)
        downs_str = "+".join(str(dv) for dv in downs)
        add(
            "tricount", "SHAPE_MEASUREMENT", 10, ["삼각형 세기", "방향 나눠 세기"],
            f"한 변의 길이가 {n}인 큰 정삼각형을, 한 변의 길이가 1인 작은 정삼각형 {n * n}개로 빈틈없이 나눴어요"
            f"(맨 윗줄부터 1개, 3개, 5개, …, {2 * n - 1}개 순서로 놓여요). 이 그림 속에서 찾을 수 있는 크고 작은 "
            f"정삼각형은 모두 몇 개일까요? (거꾸로 선 정삼각형도 빠짐없이 세요)",
            f"{ans}개", [f"{up}개", f"{n * n}개", f"{2 * up}개"],
            f"변 1·2·3짜리로 직접 실험하면 1개, 5개, 13개 — 바로 선 △와 거꾸로 선 ▽를 나눠 크기별로 세는 전략이 "
            f"보여요. △는 크기 1부터 {n}까지 {ups_str}={up}개. ▽는 크기 k짜리가 전체 변이 2k 이상일 때만 있어 "
            f"훨씬 빨리 줄어요: {downs_str}={down}개. 더하면 {up}+{down}={ans}개예요.",
            [(f"{up}개", "거꾸로 선(▽) 정삼각형을 빠뜨렸어요. 방향을 나눠 따로 세야 해요."),
             (f"{n * n}개", "크기 1짜리만 셌어요. 크기 2, 3, …의 큰 정삼각형도 숨어 있어요."),
             (f"{2 * up}개", "역방향(▽)이 정방향(△)과 개수가 같다고 가정했어요. 역방향은 크기가 커질수록 훨씬 빨리 줄어들어요(크기 k는 변이 2k 이상일 때만 존재).")],
            detail=f"▽의 꼭짓점은 아래로 향해 공간을 두 배로 잡아먹어요 — 크기 k짜리 ▽는 전체 변이 2k 이상이어야 "
            f"존재해서, 규칙이 △와 ▽ 두 갈래로 갈라지는 것이 이 문제의 심장이에요. n=2로 검산해 보세요(△4+▽1=5개). "
            f"변이 10이어도 크기별 표가 그대로 확장돼요. 사실 이 총수에는 n(n+2)(2n+1)÷8의 몫이라는 폐형식도 "
            f"있지만, 두 갈래 표를 스스로 만드는 눈이 핵심이랍니다.",
            en={
                "concepts": ["counting triangles", "counting by direction"],
                "statement": f"A big equilateral triangle of side {n} is divided completely into {n * n} unit triangles "
                             f"(rows of 1, 3, 5, …, {2 * n - 1} from the top). How many equilateral triangles of all sizes "
                             f"can be found in this figure? (Count the upside-down ones too.)",
                "answer": _en_plural(ans, "triangle"),
                "distractors": [_en_plural(up, "triangle"), _en_plural(n * n, "triangle"), _en_plural(2 * up, "triangle")],
                "explanation": f"Experimenting with sides 1, 2, 3 gives 1, 5, 13 — which reveals the strategy: split into "
                               f"upright △ and upside-down ▽, and count by size. △: sizes 1 to {n} give {ups_str}={up}. "
                               f"▽ of size k exists only when the whole side is at least 2k, so they shrink much faster: "
                               f"{downs_str}={down}. Adding, {up}+{down}={ans}.",
                "mistakes": [(_en_plural(up, "triangle"), "You missed the upside-down (▽) triangles. Split by direction and count them separately."),
                             (_en_plural(n * n, "triangle"), "You counted only the size-1 triangles. Bigger ones of size 2, 3, … are hiding too."),
                             (_en_plural(2 * up, "triangle"), "You assumed ▽ come in the same number as △. The ▽ shrink much faster as size grows (size k exists only when the side is at least 2k).")],
                "detail": f"A ▽'s apex points down and eats up twice the room — a size-k ▽ needs the whole side to be at "
                          f"least 2k, so the rule splits into two branches for △ and ▽, and that split is the heart of this "
                          f"problem. Check with n=2 (△4+▽1=5). Even with side 10 the size-by-size table extends unchanged. "
                          f"There is in fact a closed form, the quotient of n(n+2)(2n+1)÷8, but building the two-branch "
                          f"table yourself is the real skill.",
            },
        )


# ── 142. 당구대 45° 반사 (난8, 도형과측정) — CEILING_SPECS §3.7 ──────────────────
# 발견형 자기검증: 반사 규칙만 주어지고 세는 방법·약분 구조는 스스로 발견해야 하며(기준1),
# (15,8)·(12,9)는 손으로 끝까지 그리기 어렵게 골라 작은-사례 실험→규칙 발견을 강제한다(기준2 — (5,3)이 진입 문항).
# 그림(GRID)은 판 모양 참고용 — 렌더러가 반사 경로는 그리지 않는다(감사 시 인지).
def gen_billiard():
    corner_ko = {"RU": "오른쪽 위", "LU": "왼쪽 위", "RD": "오른쪽 아래"}
    corner_en = {"RU": "top-right", "LU": "top-left", "RD": "bottom-right"}
    for p, q, corner, d3, mis3, mis3_en in [
        (5, 3, "RU", 15, "가로×세로(전체 칸 수)를 곱했어요. 튕김은 곱이 아니라 두 방향의 리듬이 구석에서 처음 만날 때까지의 벽 접촉 수예요.",
         "You multiplied width×height (the total cells). Bounces aren't a product — they are the wall contacts before the two rhythms first meet at a corner."),
        (7, 4, "LU", 28, "가로×세로(전체 칸 수)를 곱했어요. 튕김은 곱이 아니라 두 방향의 리듬이 구석에서 처음 만날 때까지의 벽 접촉 수예요.",
         "You multiplied width×height (the total cells). Bounces aren't a product — they are the wall contacts before the two rhythms first meet at a corner."),
        (12, 9, "RD", 19, "가로·세로가 공약수를 가지면 공은 판을 다 훑기 전에 구석에 도착해요. 12×9는 4×3 판을 3배 확대한 것 — 최대공약수로 나눈 모양이 진짜 경로를 결정해요.",
         "When the width and height share a common factor, the ball reaches a corner before sweeping the whole table. 12×9 is a 4×3 table scaled by 3 — the shape divided by the gcd decides the real path."),
        (15, 8, "LU", 120, "가로×세로(전체 칸 수)를 곱했어요. 튕김은 곱이 아니라 두 방향의 리듬이 구석에서 처음 만날 때까지의 벽 접촉 수예요.",
         "You multiplied width×height (the total cells). Bounces aren't a product — they are the wall contacts before the two rhythms first meet at a corner."),
    ]:
        g = gcd(p, q)
        lcm = p * q // g
        ans = p // g + q // g - 2
        # 검산: 걸음 단위 반사 시뮬레이션(독립 경로)으로 튕김 수·도착 구석을 모두 대조
        sim_b, (cx, cy) = _billiard_bounces(p, q)
        sim_corner = {(p, q): "RU", (0, q): "LU", (p, 0): "RD"}[(cx, cy)]
        assert sim_b == ans, f"billiard 검산실패: {p}x{q} 시뮬 {sim_b} ≠ {ans}"
        assert sim_corner == corner, f"billiard 검산실패(구석): {p}x{q} {sim_corner} ≠ {corner}"
        add(
            "billiard", "SHAPE_MEASUREMENT", 8, ["반사 경로", "최소공배수 주기"],
            f"가로 {p}칸, 세로 {q}칸인 직사각형 당구대의 왼쪽 아래 구석에서 공을 대각선 45°로 쳤어요. 공은 벽에 "
            f"닿을 때마다 같은 각도로 튕기고, 네 구석 중 어느 한 곳에 도착하면 멈춰요. 공이 멈출 때까지 벽에서 "
            f"튕기는 횟수는 모두 몇 번일까요? (구석에 도착하는 것은 튕기는 횟수에 넣지 않아요)",
            f"{ans}번", [f"{p + q}번", f"{p + q - g}번", f"{d3}번"],
            f"2×1, 3×2 같은 작은 판을 그려 실험하면 규칙이 보여요. 공은 대각선으로 1칸씩 가므로 가로로 {p}칸 갈 "
            f"때마다 좌우 벽에, 세로로 {q}칸 갈 때마다 위아래 벽에 닿아요. 두 리듬이 처음으로 동시에 벽에 닿는 "
            f"곳이 구석 — 최소공배수 {lcm}걸음째예요. 그때까지 좌우 벽 {lcm // p}−1={lcm // p - 1}번, 위아래 벽 "
            f"{lcm // q}−1={lcm // q - 1}번, 합해서 {ans}번 튕겨요.",
            [(f"{p + q}번", "출발과 도착 구석까지 튕김으로 세면 2번이 더해져요. 구석은 튕기는 게 아니라 멈추는 곳이에요."),
             (f"{p + q - g}번", "대각선이 '지나는 칸 수' 문제와 혼동했어요. 여기서는 벽에 닿는 횟수를 세요."),
             (f"{d3}번", mis3)],
            figure={"type": "GRID", "params": {"w": p, "h": q}},
            detail=f"공이 멈추는 구석도 예측할 수 있어요: {lcm}÷{p}={lcm // p}이 홀수면 오른쪽·짝수면 왼쪽, "
            f"{lcm}÷{q}={lcm // q}이 홀수면 위·짝수면 아래 — 이번엔 {corner_ko[corner]} 구석이에요. 판을 "
            f"최대공약수로 약분한 {p // g}×{q // g} 모양이 경로의 원형이라, 12×9처럼 큰 판이 5번 만에 끝나기도 "
            f"해요. 벽에서 꺾지 않고 판을 거울처럼 이어 붙여 펼치면 공은 곧게 가는 대각선 하나가 되는데, 이 눈으로 "
            f"보면 튕김 = 그 대각선이 넘는 안쪽 격자선의 수랍니다.",
            en={
                "concepts": ["reflection paths", "least common multiple cycles"],
                "statement": f"A ball is shot at 45° from the bottom-left corner of a {p}-by-{q} rectangular billiard "
                             f"table. It bounces off each wall at the same angle and stops when it reaches any of the "
                             f"four corners. How many times does it bounce off the walls before stopping? (Arriving at "
                             f"a corner does not count as a bounce.)",
                "answer": _en_plural(ans, "bounce"),
                "distractors": [_en_plural(p + q, "bounce"), _en_plural(p + q - g, "bounce"), _en_plural(d3, "bounce")],
                "explanation": f"Drawing small tables like 2×1 and 3×2 reveals the rule. The ball moves one cell "
                               f"diagonally per step, so it meets a left/right wall every {p} cells across and a "
                               f"top/bottom wall every {q} cells up. The first time the two rhythms touch walls at "
                               f"the same moment is a corner — at the least common multiple, step {lcm}. Until then it "
                               f"bounces {lcm // p}−1={lcm // p - 1} times off the side walls and {lcm // q}−1={lcm // q - 1} "
                               f"times off the top/bottom, {ans} bounces in all.",
                "mistakes": [(_en_plural(p + q, "bounce"), "Counting the start and finish corners as bounces adds 2. A corner is where it stops, not a bounce."),
                             (_en_plural(p + q - g, "bounce"), "You confused this with the 'how many cells does a diagonal cross' problem. Here you count wall contacts."),
                             (_en_plural(d3, "bounce"), mis3_en)],
                "detail": f"You can even predict the finishing corner: {lcm}÷{p}={lcm // p} odd means right, even means "
                          f"left; {lcm}÷{q}={lcm // q} odd means top, even means bottom — this time it is the "
                          f"{corner_en[corner]} corner. The table reduced by the gcd, {p // g}×{q // g}, is the true "
                          f"shape of the path, which is why a big 12×9 table can finish in just 5 bounces. And if you "
                          f"unfold the table like mirrors instead of bending at walls, the ball becomes one straight "
                          f"diagonal — seen that way, bounces = the interior grid lines that diagonal crosses.",
            },
        )


# ── 143. 오목 격자 다각형의 넓이 (난8, 도형과측정) — CEILING_SPECS §3.B1, 그림 필수 ──
# 발견형 자기검증: 옛 pick(d5)과 달리 내부점·둘레점을 주지 않고 그림만 준다 — 관계식은 물론
# '점을 센다'는 발상 자체를 스스로 세워야 하고(기준1), 오목 6~8꼭짓점이라 단순 분해는 조각 7~9개의
# 오답 유도 지뢰밭이다(기준2 — 분해 정공법도 막혀 있진 않아 낮은 문턱 유지).
def gen_pickfig():
    def half(a2):
        return str(a2 // 2) if a2 % 2 == 0 else f"{a2 // 2}.5"

    for pts, d3 in [
        ([(1, 0), (4, 2), (3, 2), (6, 5), (2, 6), (3, 4), (0, 3)], 15),   # 번개
        ([(0, 5), (3, 0), (6, 5), (3, 3), (4, 6), (2, 6), (3, 5)], 13),   # 화살깃
        ([(0, 0), (5, 1), (3, 3), (6, 5), (1, 6), (2, 3)], 16),           # 갈고리
        ([(0, 4), (2, 0), (3, 3), (5, 0), (6, 4), (4, 3), (3, 6), (2, 3)], 13),  # 톱니
    ]:
        # 검산: 단순성 + 신발끈 + 내부점 반직선 판정 + 둘레점 gcd/열거 이중 + 픽 정리 삼중 대조
        area2, inner, boundary = _lattice_polygon_stats(pts)
        ans_s = half(area2)
        assert ans_s not in (half(area2 + 2), str(inner + boundary), str(d3)), f"pickfig 보기 충돌: {pts}"
        add(
            "pickfig", "SHAPE_MEASUREMENT", 8, ["격자점과 넓이", "관계 발견"],
            "모눈종이 위에 색칠한 다각형이 있어요(꼭짓점은 모두 격자점이에요). 이 다각형의 넓이는 몇 ㎠일까요? "
            "(모눈 한 칸은 1㎠예요)",
            f"{ans_s}㎠", [f"{half(area2 + 2)}㎠", f"{inner + boundary}㎠", f"{d3}㎠"],
            f"정공법은 도형을 감싼 직사각형에서 바깥 조각을 하나씩 빼는 것 — 오목한 모양이라 조각이 많아 실수하기 "
            f"쉬워요. 지름길이 있어요: 1×1 정사각형, 1×2 직사각형, 반쪽 직각삼각형 같은 아주 작은 격자 도형들로 "
            f"(넓이, 안쪽 점, 둘레 위 점) 표를 만들어 보면 '넓이 = 안쪽 점 + 둘레 점÷2 − 1'이라는 관계가 떠올라요. "
            f"이 그림은 안쪽 점 {inner}개, 둘레 점 {boundary}개니까 {inner}+{boundary}÷2−1={ans_s}㎠예요.",
            [(f"{half(area2 + 2)}㎠", "격자점으로 넓이를 어림하다 마지막 보정(−1)을 빠뜨렸어요. 작은 직사각형으로 실험해 관계식을 완성하세요."),
             (f"{inner + boundary}㎠", "다각형에 걸친 격자점 개수 자체는 넓이가 아니에요. 둘레의 점은 절반만 넓이에 기여해요."),
             (f"{d3}㎠", "경계에 걸린 반 칸들을 대충 반올림했어요. 반 칸끼리 짝을 지어 정확히 세거나, 격자점 관계를 이용하세요.")],
            figure=_grid_fig(pts),
            detail=f"안쪽 격자점 하나는 제 둘레의 한 칸어치 넓이를 온전히 대표하지만, 둘레 위의 점은 절반만 도형 "
            f"안쪽이에요. 그리고 다각형을 한 바퀴 도는 동안 딱 한 칸어치(−1)가 겹쳐 빠져요 — 그래서 넓이 = 안쪽 점 "
            f"+ 둘레 점÷2 − 1(픽의 정리라 불러요). 분해해서 빼는 정공법과 점 세기, 두 길의 답이 같은지 확인하는 "
            f"이중 검산이 이 문제의 진짜 학습 목표예요. 아무 격자 다각형이나 그려 관계식이 또 맞는지 실험해 보세요.",
            en={
                "concepts": ["lattice points and area", "discovering a relationship"],
                "statement": "A polygon is shaded on grid paper (every vertex is on a lattice point). What is its area "
                             "in cm²? (Each grid cell is 1 cm².)",
                "answer": f"{ans_s}cm²",
                "distractors": [f"{half(area2 + 2)}cm²", f"{inner + boundary}cm²", f"{d3}cm²"],
                "explanation": f"The direct route is to box the shape in a rectangle and subtract the outside pieces — "
                               f"but the shape is concave, so the pieces are many and mistakes are easy. There is a "
                               f"shortcut: make a table of (area, inside points, boundary points) for tiny grid shapes "
                               f"like a 1×1 square, a 1×2 rectangle, and half-square right triangles, and the relation "
                               f"'area = inside points + boundary points÷2 − 1' emerges. This figure has {inner} inside "
                               f"points and {boundary} boundary points, so {inner}+{boundary}÷2−1={ans_s}cm².",
                "mistakes": [(f"{half(area2 + 2)}cm²", "You estimated the area from lattice points but dropped the final correction (−1). Experiment with small rectangles to complete the relation."),
                             (f"{inner + boundary}cm²", "The raw number of lattice points touching the polygon is not its area. Boundary points contribute only half each."),
                             (f"{d3}cm²", "You roughly rounded the half-cells along the boundary. Pair up the half-cells exactly, or use the lattice-point relation.")],
                "detail": "Each inside lattice point fully represents one cell's worth of area around it, while a "
                          "boundary point is only half inside the shape. And going once around the polygon, exactly one "
                          "cell's worth (−1) drops out from the overlap — hence area = inside + boundary÷2 − 1 (known "
                          "as Pick's theorem). The real learning goal is the double check: decompose-and-subtract "
                          "versus point counting, and confirming the two roads agree. Draw any lattice polygon and test "
                          "whether the relation holds again.",
            },
        )


# ── 144. 앞·옆 실루엣으로 최대 쌓기나무 (난7, 도형과측정) — 신규 슬롯(시점·투영 추론) ──
# 발견형 자기검증: '각 칸의 상한 = min(앞모습, 옆모습)' 규칙이 문제문에 없고(기준1), 배치를 손으로
# 나열하는 우회는 4^6~4^9가지라 불가능해 칸별 상한의 발견이 필수다(기준2).
def gen_cubeviews():
    for front, side in [
        ([3, 2, 3], [3, 1]),
        ([2, 3, 1], [1, 3]),
        ([3, 1, 2], [2, 3, 1]),
        ([3, 2], [2, 3, 2]),
    ]:
        w, d = len(front), len(side)
        max_h = max(front)
        assert max(front) == max(side), f"cubeviews 실루엣 모순: {front}/{side}"
        ans = sum(min(fc, sr) for fc in front for sr in side)
        # 검산: 실루엣이 정확히 일치하는 모든 배치를 전수조사(독립 경로)한 최대와 대조
        assert _views_max_cubes(front, side) == ans, f"cubeviews 검산실패: {front}/{side}"
        d1 = sum(front) + sum(side)                      # 보이는 칸 수 합
        d2 = d * sum(front)                              # 옆모습 무시, 모든 줄을 앞모습대로
        d3 = w * d * max_h                               # 전 칸을 최고 높이로
        assert len({ans, d1, d2, d3}) == 4, f"cubeviews 보기 충돌: {front}/{side}"
        f_str = ", ".join(f"{v}층" for v in front)
        s_str = ", ".join(f"{v}층" for v in side)
        row_sums = ["+".join(str(min(fc, sr)) for fc in front) for sr in side]
        sum_str = "(" + ")+(".join(row_sums) + ")"
        f_en = ", ".join(str(v) for v in front)
        s_en = ", ".join(str(v) for v in side)
        add(
            "cubeviews", "SHAPE_MEASUREMENT", 7, ["쌓기나무", "시점 추론"],
            f"쌓기나무를 가로 {w}칸, 세로 {d}칸인 직사각형 바닥판 위에 쌓아요. 칸마다 높이는 달라도 되고, 하나도 "
            f"놓지 않는 칸이 있어도 돼요. 다 쌓은 뒤 앞에서 보면 왼쪽부터 차례로 {f_str}으로 보이고, 오른쪽 옆에서 "
            f"보면 앞쪽부터 차례로 {s_str}으로 보여요. 이렇게 보이도록 쌓을 때 쌓기나무를 '가장 많이' 쓰면 몇 개일까요?",
            f"{ans}개", [f"{d1}개", f"{d2}개", f"{d3}개"],
            f"칸 하나하나에 상한이 숨어 있어요. 어떤 칸의 기둥이 그 세로줄의 앞모습 높이보다 높으면 앞에서 튀어나와 "
            f"보이고, 그 가로줄의 옆모습 높이보다 높으면 옆에서 튀어나와 보여요. 그래서 각 칸은 두 실루엣 높이 중 "
            f"'작은 쪽'까지만 쌓을 수 있어요. 모든 칸을 그 상한까지 꽉 채워도 두 모습은 그대로예요 — 채운 개수는 "
            f"{sum_str}={ans}개예요.",
            [(f"{d1}개", "앞·옆에서 '보이는' 칸 수를 더한 값이에요. 보이는 건 실루엣일 뿐, 그 뒤로 여러 기둥이 겹쳐 숨어 있어요."),
             (f"{d2}개", "옆에서 본 모양을 무시하고 모든 줄을 앞모습대로 채웠어요. 그러면 옆모습이 조건과 달라져요."),
             (f"{d3}개", "모든 칸을 가장 높은 층수로 채우면 앞·옆 실루엣이 조건보다 높이 솟아 보여요. 칸마다 상한이 달라요.")],
            detail=f"실루엣은 '그 줄에서 가장 높은 기둥'만 보여 줘요 — 여러 기둥이 한 그림자에 숨는 거죠. 그래서 "
            f"보이는 모습이 같아도 개수는 여러 가지일 수 있고, 최대는 칸마다 min(앞모습, 옆모습)을 쌓은 배치예요. "
            f"반대로 '가장 적게' 쓰는 배치를 찾는 것도 좋은 도전이에요 — 기둥 하나가 앞·옆 실루엣을 동시에 책임지게 "
            f"겹쳐 보세요. 위에서 본 판에 칸별 상한을 적어 놓으면 3차원 문제가 2차원 표로 내려온답니다.",
            en={
                "concepts": ["stacking blocks", "reasoning from views"],
                "statement": f"You stack unit cubes on a rectangular base {w} columns wide and {d} rows deep. Each cell "
                             f"may hold a column of any height, and some cells may stay empty. Seen from the front, the "
                             f"silhouette shows heights {f_en} from left to right; seen from the right side, it shows "
                             f"heights {s_en} from front to back. What is the greatest number of cubes you could have used?",
                "answer": _en_plural(ans, "cube"),
                "distractors": [_en_plural(d1, "cube"), _en_plural(d2, "cube"), _en_plural(d3, "cube")],
                "explanation": f"A hidden ceiling sits on every cell. If a cell's column rose above its file's front-view "
                               f"height it would stick out from the front, and above its row's side-view height it would "
                               f"stick out from the side. So each cell can hold at most the 'smaller' of the two "
                               f"silhouette heights. Filling every cell right up to that ceiling still matches both "
                               f"views — and that filling uses {sum_str}={ans} cubes.",
                "mistakes": [(_en_plural(d1, "cube"), "That adds the squares 'visible' from the front and side. A silhouette is only an outline — several columns hide behind it."),
                             (_en_plural(d2, "cube"), "You ignored the side view and filled every row like the front view. Then the side view would no longer match."),
                             (_en_plural(d3, "cube"), "Filling every cell to the tallest height would make the front and side silhouettes rise higher than given. Each cell has its own ceiling.")],
                "detail": "A silhouette shows only 'the tallest column in that line' — many columns hide in one shadow. "
                          "So the same views can come from many different counts, and the maximum is the arrangement "
                          "with min(front, side) on every cell. Finding the 'fewest' cubes is a great follow-up "
                          "challenge — overlap the duties so one column serves the front and side silhouettes at once. "
                          "Writing each cell's ceiling on the top view turns a 3-D problem into a 2-D table.",
            },
        )


# ── 145. 계단 도형의 둘레 (난6, 도형과측정) — 신규 슬롯(변 밀어 붙이기 발견), 그림 필수 ──
# 발견형 자기검증: '가로 변은 위로, 세로 변은 오른쪽으로 밀면 직사각형'이라는 통찰이 문제문에 없고(기준1),
# 턱 6~8개짜리 도형은 낱개 변 세기(20~30개)가 실수를 강하게 유발해 통찰 경로가 압도적으로 유리하다(기준2).
def gen_stairperim():
    for heights in [
        [5, 4, 4, 2, 2, 1],
        [6, 4, 4, 3, 3, 1, 1],
        [6, 6, 5, 5, 3, 3, 2, 1],
        [5, 4, 4, 3, 2, 2, 1],
    ]:
        w, h = len(heights), max(heights)
        assert all(a >= b for a, b in zip(heights, heights[1:])) and heights[-1] >= 1, f"stairperim 비계단: {heights}"
        ans = 2 * (w + h)
        pts = _stair_polygon(heights)
        # 검산: 셀 단위 완전열거(이웃 없는 변 수)로 둘레를 직접 세고, 다각형 넓이·둘레와 삼중 대조
        cell_perim, cell_area = _stair_cell_stats(heights)
        walk = sum(abs(x2 - x1) + abs(y2 - y1) for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))
        assert cell_perim == walk == ans, f"stairperim 검산실패: {heights} ({cell_perim},{walk})≠{ans}"
        assert cell_area == sum(heights) == _shoelace2(pts) // 2, f"stairperim 넓이 불일치: {heights}"
        area = cell_area
        assert len({ans, area, ans - 2, ans + 4}) == 4, f"stairperim 보기 충돌: {heights}"
        add(
            "stairperim", "SHAPE_MEASUREMENT", 6, ["둘레", "변 밀어 붙이기"],
            "모눈종이에 계단 모양 도형을 색칠했어요(그림). 이 도형의 둘레는 몇 cm일까요? (모눈 한 칸의 한 변은 1cm예요)",
            f"{ans}cm", [f"{area}cm", f"{ans - 2}cm", f"{ans + 4}cm"],
            f"턱이 많아 변을 하나씩 세다 보면 꼭 빠뜨려요. 계단의 가로 변들을 모두 위로 밀어 올리고, 세로 변들을 "
            f"모두 오른쪽으로 밀어 보세요 — 정확히 도형을 둘러싼 가로 {w}칸, 세로 {h}칸 직사각형의 둘레가 돼요. "
            f"그래서 둘레는 ({w}+{h})×2={ans}cm예요.",
            [(f"{area}cm", "색칠한 칸의 수(넓이)를 세었어요. 둘레는 도형을 두르는 바깥 변의 길이예요."),
             (f"{ans - 2}cm", "계단 턱의 짧은 변을 빠뜨렸어요. 턱마다 가로·세로 변이 하나씩 꼭 있어요."),
             (f"{ans + 4}cm", "턱이 많으니 둘러싼 직사각형보다 길 거라 짐작했어요. 가로 변을 위로·세로 변을 오른쪽으로 밀어 붙이면 정확히 직사각형 둘레와 같아져요.")],
            figure=_grid_fig(pts),
            detail=f"계단처럼 '안으로 파인 곳 없이 한 방향으로만 내려가는' 도형은 턱이 몇 개든 둘레가 둘러싼 "
            f"직사각형과 똑같아요. 하지만 ㄷ자처럼 파인 곳이 있으면 밀어 붙일 때 변이 겹쳐 둘레가 더 길어져요 — "
            f"어떤 도형이 '밀어 붙이기'가 되는지 직접 그려 실험해 보세요. 그리고 이 도형의 넓이는 {area}㎠로 계단 "
            f"모양마다 달라지지만 둘레는 그대로예요. 넓이와 둘레가 따로 논다는 것, 그것도 이 문제의 발견이랍니다.",
            en={
                "concepts": ["perimeter", "sliding edges"],
                "statement": "A staircase-shaped figure is shaded on grid paper (see the picture). What is the "
                             "perimeter of this figure, in cm? (Each side of a grid cell is 1 cm.)",
                "answer": f"{ans}cm",
                "distractors": [f"{area}cm", f"{ans - 2}cm", f"{ans + 4}cm"],
                "explanation": f"With so many steps, counting the sides one by one always drops a few. Instead, slide "
                               f"every horizontal edge of the staircase up and every vertical edge to the right — they "
                               f"become exactly the surrounding rectangle, {w} cells wide and {h} cells tall. So the "
                               f"perimeter is ({w}+{h})×2={ans}cm.",
                "mistakes": [(f"{area}cm", "You counted the shaded cells (the area). The perimeter is the length of the outer edges wrapping the shape."),
                             (f"{ans - 2}cm", "You dropped one of the short step edges. Every step has exactly one horizontal and one vertical edge."),
                             (f"{ans + 4}cm", "You guessed the many steps make it longer than the surrounding rectangle. Slide the horizontal edges up and the vertical edges right — it matches the rectangle exactly.")],
                "detail": f"A shape that, like a staircase, only ever descends in one direction with no inward dents "
                          f"has the same perimeter as its surrounding rectangle, no matter how many steps. But a shape "
                          f"with a dent, like a U, gains perimeter because edges overlap when you slide them — draw "
                          f"your own shapes and test which ones 'slide'. Also, this figure's area is {area}cm² and "
                          f"changes with each staircase, while the perimeter stays put. Area and perimeter living "
                          f"separate lives — that too is this problem's discovery.",
            },
        )


# ── 146. 접어 자른 테이프의 조각 수 (난5, 도형과측정) — 신규 슬롯(접기/자르기 결과 추론) ──
# 발견형 자기검증: 조각 수 규칙이 문제문에 없어 '겹×자르기 = 잘린 점, 조각 = 잘린 점+1'의 두 겹
# 구조를 스스로 세워야 하고(기준1), 3번 접어 2번 자르는 경우는 머릿속 낱장 추적이 17조각 규모라
# 실수 없이는 비현실적이라 구조 발견 경로가 압도적으로 유리하다(기준2 — (2,1)이 진입 문항).
def gen_foldpieces():
    for folds, cuts in [(2, 1), (3, 1), (2, 2), (3, 2)]:
        layers = 2 ** folds
        ans = cuts * layers + 1
        # 검산: 겹의 (원점, 방향)을 추적하는 접기 시뮬레이션(독립 경로)으로 잘린 점을 전부 모아 대조
        assert _fold_cut_pieces(folds, cuts) == ans, f"foldpieces 검산실패: k={folds}, c={cuts}"
        assert len({ans, cuts * layers, cuts + 1, (cuts + 1) * layers}) == 4, f"foldpieces 보기 충돌: {folds},{cuts}"
        add(
            "foldpieces", "SHAPE_MEASUREMENT", 5, ["접어 자르기", "겹과 조각"],
            f"폭이 좁고 긴 종이 테이프를 반으로 {folds}번 접었어요. 접힌 채로 가위로 테이프의 폭 방향을 따라 곧게 "
            f"{cuts}번 잘랐어요(서로 다른 곳을, 양 끝이나 접힌 자리가 아닌 곳에서요). 종이를 모두 펼치면 몇 조각으로 "
            f"나뉘어 있을까요?",
            f"{ans}조각", [f"{cuts * layers}조각", f"{cuts + 1}조각", f"{(cuts + 1) * layers}조각"],
            f"반으로 {folds}번 접으면 테이프가 {layers}겹으로 포개져요. 가위질 한 번은 {layers}겹을 동시에 지나므로, "
            f"펼친 테이프에는 잘린 곳이 {cuts}×{layers}={cuts * layers}군데 생겨요. 긴 테이프는 잘린 곳이 1군데면 "
            f"2조각, 2군데면 3조각 — 조각은 언제나 잘린 곳보다 1 많아요. 그래서 {cuts * layers}+1={ans}조각이에요.",
            [(f"{cuts * layers}조각", "잘린 곳의 개수까지는 맞게 셌는데, 조각 수는 잘린 곳보다 1 많아요(선 하나가 종이를 2조각으로 나누듯이요)."),
             (f"{cuts + 1}조각", f"접힌 겹을 잊었어요. 가위질 한 번이 {layers}겹을 동시에 자르니, 펼치면 잘린 곳이 {layers}배로 늘어나요."),
             (f"{(cuts + 1) * layers}조각", f"겹마다 {cuts + 1}조각이 된다고 곱했어요. 하지만 접힌 자리는 잘리지 않아 이웃한 겹끼리 이어져 있어요 — 펼치면 하나로 연결된 조각이 많아요.")],
            detail=f"두 규칙의 합작이에요: ① 접을 때마다 겹이 2배(접기 {folds}번 → {layers}겹) ② 조각 수 = 잘린 곳 "
            f"+ 1(울타리 기둥과 칸의 관계). 헷갈리면 접기 1번·자르기 1번부터 실제로 해 보세요 — 2겹이라 잘린 곳 "
            f"2군데, 3조각이 나와요. 펼친 종이의 산·골 접힌 자국을 관찰하면 접힌 자리가 왜 조각들을 이어 주는지, "
            f"'겹×자르기'가 왜 곱셈이고 마지막에 왜 +1인지가 한눈에 보인답니다.",
            en={
                "concepts": ["folding and cutting", "layers and pieces"],
                "statement": f"You fold a long, narrow paper tape in half {folds} times. Still folded, you make "
                             f"{cuts} straight scissor cut(s) across its width (at different places, away from the ends "
                             f"and the folds). When you unfold the tape completely, how many pieces is it in?",
                "answer": _en_plural(ans, "piece"),
                "distractors": [_en_plural(cuts * layers, "piece"), _en_plural(cuts + 1, "piece"), _en_plural((cuts + 1) * layers, "piece")],
                "explanation": f"Folding in half {folds} times stacks the tape into {layers} layers. One scissor cut "
                               f"passes through all {layers} layers at once, so the unfolded tape has "
                               f"{cuts}×{layers}={cuts * layers} cut places. A long tape with 1 cut place is 2 pieces, "
                               f"with 2 places 3 pieces — pieces are always one more than cut places. So "
                               f"{cuts * layers}+1={ans} pieces.",
                "mistakes": [(_en_plural(cuts * layers, "piece"), "You counted the cut places correctly, but the pieces number one more than the cuts (just as one snip turns paper into 2 pieces)."),
                             (_en_plural(cuts + 1, "piece"), f"You forgot the folded layers. One snip cuts {layers} layers at once, so unfolding multiplies the cut places by {layers}."),
                             (_en_plural((cuts + 1) * layers, "piece"), f"You multiplied as if each layer became {cuts + 1} separate pieces. But the folds are not cut — neighboring layers stay joined there, so many pieces unfold into one connected strip.")],
                "detail": f"Two rules work together: ① each fold doubles the layers ({folds} folds → {layers} layers), "
                          f"② pieces = cut places + 1 (the fence-post relation). If it feels slippery, actually try one "
                          f"fold and one cut — 2 layers give 2 cut places and 3 pieces. Watching the mountain-and-valley "
                          f"creases on the unfolded strip shows why folds keep pieces joined, why 'layers × cuts' is a "
                          f"multiplication, and why the +1 comes last.",
            },
        )
