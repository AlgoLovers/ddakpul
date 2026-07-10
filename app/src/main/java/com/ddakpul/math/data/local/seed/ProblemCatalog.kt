package com.ddakpul.math.data.local.seed

import com.ddakpul.math.domain.model.Answer
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.Mistake
import com.ddakpul.math.domain.model.Problem

/**
 * 앱에 내장되는 초등 4학년 2학기 사고력 수학 문제은행(사전 생성, 실시간 생성 금지).
 *
 * 난이도 1~5가 모두 존재하도록 구성해 추천 알고리즘이 어느 난이도로 이동해도 그룹을 찾을 수 있게 한다.
 * 그룹(`groupId`)이 추천 단위이며, 해설(`explanation`)은 각 그룹 대표문제에만 둔다.
 *
 * LargeClass 억제: 로직 없는 선언적 콘텐츠 목록이라 크기가 복잡도를 뜻하지 않는다.
 * 무결성은 ProblemCatalogTest가 지키고, 콘텐츠가 더 커지면 JSON 에셋으로 분리한다(ROADMAP).
 */
@Suppress("LargeClass")
object ProblemCatalog {
    private fun mc(
        id: String,
        area: MathArea,
        difficulty: Int,
        groupId: String,
        concepts: List<String>,
        statement: String,
        choices: List<String>,
        answerIndex: Int,
        explanation: String? = null,
        mistakes: List<Mistake> = emptyList(),
    ): Problem =
        Problem(
            id = id,
            area = area,
            conceptTags = concepts,
            difficulty = difficulty,
            groupId = groupId,
            statement = statement,
            choices = choices,
            answer = Answer(answerIndex),
            explanation = explanation,
            commonMistakes = mistakes,
        )

    val problems: List<Problem> =
        buildList {
            // ── 난이도 1 · 수와 연산(세 자리 덧셈·뺄셈, 몸풀기) ─────────────────────────

            // ── 난이도 2 · 도형과 측정(각도 기초) ─────────────────────────────────────
            add(
                mc(
                    id = "geo2-01",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 2,
                    groupId = "g-geo-angle-2",
                    concepts = listOf("각도", "직각"),
                    statement = "직각은 몇 도일까요?",
                    choices = listOf("45도", "90도", "180도", "360도"),
                    answerIndex = 1,
                    explanation = "직각은 90도예요. 평각(일직선)은 180도, 한 바퀴는 360도랍니다.",
                    mistakes =
                        listOf(
                            Mistake(2, "180도는 평각(일직선)이에요. 직각은 그 절반인 90도."),
                        ),
                ),
            )
            add(
                mc(
                    id = "geo2-02",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 2,
                    groupId = "g-geo-angle-2",
                    concepts = listOf("각도", "시계"),
                    statement = "시계가 정확히 3시를 가리킬 때, 긴바늘과 짧은바늘이 이루는 작은 각은?",
                    choices = listOf("30도", "60도", "90도", "120도"),
                    answerIndex = 2,
                ),
            )
            add(
                mc(
                    id = "geo2-03",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 2,
                    groupId = "g-geo-angle-2",
                    concepts = listOf("각도", "평각"),
                    statement = "일직선이 이루는 각(평각)은 몇 도일까요?",
                    choices = listOf("90도", "180도", "270도", "360도"),
                    answerIndex = 1,
                ),
            )

            // ── 난이도 2 · 자료와 가능성(막대그래프 읽기) ──────────────────────────────
            add(
                mc(
                    id = "data2-01",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 2,
                    groupId = "g-data-graph-2",
                    concepts = listOf("막대그래프"),
                    statement = "항목별 크기를 막대의 길이로 나타내어 비교하는 그래프는 무엇일까요?",
                    choices = listOf("꺾은선그래프", "막대그래프", "그림그래프", "원그래프"),
                    answerIndex = 1,
                    explanation = "막대의 길이로 수량을 비교하는 그래프가 막대그래프예요.",
                ),
            )
            add(
                mc(
                    id = "data2-02",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 2,
                    groupId = "g-data-graph-2",
                    concepts = listOf("자료 해석"),
                    statement = "학생 20명 중 축구 8명, 야구 5명, 농구 7명이 좋아해요. 가장 많이 좋아하는 운동은?",
                    choices = listOf("축구", "야구", "농구", "모두 같다"),
                    answerIndex = 0,
                ),
            )

            // ── 난이도 3 · 도형과 측정(삼각형) ────────────────────────────────────────
            add(
                mc(
                    id = "geo3-01",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 3,
                    groupId = "g-geo-triangle-3",
                    concepts = listOf("삼각형의 종류"),
                    statement = "세 각이 모두 60도인 삼각형을 무엇이라고 할까요?",
                    choices = listOf("직각삼각형", "정삼각형", "둔각삼각형", "이등변삼각형"),
                    answerIndex = 1,
                    explanation = "세 각이 모두 같으면(각각 60도) 세 변도 모두 같은 정삼각형이에요.",
                ),
            )
            add(
                mc(
                    id = "geo3-02",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 3,
                    groupId = "g-geo-triangle-3",
                    concepts = listOf("삼각형의 종류", "이등변삼각형"),
                    statement = "두 변의 길이가 같은 삼각형을 무엇이라고 할까요?",
                    choices = listOf("정삼각형", "이등변삼각형", "직각삼각형", "예각삼각형"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "정삼각형은 '세 변'이 모두 같아요. '두 변'만 같으면 이등변삼각형이에요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "geo3-03",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 3,
                    groupId = "g-geo-triangle-3",
                    concepts = listOf("삼각형의 종류", "둔각"),
                    statement = "한 각이 90도보다 큰 삼각형을 무엇이라고 할까요?",
                    choices = listOf("예각삼각형", "직각삼각형", "둔각삼각형", "정삼각형"),
                    answerIndex = 2,
                ),
            )

            // ── 난이도 3 · 변화와 관계(수의 규칙) ────────────────────────────────────
            add(
                mc(
                    id = "rel3-01",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 3,
                    groupId = "g-rel-pattern-3",
                    concepts = listOf("규칙 찾기", "등차"),
                    statement = "2, 4, 6, 8, … 다음에 올 수는?",
                    choices = listOf("9", "10", "12", "11"),
                    answerIndex = 1,
                    explanation = "2씩 커지는 규칙이에요. 8 다음은 10.",
                ),
            )
            add(
                mc(
                    id = "rel3-02",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 3,
                    groupId = "g-rel-pattern-3",
                    concepts = listOf("규칙 찾기", "배수"),
                    statement = "3, 6, 12, 24, … 다음에 올 수는?",
                    choices = listOf("36", "48", "30", "46"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "일정하게 더하는 규칙이 아니라 2배씩 커지는 규칙이에요. 24×2=48."),
                        ),
                ),
            )
            add(
                mc(
                    id = "rel3-03",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 3,
                    groupId = "g-rel-pattern-3",
                    concepts = listOf("규칙 찾기", "제곱수"),
                    statement = "1, 4, 9, 16, … 다음에 올 수는?",
                    choices = listOf("20", "25", "24", "21"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "1², 2², 3², 4²…로 커지는 제곱수예요. 다음은 5²=25."),
                        ),
                ),
            )

            // ── 난이도 4 · 도형과 측정(넓이·둘레) ─────────────────────────────────────
            add(
                mc(
                    id = "geo4-01",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 4,
                    groupId = "g-geo-area-4",
                    concepts = listOf("넓이와 둘레", "비교 사고"),
                    statement = "둘레가 24cm로 같은 정사각형과 직사각형(가로 8cm)이 있어요. 정사각형의 넓이는 직사각형보다 몇 cm² 더 넓을까요?",
                    choices = listOf("0cm²", "4cm²", "8cm²", "16cm²"),
                    answerIndex = 1,
                    explanation = "정사각형은 한 변 6cm라 넓이 36cm². 직사각형은 가로 8, 세로 4라 32cm². 둘레가 같아도 정사각형이 가장 넓어요.",
                    mistakes =
                        listOf(
                            Mistake(0, "둘레가 같다고 넓이도 같은 건 아니에요. 직접 구해서 비교해요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "geo4-02",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 4,
                    groupId = "g-geo-area-4",
                    concepts = listOf("넓이", "배 관계 사고"),
                    statement = "정사각형 모양 밭의 각 변을 2배로 늘리면 넓이는 몇 배가 될까요?",
                    choices = listOf("2배", "3배", "4배", "8배"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(0, "변이 2배면 가로도 2배, 세로도 2배 — 넓이는 2×2=4배예요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "geo4-03",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 4,
                    groupId = "g-geo-area-4",
                    concepts = listOf("둘레", "비 사고"),
                    statement = "가로와 세로의 비가 3:2인 직사각형의 둘레가 30cm예요. 가로는 몇 cm일까요?",
                    choices = listOf("6cm", "9cm", "10cm", "12cm"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "6cm는 세로예요. 가로+세로=15를 3:2로 나누면 9와 6."),
                        ),
                ),
            )

            // ── 난이도 4 · 변화와 관계(대응 관계) ────────────────────────────────────
            add(
                mc(
                    id = "rel4-01",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 4,
                    groupId = "g-rel-relation-4",
                    concepts = listOf("대응 관계", "곱셈"),
                    statement = "사탕이 한 봉지에 5개씩 들어 있어요. 4봉지에는 모두 몇 개일까요?",
                    choices = listOf("9개", "20개", "15개", "25개"),
                    answerIndex = 1,
                    explanation = "봉지 수 × 5 = 사탕 수. 4 × 5 = 20개예요.",
                    mistakes =
                        listOf(
                            Mistake(0, "5+4를 했어요. '한 봉지에 5개씩'이니 곱해야 해요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "rel4-02",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 4,
                    groupId = "g-rel-relation-4",
                    concepts = listOf("대응 관계", "속력 기초"),
                    statement = "한 시간에 12km를 가는 자전거는 3시간 동안 몇 km를 갈까요?",
                    choices = listOf("15km", "36km", "24km", "30km"),
                    answerIndex = 1,
                ),
            )
            add(
                mc(
                    id = "rel4-03",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 4,
                    groupId = "g-rel-relation-4",
                    concepts = listOf("대응 관계", "식으로 나타내기"),
                    statement = "봉지 수가 1일 때 사탕 5개, 2일 때 10개, 3일 때 15개예요. 봉지 수(□)와 사탕 수(△)의 관계는?",
                    choices = listOf("△ = □ + 5", "△ = □ × 5", "△ = □ − 5", "△ = □ × 2"),
                    answerIndex = 1,
                ),
            )

            // ── 난이도 4 · 자료와 가능성(평균) ────────────────────────────────────────
            add(
                mc(
                    id = "data4-01",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 4,
                    groupId = "g-data-average-4",
                    concepts = listOf("평균", "거꾸로 생각하기"),
                    statement = "세 번의 시험 평균이 80점이었어요. 네 번째 시험을 본 뒤 평균이 85점이 되었다면 네 번째 시험 점수는?",
                    choices = listOf("85점", "90점", "95점", "100점"),
                    answerIndex = 3,
                    explanation = "네 번 합은 85×4=340, 세 번 합은 80×3=240. 차이 340−240=100점이 네 번째 점수예요.",
                    mistakes =
                        listOf(
                            Mistake(1, "평균이 5점 올랐다고 5점만 더 받은 게 아니에요. 합으로 비교해요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "data4-02",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 4,
                    groupId = "g-data-average-4",
                    concepts = listOf("평균", "거꾸로 생각하기"),
                    statement = "다섯 수의 평균이 20이에요. 이 중 하나를 뺐더니 남은 네 수의 평균이 18이 되었어요. 뺀 수는?",
                    choices = listOf("20", "24", "28", "38"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(0, "합으로 비교해요. 100−72=28."),
                        ),
                ),
            )
            add(
                mc(
                    id = "data4-03",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 4,
                    groupId = "g-data-average-4",
                    concepts = listOf("평균", "거꾸로 생각하기"),
                    statement = "어떤 수 4개의 평균이 6이에요. 이 수들의 합은 얼마일까요?",
                    choices = listOf("10", "24", "6", "18"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "평균+개수(6+4)가 아니에요. 합 = 평균 × 개수 = 6 × 4 = 24."),
                        ),
                ),
            )

            // ── 난이도 5 · 수와 연산(사고력·거꾸로 생각하기) ──────────────────────────
            add(
                mc(
                    id = "num5-01",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 5,
                    groupId = "g-num-logic-5",
                    concepts = listOf("거꾸로 생각하기", "혼합 계산"),
                    statement = "어떤 수에 7을 더한 뒤 3을 곱했더니 30이 되었어요. 어떤 수는?",
                    choices = listOf("3", "4", "5", "7"),
                    answerIndex = 0,
                    explanation = "거꾸로 풀어요. 30 ÷ 3 = 10, 10 − 7 = 3. 어떤 수는 3이에요.",
                    mistakes =
                        listOf(
                            Mistake(1, "30에서 곱셈을 먼저 되돌려야 해요. 나누기(÷3)부터 하고 빼기(−7)를 해요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "num5-02",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 5,
                    groupId = "g-num-logic-5",
                    concepts = listOf("연속하는 수", "논리"),
                    statement = "연속한 세 자연수의 합이 24예요. 가장 작은 수는?",
                    choices = listOf("6", "7", "8", "9"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(2, "24 ÷ 3 = 8은 '가운데' 수예요. 가장 작은 수는 그보다 1 작은 7."),
                        ),
                ),
            )
            add(
                mc(
                    id = "num5-03",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 5,
                    groupId = "g-num-logic-5",
                    concepts = listOf("규칙적인 합"),
                    statement = "1부터 10까지 자연수를 모두 더하면?",
                    choices = listOf("45", "55", "50", "54"),
                    answerIndex = 1,
                ),
            )

            // ── 난이도 5 · 도형과 측정(입체·각의 합) ──────────────────────────────────
            add(
                mc(
                    id = "geo5-01",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 5,
                    groupId = "g-geo-solid-5",
                    concepts = listOf("정육면체", "면"),
                    statement = "정육면체의 면은 모두 몇 개일까요?",
                    choices = listOf("4개", "6개", "8개", "12개"),
                    answerIndex = 1,
                    explanation = "정육면체는 면 6개, 모서리 12개, 꼭짓점 8개예요.",
                    mistakes =
                        listOf(
                            Mistake(2, "8개는 '꼭짓점' 수예요. '면'은 6개랍니다."),
                        ),
                ),
            )
            add(
                mc(
                    id = "geo5-02",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 5,
                    groupId = "g-geo-solid-5",
                    concepts = listOf("정육면체", "모서리"),
                    statement = "정육면체의 모서리는 모두 몇 개일까요?",
                    choices = listOf("6개", "8개", "12개", "4개"),
                    answerIndex = 2,
                ),
            )
            add(
                mc(
                    id = "geo5-03",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 5,
                    groupId = "g-geo-solid-5",
                    concepts = listOf("삼각형의 각의 합"),
                    statement = "삼각형 세 각의 크기를 모두 더하면?",
                    choices = listOf("90도", "180도", "270도", "360도"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(3, "360도는 사각형 네 각의 합이에요. 삼각형은 180도."),
                        ),
                ),
            )

            // ═══════════ 확충분 — 그룹당 문항 밀도 상향 (규칙5가 실제로 작동하도록) ═══════════

            // ── 난이도 2 · 도형과 측정 추가 ──────────────────────────────────────────
            add(
                mc(
                    id = "geo2-04",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 2,
                    groupId = "g-geo-angle-2",
                    concepts = listOf("각도", "직각"),
                    statement = "직각을 똑같이 반으로 나누면 한 각은 몇 도일까요?",
                    choices = listOf("30도", "45도", "60도", "90도"),
                    answerIndex = 1,
                ),
            )
            add(
                mc(
                    id = "geo2-05",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 2,
                    groupId = "g-geo-angle-2",
                    concepts = listOf("각도", "시계"),
                    statement = "시계가 정확히 6시를 가리킬 때, 두 바늘이 이루는 각은?",
                    choices = listOf("90도", "120도", "180도", "360도"),
                    answerIndex = 2,
                ),
            )

            // ── 난이도 2 · 자료와 가능성 추가 ────────────────────────────────────────
            add(
                mc(
                    id = "data2-03",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 2,
                    groupId = "g-data-graph-2",
                    concepts = listOf("막대그래프"),
                    statement = "막대그래프에서 막대의 길이가 나타내는 것은 무엇일까요?",
                    choices = listOf("항목의 순서", "수량의 크기", "항목의 색깔", "조사한 날짜"),
                    answerIndex = 1,
                ),
            )
            add(
                mc(
                    id = "data2-04",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 2,
                    groupId = "g-data-graph-2",
                    concepts = listOf("자료 해석"),
                    statement = "학생 30명 중 사과 12명, 배 8명, 포도 10명이 좋아해요. 두 번째로 많이 좋아하는 과일은?",
                    choices = listOf("사과", "배", "포도", "알 수 없다"),
                    answerIndex = 2,
                ),
            )

            // ── 난이도 3 · 삼각형 추가 ───────────────────────────────────────────────
            add(
                mc(
                    id = "geo3-04",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 3,
                    groupId = "g-geo-triangle-3",
                    concepts = listOf("이등변삼각형", "각"),
                    statement = "이등변삼각형에서 크기가 서로 같은 것은?",
                    choices = listOf("세 각 모두", "두 각", "세 변 모두", "같은 것이 없다"),
                    answerIndex = 1,
                ),
            )
            add(
                mc(
                    id = "geo3-05",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 3,
                    groupId = "g-geo-triangle-3",
                    concepts = listOf("삼각형의 종류", "직각"),
                    statement = "한 각이 90도인 삼각형을 무엇이라고 할까요?",
                    choices = listOf("예각삼각형", "직각삼각형", "둔각삼각형", "정삼각형"),
                    answerIndex = 1,
                ),
            )

            // ── 난이도 3 · 규칙 추가 ─────────────────────────────────────────────────
            add(
                mc(
                    id = "rel3-04",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 3,
                    groupId = "g-rel-pattern-3",
                    concepts = listOf("규칙 찾기", "등차"),
                    statement = "5, 10, 15, 20, … 다음에 올 수는?",
                    choices = listOf("22", "25", "30", "24"),
                    answerIndex = 1,
                ),
            )
            add(
                mc(
                    id = "rel3-05",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 3,
                    groupId = "g-rel-pattern-3",
                    concepts = listOf("규칙 찾기", "나눗셈 규칙"),
                    statement = "81, 27, 9, 3, … 다음에 올 수는?",
                    choices = listOf("0", "1", "2", "3"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "일정하게 빼는 규칙이 아니라 3으로 나누는 규칙이에요. 3÷3=1."),
                        ),
                ),
            )

            // ── 난이도 3 · 꺾은선그래프 (4-2 단원, 신규 그룹) ────────────────────────
            add(
                mc(
                    id = "line3-01",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 3,
                    groupId = "g-data-line-3",
                    concepts = listOf("꺾은선그래프"),
                    statement = "하루 동안의 기온처럼 시간에 따라 변하는 양을 나타내기 좋은 그래프는?",
                    choices = listOf("막대그래프", "그림그래프", "꺾은선그래프", "원그래프"),
                    answerIndex = 2,
                    explanation = "변화하는 모습을 선의 기울기로 볼 수 있는 꺾은선그래프가 좋아요. 막대그래프는 크기 비교에 좋아요.",
                ),
            )
            add(
                mc(
                    id = "line3-02",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 3,
                    groupId = "g-data-line-3",
                    concepts = listOf("꺾은선그래프", "자료 해석"),
                    statement = "꺾은선그래프에서 선이 가장 가파르게 올라간 구간은 무엇을 뜻할까요?",
                    choices = listOf("변화가 없다", "가장 많이 늘어났다", "가장 적게 늘어났다", "줄어들었다"),
                    answerIndex = 1,
                ),
            )
            add(
                mc(
                    id = "line3-03",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 3,
                    groupId = "g-data-line-3",
                    concepts = listOf("꺾은선그래프", "물결선"),
                    statement = "꺾은선그래프에서 물결선(≈)을 사용하는 까닭은?",
                    choices = listOf("예쁘게 꾸미려고", "필요 없는 부분을 줄여서 나타내려고", "선을 두껍게 그리려고", "눈금을 없애려고"),
                    answerIndex = 1,
                ),
            )

            // ── 난이도 4 · 넓이·둘레 추가 ────────────────────────────────────────────
            add(
                mc(
                    id = "geo4-04",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 4,
                    groupId = "g-geo-area-4",
                    concepts = listOf("정사각형의 둘레", "거꾸로 생각하기"),
                    statement = "둘레가 24cm인 정사각형의 한 변은 몇 cm일까요?",
                    choices = listOf("4cm", "6cm", "8cm", "12cm"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(3, "24÷2=12로 풀었어요. 정사각형 변은 4개이니 24÷4=6이에요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "geo4-05",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 4,
                    groupId = "g-geo-area-4",
                    concepts = listOf("넓이", "거꾸로 생각하기"),
                    statement = "넓이가 36cm²인 정사각형의 둘레는 몇 cm일까요?",
                    choices = listOf("18cm", "24cm", "36cm", "144cm"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(2, "넓이 36에서 먼저 한 변(6cm)을 찾고, 그다음 둘레(6×4)를 구해요."),
                        ),
                ),
            )

            // ── 난이도 4 · 사각형 (4-2 단원, 신규 그룹) ──────────────────────────────
            add(
                mc(
                    id = "quad4-01",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 4,
                    groupId = "g-geo-quad-4",
                    concepts = listOf("사각형의 종류", "마름모"),
                    statement = "네 변의 길이가 모두 같은 사각형을 무엇이라고 할까요?",
                    choices = listOf("사다리꼴", "마름모", "직사각형", "평행사변형"),
                    answerIndex = 1,
                    explanation = "네 변이 모두 같으면 마름모예요. 네 각이 모두 직각이면 직사각형, 둘 다 만족하면 정사각형이랍니다.",
                ),
            )
            add(
                mc(
                    id = "quad4-02",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 4,
                    groupId = "g-geo-quad-4",
                    concepts = listOf("사각형의 종류", "직사각형"),
                    statement = "네 각이 모두 직각인 사각형을 무엇이라고 할까요?",
                    choices = listOf("마름모", "사다리꼴", "직사각형", "평행사변형"),
                    answerIndex = 2,
                ),
            )
            add(
                mc(
                    id = "quad4-03",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 4,
                    groupId = "g-geo-quad-4",
                    concepts = listOf("사각형의 종류", "사다리꼴"),
                    statement = "평행한 변이 한 쌍이라도 있는 사각형을 무엇이라고 할까요?",
                    choices = listOf("사다리꼴", "마름모", "오각형", "이등변삼각형"),
                    answerIndex = 0,
                ),
            )

            // ── 난이도 4 · 대응 관계 추가 ────────────────────────────────────────────
            add(
                mc(
                    id = "rel4-04",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 4,
                    groupId = "g-rel-relation-4",
                    concepts = listOf("대응 관계", "곱셈"),
                    statement = "한 상자에 연필이 12자루씩 들어 있어요. 5상자에는 모두 몇 자루일까요?",
                    choices = listOf("17자루", "50자루", "60자루", "55자루"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(0, "12+5를 했어요. '한 상자에 12자루씩'이니 곱해야 해요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "rel4-05",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 4,
                    groupId = "g-rel-relation-4",
                    concepts = listOf("대응 관계", "식으로 나타내기"),
                    statement = "△ = □ × 4 의 관계일 때, □가 7이면 △는 얼마일까요?",
                    choices = listOf("11", "24", "28", "32"),
                    answerIndex = 2,
                ),
            )

            // ── 난이도 4 · 평균 추가 ─────────────────────────────────────────────────
            add(
                mc(
                    id = "data4-04",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 4,
                    groupId = "g-data-average-4",
                    concepts = listOf("평균", "성질 사고"),
                    statement = "네 수의 평균이 7이에요. 네 수에 각각 2씩 더하면 평균은 얼마가 될까요?",
                    choices = listOf("7", "8", "9", "15"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(0, "모든 수가 2씩 커지면 평균도 그만큼 커져요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "data4-05",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 4,
                    groupId = "g-data-average-4",
                    concepts = listOf("평균", "거꾸로 생각하기"),
                    statement = "세 수의 평균이 10이에요. 두 수가 8과 12라면 나머지 한 수는?",
                    choices = listOf("10", "30", "9", "11"),
                    answerIndex = 0,
                    mistakes =
                        listOf(
                            Mistake(1, "30은 세 수의 합이에요. 합 30에서 8과 12를 빼야 해요."),
                        ),
                ),
            )

            // ── 난이도 5 · 사고력 추가 ───────────────────────────────────────────────
            add(
                mc(
                    id = "num5-04",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 5,
                    groupId = "g-num-logic-5",
                    concepts = listOf("거꾸로 생각하기", "혼합 계산"),
                    statement = "어떤 수에서 5를 뺀 뒤 4로 나눴더니 6이 되었어요. 어떤 수는?",
                    choices = listOf("19", "24", "29", "34"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(0, "거꾸로 풀 때는 나눈 것을 곱하고(6×4=24), 뺀 것을 다시 더해요(24+5=29)."),
                        ),
                ),
            )
            add(
                mc(
                    id = "num5-05",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 5,
                    groupId = "g-num-logic-5",
                    concepts = listOf("합과 차", "논리"),
                    statement = "두 수의 합이 20이고 차가 4예요. 두 수 중 큰 수는?",
                    choices = listOf("8", "10", "12", "16"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(0, "8은 작은 수예요. 큰 수 = (합+차)÷2 = (20+4)÷2 = 12."),
                        ),
                ),
            )

            // ── 난이도 5 · 입체 추가 ─────────────────────────────────────────────────
            add(
                mc(
                    id = "geo5-04",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 5,
                    groupId = "g-geo-solid-5",
                    concepts = listOf("정육면체", "꼭짓점"),
                    statement = "정육면체의 꼭짓점은 모두 몇 개일까요?",
                    choices = listOf("6개", "8개", "12개", "4개"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(2, "12개는 '모서리' 수예요. 꼭짓점은 8개랍니다."),
                        ),
                ),
            )
            add(
                mc(
                    id = "geo5-05",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 5,
                    groupId = "g-geo-solid-5",
                    concepts = listOf("사각형의 각의 합"),
                    statement = "사각형 네 각의 크기를 모두 더하면?",
                    choices = listOf("180도", "270도", "360도", "540도"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(0, "180도는 삼각형 세 각의 합이에요. 사각형은 삼각형 2개로 나뉘니 360도."),
                        ),
                ),
            )

            // ── 난이도 5 · 등호와 규칙 심화 (변화와 관계, 신규 그룹) ─────────────────
            add(
                mc(
                    id = "eq5-01",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 5,
                    groupId = "g-rel-equal-5",
                    concepts = listOf("등호와 동치", "식 세우기"),
                    statement = "13 + □ = 20 − 2 일 때, □에 들어갈 수는?",
                    choices = listOf("3", "5", "7", "9"),
                    answerIndex = 1,
                    explanation = "등호(=)는 양쪽이 같다는 뜻이에요. 오른쪽 20−2=18을 먼저 계산하고, 13+□=18에서 □=5.",
                    mistakes =
                        listOf(
                            Mistake(2, "20−13=7로 풀었어요. 오른쪽 전체(20−2=18)를 먼저 계산해야 해요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "eq5-02",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 5,
                    groupId = "g-rel-equal-5",
                    concepts = listOf("규칙 찾기", "증가 규칙"),
                    statement = "1, 2, 4, 7, 11, … 다음에 올 수는?",
                    choices = listOf("14", "15", "16", "18"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(1, "더하는 수가 1, 2, 3, 4로 매번 1씩 커져요. 다음은 11+5=16."),
                        ),
                ),
            )
            add(
                mc(
                    id = "eq5-03",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 5,
                    groupId = "g-rel-equal-5",
                    concepts = listOf("규칙 찾기", "도형 배열"),
                    statement = "성냥개비로 삼각형을 이어 붙여요. 삼각형 1개는 3개, 2개는 5개, 3개는 7개가 필요해요. 삼각형 10개를 만들려면 성냥개비가 몇 개 필요할까요?",
                    choices = listOf("20개", "21개", "23개", "30개"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(3, "3×10=30이 아니에요. 이어 붙이면 변을 함께 쓰니 하나 늘 때마다 2개씩만 늘어요."),
                        ),
                ),
            )
            // ═══════════ 사고력 개편 — 연산 드릴 대신 퍼즐·추론·전략 문제 ═══════════

            // ── 난이도 1 · 수 감각 퍼즐 ──────────────────────────────────────────────
            add(
                mc(
                    id = "sense1-01",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 1,
                    groupId = "g-num-sense-1",
                    concepts = listOf("수 감각", "수 만들기"),
                    statement = "1부터 9까지 숫자 카드가 한 장씩 있어요. 두 장을 골라 만들 수 있는 가장 큰 두 자리 수는?",
                    choices = listOf("91", "98", "99", "89"),
                    answerIndex = 1,
                    explanation = "십의 자리에 가장 큰 9를, 일의 자리에 그다음으로 큰 8을 놓아요. 카드는 한 장씩뿐이라 99는 만들 수 없어요.",
                    mistakes =
                        listOf(
                            Mistake(2, "9 카드는 한 장뿐이라 두 번 쓸 수 없어요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "sense1-02",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 1,
                    groupId = "g-num-sense-1",
                    concepts = listOf("규칙 찾기", "홀수"),
                    statement = "1, 3, 5, 7 … 규칙대로라면 다음 수는?",
                    choices = listOf("8", "9", "10", "11"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "1씩이 아니라 2씩 커지는 규칙이에요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "sense1-03",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 1,
                    groupId = "g-num-sense-1",
                    concepts = listOf("합과 차", "수 감각"),
                    statement = "두 수의 합이 10이고 차가 2예요. 두 수 중 큰 수는?",
                    choices = listOf("4", "5", "6", "7"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(1, "5와 5는 합이 10이지만 차가 0이에요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "sense1-04",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 1,
                    groupId = "g-num-sense-1",
                    concepts = listOf("배수", "조건 사고"),
                    statement = "10보다 크고 20보다 작은 수 중에서 5의 배수는?",
                    choices = listOf("10", "15", "20", "25"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "10은 '10보다 큰 수'가 아니에요."),
                        ),
                ),
            )

            // ── 난이도 1 · 공간·도형 감각 ────────────────────────────────────────────
            add(
                mc(
                    id = "shape1-01",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 1,
                    groupId = "g-shape-sense-1",
                    concepts = listOf("주사위", "공간 감각"),
                    statement = "주사위는 마주 보는 두 면의 눈을 더하면 항상 7이에요. 윗면이 3이면 바닥에 닿은 면의 눈은?",
                    choices = listOf("3", "4", "5", "6"),
                    answerIndex = 1,
                    explanation = "바닥 면은 윗면과 마주 보는 면이니 7−3=4예요.",
                ),
            )
            add(
                mc(
                    id = "shape1-02",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 1,
                    groupId = "g-shape-sense-1",
                    concepts = listOf("접기", "공간 감각"),
                    statement = "정사각형 색종이를 반으로 한 번 접었을 때 나올 수 없는 모양은?",
                    choices = listOf("직사각형", "삼각형", "원", "모두 나올 수 있다"),
                    answerIndex = 2,
                ),
            )
            add(
                mc(
                    id = "shape1-03",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 1,
                    groupId = "g-shape-sense-1",
                    concepts = listOf("자르기", "도형 분할"),
                    statement = "정사각형 종이를 대각선을 따라 한 번 자르면 어떤 도형이 몇 개 생길까요?",
                    choices = listOf("삼각형 2개", "사각형 2개", "삼각형 4개", "원 2개"),
                    answerIndex = 0,
                ),
            )
            add(
                mc(
                    id = "shape1-04",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 1,
                    groupId = "g-shape-sense-1",
                    concepts = listOf("시계", "시간 감각"),
                    statement = "시계의 긴바늘이 한 바퀴를 다 돌면 시간이 얼마나 지난 걸까요?",
                    choices = listOf("1분", "30분", "60분", "12시간"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(3, "12시간은 짧은바늘이 한 바퀴 도는 시간이에요."),
                        ),
                ),
            )

            // ── 난이도 1 · 논리 기초 ─────────────────────────────────────────────────
            add(
                mc(
                    id = "logic1-01",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 1,
                    groupId = "g-logic-1",
                    concepts = listOf("논리 추론"),
                    statement = "가위바위보에서 철수는 가위를 냈고, 영희는 철수를 이겼어요. 영희가 낸 것은?",
                    choices = listOf("가위", "바위", "보", "알 수 없다"),
                    answerIndex = 1,
                    explanation = "가위를 이기는 것은 바위예요. 조건에서 답이 하나로 정해져요.",
                ),
            )
            add(
                mc(
                    id = "logic1-02",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 1,
                    groupId = "g-logic-1",
                    concepts = listOf("순서 추론"),
                    statement = "가는 나보다 크고, 나는 다보다 커요. 키가 가장 작은 사람은?",
                    choices = listOf("가", "나", "다", "알 수 없다"),
                    answerIndex = 2,
                ),
            )
            add(
                mc(
                    id = "logic1-03",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 1,
                    groupId = "g-logic-1",
                    concepts = listOf("요일 사고"),
                    statement = "오늘이 수요일이면 3일 뒤는 무슨 요일일까요?",
                    choices = listOf("금요일", "토요일", "일요일", "목요일"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "수요일에서 하나씩 세요: 목, 금, 토."),
                        ),
                ),
            )
            add(
                mc(
                    id = "logic1-04",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 1,
                    groupId = "g-logic-1",
                    concepts = listOf("경우의 수 기초"),
                    statement = "동전 한 개를 던질 때 나올 수 있는 면은 모두 몇 가지일까요?",
                    choices = listOf("1가지", "2가지", "3가지", "4가지"),
                    answerIndex = 1,
                ),
            )

            // ── 난이도 2 · 수 퍼즐 ───────────────────────────────────────────────────
            add(
                mc(
                    id = "puzzle2-01",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 2,
                    groupId = "g-num-puzzle-2",
                    concepts = listOf("연속수", "수 감각"),
                    statement = "연속한 두 자연수의 합이 15예요. 둘 중 큰 수는?",
                    choices = listOf("7", "8", "9", "10"),
                    answerIndex = 1,
                    explanation = "15의 절반은 7.5 — 그 양옆의 7과 8이에요. 검산: 7+8=15.",
                ),
            )
            add(
                mc(
                    id = "puzzle2-02",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 2,
                    groupId = "g-num-puzzle-2",
                    concepts = listOf("수 만들기", "순서 사고"),
                    statement = "숫자 카드 1, 2, 3을 모두 한 번씩 써서 만든 세 자리 수 중 둘째로 작은 수는?",
                    choices = listOf("123", "132", "213", "231"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "123은 가장 작은 수예요. 문제는 '둘째로' 작은 수를 물었어요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "puzzle2-03",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 2,
                    groupId = "g-num-puzzle-2",
                    concepts = listOf("돈 계산", "고르기 전략"),
                    statement = "10원, 50원, 100원 동전이 한 개씩 있어요. 이 중 두 개만 골라 만들 수 있는 가장 큰 금액은?",
                    choices = listOf("60원", "110원", "150원", "160원"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(3, "160원은 세 개를 모두 썼을 때예요. 두 개만 골라야 해요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "puzzle2-04",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 2,
                    groupId = "g-num-puzzle-2",
                    concepts = listOf("수의 성질", "홀짝"),
                    statement = "홀수와 홀수를 더하면 항상 어떤 수가 될까요?",
                    choices = listOf("홀수", "짝수", "알 수 없다", "0"),
                    answerIndex = 1,
                ),
            )

            // ── 난이도 2 · 경우의 수 기초 ────────────────────────────────────────────
            add(
                mc(
                    id = "case2-01",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 2,
                    groupId = "g-case-2",
                    concepts = listOf("경우의 수"),
                    statement = "티셔츠 2벌과 바지 2벌이 있어요. 티셔츠와 바지를 하나씩 골라 입는 방법은 모두 몇 가지일까요?",
                    choices = listOf("2가지", "4가지", "6가지", "8가지"),
                    answerIndex = 1,
                    explanation = "티셔츠마다 바지를 2가지씩 짝지을 수 있어요. 2×2=4가지.",
                    mistakes =
                        listOf(
                            Mistake(0, "티셔츠 수만 세면 안 돼요. 티셔츠마다 바지 조합을 세요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "case2-02",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 2,
                    groupId = "g-case-2",
                    concepts = listOf("경우의 수", "줄 세우기"),
                    statement = "세 친구가 한 줄로 서요. 철수가 맨 앞에 서기로 했다면 줄을 서는 방법은 모두 몇 가지일까요?",
                    choices = listOf("1가지", "2가지", "3가지", "6가지"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(3, "6가지는 철수 자리가 정해지지 않았을 때예요. 남은 두 명만 순서를 바꿔요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "case2-03",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 2,
                    groupId = "g-case-2",
                    concepts = listOf("경우의 수"),
                    statement = "서로 다른 동전 두 개를 동시에 던질 때 나올 수 있는 경우는 모두 몇 가지일까요?",
                    choices = listOf("2가지", "3가지", "4가지", "6가지"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(1, "(앞,뒤)와 (뒤,앞)은 서로 다른 경우예요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "case2-04",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 2,
                    groupId = "g-case-2",
                    concepts = listOf("경우의 수", "최댓값"),
                    statement = "주사위 두 개를 던져 나온 눈의 합이 가장 클 때, 그 합은 얼마일까요?",
                    choices = listOf("6", "10", "12", "36"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(3, "36은 곱한 값이에요. 합은 6+6=12."),
                        ),
                ),
            )

            // ── 난이도 3 · 수 사고 (다리 세기·연속수·나머지) ─────────────────────────
            add(
                mc(
                    id = "think3-01",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 3,
                    groupId = "g-num-think-3",
                    concepts = listOf("다리 세기", "가정하여 풀기"),
                    statement = "오리와 강아지가 모두 5마리 있고 다리를 세어 보니 14개예요. 강아지는 몇 마리일까요?",
                    choices = listOf("1마리", "2마리", "3마리", "4마리"),
                    answerIndex = 1,
                    explanation = "모두 오리라면 다리는 10개. 실제보다 4개 부족한데, 강아지는 오리보다 다리가 2개 많으니 4÷2=2마리가 강아지예요.",
                    mistakes =
                        listOf(
                            Mistake(2, "강아지 3마리면 다리가 4×3+2×2=16개라 너무 많아요. 검산해 봐요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "think3-02",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 3,
                    groupId = "g-num-think-3",
                    concepts = listOf("연속수", "짝수"),
                    statement = "연속한 세 짝수의 합이 24예요. 가장 큰 수는?",
                    choices = listOf("8", "10", "12", "14"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "8은 가운데 수예요(6, 8, 10). 가장 큰 수는 10."),
                        ),
                ),
            )
            add(
                mc(
                    id = "think3-03",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 3,
                    groupId = "g-num-think-3",
                    concepts = listOf("나눗셈", "거꾸로 생각하기"),
                    statement = "어떤 수를 4로 나눴더니 몫이 7이고 나머지가 2였어요. 어떤 수는?",
                    choices = listOf("28", "30", "26", "32"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "나머지 2를 더하는 걸 잊었어요. 4×7+2=30."),
                        ),
                ),
            )
            add(
                mc(
                    id = "think3-04",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 3,
                    groupId = "g-num-think-3",
                    concepts = listOf("숫자 세기", "빠짐없이 세기"),
                    statement = "1부터 20까지 수를 차례로 쓸 때 숫자 '1'은 모두 몇 번 쓰게 될까요?",
                    choices = listOf("11번", "12번", "13번", "10번"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "11에는 1이 두 번 들어가요. 1, 10, 11(두 번), 12~19까지 세어 봐요."),
                        ),
                ),
            )

            // ── 난이도 3 · 분수 사고 ─────────────────────────────────────────────────
            add(
                mc(
                    id = "fracth3-01",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 3,
                    groupId = "g-frac-think-3",
                    concepts = listOf("분수", "부분의 부분"),
                    statement = "피자의 3/4이 남아 있었는데, 그중 절반을 먹었어요. 이제 남은 피자는 전체의 얼마일까요?",
                    choices = listOf("1/4", "3/8", "1/2", "1/8"),
                    answerIndex = 1,
                    explanation = "남아 있던 3/4의 절반이 남았으니 3/4의 반 = 3/8이에요. 8조각으로 나눠 생각하면 6조각 중 3조각이 남은 셈.",
                ),
            )
            add(
                mc(
                    id = "fracth3-02",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 3,
                    groupId = "g-frac-think-3",
                    concepts = listOf("분수 비교"),
                    statement = "1/2, 2/5, 3/10 중에서 가장 큰 수는?",
                    choices = listOf("1/2", "2/5", "3/10", "모두 같다"),
                    answerIndex = 0,
                    mistakes =
                        listOf(
                            Mistake(2, "분자가 크다고 큰 수가 아니에요. 10칸으로 나누면 5칸, 4칸, 3칸이에요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "fracth3-03",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 3,
                    groupId = "g-frac-think-3",
                    concepts = listOf("분수", "거꾸로 생각하기"),
                    statement = "물통에 물이 1/3만큼 차 있어요. 6L를 더 부었더니 2/3이 되었어요. 물통에 가득 담으면 몇 L일까요?",
                    choices = listOf("12L", "18L", "9L", "6L"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "6L는 전체의 1/3(2/3−1/3)이에요. 전체는 6×3=18L."),
                        ),
                ),
            )
            add(
                mc(
                    id = "fracth3-04",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 3,
                    groupId = "g-frac-think-3",
                    concepts = listOf("분수", "전체 구하기"),
                    statement = "리본 전체의 1/4 길이가 5cm예요. 리본 전체 길이는?",
                    choices = listOf("9cm", "20cm", "15cm", "25cm"),
                    answerIndex = 1,
                ),
            )

            // ── 난이도 3 · 도형 사고 ─────────────────────────────────────────────────
            add(
                mc(
                    id = "geoth3-01",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 3,
                    groupId = "g-geo-think-3",
                    concepts = listOf("도형 세기", "빠짐없이 세기"),
                    statement = "정사각형을 가로·세로 3칸씩 9칸으로 나눴어요. 이 그림에서 찾을 수 있는 크고 작은 정사각형은 모두 몇 개일까요?",
                    choices = listOf("9개", "10개", "13개", "14개"),
                    answerIndex = 3,
                    explanation = "1칸짜리 9개, 4칸짜리(2×2) 4개, 9칸짜리(3×3) 1개 — 모두 14개예요. 크기별로 나눠 세면 빠뜨리지 않아요.",
                    mistakes =
                        listOf(
                            Mistake(0, "가장 작은 정사각형만 셌어요. 2×2, 3×3짜리도 정사각형이에요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "geoth3-02",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 3,
                    groupId = "g-geo-think-3",
                    concepts = listOf("시계 각도"),
                    statement = "시계가 3시 30분일 때 두 바늘이 이루는 작은 쪽 각도는?",
                    choices = listOf("90도", "75도", "60도", "105도"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "짧은바늘은 3에 딱 있지 않아요. 30분이 지나 3과 4의 중간에 있어요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "geoth3-03",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 3,
                    groupId = "g-geo-think-3",
                    concepts = listOf("둘레와 넓이", "두 단계 사고"),
                    statement = "둘레가 20cm인 정사각형의 넓이는 몇 cm²일까요?",
                    choices = listOf("20cm²", "25cm²", "16cm²", "100cm²"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(3, "둘레 20을 한 변으로 착각했어요. 한 변은 20÷4=5cm."),
                        ),
                ),
            )
            add(
                mc(
                    id = "geoth3-04",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 3,
                    groupId = "g-geo-think-3",
                    concepts = listOf("삼각형 각의 합"),
                    statement = "삼각형의 한 각은 90도, 다른 한 각은 30도예요. 나머지 한 각은?",
                    choices = listOf("30도", "45도", "60도", "90도"),
                    answerIndex = 2,
                ),
            )

            // ── 난이도 3 · 관계 사고 (간격·달력·나이) ────────────────────────────────
            add(
                mc(
                    id = "relth3-01",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 3,
                    groupId = "g-rel-think-3",
                    concepts = listOf("간격 문제"),
                    statement = "길이 20m인 길 한쪽에 처음부터 끝까지 5m 간격으로 나무를 심어요. 나무는 몇 그루 필요할까요?",
                    choices = listOf("4그루", "5그루", "6그루", "3그루"),
                    answerIndex = 1,
                    explanation = "간격은 20÷5=4개지만, 나무는 양쪽 끝에도 심으니 4+1=5그루예요.",
                    mistakes =
                        listOf(
                            Mistake(0, "간격 수와 나무 수는 달라요. 처음 나무 1그루를 더해요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "relth3-02",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 3,
                    groupId = "g-rel-think-3",
                    concepts = listOf("달력 사고"),
                    statement = "어떤 달의 1일이 금요일이면 그달 15일은 무슨 요일일까요?",
                    choices = listOf("목요일", "금요일", "토요일", "일요일"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "15일은 1일에서 딱 14일(2주) 뒤라 같은 요일이에요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "relth3-03",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 3,
                    groupId = "g-rel-think-3",
                    concepts = listOf("나이 문제", "합과 차"),
                    statement = "형은 동생보다 4살 많고, 두 사람 나이의 합은 20살이에요. 형은 몇 살일까요?",
                    choices = listOf("8살", "10살", "12살", "14살"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(1, "10살은 합의 절반이에요. 형은 절반보다 차의 절반(2살)만큼 많아요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "relth3-04",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 3,
                    groupId = "g-rel-think-3",
                    concepts = listOf("변화율 사고"),
                    statement = "길이 10cm인 양초가 1분에 2cm씩 타요. 3분 뒤 남은 길이는?",
                    choices = listOf("6cm", "4cm", "8cm", "2cm"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "6cm는 '탄' 길이예요. 남은 길이는 10−6=4cm."),
                        ),
                ),
            )

            // ── 난이도 4 · 수 사고 심화 ──────────────────────────────────────────────
            add(
                mc(
                    id = "master4-01",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 4,
                    groupId = "g-num-master-4",
                    concepts = listOf("수 만들기", "순서 전략"),
                    statement = "숫자 카드 2, 5, 7, 8 중 세 장을 골라 만든 세 자리 수 중에서 둘째로 큰 수는?",
                    choices = listOf("875", "872", "857", "852"),
                    answerIndex = 1,
                    explanation = "가장 큰 수는 875. 둘째로 큰 수는 앞 두 자리는 그대로 두고 일의 자리만 그다음 카드로 바꾼 872예요.",
                    mistakes =
                        listOf(
                            Mistake(0, "875는 가장 큰 수예요. '둘째로' 큰 수를 물었어요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "master4-02",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 4,
                    groupId = "g-num-master-4",
                    concepts = listOf("나머지", "최댓값 사고"),
                    statement = "어떤 수를 6으로 나눴더니 몫이 8이었어요. 나머지가 가장 클 때 어떤 수는?",
                    choices = listOf("48", "53", "54", "50"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(2, "나머지는 나누는 수 6보다 작아야 하니 최대 5예요. 6×8+5=53."),
                        ),
                ),
            )
            add(
                mc(
                    id = "master4-03",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 4,
                    groupId = "g-num-master-4",
                    concepts = listOf("곱과 합", "수 찾기"),
                    statement = "두 수의 곱이 36이고 합이 13이에요. 둘 중 큰 수는?",
                    choices = listOf("6", "9", "12", "18"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "6×6은 곱이 36이지만 합이 12예요. 곱이 36인 짝을 차례로 검사해요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "master4-04",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 4,
                    groupId = "g-num-master-4",
                    concepts = listOf("규칙적인 합", "거꾸로 생각하기"),
                    statement = "1 + 2 + 3 + … + □ = 45. □에 들어갈 수는?",
                    choices = listOf("8", "9", "10", "11"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(2, "1부터 10까지 더하면 55예요. 45는 1부터 9까지의 합."),
                        ),
                ),
            )

            // ── 난이도 4 · 경우·전략 사고 ────────────────────────────────────────────
            add(
                mc(
                    id = "dmaster4-01",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 4,
                    groupId = "g-data-master-4",
                    concepts = listOf("토너먼트", "발상 전환"),
                    statement = "8팀이 토너먼트(지면 바로 탈락)로 우승팀을 가려요. 우승팀이 나올 때까지 전체 경기 수는?",
                    choices = listOf("6경기", "7경기", "8경기", "15경기"),
                    answerIndex = 1,
                    explanation = "한 경기마다 꼭 한 팀이 탈락해요. 우승팀 빼고 7팀이 탈락해야 하니 경기도 7번이에요.",
                    mistakes =
                        listOf(
                            Mistake(2, "팀 수와 경기 수는 달라요. '탈락하는 팀 수'로 생각해 봐요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "dmaster4-02",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 4,
                    groupId = "g-data-master-4",
                    concepts = listOf("리그전", "중복 없이 세기"),
                    statement = "4팀이 서로 한 번씩 빠짐없이 경기하는 리그전의 전체 경기 수는?",
                    choices = listOf("4경기", "6경기", "8경기", "12경기"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(3, "4×3=12는 같은 경기를 두 번 센 거예요. 반으로 나눠요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "dmaster4-03",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 4,
                    groupId = "g-data-master-4",
                    concepts = listOf("경우의 수"),
                    statement = "서로 다른 주사위 두 개를 던져 눈의 합이 7이 되는 경우는 모두 몇 가지일까요?",
                    choices = listOf("3가지", "5가지", "6가지", "7가지"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(0, "(1,6)과 (6,1)은 다른 경우예요. 1+6부터 6+1까지 모두 세요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "dmaster4-04",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 4,
                    groupId = "g-data-master-4",
                    concepts = listOf("악수 문제", "중복 없이 세기"),
                    statement = "5명이 서로 빠짐없이 한 번씩 악수하면 악수는 모두 몇 번 하게 될까요?",
                    choices = listOf("5번", "10번", "20번", "25번"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(2, "5×4=20은 같은 악수를 두 번 센 거예요."),
                        ),
                ),
            )

            // ── 난이도 5 · 공간 사고 심화 (페인트 정육면체·도형 세기) ────────────────
            add(
                mc(
                    id = "ggen5-01",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 5,
                    groupId = "g-geo-genius-5",
                    concepts = listOf("페인트 정육면체", "공간 사고"),
                    statement = "정육면체 겉면 전체에 페인트를 칠한 뒤, 가로·세로·높이를 3등분해 작은 정육면체 27개로 잘랐어요. 세 면에 페인트가 칠해진 조각은 몇 개일까요?",
                    choices = listOf("6개", "8개", "12개", "27개"),
                    answerIndex = 1,
                    explanation = "세 면이 칠해진 조각은 꼭짓점 자리에 있어요. 정육면체의 꼭짓점은 8개니까 8개예요.",
                    mistakes =
                        listOf(
                            Mistake(0, "6개는 면의 수예요. 세 면이 만나는 곳은 꼭짓점이에요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "ggen5-02",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 5,
                    groupId = "g-geo-genius-5",
                    concepts = listOf("페인트 정육면체", "공간 사고"),
                    statement = "정육면체 겉면 전체에 페인트를 칠한 뒤 27개의 작은 정육면체로 잘랐을 때, 정확히 두 면에만 페인트가 칠해진 조각은 몇 개일까요?",
                    choices = listOf("8개", "12개", "6개", "4개"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "8개는 세 면이 칠해진 꼭짓점 조각이에요. 두 면짜리는 모서리 가운데 — 모서리는 12개."),
                        ),
                ),
            )
            add(
                mc(
                    id = "ggen5-03",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 5,
                    groupId = "g-geo-genius-5",
                    concepts = listOf("페인트 정육면체", "공간 사고"),
                    statement = "정육면체 겉면 전체에 페인트를 칠한 뒤 27개의 작은 정육면체로 잘랐을 때, 한 면도 칠해지지 않은 조각은 몇 개일까요?",
                    choices = listOf("0개", "1개", "3개", "6개"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "한가운데 숨어 있는 조각 1개는 어느 면도 겉으로 드러나지 않았어요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "ggen5-04",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 5,
                    groupId = "g-geo-genius-5",
                    concepts = listOf("도형 세기", "체계적으로 세기"),
                    statement = "정사각형을 가로·세로 4칸씩 16칸으로 나눴어요. 이 그림에서 찾을 수 있는 크고 작은 정사각형은 모두 몇 개일까요?",
                    choices = listOf("16개", "25개", "30개", "32개"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(0, "1칸짜리만 셌어요. 16+9+4+1로 크기별로 더해요."),
                        ),
                ),
            )

            // ── 난이도 5 · 논리 추론 심화 ────────────────────────────────────────────
            add(
                mc(
                    id = "lgen5-01",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 5,
                    groupId = "g-logic-genius-5",
                    concepts = listOf("순서 추론"),
                    statement = "달리기에서 가는 나보다 빨랐고, 다는 가보다 빨랐어요. 2등은 누구일까요?",
                    choices = listOf("가", "나", "다", "알 수 없다"),
                    answerIndex = 0,
                    explanation = "빠른 순서대로 늘어놓으면 다 → 가 → 나. 그래서 2등은 가예요.",
                ),
            )
            add(
                mc(
                    id = "lgen5-02",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 5,
                    groupId = "g-logic-genius-5",
                    concepts = listOf("무게 비교", "단위 바꿔 생각하기"),
                    statement = "사과 1개의 무게는 귤 2개와 같고, 귤 4개의 무게는 배 1개와 같아요. 배 1개는 사과 몇 개와 무게가 같을까요?",
                    choices = listOf("1개", "2개", "4개", "8개"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(2, "배 1개=귤 4개이고, 귤 2개=사과 1개니까 귤 4개=사과 2개예요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "lgen5-03",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 5,
                    groupId = "g-logic-genius-5",
                    concepts = listOf("달력 사고"),
                    statement = "어느 해 3월 1일은 화요일이에요. 같은 해 3월 31일은 무슨 요일일까요?",
                    choices = listOf("수요일", "목요일", "금요일", "화요일"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(3, "28일(4주) 뒤인 29일이 화요일이고, 31일은 그보다 2일 뒤예요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "lgen5-04",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 5,
                    groupId = "g-logic-genius-5",
                    concepts = listOf("진실과 거짓", "경우 나누기"),
                    statement = "유리창을 깬 사람은 가, 나, 다 중 한 명이에요. 가: '저는 안 깼어요', 나: '가가 깼어요', 다: '저는 안 깼어요'. 이 중 한 명만 진실을 말했다면 깬 사람은?",
                    choices = listOf("가", "나", "다", "알 수 없다"),
                    answerIndex = 2,
                    explanation = "다가 깼다고 하면: 가의 말 진실, 나의 말 거짓, 다의 말 거짓 — 진실이 딱 한 명이라 조건에 맞아요. 다른 경우는 진실이 두 명이 돼요.",
                ),
            )

            // ── 난이도 5 · 수 사고 확충 (마방진·약속 연산) ───────────────────────────
            add(
                mc(
                    id = "num5-06",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 5,
                    groupId = "g-num-logic-5",
                    concepts = listOf("마방진"),
                    statement = "1부터 9까지 수를 한 번씩 써서 가로·세로·대각선의 합이 모두 같게 만들면(마방진), 한 줄의 합은 얼마일까요?",
                    choices = listOf("12", "15", "18", "20"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "1부터 9까지 합 45를 세 줄로 똑같이 나누면 45÷3=15예요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "num5-07",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 5,
                    groupId = "g-num-logic-5",
                    concepts = listOf("약속 연산", "규칙 적용"),
                    statement = "새로운 기호 ◎를 '앞 수 × 뒤 수 − 앞 수'로 약속해요. 5◎3의 값은?",
                    choices = listOf("10", "12", "15", "8"),
                    answerIndex = 0,
                    mistakes =
                        listOf(
                            Mistake(2, "5×3=15에서 앞 수 5를 빼는 것까지가 약속이에요."),
                        ),
                ),
            )

            // ── 난이도 4 · 관계 사고 확충 (달팽이·톱니바퀴) ──────────────────────────
            add(
                mc(
                    id = "rel4-06",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 4,
                    groupId = "g-rel-relation-4",
                    concepts = listOf("규칙 사고", "함정 피하기"),
                    statement = "달팽이가 10m 나무 기둥을 올라가요. 낮에는 3m 오르고 밤에는 2m 미끄러져요. 꼭대기에 처음 닿는 것은 며칠째 낮일까요?",
                    choices = listOf("8일째", "9일째", "10일째", "7일째"),
                    answerIndex = 0,
                    mistakes =
                        listOf(
                            Mistake(2, "하루 1m씩만 계산하면 안 돼요. 7일 밤까지 7m, 8일째 낮에 3m를 올라 10m에 먼저 닿아요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "rel4-07",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 4,
                    groupId = "g-rel-relation-4",
                    concepts = listOf("톱니바퀴", "반비례 사고"),
                    statement = "톱니가 20개인 톱니바퀴 A와 10개인 톱니바퀴 B가 맞물려 있어요. A가 1바퀴 돌면 B는 몇 바퀴 돌까요?",
                    choices = listOf("반 바퀴", "1바퀴", "2바퀴", "4바퀴"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(0, "톱니가 적은 바퀴가 더 많이 돌아요. A가 옮긴 톱니 20개 = B의 2바퀴."),
                        ),
                ),
            )
            // ═══════ 심화(5분급) — 연습장에 그리고 따져 봐야 풀리는 다단계 문제 ═══════

            // ── 난이도 3 · 체계적으로 세기 심화 ──────────────────────────────────────
            add(
                mc(
                    id = "deep3-01",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 3,
                    groupId = "g-deep-count-3",
                    concepts = listOf("숫자 세기", "중복 조심"),
                    statement = "1부터 100까지의 수 중에서 숫자 3이 한 번이라도 들어가는 수는 모두 몇 개일까요? (예: 3, 13, 35, 73…)",
                    choices = listOf("10개", "18개", "19개", "20개"),
                    answerIndex = 2,
                    explanation = "일의 자리가 3인 수 10개(3, 13, …, 93)와 삼십대 10개(30~39)를 더하면 20개지만, 33이 두 번 세어졌으니 하나 빼서 19개예요.",
                    mistakes =
                        listOf(
                            Mistake(3, "33을 두 번 세지 않았는지 확인해요. 두 묶음에 모두 들어 있어요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "deep3-02",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 3,
                    groupId = "g-deep-count-3",
                    concepts = listOf("숫자 세기", "자릿수 나누기"),
                    statement = "1쪽부터 50쪽까지 책에 쪽수를 매기려면 숫자를 모두 몇 개 써야 할까요?",
                    choices = listOf("82개", "90개", "91개", "100개"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(0, "한 자리 쪽수(1~9)의 숫자 9개를 빠뜨렸어요. 9 + 41×2 = 91."),
                        ),
                ),
            )
            add(
                mc(
                    id = "deep3-03",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 3,
                    groupId = "g-deep-count-3",
                    concepts = listOf("테두리 세기", "꼭짓점 중복"),
                    statement = "바둑돌을 속이 빈 정사각형 모양으로 한 변에 10개씩 놓으려고 해요. 바둑돌은 모두 몇 개 필요할까요?",
                    choices = listOf("40개", "36개", "38개", "32개"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "10×4=40으로 하면 네 꼭짓점 돌을 두 번 센 거예요. 40−4=36."),
                        ),
                ),
            )
            add(
                mc(
                    id = "deep3-04",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 3,
                    groupId = "g-deep-count-3",
                    concepts = listOf("달력 구조", "가운데 수 사고"),
                    statement = "달력에서 위아래로 나란히 붙은 세 수를 골랐더니 합이 42였어요. 세 수 중 가운데 수는?",
                    choices = listOf("12", "13", "14", "21"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(3, "42÷2가 아니에요. 세 수는 (가운데−7), 가운데, (가운데+7)이라 합이 가운데×3이에요."),
                        ),
                ),
            )

            // ── 난이도 4 · 수 구성 심화 (복면산·카드·조건 찾기) ──────────────────────
            add(
                mc(
                    id = "deep4n-01",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 4,
                    groupId = "g-deep-number-4",
                    concepts = listOf("복면산", "자리값 사고"),
                    statement = "두 자리 수 (AB)와 자리를 바꾼 수 (BA)를 더했더니 132가 되었어요. A+B는 얼마일까요? (A, B는 한 자리 숫자)",
                    choices = listOf("10", "11", "12", "13"),
                    answerIndex = 2,
                    explanation = "(AB)+(BA) = (10A+B)+(10B+A) = 11×(A+B). 11×(A+B)=132이므로 A+B=12예요.",
                    mistakes =
                        listOf(
                            Mistake(1, "132÷12가 아니라 132÷11이에요. 두 수의 합은 항상 11의 배수가 돼요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "deep4n-02",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 4,
                    groupId = "g-deep-number-4",
                    concepts = listOf("수 만들기", "경우 나누기"),
                    statement = "숫자 카드 1, 2, 3, 4를 모두 한 번씩 써서 만든 네 자리 수 중 3200보다 큰 수는 모두 몇 개일까요?",
                    choices = listOf("6개", "8개", "10개", "12개"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(3, "31□□는 3200보다 작아요. 4□□□ 6개 + 34□□ 2개 + 32□□ 2개 = 10개."),
                        ),
                ),
            )
            add(
                mc(
                    id = "deep4n-03",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 4,
                    groupId = "g-deep-number-4",
                    concepts = listOf("조건으로 수 찾기"),
                    statement = "세 자리 수가 있어요. 각 자리 숫자의 합은 14이고, 십의 자리는 5, 백의 자리는 일의 자리의 2배예요. 이 수는?",
                    choices = listOf("653", "356", "554", "635"),
                    answerIndex = 0,
                    mistakes =
                        listOf(
                            Mistake(3, "십의 자리가 5라는 조건을 다시 확인해요. 백+일=9이고 백=일×2이니 백6, 일3."),
                        ),
                ),
            )
            add(
                mc(
                    id = "deep4n-04",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 4,
                    groupId = "g-deep-number-4",
                    concepts = listOf("곱의 성질", "0의 개수"),
                    statement = "1×2×3×…×10을 모두 곱한 수의 끝에는 0이 몇 개 붙어 있을까요?",
                    choices = listOf("1개", "2개", "3개", "4개"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "0은 2×5에서 생겨요. 5와 10(=2×5), 두 번 만들어지니 0도 2개."),
                        ),
                ),
            )

            // ── 난이도 4 · 도형 사고 심화 (분할·둘레 보존·경로) ──────────────────────
            add(
                mc(
                    id = "deep4g-01",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 4,
                    groupId = "g-deep-geo-4",
                    concepts = listOf("둘레 보존", "발상 전환"),
                    statement = "한 변이 10cm인 정사각형 종이의 한 모퉁이에서 한 변이 4cm인 정사각형을 잘라내 L자 모양을 만들었어요. L자 도형의 둘레는?",
                    choices = listOf("32cm", "36cm", "40cm", "48cm"),
                    answerIndex = 2,
                    explanation = "잘라낸 자리의 파인 두 변은 밖으로 밀어내면 원래 변과 똑같이 맞춰져요. 그래서 둘레는 원래 정사각형과 같은 40cm!",
                    mistakes =
                        listOf(
                            Mistake(0, "잘라냈다고 둘레가 줄지 않아요. 파인 부분의 변을 밀어 붙여 보세요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "deep4g-02",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 4,
                    groupId = "g-deep-geo-4",
                    concepts = listOf("평면 분할", "규칙 찾기"),
                    statement = "직선 4개를 그어 평면(종이)을 최대 몇 부분으로 나눌 수 있을까요? (직선 1개면 2부분, 2개면 4부분…)",
                    choices = listOf("8부분", "9부분", "10부분", "11부분"),
                    answerIndex = 3,
                    mistakes =
                        listOf(
                            Mistake(0, "8은 서로 평행하지 않게만 그은 게 아니에요. 새 직선이 기존 직선을 모두 가로지르면 1+1+2+3+4=11."),
                        ),
                ),
            )
            add(
                mc(
                    id = "deep4g-03",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 4,
                    groupId = "g-deep-geo-4",
                    concepts = listOf("접기와 구멍", "공간 사고"),
                    statement = "정사각형 색종이를 반으로 접고 또 반으로 접은 뒤(총 2번), 구멍을 1개 뚫고 펼쳤어요. 구멍은 모두 몇 개일까요?",
                    choices = listOf("1개", "2개", "4개", "8개"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(1, "두 번 접으면 종이가 4겹이에요. 겹마다 구멍이 하나씩 뚫려요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "deep4g-04",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 4,
                    groupId = "g-deep-geo-4",
                    concepts = listOf("최단 경로", "체계적으로 세기"),
                    statement = "가로 2칸, 세로 2칸의 바둑판 모양 길이 있어요. 왼쪽 아래에서 오른쪽 위까지 가장 짧게 가는 길은 모두 몇 가지일까요?",
                    choices = listOf("4가지", "6가지", "8가지", "12가지"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "각 갈림길에 '거기까지 가는 방법 수'를 적어 가며 더해 보세요. 1,2,1 → 1,3,3 → 6."),
                        ),
                ),
            )

            // ── 난이도 4 · 작업·속력·나이 사고 ───────────────────────────────────────
            add(
                mc(
                    id = "deep4w-01",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 4,
                    groupId = "g-deep-work-4",
                    concepts = listOf("일의 양", "단위 시간 사고"),
                    statement = "물탱크를 A 수도만 틀면 6분, B 수도만 틀면 12분에 가득 채워요. 두 수도를 동시에 틀면 몇 분 만에 가득 찰까요?",
                    choices = listOf("3분", "4분", "8분", "9분"),
                    answerIndex = 1,
                    explanation = "1분에 A는 전체의 1/6, B는 1/12을 채워요. 합치면 1분에 1/6+1/12=1/4 — 그래서 4분이면 가득!",
                    mistakes =
                        listOf(
                            Mistake(3, "9분은 6과 12의 평균이에요. 같이 틀면 혼자보다 빨라져야 해요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "deep4w-02",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 4,
                    groupId = "g-deep-work-4",
                    concepts = listOf("나이 문제", "배 관계 변화"),
                    statement = "지금 아버지 나이는 아들의 4배예요. 5년 뒤에는 3배가 돼요. 지금 아들은 몇 살일까요?",
                    choices = listOf("8살", "10살", "12살", "15살"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "검산해요: 아들 8이면 아버지 32, 5년 뒤 13과 37 — 3배가 아니에요. 아들 10이면 40→15와 45로 딱 3배."),
                        ),
                ),
            )
            add(
                mc(
                    id = "deep4w-03",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 4,
                    groupId = "g-deep-work-4",
                    concepts = listOf("자르기 횟수", "간격 사고"),
                    statement = "긴 통나무를 5도막으로 자르려고 해요. 한 번 자르는 데 3분이 걸린다면 모두 몇 분이 걸릴까요?",
                    choices = listOf("15분", "12분", "9분", "18분"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "5도막을 내는 데 필요한 건 4번 자르기예요. 도막 수와 자르는 횟수는 달라요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "deep4w-04",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 4,
                    groupId = "g-deep-work-4",
                    concepts = listOf("만남 문제", "속력 합"),
                    statement = "둘레 400m인 트랙의 같은 지점에서 두 사람이 서로 반대 방향으로 동시에 출발해요. 한 명은 1분에 60m, 다른 한 명은 1분에 40m를 걸어요. 두 사람은 몇 분 뒤 처음 만날까요?",
                    choices = listOf("2분", "4분", "8분", "10분"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(2, "반대 방향이면 두 사람이 좁히는 거리는 1분에 60+40=100m예요."),
                        ),
                ),
            )

            // ── 난이도 5 · 논리 전략 심화 (라벨·저울·계단·거울) ──────────────────────
            add(
                mc(
                    id = "deep5l-01",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 5,
                    groupId = "g-deep-logic-5",
                    concepts = listOf("논리 퍼즐", "라벨 추론"),
                    statement = "세 상자에 각각 '사과', '귤', '사과와 귤'이라는 이름표가 붙어 있는데, 셋 다 잘못 붙어 있어요. '사과와 귤' 상자에서 하나를 꺼냈더니 사과가 나왔어요. 이 상자에 실제로 든 것은?",
                    choices = listOf("사과만", "귤만", "사과와 귤", "알 수 없다"),
                    answerIndex = 0,
                    explanation = "이름표가 전부 틀렸으니 이 상자는 '사과와 귤'이 아니에요. 그런데 사과가 나왔으니 귤만도 아니죠. 남는 답은 사과만!",
                    mistakes =
                        listOf(
                            Mistake(2, "이름표가 '전부' 잘못 붙었다는 조건을 놓쳤어요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "deep5l-02",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 5,
                    groupId = "g-deep-logic-5",
                    concepts = listOf("저울 전략", "3등분 사고"),
                    statement = "겉모양이 똑같은 동전 9개 중 1개만 살짝 가벼운 가짜예요. 양팔저울을 최소 몇 번 써야 가짜를 확실히 찾을 수 있을까요?",
                    choices = listOf("2번", "3번", "4번", "8번"),
                    answerIndex = 0,
                    mistakes =
                        listOf(
                            Mistake(1, "3개씩 세 묶음으로 나누면 1번에 가짜가 든 묶음, 2번째에 가짜 동전을 찾아요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "deep5l-03",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 5,
                    groupId = "g-deep-logic-5",
                    concepts = listOf("경우 나누어 세기", "계단 문제"),
                    statement = "한 번에 1칸 또는 2칸씩 오를 수 있는 4칸 계단이 있어요. 계단을 오르는 서로 다른 방법은 모두 몇 가지일까요?",
                    choices = listOf("4가지", "5가지", "6가지", "8가지"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "1111, 112, 121, 211, 22 — 순서가 다르면 다른 방법이에요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "deep5l-04",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 5,
                    groupId = "g-deep-logic-5",
                    concepts = listOf("거울 사고", "대칭"),
                    statement = "벽시계가 거울에 비쳐 9시 정각처럼 보여요. 실제 시각은 몇 시일까요?",
                    choices = listOf("9시", "3시", "6시", "12시"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "거울은 좌우를 뒤집어요. 12를 기준으로 접었을 때 9시와 겹치는 시각을 찾아요."),
                        ),
                ),
            )

            // ── 난이도 5 · 비율·변화 심화 (기차·시계 바늘·양초) ──────────────────────
            add(
                mc(
                    id = "deep5r-01",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 5,
                    groupId = "g-deep-rate-5",
                    concepts = listOf("기차 문제", "숨은 거리"),
                    statement = "길이 100m인 기차가 1초에 20m씩 달려요. 이 기차가 길이 400m인 다리를 완전히 건너는 데(맨 앞이 들어가서 맨 뒤가 나올 때까지) 몇 초가 걸릴까요?",
                    choices = listOf("20초", "25초", "30초", "5초"),
                    answerIndex = 1,
                    explanation = "기차 맨 뒤까지 다리를 벗어나려면 다리 400m에 기차 길이 100m를 더한 500m를 가야 해요. 500÷20=25초.",
                    mistakes =
                        listOf(
                            Mistake(0, "기차 자신의 길이 100m를 잊었어요. 가야 할 거리는 400+100=500m."),
                        ),
                ),
            )
            add(
                mc(
                    id = "deep5r-02",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 5,
                    groupId = "g-deep-rate-5",
                    concepts = listOf("시계 바늘 사고"),
                    statement = "2시와 3시 사이에 긴바늘과 짧은바늘이 정확히 겹치는 순간이 있어요. 대략 몇 시 몇 분일까요?",
                    choices = listOf("2시 5분쯤", "2시 11분쯤", "2시 15분쯤", "2시 20분쯤"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(2, "긴바늘이 2(10분 자리)에 도착하면 짧은바늘은 이미 조금 더 가 있어요. 따라잡는 지점은 10분보다 조금 뒤."),
                        ),
                ),
            )
            add(
                mc(
                    id = "deep5r-03",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 5,
                    groupId = "g-deep-rate-5",
                    concepts = listOf("나이 문제", "배 관계 변화"),
                    statement = "지금 어머니 나이는 딸의 3배예요. 12년 뒤에는 2배가 돼요. 지금 딸은 몇 살일까요?",
                    choices = listOf("10살", "12살", "14살", "16살"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "검산: 딸 12살이면 어머니 36살, 12년 뒤 24살과 48살 — 딱 2배가 돼요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "deep5r-04",
                    area = MathArea.CHANGE_RELATION,
                    difficulty = 5,
                    groupId = "g-deep-rate-5",
                    concepts = listOf("따라잡기", "차이 줄이기"),
                    statement = "20cm짜리 초는 1시간에 2cm씩, 12cm짜리 초는 1시간에 1cm씩 타요. 동시에 불을 붙이면 몇 시간 뒤 두 초의 길이가 같아질까요?",
                    choices = listOf("4시간", "6시간", "8시간", "10시간"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(0, "길이 차이 8cm가 1시간에 1cm씩 줄어들어요. 8÷1=8시간."),
                        ),
                ),
            )
        }
}
