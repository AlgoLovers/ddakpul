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
 */
object ProblemCatalog {
    private const val GRADE = 4
    private const val SEMESTER = 2

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
            grade = GRADE,
            semester = SEMESTER,
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
            add(
                mc(
                    id = "num1-01",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 1,
                    groupId = "g-num-add-1",
                    concepts = listOf("세 자리 수 덧셈", "받아올림"),
                    statement = "324 + 197 = ?",
                    choices = listOf("511", "521", "515", "621"),
                    answerIndex = 1,
                    explanation = "일의 자리 4+7=11에서 1을 올리고, 십의 자리 2+9+1=12에서 다시 1을 올려 백의 자리 3+1+1=5. 답은 521이에요.",
                    mistakes =
                        listOf(
                            Mistake(0, "받아올림 한 번을 빠뜨렸어요. 자리마다 올라간 1을 꼭 더해요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "num1-02",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 1,
                    groupId = "g-num-add-1",
                    concepts = listOf("세 자리 수 뺄셈", "받아내림"),
                    statement = "705 − 268 = ?",
                    choices = listOf("437", "447", "537", "443"),
                    answerIndex = 0,
                    mistakes =
                        listOf(
                            Mistake(2, "십의 자리에서 백의 자리 받아내림을 하지 않았어요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "num1-03",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 1,
                    groupId = "g-num-add-1",
                    concepts = listOf("세 자리 수 뺄셈", "0에서 받아내림"),
                    statement = "1000 − 645 = ?",
                    choices = listOf("355", "365", "455", "345"),
                    answerIndex = 0,
                ),
            )

            // ── 난이도 2 · 수와 연산(곱셈·나눗셈) ──────────────────────────────────────
            add(
                mc(
                    id = "num2-01",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 2,
                    groupId = "g-num-mul-2",
                    concepts = listOf("두 자리 × 한 자리"),
                    statement = "23 × 4 = ?",
                    choices = listOf("82", "92", "86", "112"),
                    answerIndex = 1,
                    explanation = "20×4=80, 3×4=12를 더하면 92예요. 자리별로 곱한 뒤 합쳐요.",
                    mistakes =
                        listOf(
                            Mistake(0, "3×4=12의 받아올림 1(십의 자리)을 더하지 않았어요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "num2-02",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 2,
                    groupId = "g-num-mul-2",
                    concepts = listOf("두 자리 ÷ 한 자리"),
                    statement = "84 ÷ 6 = ?",
                    choices = listOf("12", "14", "13", "16"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "6×14=84예요. 6×12=72라서 12는 너무 작아요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "num2-03",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 2,
                    groupId = "g-num-mul-2",
                    concepts = listOf("두 자리 × 한 자리"),
                    statement = "17 × 5 = ?",
                    choices = listOf("75", "85", "95", "805"),
                    answerIndex = 1,
                ),
            )

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

            // ── 난이도 3 · 수와 연산(분수) ────────────────────────────────────────────
            add(
                mc(
                    id = "frac3-01",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 3,
                    groupId = "g-num-frac-3",
                    concepts = listOf("분수의 덧셈", "분모가 같은 분수"),
                    statement = "1/5 + 2/5 = ?",
                    choices = listOf("3/5", "3/10", "2/25", "1/2"),
                    answerIndex = 0,
                    explanation = "분모가 같으면 분자끼리만 더해요. 1+2=3이므로 3/5. 분모 5는 그대로 둬요.",
                    mistakes =
                        listOf(
                            Mistake(1, "분모끼리도 더했어요(5+5=10). 분모가 같을 땐 분모는 그대로!"),
                        ),
                ),
            )
            add(
                mc(
                    id = "frac3-02",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 3,
                    groupId = "g-num-frac-3",
                    concepts = listOf("분수와 소수"),
                    statement = "3/4 을 소수로 나타내면?",
                    choices = listOf("0.34", "0.75", "0.4", "0.7"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(0, "분자·분모를 그대로 이어 쓴 게 아니에요. 3÷4=0.75로 계산해요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "frac3-03",
                    area = MathArea.NUMBER_OPERATION,
                    difficulty = 3,
                    groupId = "g-num-frac-3",
                    concepts = listOf("분수의 뺄셈", "1에서 빼기"),
                    statement = "1 − 3/8 = ?",
                    choices = listOf("5/8", "4/8", "3/8", "7/8"),
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
                    concepts = listOf("직사각형의 넓이"),
                    statement = "가로 6cm, 세로 4cm인 직사각형의 넓이는?",
                    choices = listOf("10cm²", "24cm²", "20cm²", "12cm²"),
                    answerIndex = 1,
                    explanation = "직사각형의 넓이는 가로 × 세로예요. 6 × 4 = 24cm².",
                    mistakes =
                        listOf(
                            Mistake(0, "가로+세로(6+4)를 구했어요. 넓이는 더하기가 아니라 곱하기예요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "geo4-02",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 4,
                    groupId = "g-geo-area-4",
                    concepts = listOf("정사각형의 둘레"),
                    statement = "한 변이 5cm인 정사각형의 둘레는?",
                    choices = listOf("10cm", "15cm", "20cm", "25cm"),
                    answerIndex = 2,
                    mistakes =
                        listOf(
                            Mistake(3, "5×5=25는 넓이예요. 둘레는 네 변의 합(5×4=20)이에요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "geo4-03",
                    area = MathArea.SHAPE_MEASUREMENT,
                    difficulty = 4,
                    groupId = "g-geo-area-4",
                    concepts = listOf("직사각형의 둘레"),
                    statement = "가로 8cm, 세로 3cm인 직사각형의 둘레는?",
                    choices = listOf("11cm", "22cm", "24cm", "16cm"),
                    answerIndex = 1,
                    mistakes =
                        listOf(
                            Mistake(2, "8×3=24는 넓이예요. 둘레는 (8+3)×2=22cm."),
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
                    concepts = listOf("평균"),
                    statement = "3, 5, 7의 평균은?",
                    choices = listOf("5", "4", "6", "15"),
                    answerIndex = 0,
                    explanation = "평균은 (모두 더한 값) ÷ (개수)예요. (3+5+7) ÷ 3 = 15 ÷ 3 = 5.",
                    mistakes =
                        listOf(
                            Mistake(3, "합(15)까지만 구했어요. 개수 3으로 나눠야 평균이에요."),
                        ),
                ),
            )
            add(
                mc(
                    id = "data4-02",
                    area = MathArea.DATA_POSSIBILITY,
                    difficulty = 4,
                    groupId = "g-data-average-4",
                    concepts = listOf("평균"),
                    statement = "네 번의 점수 80, 90, 70, 80의 평균은?",
                    choices = listOf("80", "85", "75", "320"),
                    answerIndex = 0,
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
        }
}
