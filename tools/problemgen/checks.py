#!/usr/bin/env python3
"""문제은행 품질 게이트 — build.py가 저장 후 자동 호출한다. 치명 위반이면 예외로 멈춘다.

치명(빌드 실패):
  1. 파이프라인 .py 안 최상위 def 중복(뒤 정의가 앞을 무음으로 덮어쓰는 버그 원천)
  2. gen_* 정의 ↔ GENERATORS 등록 불일치(등록 누락 = 무음 미생성)
  3. 한/영 대칭: 같은 id 집합, 같은 difficulty·groupId·code, 같은 숫자 정답
  4. 난이도 순서 제약(difficulty_constraints.json) 위반
     — 예: '규칙을 받아 적용만'(recur)은 '규칙을 스스로 발견'(hanoi·tribstairs)보다 낮아야 한다

  5. 사실상 중복 유형(개념·정답·문장이 모두 유사) — 다양성의 반대말. 대량 저작 시 최대 위험.
     의도된 형제(난이도 사다리 등)는 한 축이 반드시 낮으므로 통과, duplicate_allowlist.json로 예외.

보고(비치명, 콘솔):
  6. 정답 숫자가 해설에 안 보이는 문항(해설-정답 불일치 의심)
  7. 독립 검산(assert/기각) 없는 제너레이터 목록 — 솔버 검증 100% 커버리지가 목표
  8. 영역×난이도 문항 수 + 유형 다양성 지도(서로 다른 유형이 얇은 칸 조준용)
  9. 중복 주의 유형쌍(같은 개념+유사 문장 — 형제면 정상, 창궐하면 검토)
"""
import ast
import json
import re
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIPELINE_FILES = ["core.py", "gen_number.py", "gen_change.py", "gen_shape.py", "gen_data.py", "build.py"]
AREA_ORDER = ["NUMBER_OPERATION", "CHANGE_RELATION", "SHAPE_MEASUREMENT", "DATA_POSSIBILITY"]
_GID = re.compile(r"g-gen-(.+)-(\d+)$")

# 유형 중복 임계 — 현재 227유형의 최고 유사쌍(cubestack↔cubemid: 개념1.0·정답0.33·문장0.86,
# 의도된 사다리)을 통과시키도록 보정. 진짜 중복은 세 축이 동시에 높다(오늘 지운 boxsurface=cubesurf 등).
DUP_CONCEPT, DUP_ANSWER, DUP_SKEL = 0.99, 0.50, 0.85  # 셋 다 넘으면 치명
WATCH_CONCEPT, WATCH_SKEL = 0.99, 0.80  # 같은 개념+유사 문장 = 보고(사람 검토)


def _digits(s):
    return re.sub(r"[^0-9]", "", s)


def _check_defs(registered_names):
    """중복 def·등록 정합. 반환: gen_* 이름 → 소스 세그먼트(검산 커버리지 보고용)."""
    seen = {}
    gen_src = {}
    for fname in PIPELINE_FILES:
        src = (HERE / fname).read_text(encoding="utf-8")
        tree = ast.parse(src)
        lines = src.splitlines(keepends=True)
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            if node.name in seen:
                raise AssertionError(f"[게이트1] 최상위 def 중복: {node.name} ({seen[node.name]} ↔ {fname})")
            seen[node.name] = fname
            if node.name.startswith("gen_"):
                gen_src[node.name] = "".join(lines[node.lineno - 1 : node.end_lineno])
    defined = set(gen_src)
    registered = set(registered_names)
    assert len(registered_names) == len(registered), (
        f"[게이트2] GENERATORS 중복 등록: {[n for n in registered if registered_names.count(n) > 1]}"
    )
    assert registered <= defined, f"[게이트2] 정의 없는 등록: {sorted(registered - defined)}"
    assert defined <= registered, f"[게이트2] 등록 안 된 gen_*(무음 미생성): {sorted(defined - registered)}"
    return gen_src


def _check_parity(problems, problems_en):
    ko = {p["id"]: p for p in problems}
    en = {p["id"]: p for p in problems_en}
    assert set(ko) == set(en), (
        f"[게이트3] 한/영 id 불일치: ko만 {sorted(set(ko) - set(en))[:5]} / en만 {sorted(set(en) - set(ko))[:5]}"
    )
    for pid, k in ko.items():
        e = en[pid]
        for field in ("difficulty", "groupId", "code"):
            assert k.get(field) == e.get(field), (
                f"[게이트3] {pid} {field} 불일치: ko={k.get(field)} en={e.get(field)}"
            )
        ka = _digits(k["choices"][k["answerIndex"]])
        ea = _digits(e["choices"][e["answerIndex"]])
        if ka and ea:  # 둘 다 숫자 정답일 때만(단위어는 언어별로 다른 게 정상)
            assert ka == ea, f"[게이트3] {pid} 정답 숫자 불일치: ko={ka} en={ea}"


def _check_constraints(problems):
    path = HERE / "difficulty_constraints.json"
    if not path.exists():
        return
    fam_diff = defaultdict(set)
    for p in problems:
        m = _GID.match(p["groupId"])
        if m:
            fam_diff[m.group(1)].add(int(m.group(2)))
    for lo, hi in json.load(open(path, encoding="utf-8"))["constraints"]:
        if lo not in fam_diff or hi not in fam_diff:
            continue  # 한쪽이 은행에서 빠지면(블록리스트 등) 제약도 쉼
        assert max(fam_diff[lo]) < min(fam_diff[hi]), (
            f"[게이트4] 난이도 순서 위반: {lo}(d{max(fam_diff[lo])}) < {hi}(d{min(fam_diff[hi])}) 이어야 함"
        )


def _report_explanation(problems):
    misses = [
        p["id"]
        for p in problems
        if _digits(p["choices"][p["answerIndex"]])
        and _digits(p["choices"][p["answerIndex"]]) not in _digits(p["explanation"])
    ]
    if misses:
        print(f"  보고5 · 정답 숫자가 해설에 안 보임(확인 권장): {len(misses)}건 — {misses[:6]}")


def _report_verification(gen_src):
    bare = sorted(n for n, s in gen_src.items() if "assert" not in s and "rejected" not in s)
    print(f"  보고6 · 독립 검산 없는 제너레이터: {len(bare)}/{len(gen_src)} (목표 0)")
    if bare:
        print(f"          {', '.join(bare[:8])}{' …' if len(bare) > 8 else ''}")


def _report_coverage(problems):
    cov = defaultdict(int)
    for p in problems:
        cov[(p["area"], p["difficulty"])] += 1
    print("  보고7 · 영역×난이도 커버리지 (문항 수):")
    print("          " + " ".join(f"d{d:<3}" for d in range(1, 11)))
    for area in AREA_ORDER:
        row = " ".join(f"{cov[(area, d)]:<4}" for d in range(1, 11))
        thin = [f"d{d}" for d in range(1, 11) if cov[(area, d)] < 4]
        print(f"    {area[:12]:12} {row}" + (f"  ← 얇음: {','.join(thin)}" if thin else ""))


def _skeleton(s):
    """문장에서 숫자를 지워 '유형 골격'만 남긴다(파라미터 변형끼리는 같은 골격)."""
    return re.sub(r"\s+", " ", re.sub(r"\d+", "N", s)).strip()


def _jaccard(a, b):
    return len(a & b) / len(a | b) if (a | b) else 0.0


def _family_sigs(problems):
    """유형(family)별 지문: 정답값 집합·개념 태그 집합·대표 문장 골격."""
    sig = {}
    for p in problems:
        f = _GID.match(p["groupId"]).group(1)
        d = sig.setdefault(f, {"area": p["area"], "ans": set(), "concepts": set(), "skel": None})
        ans = p["choices"][p["answerIndex"]]
        d["ans"].add(_digits(ans) or ans)
        d["concepts"].update(p.get("concepts", []))
        if d["skel"] is None:
            d["skel"] = _skeleton(p["statement"])
    return sig


def _pairwise(problems):
    """같은 영역 유형쌍의 (정답겹침, 개념겹침, 문장유사) — 한 번만 계산해 게이트·보고가 공유."""
    sig = list(_family_sigs(problems).items())
    out = []
    for i in range(len(sig)):
        fa, da = sig[i]
        for j in range(i + 1, len(sig)):
            fb, db = sig[j]
            if da["area"] != db["area"]:
                continue
            ao = _jaccard(da["ans"], db["ans"])
            co = _jaccard(da["concepts"], db["concepts"])
            sk = SequenceMatcher(None, da["skel"] or "", db["skel"] or "").ratio()
            out.append((fa, fb, ao, co, sk))
    return out


def _check_duplicates(pairs):
    """치명: 개념·정답·문장이 모두 유사한 유형쌍(사실상 같은 문제를 두 번 만든 것)."""
    allow = set()
    ap = HERE / "duplicate_allowlist.json"
    if ap.exists():
        allow = {tuple(sorted(x)) for x in json.load(open(ap, encoding="utf-8")).get("pairs", [])}
    dups = [
        (fa, fb, ao, co, sk)
        for fa, fb, ao, co, sk in pairs
        if co >= DUP_CONCEPT and ao >= DUP_ANSWER and sk >= DUP_SKEL and tuple(sorted((fa, fb))) not in allow
    ]
    assert not dups, "[게이트5] 사실상 중복 유형:\n" + "\n".join(
        f"  {fa} ↔ {fb} (정답 {ao:.0%}·개념 {co:.0%}·문장 {sk:.0%})" for fa, fb, ao, co, sk in dups
    ) + "\n  → 한쪽을 blocklist.txt로 제거하거나, 의도된 형제면 duplicate_allowlist.json의 pairs에 등록"


def _report_diversity(problems, pairs):
    cell = defaultdict(set)
    for p in problems:
        cell[(p["area"], p["difficulty"])].add(_GID.match(p["groupId"]).group(1))
    total_types = len({_GID.match(p["groupId"]).group(1) for p in problems})
    print(f"  보고8b · 유형 다양성 지도 (영역×난이도 = 서로 다른 유형 수 · 총 {total_types}유형):")
    print("          " + " ".join(f"d{d:<3}" for d in range(1, 11)))
    for area in AREA_ORDER:
        row = " ".join(f"{len(cell[(area, d)]):<4}" for d in range(1, 11))
        thin = [f"d{d}" for d in range(1, 11) if 0 < len(cell[(area, d)]) <= 2]
        print(f"    {area[:12]:12} {row}" + (f"  ← 유형 얇음: {','.join(thin)}" if thin else ""))
    watch = sorted(
        ((fa, fb, sk) for fa, fb, ao, co, sk in pairs if co >= WATCH_CONCEPT and sk >= WATCH_SKEL),
        key=lambda x: -x[2],
    )
    if watch:
        print(f"  보고9 · 중복 주의 유형쌍 {len(watch)}건(같은 개념+유사 문장 — 형제 사다리면 정상):")
        for fa, fb, sk in watch[:8]:
            print(f"          {fa} ↔ {fb} (문장 {sk:.0%})")


def run_checks(problems, problems_en, generators):
    gen_src = _check_defs([g.__name__ for g in generators])
    _check_parity(problems, problems_en)
    _check_constraints(problems)
    pairs = _pairwise(problems)  # 유형쌍 유사도 1회 계산 → 게이트·보고 공유
    _check_duplicates(pairs)
    print("품질 게이트 통과 (중복정의·등록정합·한/영대칭·난이도제약·유형중복)")
    _report_explanation(problems)
    _report_verification(gen_src)
    _report_coverage(problems)
    _report_diversity(problems, pairs)
