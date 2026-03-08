package com.travlytic.app.ui.viewmodel

import android.content.Context
import android.content.Intent
import android.provider.Settings
import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.auth.api.signin.GoogleSignInAccount
import com.google.android.gms.auth.api.signin.GoogleSignInOptions
import com.google.api.services.sheets.v4.SheetsScopes
import com.travlytic.app.data.db.dao.RegisteredSheetDao
import com.travlytic.app.data.db.dao.ResponseLogDao
import com.travlytic.app.data.db.entities.ResponseLog
import com.travlytic.app.data.db.entities.RegisteredSheet
import com.travlytic.app.data.prefs.AppPreferences
import com.travlytic.app.data.db.dao.TrainingRuleDao
import com.travlytic.app.data.db.entities.TrainingRule
import com.travlytic.app.engine.AiConfigExport
import com.google.gson.Gson
import com.travlytic.app.data.sheets.SheetsRepository
import com.travlytic.app.data.sheets.SyncResult
import com.travlytic.app.engine.GeminiAgent
import com.travlytic.app.engine.SessionSummary
import com.travlytic.app.engine.SummaryGenerator
import com.travlytic.app.engine.TtsManager
import com.travlytic.app.engine.TtsState
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

private const val TAG = "MainViewModel"

data class UiState(
    val isServiceEnabled: Boolean = false,
    val googleAccountEmail: String = "",
    val registeredSheets: List<RegisteredSheet> = emptyList(),
    val recentLogs: List<ResponseLog> = emptyList(),
    val isLoading: Boolean = false,
    val syncingSheetId: String? = null,
    val snackbarMessage: String? = null
)

data class ScheduleState(
    val enabled: Boolean = false,
    val startHour: Int = 8,
    val startMinute: Int = 0,
    val endHour: Int = 20,
    val endMinute: Int = 0,
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
    private val sheetsRepository: SheetsRepository,
    private val registeredSheetDao: RegisteredSheetDao,
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

    // Settings screen state
    val geminiApiKey: StateFlow<String> = appPreferences.geminiApiKey
        .stateIn(viewModelScope, SharingStarted.Lazily, "")

    val systemPrompt: StateFlow<String> = appPreferences.systemPrompt
        .stateIn(viewModelScope, SharingStarted.Lazily, AppPreferences.DEFAULT_SYSTEM_PROMPT)

    val botEnabled: StateFlow<Boolean> = appPreferences.botEnabled
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
        appPreferences.scheduleStartHour,
        appPreferences.scheduleStartMinute,
        appPreferences.scheduleEndHour,
        appPreferences.scheduleEndMinute,
        appPreferences.scheduleDays
    ) { values ->
        ScheduleState(
            enabled      = values[0] as Boolean,
            startHour    = values[1] as Int,
            startMinute  = values[2] as Int,
            endHour      = values[3] as Int,
            endMinute    = values[4] as Int,
            activeDays   = @Suppress("UNCHECKED_CAST") (values[5] as Set<Int>)
        )
    }.stateIn(viewModelScope, SharingStarted.Lazily, ScheduleState())

    // ─── Dashboard State ────────────────────────────────────────────
    private val _dashboardState = MutableStateFlow(DashboardState())
    val dashboardState: StateFlow<DashboardState> = _dashboardState.asStateFlow()

    // ─── Test Message State ──────────────────────────────────────────
    private val _testMsgState = MutableStateFlow(TestMessageState())
    val testMsgState: StateFlow<TestMessageState> = _testMsgState.asStateFlow()

    init {
        observeRegisteredSheets()
        observeRecentLogs()
        observeGoogleAccount()
        observeServiceStatus()
        observeDashboard()
    }

    private fun observeRegisteredSheets() {
        registeredSheetDao.observeAll()
            .onEach { sheets -> _uiState.update { it.copy(registeredSheets = sheets) } }
            .launchIn(viewModelScope)
    }

    private fun observeRecentLogs() {
        responseLogDao.observeRecent(50)
            .onEach { logs -> _uiState.update { it.copy(recentLogs = logs) } }
            .launchIn(viewModelScope)
    }

    private fun observeGoogleAccount() {
        appPreferences.googleAccountEmail
            .onEach { email -> _uiState.update { it.copy(googleAccountEmail = email) } }
            .launchIn(viewModelScope)
    }

    private fun observeServiceStatus() {
        appPreferences.botEnabled
            .onEach { enabled -> _uiState.update { it.copy(isServiceEnabled = enabled) } }
            .launchIn(viewModelScope)
    }

    private fun observeDashboard() {
        // Actualiza el dashboard cada vez que cambian los logs o los sheets
        viewModelScope.launch {
            combine(
                responseLogDao.observeRecent(500),
                registeredSheetDao.observeAll()
            ) { logs, sheets ->
                val now = System.currentTimeMillis()
                val todayStart = java.util.Calendar.getInstance().apply {
                    set(java.util.Calendar.HOUR_OF_DAY, 0)
                    set(java.util.Calendar.MINUTE, 0)
                    set(java.util.Calendar.SECOND, 0)
                }.timeInMillis
                val weekStart = todayStart - (6 * 24 * 60 * 60 * 1000L)

                val repliesToday = logs.count { it.timestamp >= todayStart }
                val repliesWeek  = logs.count { it.timestamp >= weekStart }
                val activeSheets = sheets.filter { it.isEnabled }

                // Suma total de filas de todos los sheets activos
                val totalRows = activeSheets.sumOf { it.rowCount }

                DashboardState(
                    repliesToday = repliesToday,
                    repliesThisWeek = repliesWeek,
                    totalKnowledgeRows = totalRows,
                    activeSheetsCount = activeSheets.size
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
                    response = response ?: "Sin respuesta. Verifica que tienes Sheets sincronizados.",
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

    // ─── Google Sign-In ───────────────────────────────────────────────

    fun getGoogleSignInClient(context: Context) =
        GoogleSignIn.getClient(
            context,
            GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
                .requestIdToken(context.getString(com.travlytic.app.R.string.default_web_client_id))
                .requestEmail()
                .requestScopes(
                    com.google.android.gms.common.api.Scope(SheetsScopes.SPREADSHEETS_READONLY)
                )
                .build()
        )

    fun onGoogleSignInSuccess(account: GoogleSignInAccount) {
        viewModelScope.launch {
            val email = account.email ?: return@launch
            appPreferences.setGoogleAccountEmail(email)
            showSnackbar("✅ Conectado como $email")
            Log.d(TAG, "Google Sign-In exitoso: $email")
        }
    }

    fun signOut() {
        viewModelScope.launch {
            appPreferences.setGoogleAccountEmail("")
            showSnackbar("Sesión de Google cerrada")
        }
    }

    // ─── Sheets ───────────────────────────────────────────────────────

    fun addSheet(input: String) {
        viewModelScope.launch {
            val spreadsheetId = sheetsRepository.extractSpreadsheetId(input)
            if (spreadsheetId.isNullOrBlank()) {
                showSnackbar("❌ URL o ID de Sheet inválido")
                return@launch
            }

            val existing = registeredSheetDao.getById(spreadsheetId)
            if (existing != null) {
                showSnackbar("⚠️ Este Sheet ya está registrado")
                return@launch
            }

            _uiState.update { it.copy(isLoading = true) }

            val email = appPreferences.googleAccountEmail.first()
            if (email.isBlank()) {
                showSnackbar("❌ Primero conecta tu cuenta de Google")
                _uiState.update { it.copy(isLoading = false) }
                return@launch
            }

            // Intentar obtener el título del sheet
            val title = sheetsRepository.fetchSheetTitle(spreadsheetId, email)
                ?: "Sheet $spreadsheetId"

            sheetsRepository.registerSheet(spreadsheetId, title)

            // Auto-sincronizar al agregar
            syncSheet(spreadsheetId)

            _uiState.update { it.copy(isLoading = false) }
        }
    }

    fun syncSheet(spreadsheetId: String) {
        viewModelScope.launch {
            val email = appPreferences.googleAccountEmail.first()
            if (email.isBlank()) {
                showSnackbar("❌ Primero conecta tu cuenta de Google")
                return@launch
            }

            _uiState.update { it.copy(syncingSheetId = spreadsheetId) }

            val result = sheetsRepository.syncSheet(spreadsheetId, email)

            when (result) {
                is SyncResult.Success ->
                    showSnackbar("✅ ${result.sheetTitle} sincronizado (${result.rowCount} filas)")
                is SyncResult.Error ->
                    showSnackbar("❌ Error: ${result.message}")
            }

            _uiState.update { it.copy(syncingSheetId = null) }
        }
    }

    fun syncAllSheets() {
        viewModelScope.launch {
            val email = appPreferences.googleAccountEmail.first()
            if (email.isBlank()) {
                showSnackbar("❌ Primero conecta tu cuenta de Google")
                return@launch
            }

            _uiState.update { it.copy(isLoading = true) }
            val results = sheetsRepository.syncAll(email)
            val successCount = results.values.count { it is SyncResult.Success }
            val totalRows = results.values
                .filterIsInstance<SyncResult.Success>()
                .sumOf { it.rowCount }

            showSnackbar("✅ $successCount sheets sincronizados ($totalRows filas totales)")
            _uiState.update { it.copy(isLoading = false) }
        }
    }

    fun removeSheet(spreadsheetId: String) {
        viewModelScope.launch {
            sheetsRepository.removeSheet(spreadsheetId)
            showSnackbar("Sheet eliminado")
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

    fun setScheduleStart(hour: Int, minute: Int) = viewModelScope.launch {
        appPreferences.setScheduleStart(hour, minute)
    }

    fun setScheduleEnd(hour: Int, minute: Int) = viewModelScope.launch {
        appPreferences.setScheduleEnd(hour, minute)
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

                val summary = summaryGenerator.generateSummary(
                    apiKey = apiKey,
                    logs = filteredLogs,
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
