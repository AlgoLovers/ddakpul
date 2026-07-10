package com.ddakpul.math.domain.repository

import com.ddakpul.math.domain.model.MathArea
import com.ddakpul.math.domain.model.Problem
import com.ddakpul.math.domain.model.ProblemGroup

/**
 * 내장 문제은행에 대한 단일 진실 공급원. 구현체(Room + 시딩)는 data 계층에 있고,
 * domain은 이 인터페이스에만 의존한다.
 */
interface ProblemRepository {
    /** 추천 단위인 그룹으로 묶어 전체 문제를 돌려준다. */
    suspend fun getAllGroups(): List<ProblemGroup>

    suspend fun getProblem(id: String): Problem?

    /** 리포트에서 시도를 영역별로 집계하기 위한 문제ID → 영역 색인. */
    suspend fun areaByProblemId(): Map<String, MathArea>
}
