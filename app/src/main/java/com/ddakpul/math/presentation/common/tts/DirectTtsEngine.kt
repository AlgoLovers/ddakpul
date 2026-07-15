package com.ddakpul.math.presentation.common.tts

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.os.Binder
import android.os.Bundle
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.os.Parcel
import android.speech.tts.TextToSpeech
import android.text.TextUtils
import android.util.Log

/**
 * TTS 엔진 서비스에 **직접 바인딩**해 읽는 백엔드(우회). 안드로이드 TextToSpeech.getEngines()가
 * 삼성 등을 걸러내(MATCH_DEFAULT_ONLY) 표준 API로는 삼성을 못 부르는 기기(S24/Android16)를 위한 것.
 *
 * 프레임워크의 숨은 `ITextToSpeechService`(비-SDK)를 참조하면 런타임 제한에 걸리므로, **원시 Binder
 * 트랜잭션**으로 직접 speak를 호출한다(디스크립터·마샬링을 손으로 맞춤). 실패해도 크래시하지 않고
 * [onUnavailable]로 알려 시스템 음성으로 폴백한다.
 */
class DirectTtsEngine(
    context: Context,
    private val enginePackage: String,
    override val label: String,
    private val onSpeakingChanged: (Boolean) -> Unit,
    private val onUnavailable: () -> Unit,
) : SpeechEngine {
    private val appContext = context.applicationContext
    private val mainHandler = Handler(Looper.getMainLooper())
    private val callerToken = Binder()

    @Volatile
    private var service: IBinder? = null

    @Volatile
    private var pendingText: String? = null

    private val connection =
        object : ServiceConnection {
            override fun onServiceConnected(
                name: ComponentName?,
                binder: IBinder?,
            ) {
                service = binder
                pendingText?.let { text ->
                    pendingText = null
                    doSpeak(text)
                }
            }

            override fun onServiceDisconnected(name: ComponentName?) {
                service = null
            }
        }

    init {
        val bound =
            runCatching {
                val intent = Intent(INTENT_ACTION_TTS_SERVICE).setPackage(enginePackage)
                appContext.bindService(intent, connection, Context.BIND_AUTO_CREATE)
            }.getOrDefault(false)
        if (!bound) {
            Log.w(TAG, "$enginePackage TTS 서비스 바인딩 실패 — 폴백")
            mainHandler.post { onUnavailable() }
        }
    }

    override fun speak(text: String) {
        if (service == null) {
            pendingText = text // 연결되면 말한다
            return
        }
        doSpeak(text)
    }

    private fun doSpeak(text: String) {
        val target = service ?: return
        val ok = runCatching { transactSpeak(target, text) }.getOrElse { false }
        if (ok) {
            mainHandler.post { onSpeakingChanged(true) }
        } else {
            Log.w(TAG, "$enginePackage speak 실패 — 폴백")
            mainHandler.post {
                onSpeakingChanged(false)
                onUnavailable()
            }
        }
    }

    /** ITextToSpeechService.speak(트랜잭션 0)를 원시 Binder로 호출. */
    private fun transactSpeak(
        target: IBinder,
        text: String,
    ): Boolean {
        val data = Parcel.obtain()
        val reply = Parcel.obtain()
        return try {
            data.writeInterfaceToken(SERVICE_DESCRIPTOR)
            data.writeStrongBinder(callerToken) // in IBinder callingInstance
            data.writeInt(1) // CharSequence 널마커
            TextUtils.writeToParcel(text, data, 0) // in CharSequence text
            data.writeInt(TextToSpeech.QUEUE_FLUSH) // in int queueMode
            data.writeInt(1) // Bundle 널마커
            Bundle().writeToParcel(data, 0) // in Bundle params(빈 번들)
            data.writeString("ddakpul") // String utteranceId
            target.transact(TRANSACTION_SPEAK, data, reply, 0)
            reply.readException()
            reply.readInt() == TextToSpeech.SUCCESS
        } finally {
            data.recycle()
            reply.recycle()
        }
    }

    override fun stop() {
        onSpeakingChanged(false)
        val target = service ?: return
        runCatching {
            val data = Parcel.obtain()
            val reply = Parcel.obtain()
            try {
                data.writeInterfaceToken(SERVICE_DESCRIPTOR)
                data.writeStrongBinder(callerToken)
                target.transact(TRANSACTION_STOP, data, reply, 0)
                reply.readException()
            } finally {
                data.recycle()
                reply.recycle()
            }
        }
    }

    override fun release() {
        pendingText = null
        runCatching { appContext.unbindService(connection) }
        service = null
    }

    private companion object {
        const val TAG = "DirectTtsEngine"
        const val INTENT_ACTION_TTS_SERVICE = "android.intent.action.TTS_SERVICE"
        const val SERVICE_DESCRIPTOR = "android.speech.tts.ITextToSpeechService"

        // 트랜잭션 코드 = AOSP ITextToSpeechService 메서드 순서.
        // 0:speak 1:synthesizeToFileDescriptor 2:playAudio 3:playSilence 4:stop ...
        const val TRANSACTION_SPEAK = IBinder.FIRST_CALL_TRANSACTION + 0
        const val TRANSACTION_STOP = IBinder.FIRST_CALL_TRANSACTION + 4
    }
}
