package com.travlytic.app.ui.screens

import androidx.compose.animation.*
import androidx.compose.animation.core.*
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
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.travlytic.app.engine.SessionSummary
import com.travlytic.app.engine.TtsState
import com.travlytic.app.ui.theme.*
import com.travlytic.app.ui.viewmodel.MainViewModel
import com.travlytic.app.ui.viewmodel.SummaryUiState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SummaryScreen(
    viewModel: MainViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit
) {
    val summaryState by viewModel.summaryUiState.collectAsState()
    val ttsState    by viewModel.ttsState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = MinItoSurface,
        topBar = {
            TopAppBar(
                title = {
                    Text("Resumen de Sesión",
                        color = MinItoOnSurface, fontWeight = FontWeight.SemiBold)
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Filled.ArrowBack, "Volver", tint = MinItoOnSurface)
                    }
                },
                actions = {
                    // Selector de período
                    val periods = listOf("Hoy","Semana","Todo")
                    periods.forEach { period ->
                        val selected = summaryState.selectedPeriod == period
                        FilterChip(
                            selected = selected,
                            onClick = { viewModel.setSummaryPeriod(period) },
                            label = { Text(period, fontSize = 11.sp) },
                            modifier = Modifier.padding(end = 4.dp),
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = MinItoBlue.copy(alpha = 0.25f),
                                selectedLabelColor = MinItoBlue
                            )
                        )
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
            when {
                summaryState.isLoading -> {
                    LoadingCard()
                }
                summaryState.summary != null -> {
                    val summary = summaryState.summary!!

                    // ─── Reproductor de audio ──────────────────────────────
                    AudioPlayerCard(
                        summary = summary,
                        ttsState = ttsState,
                        speechRate = summaryState.speechRate,
                        onPlay = { viewModel.speakSummary() },
                        onStop = { viewModel.stopSpeaking() },
                        onRateChange = { viewModel.setSpeechRate(it) }
                    )

                    // ─── Estadísticas ──────────────────────────────────────
                    StatisticsCard(summary)

                    // ─── Top Contactos ─────────────────────────────────────
                    if (summary.topContacts.isNotEmpty()) {
                        TopContactsCard(summary.topContacts)
                    }

                    // ─── Tópicos frecuentes ────────────────────────────────
                    if (summary.topTopics.isNotEmpty()) {
                        TopicsCard(summary.topTopics)
                    }

                    // ─── Texto narrativo completo ──────────────────────────
                    NarrativeCard(summary.narrativeText)

                    // ─── Botón regenerar ───────────────────────────────────
                    OutlinedButton(
                        onClick = { viewModel.generateSummary() },
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.outlinedButtonColors(
                            contentColor = MinItoBlue
                        ),
                        border = androidx.compose.foundation.BorderStroke(1.dp, MinItoBlue.copy(alpha = 0.5f))
                    ) {
                        Icon(Icons.Filled.Refresh, null, modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(6.dp))
                        Text("Regenerar resumen", fontSize = 13.sp)
                    }
                }
                summaryState.error.isNotBlank() -> {
                    ErrorCard(summaryState.error) { viewModel.generateSummary() }
                }
                else -> {
                    // Estado inicial: botón para generar
                    EmptySummaryCard { viewModel.generateSummary() }
                }
            }
            Spacer(Modifier.height(24.dp))
        }
    }
}

// ─── Audio Player Card ────────────────────────────────────────────────────────

@Composable
fun AudioPlayerCard(
    summary: SessionSummary,
    ttsState: TtsState,
    speechRate: Float,
    onPlay: () -> Unit,
    onStop: () -> Unit,
    onRateChange: (Float) -> Unit
) {
    val isSpeaking = ttsState == TtsState.SPEAKING

    // Animación del botón de play cuando está hablando
    val scale by animateFloatAsState(
        targetValue = if (isSpeaking) 1.08f else 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(700, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulse"
    )

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.Transparent),
        shape = RoundedCornerShape(20.dp)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    Brush.linearGradient(
                        listOf(
                            MinItoBlue.copy(alpha = 0.25f),
                            MinItoGreen.copy(alpha = 0.15f)
                        )
                    )
                )
                .border(
                    1.dp,
                    Brush.linearGradient(listOf(MinItoBlue.copy(0.5f), MinItoGreen.copy(0.3f))),
                    RoundedCornerShape(20.dp)
                )
        ) {
            Column(
                modifier = Modifier.padding(20.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    "🎙️ Resumen en voz",
                    color = MinItoOnSurface2,
                    fontSize = 12.sp
                )
                Spacer(Modifier.height(16.dp))

                // Botón central de play/stop
                Box(
                    modifier = Modifier
                        .scale(if (isSpeaking) scale else 1f)
                        .size(72.dp)
                        .clip(CircleShape)
                        .background(
                            Brush.radialGradient(
                                listOf(
                                    if (isSpeaking) MinItoRed else MinItoBlue,
                                    if (isSpeaking) MinItoRed.copy(0.7f) else MinItoBlue.copy(0.7f)
                                )
                            )
                        )
                        .clickable { if (isSpeaking) onStop() else onPlay() },
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        if (isSpeaking) Icons.Filled.Stop else Icons.Filled.PlayArrow,
                        contentDescription = if (isSpeaking) "Detener" else "Reproducir",
                        tint = Color.White,
                        modifier = Modifier.size(36.dp)
                    )
                }

                Spacer(Modifier.height(12.dp))

                Text(
                    if (isSpeaking) "Reproduciendo..." else "Toca para escuchar el resumen",
                    color = if (isSpeaking) MinItoGreen else MinItoOnSurface2,
                    fontSize = 12.sp,
                    fontWeight = if (isSpeaking) FontWeight.SemiBold else FontWeight.Normal
                )

                // ─── Control de velocidad ──────────────────────────────
                Spacer(Modifier.height(16.dp))
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.Center
                ) {
                    Text("🐢", fontSize = 14.sp)
                    Slider(
                        value = speechRate,
                        onValueChange = onRateChange,
                        valueRange = 0.5f..2.0f,
                        modifier = Modifier.width(160.dp).padding(horizontal = 8.dp),
                        colors = SliderDefaults.colors(
                            thumbColor = MinItoBlue,
                            activeTrackColor = MinItoBlue
                        )
                    )
                    Text("🐇", fontSize = 14.sp)
                }
                Text(
                    "Velocidad: ${String.format("%.1f", speechRate)}x",
                    color = MinItoOnSurface2, fontSize = 10.sp
                )
            }
        }
    }
}

// ─── Statistics Card ──────────────────────────────────────────────────────────

@Composable
fun StatisticsCard(summary: SessionSummary) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MinItoSurface2),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(Modifier.padding(16.dp)) {
            Text("📊 Estadísticas", color = MinItoOnSurface,
                fontWeight = FontWeight.SemiBold, fontSize = 15.sp)
            Spacer(Modifier.height(14.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatPill(
                    icon = Icons.Filled.Message,
                    value = "${summary.totalReplies}",
                    label = "Respuestas",
                    color = MinItoBlue
                )
                StatPill(
                    icon = Icons.Filled.People,
                    value = "${summary.uniqueContacts}",
                    label = "Contactos",
                    color = MinItoGreen
                )
                StatPill(
                    icon = Icons.Filled.Warning,
                    value = "${summary.totalEscalations}",
                    label = "Escalados",
                    color = MinItoOrange
                )
            }
        }
    }
}

@Composable
fun StatPill(icon: ImageVector, value: String, label: String, color: Color) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier
            .clip(RoundedCornerShape(12.dp))
            .background(color.copy(alpha = 0.1f))
            .padding(horizontal = 24.dp, vertical = 12.dp)
    ) {
        Icon(icon, null, tint = color, modifier = Modifier.size(22.dp))
        Spacer(Modifier.height(4.dp))
        Text(value, color = MinItoOnSurface, fontWeight = FontWeight.Bold, fontSize = 24.sp)
        Text(label, color = color, fontSize = 11.sp)
    }
}

// ─── Top Contacts Card ────────────────────────────────────────────────────────

@Composable
fun TopContactsCard(contacts: List<Pair<String, Int>>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MinItoSurface2),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(Modifier.padding(16.dp)) {
            Text("👤 Contactos más activos", color = MinItoOnSurface,
                fontWeight = FontWeight.SemiBold, fontSize = 15.sp)
            Spacer(Modifier.height(10.dp))
            contacts.forEachIndexed { index, (name, count) ->
                val maxCount = contacts.firstOrNull()?.second ?: 1
                val progress = count.toFloat() / maxCount.toFloat()
                ContactBar(
                    rank  = index + 1,
                    name = name,
                    count = count,
                    progress = progress
                )
                if (index < contacts.lastIndex) Spacer(Modifier.height(8.dp))
            }
        }
    }
}

@Composable
fun ContactBar(rank: Int, name: String, count: Int, progress: Float) {
    val barColor = when (rank) {
        1 -> Color(0xFFFFD700) // Oro
        2 -> Color(0xFFC0C0C0) // Plata
        3 -> Color(0xFFCD7F32) // Bronce
        else -> MinItoBlue.copy(alpha = 0.7f)
    }
    Column {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("#$rank", color = barColor, fontWeight = FontWeight.Bold,
                    fontSize = 12.sp, modifier = Modifier.width(24.dp))
                Text(name, color = MinItoOnSurface, fontSize = 13.sp, maxLines = 1)
            }
            Text("$count msg", color = MinItoOnSurface2, fontSize = 11.sp)
        }
        Spacer(Modifier.height(3.dp))
        LinearProgressIndicator(
            progress = progress,
            modifier = Modifier.fillMaxWidth().height(4.dp).clip(RoundedCornerShape(2.dp)),
            color = barColor,
            trackColor = MinItoSurface3
        )
    }
}

// ─── Topics Card ──────────────────────────────────────────────────────────────

@Composable
fun TopicsCard(topics: List<String>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MinItoSurface2),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(Modifier.padding(16.dp)) {
            Text("🔍 Tópicos frecuentes", color = MinItoOnSurface,
                fontWeight = FontWeight.SemiBold, fontSize = 15.sp)
            Spacer(Modifier.height(10.dp))
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                topics.forEach { topic ->
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(20.dp))
                            .background(MinItoBlue.copy(alpha = 0.15f))
                            .border(1.dp, MinItoBlue.copy(0.3f), RoundedCornerShape(20.dp))
                            .padding(horizontal = 12.dp, vertical = 6.dp)
                    ) {
                        Text(topic, color = MinItoBlue, fontSize = 12.sp,
                            fontWeight = FontWeight.Medium)
                    }
                }
            }
        }
    }
}

// ─── Narrative Card ───────────────────────────────────────────────────────────

@Composable
fun NarrativeCard(text: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MinItoSurface2),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Filled.AutoAwesome, null,
                    tint = MinItoBlue, modifier = Modifier.size(16.dp))
                Spacer(Modifier.width(6.dp))
                Text("Resumen generado por Gemini", color = MinItoOnSurface,
                    fontWeight = FontWeight.SemiBold, fontSize = 15.sp)
            }
            Spacer(Modifier.height(10.dp))
            Text(
                text,
                color = MinItoOnSurface,
                fontSize = 14.sp,
                lineHeight = 21.sp
            )
        }
    }
}

// ─── Loading / Empty / Error Cards ───────────────────────────────────────────

@Composable
fun LoadingCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MinItoSurface2),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(40.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            CircularProgressIndicator(color = MinItoBlue)
            Spacer(Modifier.height(16.dp))
            Text("Gemini está analizando tu sesión...",
                color = MinItoOnSurface2, fontSize = 14.sp)
        }
    }
}

@Composable
fun EmptySummaryCard(onGenerate: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MinItoSurface2),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(40.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(Icons.Filled.AutoAwesome, null,
                tint = MinItoOnSurface2, modifier = Modifier.size(48.dp))
            Spacer(Modifier.height(12.dp))
            Text("Sin resumen generado aún",
                color = MinItoOnSurface, fontWeight = FontWeight.SemiBold)
            Text("Genera un resumen de la actividad del bot y escúchalo en voz alta.",
                color = MinItoOnSurface2, fontSize = 12.sp,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(top = 4.dp, bottom = 20.dp))
            Button(
                onClick = onGenerate,
                colors = ButtonDefaults.buttonColors(containerColor = MinItoBlue)
            ) {
                Icon(Icons.Filled.AutoAwesome, null, modifier = Modifier.size(16.dp))
                Spacer(Modifier.width(6.dp))
                Text("✨ Generar resumen con Gemini")
            }
        }
    }
}

@Composable
fun ErrorCard(error: String, onRetry: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MinItoSurface2),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(error, color = MinItoRed, fontSize = 13.sp, textAlign = TextAlign.Center)
            Spacer(Modifier.height(12.dp))
            TextButton(onClick = onRetry) {
                Text("Reintentar", color = MinItoBlue)
            }
        }
    }
}
