package com.ddakpul.math.architecture

import com.google.common.truth.Truth.assertThat
import org.junit.Test
import java.io.File

/**
 * 계층 경계를 테스트로 못 박는다. 지금까지 이 규칙들은 CLAUDE.md의 글과 사람 리뷰에만
 * 기대고 있었다 — 어기기는 쉽고(import 한 줄) 알아채기는 어렵다.
 *
 * detekt의 ForbiddenImport는 프로젝트 전체에 같은 규칙을 걸어 "domain에서만 금지" 같은
 * 경로별 규칙을 만들 수 없어서, 소스 트리를 직접 읽어 검사한다(추가 의존성 없음).
 */
class ArchitectureRulesTest {
    private data class SourceFile(
        val path: String,
        val imports: List<String>,
        val text: String,
    )

    private val sources: List<SourceFile> by lazy {
        val root =
            sequenceOf(File("src/main/java/com/ddakpul/math"), File("app/src/main/java/com/ddakpul/math"))
                .firstOrNull { it.isDirectory }
        requireNotNull(root) { "소스 트리를 찾지 못했다 — 이 테스트가 조용히 통과하면 안 된다." }
        root
            .walkTopDown()
            .filter { it.isFile && it.extension == "kt" }
            .map { file ->
                val text = file.readText()
                SourceFile(
                    path = file.path.substringAfter("com/ddakpul/math/"),
                    imports =
                        text
                            .lineSequence()
                            .filter { it.startsWith("import ") }
                            .map { it.removePrefix("import ").trim() }
                            .toList(),
                    text = text,
                )
            }.toList()
    }

    private fun layer(prefix: String) = sources.filter { it.path.startsWith(prefix) }

    @Test
    fun `소스 트리를 실제로 읽었다`() {
        assertThat(sources.size).isGreaterThan(MIN_EXPECTED_SOURCES)
    }

    @Test
    fun `domain은 안드로이드 프레임워크에 의존하지 않는다`() {
        val violations =
            layer("domain/").flatMap { file ->
                file.imports
                    .filter { it.startsWith("android.") || it.startsWith("androidx.") }
                    .map { "${file.path} → $it" }
            }

        assertThat(violations).isEmpty()
    }

    @Test
    fun `domain은 바깥 계층을 알지 못한다`() {
        val outerLayers = listOf("com.ddakpul.math.data.", "com.ddakpul.math.presentation.", "com.ddakpul.math.core.", "com.ddakpul.math.ui.")
        val violations =
            layer("domain/").flatMap { file ->
                file.imports
                    .filter { imported -> outerLayers.any { imported.startsWith(it) } }
                    .map { "${file.path} → $it" }
            }

        assertThat(violations).isEmpty()
    }

    @Test
    fun `화면은 data 계층을 직접 알지 못한다`() {
        val violations =
            (layer("presentation/") + layer("ui/") + layer("core/designsystem/")).flatMap { file ->
                file.imports
                    .filter { it.startsWith("com.ddakpul.math.data.") }
                    .map { "${file.path} → $it" }
            }

        assertThat(violations).isEmpty()
    }

    @Test
    fun `ViewModel은 UseCase만 호출한다`() {
        val violations =
            sources
                .filter { it.path.endsWith("ViewModel.kt") }
                .flatMap { file ->
                    file.imports
                        .filter { it.startsWith("com.ddakpul.math.domain.repository.") }
                        .map { "${file.path} → $it" }
                }

        assertThat(violations).isEmpty()
    }

    @Test
    fun `널 단언 연산자를 쓰지 않는다`() {
        val violations =
            sources
                .filter { file -> NOT_NULL_ASSERTION.containsMatchIn(file.text) }
                .map { it.path }

        assertThat(violations).isEmpty()
    }

    private companion object {
        /** 소스 트리를 잘못 짚어 빈 목록을 검사하고 통과하는 사고를 막는 하한. */
        const val MIN_EXPECTED_SOURCES = 100

        /**
         * `!!` 사용 탐지. 문자열 리터럴 안의 느낌표("와!!")와 `!=`는 제외해야 하므로,
         * 식별자·닫는 괄호 바로 뒤에 오는 `!!`만 본다.
         */
        val NOT_NULL_ASSERTION = Regex("""[\w)\]]!!""")
    }
}
