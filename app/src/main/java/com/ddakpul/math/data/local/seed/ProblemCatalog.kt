package com.ddakpul.math.data.local.seed

import com.ddakpul.math.domain.model.Answer
import com.ddakpul.math.domain.model.FigureType
import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.Mistake
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.model.ProblemFigure

/**
 * 앱에 내장되는 초등 사고력 수학 문제은행(사전 생성, 실시간 생성 금지).
 *
 * 난이도 1~5가 모두 존재하도록 구성해 추천 알고리즘이 어느 난이도로 이동해도 그룹을 찾을 수 있게 한다.
 * 그룹(`groupId`)이 추천 단위이며, 모든 문제가 단계별 풀이(`explanation`)를 보유한다 —
 * 정답만 보여주는 문제는 금지(ProblemCatalogTest가 강제).
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
        figure: ProblemFigure? = null,
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
            figure = figure,
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
                    explanation = "시계 한 바퀴는 360도이고 숫자 칸은 12개이니 한 칸은 360÷12=30도예요. 3시에는 긴바늘이 12, 짧은바늘이 3을 가리켜서 두 바늘 사이가 3칸이에요. 그래서 30×3=90도, 정답은 90도예요.",
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
                    explanation = "종이 모서리 같은 직각(90도) 두 개를 나란히 이어 붙이면 일직선이 돼요. 그래서 평각은 90+90=180도예요. 정답은 180도.",
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
                    explanation = "수를 큰 것부터 줄 세워 비교해 봐요. 축구 8명, 농구 7명, 야구 5명 순서니까 8이 가장 커요. 가장 많이 좋아하는 운동은 축구예요.",
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
                    explanation = "삼각형 이름에는 특징이 숨어 있어요. '이등변'은 두(이) 변의 길이가 같다(등)는 뜻이에요. 세 변이 모두 같으면 정삼각형이고, 두 변만 같으면 이등변삼각형이에요. 정답은 이등변삼각형.",
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
                    explanation = "삼각형은 가장 큰 각을 보고 이름을 붙여요. 세 각이 모두 90도보다 작으면 예각삼각형, 한 각이 딱 90도면 직각삼각형이에요. 한 각이 90도보다 크면(둔각) 둔각삼각형이라고 해요. 정답은 둔각삼각형.",
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
                    explanation = "이웃한 수의 관계를 살펴봐요. 3에서 6은 +3인데 6에서 12는 +6이라 일정하게 더하는 규칙이 아니에요. 대신 3×2=6, 6×2=12, 12×2=24처럼 2배씩 커지는 규칙이에요. 그러니 다음 수는 24×2=48이에요.",
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
                    explanation = "이웃한 수의 차이를 적어 보면 3, 5, 7로 2씩 커지는 규칙이 보여요. 그래서 16 다음은 16+9=25예요. 사실 이 수들은 1×1, 2×2, 3×3, 4×4라서 다음이 5×5=25이기도 해요. 정답은 25.",
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
                    explanation = "작은 수로 먼저 해봐요. 한 변이 1cm인 정사각형은 넓이가 1cm²인데, 변을 2배인 2cm로 늘리면 넓이는 2×2=4cm²가 돼요. 가로도 2배, 세로도 2배가 되니 넓이는 2×2=4배예요. 정답은 4배.",
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
                    explanation = "둘레는 (가로+세로)×2이니 가로+세로=30÷2=15cm예요. 비가 3:2이니 15를 3+2=5묶음으로 똑같이 나누면 한 묶음은 15÷5=3cm예요. 가로는 3묶음이니까 3×3=9cm가 정답이에요.",
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
                    explanation = "표로 정리해 봐요. 1시간에 12km, 2시간에 24km, 3시간에 36km — 시간이 1씩 늘 때마다 12km씩 늘어요. 그래서 3시간 동안 간 거리는 12×3=36km예요.",
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
                    explanation = "표에서 규칙을 찾아봐요. 봉지 1개일 때 5, 2개일 때 10, 3개일 때 15 — 사탕 수가 항상 봉지 수의 5배예요. 만약 5를 더하는 규칙이라면 봉지 2개일 때 7이 되어야 하니 맞지 않아요. 그래서 정답은 △ = □ × 5예요.",
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
                    explanation = "평균 대신 합으로 바꿔서 생각해요. 다섯 수의 합은 20×5=100이고, 남은 네 수의 합은 18×4=72예요. 사라진 수는 100−72=28이니까 정답은 28이에요.",
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
                    explanation = "평균은 합을 개수로 나눈 것이니, 거꾸로 합은 평균×개수로 구해요. 평균이 6이고 수가 4개니까 합은 6×4=24예요. 정답은 24.",
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
                    explanation = "연속한 세 수는 가운데 수보다 1 작은 수와 1 큰 수로 이루어져요. 그래서 합 24를 3으로 나누면 가운데 수 8이 나와요. 세 수는 7, 8, 9이고 가장 작은 수는 7이에요.",
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
                    explanation = "양 끝에서 짝을 지어 더해 봐요. 1+10=11, 2+9=11, 3+8=11처럼 합이 11인 짝이 모두 5개 생겨요. 그래서 11×5=55, 정답은 55예요.",
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
                    explanation = "주사위를 떠올리며 나누어 세어 봐요. 위쪽 면에 모서리 4개, 아래쪽 면에 4개, 그리고 위와 아래를 잇는 기둥 모서리가 4개 있어요. 4+4+4=12개, 정답은 12개예요.",
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
                    explanation = "삼각형의 세 각을 찢어서 한 점에 나란히 모으면 일직선(평각)이 만들어져요. 일직선은 180도이니 세 각의 합도 180도예요. 정답은 180도.",
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
                    explanation = "직각은 90도라는 것부터 떠올려요. 똑같이 반으로 나누면 90÷2=45도가 돼요. 정답은 45도.",
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
                    explanation = "6시에는 짧은바늘이 6, 긴바늘이 12를 가리켜서 두 바늘이 서로 정반대 방향의 일직선이 돼요. 일직선이 이루는 각(평각)은 180도예요. 정답은 180도.",
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
                    explanation = "막대그래프는 수량이 많을수록 막대를 더 길게 그려요. 그래서 막대의 길이만 비교해도 어느 항목이 많고 적은지 한눈에 알 수 있어요. 막대의 길이가 나타내는 것은 수량의 크기예요.",
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
                    explanation = "큰 수부터 순서대로 줄을 세워 봐요. 사과 12명, 포도 10명, 배 8명 순서가 돼요. 두 번째로 많이 좋아하는 과일은 포도예요.",
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
                    explanation = "이등변삼각형을 종이로 만들어 반으로 접으면 양쪽이 딱 겹쳐요. 그래서 두 변의 길이가 같고, 밑에 있는 두 각의 크기도 서로 같아요. 세 각이 모두 같은 것은 정삼각형이에요. 정답은 두 각이에요.",
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
                    explanation = "삼각형은 가장 큰 각을 보고 이름을 붙여요. 한 각이 딱 90도(직각)이면 직각삼각형이에요. 삼각자의 네모난 모서리를 떠올리면 기억하기 쉬워요. 정답은 직각삼각형.",
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
                    explanation = "이웃한 수의 차이를 살펴봐요. 5, 10, 15, 20은 모두 5씩 커지는 규칙이에요. 그래서 20 다음에 올 수는 20+5=25예요.",
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
                    explanation = "수가 점점 작아지니 빼기나 나누기 규칙을 의심해 봐요. 81−27=54, 27−9=18이라 일정하게 빼는 규칙은 아니고, 81÷3=27, 27÷3=9처럼 3으로 나누는 규칙이에요. 그래서 다음 수는 3÷3=1, 정답은 1이에요.",
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
                    explanation = "꺾은선그래프에서 선의 기울기는 변화의 크기를 나타내요. 선이 가파를수록 짧은 시간에 값이 많이 변한 거예요. 위로 가파르게 올라갔다면 그 구간에서 값이 가장 많이 늘어난 것이지요. 정답은 '가장 많이 늘어났다'예요.",
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
                    explanation = "자료의 값이 모두 큰 수라면 0부터 눈금을 전부 그렸을 때 아래쪽이 텅 비어 낭비돼요. 그래서 필요 없는 부분을 물결선으로 줄이면 눈금을 크게 잡아 변화가 잘 보이게 그릴 수 있어요. 정답은 '필요 없는 부분을 줄여서 나타내려고'예요.",
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
                    explanation = "거꾸로 생각해 봐요. 정사각형은 네 변의 길이가 모두 같으니 둘레는 한 변의 4배예요. 그러니 한 변은 24÷4=6이에요. 검산하면 6×4=24로 딱 맞으니 정답은 6cm예요.",
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
                    explanation = "두 단계로 나눠 풀어요. 먼저 같은 수를 두 번 곱해 36이 되는 수를 찾으면 6×6=36이니 한 변은 6cm예요. 정사각형의 둘레는 한 변의 4배이므로 6×4=24예요. 정답은 24cm예요.",
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
                    explanation = "사각형의 이름은 조건으로 정해져요. 네 각이 모두 직각인 사각형은 직사각형이에요. 마름모는 네 변의 길이가 같은 사각형이고, 사다리꼴은 평행한 변이 한 쌍이라도 있는 사각형이지요. 정답은 직사각형이에요.",
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
                    explanation = "사다리꼴은 평행한 변이 한 쌍이라도 있으면 되는, 조건이 가장 느슨한 사각형이에요. 그래서 평행사변형이나 직사각형도 모두 사다리꼴이라고 할 수 있지요. 정답은 사다리꼴이에요.",
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
                    explanation = "'한 상자에 12자루씩'이라는 말은 상자 수에 12를 곱하는 대응 관계예요. 상자가 1개면 12자루, 2개면 24자루처럼 12씩 늘어나요. 그러니 5상자는 12×5=60이에요. 정답은 60자루예요.",
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
                    explanation = "△ = □ × 4는 □에 4를 곱하면 △가 된다는 약속이에요. □ 자리에 7을 넣으면 △는 7×4=28이 돼요. 정답은 28이에요.",
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
                    explanation = "작은 예로 먼저 해 봐요. 네 수가 모두 7이라면 평균도 7이지요. 여기에 각각 2씩 더하면 네 수가 모두 9가 되니 평균도 9가 돼요. 모든 수가 똑같이 커지면 평균도 그만큼 커지므로 정답은 9예요.",
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
                    explanation = "거꾸로 생각해요. 평균이 10인 세 수의 합은 10×3=30이에요. 그 합에서 아는 두 수 8과 12를 빼면 30−8−12=10이 남아요. 정답은 10이에요.",
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
                    explanation = "거꾸로 생각하기 전략을 써요. 마지막 결과 6에서 출발해 반대로 되돌리면, 4로 나누기 전은 6×4=24이고 5를 빼기 전은 24+5=29예요. 검산하면 29에서 5를 빼고 4로 나눠 6이 되니 정답은 29예요.",
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
                    explanation = "큰 수는 작은 수보다 4만큼 크니, 합 20에 차 4를 더한 24는 큰 수를 두 번 더한 것과 같아요. 그래서 큰 수는 24÷2=12, 작은 수는 12−4=8이에요. 검산하면 12+8=20, 12−8=4로 딱 맞아요. 정답은 12예요.",
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
                    explanation = "정육면체는 주사위 모양이에요. 꼭짓점은 위쪽 면에 4개, 아래쪽 면에 4개 있어서 모두 4+4=8개예요. 모서리 12개, 면 6개와 헷갈리기 쉬우니 머릿속으로 직접 세어 봐요. 정답은 8개예요.",
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
                    explanation = "사각형에 대각선을 하나 그으면 삼각형 2개로 나뉘어요. 삼각형 세 각의 합은 180도이니, 사각형 네 각의 합은 180×2=360이에요. 정답은 360도예요.",
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
                    explanation = "이웃한 수의 차이를 살펴봐요. 1에서 2는 +1, 2에서 4는 +2, 4에서 7은 +3, 7에서 11은 +4로 더하는 수가 매번 1씩 커지는 규칙이에요. 그러니 다음은 11+5=16이에요. 정답은 16이에요.",
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
                    explanation = "규칙을 먼저 찾아요. 성냥개비는 3, 5, 7로 삼각형이 하나 늘 때마다 2개씩 늘어나요. 이어 붙이면 변을 함께 쓰기 때문이지요. 처음 3개에서 2개씩 9번 더 늘어나니 3+2×9=21이에요. 정답은 21개예요.",
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
                    explanation = "이웃한 수의 차이를 보면 1, 3, 5, 7은 2씩 커지는 규칙이에요. 홀수를 차례로 늘어놓은 것이지요. 그러니 7 다음은 7+2=9예요. 정답은 9예요.",
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
                    explanation = "합이 10인 두 수의 짝을 차례로 떠올려 봐요. 5와 5는 차가 0이고, 6과 4는 차가 2로 조건에 딱 맞아요. 검산하면 6+4=10, 6−4=2예요. 큰 수를 물었으니 정답은 6이에요.",
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
                    explanation = "5의 배수를 차례로 써 봐요. 5, 10, 15, 20, 25 중에서 10보다 크고 20보다 작은 수는 15뿐이에요. 10과 20은 '보다 크다, 보다 작다'는 조건에 들어가지 않는다는 점을 조심해요. 정답은 15예요.",
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
                    explanation = "직접 접는 모습을 떠올려 봐요. 변의 가운데끼리 만나게 접으면 직사각형, 대각선으로 접으면 삼각형이 돼요. 하지만 접은 자국은 언제나 곧은 선이라서, 굽은 선으로 둘러싸인 원은 만들 수 없어요. 정답은 원이에요.",
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
                    explanation = "머릿속으로 잘라 봐요. 대각선은 마주 보는 두 꼭짓점을 잇는 곧은 선이에요. 그 선을 따라 자르면 종이가 두 조각 나고, 각 조각은 변이 3개인 삼각형이 돼요. 정답은 삼각형 2개예요.",
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
                    explanation = "긴바늘은 분을 나타내는 바늘이에요. 작은 눈금 한 칸이 1분이고 시계 한 바퀴에는 눈금이 60칸 있어요. 그래서 긴바늘이 한 바퀴를 다 돌면 60분, 곧 1시간이 지난 거예요. 정답은 60분이에요.",
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
                    explanation = "키 순서대로 줄을 세워 봐요. 가는 나보다 크고 나는 다보다 크니, 큰 순서대로 가, 나, 다가 돼요. 맨 끝에 오는 가장 작은 사람은 다예요. 정답은 다예요.",
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
                    explanation = "하루씩 차례로 세어 봐요. 수요일에서 1일 뒤는 목요일, 2일 뒤는 금요일, 3일 뒤는 토요일이에요. 손가락으로 하나씩 짚으며 세면 헷갈리지 않아요. 정답은 토요일이에요.",
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
                    explanation = "나올 수 있는 경우를 빠짐없이 적어 봐요. 동전에는 앞면과 뒷면 두 면이 있고, 던지면 둘 중 하나가 나와요. 그래서 나올 수 있는 면은 앞면, 뒷면으로 모두 2가지예요. 정답은 2가지예요.",
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
                    explanation = "작은 수부터 차례로 만들어 봐요. 작은 숫자를 앞자리에 놓을수록 작은 수가 되니 가장 작은 수는 123이에요. 둘째로 작은 수는 맨 앞의 1은 그대로 두고 뒤의 두 숫자만 서로 바꾼 132예요. 답은 132예요.",
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
                    explanation = "가장 큰 금액을 만들려면 세 동전 중 가장 큰 두 개를 골라야 해요. 100원과 50원을 고르면 100+50=150원이에요. 10원이 들어가면 금액이 더 작아지니, 답은 150원이에요.",
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
                    explanation = "작은 수로 먼저 해 봐요. 1+3=4, 3+5=8, 5+7=12처럼 홀수끼리 더하면 언제나 짝수가 나와요. 홀수는 짝수보다 1 큰 수라서, 홀수 둘을 더하면 남는 1이 두 개 모여 2가 되어 짝수가 되기 때문이에요. 답은 짝수예요.",
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
                    explanation = "철수 자리는 맨 앞으로 이미 정해졌으니, 남은 두 친구가 둘째와 셋째 자리에 서는 방법만 세면 돼요. 두 친구가 서로 자리를 바꾸는 경우까지 해서 2가지뿐이에요. 답은 2가지예요.",
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
                    explanation = "표로 정리해 봐요. 첫째 동전이 앞일 때 둘째 동전은 앞 또는 뒤, 첫째 동전이 뒤일 때도 둘째는 앞 또는 뒤가 나와요. (앞,앞), (앞,뒤), (뒤,앞), (뒤,뒤)로 2×2=4가지예요. 답은 4가지예요.",
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
                    explanation = "합이 가장 크려면 두 주사위 모두 가장 큰 눈이 나와야 해요. 주사위의 가장 큰 눈은 6이니까 6+6=12예요. 곱하기가 아니라 더하기라는 점에 주의해요. 답은 12예요.",
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
                    explanation = "가운데 수를 먼저 찾는 전략을 써요. 연속한 세 짝수의 합은 가운데 수의 3배와 같으니 가운데 수는 24÷3=8이에요. 세 수는 6, 8, 10이고 검산하면 6+8+10=24로 딱 맞아요. 가장 큰 수는 10이에요.",
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
                    explanation = "거꾸로 생각해요. 나누는 수 곱하기 몫에 나머지를 더하면 원래 수가 돼요. 4×7=28에 나머지 2를 더하면 30이에요. 검산하면 30÷4는 몫 7, 나머지 2로 딱 맞으니 답은 30이에요.",
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
                    explanation = "자리별로 나눠 세면 빠뜨리지 않아요. 일의 자리에 1이 있는 수는 1과 11로 2번, 십의 자리에 1이 있는 수는 10부터 19까지 10번이에요. 11은 두 자리 모두 1이라 두 번으로 세어지는 게 포인트예요. 모두 2+10=12번이에요.",
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
                    explanation = "분모를 10으로 똑같이 맞춰 비교해요. 1/2은 5/10, 2/5는 4/10, 3/10은 그대로 3/10이에요. 10칸 중 5칸을 차지하는 게 가장 크니 답은 1/2이에요.",
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
                    explanation = "물통을 똑같이 3칸으로 나눠 그려 봐요. 1/3에서 2/3이 되었으니 더 부은 6L는 딱 한 칸, 즉 전체의 1/3이에요. 한 칸이 6L니까 세 칸 가득은 6×3=18L예요. 답은 18L예요.",
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
                    explanation = "리본을 똑같이 4도막으로 나눈 그림을 떠올려요. 한 도막(전체의 1/4)이 5cm니까 전체는 그런 도막 4개예요. 5×4=20이니 리본 전체 길이는 20cm예요.",
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
                    figure = ProblemFigure(FigureType.GRID, mapOf("w" to 3, "h" to 3)),
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
                    explanation = "바늘이 실제로 어디 있는지 그려 봐요. 긴바늘은 6을 가리키고, 짧은바늘은 30분이 지난 만큼 움직여서 3과 4의 딱 중간에 있어요. 시계 숫자 한 칸은 30도인데 두 바늘 사이는 두 칸 반이니 30×2.5=75도예요. 답은 75도예요.",
                    mistakes =
                        listOf(
                            Mistake(0, "짧은바늘은 3에 딱 있지 않아요. 30분이 지나 3과 4의 중간에 있어요."),
                        ),
                    figure = ProblemFigure(FigureType.CLOCK, mapOf("hour" to 3, "minute" to 30)),
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
                    explanation = "두 단계로 나눠 풀어요. 정사각형은 네 변의 길이가 같으니 한 변은 둘레를 4로 나눈 20÷4=5cm예요. 넓이는 한 변 곱하기 한 변이니 5×5=25예요. 답은 25cm²예요.",
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
                    explanation = "삼각형 세 각의 합은 언제나 180도라는 규칙을 써요. 이미 아는 두 각을 더하면 90+30=120도예요. 180에서 120을 빼면 나머지 한 각은 60도예요.",
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
                    explanation = "요일은 7일마다 똑같이 돌아온다는 규칙을 써요. 1일에서 15일까지는 14일 뒤인데, 14는 7×2로 딱 2주예요. 그래서 15일은 1일과 같은 요일인 금요일이에요.",
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
                    explanation = "합에서 차를 먼저 덜어내는 전략을 써요. 형이 4살 많으니 합 20에서 4를 빼면 16, 이걸 반으로 나눈 8살이 동생이에요. 형은 8+4=12살이에요. 검산하면 12+8=20으로 딱 맞아요.",
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
                    explanation = "먼저 3분 동안 탄 길이를 구해요. 1분에 2cm씩 타니까 3분이면 2×3=6cm가 타요. 문제는 남은 길이를 물었으니 처음 10cm에서 빼서 10−6=4cm예요. 답은 4cm예요.",
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
                    explanation = "나머지의 규칙을 떠올려요. 나머지는 나누는 수보다 항상 작아야 하니 6으로 나눌 때 나머지는 최대 5예요. 거꾸로 계산하면 6×8+5=53이에요. 답은 53이에요.",
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
                    explanation = "곱이 36인 두 수의 짝을 표로 정리해요. 1과 36, 2와 18, 3과 12, 4와 9, 6과 6 중에서 합이 13인 짝을 찾으면 4+9=13이에요. 두 수는 4와 9이고, 둘 중 큰 수는 9예요.",
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
                    explanation = "1부터 차례로 더해 가며 45가 되는 순간을 찾아요. 1부터 8까지 더하면 36이고, 여기에 9를 더하면 딱 45가 돼요. 10까지 더하면 55라서 넘치니, 네모에 들어갈 수는 9예요.",
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
                    explanation = "짝을 지어 세는 전략을 써요. 4팀이 각각 다른 3팀과 경기한다고 하면 4×3=12지만, 이러면 같은 경기를 두 번씩 센 거예요. 절반으로 나누면 12÷2=6경기예요. 답은 6경기예요.",
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
                    explanation = "첫째 주사위 눈을 1부터 차례로 정하고 합이 7이 되도록 둘째 주사위를 맞춰 봐요. (1,6), (2,5), (3,4), (4,3), (5,2), (6,1)로 첫째 눈마다 짝이 하나씩 있어요. 서로 다른 주사위라 (1,6)과 (6,1)은 다른 경우로 세요. 모두 6가지예요.",
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
                    explanation = "한 명씩 차례로 세어 봐요. 5명이 각각 다른 4명과 악수하면 5×4=20인데, 이러면 같은 악수를 두 사람 쪽에서 두 번씩 센 거예요. 그래서 20÷2=10번이에요. 답은 10번이에요.",
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
                    explanation = "조각이 어느 자리에 있었는지로 나눠 생각해요. 두 면만 칠해진 조각은 두 면이 만나는 모서리의 한가운데에 있어요. 정육면체의 모서리는 12개이고 모서리마다 그런 조각이 1개씩 있으니 모두 12개예요. 답은 12개예요.",
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
                    explanation = "한 면도 칠해지지 않은 조각은 큰 정육면체 속에 완전히 숨어 있는 조각이에요. 27개로 자르면 가로·세로·높이 3칸씩인데, 겉을 한 겹씩 벗겨 내면 한가운데에 1개만 남아요. 그래서 정답은 1개예요.",
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
                    explanation = "크기별로 나누어 세는 게 요령이에요. 1칸짜리는 16개, 2×2짜리는 3×3=9개, 3×3짜리는 2×2=4개, 4×4짜리는 1개예요. 모두 더하면 16+9+4+1=30개가 정답이에요.",
                    mistakes =
                        listOf(
                            Mistake(0, "1칸짜리만 셌어요. 16+9+4+1로 크기별로 더해요."),
                        ),
                    figure = ProblemFigure(FigureType.GRID, mapOf("w" to 4, "h" to 4)),
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
                    explanation = "귤로 단위를 통일해서 생각해요. 배 1개는 귤 4개와 같고, 귤 2개가 사과 1개와 같으니 귤 4개는 사과 2개와 같아요. 그래서 배 1개는 사과 2개와 무게가 같아요. 정답은 2개예요.",
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
                    explanation = "달력은 7일마다 같은 요일이 돌아와요. 3월 1일이 화요일이면 8일, 15일, 22일, 29일도 모두 화요일이에요. 31일은 29일보다 2일 뒤니까 화요일에서 두 칸 간 목요일이 정답이에요.",
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
                    explanation = "1부터 9까지 모두 더하면 45예요. 가로 세 줄에 아홉 개의 수가 한 번씩 나뉘어 들어가니, 한 줄의 합은 45를 3으로 똑같이 나눈 값이에요. 45÷3=15, 정답은 15예요.",
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
                    explanation = "약속을 그대로 따라가면 돼요. 앞 수는 5, 뒤 수는 3이니까 먼저 5×3=15를 구하고, 거기서 앞 수 5를 빼요. 15−5=10이라서 정답은 10이에요.",
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
                    explanation = "하루에 1m씩 오른다고만 계산하면 함정에 빠져요. 표로 따라가 보면 7일째 밤이 끝났을 때 달팽이는 7m 지점에 있어요. 8일째 낮에 3m를 오르면 7+3=10m로 꼭대기에 딱 닿으니, 정답은 8일째예요.",
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
                    explanation = "맞물린 톱니바퀴는 지나가는 톱니 수가 서로 같아요. A가 1바퀴 돌면 톱니 20개가 지나가는데, B는 톱니가 10개뿐이라 20÷10=2바퀴를 돌아야 해요. 그래서 정답은 2바퀴예요.",
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
                    explanation = "쪽수를 자릿수별로 나누어 세어 봐요. 1쪽부터 9쪽까지는 한 자리 수라 숫자 9개, 10쪽부터 50쪽까지는 두 자리 수가 41개라 숫자 41×2=82개가 필요해요. 9+82=91개가 정답이에요.",
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
                    explanation = "10×4=40으로 계산하면 네 모퉁이의 돌을 두 번 센 셈이에요. 모퉁이 돌 4개를 한 번씩만 세도록 40에서 4를 빼면 36개예요. 정답은 36개예요.",
                    mistakes =
                        listOf(
                            Mistake(0, "10×4=40으로 하면 네 꼭짓점 돌을 두 번 센 거예요. 40−4=36."),
                        ),
                    figure = ProblemFigure(FigureType.DOT_BORDER, mapOf("side" to 10)),
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
                    explanation = "달력에서 위아래로 붙은 수는 7씩 차이가 나요. 세 수를 (가운데−7), 가운데, (가운데+7)로 나타내면 −7과 +7이 서로 사라져서 합이 가운데×3이 돼요. 42÷3=14, 그래서 가운데 수는 14예요.",
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
                    explanation = "천의 자리부터 경우를 나눠 세요. 4로 시작하면 나머지 세 카드를 늘어놓는 방법이 3×2×1=6개, 34로 시작하면 3412와 3421로 2개, 32로 시작하면 3214와 3241로 2개예요. 31로 시작하면 3200보다 작으니 빼고, 6+2+2=10개가 정답이에요.",
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
                    explanation = "조건을 하나씩 써서 범위를 좁혀 가요. 십의 자리가 5니까 백의 자리와 일의 자리의 합은 14−5=9예요. 백의 자리가 일의 자리의 2배이므로 2배+1배=9에서 일의 자리는 3, 백의 자리는 6이에요. 그래서 이 수는 653이에요.",
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
                    explanation = "끝의 0은 2×5=10이 곱해질 때마다 하나씩 생겨요. 1부터 10까지에서 5를 만드는 수는 5와 10(=2×5)의 두 번이고, 짝이 될 2는 충분히 많아요. 그래서 10이 두 번 만들어져 끝의 0도 2개예요.",
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
                    figure = ProblemFigure(FigureType.L_SHAPE, mapOf("w" to 10, "h" to 10, "cutW" to 4, "cutH" to 4)),
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
                    explanation = "새 직선이 이미 있는 직선을 모두 가로지르게 그으면 조각이 가장 많이 늘어나요. 직선을 하나씩 그을 때마다 늘어나는 조각 수는 1개, 2개, 3개, 4개로 커져요. 처음 1부분에서 시작해 1+1+2+3+4=11부분이 정답이에요.",
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
                    explanation = "종이를 반으로 접을 때마다 겹이 2배가 돼요. 두 번 접으면 2×2=4겹이 되고, 구멍을 한 번 뚫으면 네 겹이 한꺼번에 뚫려요. 펼치면 구멍은 모두 4개예요.",
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
                    explanation = "각 갈림길 점에 '거기까지 가는 방법 수'를 적어 가며 더하는 전략을 써요. 어떤 점까지 가는 방법 수는 그 점의 왼쪽 점과 아래쪽 점의 방법 수를 더한 것과 같아요. 이렇게 차근차근 채우면 맨 오른쪽 위 점은 6이 되어, 정답은 6가지예요.",
                    mistakes =
                        listOf(
                            Mistake(0, "각 갈림길에 '거기까지 가는 방법 수'를 적어 가며 더해 보세요. 1,2,1 → 1,3,3 → 6."),
                        ),
                    figure = ProblemFigure(FigureType.GRID, mapOf("w" to 2, "h" to 2, "mark" to 1)),
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
                    explanation = "보기를 하나씩 검산해 보는 것도 훌륭한 전략이에요. 아들이 10살이면 아버지는 4배인 40살이고, 5년 뒤에는 15살과 45살이 돼요. 45는 15의 딱 3배라서 조건에 맞으니, 정답은 10살이에요.",
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
                    explanation = "도막 수와 자르는 횟수는 달라요. 그림을 그려 보면 통나무를 한 번 자를 때마다 도막이 1개씩 늘어나서, 5도막을 만들려면 4번만 자르면 돼요. 한 번에 3분이니 4×3=12분이 정답이에요.",
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
                    explanation = "서로 반대 방향으로 걸으면 두 사람이 좁히는 거리는 두 속력의 합이에요. 1분에 60+40=100m씩 가까워지니, 트랙 한 바퀴 400m를 다 좁히는 데 400÷100=4분이 걸려요. 정답은 4분이에요.",
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
                    explanation = "동전을 3개씩 세 묶음으로 나누는 게 열쇠예요. 첫 번째로 두 묶음을 저울에 올리면, 기울면 가벼운 쪽에, 평형이면 남은 묶음에 가짜가 있어요. 가짜가 든 묶음 3개 중 2개를 다시 올리면 같은 방법으로 가짜를 찾을 수 있으니, 2번이면 충분해요.",
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
                    explanation = "빠짐없이 나열하는 전략을 써요. 1+1+1+1, 1+1+2, 1+2+1, 2+1+1, 2+2처럼 오르는 순서가 다르면 다른 방법으로 세어야 해요. 모두 나열하면 5가지가 정답이에요.",
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
                    explanation = "거울은 시계의 좌우를 뒤집어서 보여 줘요. 실제 시각과 거울 속 시각을 더하면 12시가 된다고 생각하면 쉬워요. 12−9=3이니 실제 시각은 3시예요.",
                    mistakes =
                        listOf(
                            Mistake(0, "거울은 좌우를 뒤집어요. 12를 기준으로 접었을 때 9시와 겹치는 시각을 찾아요."),
                        ),
                    figure = ProblemFigure(FigureType.CLOCK, mapOf("hour" to 9, "minute" to 0)),
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
                    explanation = "긴바늘이 짧은바늘을 따라잡는 문제로 생각해요. 2시 정각에 짧은바늘은 숫자 2(10분 눈금 자리)에 있는데, 긴바늘이 10분 동안 거기까지 가면 짧은바늘은 그 사이 조금 더 앞으로 가 있어요. 그래서 겹치는 순간은 10분보다 살짝 뒤인 2시 11분쯤이에요.",
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
                    explanation = "두 사람의 나이 차이는 시간이 지나도 변하지 않는다는 게 열쇠예요. 딸이 12살이면 어머니는 3배인 36살이고, 12년 뒤에는 24살과 48살이 돼요. 48은 24의 딱 2배라 조건에 맞으니, 정답은 12살이에요.",
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
                    explanation = "두 초의 길이 차이가 어떻게 줄어드는지 살펴봐요. 처음 차이는 20−12=8cm이고, 1시간마다 긴 초가 1cm 더 타니 차이가 1cm씩 줄어들어요. 8÷1=8시간 뒤에 두 초 모두 4cm로 같아지니, 정답은 8시간이에요.",
                    mistakes =
                        listOf(
                            Mistake(0, "길이 차이 8cm가 1시간에 1cm씩 줄어들어요. 8÷1=8시간."),
                        ),
                ),
            )
        }
}
