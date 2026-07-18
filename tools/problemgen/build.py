"""문제은행 빌드 — GENERATORS 순서대로 실행 → 무결성 → blocklist → 코드주입 → 저장.

GENERATORS 순서 = rng 소비 순서 = 산출 재현성. 항목 추가는 끝에, 재배치 금지.
"""
from core import *  # noqa: F401,F403 — 공용 인프라(add·rng·헬퍼·상수)
from gen_number import *  # noqa: F401,F403
from gen_change import *  # noqa: F401,F403
from gen_shape import *  # noqa: F401,F403
from gen_data import *  # noqa: F401,F403



GENERATORS = [
    gen_crt3, gen_fibsum, gen_diagcross, gen_partition,
    gen_league, gen_twodigit, gen_tablediff, gen_unitprice,
    gen_rectperim, gen_interiorangle, gen_prismparts, gen_triangleangle,
    gen_avgbasic, gen_lineup, gen_mode, gen_simpleprob,
    gen_geosum, gen_dist3d, gen_necklace, gen_boxsurface, gen_passcode, gen_symaxis,
    gen_rectdiag, gen_electpair,
    gen_diagregions, gen_barchart, gen_chartavg,
    gen_foldcut, gen_knockout,
    gen_makesquare, gen_compose, gen_euler, gen_atleastprob,
    gen_sigma, gen_recur, gen_conevolume, gen_setpartition,
    gen_lasttwo, gen_cubesum, gen_pick, gen_catalan,
    gen_totient, gen_josephus, gen_spacediag, gen_derange, gen_prodsum,
    gen_quadseq, gen_polyhedron, gen_multiperm,
    gen_diophantine, gen_painted_cube_faces, gen_stars_bars,
    gen_transitivity, gen_repeating_pattern, gen_io_rule,
    gen_midpoint, gen_consecutive_middle, gen_multiple_condition,
    gen_choose_two, gen_data_read,
    gen_aliquot, gen_narcissistic,
    gen_mod_power, gen_lattice_paths, gen_coin_weighing,
    gen_number_split, gen_height_order, gen_position_count, gen_missing_addend,
    gen_lcm_together, gen_consecutive_sum, gen_pigeonhole, gen_missing_score,
    gen_units_cycle, gen_set_both, gen_round_trip,
    gen_handshake, gen_gauss_sum, gen_ratio_share, gen_fraction_whole,
    gen_tournament, gen_change_coins, gen_recipe_ratio, gen_square_area,
    gen_day_of_week, gen_frog_well, gen_odd_sum_square, gen_permutation,
    gen_reverse_diff, gen_leftover_crt, gen_square_numbers, gen_triangular,
    gen_power_of_two, gen_multiples_in_range, gen_common_mult_range, gen_weighted_average,
    gen_coin_flips, gen_dice_product, gen_salt_concentration, gen_percent_of,
    gen_gear_ratio, gen_seesaw, gen_divisor_sum, gen_clock_strikes,
    gen_ratio_three, gen_marble_transfer, gen_least_to_share, gen_tank_fill_drain,
    gen_leap_year_count, gen_average_needed, gen_stacking_cups, gen_number_line_jump,
    gen_double_discount, gen_max_product, gen_gift_exchange, gen_hanoi,
    gen_grid_area_hard,
    gen_median, gen_gcd_bags, gen_lcm_square, gen_collatz,
    gen_fibonacci, gen_prime_pick, gen_gcd_lcm_product,
    gen_mixture, gen_arithmetic_nth, gen_geometric_nth,
    gen_clock_gain, gen_book_reading, gen_train_pass_person,
    gen_reverse_operation, gen_similar_area_ratio, gen_handshake_reverse,
    gen_divisor_from_remainder, gen_diagonal_cells,
    gen_gcd_three, gen_sum_arithmetic_series, gen_tribonacci_stairs, gen_toggle_lights,
    gen_sum_product_pair, gen_time_duration, gen_squares_in_grid, gen_two_sum_diff,
    gen_cryptarithm, gen_chicken_rabbit, gen_excess_deficit, gen_age, gen_trees,
    gen_log, gen_meeting, gen_work, gen_train, gen_pyramid, gen_stairs, gen_grid,
    gen_cycle, gen_calendar, gen_average, gen_border, gen_candle, gen_mirror,
    # v2 확충 — 난이도1 바닥 + 신규 아이디어(다양성)
    gen_digit_cards, gen_sequence_simple, gen_matchsticks, gen_outfits,
    gen_broken_arithmetic, gen_cases, gen_custom_op, gen_sequence_advanced,
    gen_true_false,
    # v2.1 확충 — 도형 난2·자료 난3 빈칸 + 수 감각 다양성
    # (gen_handshake·gen_consecutive_sum·gen_pigeonhole는 v5 신규판이 같은 이름으로 재정의 →
    #  중복 등록 제거. 여기선 등록하지 않고 아래 v5 블록의 등록 하나만 남긴다.)
    gen_triangles_match, gen_dice_sum, gen_remainder,
    # v3 확충 — 유료(난4·5) 깊이: 색칠정육면체·약수개수·수 추리
    gen_painted_cube, gen_divisor_count, gen_number_riddle,
    # v3.1 확충 — 도형 난4 보강 + 등비 다양성
    gen_clock_angle, gen_rectangle_count, gen_geometric_seq,
    # v4 확충 — 경시급 난6·7(불변량·포함배제·님게임) + 도형 대량
    gen_parity_invariant, gen_inclusion_exclusion, gen_nim,
    gen_polygon_angle, gen_polygon_diagonals, gen_clock_minutes,
    gen_rect_area_max, gen_cube_surface,
    # v4.1 확충 — 도형 그림(POLYGON) 부착 + 외각
    gen_polygon_exterior,
    # v4.2 확충 — 쌓기나무(CUBE_STACK 입체 그림, 그림 필수)
    gen_cube_stack,
    # v4.6 확충 — 무료(난2) 작은 쌓기나무: 첫 경험용 그림 문제(무료 체험 비주얼 강화)
    gen_cube_stack_easy,
    # v4.7 확충 — 저난도 그림 밀도↑(난1~3): 그림 문제가 초반부터 자주 나오게
    gen_cube_stack_tiny, gen_grid_tiny, gen_grid_area_easy, gen_cube_stack_mid,
    # v4.3 확충 — 격자 넓이(GRID_POLYGON 그림 필수): 삼각형·평행사변형·사다리꼴·기울어진 도형
    gen_grid_area,
    # v4.4 확충 — 삼각형 개수 세기(TRIANGLE_FAN 그림 필수): 체계적 세기
    gen_shape_count,
    # v4.5 확충 — 주사위 전개도 마주 보는 면(CUBE_NET 그림 필수): 접기 시뮬로 검산
    gen_cube_net,
    # v4.8 확충 — 경시급(난6~7): 저울 3진탐색·원순열·팩토리얼 끝자리 0
    gen_coin_balance, gen_circular_perm, gen_factorial_zeros,
    # v4.9 확충 — 격자 최단경로 장애물 회피(GRID 그림 필수, 난6): DP 검산
    gen_grid_blocked,
    # v5.0 확충 — 콘텐츠 볼륨: 저울 치환·동전 조합·최대공약수 타일(그림)
    gen_balance_substitution, gen_coin_combinations, gen_gcd_tiles,
]

for g in GENERATORS:
    g()

# ── 전역 무결성 자체 검사 ─────────────────────────────────────────────────────
ids = [p["id"] for p in problems]
assert len(ids) == len(set(ids)), "id 중복"
for p in problems:
    assert len(p["choices"]) == 4 and len(set(p["choices"])) == 4, f"보기 오류: {p['id']}"
    assert 0 <= p["answerIndex"] < 4
    assert len(p["explanation"]) >= 20, f"풀이가 없거나 너무 짧음: {p['id']}"
    for m in p["mistakes"]:
        assert m["choiceIndex"] != p["answerIndex"], f"오개념이 정답에 붙음: {p['id']}"
groups = {}
for p in problems:
    groups.setdefault(p["groupId"], []).append(p)
for gid, ps in groups.items():
    assert len(ps) >= 3, f"그룹 {gid} 문항 부족({len(ps)})"
    assert len({p["difficulty"] for p in ps}) == 1 and len({p["area"] for p in ps}) == 1, f"그룹 불일치 {gid}"

# 큐레이션 블록리스트 적용 — 검수에서 제거된 문제는 영구 제외
blockfile = Path(__file__).parent / "blocklist.txt"
blocked = set()
if blockfile.exists():
    for line in blockfile.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            blocked.add(line)
before = len(problems)
problems = [p for p in problems if p["id"] not in blocked]
problems_en = [p for p in problems_en if p["id"] not in blocked]
if blocked:
    print(f"블록리스트 제외: {before - len(problems)}문항 (등록 {len(blocked)}건)")

# ── 계층 코드(AA-BB-CC-DD-SS) 주입 — 재생성 시 code 필드를 항상 재구축한다(codes.py) ──
# method_codes.json을 안정 레지스트리로: 기존 방법 코드는 불변, 신규 family만 추가.
registry, new_methods, unmatched = ensure_registry(problems + problems_en)
if new_methods:
    print(f"신규 방법 코드 배정 {len(new_methods)}건: " + ", ".join(f"{k}={v}" for k, v in new_methods))
if unmatched:
    print(f"⚠️  미분류(99) family {len(unmatched)}건 — taxonomy.py 키워드 보강 필요: {unmatched}")
inject_codes(problems, registry)
inject_codes(problems_en, registry)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"version": 1, "problems": problems}, ensure_ascii=False, indent=1), encoding="utf-8")

# 영어 뱅크 — add(en=...)로 변환된 계열만. 아직 변환 중이라 부분 뱅크.
OUT_EN.write_text(json.dumps({"version": 1, "lang": "en", "problems": problems_en}, ensure_ascii=False, indent=1), encoding="utf-8")
en_cov = len({p["groupId"].replace("g-gen-", "").rsplit("-", 1)[0] for p in problems_en})
print(f"영어 뱅크: {len(problems_en)}문항 · {en_cov}계열 → {OUT_EN.name}")

by_diff = {}
for p in problems:
    by_diff[p["difficulty"]] = by_diff.get(p["difficulty"], 0) + 1
print(f"생성 {stats['generated']}문항 / 기각 {stats['rejected']} / 그룹 {len(groups)}개")
print(f"난이도 분포: {dict(sorted(by_diff.items()))}")
print(f"→ {OUT}")

# ── 품질 게이트(checks.py) — 치명 위반(중복정의·등록누락·한/영 비대칭·난이도 제약)이면 빌드 실패 ──
from checks import run_checks  # noqa: E402 — 데이터 확정 후 검사

run_checks(problems, problems_en, GENERATORS)
