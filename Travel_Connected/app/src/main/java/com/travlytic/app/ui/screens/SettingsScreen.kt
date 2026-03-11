package com.travlytic.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.text.style.TextOverflow
import androidx.hilt.navigation.compose.hiltViewModel
import com.travlytic.app.ui.theme.*
import com.travlytic.app.ui.viewmodel.MainViewModel
import android.app.Activity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.ui.platform.LocalContext
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.ui.draw.clip

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    viewModel: MainViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit,
    onNavigateToTraining: () -> Unit,
    onNavigateToProfile: () -> Unit,
    onNavigateToKnowledge: () -> Unit,
    onNavigateToChannels: () -> Unit
) {
    val geminiKey by viewModel.geminiApiKey.collectAsState()
    val systemPrompt by viewModel.systemPrompt.collectAsState()
    val welcomeMessage by viewModel.welcomeMessage.collectAsState()
    val escalationMessage by viewModel.escalationMessage.collectAsState()
    val autoReminderEnabled by viewModel.autoReminderEnabled.collectAsState()
    val autoReminderMessage by viewModel.autoReminderMessage.collectAsState()
    val internetSearchEnabled by viewModel.internetSearchEnabled.collectAsState()
    val uiState by viewModel.uiState.collectAsState()
    
    var apiKeyInput by remember(geminiKey) { mutableStateOf(geminiKey) }
    var promptInput by remember(systemPrompt) { mutableStateOf(systemPrompt) }
    var showApiKey by remember { mutableStateOf(false) }
    var welcomeInput by remember(welcomeMessage) { mutableStateOf(welcomeMessage) }
    var escalationInput by remember(escalationMessage) { mutableStateOf(escalationMessage) }    
    var autoReminderInput by remember(autoReminderMessage) { mutableStateOf(autoReminderMessage) }    
    
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(uiState.snackbarMessage) {
        uiState.snackbarMessage?.let {
            snackbarHostState.showSnackbar(it)
            viewModel.clearSnackbar()
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = MinItoSurface,
        topBar = {
            TopAppBar(
                title = { Text("Configuración", color = MinItoOnSurface, fontWeight = FontWeight.SemiBold) },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Filled.ArrowBack, "Volver", tint = MinItoOnSurface)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = MinItoSurface)
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // ─── Base de Conocimiento ─────────────────────────────
            SettingsSection(title = "📚 Fuente de Conocimiento") {
                Text(
                    "Agrega archivos Excel locales de donde Gemini tomará las respuestas.",
                    color = MinItoOnSurface2, fontSize = 12.sp
                )
                Spacer(Modifier.height(12.dp))
                Button(
                    onClick = onNavigateToKnowledge,
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(containerColor = MinItoBlue)
                ) {
                    Icon(Icons.Filled.TableChart, null, modifier = Modifier.size(16.dp))
                    Spacer(Modifier.width(8.dp))
                    Text("Gestionar Documentos")
                }
            }

            // ─── Perfil ────────────────────────────────────────────────────
            SettingsSection(title = "👤 Perfil y Personalización") {
                Text(
                    "Agrega el nombre de tu empresa y el tono de respuesta.",
                    color = MinItoOnSurface2, fontSize = 12.sp
                )
                Spacer(Modifier.height(12.dp))
                Button(
                    onClick = onNavigateToProfile,
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(containerColor = MinItoSurface3)
                ) {
                    Icon(Icons.Filled.Person, null, modifier = Modifier.size(16.dp), tint = MinItoBlue)
                    Spacer(Modifier.width(8.dp))
                    Text("Editar Perfil", color = MinItoBlue)
                }
            }

            // ─── Mensajes Automáticos ──────────────────────────────────────────
            SettingsSection(title = "💬 Mensajes Automáticos") {
                Text(
                    "Mensaje de Bienvenida (Primer contacto)",
                    color = MinItoOnSurface2, fontSize = 12.sp
                )
                OutlinedTextField(
                    value = welcomeInput,
                    onValueChange = { welcomeInput = it },
                    placeholder = { Text("Ej. ¡Hola! Bienvenido a Travelers.") },
                    modifier = Modifier.fillMaxWidth().padding(top = 4.dp, bottom = 8.dp),
                    colors = settingsTextFieldColors(),
                    singleLine = false,
                    maxLines = 3
                )
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.End
                ) {
                    Button(
                        onClick = { viewModel.saveWelcomeMessage(welcomeInput) },
                        enabled = welcomeInput != welcomeMessage,
                        colors = ButtonDefaults.buttonColors(containerColor = MinItoBlue)
                    ) {
                        Text("Guardar Bienvenida")
                    }
                }

                Spacer(Modifier.height(16.dp))

                Text(
                    "Mensaje de Escalado (Cuando el AI no sabe qué responder)",
                    color = MinItoOnSurface2, fontSize = 12.sp
                )
                OutlinedTextField(
                    value = escalationInput,
                    onValueChange = { escalationInput = it },
                    placeholder = { Text("Ej. Un agente te atenderá en breve.") },
                    modifier = Modifier.fillMaxWidth().padding(top = 4.dp, bottom = 8.dp),
                    colors = settingsTextFieldColors(),
                    singleLine = false,
                    maxLines = 3
                )
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.End
                ) {
                    Button(
                        onClick = { viewModel.saveEscalationMessage(escalationInput) },
                        enabled = escalationInput != escalationMessage,
                        colors = ButtonDefaults.buttonColors(containerColor = MinItoBlue)
                    ) {
                        Text("Guardar Escalado")
                    }
                }

                Spacer(Modifier.height(16.dp))

                Row(
                    modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            "Recordatorio de Inactividad (5 min)",
                            color = MinItoOnSurface, fontSize = 14.sp, fontWeight = FontWeight.Medium
                        )
                        Text(
                            "Enviar si el usuario no responde después de 5 min.",
                            color = MinItoOnSurface2, fontSize = 12.sp
                        )
                    }
                    Switch(
                        checked = autoReminderEnabled,
                        onCheckedChange = { viewModel.saveAutoReminderEnabled(it) },
                        colors = SwitchDefaults.colors(checkedThumbColor = MinItoBlue, checkedTrackColor = MinItoBlue.copy(alpha = 0.5f))
                    )
                }

                if (autoReminderEnabled) {
                    OutlinedTextField(
                        value = autoReminderInput,
                        onValueChange = { autoReminderInput = it },
                        placeholder = { Text("Ej. ¿Puedo ayudarte en algo más?") },
                        modifier = Modifier.fillMaxWidth().padding(top = 4.dp, bottom = 8.dp),
                        colors = settingsTextFieldColors(),
                        singleLine = false,
                        maxLines = 2
                    )
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.End
                    ) {
                        Button(
                            onClick = { viewModel.saveAutoReminderMessage(autoReminderInput) },
                            enabled = autoReminderInput != autoReminderMessage,
                            colors = ButtonDefaults.buttonColors(containerColor = MinItoBlue)
                        ) {
                            Text("Guardar Recordatorio")
                        }
                    }
                }
            }

            // ─── Gemini API Key ────────────────────────────────────────
            SettingsSection(title = "🤖 Gemini AI") {
                Text(
                    "Obtén tu API Key gratis en aistudio.google.com",
                    color = MinItoBlueLight, fontSize = 12.sp
                )
                Spacer(Modifier.height(8.dp))
                OutlinedTextField(
                    value = apiKeyInput,
                    onValueChange = { apiKeyInput = it },
                    label = { Text("Gemini API Key") },
                    placeholder = { Text("AIza...") },
                    trailingIcon = {
                        IconButton(onClick = { showApiKey = !showApiKey }) {
                            Icon(
                                if (showApiKey) Icons.Filled.VisibilityOff else Icons.Filled.Visibility,
                                null, tint = MinItoOnSurface2
                            )
                        }
                    },
                    visualTransformation = if (showApiKey) VisualTransformation.None
                    else PasswordVisualTransformation(),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                    modifier = Modifier.fillMaxWidth(),
                    colors = settingsTextFieldColors(),
                    singleLine = true
                )
                Spacer(Modifier.height(16.dp))
                
                // Toggle para búsqueda en internet
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            "Búsqueda de IA (Internet)",
                            color = MinItoOnSurface, fontSize = 14.sp, fontWeight = FontWeight.Medium
                        )
                        Text(
                            "Permite que el bot use conocimiento general si lo autorizas en tus reglas.",
                            color = MinItoOnSurface2, fontSize = 12.sp
                        )
                    }
                    Switch(
                        checked = internetSearchEnabled,
                        onCheckedChange = { viewModel.saveInternetSearchEnabled(it) },
                        colors = SwitchDefaults.colors(checkedThumbColor = MinItoBlue, checkedTrackColor = MinItoBlue.copy(alpha = 0.5f))
                    )
                }
                Spacer(Modifier.height(8.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.End
                ) {
                    Button(
                        onClick = { viewModel.saveGeminiApiKey(apiKeyInput) },
                        enabled = apiKeyInput.isNotBlank() && apiKeyInput != geminiKey,
                        colors = ButtonDefaults.buttonColors(containerColor = MinItoBlue)
                    ) {
                        Icon(Icons.Filled.Save, null, modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(4.dp))
                        Text("Guardar Key")
                    }
                }

                // Status de la key
                if (geminiKey.isNotBlank()) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Filled.CheckCircle, null,
                            tint = MinItoGreen, modifier = Modifier.size(14.dp))
                        Spacer(Modifier.width(4.dp))
                        Text("API Key configurada", color = MinItoGreen, fontSize = 12.sp)
                    }
                } else {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Filled.Warning, null,
                            tint = MinItoOrange, modifier = Modifier.size(14.dp))
                        Spacer(Modifier.width(4.dp))
                        Text("API Key no configurada", color = MinItoOrange, fontSize = 12.sp)
                    }
                }
            }

            // ─── System Prompt ─────────────────────────────────────────
            SettingsSection(title = "📝 Prompt del Sistema") {
                Text(
                    "Define cómo Gemini responde los mensajes.",
                    color = MinItoOnSurface2, fontSize = 12.sp
                )
                Spacer(Modifier.height(8.dp))
                OutlinedTextField(
                    value = promptInput,
                    onValueChange = { promptInput = it },
                    label = { Text("Instrucciones del agente") },
                    modifier = Modifier.fillMaxWidth(),
                    colors = settingsTextFieldColors(),
                    minLines = 6,
                    maxLines = 12
                )
                Spacer(Modifier.height(8.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp, Alignment.End)
                ) {
                    OutlinedButton(
                        onClick = {
                            viewModel.resetSystemPrompt()
                            promptInput = com.travlytic.app.data.prefs.AppPreferences.DEFAULT_SYSTEM_PROMPT
                        },
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = MinItoOnSurface2),
                        border = ButtonDefaults.outlinedButtonBorder.copy()
                    ) {
                        Icon(Icons.Filled.Restore, null, modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(4.dp))
                        Text("Reset")
                    }
                    Button(
                        onClick = { viewModel.saveSystemPrompt(promptInput) },
                        enabled = promptInput != systemPrompt && promptInput.isNotBlank(),
                        colors = ButtonDefaults.buttonColors(containerColor = MinItoBlue)
                    ) {
                        Icon(Icons.Filled.Save, null, modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(4.dp))
                        Text("Guardar")
                    }
                }
            }

            // ─── Canales ───────────────────────────────────────────────────
            SettingsSection(title = "📲 Canales") {
                Text(
                    "Elige en qué apps el bot contestará mensajes.",
                    color = MinItoOnSurface2, fontSize = 12.sp
                )
                Spacer(Modifier.height(12.dp))
                Button(
                    onClick = onNavigateToChannels,
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(containerColor = MinItoSurface3)
                ) {
                    Icon(Icons.Filled.Forum, null, modifier = Modifier.size(16.dp))
                    Spacer(Modifier.width(8.dp))
                    Text("Gestionar Canales Activos")
                }
            }

            // ─── Entrenamiento IA ──────────────────────────────────────────
            SettingsSection(title = "🧠 Entrenamiento IA") {
                Text(
                    "Agrega reglas estrictas o enseña a Gemini cómo responder usando ejemplos (Few-Shot).",
                    color = MinItoOnSurface2, fontSize = 12.sp
                )
                Spacer(Modifier.height(12.dp))
                Button(
                    onClick = onNavigateToTraining,
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(containerColor = MinItoBlue)
                ) {
                    Icon(Icons.Filled.School, null, modifier = Modifier.size(16.dp))
                    Spacer(Modifier.width(8.dp))
                    Text("Abrir Panel de Entrenamiento")
                }
            }

            // ─── Sistema ───────────────────────────────────────────────
            SettingsSection(title = "⚙️ Sistema") {
                Text(
                    "Restaura todas las configuraciones globales, reglas y mensajes a sus valores de fábrica originales.",
                    color = MinItoOnSurface2, fontSize = 12.sp
                )
                Spacer(Modifier.height(12.dp))
                Button(
                    onClick = { viewModel.resetToDefaultSettings() },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error)
                ) {
                    Icon(Icons.Filled.Warning, null, modifier = Modifier.size(16.dp))
                    Spacer(Modifier.width(8.dp))
                    Text("Restablecer a Valores Originales")
                }
            }

            // ─── Info Section ──────────────────────────────────────────
            SettingsSection(title = "ℹ️ Información") {
                InfoRow("Versión", "1.0.0")
                InfoRow("Motor IA", "Gemini 2.5 Flash")
                InfoRow("Base de datos", "Room (SQLite local)")
                Spacer(Modifier.height(4.dp))
                Text(
                    "Travlytic responde automáticamente mensajes de WhatsApp usando tu contenido local de Excel como fuente de conocimiento.",
                    color = TravlyticOnSurface2, fontSize = 12.sp, lineHeight = 18.sp
                )
            }

            Spacer(Modifier.height(24.dp))
        }
    }
}

@Composable
fun SettingsSection(title: String, content: @Composable ColumnScope.() -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = TravlyticSurface2),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(Modifier.padding(16.dp)) {
            Text(title, color = TravlyticOnSurface, fontWeight = FontWeight.SemiBold, fontSize = 15.sp)
            Spacer(Modifier.height(12.dp))
            content()
        }
    }
}

@Composable
fun InfoRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 3.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(label, color = MinItoOnSurface2, fontSize = 13.sp)
        Text(value, color = MinItoOnSurface, fontSize = 13.sp, fontWeight = FontWeight.Medium)
    }
}

@Composable
fun settingsTextFieldColors() = OutlinedTextFieldDefaults.colors(
    focusedBorderColor = MinItoBlue,
    unfocusedBorderColor = MinItoSurface3,
    focusedTextColor = MinItoOnSurface,
    unfocusedTextColor = MinItoOnSurface,
    cursorColor = MinItoBlue,
    focusedLabelColor = MinItoBlue,
    unfocusedLabelColor = MinItoOnSurface2
)

@Composable
fun GoogleAccountCard(
    email: String,
    onSignIn: () -> Unit,
    onSignOut: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MinItoSurface3),
        shape = RoundedCornerShape(12.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp).fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier.size(40.dp).clip(CircleShape)
                        .background(if (email.isNotBlank()) MinItoBlue else MinItoSurface2),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        if (email.isNotBlank()) Icons.Filled.Person else Icons.Outlined.Person,
                        null, tint = Color.White
                    )
                }
                Spacer(Modifier.width(12.dp))
                Column {
                    Text("Google Account", color = MinItoOnSurface2, fontSize = 11.sp)
                    Text(
                        if (email.isNotBlank()) email else "Sin conectar",
                        color = MinItoOnSurface,
                        fontWeight = FontWeight.Medium,
                        fontSize = 13.sp,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                        modifier = Modifier.widthIn(max = 160.dp)
                    )
                }
            }
            if (email.isNotBlank()) {
                IconButton(onClick = onSignOut) {
                    Icon(Icons.Filled.Logout, "Cerrar sesión",
                        tint = MinItoOnSurface2, modifier = Modifier.size(20.dp))
                }
            } else {
                FilledTonalButton(
                    onClick = onSignIn,
                    colors = ButtonDefaults.filledTonalButtonColors(
                        containerColor = MinItoBlue.copy(alpha = 0.2f)
                    )
                ) {
                    Text("Conectar", color = MinItoBlue, fontSize = 13.sp)
                }
            }
        }
    }
}
