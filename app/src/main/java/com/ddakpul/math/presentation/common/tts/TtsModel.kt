package com.ddakpul.math.presentation.common.tts

import android.content.Context
import java.io.File

/** 다운로드형 신경망 TTS 모델의 파일 하나. [bytes]는 진행률 총량 계산용(대략치). */
data class ModelFile(
    val name: String,
    val bytes: Long,
)

/**
 * 런타임에 내려받는 온디바이스 신경망 TTS 모델. **모델 파일과 네이티브 런타임(.so) 모두 앱에
 * 내장하지 않고** 받는 순간에만 내려받아 기기 내부 저장소에 둔다 — 기본 APK는 가볍게 유지되고
 * (안 쓰는 사용자엔 부담 0), 받은 뒤엔 완전 오프라인.
 *
 * 네이티브 .so는 sherpa-onnx 공식 AAR에서 현재 기기 ABI에 맞는 것만 꺼내 [soFile]에 저장한다.
 * 여러 모델을 얹을 수 있게 [TtsModels.ALL]에 나열한다(인터페이스 확장 용이).
 */
data class TtsModel(
    val id: String,
    val displayName: String,
    /** HuggingFace resolve 기준 URL. 파일명을 붙여 개별 다운로드. */
    val baseUrl: String,
    val files: List<ModelFile>,
    /** sherpa-onnx 정적링크 AAR(모든 ABI 포함) — 여기서 현재 ABI .so만 추출한다. */
    val nativeAarUrl: String,
    /** AAR 크기(진행률 총량 계산용). */
    val nativeAarBytes: Long,
    /** 추출·로드할 네이티브 라이브러리 파일명. */
    val nativeSoName: String,
    /** 라이선스 메모(출시 전 확인용). */
    val licenseNote: String,
) {
    /** 모델 파일 합계(네이티브 제외). */
    val modelBytes: Long get() = files.sumOf { it.bytes }

    /** 진행률 총량 = 모델 파일 + 네이티브 AAR. */
    val totalBytes: Long get() = modelBytes + nativeAarBytes

    fun url(file: ModelFile): String = "$baseUrl/${file.name}"

    /** 이 모델 파일들이 저장되는 폴더(앱 내부 저장소). */
    fun dir(context: Context): File = File(context.filesDir, "tts/$id")

    /** 추출된 네이티브 .so 경로(앱 내부 저장소). */
    fun soFile(context: Context): File = File(File(dir(context), "lib"), nativeSoName)

    /** 모델 파일이 모두 존재하는지. */
    fun isModelDownloaded(context: Context): Boolean {
        val dir = dir(context)
        return files.all { File(dir, it.name).let { f -> f.exists() && f.length() > 0 } }
    }

    /** 모델 + 네이티브 .so까지 모두 있으면 재생 가능(다운로드 완료). */
    fun isDownloaded(context: Context): Boolean = isModelDownloaded(context) && soFile(context).let { it.exists() && it.length() > 0 }
}

object TtsModels {
    /**
     * 엔진 선택값이 이 접두사로 시작하면 신경망 모델을 뜻한다(시스템 TTS 패키지명과 구분).
     * 예: "neural:supertonic-ko-int8". [SpeechSettings]에 이 문자열이 저장된다.
     */
    const val NEURAL_PREFIX = "neural:"

    /** sherpa-onnx 네이티브 런타임(정적링크 AAR, v1.13.4). Tts.kt 소스와 버전 일치 필수. */
    private const val SHERPA_AAR_URL =
        "https://github.com/k2-fsa/sherpa-onnx/releases/download/v1.13.4/sherpa-onnx-static-link-onnxruntime-1.13.4.aar"
    private const val SHERPA_AAR_BYTES = 37_631_864L

    /**
     * Supertonic(한국 Supertone) 한국어 INT8 — sherpa-onnx 배포본. 한국어가 1급이라 자연스럽다.
     * 라이선스: 코드 MIT / 가중치 OpenRAIL-M(상업 허용, 사용 제한조항 있음 — 출시 전 확인).
     */
    val SUPERTONIC =
        TtsModel(
            id = "supertonic-ko-int8",
            displayName = "고품질 음성 (Supertonic)",
            baseUrl = "https://huggingface.co/csukuangfj2/sherpa-onnx-supertonic-tts-int8-2026-03-06/resolve/main",
            files =
                listOf(
                    ModelFile("tts.json", 8_192),
                    ModelFile("unicode_indexer.bin", 262_144),
                    ModelFile("voice.bin", 517_120),
                    ModelFile("duration_predictor.int8.onnx", 1_520_640),
                    ModelFile("vocoder.int8.onnx", 25_977_000),
                    ModelFile("text_encoder.int8.onnx", 27_430_912),
                    ModelFile("vector_estimator.int8.onnx", 40_686_000),
                ),
            nativeAarUrl = SHERPA_AAR_URL,
            nativeAarBytes = SHERPA_AAR_BYTES,
            nativeSoName = "libsherpa-onnx-jni.so",
            licenseNote = "OpenRAIL-M",
        )

    val ALL = listOf(SUPERTONIC)

    /** 엔진 선택값에서 신경망 모델을 찾는다(neural: 접두사 형태). 아니면 null. */
    fun neuralOf(enginePackage: String?): TtsModel? {
        if (enginePackage == null || !enginePackage.startsWith(NEURAL_PREFIX)) return null
        val id = enginePackage.removePrefix(NEURAL_PREFIX)
        return ALL.firstOrNull { it.id == id }
    }

    /** 이 모델을 엔진 선택값으로 저장할 때 쓰는 문자열. */
    fun engineValue(model: TtsModel): String = NEURAL_PREFIX + model.id
}
