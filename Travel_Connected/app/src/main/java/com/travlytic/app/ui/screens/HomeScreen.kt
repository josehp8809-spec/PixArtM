package com.travlytic.app.ui.screens

import android.app.Activity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.*
import androidx.compose.foundation.*
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.common.api.ApiException
import com.travlytic.app.data.db.entities.RegisteredSheet
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
    onNavigateToSchedule: () -> Unit
) {
    val context = LocalContext.current
    val uiState by viewModel.uiState.collectAsState()
    val dashboardState by viewModel.dashboardState.collectAsState()
    val testMsgState by viewModel.testMsgState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }
    var showAddSheetDialog by remember { mutableStateOf(false) }
    var showTestMessage by remember { mutableStateOf(false) }
    val isListenerEnabled = remember { viewModel.isNotificationListenerEnabled() }

    // Google Sign-In launcher
    val signInLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            val task = GoogleSignIn.getSignedInAccountFromIntent(result.data)
            try {
                val account = task.getResult(ApiException::class.java)
                viewModel.onGoogleSignInSuccess(account)
            } catch (e: ApiException) {
                // Error manejado en ViewModel
            }
        }
    }

    // Snackbar
    LaunchedEffect(uiState.snackbarMessage) {
        uiState.snackbarMessage?.let {
            snackbarHostState.showSnackbar(it)
            viewModel.clearSnackbar()
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = TravlyticSurface,
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
                containerColor = if (uiState.isServiceEnabled) TravlyticRed else TravlyticGreen,
                contentColor = Color.White
            )
        },
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(32.dp)
                                .clip(CircleShape)
                                .background(
                                    Brush.linearGradient(
                                        listOf(TravlyticBlue, TravlyticGreen)
                                    )
                                ),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                Icons.Filled.Psychology,
                                contentDescription = null,
                                tint = Color.White,
                                modifier = Modifier.size(20.dp)
                            )
                        }
                        Spacer(Modifier.width(10.dp))
                        Text(
                            "Travlytic",
                            fontWeight = FontWeight.Bold,
                            color = TravlyticOnSurface
                        )
                    }
                },
                actions = {
                    IconButton(onClick = onNavigateToSchedule) {
                        Icon(Icons.Filled.Schedule, contentDescription = "Horarios",
                            tint = if (uiState.isServiceEnabled) TravlyticGreen else TravlyticOnSurface2)
                    }
                    IconButton(onClick = onNavigateToSettings) {
                        Icon(Icons.Filled.Settings, contentDescription = "Configuración",
                            tint = TravlyticOnSurface2)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = TravlyticSurface)
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
                    isListenerEnabled = isListenerEnabled,
                    onToggle = { viewModel.toggleBot(it) },
                    onOpenSettings = { viewModel.openNotificationSettings(context) }
                )
            }

            // ─── Dashboard Card ────────────────────────────────────────────
            item {
                DashboardCard(dashboardState)
            }

            // ─── Google Account ────────────────────────────────────────────
            item {
                GoogleAccountCard(
                    email = uiState.googleAccountEmail,
                    onSignIn = {
                        val client = viewModel.getGoogleSignInClient(context)
                        signInLauncher.launch(client.signInIntent)
                    },
                    onSignOut = { viewModel.signOut() }
                )
            }

            // ─── Sheets Section ────────────────────────────────────────
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        "📊 Google Sheets",
                        color = TravlyticOnSurface,
                        fontWeight = FontWeight.SemiBold,
                        fontSize = 16.sp
                    )
                    Row {
                        if (uiState.registeredSheets.isNotEmpty()) {
                            IconButton(
                                onClick = { viewModel.syncAllSheets() },
                                enabled = !uiState.isLoading
                            ) {
                                Icon(Icons.Filled.Sync, "Sincronizar todos",
                                    tint = TravlyticBlue, modifier = Modifier.size(20.dp))
                            }
                        }
                        FilledTonalButton(
                            onClick = { showAddSheetDialog = true },
                            colors = ButtonDefaults.filledTonalButtonColors(
                                containerColor = TravlyticSurface3
                            )
                        ) {
                            Icon(Icons.Filled.Add, null, modifier = Modifier.size(16.dp))
                            Spacer(Modifier.width(4.dp))
                            Text("Agregar", fontSize = 13.sp)
                        }
                    }
                }
            }

            if (uiState.registeredSheets.isEmpty()) {
                item {
                    EmptySheetPlaceholder()
                }
            } else {
                items(uiState.registeredSheets, key = { it.spreadsheetId }) { sheet ->
                    SheetCard(
                        sheet = sheet,
                        isSyncing = uiState.syncingSheetId == sheet.spreadsheetId,
                        onSync = { viewModel.syncSheet(sheet.spreadsheetId) },
                        onRemove = { viewModel.removeSheet(sheet.spreadsheetId) }
                    )
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
                        color = TravlyticOnSurface,
                        fontWeight = FontWeight.SemiBold,
                        fontSize = 16.sp
                    )
                    TextButton(onClick = { showTestMessage = !showTestMessage }) {
                        Text(
                            if (showTestMessage) "Ocultar" else "Abrir",
                            color = TravlyticBlue, fontSize = 12.sp
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
                        color = TravlyticOnSurface,
                        fontWeight = FontWeight.SemiBold,
                        fontSize = 16.sp
                    )
                    if (uiState.recentLogs.isNotEmpty()) {
                        TextButton(onClick = { viewModel.clearLogs() }) {
                            Text("Borrar", color = TravlyticRed, fontSize = 12.sp)
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
                            color = TravlyticOnSurface2, fontSize = 13.sp)
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

    // ─── Add Sheet Dialog ─────────────────────────────────────────────
    if (showAddSheetDialog) {
        AddSheetDialog(
            onDismiss = { showAddSheetDialog = false },
            onAdd = { input ->
                showAddSheetDialog = false
                viewModel.addSheet(input)
            }
        )
    }
}

// ─── Composables ─────────────────────────────────────────────────────────────

@Composable
fun BotStatusCard(
    isServiceEnabled: Boolean,
    isListenerEnabled: Boolean,
    onToggle: (Boolean) -> Unit,
    onOpenSettings: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = TravlyticSurface2),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text("Estado del Bot", color = TravlyticOnSurface2, fontSize = 12.sp)
                    Text(
                        if (isServiceEnabled) "🟢 Activo" else "🔴 Inactivo",
                        color = if (isServiceEnabled) TravlyticGreen else TravlyticRed,
                        fontWeight = FontWeight.Bold,
                        fontSize = 18.sp
                    )
                }
                Switch(
                    checked = isServiceEnabled,
                    onCheckedChange = onToggle,
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = Color.White,
                        checkedTrackColor = TravlyticGreen,
                        uncheckedThumbColor = TravlyticOnSurface2,
                        uncheckedTrackColor = TravlyticSurface3
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
                        tint = TravlyticOrange, modifier = Modifier.size(16.dp))
                    Spacer(Modifier.width(8.dp))
                    Text(
                        "⚠️ Activa el permiso de Notificaciones → Toca aquí",
                        color = TravlyticOrange, fontSize = 12.sp
                    )
                }
            }
        }
    }
}

@Composable
fun GoogleAccountCard(
    email: String,
    onSignIn: () -> Unit,
    onSignOut: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = TravlyticSurface2),
        shape = RoundedCornerShape(16.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp).fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier.size(40.dp).clip(CircleShape)
                        .background(if (email.isNotBlank()) TravlyticBlue else TravlyticSurface3),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        if (email.isNotBlank()) Icons.Filled.Person else Icons.Outlined.Person,
                        null, tint = Color.White
                    )
                }
                Spacer(Modifier.width(12.dp))
                Column {
                    Text("Google Account", color = TravlyticOnSurface2, fontSize = 11.sp)
                    Text(
                        if (email.isNotBlank()) email else "Sin conectar",
                        color = TravlyticOnSurface,
                        fontWeight = FontWeight.Medium,
                        fontSize = 13.sp,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                        modifier = Modifier.widthIn(max = 180.dp)
                    )
                }
            }
            if (email.isNotBlank()) {
                IconButton(onClick = onSignOut) {
                    Icon(Icons.Filled.Logout, "Cerrar sesión",
                        tint = TravlyticOnSurface2, modifier = Modifier.size(20.dp))
                }
            } else {
                FilledTonalButton(
                    onClick = onSignIn,
                    colors = ButtonDefaults.filledTonalButtonColors(
                        containerColor = TravlyticBlue.copy(alpha = 0.2f)
                    )
                ) {
                    Text("Conectar", color = TravlyticBlue, fontSize = 13.sp)
                }
            }
        }
    }
}

@Composable
fun SheetCard(
    sheet: RegisteredSheet,
    isSyncing: Boolean,
    onSync: () -> Unit,
    onRemove: () -> Unit
) {
    val dateFormat = remember { SimpleDateFormat("dd/MM HH:mm", Locale.getDefault()) }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = TravlyticSurface3),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier.padding(12.dp).fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier.size(36.dp).clip(RoundedCornerShape(8.dp))
                    .background(Color(0x2200C853)),
                contentAlignment = Alignment.Center
            ) {
                Icon(Icons.Filled.TableChart, null,
                    tint = TravlyticGreen, modifier = Modifier.size(20.dp))
            }
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Text(sheet.title, color = TravlyticOnSurface,
                    fontWeight = FontWeight.Medium, fontSize = 14.sp,
                    maxLines = 1, overflow = TextOverflow.Ellipsis)
                Text(
                    if (sheet.lastSynced == 0L) "Sin sincronizar"
                    else "${sheet.rowCount} filas · ${dateFormat.format(Date(sheet.lastSynced))}",
                    color = TravlyticOnSurface2, fontSize = 11.sp
                )
            }

            if (isSyncing) {
                CircularProgressIndicator(modifier = Modifier.size(20.dp),
                    color = TravlyticBlue, strokeWidth = 2.dp)
            } else {
                IconButton(onClick = onSync, modifier = Modifier.size(36.dp)) {
                    Icon(Icons.Filled.Refresh, "Sincronizar",
                        tint = TravlyticBlue, modifier = Modifier.size(18.dp))
                }
            }
            IconButton(onClick = onRemove, modifier = Modifier.size(36.dp)) {
                Icon(Icons.Filled.DeleteOutline, "Eliminar",
                    tint = TravlyticRed.copy(alpha = 0.7f), modifier = Modifier.size(18.dp))
            }
        }
    }
}

@Composable
fun EmptySheetPlaceholder() {
    Box(
        modifier = Modifier.fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(TravlyticSurface2)
            .padding(24.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Icon(Icons.Outlined.TableChart, null,
                tint = TravlyticOnSurface2, modifier = Modifier.size(36.dp))
            Spacer(Modifier.height(8.dp))
            Text("Agrega un Google Sheet para comenzar",
                color = TravlyticOnSurface2, fontSize = 13.sp)
        }
    }
}

@Composable
fun ResponseLogCard(log: ResponseLog) {
    val dateFormat = remember { SimpleDateFormat("dd/MM HH:mm", Locale.getDefault()) }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = TravlyticSurface3),
        shape = RoundedCornerShape(10.dp)
    ) {
        Column(Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("👤 ${log.contact}", color = TravlyticBlueLight,
                    fontWeight = FontWeight.SemiBold, fontSize = 13.sp)
                Text(dateFormat.format(Date(log.timestamp)),
                    color = TravlyticOnSurface2, fontSize = 11.sp)
            }
            Spacer(Modifier.height(4.dp))
            Text("📩 ${log.incomingMessage}", color = TravlyticOnSurface2,
                fontSize = 12.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
            Spacer(Modifier.height(2.dp))
            Text("🤖 ${log.sentResponse}", color = TravlyticOnSurface,
                fontSize = 12.sp, maxLines = 2, overflow = TextOverflow.Ellipsis)
        }
    }
}

@Composable
fun AddSheetDialog(onDismiss: () -> Unit, onAdd: (String) -> Unit) {
    var input by remember { mutableStateOf("") }

    AlertDialog(
        onDismissRequest = onDismiss,
        containerColor = TravlyticSurface2,
        title = { Text("Agregar Google Sheet", color = TravlyticOnSurface) },
        text = {
            Column {
                Text("Pega el ID o URL del Google Sheet:",
                    color = TravlyticOnSurface2, fontSize = 13.sp)
                Spacer(Modifier.height(8.dp))
                OutlinedTextField(
                    value = input,
                    onValueChange = { input = it },
                    placeholder = { Text("ID o URL del Sheet...", fontSize = 12.sp) },
                    singleLine = false,
                    minLines = 2,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = TravlyticBlue,
                        unfocusedBorderColor = TravlyticSurface3,
                        focusedTextColor = TravlyticOnSurface,
                        unfocusedTextColor = TravlyticOnSurface
                    )
                )
            }
        },
        confirmButton = {
            Button(
                onClick = { if (input.isNotBlank()) onAdd(input) },
                colors = ButtonDefaults.buttonColors(containerColor = TravlyticBlue)
            ) { Text("Agregar") }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("Cancelar", color = TravlyticOnSurface2) }
        }
    )
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
            color = TravlyticOnSurface,
            fontWeight = FontWeight.Bold,
            fontSize = 20.sp
        )
        Text(label, color = TravlyticOnSurface2, fontSize = 10.sp)
    }
}

@Composable
private fun DashboardDivider() {
    Divider(
        modifier = Modifier
            .height(40.dp)
            .width(1.dp),
        color = TravlyticSurface3
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
        colors = CardDefaults.cardColors(containerColor = TravlyticSurface2),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(Modifier.padding(14.dp)) {
            Text(
                "Escribe un mensaje para ver cómo respondería el bot:",
                color = TravlyticOnSurface2, fontSize = 12.sp
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
                        focusedBorderColor = TravlyticBlue,
                        unfocusedBorderColor = TravlyticSurface3,
                        focusedTextColor = TravlyticOnSurface,
                        unfocusedTextColor = TravlyticOnSurface
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
                                TravlyticBlue else TravlyticSurface3
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
                        color = TravlyticOnSurface,
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
                    Text("Limpiar", color = TravlyticOnSurface2, fontSize = 11.sp)
                }
            }

            // Error
            if (state.error.isNotBlank()) {
                Spacer(Modifier.height(8.dp))
                Text(state.error, color = TravlyticRed, fontSize = 12.sp)
            }
        }
    }
}
