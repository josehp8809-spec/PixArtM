package com.travlytic.app.ui.theme

import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// ─── Paleta de colores MINI-TO (Blue-Cyan Gradient Brand) ────────────────────
// Basada en el logo oficial: azul eléctrico → cian
val MinItoBlue      = Color(0xFF1A52F0)   // Azul eléctrico (nodo izquierdo del logo)
val MinItoBlueDark  = Color(0xFF0B32B8)   // Azul marino profundo
val MinItoBlueLight = Color(0xFF5C8FFF)   // Azul soft / highlight
val MinItoCyan         = Color(0xFF00D4FF)   // Cian brillante (nodo derecho del logo)
val MinItoCyanDark     = Color(0xFF0097C7)   // Cian oscuro / hover
val MinItoGreen     = Color(0xFF00C853)   // Verde éxito
val MinItoGreenLight= Color(0xFF69F0AE)
val MinItoRed       = Color(0xFFE53935)   // Rojo error
val MinItoOrange    = Color(0xFFFF6D00)   // Naranja advertencia

// Superficies – Navy profundo para que el azul/cyan resalte
val MinItoSurface   = Color(0xFF060D1F)   // Navy casi negro
val MinItoSurface2  = Color(0xFF0D1932)   // Navy oscuro
val MinItoSurface3  = Color(0xFF152240)   // Navy medio
val MinItoOnSurface = Color(0xFFE6EEFF)   // Blanco con tono azulado
val MinItoOnSurface2= Color(0xFF8BA3CC)   // Gris-azul suave

// ─── Color Scheme (Dark) ─────────────────────────────────────────────────────
private val DarkColorScheme = darkColorScheme(
    primary = MinItoBlue,
    onPrimary = Color.White,
    primaryContainer = MinItoBlueDark,
    onPrimaryContainer = MinItoBlueLight,
    secondary = MinItoCyan,
    onSecondary = Color(0xFF003040),
    secondaryContainer = Color(0xFF003D54),
    onSecondaryContainer = MinItoCyan,
    background = MinItoSurface,
    onBackground = MinItoOnSurface,
    surface = MinItoSurface2,
    onSurface = MinItoOnSurface,
    surfaceVariant = MinItoSurface3,
    onSurfaceVariant = MinItoOnSurface2,
    error = MinItoRed,
    outline = Color(0xFF1E3560)
)

@Composable
fun MinItoTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = DarkColorScheme,
        typography = Typography(),
        content = content
    )
}

