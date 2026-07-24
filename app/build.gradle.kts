import java.io.FileInputStream
import java.net.URL
import java.security.MessageDigest
import java.util.Properties
import java.util.zip.ZipFile

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.kotlin.serialization)
    alias(libs.plugins.detekt)
    alias(libs.plugins.ksp)
    alias(libs.plugins.hilt)
}

// ── sherpa-onnx 네이티브 런타임(.so)을 빌드 시점에 받아 AAB에 동봉한다 ─────────────────
// Google Play 정책상 실행 코드(.so)는 스토어 밖에서 런타임 다운로드가 금지라(Device & Network
// Abuse), 모델 파일(데이터)만 런타임에 받고 .so는 앱과 함께 배포한다. AAB의 ABI 분할 덕에
// 기기당 추가 용량은 자기 ABI 한 벌(arm64 기준 ~22MB)이다. 해시 고정으로 공급망 변조를 막는다.
val sherpaAarUrl =
    "https://github.com/k2-fsa/sherpa-onnx/releases/download/v1.13.4/" +
        "sherpa-onnx-static-link-onnxruntime-1.13.4.aar"
val sherpaAarSha256 = "dc5ac19a28dee3bffc5e5a5d50cb6afa977703fc4a7ee535a308506990fdd295"
val sherpaJniDir = layout.buildDirectory.dir("sherpaJniLibs")

val fetchSherpaJni =
    tasks.register("fetchSherpaJni") {
        description = "sherpa-onnx AAR을 받아(해시 검증) 모든 ABI의 .so를 jniLibs로 추출한다"
        outputs.dir(sherpaJniDir)
        doLast {
            val outDir = sherpaJniDir.get().asFile
            val marker = File(outDir, ".ok-1.13.4")
            if (marker.exists()) return@doLast
            outDir.mkdirs()
            val aar = File(outDir, "sherpa.aar")
            URL(sherpaAarUrl).openStream().use { input ->
                aar.outputStream().use { output -> input.copyTo(output) }
            }
            val digest = MessageDigest.getInstance("SHA-256")
            aar.inputStream().use { input ->
                val buf = ByteArray(1 shl 16)
                var n = input.read(buf)
                while (n >= 0) {
                    digest.update(buf, 0, n)
                    n = input.read(buf)
                }
            }
            val hex = digest.digest().joinToString("") { "%02x".format(it) }
            check(hex == sherpaAarSha256) { "sherpa AAR 해시 불일치: $hex (변조/버전 변경 의심)" }
            ZipFile(aar).use { zip ->
                zip
                    .entries()
                    .asSequence()
                    .filter { it.name.startsWith("jni/") && it.name.endsWith(".so") }
                    .forEach { entry ->
                        // jni/<abi>/<lib>.so → jniLibs/<abi>/<lib>.so (x86는 .so가 2개라 전부 추출)
                        val target = File(outDir, "jniLibs/" + entry.name.removePrefix("jni/"))
                        target.parentFile.mkdirs()
                        zip.getInputStream(entry).use { input ->
                            target.outputStream().use { output -> input.copyTo(output) }
                        }
                    }
            }
            aar.delete()
            marker.writeText("ok")
        }
    }

// 업로드 키 정보는 gitignore된 keystore.properties에서만 읽는다(비밀번호를 저장소에 넣지 않기 위함).
// 이 파일이 없으면(CI 등) 릴리스 빌드는 디버그 키로 폴백해 빌드 자체는 통과한다.
val keystorePropsFile = rootProject.file("keystore.properties")
val keystoreProps =
    Properties().apply {
        if (keystorePropsFile.exists()) FileInputStream(keystorePropsFile).use { load(it) }
    }
val hasUploadKey = keystorePropsFile.exists()

android {
    namespace = "com.ddakpul.math"
    compileSdk = 36

    lint {
        // compose-lints는 가드레일 — 위반은 보되 릴리스 빌드를 막지는 않는다(솔로·프리런치).
        // 성능 권고(불안정 컬렉션/리시버 등)는 출시 후 백로그. 진짜 문제는 리뷰에서 대응한다.
        warningsAsErrors = false
        abortOnError = false
        // 의존성 최신버전 안내는 소음이라 뺀다(업그레이드는 의도적으로 관리).
        disable += setOf("GradleDependency", "NewerVersionAvailable", "AndroidGradlePluginVersion")
    }

    defaultConfig {
        applicationId = "com.ddakpul.math"
        minSdk = 26
        targetSdk = 36
        versionCode = 11
        versionName = "0.3.9"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    signingConfigs {
        getByName("debug") {
            storeFile = file("debug.keystore")
            storePassword = "android"
            keyAlias = "androiddebugkey"
            keyPassword = "android"
        }
        if (hasUploadKey) {
            create("release") {
                storeFile = rootProject.file(keystoreProps.getProperty("storeFile"))
                storePassword = keystoreProps.getProperty("storePassword")
                keyAlias = keystoreProps.getProperty("keyAlias")
                keyPassword = keystoreProps.getProperty("keyPassword")
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro",
            )
            // Play Console '네이티브 디버그 심볼 없음' 경고 해소 — .so 심볼을 AAB에 포함(크래시 분석용).
            ndk {
                debugSymbolLevel = "FULL"
            }
            // 업로드 키가 있으면 그것으로, 없으면(CI) 디버그 키로 서명해 빌드는 항상 통과.
            signingConfig =
                if (hasUploadKey) {
                    signingConfigs.getByName("release")
                } else {
                    signingConfigs.getByName("debug")
                }
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    // 텔레그램 배달용 단일 ABI 빌드(-PabiSplit): 4개 ABI 동봉 시 111MB로 봇 한도(50MB) 초과.
    // 평소 빌드에는 영향 없음 — CI의 배달 스텝만 이 속성을 켠다.
    if (project.hasProperty("abiSplit")) {
        splits {
            abi {
                isEnable = true
                reset()
                include("arm64-v8a")
                isUniversalApk = false
            }
        }
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    // 빌드 시점에 받은 sherpa-onnx .so를 앱 네이티브 라이브러리로 포함(AAB가 ABI별 분할 배포).
    sourceSets["main"].jniLibs.srcDir(sherpaJniDir.map { it.dir("jniLibs") })
}

tasks.named("preBuild") { dependsOn(fetchSherpaJni) }

detekt {
    buildUponDefaultConfig = true
    allRules = false
    config.setFrom(files("$rootDir/config/detekt/detekt.yml"))
}

// 벤더링한 sherpa-onnx Kotlin 바인딩(외부 코드)은 정적분석 제외.
tasks.withType<io.gitlab.arturbosch.detekt.Detekt>().configureEach {
    exclude("**/com/k2fsa/**")
}

dependencies {
    // 온디바이스 신경망 TTS(Supertonic)는 sherpa-onnx 1.13.4 Kotlin 바인딩(com.k2fsa.sherpa.onnx.Tts)을
    // 소스로 포함하고, 네이티브 .so는 APK에 넣지 않는다 — 모델과 함께 런타임에 받아 filesDir에서 로드해
    // 기본 APK를 가볍게 유지한다(안 쓰는 사용자엔 부담 0).
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.lifecycle.runtime.compose)
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    implementation(libs.androidx.material3.window.size)
    implementation(libs.androidx.material.icons.extended)
    implementation(libs.androidx.navigation.compose)
    implementation(libs.androidx.media3.exoplayer)
    implementation(libs.androidx.media3.ui)

    implementation(libs.hilt.android)
    implementation(libs.androidx.hilt.navigation.compose)
    ksp(libs.hilt.compiler)

    implementation(libs.androidx.room.runtime)
    implementation(libs.androidx.room.ktx)
    ksp(libs.androidx.room.compiler)

    implementation(libs.kotlinx.serialization.json)

    // Compose 디자인/안정성 린트 — 모디파이어 순서·하드코딩 파라미터·상태 안정성 등 위험 패턴을
    // Android Lint 단계에서 잡는다(런타임 비용 0, 코드 변경 불필요한 드롭인 가드레일).
    lintChecks(libs.compose.lints)

    testImplementation(libs.junit)
    testImplementation(libs.kotlinx.coroutines.test)
    testImplementation(libs.turbine)
    testImplementation(libs.truth)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.ui.test.junit4)
    debugImplementation(libs.androidx.ui.tooling)
    debugImplementation(libs.androidx.ui.test.manifest)
}
