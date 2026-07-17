package com.ddakpul.math.data.repository

import android.content.Context
import com.ddakpul.math.domain.model.SolutionVideo
import com.ddakpul.math.domain.repository.SolutionVideoRepository
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.io.File
import java.io.FileOutputStream
import java.io.InputStream
import java.net.HttpURLConnection
import java.net.URL
import javax.inject.Inject
import javax.inject.Singleton

@Serializable
private data class VideoDto(
    val method: String,
    val title: String,
    val url: String,
    val version: Int = 1,
    val durationSec: Int = 0,
)

@Serializable
private data class VideoManifest(
    val version: Int = 1,
    val videos: List<VideoDto> = emptyList(),
)

/**
 * 해설 영상 저장소 — 영상은 APK에 넣지 않고 1회 다운로드 후 캐시한다.
 *
 * - 매니페스트: 원격(Pages)을 [MANIFEST_TTL_MILLIS]마다 갱신해 앱 업데이트 없이 새 영상 추가.
 *   오프라인이면 마지막 사본, 그것도 없으면 내장 시드(assets/videos.json).
 * - 영상 캐시: files/videos/<method>-v<version>.mp4. 버전이 오르면 새 파일을 받고 옛 버전 삭제.
 * - 다운로드 완결성: Content-Length 대조 후 .part→확정 (TTS 모델과 동일 규약).
 */
@Singleton
class SolutionVideoRepositoryImpl
    @Inject
    constructor(
        @ApplicationContext private val context: Context,
    ) : SolutionVideoRepository {
        private val json = Json { ignoreUnknownKeys = true }
        private val manifestMutex = Mutex()

        @Volatile
        private var cachedManifest: Map<String, SolutionVideo>? = null

        @Volatile
        private var manifestLoadedAt: Long = 0L

        private fun videoDir(): File = File(context.filesDir, VIDEO_DIR).apply { mkdirs() }

        private fun manifestFile(): File = File(videoDir(), MANIFEST_FILE)

        private fun localFile(video: SolutionVideo): File = File(videoDir(), "${video.methodCode}-v${video.version}.mp4")

        override suspend fun videoForMethod(methodCode: String?): SolutionVideo? {
            if (methodCode == null) return null
            return loadManifest()[methodCode]
        }

        override fun isCached(video: SolutionVideo): Boolean = localFile(video).let { it.exists() && it.length() > 0 }

        override suspend fun ensureLocal(
            video: SolutionVideo,
            onProgress: (Long, Long) -> Unit,
        ): String? =
            withContext(Dispatchers.IO) {
                val target = localFile(video)
                if (target.exists() && target.length() > 0) return@withContext target.absolutePath
                runCatching {
                    downloadWithIntegrity(video.url, target, onProgress)
                    // 같은 방법의 옛 버전 캐시 정리 — 버전이 오르면 저장 공간을 두 배로 쓰지 않게.
                    videoDir()
                        .listFiles { f -> f.name.startsWith("${video.methodCode}-v") && f.name != target.name }
                        ?.forEach { it.delete() }
                    target.absolutePath
                }.getOrNull()
            }

        /** 매니페스트 로드: 메모리(TTL 내) → 원격 갱신 → 로컬 사본 → 내장 시드. */
        private suspend fun loadManifest(): Map<String, SolutionVideo> =
            manifestMutex.withLock {
                val now = System.currentTimeMillis()
                cachedManifest?.let { if (now - manifestLoadedAt < MANIFEST_TTL_MILLIS) return it }
                val remote = withContext(Dispatchers.IO) { fetchRemoteManifest() }
                val parsed =
                    remote
                        ?: readManifestText(manifestFile())
                        ?: readSeedManifest()
                val map = parsed?.let(::toMap) ?: emptyMap()
                if (map.isNotEmpty() || remote != null) {
                    cachedManifest = map
                    manifestLoadedAt = now
                }
                map
            }

        /** 원격 매니페스트를 받아 로컬 사본으로 저장. 실패(오프라인 등)하면 null — 폴백 체인이 잇는다. */
        private fun fetchRemoteManifest(): VideoManifest? =
            runCatching {
                val conn =
                    (URL(MANIFEST_URL).openConnection() as HttpURLConnection).apply {
                        connectTimeout = CONNECT_TIMEOUT
                        readTimeout = READ_TIMEOUT
                        instanceFollowRedirects = true
                    }
                try {
                    val text = conn.inputStream.use { it.readBytes().decodeToString() }
                    val parsed = json.decodeFromString(VideoManifest.serializer(), text)
                    manifestFile().writeText(text)
                    parsed
                } finally {
                    conn.disconnect()
                }
            }.getOrNull()

        private fun readManifestText(file: File): VideoManifest? =
            runCatching {
                json.decodeFromString(VideoManifest.serializer(), file.readText())
            }.getOrNull()

        private fun readSeedManifest(): VideoManifest? =
            runCatching {
                val text =
                    context.assets
                        .open(SEED_ASSET)
                        .bufferedReader()
                        .use { it.readText() }
                json.decodeFromString(VideoManifest.serializer(), text)
            }.getOrNull()

        private fun toMap(manifest: VideoManifest): Map<String, SolutionVideo> =
            manifest.videos
                .map { SolutionVideo(it.method, it.title, it.url, it.version, it.durationSec) }
                .associateBy { it.methodCode }

        /** Content-Length 대조 후 .part→확정 — 잘린 파일이 캐시로 남는 것을 막는다. */
        private fun downloadWithIntegrity(
            url: String,
            target: File,
            onProgress: (Long, Long) -> Unit,
        ) {
            val tmp = File(target.parentFile, "${target.name}.part")
            val conn =
                (URL(url).openConnection() as HttpURLConnection).apply {
                    connectTimeout = CONNECT_TIMEOUT
                    readTimeout = READ_TIMEOUT
                    instanceFollowRedirects = true
                }
            try {
                val expected = conn.contentLengthLong
                val received = conn.inputStream.use { input -> copyWithProgress(input, tmp, expected, onProgress) }
                check(expected <= 0 || received == expected) { "download truncated ($received/$expected bytes)" }
                check(tmp.renameTo(target)) { "rename failed: ${target.name}" }
            } finally {
                conn.disconnect()
                tmp.delete()
            }
        }

        private fun copyWithProgress(
            input: InputStream,
            tmp: File,
            total: Long,
            onProgress: (Long, Long) -> Unit,
        ): Long {
            var done = 0L
            FileOutputStream(tmp).use { out ->
                val buffer = ByteArray(BUFFER_SIZE)
                var read = input.read(buffer)
                while (read >= 0) {
                    out.write(buffer, 0, read)
                    done += read
                    onProgress(done, total)
                    read = input.read(buffer)
                }
            }
            return done
        }

        private companion object {
            const val MANIFEST_URL = "https://algolovers.github.io/ddakpul/videos/manifest.json"
            const val SEED_ASSET = "videos.json"
            const val VIDEO_DIR = "videos"
            const val MANIFEST_FILE = "manifest.json"

            /** 원격 매니페스트 재확인 주기 — 세션 중 반복 네트워크 접근을 막는다. */
            const val MANIFEST_TTL_MILLIS = 6 * 60 * 60 * 1000L
            const val CONNECT_TIMEOUT = 15_000
            const val READ_TIMEOUT = 30_000
            const val BUFFER_SIZE = 64 * 1024
        }
    }
