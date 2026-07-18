#!/usr/bin/env python3
"""계층 코드(AA-BB-CC-DD-SS) 주입 — 재생성 시 `code` 필드를 항상 재구축한다.

과거엔 코드가 일회성으로 주입되고 파이프라인이 재현하지 않아, generate.py를 다시 돌리면
830문항의 code가 전부 사라졌다. 이 모듈이 그 결함을 없앤다.

`method_codes.json`을 **안정 레지스트리**로 쓴다: 기존 방법(family)의 AA-BB-CC는 절대 바꾸지
않고(코드 churn 방지), 처음 보는 family만 해당 유형의 다음 빈 CC로 append한다. 난이도(DD)와
일련번호(SS)는 각 문항의 groupId·id에서 결정론적으로 파생한다.

코드 형식: AA-BB-CC-DD-SS = 영역·유형·방법·난이도·일련.
동영상은 앞 6자리(AA-BB-CC = 방법)에 붙는다(난이도·숫자가 달라도 방법 같으면 한 영상).
"""
import json
import os
import re

from taxonomy import AREA_CODE, classify

ROOT = os.path.dirname(os.path.abspath(__file__))
MC_PATH = os.path.join(ROOT, "method_codes.json")
_GID = re.compile(r"g-gen-(.+)-(\d+)$")


def _family_diff(p):
    """문항의 groupId(g-gen-{family}-{diff})에서 (family, 난이도)를 뽑는다."""
    m = _GID.match(p.get("groupId", ""))
    if not m:
        raise ValueError(f"groupId 형식 오류: {p.get('id')} / {p.get('groupId')!r}")
    return m.group(1), int(m.group(2))


def ensure_registry(problems):
    """problems에 등장하는 모든 family가 method_codes.json에 있도록 보장한다(append-only).

    기존 매핑은 그대로 두고, 신규 family만 그 유형(AA-BB)의 다음 빈 CC로 추가한다.
    반환: (registry, 신규배정목록, 미분류(99)목록). 신규가 있으면 파일을 갱신 저장한다.
    """
    registry = {}
    if os.path.exists(MC_PATH):
        registry = json.load(open(MC_PATH, encoding="utf-8"))

    used = {}  # (aa, bb) -> {이미 쓰인 cc 정수}
    for code in registry.values():
        aa, bb, cc = code.split("-")
        used.setdefault((aa, bb), set()).add(int(cc))

    rep = {}  # family -> (area, concepts) — 신규 분류용 대표 정보
    for p in problems:
        fam, _ = _family_diff(p)
        rep.setdefault(fam, (p["area"], p.get("concepts", [])))

    new, unmatched = [], []
    for fam in sorted(rep):  # 결정론적 순서
        if fam in registry:
            continue
        area, concepts = rep[fam]
        aa = AREA_CODE[area]
        bb, _ = classify(area, fam, concepts)
        if bb == "99":
            unmatched.append(fam)
        seen = used.setdefault((aa, bb), set())
        cc = 1
        while cc in seen:
            cc += 1
        seen.add(cc)
        registry[fam] = f"{aa}-{bb}-{cc:02d}"
        new.append((fam, registry[fam]))

    if new:
        json.dump(registry, open(MC_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return registry, new, unmatched


def inject_codes(problems, registry):
    """각 문항에 code(AA-BB-CC-DD-SS)를 주입하고, code를 id 바로 뒤 자리로 정렬한다."""
    for i, p in enumerate(problems):
        fam, diff = _family_diff(p)
        serial = int(p["id"].rsplit("-", 1)[1])  # id=gen-{family}-{idx}, idx=그룹 내 일련
        code = f"{registry[fam]}-{diff:02d}-{serial:02d}"
        rest = {k: v for k, v in p.items() if k not in ("id", "code")}
        problems[i] = {"id": p["id"], "code": code, **rest}
