package com.travlytic.app.ui.screens

import android.content.Intent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.travlytic.app.data.db.entities.TrainingRule
import com.travlytic.app.ui.theme.*
import com.travlytic.app.ui.viewmodel.MainViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TrainingScreen(
    viewModel: MainViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit
) {
    val rules by viewModel.trainingRules.collectAsState(initial = emptyList())
    var selectedTab by remember { mutableStateOf(0) } // 0 = Reglas, 1 = Ejemplos
    var showAddDialog by remember { mutableStateOf(false) }

    val context = LocalContext.current

    val exportJson by viewModel.exportEvent.collectAsState(initial = null)
    
    LaunchedEffect(exportJson) {
        exportJson?.let { json ->
            val sendIntent = Intent().apply {
                action = Intent.ACTION_SEND
                putExtra(Intent.EXTRA_TEXT, json)
                type = "text/plain"
            }
            val shareIntent = Intent.createChooser(sendIntent, "Exportar Configuración Travlytic")
            context.startActivity(shareIntent)
            viewModel.clearExportEvent()
        }
    }

    val importLauncher = rememberLauncherForActivityResult(ActivityResultContracts.GetContent()) { uri ->
        uri?.let {
            val inputStream = context.contentResolver.openInputStream(it)
            val jsonString = inputStream?.bufferedReader().use { reader -> reader?.readText() }
            if (!jsonString.isNullOrBlank()) {
                viewModel.importConfiguration(jsonString)
            }
        }
    }

    Scaffold(
        containerColor = TravlyticSurface,
        topBar = {
            TopAppBar(
                title = { Text("Entrenamiento IA", color = TravlyticOnSurface, fontWeight = FontWeight.SemiBold) },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Filled.ArrowBack, "Volver", tint = TravlyticOnSurface)
                    }
                },
                actions = {
                    IconButton(onClick = { importLauncher.launch("application/json") }) {
                        Icon(Icons.Filled.Download, contentDescription = "Importar", tint = TravlyticBlue)
                    }
                    IconButton(onClick = { viewModel.exportConfiguration() }) {
                        Icon(Icons.Filled.Share, contentDescription = "Exportar", tint = TravlyticBlue)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = TravlyticSurface)
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = { showAddDialog = true },
                containerColor = TravlyticBlue,
                contentColor = Color.White
            ) {
                Icon(Icons.Filled.Add, "Agregar")
            }
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            TabRow(
                selectedTabIndex = selectedTab,
                containerColor = TravlyticSurface,
                contentColor = TravlyticBlue,
                indicator = { tabPositions ->
                    TabRowDefaults.SecondaryIndicator(
                        Modifier.tabIndicatorOffset(tabPositions[selectedTab]),
                        color = TravlyticBlue
                    )
                }
            ) {
                Tab(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    text = { Text("Reglas Estrictas", color = if (selectedTab == 0) TravlyticBlue else TravlyticOnSurface2) }
                )
                Tab(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    text = { Text("Ejemplos (Few-Shot)", color = if (selectedTab == 1) TravlyticBlue else TravlyticOnSurface2) }
                )
            }

            val filteredRules = if (selectedTab == 0) {
                rules.filter { it.type == "RULE" }
            } else {
                rules.filter { it.type == "EXAMPLE" }
            }

            if (filteredRules.isEmpty()) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Text(
                        if (selectedTab == 0) "No hay reglas definidas." else "No hay ejemplos (Few-Shot).",
                        color = TravlyticOnSurface2
                    )
                }
            } else {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    items(filteredRules) { rule ->
                        RuleItem(
                            rule = rule,
                            onToggle = { viewModel.toggleTrainingRule(rule) },
                            onDelete = { viewModel.deleteTrainingRule(rule) }
                        )
                    }
                }
            }
        }
    }

    if (showAddDialog) {
        val isRuleMode = selectedTab == 0
        AddRuleDialog(
            isRuleMode = isRuleMode,
            onDismiss = { showAddDialog = false },
            onConfirm = { input, output ->
                viewModel.addTrainingRule(
                    type = if (isRuleMode) "RULE" else "EXAMPLE",
                    input = input,
                    output = output
                )
                showAddDialog = false
            }
        )
    }
}

@Composable
fun RuleItem(rule: TrainingRule, onToggle: () -> Unit, onDelete: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = TravlyticSurface2),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                if (rule.type == "RULE") {
                    Text("Regla", color = TravlyticOrange, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(4.dp))
                    Text("« ${rule.input} »", color = TravlyticOnSurface, fontSize = 14.sp)
                } else {
                    Text("Si el cliente dice:", color = TravlyticBlueLight, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    Text(rule.input, color = TravlyticOnSurface, fontSize = 14.sp, maxLines = 2, overflow = TextOverflow.Ellipsis)
                    
                    Spacer(Modifier.height(8.dp))
                    
                    Text("Responder exactamente:", color = TravlyticGreen, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    Text(rule.output ?: "", color = TravlyticOnSurface, fontSize = 14.sp, maxLines = 4, overflow = TextOverflow.Ellipsis)
                }
            }
            
            Switch(
                checked = rule.isActive,
                onCheckedChange = { onToggle() },
                colors = SwitchDefaults.colors(checkedThumbColor = TravlyticBlue, checkedTrackColor = TravlyticBlue.copy(alpha = 0.3f))
            )
            
            IconButton(onClick = onDelete) {
                Icon(Icons.Filled.Delete, "Eliminar", tint = TravlyticRed)
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AddRuleDialog(
    isRuleMode: Boolean,
    onDismiss: () -> Unit,
    onConfirm: (String, String?) -> Unit
) {
    var input by remember { mutableStateOf("") }
    var output by remember { mutableStateOf("") }

    AlertDialog(
        onDismissRequest = onDismiss,
        containerColor = TravlyticSurface2,
        title = {
            Text(if (isRuleMode) "Nueva Regla Estricta" else "Nuevo Ejemplo (Few-Shot)", color = TravlyticOnSurface)
        },
        text = {
            Column {
                if (isRuleMode) {
                    Text("Define una instrucción que Gemini debe seguir siempre.", color = TravlyticOnSurface2, fontSize = 12.sp)
                    Spacer(Modifier.height(8.dp))
                    OutlinedTextField(
                        value = input,
                        onValueChange = { input = it },
                        label = { Text("Ej: Nunca compartas contraseñas") },
                        modifier = Modifier.fillMaxWidth(),
                        colors = settingsTextFieldColors()
                    )
                } else {
                    Text("Dale a Gemini un ejemplo exacto de cómo responder.", color = TravlyticOnSurface2, fontSize = 12.sp)
                    Spacer(Modifier.height(8.dp))
                    OutlinedTextField(
                        value = input,
                        onValueChange = { input = it },
                        label = { Text("Si te preguntan...") },
                        modifier = Modifier.fillMaxWidth(),
                        colors = settingsTextFieldColors(),
                        singleLine = false
                    )
                    Spacer(Modifier.height(8.dp))
                    OutlinedTextField(
                        value = output,
                        onValueChange = { output = it },
                        label = { Text("Debes responder...") },
                        modifier = Modifier.fillMaxWidth(),
                        colors = settingsTextFieldColors(),
                        singleLine = false
                    )
                }
            }
        },
        confirmButton = {
            Button(
                onClick = { onConfirm(input, if (isRuleMode) null else output) },
                enabled = input.isNotBlank() && (isRuleMode || output.isNotBlank()),
                colors = ButtonDefaults.buttonColors(containerColor = TravlyticBlue)
            ) {
                Text("Guardar")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancelar", color = TravlyticOnSurface2)
            }
        }
    )
}
