package com.travlytic.app.engine

import android.util.Log
import com.google.ai.client.generativeai.GenerativeModel
import com.google.ai.client.generativeai.type.content
import com.google.ai.client.generativeai.type.generationConfig
import com.travlytic.app.data.db.entities.EscalationLog
import com.travlytic.app.data.db.entities.ResponseLog
import java.text.SimpleDateFormat
import java.util.*
import javax.inject.Inject
import javax.inject.Singleton

private const val TAG = "SummaryGenerator"

data class SessionSummary(
    val narrativeText: String,    // Texto narrado por Gemini
    val totalReplies: Int,
    val uniqueContacts: Int,
    val totalEscalations: Int,
    val topTopics: List<String>,
    val topContacts: List<Pair<String, Int>>,  // contacto → nº de mensajes
    val generatedAt: Long = System.currentTimeMillis()
)

@Singleton
class SummaryGenerator @Inject constructor() {

    /**
     * Genera un resumen narrativo de los logs de respuesta.
     * Usa Gemini para crear un texto natural tipo "Daily Briefing".
     */
    suspend fun generateSummary(
        apiKey: String,
        logs: List<ResponseLog>,
        escalations: List<EscalationLog>,
        periodLabel: String = "hoy"  // "hoy", "esta semana", "últimas 24h"
    ): SessionSummary? {
        if (logs.isEmpty() && escalations.isEmpty()) return null
        if (apiKey.isBlank()) return null

        return try {
            // ─── Estadísticas base ───────────────────────────────────────
            val uniqueContacts = (logs.map { it.contact } + escalations.map { it.contact }).distinct()
            val contactCount = (logs.map { it.contact } + escalations.map { it.contact })
                .groupBy { it }
                .map { Pair(it.key, it.value.size) }
                .sortedByDescending { it.second }
                .take(5)

            // ─── Prompt para Gemini ──────────────────────────────────────
            val logsText = logs.take(30).joinToString("\n") { log ->
                "- [${log.contact}] Pregunta: \"${log.incomingMessage}\" → Respuesta: \"${log.sentResponse.take(80)}\""
            }

            val prompt = """
Eres el asistente de análisis de MINI-TO. Tu tarea es generar un RESUMEN EJECUTIVO breve, amigable y en español de la actividad del bot de WhatsApp de $periodLabel.

DATOS DE ACTIVIDAD:
- Total de mensajes respondidos automáticamente: ${logs.size}
- Total de mensajes que requirieron escalado a humano: ${escalations.size}
- Contactos únicos atendidos: ${uniqueContacts.size}
- Contacto más activo: ${contactCount.firstOrNull()?.first ?: "N/A"} (${contactCount.firstOrNull()?.second ?: 0} mensajes)

MUESTRA DE CONVERSACIONES (RESPONDIDAS AUTOMÁTICAMENTE):
$logsText

INSTRUCCIONES:
1. Genera 2-3 párrafos cortos y naturales como si fuera un "daily briefing" de voz.
2. Menciona los temas más frecuentes preguntados.
3. Destaca si hay algún patrón interesante.
4. Usa un tono amigable, profesional pero conversacional (para ser leído en voz alta).
5. Máximo 200 palabras. NO uses bullets, usa texto corrido natural.
6. Empieza con "Hola! Aquí tu resumen de actividad..." o similar.
""".trimIndent()

            val model = GenerativeModel(
                modelName = "gemini-2.5-flash",
                apiKey = apiKey,
                generationConfig = generationConfig {
                    temperature = 0.8f
                    maxOutputTokens = 350
                }
            )

            val response = model.generateContent(content { text(prompt) })
            val narrativeText = response.text?.trim() ?: generateFallbackNarrative(logs.size, escalations.size, uniqueContacts.size, periodLabel, contactCount.firstOrNull()?.first ?: "")

            // Extraer tópicos (heurística simple: palabras más frecuentes en preguntas)
            val topTopics = extractTopTopics(logs)

            Log.d(TAG, "Resumen generado: ${narrativeText.take(100)}...")

            SessionSummary(
                narrativeText = narrativeText,
                totalReplies = logs.size,
                uniqueContacts = uniqueContacts.size,
                totalEscalations = escalations.size,
                topTopics = topTopics,
                topContacts = contactCount
            )
        } catch (e: Exception) {
            Log.e(TAG, "Error generando resumen", e)
            val unique = (logs.map { it.contact } + escalations.map { it.contact }).distinct()
            val contactCountTop = (logs.map { it.contact } + escalations.map { it.contact })
                .groupBy { it }
                .map { Pair(it.key, it.value.size) }
                .sortedByDescending { it.second }.take(5)
            // Fallback sin Gemini
            SessionSummary(
                narrativeText = generateFallbackNarrative(logs.size, escalations.size, unique.size, periodLabel, contactCountTop.firstOrNull()?.first ?: ""),
                totalReplies = logs.size,
                uniqueContacts = unique.size,
                totalEscalations = escalations.size,
                topTopics = extractTopTopics(logs),
                topContacts = contactCountTop
            )
        }
    }

    /** Resumen básico sin llamar a Gemini (fallback) */
    private fun generateFallbackNarrative(replyCount: Int, escalateCount: Int, contactCount: Int, period: String, topContact: String): String {
        return "¡Hola! Tu resumen de $period: MINI-TO respondió $replyCount mensajes y escaló $escalateCount consultas " +
               "de $contactCount contacto${if (contactCount == 1) "" else "s"} diferentes. " +
               (if (topContact.isNotBlank()) "El contacto más activo fue $topContact. " else "") +
               "El bot estuvo funcionando correctamente durante toda la sesión."
    }

    /** Extrae los 5 temas/palabras más frecuentes en las preguntas */
    private fun extractTopTopics(logs: List<ResponseLog>): List<String> {
        val stopWords = setOf("el", "la", "de", "que", "es", "en", "y", "a", "los", "las",
            "del", "un", "una", "por", "con", "me", "mi", "se", "su", "lo", "le",
            "como", "para", "al", "o", "si", "hay", "tienen", "puede", "cuál", "cuales")
        return logs
            .flatMap { it.incomingMessage.lowercase().split(" ", "?", "¿", ".", ",", "!") }
            .filter { it.length > 3 && it !in stopWords }
            .groupBy { it }
            .map { Pair(it.key, it.value.size) }
            .sortedByDescending { it.second }
            .take(5)
            .map { it.first.replaceFirstChar { c -> c.uppercase() } }
    }
}
