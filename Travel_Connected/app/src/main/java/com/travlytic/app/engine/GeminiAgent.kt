package com.travlytic.app.engine

import android.util.Log
import com.google.ai.client.generativeai.GenerativeModel
import com.google.ai.client.generativeai.type.content
import com.google.ai.client.generativeai.type.generationConfig
import com.travlytic.app.data.db.dao.SheetDataDao
import com.travlytic.app.data.db.dao.TrainingRuleDao
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import javax.inject.Inject
import javax.inject.Singleton

private const val TAG = "GeminiAgent"

@Singleton
class GeminiAgent @Inject constructor(
    private val sheetDataDao: SheetDataDao,
    private val registeredSheetDao: RegisteredSheetDao,
    private val trainingRuleDao: TrainingRuleDao
) {
    private val gson = Gson()

    /**
     * Genera una respuesta automática para un mensaje de WhatsApp
     * usando el contenido de los Google Sheets como contexto.
     *
     * @param apiKey Gemini API Key del usuario
     * @param apiKey Gemini API Key del usuario
     * @param systemPrompt Prompt del sistema configurado
     * @param contactName Nombre del contacto que envió el mensaje
     * @param userMessage Mensaje recibido
     * @param userName Nombre del responsable o bot
     * @param businessName Nombre del negocio
     * @param tone Tono de respuesta
     * @return Respuesta generada por Gemini o null si hay error
     */
    suspend fun generateResponse(
        apiKey: String,
        systemPrompt: String,
        contactName: String,
        userMessage: String,
        userName: String = "",
        businessName: String = "",
        tone: String = ""
    ): String? {
        if (apiKey.isBlank()) {
            Log.w(TAG, "Gemini API Key no configurada")
            return null
        }

        return try {
            // 1. Cargar el contexto de todos los Sheets sincronizados
            val sheetContext = buildSheetContext()

            if (sheetContext.isBlank()) {
                Log.w(TAG, "No hay datos de Sheets sincronizados")
                return "No tengo información disponible en este momento. Por favor sincroniza tu base de conocimiento."
            }

            // 2. Cargar Reglas y Ejemplos Activos
            // 2. Cargar Reglas y Ejemplos Activos
            val activeRules = trainingRuleDao.getActiveRules()
            
            // 3. Construir el prompt completo
            val fullPrompt = buildPrompt(
                systemPrompt, sheetContext, activeRules, contactName, userMessage,
                userName, businessName, tone
            )

            // 4. Configurar y llamar a Gemini
            val model = GenerativeModel(
                modelName = "gemini-2.5-flash",
                apiKey = apiKey,
                generationConfig = generationConfig {
                    temperature = 0.7f
                    maxOutputTokens = 500
                    topK = 40
                    topP = 0.95f
                }
            )

            val response = model.generateContent(
                content {
                    text(fullPrompt)
                }
            )

            val responseText = response.text?.trim()
            Log.d(TAG, "Respuesta generada para '$contactName': $responseText")
            responseText

        } catch (e: Exception) {
            Log.e(TAG, "Error generando respuesta Gemini", e)
            null
        }
    }

    /**
     * Construye el contexto de todos los Sheets habilitados
     * combinando su contenido en un string legible para Gemini.
     */
    private suspend fun buildSheetContext(): String {
        val sheets = registeredSheetDao.getAll().filter { it.isEnabled }
        if (sheets.isEmpty()) return ""

        val sb = StringBuilder()

        for (sheet in sheets) {
            val rows = sheetDataDao.getBySpreadsheet(sheet.spreadsheetId)
            if (rows.isEmpty()) continue

            sb.appendLine("=== ${sheet.title} ===")

            for (row in rows) {
                try {
                    val mapType = object : TypeToken<Map<String, String>>() {}.type
                    val rowMap: Map<String, String> = gson.fromJson(row.content, mapType)
                    val rowText = rowMap.entries.joinToString(" | ") { (k, v) -> "$k: $v" }
                    sb.appendLine(rowText)
                } catch (e: Exception) {
                    sb.appendLine(row.content)
                }
            }
            sb.appendLine()
        }

        return sb.toString()
    }

    /**
     * Construye el prompt final que se enviará a Gemini integrando las reglas y ejemplos.
     */
    private fun buildPrompt(
        systemPrompt: String,
        sheetContext: String,
        activeRules: List<com.travlytic.app.data.db.entities.TrainingRule>,
        contactName: String,
        userMessage: String,
        userName: String,
        businessName: String,
        tone: String
    ): String {
        val rules = activeRules.filter { it.type == "RULE" }
        val examples = activeRules.filter { it.type == "EXAMPLE" }
        
        val rulesText = if (rules.isNotEmpty()) {
            "\n=== REGLAS ESTRICTAS DE COMPORTAMIENTO ===\n" +
            rules.joinToString("\n") { "- ${it.input}" }
        } else ""

        val examplesText = if (examples.isNotEmpty()) {
            "\n=== EJEMPLOS DE RESPUESTAS (ESTILO FEW-SHOT) ===\n" +
            examples.joinToString("\n\n") { "Si el usuario dice: \"${it.input}\"\nDebes responder exactamente así: \"${it.output}\"" }
        } else ""

        return """
$systemPrompt

=== PERFIL DE IDENTIDAD ===
Tu Nombre / Agente: ${if(userName.isNotBlank()) userName else "Travlytic Bot"}
Empresa / Negocio: ${if(businessName.isNotBlank()) businessName else "N/A"}
Tono de respuesta indicado: ${if(tone.isNotBlank()) tone else "Profesional y amable"}

$rulesText
$examplesText

=== BASE DE CONOCIMIENTO (OBLIGATORIO) ===
$sheetContext

=== MENSAJE ACTUAL RECIÉN RECIBIDO ===
Contacto: $contactName
Mensaje: $userMessage

=== TU RESPUESTA (Directa y Natural) ===
""".trimIndent()
    }
}
