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
        // Básicos
        val GEMINI_API_KEY        = stringPreferencesKey("gemini_api_key")
        val BOT_ENABLED           = booleanPreferencesKey("bot_enabled")
        val SYSTEM_PROMPT         = stringPreferencesKey("system_prompt")
        val GOOGLE_ACCOUNT_EMAIL  = stringPreferencesKey("google_account_email")
        val AUTO_REPLY_DELAY_MS   = longPreferencesKey("auto_reply_delay_ms")

        // ─── Canales ───────────────────────────────────────────────────
        val CHANNEL_WHATSAPP      = booleanPreferencesKey("channel_whatsapp")
        val CHANNEL_FB_MESSENGER  = booleanPreferencesKey("channel_fb_messenger")
        val CHANNEL_IG_DIRECT     = booleanPreferencesKey("channel_ig_direct")

        // ─── Profile ───────────────────────────────────────────────────
        val PROFILE_USER_NAME     = stringPreferencesKey("profile_user_name")
        val PROFILE_BUSINESS_NAME = stringPreferencesKey("profile_business_name")
        val PROFILE_TONE          = stringPreferencesKey("profile_tone")

        // ─── Scheduler ────────────────────────────────────────────────
        val SCHEDULE_ENABLED  = booleanPreferencesKey("schedule_enabled")
        val SCHEDULE_START_H  = intPreferencesKey("schedule_start_hour")
        val SCHEDULE_START_M  = intPreferencesKey("schedule_start_minute")
        val SCHEDULE_END_H    = intPreferencesKey("schedule_end_hour")
        val SCHEDULE_END_M    = intPreferencesKey("schedule_end_minute")
        /** Días activos: Set de ints 1=Lun, 2=Mar, 3=Mié, 4=Jue, 5=Vie, 6=Sáb, 7=Dom */
        val SCHEDULE_DAYS     = stringPreferencesKey("schedule_days")

        const val DEFAULT_SYSTEM_PROMPT = """Eres Travlytic, un asistente de respuesta automática para WhatsApp.
Tu misión es responder mensajes de forma natural, precisa y concisa basándote EXCLUSIVAMENTE en la información proporcionada en tu base de conocimiento.

REGLAS:
1. Responde SIEMPRE en el mismo idioma del mensaje recibido.
2. Sé breve y directo. Máximo 3-4 oraciones por respuesta.
3. Si la información no está en la base de conocimiento, responde: "No tengo información sobre eso en este momento."
4. No inventes información. Usa solo lo que está en el contexto.
5. Sé amable y profesional."""

        /** Días activos por defecto: Lun–Vie */
        const val DEFAULT_DAYS = "1,2,3,4,5"
    }

    // ─── Gemini API Key ───────────────────────────────────────────────
    val geminiApiKey: Flow<String> = context.dataStore.data.map { it[GEMINI_API_KEY] ?: "" }
    suspend fun setGeminiApiKey(key: String) = context.dataStore.edit { it[GEMINI_API_KEY] = key }

    // ─── Bot toggle ───────────────────────────────────────────────────
    val botEnabled: Flow<Boolean> = context.dataStore.data.map { it[BOT_ENABLED] ?: false }
    suspend fun setBotEnabled(enabled: Boolean) = context.dataStore.edit { it[BOT_ENABLED] = enabled }

    // ─── System Prompt ────────────────────────────────────────────────
    val systemPrompt: Flow<String> = context.dataStore.data.map { it[SYSTEM_PROMPT] ?: DEFAULT_SYSTEM_PROMPT }
    suspend fun setSystemPrompt(prompt: String) = context.dataStore.edit { it[SYSTEM_PROMPT] = prompt }

    // ─── Canales ──────────────────────────────────────────────────────
    val channelWhatsApp: Flow<Boolean> = context.dataStore.data.map { it[CHANNEL_WHATSAPP] ?: true }
    suspend fun setChannelWhatsApp(enabled: Boolean) = context.dataStore.edit { it[CHANNEL_WHATSAPP] = enabled }

    val channelFbMessenger: Flow<Boolean> = context.dataStore.data.map { it[CHANNEL_FB_MESSENGER] ?: false }
    suspend fun setChannelFbMessenger(enabled: Boolean) = context.dataStore.edit { it[CHANNEL_FB_MESSENGER] = enabled }

    val channelIgDirect: Flow<Boolean> = context.dataStore.data.map { it[CHANNEL_IG_DIRECT] ?: false }
    suspend fun setChannelIgDirect(enabled: Boolean) = context.dataStore.edit { it[CHANNEL_IG_DIRECT] = enabled }

    // ─── Profile ──────────────────────────────────────────────────────
    val profileUserName: Flow<String> = context.dataStore.data.map { it[PROFILE_USER_NAME] ?: "" }
    suspend fun setProfileUserName(name: String) = context.dataStore.edit { it[PROFILE_USER_NAME] = name }

    val profileBusinessName: Flow<String> = context.dataStore.data.map { it[PROFILE_BUSINESS_NAME] ?: "" }
    suspend fun setProfileBusinessName(name: String) = context.dataStore.edit { it[PROFILE_BUSINESS_NAME] = name }

    val profileTone: Flow<String> = context.dataStore.data.map { it[PROFILE_TONE] ?: "Profesional y amable" }
    suspend fun setProfileTone(tone: String) = context.dataStore.edit { it[PROFILE_TONE] = tone }

    // ─── Google Account ───────────────────────────────────────────────
    val googleAccountEmail: Flow<String> = context.dataStore.data.map { it[GOOGLE_ACCOUNT_EMAIL] ?: "" }
    suspend fun setGoogleAccountEmail(email: String) = context.dataStore.edit { it[GOOGLE_ACCOUNT_EMAIL] = email }

    // ─── Reply delay ──────────────────────────────────────────────────
    val autoReplyDelayMs: Flow<Long> = context.dataStore.data.map { it[AUTO_REPLY_DELAY_MS] ?: 1500L }
    suspend fun setAutoReplyDelayMs(ms: Long) = context.dataStore.edit { it[AUTO_REPLY_DELAY_MS] = ms }

    // ─── Scheduler ───────────────────────────────────────────────────

    val scheduleEnabled: Flow<Boolean> = context.dataStore.data.map { it[SCHEDULE_ENABLED] ?: false }
    suspend fun setScheduleEnabled(v: Boolean) = context.dataStore.edit { it[SCHEDULE_ENABLED] = v }

    val scheduleStartHour: Flow<Int>   = context.dataStore.data.map { it[SCHEDULE_START_H] ?: 8 }
    val scheduleStartMinute: Flow<Int> = context.dataStore.data.map { it[SCHEDULE_START_M] ?: 0 }
    val scheduleEndHour: Flow<Int>     = context.dataStore.data.map { it[SCHEDULE_END_H] ?: 20 }
    val scheduleEndMinute: Flow<Int>   = context.dataStore.data.map { it[SCHEDULE_END_M] ?: 0 }

    suspend fun setScheduleStart(hour: Int, minute: Int) = context.dataStore.edit {
        it[SCHEDULE_START_H] = hour; it[SCHEDULE_START_M] = minute
    }
    suspend fun setScheduleEnd(hour: Int, minute: Int) = context.dataStore.edit {
        it[SCHEDULE_END_H] = hour; it[SCHEDULE_END_M] = minute
    }

    /** Días activos: string separado por comas ej. "1,2,3,4,5" */
    val scheduleDays: Flow<Set<Int>> = context.dataStore.data.map { prefs ->
        (prefs[SCHEDULE_DAYS] ?: DEFAULT_DAYS)
            .split(",")
            .mapNotNull { it.trim().toIntOrNull() }
            .toSet()
    }
    suspend fun setScheduleDays(days: Set<Int>) = context.dataStore.edit {
        it[SCHEDULE_DAYS] = days.joinToString(",")
    }
}
