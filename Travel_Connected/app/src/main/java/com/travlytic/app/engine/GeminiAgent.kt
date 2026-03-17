package com.travlytic.app.engine

import android.util.Log
import com.google.ai.client.generativeai.GenerativeModel
import com.google.ai.client.generativeai.type.content
import com.google.ai.client.generativeai.type.generationConfig
import com.travlytic.app.data.db.dao.ResponseLogDao
import com.travlytic.app.data.db.dao.TrainingRuleDao
import com.travlytic.app.data.repository.KnowledgeRepository
import com.google.gson.Gson
import javax.inject.Inject
import javax.inject.Singleton

private const val TAG = "GeminiAgent"

/** ═══════════════════════════════════════════════════════════════════════════
 *  SISTEMA BASE DE MINI-TO — REGLAS DE RAÍZ BLOQUEADAS EN CÓDIGO
 * ═══════════════════════════════════════════════════════════════════════════ */
private fun buildSistemaBase(internetSearchEnabled: Boolean, isFirstInteraction: Boolean): String {
    val searchInstruction = if (internetSearchEnabled) {
        """
        USO DE CONOCIMIENTO GENERAL (ESTADO: ACTIVADO):
        - Por defecto, sigues siendo estricto con la base de conocimiento del Excel.
        - SIN EMBARGO, si detectas una instrucción específica que te autorice explícitamente a usar tu conocimiento externo para este caso, HAZLO.
        """.trimIndent()
    } else {
        """
        USO DE CONOCIMIENTO GENERAL (ESTADO: DESACTIVADO):
        - Eres 100% dependiente de la base de conocimiento del Excel proporcionada.
        - No uses bajo ninguna circunstancia tu conocimiento externo o de internet.
        - Si no está en el Excel, responde ESCALATE_REQUIRED.
        """.trimIndent()
    }

    val interactionRule = if (isFirstInteraction) {
        """
        PRESENTACIÓN (SOLO PRIMER MENSAJE):
        - Saluda cordialmente y menciónate como MINI-TO (tu nombre de agente).
        - Indica que eres el asistente de la empresa.
        """.trimIndent()
    } else {
        """
        RE-INTERACCIÓN (CHAT EN CURSO):
        - 🚫 PROHIBIDO: No vuelvas a decir "Hola soy MINI-TO" ni a presentarte formalmente.
        - Sé directo y amable. Continúa el flujo de la duda actual sin repetir tu identidad.
        """.trimIndent()
    }

    return """
    ⚙️ [SISTEMA BASE MINI-TO — RAÍZ INMUTABLE]
    
    Tono: Siempre amable, servicial y profesional (Atención al Cliente Premium).
    
    $interactionRule
    
    CUÁNDO ESCALAR (usar ESCALATE_REQUIRED):
    - Escala si después de buscar semánticamente NO hay relación con el Excel.
    - NUNCA escales por saludos, despedidas o agradecimientos.
    
    $searchInstruction
    
    REGLA DE REPETICIÓN (ANTI-ECO):
    - Si detectas que el usuario está repitiendo exactamente lo último que tú respondiste (es un eco), responde con extrema cortesía indicando que quizás hubo un error de red y repite la info brevemente preguntando si se recibió bien.
    
    FLUIDEZ: Estilo WhatsApp, respuestas cortas (2-4 oraciones). Emojis con moderación.
    [FIN SISTEMA BASE]
    """.trimIndent()
}

@Singleton
class GeminiAgent @Inject constructor(
    private val knowledgeRepository: KnowledgeRepository,
    private val trainingRuleDao: TrainingRuleDao,
    private val responseLogDao: ResponseLogDao
) {
    private val gson = Gson()

    suspend fun generateResponse(
        apiKey: String,
        systemPrompt: String,
        contactName: String,
        userMessage: String,
        userName: String = "",
        businessName: String = "",
        tone: String = "",
        audioData: ByteArray? = null,
        internetSearchEnabled: Boolean = false,
        isFirstInteraction: Boolean = true
    ): String? {
        if (apiKey.isBlank()) return null

        return try {
            val sheetContext = knowledgeRepository.getEnabledContextString()
            val activeRules = trainingRuleDao.getActiveRules()

            val fullPrompt = buildPrompt(
                userSystemPrompt = systemPrompt,
                sheetContext = sheetContext,
                activeRules = activeRules,
                contactName = contactName,
                userMessage = userMessage,
                userName = userName,
                businessName = businessName,
                tone = tone,
                hasAudio = audioData != null,
                internetSearchEnabled = internetSearchEnabled,
                isFirstInteraction = isFirstInteraction
            )

            val model = GenerativeModel(
                modelName = "gemini-2.5-flash",
                apiKey = apiKey,
                generationConfig = generationConfig {
                    temperature = 0.85f
                    maxOutputTokens = 800
                    topK = 40
                    topP = 0.95f
                }
            )

            val rawHistory = responseLogDao.getRecentForContact(contactName, 10).reversed()
            val chatHistory = rawHistory.flatMap { log ->
                listOf(
                    content("user") { text(log.incomingMessage) },
                    content("model") { text(log.sentResponse) }
                )
            }

            val chat = model.startChat(history = chatHistory)
            val response = chat.sendMessage(
                content {
                    if (audioData != null) blob("audio/ogg", audioData)
                    text(fullPrompt)
                }
            )

            val responseText = response.text?.trim()
            Log.d(TAG, "Respuesta generada [$contactName]: $responseText")
            responseText

        } catch (e: Exception) {
            Log.e(TAG, "Error Gemini", e)
            null
        }
    }

    private fun buildPrompt(
        userSystemPrompt: String,
        sheetContext: String,
        activeRules: List<com.travlytic.app.data.db.entities.TrainingRule>,
        contactName: String,
        userMessage: String,
        userName: String,
        businessName: String,
        tone: String,
        hasAudio: Boolean,
        internetSearchEnabled: Boolean,
        isFirstInteraction: Boolean
    ): String {
        val rules = activeRules.filter { it.type == "RULE" }
        val examples = activeRules.filter { it.type == "EXAMPLE" }

        val rulesText = if (rules.isNotEmpty()) {
            "\n=== REGLAS DEL USUARIO ===\n" + rules.joinToString("\n") { "- ${it.input}" }
        } else ""

        val examplesText = if (examples.isNotEmpty()) {
            "\n=== EJEMPLOS (FEW-SHOT) ===\n" +
            examples.joinToString("\n\n") { "Usuario: \"${it.input}\"\nRespuesta: \"${it.output}\"" }
        } else ""

        val knowledgeSection = if (sheetContext.isNotBlank()) {
            "=== BASE DE CONOCIMIENTO (EXCEL) ===\n$sheetContext"
        } else "=== BASE DE CONOCIMIENTO === (vacía)\n"

        return """
$knowledgeSection

=== MENSAJE DEL USUARIO ===
Contacto: $contactName
Mensaje: $userMessage
${if(hasAudio) "(Contenido de mensaje de voz adjunto)." else ""}

=== TU RESPUESTA (WhatsApp Style) ===
""".trimIndent()
    }
}
