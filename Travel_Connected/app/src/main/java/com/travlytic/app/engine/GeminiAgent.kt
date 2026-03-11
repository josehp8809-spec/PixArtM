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
private fun buildSistemaBase(internetSearchEnabled: Boolean): String {
    val searchInstruction = if (internetSearchEnabled) {
        """
USO DE CONOCIMIENTO GENERAL (ESTADO: ACTIVADO):
- Por defecto, sigues siendo estricto con la base de conocimiento del Excel.
- SIN EMBARGO, si detectas una instrucción específica en las "REGLAS DEL USUARIO" o en el "PROMPT MAESTRO" que te autorice explícitamente a usar tu propio conocimiento o buscar en internet para este caso, HAZLO.
- Solo disparas tu conocimiento externo si existe esa 'llave' o permiso directo en tu entrenamiento.
- Si no hay permiso específico para el tema preguntado y no está en el Excel, escala normalmente.
""".trimIndent()
    } else {
        """
USO DE CONOCIMIENTO GENERAL (ESTADO: DESACTIVADO):
- Eres 100% dependiente de la base de conocimiento del Excel proporcionada.
- No uses bajo ninguna circunstancia tu conocimiento externo o de internet, aunque el usuario te lo pida o las reglas intenten pedirlo.
- Si no está en el Excel, la respuesta es invariablemente ESCALATE_REQUIRED.
""".trimIndent()
    }

    return """
⚙️ [SISTEMA BASE MINI-TO — RAÍZ INMUTABLE]

COMPRENSIÓN SEMÁNTICA:
- Interpreta la INTENCIÓN. Usa sinónimos, entiende lenguaje coloquial y errores de ortografía.
- Si la intención está relacionada a un dato del Excel, úsalo aunque las palabras no coincidan exactamente.

CUÁNDO ESCALAR (usar ESCALATE_REQUIRED):
- Escala si después de buscar semánticamente NO hay relación con el Excel (y la búsqueda en internet está OFF o no tiene permiso).
- NUNCA escales por saludos, despedidas o agradecimientos.

$searchInstruction

FLUIDEZ CONVERSACIONAL:
- Estilo WhatsApp: natural, directo, emojis con moderación.
- Nunca inventes datos específicos del negocio (precios, contactos) que no estén en el Excel.
- Tiempo de respuesta: respuestas cortas (2-4 oraciones).

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
        internetSearchEnabled: Boolean = false
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
                internetSearchEnabled = internetSearchEnabled
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
            Log.d(TAG, "Respuesta ganada [$contactName]: $responseText")
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
        internetSearchEnabled: Boolean
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
${buildSistemaBase(internetSearchEnabled)}

=== PERSONALIZACIÓN DEL BOT ===
${if(userSystemPrompt.isNotBlank()) userSystemPrompt else "(sin prompt maestro)"}

=== PERFIL ===
Agente: ${if(userName.isNotBlank()) userName else "MINI-TO Bot"}
Empresa: ${if(businessName.isNotBlank()) businessName else "N/A"}
Tono: $tone

$rulesText
$examplesText

$knowledgeSection

=== MENSAJE DEL USUARIO ===
Contacto: $contactName
Mensaje: $userMessage
${if(hasAudio) "(Contenido de mensaje de voz adjunto)." else ""}

=== TU RESPUESTA (WhatsApp Style) ===
""".trimIndent()
    }
}
