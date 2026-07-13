package com.ddakpul.math.presentation.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ddakpul.math.domain.model.SessionGoals
import com.ddakpul.math.domain.usecase.BuildExclusionReportUseCase
import com.ddakpul.math.domain.usecase.ObserveDailyGoalUseCase
import com.ddakpul.math.domain.usecase.ObserveEntitlementUseCase
import com.ddakpul.math.domain.usecase.ObserveExcludedCountUseCase
import com.ddakpul.math.domain.usecase.ResetProgressUseCase
import com.ddakpul.math.domain.usecase.SetDailyGoalUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import javax.inject.Inject
import kotlin.math.ceil

data class SettingsUiState(
    val dailyGoal: Int = SessionGoals.DAILY_GOAL_PROBLEMS,
    /** "별로예요"로 제외한 문제 수 — 내보내기 버튼의 라벨·활성화에 쓴다. */
    val excludedCount: Int = 0,
    /** 프리미엄 이용권 보유 여부와 남은 일수 — 이용권 카드 상태 표시. */
    val isPremium: Boolean = false,
    val premiumDaysLeft: Int = 0,
)

@HiltViewModel
class SettingsViewModel
    @Inject
    constructor(
        observeDailyGoal: ObserveDailyGoalUseCase,
        observeExcludedCount: ObserveExcludedCountUseCase,
        observeEntitlement: ObserveEntitlementUseCase,
        private val setDailyGoal: SetDailyGoalUseCase,
        private val resetProgress: ResetProgressUseCase,
        private val buildExclusionReport: BuildExclusionReportUseCase,
    ) : ViewModel() {
        val uiState: StateFlow<SettingsUiState> =
            combine(observeDailyGoal(), observeExcludedCount(), observeEntitlement()) { goal, excluded, entitlement ->
                val now = System.currentTimeMillis()
                val premium = entitlement.isPremium(now)
                SettingsUiState(
                    dailyGoal = goal,
                    excludedCount = excluded,
                    isPremium = premium,
                    premiumDaysLeft = if (premium) ceil((entitlement.premiumUntilMillis - now).toDouble() / MILLIS_PER_DAY).toInt() else 0,
                )
            }.stateIn(
                scope = viewModelScope,
                started = SharingStarted.WhileSubscribed(STOP_TIMEOUT_MILLIS),
                initialValue = SettingsUiState(),
            )

        // 내보내기 텍스트가 준비되면 UI가 공유 시트를 띄우고 소비(consume)하는 일회성 이벤트.
        private val _pendingShareText = MutableStateFlow<String?>(null)
        val pendingShareText: StateFlow<String?> = _pendingShareText.asStateFlow()

        fun setDailyGoal(goal: Int) {
            viewModelScope.launch { setDailyGoal.invoke(goal) }
        }

        fun resetProgress() {
            viewModelScope.launch { resetProgress.invoke() }
        }

        fun requestExclusionShare() {
            viewModelScope.launch { _pendingShareText.value = buildExclusionReport() }
        }

        fun consumeShareText() {
            _pendingShareText.value = null
        }

        private companion object {
            const val STOP_TIMEOUT_MILLIS = 5_000L
            const val MILLIS_PER_DAY = 86_400_000L
        }
    }
