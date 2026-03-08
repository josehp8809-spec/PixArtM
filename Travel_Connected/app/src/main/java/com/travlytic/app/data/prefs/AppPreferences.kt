package com.travlytic.app.data.prefs

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "travlytic_prefs")

class AppPreferences(private val context: Context) {

    companion object {
        val GEMINI_API_KEY = stringPreferencesKey("gemini_api_key")
        val BOT_ENABLED = booleanPreferencesKey("bot_enabled")
        val SYSTEM_PROMPT = stringPreferencesKey("system_prompt")
        val GOOGLE_ACCOUNT_EMAIL = stringPreferencesKey("google_account_email")
        val AUTO_REPLY_DELAY_MS = longPreferencesKey("auto_reply_delay_ms")

        const val DEFAULT_SYSTEM_PROMPT = """Eres Travlytic, un asistente de respuesta automática para WhatsApp.
Tu misión es responder mensajes de forma natural, precisa y concisa basándote EXCLUSIVAMENTE en la información proporcionada en tu base de conocimiento.

REGLAS:
1. Responde SIEMPRE en el mismo idioma del mensaje recibido.
2. Sé breve y directo. Máximo 3-4 oraciones por respuesta.
3. Si la información no está en la base de conocimiento, responde: "No tengo información sobre eso en este momento."
4. No inventes información. Usa solo lo que está en el contexto.
5. Sé amable y profesional."""
    }

    // Gemini API Key
    val geminiApiKey: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[GEMINI_API_KEY] ?: ""
    }

    suspend fun setGeminiApiKey(key: String) {
        context.dataStore.edit { prefs ->
            prefs[GEMINI_API_KEY] = key
        }
    }

    // Bot habilitado/deshabilitado
    val botEnabled: Flow<Boolean> = context.dataStore.data.map { prefs ->
        prefs[BOT_ENABLED] ?: false
    }

    suspend fun setBotEnabled(enabled: Boolean) {
        context.dataStore.edit { prefs ->
            prefs[BOT_ENABLED] = enabled
        }
    }

    // System Prompt de Gemini
    val systemPrompt: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[SYSTEM_PROMPT] ?: DEFAULT_SYSTEM_PROMPT
    }

    suspend fun setSystemPrompt(prompt: String) {
        context.dataStore.edit { prefs ->
            prefs[SYSTEM_PROMPT] = prompt
        }
    }

    // Email de la cuenta Google conectada
    val googleAccountEmail: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[GOOGLE_ACCOUNT_EMAIL] ?: ""
    }

    suspend fun setGoogleAccountEmail(email: String) {
        context.dataStore.edit { prefs ->
            prefs[GOOGLE_ACCOUNT_EMAIL] = email
        }
    }

    // Delay de respuesta automática en ms (para simular que "alguien escribe")
    val autoReplyDelayMs: Flow<Long> = context.dataStore.data.map { prefs ->
        prefs[AUTO_REPLY_DELAY_MS] ?: 1500L
    }

    suspend fun setAutoReplyDelayMs(delayMs: Long) {
        context.dataStore.edit { prefs ->
            prefs[AUTO_REPLY_DELAY_MS] = delayMs
        }
    }
}
