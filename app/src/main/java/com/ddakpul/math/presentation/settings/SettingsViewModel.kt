package com.ddakpul.math.presentation.settings

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ddakpul.math.domain.model.SessionGoals
import com.ddakpul.math.domain.usecase.BuildExclusionReportUseCase
import com.ddakpul.math.domain.usecase.ObserveDailyGoalUseCase
import com.ddakpul.math.domain.usecase.ObserveExcludedCountUseCase
import com.ddakpul.math.domain.usecase.ObserveUnlockAllLevelsUseCase
import com.ddakpul.math.domain.usecase.ResetProgressUseCase
import com.ddakpul.math.domain.usecase.SetDailyGoalUseCase
import com.ddakpul.math.domain.usecase.SetUnlockAllLevelsUseCase
import com.ddakpul.math.presentation.common.SpeechSettings
import com.ddakpul.math.presentation.common.tts.DownloadState
import com.ddakpul.math.presentation.common.tts.TtsModel
import com.ddakpul.math.presentation.common.tts.TtsModelManager
import com.ddakpul.math.presentation.common.tts.TtsModels
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SettingsUiState(
    val dailyGoal: Int = SessionGoals.DAILY_GOAL_PROBLEMS,
    /** "별로예요"로 제외한 문제 수 — 내보내기 버튼의 라벨·활성화에 쓴다. */
    val excludedCount: Int = 0,
    /** 상위 난이도(기본 상한 위) 열기 스위치 상태. */
    val unlockAllLevels: Boolean = false,
)

@HiltViewModel
class SettingsViewModel
    @Inject
    constructor(
        observeDailyGoal: ObserveDailyGoalUseCase,
        observeExcludedCount: ObserveExcludedCountUseCase,
        observeUnlockAllLevels: ObserveUnlockAllLevelsUseCase,
        private val setDailyGoal: SetDailyGoalUseCase,
        private val setUnlockAllLevels: SetUnlockAllLevelsUseCase,
        private val resetProgress: ResetProgressUseCase,
        private val buildExclusionReport: BuildExclusionReportUseCase,
        private val ttsModelManager: TtsModelManager,
        @ApplicationContext private val context: Context,
    ) : ViewModel() {
        /** 신경망 TTS 모델 다운로드 진행 상태(진행바·재시도 UI용). */
        val ttsDownloadState: StateFlow<DownloadState> = ttsModelManager.state

        private val _ttsDownloaded = MutableStateFlow(false)

        /** 고품질 음성 모델이 이미 받아져 있는지(초기 표시용). */
        val ttsDownloaded: StateFlow<Boolean> = _ttsDownloaded.asStateFlow()

        fun refreshTtsDownloaded(model: TtsModel) {
            _ttsDownloaded.value = ttsModelManager.isDownloaded(model)
        }

        fun downloadTtsModel(model: TtsModel) {
            viewModelScope.launch {
                ttsModelManager.download(model)
                val ok = ttsModelManager.isDownloaded(model)
                _ttsDownloaded.value = ok
                // 받자마자 이 음성으로 바로 읽어 준다 — 다운로드 카드가 사라진 뒤에도 "받은 게
                // 켜졌다"는 걸 위 '읽어주기 음성' 칩/안내로 즉시 확인시켜 준다(따로 안 눌러도 됨).
                if (ok) SpeechSettings.setEngine(context, TtsModels.engineValue(model), model.displayName(context))
            }
        }

        fun deleteTtsModel(model: TtsModel) {
            ttsModelManager.delete(model)
            _ttsDownloaded.value = false
            // 지금 이 음성으로 읽는 중이었다면 기기 기본으로 되돌린다(사라진 음성을 계속 가리키지 않게).
            if (SpeechSettings.engine.value == TtsModels.engineValue(model)) {
                SpeechSettings.setEngine(context, null, null)
            }
        }

        val uiState: StateFlow<SettingsUiState> =
            combine(observeDailyGoal(), observeExcludedCount(), observeUnlockAllLevels()) { goal, excluded, unlockAll ->
                SettingsUiState(
                    dailyGoal = goal,
                    excludedCount = excluded,
                    unlockAllLevels = unlockAll,
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

        fun setUnlockAllLevels(enabled: Boolean) {
            viewModelScope.launch { setUnlockAllLevels.invoke(enabled) }
        }

        fun resetProgress() {
            viewModelScope.launch { resetProgress.invoke() }
        }

        fun requestExclusionShare() {
            viewModelScope.launch { _pendingShareText.value = buildExclusionReport()?.toShareText(context) }
        }

        fun consumeShareText() {
            _pendingShareText.value = null
        }

        private companion object {
            const val STOP_TIMEOUT_MILLIS = 5_000L
        }
    }
