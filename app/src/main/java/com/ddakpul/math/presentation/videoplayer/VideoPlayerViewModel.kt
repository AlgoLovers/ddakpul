package com.ddakpul.math.presentation.videoplayer

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ddakpul.math.domain.repository.SolutionVideoRepository
import dagger.hilt.android.lifecycle.HiltViewModel
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

/**
 * 방법코드로 영상을 찾아 로컬 확보(캐시 또는 1회 다운로드) 후 재생 준비 상태를 노출한다.
 * 영상은 버전 파일명으로 캐시되므로 한 번 받으면 오프라인에서도 재생된다.
 */
@HiltViewModel
class VideoPlayerViewModel
    @Inject
    constructor(
        private val repository: SolutionVideoRepository,
    ) : ViewModel() {
        private val _state = MutableStateFlow<VideoPlayerState>(VideoPlayerState.Loading)
        val state: StateFlow<VideoPlayerState> = _state.asStateFlow()

        private var startedFor: String? = null

        /** 화면 진입 시 1회 호출. 재시도 버튼도 이걸 다시 부른다. */
        fun load(methodCode: String) {
            startedFor = methodCode
            _state.value = VideoPlayerState.Loading
            viewModelScope.launch {
                val video = repository.videoForMethod(methodCode)
                if (video == null) {
                    _state.value = VideoPlayerState.Failed
                    return@launch
                }
                if (!repository.isCached(video)) {
                    _state.value = VideoPlayerState.Downloading(0, 0)
                }
                val path =
                    repository.ensureLocal(video) { received, total ->
                        _state.value = VideoPlayerState.Downloading(received, total)
                    }
                _state.value = if (path != null) VideoPlayerState.Ready("file://$path") else VideoPlayerState.Failed
            }
        }
    }
