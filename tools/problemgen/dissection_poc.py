#!/usr/bin/env python3
"""격자 합동 등분 퍼즐 — 생성기 + 검증기 + 유일해 증명 (feasibility POC).

핵심 주장 검증:
  (1) 생성: 격자 도형을 K개의 '서로 합동인 연결 조각'으로 나누는 모든 방법을 완전탐색.
  (2) 검증: 사용자의 '셀→조각' 배정이 유효한 등분인지 알고리즘으로 판정(정답 저장 불필요).
  (3) 유일해: 작은 격자는 해가 정확히 1개인지 전수로 보장 → 퍼즐 품질.
  (4) 응용: 각 조각에 심볼(○△□)이 하나씩 들어가는 제약 버전.
앱 코드 무변경. 되는지 증명하고 예시를 PNG로 렌더한다.
"""
DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
# 8개 대칭(회전4 × 반사2) — 정사각 격자 위 강체 변환
TF = [
    lambda r, c: (r, c), lambda r, c: (-c, r), lambda r, c: (-r, -c), lambda r, c: (c, -r),
    lambda r, c: (r, -c), lambda r, c: (-c, -r), lambda r, c: (-r, c), lambda r, c: (c, r),
]


def _normalize(cells):
    cells = list(cells)
    mr = min(r for r, c in cells)
    mc = min(c for r, c in cells)
    return frozenset((r - mr, c - mc) for r, c in cells)


def canon(cells):
    """폴리오미노의 표준형 — 8대칭 중 사전순 최소. 두 조각이 합동 ⇔ canon이 같다."""
    return min(tuple(sorted(_normalize(t(r, c) for r, c in cells))) for t in TF)


def connected(cells):
    cells = set(cells)
    if not cells:
        return True
    start = next(iter(cells))
    seen, stack = {start}, [start]
    while stack:
        r, c = stack.pop()
        for dr, dc in DIRS:
            nb = (r + dr, c + dc)
            if nb in cells and nb not in seen:
                seen.add(nb)
                stack.append(nb)
    return len(seen) == len(cells)


def _connected_subsets(region, anchor, size):
    """region 안에서 anchor를 포함하는, 크기 size의 연결 부분집합 전부."""
    region = set(region)
    found = set()

    def rec(piece):
        if len(piece) == size:
            found.add(frozenset(piece))
            return
        border = set()
        for (r, c) in piece:
            for dr, dc in DIRS:
                nb = (r + dr, c + dc)
                if nb in region and nb not in piece:
                    border.add(nb)
        for nb in border:
            rec(piece | {nb})

    rec({anchor})
    return found


def _orientations(shape):
    return {_normalize(t(r, c) for r, c in shape) for t in TF}


def _placements_covering(shape, cell, region, covered):
    """shape(표준형)를 cell을 덮도록 놓는 모든 배치(회전·반사·평행이동), region 안·covered와 비겹침."""
    res = set()
    for orient in _orientations(shape):
        for (ar, ac) in orient:
            dr, dc = cell[0] - ar, cell[1] - ac
            placed = frozenset((r + dr, c + dc) for (r, c) in orient)
            if placed <= region and not (placed & covered):
                res.add(placed)
    return res


def all_partitions(region, k, symbols=None, limit=None):
    """region을 K개의 서로 합동인 연결 조각으로 나누는 모든 방법. symbols가 있으면
    각 조각이 모든 심볼종류를 정확히 하나씩 포함해야 한다. 결과: [ [조각셋, ...], ... ]."""
    region = set(region)
    n = len(region)
    if n % k:
        return []
    s = n // k
    symtypes = set(symbols.values()) if symbols else None
    if symtypes and len(symtypes) != s:
        return []  # 조각 크기 = 심볼 종류 수여야 '하나씩'이 성립
    order = sorted(region)
    anchor0 = order[0]
    sols = []

    def ok_sym(piece):
        if not symbols:
            return True
        got = [symbols[c] for c in piece if c in symbols]
        return len(got) == len(set(got)) == len(symtypes)

    def bt(covered, pieces, shape):
        if limit and len(sols) >= limit:
            return
        cell = next((c for c in order if c not in covered), None)
        if cell is None:
            sols.append(list(pieces))
            return
        for piece in _placements_covering(shape, cell, region, covered):
            if ok_sym(piece):
                bt(covered | piece, pieces + [piece], shape)

    for first in _connected_subsets(region, anchor0, s):
        if ok_sym(first):
            bt(set(first), [first], canon(first))
    return sols


def validate(region, assignment, k, symbols=None):
    """사용자 답 검증: assignment = {cell: piece_id(0..k-1)}. 유효한 등분인가?
    반환 (ok, 이유). 이게 앱 채점기의 파이썬 원형이다."""
    region = set(region)
    if set(assignment) != region:
        return False, "모든 칸을 정확히 한 조각에 배정해야 해요."
    pieces = {}
    for cell, pid in assignment.items():
        pieces.setdefault(pid, set()).add(cell)
    if len(pieces) != k:
        return False, f"조각이 {k}개여야 해요(현재 {len(pieces)}개)."
    sizes = {len(p) for p in pieces.values()}
    if len(sizes) != 1:
        return False, "조각들의 칸 수가 서로 달라요."
    for p in pieces.values():
        if not connected(p):
            return False, "각 조각은 한 덩어리로 이어져야 해요."
    shapes = {canon(p) for p in pieces.values()}
    if len(shapes) != 1:
        return False, "조각들의 '모양'이 서로 합동이 아니에요(회전·뒤집기까지 같아야 함)."
    if symbols:
        symtypes = set(symbols.values())
        for p in pieces.values():
            got = [symbols[c] for c in p if c in symbols]
            if not (len(got) == len(set(got)) == len(symtypes)):
                return False, "각 조각에 모든 심볼이 하나씩 들어가야 해요."
    return True, "정답! 합동 등분이 완성됐어요."


def parse(art):
    """문자열 도형 파싱. '#'=칸(심볼 없음), '.'·' '=빈칸, 그 외 문자=심볼 있는 칸."""
    cells, symbols = set(), {}
    for r, line in enumerate(art.strip("\n").splitlines()):
        for c, ch in enumerate(line):
            if ch not in " .":
                cells.add((r, c))
                if ch != "#":
                    symbols[(r, c)] = ch
    return cells, symbols


# ── 렌더링(PIL) — 퍼즐과 해답을 그림으로 (앱 ProblemFigureView의 파이썬 미리보기 역할) ──
from PIL import Image, ImageDraw  # noqa: E402

_PIECE_COLORS = [(255, 214, 165), (168, 230, 207), (255, 170, 165), (174, 198, 255),
                 (220, 198, 255), (255, 236, 179), (179, 229, 252), (248, 187, 208)]
_INK = (40, 46, 56)


def _draw_symbol(dr, cx, cy, rad, sym):
    col = {"O": (232, 76, 70), "T": (18, 178, 110), "S": (76, 141, 246), "*": (199, 125, 14)}.get(sym, _INK)
    if sym == "O":
        dr.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=col, width=4)
    elif sym == "T":
        dr.polygon([(cx, cy - rad), (cx - rad, cy + rad), (cx + rad, cy + rad)], outline=col, width=4)
    elif sym == "S":
        dr.rectangle([cx - rad, cy - rad, cx + rad, cy + rad], outline=col, width=4)
    else:  # 별(★) 근사 — 다이아
        dr.polygon([(cx, cy - rad), (cx + rad, cy), (cx, cy + rad), (cx - rad, cy)], outline=col, width=4)


def render(cells, k, symbols=None, solution=None, cell=64, pad=24):
    """한 퍼즐을 그린다. solution(조각 리스트)을 주면 색칠+굵은 절단선, 없으면 빈 퍼즐."""
    rs = [r for r, c in cells]
    cs = [c for r, c in cells]
    H, W = max(rs) + 1, max(cs) + 1
    img = Image.new("RGB", (W * cell + 2 * pad, H * cell + 2 * pad), (246, 247, 249))
    dr = ImageDraw.Draw(img)
    pid = {}
    if solution:
        for i, piece in enumerate(solution):
            for c in piece:
                pid[c] = i

    def px(r, c):
        return pad + c * cell, pad + r * cell

    for (r, c) in cells:
        x, y = px(r, c)
        fill = _PIECE_COLORS[pid[(r, c)] % len(_PIECE_COLORS)] if (r, c) in pid else (255, 255, 255)
        dr.rectangle([x, y, x + cell, y + cell], fill=fill, outline=(210, 214, 220), width=1)
    # 조각 경계(굵은 절단선) — 이웃이 없거나 다른 조각이면 두껍게
    for (r, c) in cells:
        x, y = px(r, c)
        edges = [((r - 1, c), [(x, y), (x + cell, y)]), ((r + 1, c), [(x, y + cell), (x + cell, y + cell)]),
                 ((r, c - 1), [(x, y), (x, y + cell)]), ((r, c + 1), [(x + cell, y), (x + cell, y + cell)])]
        for nb, seg in edges:
            outer = nb not in cells
            cut = solution and (r, c) in pid and nb in pid and pid[nb] != pid[(r, c)]
            if outer or cut:
                dr.line(seg, fill=_INK, width=5)
    for c, sym in (symbols or {}).items():
        x, y = px(*c)
        _draw_symbol(dr, x + cell // 2, y + cell // 2, cell // 3, sym)
    return img


def showcase(items, path):
    """items = [(제목, cells, symbols, solution), ...] — 각 행에 [퍼즐 | 해답] 나란히."""
    from PIL import ImageFont
    try:
        font = ImageFont.truetype("/System/Library/Fonts/AppleSDGothicNeo.ttc", 26, index=1)
    except Exception:
        font = ImageFont.load_default()
    rows = []
    for title, cells, symbols, sol in items:
        puz = render(cells, len(sol), symbols=symbols)
        ans = render(cells, len(sol), symbols=symbols, solution=sol)
        gap = 40
        w = puz.width + ans.width + gap
        h = max(puz.height, ans.height) + 56
        row = Image.new("RGB", (w, h), (255, 255, 255))
        row.paste(puz, (0, 48))
        row.paste(ans, (puz.width + gap, 48))
        d = ImageDraw.Draw(row)
        d.text((4, 10), title + "  —  왼쪽: 문제(등분해 보세요)   오른쪽: 정답", fill=_INK, font=font)
        rows.append(row)
    W = max(r.width for r in rows)
    Himg = Image.new("RGB", (W + 40, sum(r.height + 30 for r in rows) + 30), (255, 255, 255))
    y = 20
    for r in rows:
        Himg.paste(r, (20, y))
        y += r.height + 30
    Himg.save(path)
    return path


def demo(out_dir="/tmp/ddakpul-dissection"):
    """유일해 예시 4종을 찾아 [문제|정답] 그림으로 렌더(자가검증)."""
    import os
    from itertools import permutations
    os.makedirs(out_dir, exist_ok=True)
    L = {(0, 0), (1, 0), (2, 0), (3, 0), (0, 1), (1, 1), (2, 1), (3, 1),
         (2, 2), (3, 2), (2, 3), (3, 3)}                                  # L 12칸 → 4개의 작은 L
    stair = {(0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (0, 1)}              # 계단 6칸 → 2
    notch = {(r, c) for r in range(3) for c in range(4)} - {(0, 0), (0, 3)}  # 10칸 → 2
    items = [("L → 작은 L 4개(rep-tile)", L, None, all_partitions(L, 4)[0]),
             ("계단 → 2조각", stair, None, all_partitions(stair, 2)[0]),
             ("볼록 도형 → 2조각", notch, None, all_partitions(notch, 2)[0])]
    # 심볼: 2x6 → 4조각, 각 조각에 O·T·S 하나씩(유일해 되는 배치 탐색)
    grid = {(r, c) for r in range(2) for c in range(6)}
    cl = sorted(grid)
    for perm in permutations(("O" * 4) + ("T" * 4) + ("S" * 4)):
        sa = dict(zip(cl, perm))
        sols = all_partitions(grid, 4, symbols=sa)
        if len(sols) == 1:
            items.append(("심볼 응용: 각 조각에 ○△□ 하나씩", grid, sa, sols[0]))
            break
    path = showcase(items, os.path.join(out_dir, "showcase.png"))
    print(f"렌더: {path} ({len(items)}개 유일해 퍼즐)")


if __name__ == "__main__":
    demo()
