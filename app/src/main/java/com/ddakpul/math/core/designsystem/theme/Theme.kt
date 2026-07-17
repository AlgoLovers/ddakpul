package com.ddakpul.math.core.designsystem.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColorScheme =
    lightColorScheme(
        primary = Violet40,
        onPrimary = Color.White,
        primaryContainer = Violet90,
        onPrimaryContainer = Violet10,
        secondary = Mint40,
        onSecondary = Color.White,
        secondaryContainer = Mint90,
        onSecondaryContainer = Mint10,
        tertiary = Amber40,
        onTertiary = Color.White,
        tertiaryContainer = Amber90,
        onTertiaryContainer = Amber10,
        background = CanvasLight,
        onBackground = Neutral10,
        surface = CanvasLight,
        onSurface = Neutral10,
        surfaceVariant = NeutralVariant90,
        onSurfaceVariant = NeutralVariant30,
        error = Red40,
        onError = Color.White,
        errorContainer = Red90,
        onErrorContainer = Red10,
        outline = NeutralVariant50,
        outlineVariant = NeutralVariant80,
        surfaceContainer = SurfaceContainerLight,
        surfaceContainerHigh = SurfaceContainerHighLight,
    )

private val DarkColorScheme =
    darkColorScheme(
        primary = Violet80,
        onPrimary = Violet20,
        primaryContainer = Violet30,
        onPrimaryContainer = Violet90,
        secondary = Mint80,
        onSecondary = Mint20,
        secondaryContainer = Mint30,
        onSecondaryContainer = Mint90,
        tertiary = Amber80,
        onTertiary = Amber20,
        tertiaryContainer = Amber30,
        onTertiaryContainer = Amber90,
        background = Neutral06,
        onBackground = Neutral90,
        surface = Neutral06,
        onSurface = Neutral90,
        surfaceVariant = NeutralVariant30,
        onSurfaceVariant = NeutralVariant80,
        error = Red80,
        onError = Red20,
        errorContainer = Red30,
        onErrorContainer = Red90,
        outline = NeutralVariant50,
        outlineVariant = NeutralVariant30,
        surfaceContainer = SurfaceContainerDark,
        surfaceContainerHigh = SurfaceContainerHighDark,
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
