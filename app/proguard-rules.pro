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
