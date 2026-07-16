package com.ddakpul.math.presentation.common.tts

import android.content.Context
import android.os.Build
import com.ddakpul.math.R
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream
import java.io.InputStream
import java.net.HttpURLConnection
import java.net.URL
import java.util.zip.ZipFile
import javax.inject.Inject
import javax.inject.Singleton

/** 신경망 TTS 모델 다운로드 상태 — 진행바·재시도 UI가 이걸 관찰한다. */
sealed interface DownloadState {
    data object Idle : DownloadState

    data class Downloading(
        val done: Long,
        val total: Long,
    ) : DownloadState {
        val percent: Int get() = if (total > 0) ((done * 100 / total).toInt()).coerceIn(0, 100) else 0
    }

    data object Done : DownloadState

    data class Failed(
        val message: String,
    ) : DownloadState
}

/**
 * 신경망 TTS 모델을 런타임에 내려받아 기기 내부 저장소에 둔다(기본 APK 경량 유지, 받은 뒤 오프라인).
 * 여러 모델을 얹을 수 있는 구조 — [TtsModels]에 추가만 하면 된다.
 * 다운로드에는 INTERNET 권한이 필요하다(핵심 기능은 여전히 오프라인, 이 선택 기능만 1회 네트워크).
 */
@Singleton
class TtsModelManager
    @Inject
    constructor(
        @ApplicationContext private val context: Context,
    ) {
        private val _state = MutableStateFlow<DownloadState>(DownloadState.Idle)
        val state: StateFlow<DownloadState> = _state.asStateFlow()

        fun isDownloaded(model: TtsModel): Boolean = model.isDownloaded(context)

        suspend fun download(model: TtsModel) =
            withContext(Dispatchers.IO) {
                val dir = model.dir(context).apply { mkdirs() }
                val total = model.totalBytes
                var done = 0L
                _state.value = DownloadState.Downloading(0, total)
                runCatching {
                    for (file in model.files) {
                        val target = File(dir, file.name)
                        if (target.exists() && target.length() > 0) {
                            done += file.bytes
                            _state.value = DownloadState.Downloading(done, total)
                            continue
                        }
                        done = downloadFile(model.url(file), File(dir, "${file.name}.part"), target, done, total)
                    }
                    // 네이티브 런타임(.so)도 받아서 현재 기기 ABI에 맞는 것만 추출한다.
                    ensureNativeLib(model, dir, done, total)
                    _state.value = DownloadState.Done
                }.onFailure { e ->
                    _state.value = DownloadState.Failed(e.message ?: context.getString(R.string.tts_error_download_failed))
                }
            }

        /** sherpa-onnx AAR을 받아 현재 ABI의 .so만 꺼내 [TtsModel.soFile]에 둔다. AAR은 지운다. */
        private fun ensureNativeLib(
            model: TtsModel,
            dir: File,
            startDone: Long,
            total: Long,
        ): Long {
            val so = model.soFile(context)
            if (so.exists() && so.length() > 0) return startDone + model.nativeAarBytes
            so.parentFile?.mkdirs()
            val abi = Build.SUPPORTED_ABIS.firstOrNull() ?: error(context.getString(R.string.tts_error_no_abi))
            val aar = File(dir, "sherpa.aar")
            val done = downloadFile(model.nativeAarUrl, File(dir, "sherpa.aar.part"), aar, startDone, total)
            extractSo(aar, "jni/$abi/${model.nativeSoName}", so)
            aar.delete()
            return done
        }

        /** AAR(zip)에서 한 항목을 꺼내 [target]에 저장(.part→rename). */
        private fun extractSo(
            aar: File,
            entryPath: String,
            target: File,
        ) {
            ZipFile(aar).use { zip ->
                val entry = zip.getEntry(entryPath) ?: error(context.getString(R.string.tts_error_no_lib, entryPath))
                zip.getInputStream(entry).use { input -> writeToFile(input, target) }
            }
        }

        private fun writeToFile(
            input: InputStream,
            target: File,
        ) {
            val tmp = File(target.parentFile, "${target.name}.part")
            FileOutputStream(tmp).use { out -> input.copyTo(out) }
            check(tmp.renameTo(target)) { context.getString(R.string.tts_error_save_failed, target.name) }
        }

        /** 파일 하나를 .part로 받아 완료 시 이름 바꿈. 반환값은 갱신된 누적 바이트. */
        private fun downloadFile(
            url: String,
            tmp: File,
            target: File,
            startDone: Long,
            total: Long,
        ): Long {
            val conn =
                (URL(url).openConnection() as HttpURLConnection).apply {
                    connectTimeout = CONNECT_TIMEOUT
                    readTimeout = READ_TIMEOUT
                    instanceFollowRedirects = true
                }
            val done =
                try {
                    conn.inputStream.use { input -> copyWithProgress(input, tmp, startDone, total) }
                } finally {
                    conn.disconnect()
                }
            check(tmp.renameTo(target)) { context.getString(R.string.tts_error_save_failed, target.name) }
            return done
        }

        private fun copyWithProgress(
            input: java.io.InputStream,
            tmp: File,
            startDone: Long,
            total: Long,
        ): Long {
            var done = startDone
            FileOutputStream(tmp).use { out ->
                val buffer = ByteArray(BUFFER_SIZE)
                var read = input.read(buffer)
                while (read >= 0) {
                    out.write(buffer, 0, read)
                    done += read
                    _state.value = DownloadState.Downloading(done, total)
                    read = input.read(buffer)
                }
            }
            return done
        }

        fun delete(model: TtsModel) {
            model.dir(context).deleteRecursively()
            _state.value = DownloadState.Idle
        }

        private companion object {
            const val CONNECT_TIMEOUT = 30_000
            const val READ_TIMEOUT = 30_000
            const val BUFFER_SIZE = 64 * 1024
        }
    }
