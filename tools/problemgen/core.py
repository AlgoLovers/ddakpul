"""딱풀 문제 생성 공용 인프라 — rng·problems·_emit/add·조사교정·오답·상수.

제너레이터(gen_*.py)와 build.py가 `from core import *`로 쓴다.
rng/rng_en 시드와 소비 순서는 산출 JSON 재현성의 핵심 — 함부로 바꾸지 말 것.
"""
import json
import random
import re
from math import comb, factorial, gcd
from pathlib import Path

from codes import ensure_registry, inject_codes  # 계층 코드(AA-BB-CC-DD-SS) 자동 주입
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


def _fib(k):
    a, b = 1, 1
    for _ in range(k - 1):
        a, b = b, a + b
    return a


# star-import로 _언더스코어 헬퍼까지 내보낸다(제너레이터들이 _eul 등을 직접 쓴다).
__all__ = [n for n in dir() if not n.startswith("__")]
