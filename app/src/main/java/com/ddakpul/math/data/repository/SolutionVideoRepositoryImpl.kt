package com.ddakpul.math.data.repository

import android.content.Context
import com.ddakpul.math.domain.model.SolutionVideo
import com.ddakpul.math.domain.repository.SolutionVideoRepository
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import javax.inject.Inject
import javax.inject.Singleton

@Serializable
private data class VideoDto(
    val method: String,
    val title: String,
    val asset: String? = null,
    val url: String? = null,
    val durationSec: Int = 0,
)

@Serializable
private data class VideoManifest(
    val version: Int = 1,
    val videos: List<VideoDto> = emptyList(),
)

/**
 * assets/videos.json 을 읽어 방법코드→영상을 조회한다. 매니페스트에 없는 방법이면 null이라
 * 해당 문제엔 '동영상 풀이 보기' 버튼이 뜨지 않는다(있는 것만 노출). 최초 접근 시 한 번만 파싱.
 */
@Singleton
class SolutionVideoRepositoryImpl
    @Inject
    constructor(
        @ApplicationContext private val context: Context,
    ) : SolutionVideoRepository {
        private val json = Json { ignoreUnknownKeys = true }

        private val byMethod: Map<String, SolutionVideo> by lazy {
            val text =
                runCatching {
                    context.assets
                        .open(MANIFEST)
                        .bufferedReader()
                        .use { it.readText() }
                }.getOrNull() ?: return@lazy emptyMap()
            val manifest = runCatching { json.decodeFromString(VideoManifest.serializer(), text) }.getOrNull()
            manifest
                ?.videos
                ?.mapNotNull { dto ->
                    val uri = dto.asset?.let { "asset:///$it" } ?: dto.url ?: return@mapNotNull null
                    SolutionVideo(dto.method, dto.title, uri, dto.durationSec)
                }?.associateBy { it.methodCode } ?: emptyMap()
        }

        override suspend fun videoForMethod(methodCode: String?): SolutionVideo? = methodCode?.let { byMethod[it] }

        private companion object {
            const val MANIFEST = "videos.json"
        }
    }
