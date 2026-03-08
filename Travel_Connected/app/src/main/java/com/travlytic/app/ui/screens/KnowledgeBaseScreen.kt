package com.travlytic.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.travlytic.app.data.db.entities.RegisteredSheet
import com.travlytic.app.ui.theme.*
import com.travlytic.app.ui.viewmodel.MainViewModel
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun KnowledgeBaseScreen(
    viewModel: MainViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }
    var showAddSheetDialog by remember { mutableStateOf(false) }

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
                title = { Text("Fuente de Conocimiento", color = TravlyticOnSurface, fontWeight = FontWeight.SemiBold) },
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
                .padding(horizontal = 16.dp)
        ) {
            Spacer(Modifier.height(16.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    "📊 Google Sheets Registrados",
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
            Spacer(Modifier.height(8.dp))
            Text(
                "La IA contestará a los usuarios basándose en la información extraída de los siguientes documentos.",
                color = TravlyticOnSurface2, fontSize = 13.sp, lineHeight = 18.sp
            )
            Spacer(Modifier.height(16.dp))

            LazyColumn(
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
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
                item { Spacer(Modifier.height(24.dp)) }
            }
        }
    }

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
