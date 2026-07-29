package com.ddakpul.math.presentation.common

import androidx.annotation.StringRes
import androidx.compose.ui.graphics.Color
import com.ddakpul.math.R
import com.ddakpul.math.core.designsystem.theme.AreaChange
import com.ddakpul.math.core.designsystem.theme.AreaData
import com.ddakpul.math.core.designsystem.theme.AreaNumber
import com.ddakpul.math.core.designsystem.theme.AreaShape
import com.ddakpul.math.domain.model.MathArea

/** domain의 [MathArea]를 표시용 문자열 리소스로 매핑한다(domain은 리소스를 모른다). */
@StringRes
fun MathArea.labelRes(): Int =
    when (this) {
        MathArea.NUMBER_OPERATION -> R.string.area_number_operation
        MathArea.CHANGE_RELATION -> R.string.area_change_relation
        MathArea.SHAPE_MEASUREMENT -> R.string.area_shape_measurement
        MathArea.DATA_POSSIBILITY -> R.string.area_data_possibility
    }

/** 4개 영역의 고정 구분색(홈 실력 지도·리포트 공용) — 알록달록하되 절제. */
fun MathArea.areaColor(): Color =
    when (this) {
        MathArea.NUMBER_OPERATION -> AreaNumber
        MathArea.CHANGE_RELATION -> AreaChange
        MathArea.SHAPE_MEASUREMENT -> AreaShape
        MathArea.DATA_POSSIBILITY -> AreaData
    }
