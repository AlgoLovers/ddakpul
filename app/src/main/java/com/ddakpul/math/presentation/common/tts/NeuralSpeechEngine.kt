package com.ddakpul.math.presentation.common.tts

import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioTrack
import android.os.Handler
import android.os.Looper
import android.util.Log
import com.k2fsa.sherpa.onnx.OfflineTts
import com.k2fsa.sherpa.onnx.OfflineTtsConfig
import com.k2fsa.sherpa.onnx.OfflineTtsModelConfig
import com.k2fsa.sherpa.onnx.OfflineTtsSupertonicModelConfig
import java.io.File
import java.util.concurrent.Executors

/**
 * 온디바이스 신경망 TTS(Supertonic) 백엔드 — [SpeechEngine] 구현체.
 * 다운로드한 모델 파일을 sherpa-onnx `OfflineTts`로 로드해 합성하고 AudioTrack으로 재생한다.
 * 무거운 작업(모델 로드·합성)은 전부 단일 백그라운드 스레드에서 처리한다.
 *
 * 안전 원칙: 초기화·합성 실패(ABI 불일치·모델 손상·네이티브 로드 실패 등)에서 **절대 크래시하지
 * 않고** 조용히 무시한다. 초기화가 실패하면 [onUnavailable]로 알려, 화면이 시스템 음성으로
 * 자동 폴백하도록 한다(사용자가 무음을 겪지 않게).
 */
class NeuralSpeechEngine(
    private val modelDir: File,
    private val speed: Float,
    override val label: String,
    private val onSpeakingChanged: (Boolean) -> Unit,
    private val onUnavailable: () -> Unit,
) : SpeechEngine {
    private val mainHandler = Handler(Looper.getMainLooper())
    private val worker = Executors.newSingleThreadExecutor()

    @Volatile
    private var tts: OfflineTts? = null

    @Volatile
    private var initFailed = false

    @Volatile
    private var track: AudioTrack? = null

    /** 재생 세대(id) — stop()/새 speak()가 증가시켜 진행 중인 합성·재생을 무효화한다. */
    @Volatile
    private var generation = 0

    init {
        worker.execute { ensureTts() }
    }

    private fun ensureTts() {
        if (tts != null || initFailed) return
        runCatching { OfflineTts(assetManager = null, config = buildConfig()) }
            .onSuccess { tts = it }
            .onFailure { error ->
                Log.w(TAG, "Supertonic 초기화 실패 — 시스템 음성으로 폴백", error)
                initFailed = true
                mainHandler.post { onUnavailable() }
            }
    }

    private fun buildConfig(): OfflineTtsConfig {
        fun path(name: String) = File(modelDir, name).absolutePath
        return OfflineTtsConfig(
            model =
                OfflineTtsModelConfig(
                    supertonic =
                        OfflineTtsSupertonicModelConfig(
                            durationPredictor = path("duration_predictor.int8.onnx"),
                            textEncoder = path("text_encoder.int8.onnx"),
                            vectorEstimator = path("vector_estimator.int8.onnx"),
                            vocoder = path("vocoder.int8.onnx"),
                            ttsJson = path("tts.json"),
                            unicodeIndexer = path("unicode_indexer.bin"),
                            voiceStyle = path("voice.bin"),
                        ),
                    numThreads = NUM_THREADS,
                    provider = "cpu",
                ),
        )
    }

    override fun speak(text: String) {
        val gen = ++generation
        worker.execute {
            ensureTts()
            val engine = tts ?: return@execute
            if (gen != generation) return@execute
            mainHandler.post { onSpeakingChanged(true) }
            runCatching {
                val audio = engine.generate(text = text, sid = 0, speed = speed)
                if (gen == generation) playSamples(audio.samples, audio.sampleRate, gen)
            }.onFailure { Log.w(TAG, "Supertonic 합성 실패", it) }
            mainHandler.post { onSpeakingChanged(false) }
        }
    }

    private fun playSamples(
        samples: FloatArray,
        sampleRate: Int,
        gen: Int,
    ) {
        if (samples.isEmpty()) return
        val newTrack = buildTrack(sampleRate)
        track = newTrack
        newTrack.play()
        writeAll(newTrack, samples, gen)
        drain(newTrack, samples.size, gen)
        runCatching {
            newTrack.pause()
            newTrack.flush()
            newTrack.stop()
        }
        newTrack.release()
        if (track === newTrack) track = null
    }

    private fun buildTrack(sampleRate: Int): AudioTrack {
        val minBuf = AudioTrack.getMinBufferSize(sampleRate, AudioFormat.CHANNEL_OUT_MONO, AudioFormat.ENCODING_PCM_FLOAT)
        return AudioTrack
            .Builder()
            .setAudioAttributes(
                AudioAttributes
                    .Builder()
                    .setUsage(AudioAttributes.USAGE_MEDIA)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                    .build(),
            ).setAudioFormat(
                AudioFormat
                    .Builder()
                    .setEncoding(AudioFormat.ENCODING_PCM_FLOAT)
                    .setSampleRate(sampleRate)
                    .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                    .build(),
            ).setBufferSizeInBytes(maxOf(minBuf, CHUNK * Float.SIZE_BYTES))
            .setTransferMode(AudioTrack.MODE_STREAM)
            .build()
    }

    /** 청크 단위로 써서 stop()이 중간에 끊을 수 있게 한다. */
    private fun writeAll(
        t: AudioTrack,
        samples: FloatArray,
        gen: Int,
    ) {
        var offset = 0
        while (offset < samples.size && gen == generation) {
            val n = minOf(CHUNK, samples.size - offset)
            val written = t.write(samples, offset, n, AudioTrack.WRITE_BLOCKING)
            if (written < 0) break
            offset += n
        }
    }

    /** 버퍼에 남은 소리가 다 나갈 때까지 대기(끊김 방지). 진행이 멎으면 안전 탈출. */
    private fun drain(
        t: AudioTrack,
        totalFrames: Int,
        gen: Int,
    ) {
        var lastHead = -1
        var stall = 0
        while (gen == generation && t.playbackHeadPosition < totalFrames && stall < STALL_LIMIT) {
            val head = t.playbackHeadPosition
            if (head == lastHead) {
                stall++
            } else {
                stall = 0
                lastHead = head
            }
            runCatching { Thread.sleep(POLL_MS) }
        }
    }

    override fun stop() {
        generation++
        onSpeakingChanged(false)
        runCatching {
            track?.pause()
            track?.flush()
        }
    }

    override fun release() {
        generation++
        runCatching {
            track?.pause()
            track?.flush()
            track?.release()
        }
        track = null
        worker.execute {
            runCatching { tts?.release() }
            tts = null
        }
        worker.shutdown()
    }

    private companion object {
        const val TAG = "NeuralSpeechEngine"
        const val NUM_THREADS = 2
        const val CHUNK = 4096
        const val POLL_MS = 20L
        const val STALL_LIMIT = 100
    }
}
