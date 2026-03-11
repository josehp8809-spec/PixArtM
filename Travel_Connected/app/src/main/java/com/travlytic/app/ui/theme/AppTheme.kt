package com.travlytic.app.ui.theme

import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// ─── Paleta de colores MINI-TO (Blue-Cyan Gradient Brand) ────────────────────
// Basada en el logo oficial: azul eléctrico → cian
val TravlyticBlue      = Color(0xFF1A52F0)   // Azul eléctrico (nodo izquierdo del logo)
val TravlyticBlueDark  = Color(0xFF0B32B8)   // Azul marino profundo
val TravlyticBlueLight = Color(0xFF5C8FFF)   // Azul soft / highlight
val MinItoCyan         = Color(0xFF00D4FF)   // Cian brillante (nodo derecho del logo)
val MinItoCyanDark     = Color(0xFF0097C7)   // Cian oscuro / hover
val TravlyticGreen     = Color(0xFF00C853)   // Verde éxito
val TravlyticGreenLight= Color(0xFF69F0AE)
val TravlyticRed       = Color(0xFFE53935)   // Rojo error
val TravlyticOrange    = Color(0xFFFF6D00)   // Naranja advertencia

// Superficies – Navy profundo para que el azul/cyan resalte
val TravlyticSurface   = Color(0xFF060D1F)   // Navy casi negro
val TravlyticSurface2  = Color(0xFF0D1932)   // Navy oscuro
val TravlyticSurface3  = Color(0xFF152240)   // Navy medio
val TravlyticOnSurface = Color(0xFFE6EEFF)   // Blanco con tono azulado
val TravlyticOnSurface2= Color(0xFF8BA3CC)   // Gris-azul suave

// ─── Color Scheme (Dark) ─────────────────────────────────────────────────────
private val DarkColorScheme = darkColorScheme(
    primary = TravlyticBlue,
    onPrimary = Color.White,
    primaryContainer = TravlyticBlueDark,
    onPrimaryContainer = TravlyticBlueLight,
    secondary = MinItoCyan,
    onSecondary = Color(0xFF003040),
    secondaryContainer = Color(0xFF003D54),
    onSecondaryContainer = MinItoCyan,
    background = TravlyticSurface,
    onBackground = TravlyticOnSurface,
    surface = TravlyticSurface2,
    onSurface = TravlyticOnSurface,
    surfaceVariant = TravlyticSurface3,
    onSurfaceVariant = TravlyticOnSurface2,
    error = TravlyticRed,
    outline = Color(0xFF1E3560)
)

@Composable
fun TravlyticTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = DarkColorScheme,
        typography = Typography(),
        content = content
    )
}

