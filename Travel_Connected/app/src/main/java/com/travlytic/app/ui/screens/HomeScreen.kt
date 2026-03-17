package com.travlytic.app.ui.screens

import android.app.Activity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.expandVertically
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.travlytic.app.R
import com.travlytic.app.data.db.entities.EscalationLog
import com.travlytic.app.data.db.entities.ResponseLog
import com.travlytic.app.ui.theme.*
import com.travlytic.app.ui.viewmodel.DashboardState
import com.travlytic.app.ui.viewmodel.MainViewModel
import com.travlytic.app.ui.viewmodel.TestMessageState
import java.text.SimpleDateFormat
import java.util.*


@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    viewModel: MainViewModel = hiltViewModel(),
    onNavigateToSettings: () -> Unit,
    onNavigateToSchedule: () -> Unit,
    onNavigateToSummary: () -> Unit
) {
    val context = LocalContext.current
    val uiState by viewModel.uiState.collectAsState()
    val dashboardState by viewModel.dashboardState.collectAsState()
    val testMsgState by viewModel.testMsgState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }
    var showTestMessage by remember { mutableStateOf(false) }
    val isListenerEnabled = remember { viewModel.isNotificationListenerEnabled() }

    // Snackbar
    LaunchedEffect(uiState.snackbarMessage) {
        uiState.snackbarMessage?.let {
            snackbarHostState.showSnackbar(it)
            viewModel.clearSnackbar()
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = MinItoSurface,
        floatingActionButton = {
            // ─── FAB Activación Rápida ───────────────────────────────────────────
            ExtendedFloatingActionButton(
                onClick = { viewModel.toggleBot(!uiState.isServiceEnabled) },
                icon = {
                    Icon(
                        if (uiState.isServiceEnabled) Icons.Filled.Stop else Icons.Filled.PlayArrow,
                        contentDescription = null
                    )
                },
                text = {
                    Text(
                        if (uiState.isServiceEnabled) "Desactivar Bot" else "Activar Bot",
                        fontWeight = FontWeight.Bold
                    )
                },
                containerColor = if (uiState.isServiceEnabled) MinItoRed else MinItoGreen,
                contentColor = Color.White
            )
        },
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Image(
                            painter = painterResource(id = R.drawable.minito_logo),
                            contentDescription = "MINI-TO Logo",
                            modifier = Modifier
                                .size(36.dp)
                        )
                        Spacer(Modifier.width(10.dp))
                    Text(
                            "MINI-TO",
                            fontWeight = FontWeight.Bold,
                            color = MinItoOnSurface
                        )
                    }
                },
                actions = {
                    IconButton(onClick = { viewModel.forceSync() }) {
                        Icon(Icons.Filled.Sync, contentDescription = "Sincronizar",
                            tint = MinItoBlue)
                    }
                    IconButton(onClick = onNavigateToSummary) {
                        Icon(Icons.Filled.AutoAwesome, contentDescription = "Resumen",
                            tint = MinItoBlue)
                    }
                    IconButton(onClick = onNavigateToSchedule) {
                        Icon(Icons.Filled.Schedule, contentDescription = "Horarios",
                            tint = if (uiState.isServiceEnabled) MinItoGreen else MinItoOnSurface2)
                    }
                    IconButton(onClick = onNavigateToSettings) {
                        Icon(Icons.Filled.Settings, contentDescription = "Configuración",
                            tint = MinItoOnSurface2)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = MinItoSurface)
            )
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // ─── Bot Status Card ───────────────────────────────────────
            item {
                Spacer(Modifier.height(4.dp))
                BotStatusCard(
                    isServiceEnabled = uiState.isServiceEnabled,
                    isEffectivelyEnabled = uiState.isEffectivelyEnabled,
                    activationReason = uiState.activationReason,
                    isListenerEnabled = isListenerEnabled,
                    onToggle = { viewModel.toggleBot(it) },
                    onOpenSettings = { viewModel.openNotificationSettings(context) }
                )
            }

            // ─── Dashboard Card ────────────────────────────────────────────
            item {
                DashboardCard(dashboardState)
            }

            // ─── Alertas de Escalado ───────────────────────────────────────────────
            item {
                Spacer(Modifier.height(4.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        "🚨 Alertas de Escalado",
                        color = MinItoOrange,
                        fontWeight = FontWeight.SemiBold,
                        fontSize = 16.sp
                    )
                    if (uiState.recentEscalations.isNotEmpty()) {
                        Text(
                            "${uiState.recentEscalations.size} pendiente${if (uiState.recentEscalations.size > 1) "s" else ""}",
                            color = MinItoRed,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }

            if (uiState.recentEscalations.isEmpty()) {
                item {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = MinItoSurface2),
                        shape = RoundedCornerShape(10.dp)
                    ) {
                        Row(
                            modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text("✅ ", fontSize = 16.sp)
                            Text(
                                "Sin escalados pendientes",
                                color = MinItoOnSurface2,
                                fontSize = 13.sp
                            )
                        }
                    }
                }
            } else {
                items(uiState.recentEscalations, key = { "esc_${it.id}" }) { log ->
                    EscalationCard(log, onResolve = { viewModel.resolveEscalation(it) })
                }
            }

            // ─── Test Message Section ─────────────────────────────────────
            item {
                Spacer(Modifier.height(4.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        "🧪 Probar Bot",
                        color = MinItoOnSurface,
                        fontWeight = FontWeight.SemiBold,
                        fontSize = 16.sp
                    )
                    TextButton(onClick = { showTestMessage = !showTestMessage }) {
                        Text(
                            if (showTestMessage) "Ocultar" else "Abrir",
                            color = MinItoBlue, fontSize = 12.sp
                        )
                    }
                }
                AnimatedVisibility(
                    visible = showTestMessage,
                    enter = fadeIn() + expandVertically(),
                    exit = fadeOut() + shrinkVertically()
                ) {
                    TestMessageCard(
                        state = testMsgState,
                        onSend = { viewModel.testMessage(it) },
                        onClear = { viewModel.clearTestMessage() }
                    )
                }
            }

            // ─── Response Log ───────────────────────────────────────────────
            item {
                Spacer(Modifier.height(4.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        "💬 Respuestas recientes",
                        color = MinItoOnSurface,
                        fontWeight = FontWeight.SemiBold,
                        fontSize = 16.sp
                    )
                    if (uiState.recentLogs.isNotEmpty()) {
                        TextButton(onClick = { viewModel.clearLogs() }) {
                            Text("Borrar", color = MinItoRed, fontSize = 12.sp)
                        }
                    }
                }
            }

            if (uiState.recentLogs.isEmpty()) {
                item {
                    Box(
                        Modifier.fillMaxWidth().padding(24.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("Sin respuestas enviadas aún",
                            color = MinItoOnSurface2, fontSize = 13.sp)
                    }
                }
            } else {
                items(uiState.recentLogs.take(20), key = { it.id }) { log ->
                    ResponseLogCard(log)
                }
            }

            item { Spacer(Modifier.height(24.dp)) }
        }
    }
}

// ─── Composables ─────────────────────────────────────────────────────────────

@Composable
fun BotStatusCard(
    isServiceEnabled: Boolean,
    isEffectivelyEnabled: Boolean,
    activationReason: String,
    isListenerEnabled: Boolean,
    onToggle: (Boolean) -> Unit,
    onOpenSettings: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MinItoSurface2),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text("Estado del Bot", color = MinItoOnSurface2, fontSize = 12.sp)
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            if (isEffectivelyEnabled) "🟢 Activo" else "🔴 Inactivo",
                            color = if (isEffectivelyEnabled) MinItoGreen else MinItoRed,
                            fontWeight = FontWeight.Bold,
                            fontSize = 18.sp
                        )
                        if (isEffectivelyEnabled && activationReason == "horario" && !isServiceEnabled) {
                            Spacer(Modifier.width(8.dp))
                            Surface(
                                color = MinItoBlue.copy(alpha = 0.15f),
                                shape = RoundedCornerShape(4.dp)
                            ) {
                                Text(
                                    "AUTO",
                                    color = MinItoBlue,
                                    fontSize = 10.sp,
                                    fontWeight = FontWeight.Bold,
                                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                )
                            }
                        }
                    }
                    if (isEffectivelyEnabled) {
                        val text = when (activationReason) {
                            "manual" -> "Activado manualmente"
                            "horario" -> "Activado por horario"
                            else -> ""
                        }
                        Text(text, color = MinItoOnSurface2, fontSize = 11.sp)
                    }
                }
                Switch(
                    checked = isServiceEnabled,
                    onCheckedChange = onToggle,
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = Color.White,
                        checkedTrackColor = MinItoGreen,
                        uncheckedThumbColor = MinItoOnSurface2,
                        uncheckedTrackColor = MinItoSurface3
                    )
                )
            }

            if (!isListenerEnabled) {
                Spacer(Modifier.height(12.dp))
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(8.dp))
                        .background(Color(0x33FF6D00))
                        .clickable { onOpenSettings() }
                        .padding(10.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Outlined.Warning, null,
                        tint = MinItoOrange, modifier = Modifier.size(16.dp))
                    Spacer(Modifier.width(8.dp))
                    Text(
                        "⚠️ Activa el permiso de Notificaciones → Toca aquí",
                        color = MinItoOrange, fontSize = 12.sp
                    )
                }
            }
        }
    }
}



@Composable
fun ResponseLogCard(log: ResponseLog) {
    val dateFormat = remember { SimpleDateFormat("dd/MM HH:mm", Locale.getDefault()) }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MinItoSurface3),
        shape = RoundedCornerShape(10.dp)
    ) {
        Column(Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("👤 ${log.contact}", color = MinItoBlueLight,
                    fontWeight = FontWeight.SemiBold, fontSize = 13.sp)
                Text(dateFormat.format(Date(log.timestamp)),
                    color = MinItoOnSurface2, fontSize = 11.sp)
            }
            Spacer(Modifier.height(4.dp))
            Text("📩 ${log.incomingMessage}", color = MinItoOnSurface2,
                fontSize = 12.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
            Spacer(Modifier.height(2.dp))
            Text("🤖 ${log.sentResponse}", color = MinItoOnSurface,
                fontSize = 12.sp, maxLines = 2, overflow = TextOverflow.Ellipsis)
        }
    }
}

// ─── Dashboard Card ───────────────────────────────────────────────────────────

@Composable
fun DashboardCard(state: DashboardState) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFF0D2137) // azul muy oscuro
        ),
        shape = RoundedCornerShape(16.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            DashboardStat(
                icon = "💬",
                value = "${state.repliesToday}",
                label = "Hoy"
            )
            DashboardDivider()
            DashboardStat(
                icon = "📅",
                value = "${state.repliesThisWeek}",
                label = "Esta semana"
            )
            DashboardDivider()
            DashboardStat(
                icon = "📚",
                value = "${state.totalKnowledgeRows}",
                label = "Filas KB"
            )
            DashboardDivider()
            DashboardStat(
                icon = "📊",
                value = "${state.activeSheetsCount}",
                label = "Sheets"
            )
        }
    }
}

@Composable
private fun DashboardStat(icon: String, value: String, label: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(icon, fontSize = 18.sp)
        Spacer(Modifier.height(2.dp))
        Text(
            value,
            color = MinItoOnSurface,
            fontWeight = FontWeight.Bold,
            fontSize = 20.sp
        )
        Text(label, color = MinItoOnSurface2, fontSize = 10.sp)
    }
}

@Composable
private fun DashboardDivider() {
    Divider(
        modifier = Modifier
            .height(40.dp)
            .width(1.dp),
        color = MinItoSurface3
    )
}

// ─── Test Message Card ────────────────────────────────────────────────────────

@Composable
fun TestMessageCard(
    state: TestMessageState,
    onSend: (String) -> Unit,
    onClear: () -> Unit
) {
    var inputText by remember { mutableStateOf("") }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MinItoSurface2),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(Modifier.padding(14.dp)) {
            Text(
                "Escribe un mensaje para ver cómo respondería el bot:",
                color = MinItoOnSurface2, fontSize = 12.sp
            )
            Spacer(Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                OutlinedTextField(
                    value = inputText,
                    onValueChange = { inputText = it },
                    modifier = Modifier.weight(1f),
                    placeholder = { Text("¿Cuál es el horario?", fontSize = 12.sp) },
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = MinItoBlue,
                        unfocusedBorderColor = MinItoSurface3,
                        focusedTextColor = MinItoOnSurface,
                        unfocusedTextColor = MinItoOnSurface
                    )
                )
                Spacer(Modifier.width(8.dp))
                IconButton(
                    onClick = { onSend(inputText) },
                    enabled = inputText.isNotBlank() && !state.isLoading,
                    modifier = Modifier
                        .clip(CircleShape)
                        .background(
                            if (inputText.isNotBlank() && !state.isLoading)
                                MinItoBlue else MinItoSurface3
                        )
                        .size(44.dp)
                ) {
                    if (state.isLoading) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(20.dp),
                            color = Color.White,
                            strokeWidth = 2.dp
                        )
                    } else {
                        Icon(Icons.Filled.Send, "Enviar",
                            tint = Color.White, modifier = Modifier.size(20.dp))
                    }
                }
            }

            // Respuesta de Gemini
            if (state.response.isNotBlank()) {
                Spacer(Modifier.height(10.dp))
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(8.dp))
                        .background(Color(0x1500C853))
                        .padding(10.dp)
                ) {
                    Text("🤖 ", fontSize = 14.sp)
                    Text(
                        state.response,
                        color = MinItoOnSurface,
                        fontSize = 13.sp,
                        lineHeight = 18.sp,
                        modifier = Modifier.weight(1f)
                    )
                }
                Spacer(Modifier.height(6.dp))
                TextButton(
                    onClick = { onClear(); inputText = "" },
                    modifier = Modifier.align(Alignment.End)
                ) {
                    Text("Limpiar", color = MinItoOnSurface2, fontSize = 11.sp)
                }
            }

            if (state.error.isNotBlank()) {
                Spacer(Modifier.height(8.dp))
                Text(state.error, color = MinItoRed, fontSize = 12.sp)
            }
        }
    }
}

@Composable
fun EscalationCard(log: EscalationLog, onResolve: (EscalationLog) -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MinItoSurface3),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(log.contact, color = MinItoOnSurface, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                Text(
                    SimpleDateFormat("HH:mm", Locale.getDefault()).format(Date(log.timestamp)),
                    color = MinItoOnSurface2, fontSize = 12.sp
                )
            }
            Spacer(Modifier.height(8.dp))
            Text(
                "Pregunta: \"${log.originalMessage}\"",
                color = MinItoOnSurface2, fontSize = 13.sp,
                maxLines = 3, overflow = TextOverflow.Ellipsis
            )
            Spacer(Modifier.height(12.dp))
            Button(
                onClick = { onResolve(log) },
                colors = ButtonDefaults.buttonColors(containerColor = MinItoOrange),
                modifier = Modifier.align(Alignment.End),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text("Marcar Atendido")
            }
        }
    }
}
