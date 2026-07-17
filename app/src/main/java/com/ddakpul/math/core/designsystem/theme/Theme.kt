package com.ddakpul.math.core.designsystem.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColorScheme =
    lightColorScheme(
        primary = Accent,
        onPrimary = Color.White,
        primaryContainer = AccentSoft,
        onPrimaryContainer = AccentDark,
        secondary = Mint,
        onSecondary = Color.White,
        secondaryContainer = MintSoft,
        onSecondaryContainer = MintDark,
        tertiary = Amber,
        onTertiary = Color.White,
        tertiaryContainer = AmberSoft,
        onTertiaryContainer = AmberDark,
        background = CanvasLight,
        onBackground = InkLight,
        surface = CanvasLight,
        onSurface = InkLight,
        surfaceVariant = CardHighLight,
        onSurfaceVariant = BodyLight,
        error = Coral,
        onError = Color.White,
        errorContainer = CoralSoft,
        onErrorContainer = CoralDark,
        outline = OutlineLight,
        outlineVariant = BorderLight,
        surfaceContainer = CardLight,
        surfaceContainerHigh = CardHighLight,
    )

private val DarkColorScheme =
    darkColorScheme(
        primary = AccentLight,
        onPrimary = Color(0xFF23246E),
        primaryContainer = Color(0xFF3B3CA6),
        onPrimaryContainer = AccentSoft,
        secondary = MintLight,
        onSecondary = Color(0xFF00382A),
        secondaryContainer = Color(0xFF0B5A3B),
        onSecondaryContainer = MintSoft,
        tertiary = AmberLight,
        onTertiary = Color(0xFF3E2600),
        tertiaryContainer = Color(0xFF5A3A00),
        onTertiaryContainer = AmberSoft,
        background = CanvasDark,
        onBackground = InkDark,
        surface = CanvasDark,
        onSurface = InkDark,
        surfaceVariant = CardHighDark,
        onSurfaceVariant = BodyDark,
        error = CoralLight,
        onError = Color(0xFF5A1512),
        errorContainer = Color(0xFF7A1712),
        onErrorContainer = CoralSoft,
        outline = OutlineDark,
        outlineVariant = BorderDark,
        surfaceContainer = CardDark,
        surfaceContainerHigh = CardHighDark,
    )

@Composable
fun DdakPulTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    MaterialTheme(
        colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme,
        typography = Typography,
        content = content,
    )
}
