#!/usr/bin/env python3
"""문제은행 품질 게이트 — build.py가 저장 후 자동 호출한다. 치명 위반이면 예외로 멈춘다.

치명(빌드 실패):
  1. 파이프라인 .py 안 최상위 def 중복(뒤 정의가 앞을 무음으로 덮어쓰는 버그 원천)
  2. gen_* 정의 ↔ GENERATORS 등록 불일치(등록 누락 = 무음 미생성)
  3. 한/영 대칭: 같은 id 집합, 같은 difficulty·groupId·code, 같은 숫자 정답
  4. 난이도 순서 제약(difficulty_constraints.json) 위반
     — 예: '규칙을 받아 적용만'(recur)은 '규칙을 스스로 발견'(hanoi·tribstairs)보다 낮아야 한다

보고(비치명, 콘솔):
  5. 정답 숫자가 해설에 안 보이는 문항(해설-정답 불일치 의심)
  6. 독립 검산(assert/기각) 없는 제너레이터 목록 — 솔버 검증 100% 커버리지가 목표
  7. 영역×난이도 커버리지 매트릭스(빈 슬롯·얇은 슬롯 조준용)
"""
import ast
import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIPELINE_FILES = ["core.py", "gen_number.py", "gen_change.py", "gen_shape.py", "gen_data.py", "build.py"]
AREA_ORDER = ["NUMBER_OPERATION", "CHANGE_RELATION", "SHAPE_MEASUREMENT", "DATA_POSSIBILITY"]
_GID = re.compile(r"g-gen-(.+)-(\d+)$")


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


def run_checks(problems, problems_en, generators):
    gen_src = _check_defs([g.__name__ for g in generators])
    _check_parity(problems, problems_en)
    _check_constraints(problems)
    print("품질 게이트 통과 (중복정의·등록정합·한/영대칭·난이도제약)")
    _report_explanation(problems)
    _report_verification(gen_src)
    _report_coverage(problems)
