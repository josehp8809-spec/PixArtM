package com.travlytic.app.ui.viewmodel

import android.content.Context
import android.content.Intent
import android.provider.Settings
import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.travlytic.app.data.db.dao.EscalationLogDao
import com.travlytic.app.data.db.dao.ResponseLogDao
import com.travlytic.app.data.db.entities.ResponseLog
import com.travlytic.app.data.db.entities.EscalationLog
import com.travlytic.app.data.db.entities.KnowledgeItem
import com.travlytic.app.data.prefs.AppPreferences
import com.travlytic.app.data.db.dao.TrainingRuleDao
import com.travlytic.app.data.db.entities.TrainingRule
import com.travlytic.app.engine.AiConfigExport
import com.google.gson.Gson
import com.travlytic.app.data.repository.KnowledgeRepository
import com.travlytic.app.engine.GeminiAgent
import com.travlytic.app.engine.SessionSummary
import com.travlytic.app.engine.SummaryGenerator
import com.travlytic.app.engine.TtsManager
import com.travlytic.app.data.model.TimeRange
import com.travlytic.app.engine.TtsState
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

private const val TAG = "MainViewModel"

data class UiState(
    val isServiceEnabled: Boolean = false, // Estado manual
    val isEffectivelyEnabled: Boolean = false, // Estado real (Manual o Horario)
    val activationReason: String = "", // "manual", "horario" o ""
    val recentLogs: List<ResponseLog> = emptyList(),
    val recentEscalations: List<EscalationLog> = emptyList(),
    val knowledgeItems: List<KnowledgeItem> = emptyList(),
    val isLoading: Boolean = false,
    val snackbarMessage: String? = null
)

data class ScheduleState(
    val enabled: Boolean = false,
    val timeRanges: List<TimeRange> = emptyList(),
    val activeDays: Set<Int> = setOf(1, 2, 3, 4, 5)
)

data class DashboardState(
    val repliesToday: Int = 0,
    val repliesThisWeek: Int = 0,
    val totalKnowledgeRows: Int = 0,
    val activeSheetsCount: Int = 0
)

data class TestMessageState(
    val isLoading: Boolean = false,
    val response: String = "",
    val error: String = ""
)

data class SummaryUiState(
    val isLoading: Boolean = false,
    val summary: SessionSummary? = null,
    val error: String = "",
    val selectedPeriod: String = "Hoy",  // "Hoy", "Semana", "Todo"
    val speechRate: Float = 1.0f
)

@HiltViewModel
class MainViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val appPreferences: AppPreferences,
    private val knowledgeRepository: KnowledgeRepository,
    private val escalationLogDao: EscalationLogDao,
    private val responseLogDao: ResponseLogDao,
    private val trainingRuleDao: TrainingRuleDao,
    private val geminiAgent: GeminiAgent,
    private val summaryGenerator: SummaryGenerator,
    private val ttsManager: TtsManager
) : ViewModel() {

    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    // ─── Summary state ───────────────────────────────────────────────
    private val _summaryUiState = MutableStateFlow(SummaryUiState())
    val summaryUiState: StateFlow<SummaryUiState> = _summaryUiState.asStateFlow()

    val ttsState: StateFlow<TtsState> = ttsManager.ttsState

    val geminiApiKey: StateFlow<String> = appPreferences.geminiApiKey
        .stateIn(viewModelScope, SharingStarted.Lazily, "")

    val systemPrompt: StateFlow<String> = appPreferences.systemPrompt
        .stateIn(viewModelScope, SharingStarted.Lazily, AppPreferences.DEFAULT_SYSTEM_PROMPT)
        
    val welcomeMessage: StateFlow<String> = appPreferences.welcomeMessage
        .stateIn(viewModelScope, SharingStarted.Lazily, "")
        
    val escalationMessage: StateFlow<String> = appPreferences.escalationMessage
        .stateIn(viewModelScope, SharingStarted.Lazily, "")

    val autoReminderEnabled: StateFlow<Boolean> = appPreferences.autoReminderEnabled
        .stateIn(viewModelScope, SharingStarted.Lazily, false)

    val autoReminderMessage: StateFlow<String> = appPreferences.autoReminderMessage
        .stateIn(viewModelScope, SharingStarted.Lazily, "¿Puedo ayudarte en algo más?")

    val botEnabled: StateFlow<Boolean> = appPreferences.botEnabled
        .stateIn(viewModelScope, SharingStarted.Lazily, false)

    val internetSearchEnabled: StateFlow<Boolean> = appPreferences.internetSearchEnabled
        .stateIn(viewModelScope, SharingStarted.Lazily, false)

    // Profile state
    val profileUserName: StateFlow<String> = appPreferences.profileUserName
        .stateIn(viewModelScope, SharingStarted.Lazily, "")
    val profileBusinessName: StateFlow<String> = appPreferences.profileBusinessName
        .stateIn(viewModelScope, SharingStarted.Lazily, "")
    val profileTone: StateFlow<String> = appPreferences.profileTone
        .stateIn(viewModelScope, SharingStarted.Lazily, "Profesional y amable")

    // Canales
    val channelWhatsApp: StateFlow<Boolean> = appPreferences.channelWhatsApp
        .stateIn(viewModelScope, SharingStarted.Lazily, true)
    val channelFbMessenger: StateFlow<Boolean> = appPreferences.channelFbMessenger
        .stateIn(viewModelScope, SharingStarted.Lazily, false)
    val channelIgDirect: StateFlow<Boolean> = appPreferences.channelIgDirect
        .stateIn(viewModelScope, SharingStarted.Lazily, false)

    // ─── Schedule State ───────────────────────────────────────────────
    val scheduleState: StateFlow<ScheduleState> = combine(
        appPreferences.scheduleEnabled,
        appPreferences.scheduleList,
        appPreferences.scheduleDays
    ) { enabled, list, days ->
        ScheduleState(
            enabled     = enabled,
            timeRanges  = list,
            activeDays  = days
        )
    }.stateIn(viewModelScope, SharingStarted.Lazily, ScheduleState())

    // ─── Dashboard State ────────────────────────────────────────────
    private val _dashboardState = MutableStateFlow(DashboardState())
    val dashboardState: StateFlow<DashboardState> = _dashboardState.asStateFlow()

    // ─── Test Message State ──────────────────────────────────────────
    private val _testMsgState = MutableStateFlow(TestMessageState())
    val testMsgState: StateFlow<TestMessageState> = _testMsgState.asStateFlow()

    init {
        observeRecentLogs()
        observeEscalationLogs()
        observeKnowledgeItems()
        observeServiceStatus()
        observeDashboard()
    }

    private fun observeEscalationLogs() {
        escalationLogDao.getPendingFlow()
            .onEach { logs -> _uiState.update { it.copy(recentEscalations = logs) } }
            .launchIn(viewModelScope)
    }

    private fun observeKnowledgeItems() {
        knowledgeRepository.knowledgeItemsFlow
            .onEach { items -> _uiState.update { it.copy(knowledgeItems = items) } }
            .launchIn(viewModelScope)
    }

    private fun observeRecentLogs() {
        responseLogDao.observeRecent(50)
            .onEach { logs -> _uiState.update { it.copy(recentLogs = logs) } }
            .launchIn(viewModelScope)
    }

    private fun observeServiceStatus() {
        val ticker = flow {
            while (true) {
                emit(Unit)
                kotlinx.coroutines.delay(30_000) // Check cada 30 seg
            }
        }

        combine(
            appPreferences.botEnabled,
            scheduleState,
            ticker
        ) { manual, schedule, _ ->
            val isTimed = isInsideSchedule(schedule)
            val effective = manual || isTimed
            val reason = when {
                manual -> "manual"
                isTimed -> "horario"
                else -> ""
            }
            Triple(effective, reason, manual)
        }.onEach { (effective, reason, manual) ->
            _uiState.update { it.copy(
                isServiceEnabled = manual,
                isEffectivelyEnabled = effective,
                activationReason = reason
            ) }
        }.launchIn(viewModelScope)
    }

    private fun isInsideSchedule(state: ScheduleState): Boolean {
        if (!state.enabled || state.timeRanges.isEmpty()) return false
        val now = java.util.Calendar.getInstance()
        val currentMins = now.get(java.util.Calendar.HOUR_OF_DAY) * 60 + now.get(java.util.Calendar.MINUTE)
        val dayNum = if (now.get(java.util.Calendar.DAY_OF_WEEK) == java.util.Calendar.SUNDAY) 7 else now.get(java.util.Calendar.DAY_OF_WEEK) - 1
        
        if (dayNum !in state.activeDays) return false
        
        return state.timeRanges.any { range ->
            val startMins = range.startHour * 60 + range.startMinute
            val endMins = range.endHour * 60 + range.endMinute
            
            if (endMins > startMins) {
                currentMins in startMins..endMins
            } else {
                currentMins >= startMins || currentMins <= endMins
            }
        }
    }

    private fun observeDashboard() {
        viewModelScope.launch {
            combine(
                responseLogDao.observeRecent(500),
                knowledgeRepository.knowledgeItemsFlow
            ) { logs, knowledgeItems ->
                val now = System.currentTimeMillis()
                val todayStart = java.util.Calendar.getInstance().apply {
                    set(java.util.Calendar.HOUR_OF_DAY, 0)
                    set(java.util.Calendar.MINUTE, 0)
                    set(java.util.Calendar.SECOND, 0)
                }.timeInMillis
                val weekStart = todayStart - (6 * 24 * 60 * 60 * 1000L)

                val repliesToday = logs.count { it.timestamp >= todayStart }
                val repliesWeek  = logs.count { it.timestamp >= weekStart }
                val enabledItems = knowledgeItems.filter { it.isEnabled }

                DashboardState(
                    repliesToday = repliesToday,
                    repliesThisWeek = repliesWeek,
                    totalKnowledgeRows = enabledItems.size, // count items/urls instead of actual rows for simplicity
                    activeSheetsCount = enabledItems.size
                )
            }.collect { dashboard ->
                _dashboardState.value = dashboard
            }
        }
    }

    // ─── Test Message ──────────────────────────────────────────────────────────

    fun testMessage(message: String) {
        if (message.isBlank()) return
        viewModelScope.launch {
            val apiKey = appPreferences.geminiApiKey.first()
            if (apiKey.isBlank()) {
                _testMsgState.value = TestMessageState(error = "❌ Configura tu Gemini API Key primero")
                return@launch
            }

            _testMsgState.value = TestMessageState(isLoading = true)

            try {
                val prompt = appPreferences.systemPrompt.first()
                val usrName = appPreferences.profileUserName.first()
                val busName = appPreferences.profileBusinessName.first()
                val tne = appPreferences.profileTone.first()

                val response = geminiAgent.generateResponse(
                    apiKey = apiKey,
                    systemPrompt = prompt,
                    contactName = "Test",
                    userMessage = message,
                    userName = usrName,
                    businessName = busName,
                    tone = tne
                )

                _testMsgState.value = TestMessageState(
                    response = response ?: "Sin respuesta. Verifica tu Base de Conocimiento.",
                    error = ""
                )
            } catch (e: Exception) {
                _testMsgState.value = TestMessageState(error = "❌ ${e.message}")
            }
        }
    }

    fun clearTestMessage() {
        _testMsgState.value = TestMessageState()
    }

    fun resolveEscalation(log: EscalationLog) {
        viewModelScope.launch {
            escalationLogDao.update(log.copy(isResolved = true))
            showSnackbar("Escalado resuelto")
        }
    }


    fun importExcelKnowledge(uri: android.net.Uri, reference: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                knowledgeRepository.importExcel(uri, reference)
                showSnackbar("✅ Documento importado")
            } catch (e: Exception) {
                e.printStackTrace()
                showSnackbar("❌ Err Doc: ${e.javaClass.simpleName} - ${e.localizedMessage?.take(40)}")
            }
            _uiState.update { it.copy(isLoading = false) }
        }
    }

    fun toggleKnowledgeItem(item: KnowledgeItem, enabled: Boolean) {
        viewModelScope.launch {
            knowledgeRepository.toggleItem(item, enabled)
        }
    }

    fun deleteKnowledgeItem(item: KnowledgeItem) {
        viewModelScope.launch {
            knowledgeRepository.deleteItem(item)
            showSnackbar("Documento eliminado")
        }
    }


    fun forceSync() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            // Simular un tiempo breve de sincronización para dar confirmación visual
            kotlinx.coroutines.delay(800)
            
            // Ree-observar base de datos para asegurar el último estado (aunque sea reactiva)
            observeKnowledgeItems()
            observeDashboard()
            
            _uiState.value = _uiState.value.copy(isLoading = false, snackbarMessage = "Toda la configuración y base de conocimiento sincronizadas correctamente")
        }
    }

    fun saveWelcomeMessage(message: String) {
        viewModelScope.launch {
            appPreferences.setWelcomeMessage(message)
            showSnackbar("✅ Mensaje de bienvenida guardado")
        }
    }

    fun saveEscalationMessage(message: String) {
        viewModelScope.launch {
            appPreferences.setEscalationMessage(message)
            showSnackbar("✅ Mensaje de escalado guardado")
        }
    }

    fun saveAutoReminderEnabled(enabled: Boolean) {
        viewModelScope.launch {
            appPreferences.setAutoReminderEnabled(enabled)
            showSnackbar(if (enabled) "Recordatorio automático activado" else "Recordatorio automático desactivado")
        }
    }

    fun saveAutoReminderMessage(message: String) {
        viewModelScope.launch {
            appPreferences.setAutoReminderMessage(message)
            showSnackbar("Mensaje de recordatorio guardado")
        }
    }

    fun saveInternetSearchEnabled(enabled: Boolean) {
        viewModelScope.launch {
            appPreferences.setInternetSearchEnabled(enabled)
            showSnackbar(if (enabled) "Búsqueda de IA activada" else "Búsqueda de IA desactivada")
        }
    }

    fun resetToDefaultSettings() {
        viewModelScope.launch {
            appPreferences.setSystemPrompt(AppPreferences.DEFAULT_SYSTEM_PROMPT)
            appPreferences.setWelcomeMessage("")
            appPreferences.setEscalationMessage("En este momento no tengo esa información, pero en breve un colega se pondrá en contacto contigo.")
            appPreferences.setAutoReminderEnabled(false)
            appPreferences.setAutoReminderMessage("¿Puedo ayudarte en algo más?")
            appPreferences.setProfileUserName("")
            appPreferences.setProfileBusinessName("")
            appPreferences.setProfileTone("Profesional y amable")
            appPreferences.setAutoReplyDelayMs(1500L)
            showSnackbar("Ajustes restablecidos a los valores originales")
        }
    }

    fun clearLogs() {
        viewModelScope.launch {
            responseLogDao.deleteAll()
            showSnackbar("Historial borrado")
        }
    }

    // ─── Bot Toggle ───────────────────────────────────────────────────

    fun toggleBot(enabled: Boolean) {
        viewModelScope.launch {
            val apiKey = appPreferences.geminiApiKey.first()
            if (enabled && apiKey.isBlank()) {
                showSnackbar("❌ Configura tu Gemini API Key antes de activar el bot")
                return@launch
            }
            appPreferences.setBotEnabled(enabled)
        }
    }

    fun openNotificationSettings(context: Context) {
        val intent = Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
        context.startActivity(intent)
    }

    // ─── Settings ─────────────────────────────────────────────────────

    fun saveGeminiApiKey(key: String) {
        viewModelScope.launch {
            appPreferences.setGeminiApiKey(key.trim())
            showSnackbar("✅ API Key guardada")
        }
    }

    fun saveSystemPrompt(prompt: String) {
        viewModelScope.launch {
            appPreferences.setSystemPrompt(prompt)
            showSnackbar("✅ Prompt guardado")
        }
    }

    fun resetSystemPrompt() {
        viewModelScope.launch {
            appPreferences.setSystemPrompt(AppPreferences.DEFAULT_SYSTEM_PROMPT)
            showSnackbar("Prompt restablecido al valor predeterminado")
        }
    }

    fun saveProfileInfo(userName: String, businessName: String, tone: String) {
        viewModelScope.launch {
            appPreferences.setProfileUserName(userName)
            appPreferences.setProfileBusinessName(businessName)
            appPreferences.setProfileTone(tone)
            showSnackbar("✅ Perfil guardado exitosamente")
        }
    }

    // ─── Canales ──────────────────────────────────────────────────────

    fun toggleChannelWhatsApp(enabled: Boolean) = viewModelScope.launch {
        appPreferences.setChannelWhatsApp(enabled)
    }

    fun toggleChannelFbMessenger(enabled: Boolean) = viewModelScope.launch {
        appPreferences.setChannelFbMessenger(enabled)
    }

    fun toggleChannelIgDirect(enabled: Boolean) = viewModelScope.launch {
        appPreferences.setChannelIgDirect(enabled)
    }

    // ─── Training Rules & Export/Import ────────────────────────────────
    
    val trainingRules: StateFlow<List<TrainingRule>> = trainingRuleDao.observeAll()
        .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

    private val _exportEvent = MutableStateFlow<String?>(null)
    val exportEvent: StateFlow<String?> = _exportEvent.asStateFlow()

    fun clearExportEvent() {
        _exportEvent.value = null
    }

    fun addTrainingRule(type: String, input: String, output: String?) {
        viewModelScope.launch {
            trainingRuleDao.insert(TrainingRule(type = type, input = input, output = output))
            showSnackbar("Regla agregada exitosamente")
        }
    }

    fun toggleTrainingRule(rule: TrainingRule) {
        viewModelScope.launch {
            trainingRuleDao.update(rule.copy(isActive = !rule.isActive))
        }
    }

    fun deleteTrainingRule(rule: TrainingRule) {
        viewModelScope.launch {
            trainingRuleDao.delete(rule)
            showSnackbar("Regla eliminada")
        }
    }

    fun exportConfiguration() {
        viewModelScope.launch {
            try {
                val prompt = appPreferences.systemPrompt.first()
                val usrName = appPreferences.profileUserName.first()
                val busName = appPreferences.profileBusinessName.first()
                val tne = appPreferences.profileTone.first()
                val rules = trainingRules.value
                val config = AiConfigExport(
                    systemPrompt = prompt,
                    profileUserName = usrName,
                    profileBusinessName = busName,
                    profileTone = tne,
                    trainingRules = rules
                )
                val json = Gson().toJson(config)
                _exportEvent.value = json
            } catch (e: Exception) {
                showSnackbar("❌ Error al exportar: ${e.message}")
            }
        }
    }

    fun importConfiguration(jsonString: String) {
        viewModelScope.launch {
            try {
                val config = Gson().fromJson(jsonString, AiConfigExport::class.java)
                appPreferences.setSystemPrompt(config.systemPrompt)
                config.profileUserName?.let { appPreferences.setProfileUserName(it) }
                config.profileBusinessName?.let { appPreferences.setProfileBusinessName(it) }
                config.profileTone?.let { appPreferences.setProfileTone(it) }
                
                trainingRuleDao.deleteAll()
                if (!config.trainingRules.isNullOrEmpty()) {
                    trainingRuleDao.insertAll(config.trainingRules.map { it.copy(id = 0) })
                }
                showSnackbar("✅ Configuración IA importada exitosamente")
            } catch (e: Exception) {
                showSnackbar("❌ Error cargando archivo: el formato JSON no es válido")
            }
        }
    }

    // ─── Scheduler ────────────────────────────────────────────────────

    fun setScheduleEnabled(enabled: Boolean) = viewModelScope.launch {
        appPreferences.setScheduleEnabled(enabled)
    }

    fun addScheduleRange(startH: Int, startM: Int, endH: Int, endM: Int) = viewModelScope.launch {
        val current = appPreferences.scheduleList.first().toMutableList()
        current.add(TimeRange(startH, startM, endH, endM))
        appPreferences.setScheduleList(current)
    }

    fun removeScheduleRange(index: Int) = viewModelScope.launch {
        val current = appPreferences.scheduleList.first().toMutableList()
        if (index in current.indices) {
            current.removeAt(index)
            appPreferences.setScheduleList(current)
        }
    }

    fun updateScheduleRange(index: Int, range: TimeRange) = viewModelScope.launch {
        val current = appPreferences.scheduleList.first().toMutableList()
        if (index in current.indices) {
            current[index] = range
            appPreferences.setScheduleList(current)
        }
    }

    fun setScheduleDays(days: Set<Int>) = viewModelScope.launch {
        appPreferences.setScheduleDays(days)
    }

    fun toggleScheduleDay(day: Int) = viewModelScope.launch {
        val current = appPreferences.scheduleDays.first().toMutableSet()
        if (day in current) current.remove(day) else current.add(day)
        appPreferences.setScheduleDays(current)
    }

    // ─── Session Summary + TTS ────────────────────────────────────────────────

    fun generateSummary() {
        val period = _summaryUiState.value.selectedPeriod
        viewModelScope.launch {
            val apiKey = appPreferences.geminiApiKey.first()
            if (apiKey.isBlank()) {
                _summaryUiState.update { it.copy(error = "❌ Configura tu Gemini API Key primero") }
                return@launch
            }

            _summaryUiState.update { it.copy(isLoading = true, error = "", summary = null) }

            try {
                // Filtrar logs según el período seleccionado
                val allLogs = responseLogDao.observeRecent(500).first()
                val now = System.currentTimeMillis()
                val filteredLogs = when (period) {
                    "Hoy" -> {
                        val todayStart = java.util.Calendar.getInstance().apply {
                            set(java.util.Calendar.HOUR_OF_DAY, 0)
                            set(java.util.Calendar.MINUTE, 0)
                            set(java.util.Calendar.SECOND, 0)
                        }.timeInMillis
                        allLogs.filter { it.timestamp >= todayStart }
                    }
                    "Semana" -> {
                        val weekStart = now - (7 * 24 * 60 * 60 * 1000L)
                        allLogs.filter { it.timestamp >= weekStart }
                    }
                    else -> allLogs
                }

                if (filteredLogs.isEmpty()) {
                    _summaryUiState.update {
                        it.copy(isLoading = false, error = "📭 No hay actividad para '$period' aún.")
                    }
                    return@launch
                }

                val todayStart = java.util.Calendar.getInstance().apply {
                    set(java.util.Calendar.HOUR_OF_DAY, 0)
                    set(java.util.Calendar.MINUTE, 0)
                    set(java.util.Calendar.SECOND, 0)
                }.timeInMillis
                val weekStart = todayStart - (6 * 24 * 60 * 60 * 1000L)

                val allEscalations = escalationLogDao.getAllFlow().first()
                val filteredEscalations = when (period) {
                    "Hoy" -> allEscalations.filter { it.timestamp >= todayStart }
                    "Semana" -> allEscalations.filter { it.timestamp >= weekStart }
                    else -> allEscalations
                }

                val summary = summaryGenerator.generateSummary(
                    apiKey = apiKey,
                    logs = filteredLogs,
                    escalations = filteredEscalations,
                    periodLabel = period.lowercase()
                )

                _summaryUiState.update {
                    it.copy(isLoading = false, summary = summary, error = "")
                }
                Log.d(TAG, "Resumen generado con ${filteredLogs.size} logs")

            } catch (e: Exception) {
                Log.e(TAG, "Error generando resumen", e)
                _summaryUiState.update {
                    it.copy(isLoading = false, error = "❌ ${e.message}")
                }
            }
        }
    }

    fun speakSummary() {
        val text = _summaryUiState.value.summary?.narrativeText ?: return
        ttsManager.setSpeechRate(_summaryUiState.value.speechRate)
        ttsManager.speak(text)
    }

    fun stopSpeaking() {
        ttsManager.stop()
    }

    fun setSpeechRate(rate: Float) {
        _summaryUiState.update { it.copy(speechRate = rate) }
        ttsManager.setSpeechRate(rate)
    }

    fun setSummaryPeriod(period: String) {
        _summaryUiState.update { it.copy(selectedPeriod = period, summary = null, error = "") }
        ttsManager.stop()
    }

    override fun onCleared() {
        super.onCleared()
        ttsManager.stop()
    }

    // ─── Helpers ──────────────────────────────────────────────────────

    private fun showSnackbar(message: String) {
        _uiState.update { it.copy(snackbarMessage = message) }
    }

    fun clearSnackbar() {
        _uiState.update { it.copy(snackbarMessage = null) }
    }

    fun isNotificationListenerEnabled(): Boolean {
        val flat = Settings.Secure.getString(
            context.contentResolver,
            "enabled_notification_listeners"
        )
        return flat?.contains(context.packageName) == true
    }
}
