package com.travlytic.app.engine

import android.util.Log
import com.google.ai.client.generativeai.GenerativeModel
import com.google.ai.client.generativeai.type.content
import com.google.ai.client.generativeai.type.generationConfig
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
        periodLabel: String = "hoy"  // "hoy", "esta semana", "últimas 24h"
    ): SessionSummary? {
        if (logs.isEmpty()) return null
        if (apiKey.isBlank()) return null

        return try {
            // ─── Estadísticas base ───────────────────────────────────────
            val uniqueContacts = logs.map { it.contact }.distinct()
            val contactCount = logs.groupBy { it.contact }
                .map { Pair(it.key, it.value.size) }
                .sortedByDescending { it.second }
                .take(5)

            // ─── Prompt para Gemini ──────────────────────────────────────
            val logsText = logs.take(30).joinToString("\n") { log ->
                "- [${log.contact}] Pregunta: \"${log.incomingMessage}\" → Respuesta: \"${log.sentResponse.take(80)}\""
            }

            val prompt = """
Eres el asistente de análisis de Travlytic. Tu tarea es generar un RESUMEN EJECUTIVO breve, amigable y en español de la actividad del bot de WhatsApp de $periodLabel.

DATOS DE ACTIVIDAD:
- Total de mensajes respondidos: ${logs.size}
- Contactos únicos atendidos: ${uniqueContacts.size}
- Contacto más activo: ${contactCount.firstOrNull()?.first ?: "N/A"} (${contactCount.firstOrNull()?.second ?: 0} mensajes)

MUESTRA DE CONVERSACIONES:
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
                modelName = "gemini-2.0-flash",
                apiKey = apiKey,
                generationConfig = generationConfig {
                    temperature = 0.8f
                    maxOutputTokens = 350
                }
            )

            val response = model.generateContent(content { text(prompt) })
            val narrativeText = response.text?.trim() ?: generateFallbackNarrative(logs, periodLabel)

            // Extraer tópicos (heurística simple: palabras más frecuentes en preguntas)
            val topTopics = extractTopTopics(logs)

            Log.d(TAG, "Resumen generado: ${narrativeText.take(100)}...")

            SessionSummary(
                narrativeText = narrativeText,
                totalReplies = logs.size,
                uniqueContacts = uniqueContacts.size,
                topTopics = topTopics,
                topContacts = contactCount
            )
        } catch (e: Exception) {
            Log.e(TAG, "Error generando resumen", e)
            // Fallback sin Gemini
            SessionSummary(
                narrativeText = generateFallbackNarrative(logs, periodLabel),
                totalReplies = logs.size,
                uniqueContacts = logs.map { it.contact }.distinct().size,
                topTopics = extractTopTopics(logs),
                topContacts = logs.groupBy { it.contact }
                    .map { Pair(it.key, it.value.size) }
                    .sortedByDescending { it.second }.take(5)
            )
        }
    }

    /** Resumen básico sin llamar a Gemini (fallback) */
    private fun generateFallbackNarrative(logs: List<ResponseLog>, period: String): String {
        val contacts = logs.map { it.contact }.distinct()
        val topContact = logs.groupBy { it.contact }
            .maxByOrNull { it.value.size }?.key ?: ""
        return "¡Hola! Tu resumen de $period: Travlytic respondió ${logs.size} mensajes " +
               "de ${contacts.size} contacto${if (contacts.size == 1) "" else "s"} diferentes. " +
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
