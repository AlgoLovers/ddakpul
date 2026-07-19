#!/usr/bin/env python3
"""격자 합동 등분 퍼즐 정식 생성기 — 난이도별 '유일해' 퍼즐을 대량 생성해 JSON으로 낸다.

dissection_poc.py(타당성 증명)의 검증된 알고리즘(canon·all_partitions·connected)을 재사용한다.
- 폴리오미노 도형을 크기별로 열거(회전·반사 중복 제거)
- 각 도형에 대해 K개 합동 등분의 해 개수를 세어 '정확히 1개(유일해)'만 채택
- 난이도 = 도형 크기·조각 수·심볼 유무로 매핑
- area는 항상 SHAPE_MEASUREMENT. 문장은 앱이 조각 수·심볼로 지역화(문자열은 저장 안 함).

출력: app/src/main/assets/problems_dissection.json
  { "version":1, "problems":[ {id, area, difficulty, groupId, pieceCount, cells:[[r,c]...],
                               symbols:[[r,c,"O|T|S"]...](선택)} ] }
정답을 저장하지 않는다 — 앱의 ValidateDissectionUseCase가 규칙으로 채점(해가 여럿일 수 있음).
"""
import json
import os

from dissection_poc import DIRS, all_partitions, canon

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "app", "src", "main", "assets", "problems_dissection.json")

# 난이도 매핑: (조각수, 조각당 칸수, 심볼여부) → 난이도. 2조각 작음=쉬움 … 심볼=어려움.
DIFFICULTY = {
    (2, 2, False): 2,
    (2, 3, False): 3,
    (3, 2, False): 3,
    (2, 4, False): 4,
    (4, 2, False): 4,
    (3, 3, False): 5,
    (4, 3, False): 6,
    (2, 3, True): 6,   # 심볼 2조각(각 3칸)
    (3, 3, True): 7,   # 심볼 3조각
    (4, 3, True): 8,   # 심볼 4조각
}
PER_GROUP_MAX = 6  # 난이도(그룹)당 최대 문항 — 다양성 확보 + 과밀 방지


def polyominoes(size):
    """크기 size의 연결 폴리오미노 전부(회전·반사 동치는 하나만). canon으로 중복 제거."""
    frontier = {frozenset({(0, 0)})}
    for _ in range(size - 1):
        nxt = {}
        for p in frontier:
            for (r, c) in p:
                for dr, dc in DIRS:
                    nb = (r + dr, c + dc)
                    if nb not in p:
                        cand = p | {nb}
                        nxt[canon(cand)] = cand
        frontier = set(nxt.values())
    dedup = {}
    for p in frontier:
        dedup[canon(p)] = p
    return [dedup[k] for k in sorted(dedup)]  # canon 순 정렬 → 재생성 결정성


def _shift(cells):
    mr = min(r for r, c in cells)
    mc = min(c for r, c in cells)
    return [(r - mr, c - mc) for r, c in cells]


def generate():
    problems = []
    counts = {}
    # (조각수 k, 조각당 칸수 s) 조합을 훑으며 유일해 도형 수집
    for (k, s, sym), diff in sorted(DIFFICULTY.items(), key=lambda kv: kv[1]):
        if sym:
            continue  # 심볼 퍼즐은 아래에서 따로(도형 재사용)
        n = k * s
        picked = 0
        for poly in polyominoes(n):
            if picked >= PER_GROUP_MAX:
                break
            cells = sorted(_shift(poly))
            sols = all_partitions(set(cells), k)
            if len(sols) != 1:
                continue
            gid = f"g-dissect-{diff}"
            idx = counts.get(gid, 0) + 1
            counts[gid] = idx
            problems.append({
                "id": f"dissect-{diff}-{idx}",
                "area": "SHAPE_MEASUREMENT",
                "difficulty": diff,
                "groupId": gid,
                "pieceCount": k,
                "cells": [[r, c] for r, c in cells],
            })
            picked += 1

    # 심볼 퍼즐 — 유일한 (도형,K) 위에 심볼을 얹어 '심볼 제약 하 유일해'가 되는 배치 탐색
    _add_symbol_puzzles(problems, counts)

    problems.sort(key=lambda p: (p["difficulty"], p["id"]))
    payload = {"version": 1, "problems": problems}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    dist = {}
    for p in problems:
        dist[p["difficulty"]] = dist.get(p["difficulty"], 0) + 1
    print(f"생성 {len(problems)}퍼즐 → {os.path.relpath(OUT)}")
    print("난이도 분포:", dict(sorted(dist.items())))


def _add_symbol_puzzles(problems, counts):
    """각 조각에 O·T·S(●▲■)가 하나씩 — 조각당 3칸. 도형 위 심볼 배치를 결정론적으로 훑어 유일해 채택."""
    from itertools import permutations
    specs = [(2, 6), (3, 7), (4, 8)]  # (조각수 k, 난이도)
    for k, diff in specs:
        n = k * 3
        picked = 0
        for poly in polyominoes(n):
            if picked >= PER_GROUP_MAX:
                break
            cells = sorted(_shift(poly))
            if len(all_partitions(set(cells), k)) == 0:
                continue  # 애초에 합동 등분이 안 되면 건너뜀
            multiset = ("O" * k) + ("T" * k) + ("S" * k)
            seen = set()
            for perm in permutations(multiset):
                if perm in seen:
                    continue
                seen.add(perm)
                symbols = {cells[i]: perm[i] for i in range(n)}
                if len(all_partitions(set(cells), k, symbols=symbols)) == 1:
                    gid = f"g-dissect-{diff}"
                    idx = counts.get(gid, 0) + 1
                    counts[gid] = idx
                    problems.append({
                        "id": f"dissect-{diff}-{idx}",
                        "area": "SHAPE_MEASUREMENT",
                        "difficulty": diff,
                        "groupId": gid,
                        "pieceCount": k,
                        "cells": [[r, c] for r, c in cells],
                        "symbols": [[r, c, perm[cells.index((r, c))]] for r, c in cells],
                    })
                    picked += 1
                    break
                if len(seen) > 4000:
                    break


if __name__ == "__main__":
    generate()
