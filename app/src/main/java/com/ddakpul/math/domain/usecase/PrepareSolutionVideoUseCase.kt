package com.ddakpul.math.domain.usecase

import com.ddakpul.math.domain.repository.SolutionVideoRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.channelFlow
import javax.inject.Inject

/** 해설 영상을 재생할 수 있게 되기까지의 진행 상태. */
sealed interface VideoPreparation {
    /** 내려받는 중. 총량을 아직 모르면 [total]이 0이다. */
    data class Downloading(
        val received: Long,
        val total: Long,
    ) : VideoPreparation

    /** 재생 가능한 로컬 파일 경로가 확보됐다. */
    data class Ready(
        val filePath: String,
    ) : VideoPreparation

    /** 영상이 없거나 확보에 실패했다. */
    data object Failed : VideoPreparation
}

/**
 * 방법코드로 영상을 찾아 로컬에 확보하기까지를 하나의 스트림으로 돌려준다 —
 * 캐시돼 있으면 곧장 [VideoPreparation.Ready], 아니면 진행률을 흘리며 1회 내려받는다.
 * 화면은 이 스트림을 UI 상태로 옮기기만 하면 된다(저장소를 직접 알 필요가 없다).
 */
class PrepareSolutionVideoUseCase
    @Inject
    constructor(
        private val repository: SolutionVideoRepository,
    ) {
        operator fun invoke(methodCode: String): Flow<VideoPreparation> =
            channelFlow {
                val video = repository.videoForMethod(methodCode)
                if (video == null) {
                    send(VideoPreparation.Failed)
                    return@channelFlow
                }
                // 캐시에 없을 때만 진행 UI를 띄운다 — 이미 받아 뒀으면 곧바로 재생으로 넘어간다.
                if (!repository.isCached(video)) send(VideoPreparation.Downloading(0, 0))
                val path =
                    repository.ensureLocal(video) { received, total ->
                        trySend(VideoPreparation.Downloading(received, total))
                    }
                send(if (path != null) VideoPreparation.Ready(path) else VideoPreparation.Failed)
            }
    }
