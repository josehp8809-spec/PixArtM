package com.travlytic.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
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
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.common.api.ApiException
import androidx.compose.ui.platform.LocalContext
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.ui.draw.clip

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    viewModel: MainViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit,
    onNavigateToTraining: () -> Unit,
    onNavigateToProfile: () -> Unit
) {
    val geminiKey by viewModel.geminiApiKey.collectAsState()
    val systemPrompt by viewModel.systemPrompt.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }
    val uiState by viewModel.uiState.collectAsState()

    var apiKeyInput by remember(geminiKey) { mutableStateOf(geminiKey) }
    var promptInput by remember(systemPrompt) { mutableStateOf(systemPrompt) }
    var showApiKey by remember { mutableStateOf(false) }
    val context = LocalContext.current

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
                // Error manejado silenciosamente / info via snackbar en viewmodel
            }
        }
    }

    LaunchedEffect(uiState.snackbarMessage) {
        uiState.snackbarMessage?.let {
            snackbarHostState.showSnackbar(it)
            viewModel.clearSnackbar()
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = TravlyticSurface,
        topBar = {
            TopAppBar(
                title = { Text("Configuración", color = TravlyticOnSurface, fontWeight = FontWeight.SemiBold) },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Filled.ArrowBack, "Volver", tint = TravlyticOnSurface)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = TravlyticSurface)
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
            // ─── Perfil ────────────────────────────────────────────────────
            SettingsSection(title = "👤 Perfil y Personalización") {
                Text(
                    "Agrega el nombre de tu empresa y el tono de respuesta.",
                    color = TravlyticOnSurface2, fontSize = 12.sp
                )
                Spacer(Modifier.height(12.dp))
                Button(
                    onClick = onNavigateToProfile,
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(containerColor = TravlyticSurface3)
                ) {
                    Icon(Icons.Filled.Person, null, modifier = Modifier.size(16.dp), tint = TravlyticBlue)
                    Spacer(Modifier.width(8.dp))
                    Text("Editar Perfil", color = TravlyticBlue)
                }
            }

            // ─── Google Account ────────────────────────────────────────────
            SettingsSection(title = "☁️ Sincronización") {
                GoogleAccountCard(
                    email = uiState.googleAccountEmail,
                    onSignIn = {
                        val client = viewModel.getGoogleSignInClient(context)
                        signInLauncher.launch(client.signInIntent)
                    },
                    onSignOut = { viewModel.signOut() }
                )
            }

            // ─── Gemini API Key ────────────────────────────────────────
            SettingsSection(title = "🤖 Gemini AI") {
                Text(
                    "Obtén tu API Key gratis en aistudio.google.com",
                    color = TravlyticBlueLight, fontSize = 12.sp
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
                                null, tint = TravlyticOnSurface2
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
                Spacer(Modifier.height(8.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.End
                ) {
                    Button(
                        onClick = { viewModel.saveGeminiApiKey(apiKeyInput) },
                        enabled = apiKeyInput.isNotBlank() && apiKeyInput != geminiKey,
                        colors = ButtonDefaults.buttonColors(containerColor = TravlyticBlue)
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
                            tint = TravlyticGreen, modifier = Modifier.size(14.dp))
                        Spacer(Modifier.width(4.dp))
                        Text("API Key configurada", color = TravlyticGreen, fontSize = 12.sp)
                    }
                } else {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Filled.Warning, null,
                            tint = TravlyticOrange, modifier = Modifier.size(14.dp))
                        Spacer(Modifier.width(4.dp))
                        Text("API Key no configurada", color = TravlyticOrange, fontSize = 12.sp)
                    }
                }
            }

            // ─── System Prompt ─────────────────────────────────────────
            SettingsSection(title = "📝 Prompt del Sistema") {
                Text(
                    "Define cómo Gemini responde los mensajes.",
                    color = TravlyticOnSurface2, fontSize = 12.sp
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
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = TravlyticOnSurface2),
                        border = ButtonDefaults.outlinedButtonBorder.copy()
                    ) {
                        Icon(Icons.Filled.Restore, null, modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(4.dp))
                        Text("Reset")
                    }
                    Button(
                        onClick = { viewModel.saveSystemPrompt(promptInput) },
                        enabled = promptInput != systemPrompt && promptInput.isNotBlank(),
                        colors = ButtonDefaults.buttonColors(containerColor = TravlyticBlue)
                    ) {
                        Icon(Icons.Filled.Save, null, modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(4.dp))
                        Text("Guardar")
                    }
                }
            }

            // ─── Entrenamiento IA ──────────────────────────────────────────
            SettingsSection(title = "🧠 Entrenamiento IA") {
                Text(
                    "Agrega reglas estrictas o enseña a Gemini cómo responder usando ejemplos (Few-Shot).",
                    color = TravlyticOnSurface2, fontSize = 12.sp
                )
                Spacer(Modifier.height(12.dp))
                Button(
                    onClick = onNavigateToTraining,
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(containerColor = TravlyticBlue)
                ) {
                    Icon(Icons.Filled.School, null, modifier = Modifier.size(16.dp))
                    Spacer(Modifier.width(8.dp))
                    Text("Abrir Panel de Entrenamiento")
                }
            }

            // ─── Info Section ──────────────────────────────────────────
            SettingsSection(title = "ℹ️ Información") {
                InfoRow("Versión", "1.0.0")
                InfoRow("Motor IA", "Gemini 2.0 Flash")
                InfoRow("Base de datos", "Room (SQLite local)")
                InfoRow("Sheets API", "v4")
                Spacer(Modifier.height(4.dp))
                Text(
                    "Travlytic responde automáticamente mensajes de WhatsApp usando tu contenido de Google Sheets como fuente de conocimiento.",
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
        Text(label, color = TravlyticOnSurface2, fontSize = 13.sp)
        Text(value, color = TravlyticOnSurface, fontSize = 13.sp, fontWeight = FontWeight.Medium)
    }
}

@Composable
fun settingsTextFieldColors() = OutlinedTextFieldDefaults.colors(
    focusedBorderColor = TravlyticBlue,
    unfocusedBorderColor = TravlyticSurface3,
    focusedTextColor = TravlyticOnSurface,
    unfocusedTextColor = TravlyticOnSurface,
    cursorColor = TravlyticBlue,
    focusedLabelColor = TravlyticBlue,
    unfocusedLabelColor = TravlyticOnSurface2
)

@Composable
fun GoogleAccountCard(
    email: String,
    onSignIn: () -> Unit,
    onSignOut: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = TravlyticSurface3),
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
                        .background(if (email.isNotBlank()) TravlyticBlue else TravlyticSurface2),
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
                        modifier = Modifier.widthIn(max = 160.dp)
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
