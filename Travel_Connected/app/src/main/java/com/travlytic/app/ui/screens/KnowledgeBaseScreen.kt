package com.travlytic.app.ui.screens

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
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
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.travlytic.app.data.db.entities.KnowledgeItem
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
    
    var showAddUrlDialog by remember { mutableStateOf(false) }
    var pendingExcelUri by remember { mutableStateOf<Uri?>(null) }
    
    val excelPickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocument()
    ) { uri ->
        if (uri != null) {
            pendingExcelUri = uri
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
                title = { Text("Base de Conocimiento", color = TravlyticOnSurface, fontWeight = FontWeight.SemiBold) },
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
            Column(
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    "📚 Documentación Local",
                    color = TravlyticOnSurface,
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 16.sp
                )
                Spacer(Modifier.height(12.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.End
                ) {
                    FilledTonalButton(
                        onClick = { excelPickerLauncher.launch(arrayOf("*/*")) },
                        colors = ButtonDefaults.filledTonalButtonColors(containerColor = TravlyticGreen.copy(alpha=0.2f), contentColor = TravlyticGreen)
                    ) {
                        Icon(Icons.Filled.UploadFile, null, modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(4.dp))
                        Text("Subir Excel / CSV", fontSize = 13.sp)
                    }
                }
            }
            Spacer(Modifier.height(8.dp))
            Text(
                "La IA utilizará esta información para responder a tus clientes.",
                color = TravlyticOnSurface2, fontSize = 13.sp, lineHeight = 18.sp
            )
            Spacer(Modifier.height(16.dp))

            if (uiState.isLoading) {
                LinearProgressIndicator(modifier = Modifier.fillMaxWidth(), color = TravlyticBlue)
                Spacer(Modifier.height(16.dp))
            }

            LazyColumn(
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                if (uiState.knowledgeItems.isEmpty()) {
                    item { EmptyKnowledgePlaceholder() }
                } else {
                    items(uiState.knowledgeItems, key = { it.id }) { item ->
                        KnowledgeCard(
                            item = item,
                            onToggle = { enabled -> viewModel.toggleKnowledgeItem(item, enabled) },
                            onDelete = { viewModel.deleteKnowledgeItem(item) }
                        )
                    }
                }
                item { Spacer(Modifier.height(24.dp)) }
            }
        }
    }

    if (pendingExcelUri != null) {
        AddReferenceDialog(
            title = "Importar Excel Local",
            label = "Nombre de referencia:",
            placeholder = "Ej. Inventario",
            showSourceInput = false,
            onDismiss = { pendingExcelUri = null },
            onConfirm = { _, reference ->
                viewModel.importExcelKnowledge(pendingExcelUri!!, reference)
                pendingExcelUri = null
            }
        )
    }
}

@Composable
fun KnowledgeCard(
    item: KnowledgeItem,
    onToggle: (Boolean) -> Unit,
    onDelete: () -> Unit
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
                    .background(TravlyticGreen.copy(0.2f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(Icons.Filled.TableChart, null,
                    tint = TravlyticGreen, modifier = Modifier.size(20.dp))
            }
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Text(item.reference, color = TravlyticOnSurface,
                    fontWeight = FontWeight.Medium, fontSize = 14.sp,
                    maxLines = 1, overflow = TextOverflow.Ellipsis)
                Text(
                    "Act. ${dateFormat.format(Date(item.lastUpdated))}",
                    color = TravlyticOnSurface2, fontSize = 11.sp,
                    maxLines = 2, overflow = TextOverflow.Ellipsis
                )
            }
            
            Switch(
                checked = item.isEnabled,
                onCheckedChange = onToggle,
                modifier = Modifier.scale(0.8f)
            )

            IconButton(onClick = onDelete, modifier = Modifier.size(36.dp)) {
                Icon(Icons.Filled.DeleteOutline, "Eliminar",
                    tint = TravlyticRed.copy(alpha = 0.7f), modifier = Modifier.size(18.dp))
            }
        }
    }
}

@Composable
fun EmptyKnowledgePlaceholder() {
    Box(
        modifier = Modifier.fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(TravlyticSurface2)
            .padding(24.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Icon(Icons.Outlined.Folder, null,
                tint = TravlyticOnSurface2, modifier = Modifier.size(36.dp))
            Spacer(Modifier.height(8.dp))
            Text("Sube un Excel/CSV para comenzar",
                color = TravlyticOnSurface2, fontSize = 13.sp)
        }
    }
}

@Composable
fun AddReferenceDialog(
    title: String,
    label: String,
    placeholder: String,
    showSourceInput: Boolean = true,
    onDismiss: () -> Unit,
    onConfirm: (String, String) -> Unit
) {
    var source by remember { mutableStateOf("") }
    var reference by remember { mutableStateOf("") }

    AlertDialog(
        onDismissRequest = onDismiss,
        containerColor = TravlyticSurface2,
        title = { Text(title, color = TravlyticOnSurface) },
        text = {
            Column {
                if (showSourceInput) {
                    Text(label, color = TravlyticOnSurface2, fontSize = 13.sp)
                    Spacer(Modifier.height(8.dp))
                    OutlinedTextField(
                        value = source,
                        onValueChange = { source = it },
                        placeholder = { Text(placeholder, fontSize = 12.sp) },
                        singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = TravlyticOnSurface,
                            unfocusedTextColor = TravlyticOnSurface
                        )
                    )
                    Spacer(Modifier.height(16.dp))
                }
                Text("Nombre de Referencia:", color = TravlyticOnSurface2, fontSize = 13.sp)
                Spacer(Modifier.height(8.dp))
                OutlinedTextField(
                    value = reference,
                    onValueChange = { reference = it },
                    placeholder = { Text("Ej. Precios 2024", fontSize = 12.sp) },
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = TravlyticOnSurface,
                        unfocusedTextColor = TravlyticOnSurface
                    )
                )
            }
        },
        confirmButton = {
            Button(
                onClick = { if (reference.isNotBlank() && (!showSourceInput || source.isNotBlank())) onConfirm(source, reference) },
                colors = ButtonDefaults.buttonColors(containerColor = TravlyticBlue)
            ) { Text("Guardar") }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("Cancelar", color = TravlyticOnSurface2) }
        }
    )
}
