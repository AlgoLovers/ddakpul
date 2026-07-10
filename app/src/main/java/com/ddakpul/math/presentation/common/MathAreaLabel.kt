package com.ddakpul.math.presentation.common

import androidx.annotation.StringRes
import com.ddakpul.math.R
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
