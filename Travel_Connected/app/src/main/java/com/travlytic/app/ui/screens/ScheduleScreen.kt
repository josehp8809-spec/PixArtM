package com.travlytic.app.ui.screens

import android.app.TimePickerDialog
import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.travlytic.app.ui.theme.*
import com.travlytic.app.ui.viewmodel.MainViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ScheduleScreen(
    viewModel: MainViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit
) {
    val scheduleState  by viewModel.scheduleState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current

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
                title = { Text("Horarios", color = MinItoOnSurface, fontWeight = FontWeight.SemiBold) },
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

            // ─── Enable Schedule Toggle ───────────────────────────────
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
                            Text("⏰ Programación de Horario",
                                color = MinItoOnSurface, fontWeight = FontWeight.SemiBold)
                            Text(
                                if (scheduleState.enabled) "El bot responde solo en el horario definido"
                                else "El bot responde las 24 horas",
                                color = MinItoOnSurface2, fontSize = 12.sp
                            )
                        }
                        Switch(
                            checked = scheduleState.enabled,
                            onCheckedChange = { viewModel.setScheduleEnabled(it) },
                            colors = SwitchDefaults.colors(
                                checkedTrackColor = MinItoBlue,
                                uncheckedTrackColor = MinItoSurface3
                            )
                        )
                    }
                }
            }

            // ─── Time Range ───────────────────────────────────────────
            AnimatedVisibility(scheduleState.enabled) {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {

                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = MinItoSurface2),
                        shape = RoundedCornerShape(16.dp)
                    ) {
                        Column(Modifier.padding(16.dp)) {
                            Text("🕐 Rango de horas",
                                color = MinItoOnSurface, fontWeight = FontWeight.SemiBold)
                            Spacer(Modifier.height(16.dp))
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceEvenly,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                TimePickerButton(
                                    label = "Inicio",
                                    hour = scheduleState.startHour,
                                    minute = scheduleState.startMinute,
                                    context = context
                                ) { h, m -> viewModel.setScheduleStart(h, m) }

                                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                    Icon(Icons.Filled.ArrowForward, null,
                                        tint = MinItoOnSurface2, modifier = Modifier.size(20.dp))
                                    Text(calculateDuration(
                                        scheduleState.startHour, scheduleState.startMinute,
                                        scheduleState.endHour, scheduleState.endMinute
                                    ),
                                        color = MinItoOnSurface2, fontSize = 11.sp)
                                }

                                TimePickerButton(
                                    label = "Fin",
                                    hour = scheduleState.endHour,
                                    minute = scheduleState.endMinute,
                                    context = context
                                ) { h, m -> viewModel.setScheduleEnd(h, m) }
                            }
                        }
                    }

                    // ─── Days of week ─────────────────────────────────
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = MinItoSurface2),
                        shape = RoundedCornerShape(16.dp)
                    ) {
                        Column(Modifier.padding(16.dp)) {
                            Text("📅 Días activos",
                                color = MinItoOnSurface, fontWeight = FontWeight.SemiBold)
                            Spacer(Modifier.height(12.dp))
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                val dayLabels = listOf("L","M","X","J","V","S","D")
                                dayLabels.forEachIndexed { i, label ->
                                    val dayNum = i + 1
                                    val isSelected = dayNum in scheduleState.activeDays
                                    DayChip(
                                        label = label,
                                        isSelected = isSelected,
                                        onClick = { viewModel.toggleScheduleDay(dayNum) }
                                    )
                                }
                            }
                            Spacer(Modifier.height(8.dp))
                            // Botones rápidos
                            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                FilterChip(
                                    selected = scheduleState.activeDays == setOf(1,2,3,4,5),
                                    onClick = { viewModel.setScheduleDays(setOf(1,2,3,4,5)) },
                                    label = { Text("Lun–Vie", fontSize = 11.sp) },
                                    colors = FilterChipDefaults.filterChipColors(
                                        selectedContainerColor = TravlyticBlue.copy(alpha = 0.2f),
                                        selectedLabelColor = TravlyticBlue
                                    )
                                )
                                FilterChip(
                                    selected = scheduleState.activeDays == setOf(6,7),
                                    onClick = { viewModel.setScheduleDays(setOf(6,7)) },
                                    label = { Text("Fin de semana", fontSize = 11.sp) },
                                    colors = FilterChipDefaults.filterChipColors(
                                        selectedContainerColor = TravlyticBlue.copy(alpha = 0.2f),
                                        selectedLabelColor = TravlyticBlue
                                    )
                                )
                                FilterChip(
                                    selected = scheduleState.activeDays == (1..7).toSet(),
                                    onClick = { viewModel.setScheduleDays((1..7).toSet()) },
                                    label = { Text("Todos", fontSize = 11.sp) },
                                    colors = FilterChipDefaults.filterChipColors(
                                        selectedContainerColor = MinItoGreen.copy(alpha = 0.2f),
                                        selectedLabelColor = MinItoGreen
                                    )
                                )
                            }
                        }
                    }

                    // ─── Resumen activo ───────────────────────────────
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(
                            containerColor = MinItoGreen.copy(alpha = 0.08f)
                        ),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Row(
                            Modifier.padding(14.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(Icons.Filled.Info, null,
                                tint = MinItoGreen, modifier = Modifier.size(18.dp))
                            Spacer(Modifier.width(10.dp))
                            Text(
                                buildScheduleSummary(scheduleState),
                                color = MinItoGreen, fontSize = 12.sp, lineHeight = 18.sp
                            )
                        }
                    }
                }
            }

            Spacer(Modifier.height(24.dp))
        }
    }
}

// ─── Composables helper ───────────────────────────────────────────────────────

@Composable
fun DayChip(label: String, isSelected: Boolean, onClick: () -> Unit) {
    Box(
        modifier = Modifier
            .size(36.dp)
            .clip(CircleShape)
            .background(
                if (isSelected) MinItoBlue else MinItoSurface3
            )
            .border(
                width = 1.dp,
                color = if (isSelected) MinItoBlue else MinItoSurface3,
                shape = CircleShape
            )
            .clickable { onClick() },
        contentAlignment = Alignment.Center
    ) {
        Text(
            label,
            color = if (isSelected) Color.White else MinItoOnSurface2,
            fontSize = 13.sp,
            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal
        )
    }
}

@Composable
fun TimePickerButton(
    label: String,
    hour: Int,
    minute: Int,
    context: Context,
    onTimePicked: (Int, Int) -> Unit
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(label, color = MinItoOnSurface2, fontSize = 12.sp)
        Spacer(Modifier.height(4.dp))
        Box(
            modifier = Modifier
                .clip(RoundedCornerShape(12.dp))
                .background(MinItoSurface3)
                .border(1.dp, MinItoBlue.copy(alpha = 0.4f), RoundedCornerShape(12.dp))
                .clickable {
                    TimePickerDialog(context, { _, h, m ->
                        onTimePicked(h, m)
                    }, hour, minute, false).show()
                }
                .padding(horizontal = 18.dp, vertical = 12.dp),
            contentAlignment = Alignment.Center
        ) {
            Text(
                String.format("%02d:%02d", hour, minute),
                color = MinItoOnSurface,
                fontWeight = FontWeight.Bold,
                fontSize = 22.sp
            )
        }
    }
}

// ─── Funciones utilitarias ────────────────────────────────────────────────────

private fun calculateDuration(sh: Int, sm: Int, eh: Int, em: Int): String {
    val startMins = sh * 60 + sm
    val endMins = eh * 60 + em
    val diff = if (endMins >= startMins) endMins - startMins else (24 * 60) - startMins + endMins
    val h = diff / 60
    val m = diff % 60
    return if (h > 0) "${h}h ${m}min" else "${m}min"
}

private fun buildScheduleSummary(state: com.travlytic.app.ui.viewmodel.ScheduleState): String {
    if (!state.enabled) return "El bot responde las 24 horas, todos los días."
    val days = state.activeDays.sorted().joinToString(", ") {
        listOf("", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom").getOrElse(it) { "?" }
    }
    return "Activo de ${String.format("%02d:%02d", state.startHour, state.startMinute)}" +
           " a ${String.format("%02d:%02d", state.endHour, state.endMinute)}\n$days"
}

@Composable
private fun AnimatedVisibility(visible: Boolean, content: @Composable () -> Unit) {
    androidx.compose.animation.AnimatedVisibility(
        visible = visible,
        enter = androidx.compose.animation.fadeIn() + androidx.compose.animation.expandVertically(),
        exit = androidx.compose.animation.fadeOut() + androidx.compose.animation.shrinkVertically()
    ) {
        content()
    }
}
