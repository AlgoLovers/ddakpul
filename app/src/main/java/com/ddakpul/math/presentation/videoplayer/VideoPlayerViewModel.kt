package com.ddakpul.math.presentation.videoplayer

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ddakpul.math.domain.usecase.PrepareSolutionVideoUseCase
import com.ddakpul.math.domain.usecase.VideoPreparation
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/** 해설 영상 확보 상태 — 캐시돼 있으면 즉시 Ready, 아니면 다운로드 진행을 보여준다. */
sealed interface VideoPlayerState {
    data object Loading : VideoPlayerState

    data class Downloading(
        val received: Long,
        val total: Long,
    ) : VideoPlayerState {
        val percent: Int get() = if (total > 0) ((received * 100 / total).toInt()).coerceIn(0, 100) else 0
    }

    data class Ready(
        val fileUri: String,
    ) : VideoPlayerState

    data object Failed : VideoPlayerState
}

/** 확보 진행 상태를 화면이 쓰는 UI 상태로 옮긴다 — 재생기가 요구하는 file:// 스킴은 여기서 붙인다. */
private fun VideoPreparation.toUiState(): VideoPlayerState =
    when (this) {
        is VideoPreparation.Downloading -> VideoPlayerState.Downloading(received, total)
        is VideoPreparation.Ready -> VideoPlayerState.Ready("file://$filePath")
        VideoPreparation.Failed -> VideoPlayerState.Failed
    }

/**
 * 방법코드로 영상을 찾아 로컬 확보(캐시 또는 1회 다운로드) 후 재생 준비 상태를 노출한다.
 * 영상은 버전 파일명으로 캐시되므로 한 번 받으면 오프라인에서도 재생된다.
 */
@HiltViewModel
class VideoPlayerViewModel
    @Inject
    constructor(
        private val prepareVideo: PrepareSolutionVideoUseCase,
    ) : ViewModel() {
        private val _state = MutableStateFlow<VideoPlayerState>(VideoPlayerState.Loading)
        val state: StateFlow<VideoPlayerState> = _state.asStateFlow()

        private var startedFor: String? = null

        /** 진행 중인 로드 — 겹치면 이전 것을 취소한다. */
        private var loadJob: Job? = null

        /** 화면 진입 시 1회 호출. 재시도 버튼도 이걸 다시 부른다. */
        fun load(methodCode: String) {
            // 죽은 가드였던 startedFor를 실제로 쓴다 — 재시도 연타·회전으로 load가 겹치면
            // 두 코루틴이 같은 .part 파일에 동시에 써서 손상된 mp4가 영구 캐시된다.
            if (startedFor == methodCode && loadJob?.isActive == true) return
            loadJob?.cancel()
            startedFor = methodCode
            _state.value = VideoPlayerState.Loading
            loadJob =
                viewModelScope.launch {
                    prepareVideo(methodCode).collect { _state.value = it.toUiState() }
                }
        }
    }
