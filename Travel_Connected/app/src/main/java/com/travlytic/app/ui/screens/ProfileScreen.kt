package com.travlytic.app.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.background
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.travlytic.app.ui.theme.*
import com.travlytic.app.ui.viewmodel.MainViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    viewModel: MainViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }

    val profileName by viewModel.profileUserName.collectAsState()
    val businessName by viewModel.profileBusinessName.collectAsState()
    val tone by viewModel.profileTone.collectAsState()

    var nameInput by remember(profileName) { mutableStateOf(profileName) }
    var businessInput by remember(businessName) { mutableStateOf(businessName) }
    var toneInput by remember(tone) { mutableStateOf(tone) }

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
                title = { Text("Perfil de Usuario", color = MinItoOnSurface, fontWeight = FontWeight.SemiBold) },
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
            // ─── Profile Info ──────────────────────────────────────────
            SettingsSection(title = "📝 Datos Generales") {
                Text(
                    "Estos datos ayudarán a Gemini a personalizar sus respuestas y hablar de ti a los clientes.",
                    color = MinItoOnSurface2, fontSize = 12.sp
                )
                Spacer(Modifier.height(12.dp))
                OutlinedTextField(
                    value = nameInput,
                    onValueChange = { nameInput = it },
                    label = { Text("Tu Nombre o Nombre de Agente") },
                    placeholder = { Text("Ej: Carlos, Ana, Agente Virtual") },
                    modifier = Modifier.fillMaxWidth(),
                    colors = settingsTextFieldColors(),
                    singleLine = true
                )
                Spacer(Modifier.height(8.dp))
                OutlinedTextField(
                    value = businessInput,
                    onValueChange = { businessInput = it },
                    label = { Text("Nombre de la Empresa o Negocio") },
                    placeholder = { Text("Ej: Pizzería La Roma, Consultorio Dental") },
                    modifier = Modifier.fillMaxWidth(),
                    colors = settingsTextFieldColors(),
                    singleLine = true
                )
                Spacer(Modifier.height(8.dp))
                OutlinedTextField(
                    value = toneInput,
                    onValueChange = { toneInput = it },
                    label = { Text("Tono de Respuesta") },
                    placeholder = { Text("Ej: Formal y respetuoso, Casual y amigable con emojis") },
                    modifier = Modifier.fillMaxWidth(),
                    colors = settingsTextFieldColors(),
                    singleLine = false,
                    minLines = 2
                )
                
                Spacer(Modifier.height(16.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.End
                ) {
                    val isChanged = nameInput != profileName ||
                                    businessInput != businessName ||
                                    toneInput != tone

                    Button(
                        onClick = {
                            viewModel.saveProfileInfo(nameInput, businessInput, toneInput)
                        },
                        enabled = isChanged,
                        colors = ButtonDefaults.buttonColors(containerColor = MinItoBlue)
                    ) {
                        Icon(Icons.Filled.Save, null, modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(4.dp))
                        Text("Guardar Cambios")
                    }
                }
            }
        }
    }
}
