package com.travlytic.app.ui.theme

import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// ─── Paleta de colores Travlytic ────────────────────────────────────────────
val TravlyticBlue = Color(0xFF1A73E8)
val TravlyticBlueDark = Color(0xFF0D47A1)
val TravlyticBlueLight = Color(0xFF4DA3FF)
val TravlyticGreen = Color(0xFF00C853)
val TravlyticGreenLight = Color(0xFF69F0AE)
val TravlyticRed = Color(0xFFE53935)
val TravlyticOrange = Color(0xFFFF6D00)
val TravlyticSurface = Color(0xFF0F1923)
val TravlyticSurface2 = Color(0xFF1A2738)
val TravlyticSurface3 = Color(0xFF243447)
val TravlyticOnSurface = Color(0xFFE8EDF3)
val TravlyticOnSurface2 = Color(0xFF9EAFC4)

// ─── Color Scheme (Dark) ─────────────────────────────────────────────────────
private val DarkColorScheme = darkColorScheme(
    primary = TravlyticBlue,
    onPrimary = Color.White,
    primaryContainer = TravlyticBlueDark,
    onPrimaryContainer = TravlyticBlueLight,
    secondary = TravlyticGreen,
    onSecondary = Color.Black,
    secondaryContainer = Color(0xFF003820),
    onSecondaryContainer = TravlyticGreenLight,
    background = TravlyticSurface,
    onBackground = TravlyticOnSurface,
    surface = TravlyticSurface2,
    onSurface = TravlyticOnSurface,
    surfaceVariant = TravlyticSurface3,
    onSurfaceVariant = TravlyticOnSurface2,
    error = TravlyticRed,
    outline = Color(0xFF3A4F63)
)

@Composable
fun TravlyticTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = DarkColorScheme,
        typography = Typography(),
        content = content
    )
}
