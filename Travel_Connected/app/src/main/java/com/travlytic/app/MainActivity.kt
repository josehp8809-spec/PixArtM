package com.travlytic.app

import android.os.Bundle
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
import com.travlytic.app.ui.screens.HomeScreen
import com.travlytic.app.ui.screens.ScheduleScreen
import com.travlytic.app.ui.screens.SettingsScreen
import com.travlytic.app.ui.screens.SummaryScreen
import com.travlytic.app.ui.screens.TrainingScreen
import com.travlytic.app.ui.screens.ProfileScreen
import com.travlytic.app.ui.screens.KnowledgeBaseScreen
import com.travlytic.app.ui.theme.TravlyticTheme
import com.travlytic.app.ui.theme.TravlyticSurface
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            TravlyticTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = TravlyticSurface
                ) {
                    TravlyticNavHost()
                }
            }
        }
    }
}

@Composable
fun TravlyticNavHost() {
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
                onNavigateToKnowledge = { navController.navigate("knowledge") }
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
    }
}
