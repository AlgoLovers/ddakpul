# Add project specific ProGuard rules here.
# By default, the flags in this file are appended to flags specified
# in $ANDROID_HOME/tools/proguard/proguard-android.txt

# kotlinx.serialization: keep generated serializers for @Serializable data-layer DTOs.
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.**
-keepclassmembers class com.ddakpul.math.data.** {
    *** Companion;
}
-keepclasseswithmembers class com.ddakpul.math.data.** {
    kotlinx.serialization.KSerializer serializer(...);
}

# sherpa-onnx JNI: 네이티브(libsherpa-onnx-jni.so)가 이 클래스들을 "이름으로" 호출한다
# (external fun 네이티브 메서드 + generateWithCallback 콜백). R8이 리네이밍/삭제하면 TTS가 크래시나므로 전부 보존.
-keep class com.k2fsa.sherpa.onnx.** { *; }
