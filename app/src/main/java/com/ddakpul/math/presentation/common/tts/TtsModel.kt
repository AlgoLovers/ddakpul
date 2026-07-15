package com.ddakpul.math.presentation.common.tts

import android.content.Context
import java.io.File

/** 다운로드형 신경망 TTS 모델의 파일 하나. [bytes]는 진행률 총량 계산용(대략치). */
data class ModelFile(
    val name: String,
    val bytes: Long,
)

/**
 * 런타임에 내려받는 온디바이스 신경망 TTS 모델. 앱에 내장하지 않고(기본 APK 경량 유지)
 * 파일을 개별로 받아 기기 내부 저장소에 둔다 — 받은 뒤엔 완전 오프라인.
 * 여러 모델을 얹을 수 있게 [TtsModels.ALL]에 나열한다(인터페이스 확장 용이).
 */
data class TtsModel(
    val id: String,
    val displayName: String,
    /** HuggingFace resolve 기준 URL. 파일명을 붙여 개별 다운로드. */
    val baseUrl: String,
    val files: List<ModelFile>,
    /** 라이선스 메모(출시 전 확인용). */
    val licenseNote: String,
) {
    val totalBytes: Long get() = files.sumOf { it.bytes }

    fun url(file: ModelFile): String = "$baseUrl/${file.name}"

    /** 이 모델 파일들이 저장되는 폴더(앱 내부 저장소). */
    fun dir(context: Context): File = File(context.filesDir, "tts/$id")

    /** 필요한 파일이 모두 존재하고 비어 있지 않으면 다운로드 완료로 본다. */
    fun isDownloaded(context: Context): Boolean {
        val dir = dir(context)
        return files.all { File(dir, it.name).let { f -> f.exists() && f.length() > 0 } }
    }
}

object TtsModels {
    /**
     * 엔진 선택값이 이 접두사로 시작하면 신경망 모델을 뜻한다(시스템 TTS 패키지명과 구분).
     * 예: "neural:supertonic-ko-int8". [SpeechSettings]에 이 문자열이 저장된다.
     */
    const val NEURAL_PREFIX = "neural:"

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
