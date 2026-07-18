#!/usr/bin/env python3
"""딱풀 문제 넘버링 체계 — 방법(template)마다 계층 코드 부여.

코드 형식: AA-BB-CC-DD-SS
  AA 영역(2) · BB 유형(2) · CC 방법(2) · DD 난이도(2) · SS 일련번호(2, 숫자만 다른 변형)
동영상은 앞 6자리(AA-BB-CC = 방법)에 붙는다 — 난이도·숫자가 달라도 방법이 같으면 한 영상.

유형(BB)은 개념 태그/키 키워드로 분류한다(투명·조정 가능). 매칭 안 되면 99(기타)로 떨어지니
리뷰에서 0이 되도록 키워드를 보강한다.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(ROOT, "..", "..", "app", "src", "main", "assets", "problems_generated.json")

AREA_CODE = {
    "NUMBER_OPERATION": "10",
    "CHANGE_RELATION": "20",
    "SHAPE_MEASUREMENT": "30",
    "DATA_POSSIBILITY": "40",
}

# 영역별 유형(BB): (코드, 이름, [키워드]). 위에서부터 첫 매칭. 키워드는 방법key + 개념태그에 대해 검사.
TYPES = {
    "NUMBER_OPERATION": [
        ("01", "수 만들기·자리값", ["자리값", "자릿값", "카드", "cards", "crypt", "복면산", "riddle", "revdiff", "narciss", "벌레먹은", "brokensum"]),
        ("02", "약수·공약수", ["약수", "공약수", "divcount", "divsum", "gcd", "aliquot", "sigma", "소수", "소인수", "primepick", "makesquare", "totient", "factzero", "완전수", "서로소"]),
        ("03", "배수·공배수", ["배수", "공배수", "multcond", "multrange", "commrange", "leapyear", "윤년", "incexc", "포함배제"]),
        ("04", "나머지·합동", ["나머지", "remain", "leftover", "divrem", "crt", "중국인", "modpow", "거듭제곱", "lasttwo", "unitcycle", "일의 자리", "주기", "leasttoshare"]),
        ("05", "특수 합·곱", ["gauss", "연속 자연수 합", "oddsum", "홀수의 합", "제곱수", "maxprod", "곱 최대", "sumprod", "합과 곱", "마방진", "repunit", "곱셈 패턴"]),
        ("06", "문장제 추론", ["legs", "가정하여", "excess", "과부족", "mincoin", "거스름", "fracwhole", "부분과 전체", "percentof", "백분율", "bookread", "reverseop", "거꾸로", "역연산", "addend", "가르기", "consec", "연속수", "가운데", "midpt", "중간값", "pyramid", "promise", "약속"]),
        ("07", "경로·전략", ["lattice", "최단 경로", "weigh", "3분할", "저울"]),
    ],
    "CHANGE_RELATION": [
        ("01", "규칙·수열 찾기", ["규칙 찾기", "일정하게", "seq", "계차", "pattern", "반복 규칙", "cycle", "반복 주기", "geoseq", "등비 규칙", "fib", "피보나치", "squarenum", "사각수", "trinum", "삼각수", "numline", "digitpos", "자릿수 블록", "funcinv", "대응 규칙"]),
        ("02", "등차·등비수열", ["등차", "등비", "arithnth", "arithsum", "geonth", "geosum", "n번째", "수열의 합", "quadseq", "prodsum", "cubesum", "recur", "점화식", "compose", "fibsum", "pow2", "2배씩"]),
        ("03", "비·비례·농도", ["비례", "비", "unitprice", "recipe", "ratio", "농도", "concn", "mixture", "gear", "톱니", "seesaw", "시소", "반비례", "dblsale", "할인", "subst", "치환", "단위 바꾸기"]),
        ("04", "속력·따라잡기", ["속력", "meet", "만남", "candle", "따라잡기", "frog", "train", "기차", "roundtrip", "평균 속력", "거속시"]),
        ("05", "시간·간격·달력", ["시간", "timedur", "log", "간격", "tree", "간격 문제", "calweek", "달력", "dow", "요일", "clockstrike", "clockgain", "cups", "lcmbus", "주기"]),
        ("06", "일·전략·나이", ["work", "일의 양", "tank", "일률", "age", "나이", "sumdiff", "합과 차", "transfer", "주고받기", "josephus", "nim", "필승", "배수 남기기", "diophantine", "부정방정식", "trans", "이행성", "순서 추론", "stampfrob", "우표", "mergecandy", "불변량", "pyramidmax", "기여 횟수"]),
    ],
    "SHAPE_MEASUREMENT": [
        ("01", "넓이(모눈·둘러싸기)", ["넓이", "gridtilt", "둘러싸기", "gridhard", "gridtri", "gridpara", "gridtrap", "grid", "모눈", "sqarea", "areamax", "pick", "픽의", "simarea", "닮음"]),
        ("02", "둘레·측정", ["둘레", "rectperim", "border", "테두리", "match", "성냥", "tri", "변 공유"]),
        ("03", "각도", ["각도", "clockang", "clockmin", "polyang", "interiorangle", "polyext", "외각", "triangleangle", "내각"]),
        ("04", "입체·겉넓이·부피", ["겉넓이", "boxsurface", "cubesurf", "부피", "conevolume", "prismparts", "입체", "polyhedron", "다면체", "euler", "오일러", "cubenet", "전개도", "dist3d", "공간 좌표"]),
        ("05", "쌓기나무·공간지각", ["쌓기나무", "cube", "cubetiny", "cubestack", "cubemid", "cubestackeasy", "paintcube", "spacediag", "공간 대각선", "diagcells"]),
        ("06", "도형 개수 세기", ["개수", "rectcount", "trianglefan", "trianglefanx", "gridsquares", "polydiag", "대각선", "diagcross", "diagregions", "gcdtile", "lcmsquare", "gcdtile"]),
        ("07", "대칭·거울", ["대칭", "foldcut", "symaxis", "mirror", "거울", "gridtiny", "grideasy", "gridrect", "foldpieces", "접어 자르기"]),
        # tricount는 02의 "tri" 부분일치에 먼저 걸려 오분류되므로 method_codes.json에 30-06-07로 사전 배정됨.
        ("08", "경로·반사", ["billiard", "반사"]),
    ],
    "DATA_POSSIBILITY": [
        ("01", "경우의 수·곱의 원리", ["곱의 원리", "outfit", "cases", "coinflip", "passcode", "twodigit", "electpair", "coincomb", "diceprod", "dicesum", "gift"]),
        ("02", "순서 세기·순열", ["순서", "순열", "lineup", "perm", "circperm", "원순열", "necklace", "염주", "multiperm", "위치", "position", "htorder", "zigzag", "교대 배열"]),
        ("03", "조합·나누어 세기", ["조합", "choose", "handshake", "악수", "handrev", "league", "numsplit", "starsbars", "중복조합", "partition", "분할", "setpartition", "stairs", "tribstairs", "계단"]),
        ("04", "평균·자료 읽기", ["평균", "avgbasic", "avgchg", "avgneed", "wavg", "chartavg", "missscore", "median", "중앙값", "mode", "최빈값", "자료", "dataread", "barchart", "tablediff", "chart"]),
        ("05", "확률", ["확률", "simpleprob", "atleastprob", "여사건", "derange", "교란", "fairgame", "가능성 비교", "fairsplit", "공정한 분배"]),
        ("06", "논리·전략·불변량", ["truthone", "진실", "pigeon", "비둘기집", "parity", "불변량", "balance", "저울", "knockout", "tourney", "토너먼트", "hanoi", "하노이", "collatz", "lights", "catalan", "setboth", "포함배제", "logicgrid", "논리 소거", "surepick", "최악의 경우", "liarcount", "자기 지시", "pascalodd", "홀짝 패턴"]),
    ],
}


def classify(area, key, concepts):
    hay = (key + " " + " ".join(concepts)).lower()
    for code, name, kws in TYPES[area]:
        if any(kw.lower() in hay for kw in kws):
            return code, name
    return "99", "기타"


def main():
    probs = json.load(open(GEN))["problems"]
    # 방법 단위 수집
    methods = {}
    for p in probs:
        m = re.match(r"g-gen-(.+)-(\d+)$", p.get("groupId", ""))
        if not m:
            continue
        key = m.group(1)
        methods.setdefault(key, {"area": p["area"], "diff": int(m.group(2)), "concepts": p.get("concepts", [])})

    # 유형별로 방법 코드(CC) 부여 — 유형 안에서 key 알파벳 순 01,02,...
    rows = []
    unmatched = []
    by_type = {}
    for key, v in methods.items():
        aa = AREA_CODE[v["area"]]
        bb, bname = classify(v["area"], key, v["concepts"])
        if bb == "99":
            unmatched.append((v["area"], key, v["concepts"]))
        by_type.setdefault((aa, bb), []).append(key)

    method_code = {}
    for (aa, bb), keys in by_type.items():
        for i, key in enumerate(sorted(keys), start=1):
            method_code[key] = (aa, bb, f"{i:02d}")

    for key, v in sorted(methods.items(), key=lambda kv: method_code[kv[0]]):
        aa, bb, cc = method_code[key]
        dd = f"{v['diff']:02d}"
        rows.append((f"{aa}-{bb}-{cc}-{dd}", key, v["area"]))

    print(f"방법 총 {len(methods)} · 미분류(99) {len(unmatched)}")
    if unmatched:
        print("=== 미분류 ===")
        for a, k, c in unmatched:
            print(f"  {a} {k} {c}")
    print("\n=== 코드 배정 (앞부분) ===")
    for code, key, area in rows[:40]:
        print(f"{code}  {key:18} {area}")

    # method_code 매핑 저장 (매니페스트·JSON 주입에 사용)
    out = {key: f"{aa}-{bb}-{cc}" for key, (aa, bb, cc) in method_code.items()}
    json.dump(out, open(os.path.join(ROOT, "method_codes.json"), "w"), ensure_ascii=False, indent=1)
    print(f"\nmethod_codes.json 저장 ({len(out)} 방법)")


if __name__ == "__main__":
    main()
