package com.ddakpul.math.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * 문제 테이블. 리스트/구조 필드(보기, 개념태그, 흔한 오답)는 매퍼에서 JSON 문자열로 직렬화해
 * 단일 컬럼으로 저장한다 — Room 스키마를 단순하게 유지하기 위함.
 */
@Entity(tableName = "problem")
data class ProblemEntity(
    @PrimaryKey val id: String,
    val grade: Int,
    val semester: Int,
    val area: String,
    val conceptTagsJson: String,
    val difficulty: Int,
    val groupId: String,
    val statement: String,
    val choicesJson: String,
    val correctChoiceIndex: Int,
    val explanation: String?,
    val mistakesJson: String,
)
