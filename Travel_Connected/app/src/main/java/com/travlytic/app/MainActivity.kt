package com.travlytic.app

import android.content.ComponentName
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.*
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.travlytic.app.service.UniversalListenerService
import com.travlytic.app.ui.screens.HomeScreen
import com.travlytic.app.ui.screens.ScheduleScreen
import com.travlytic.app.ui.screens.SettingsScreen
import com.travlytic.app.ui.screens.SummaryScreen
import com.travlytic.app.ui.screens.TrainingScreen
import com.travlytic.app.ui.screens.ProfileScreen
import com.travlytic.app.ui.screens.KnowledgeBaseScreen
import com.travlytic.app.ui.screens.ChannelsScreen
import com.travlytic.app.ui.theme.MinItoTheme
import com.travlytic.app.ui.theme.MinItoSurface
import dagger.hilt.android.AndroidEntryPoint

private const val TAG = "MainActivity"

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ── Forzar re-vinculación del NotificationListenerService ──────────────
        // Cuando se reinstala un APK, Android puede dejar el servicio en estado
        // desconectado aunque los permisos estén activos. Este truco lo fuerza
        // a reconectarse sin que el usuario tenga que ir a Ajustes.
        forceRebindNotificationListener()

        // ── Solicitar permisos de notificación (Android 13+) ───────────────────
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            if (checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                requestPermissions(arrayOf(android.Manifest.permission.POST_NOTIFICATIONS), 101)
            }
        }

        setContent {
            MinItoTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MinItoSurface
                ) {
                    MinItoNavHost()
                }
            }
        }
    }

    /**
     * Fuerza a Android a restablecer la conexión con el NotificationListenerService.
     * Técnica: deshabilitar y re-habilitar el componente brevemente.
     * Esto hace que Android rebindee el servicio sin perder los permisos del usuario.
     */
    private fun forceRebindNotificationListener() {
        try {
            val componentName = ComponentName(this, UniversalListenerService::class.java)
            val pm = packageManager

            pm.setComponentEnabledSetting(
                componentName,
                PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
                PackageManager.DONT_KILL_APP
            )
            pm.setComponentEnabledSetting(
                componentName,
                PackageManager.COMPONENT_ENABLED_STATE_ENABLED,
                PackageManager.DONT_KILL_APP
            )
            Log.d(TAG, "✅ NotificationListenerService rebindeado exitosamente.")
        } catch (e: Exception) {
            Log.e(TAG, "⚠️ Error al hacer rebind del servicio: ${e.message}")
        }
    }
}

@Composable
fun MinItoNavHost() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = "home",
        enterTransition = { slideInHorizontally(initialOffsetX = { it }) },
        exitTransition = { slideOutHorizontally(targetOffsetX = { -it }) },
        popEnterTransition = { slideInHorizontally(initialOffsetX = { -it }) },
        popExitTransition = { slideOutHorizontally(targetOffsetX = { it }) }
    ) {
        composable("home") {
            HomeScreen(
                onNavigateToSettings = { navController.navigate("settings") },
                onNavigateToSchedule = { navController.navigate("schedule") },
                onNavigateToSummary  = { navController.navigate("summary") }
            )
        }
        composable("settings") {
            SettingsScreen(
                onNavigateBack = { navController.popBackStack() },
                onNavigateToTraining = { navController.navigate("training") },
                onNavigateToProfile = { navController.navigate("profile") },
                onNavigateToKnowledge = { navController.navigate("knowledge") },
                onNavigateToChannels = { navController.navigate("channels") }
            )
        }
        composable("schedule") {
            ScheduleScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }
        composable("summary") {
            SummaryScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }
        composable("training") {
            TrainingScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }
        composable("profile") {
            ProfileScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }
        composable("knowledge") {
            KnowledgeBaseScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }
        composable("channels") {
            ChannelsScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }
    }
}
