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
import com.travlytic.app.data.sheets.SheetsRepository
import com.travlytic.app.data.sheets.SyncResult
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
@HiltViewModel
class MainViewModel @Inject constructor(
    @ApplicationContext private val context: Context,
    private val appPreferences: AppPreferences,
    private val sheetsRepository: SheetsRepository,
    private val registeredSheetDao: RegisteredSheetDao,
    private val responseLogDao: ResponseLogDao
) : ViewModel() {

    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    // Settings screen state
    val geminiApiKey: StateFlow<String> = appPreferences.geminiApiKey
        .stateIn(viewModelScope, SharingStarted.Lazily, "")

    val systemPrompt: StateFlow<String> = appPreferences.systemPrompt
        .stateIn(viewModelScope, SharingStarted.Lazily, AppPreferences.DEFAULT_SYSTEM_PROMPT)

    val botEnabled: StateFlow<Boolean> = appPreferences.botEnabled
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
                val response = geminiAgent.generateResponse(
                    apiKey = apiKey,
                    systemPrompt = prompt,
                    contactName = "Test",
                    userMessage = message
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
