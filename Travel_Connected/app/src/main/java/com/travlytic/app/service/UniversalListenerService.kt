package com.travlytic.app.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.util.Log
import androidx.core.app.NotificationCompat
import android.app.RemoteInput
import com.travlytic.app.R
import com.travlytic.app.data.db.dao.EscalationLogDao
import com.travlytic.app.data.db.dao.ResponseLogDao
import com.travlytic.app.data.db.entities.EscalationLog
import com.travlytic.app.data.db.entities.ResponseLog
import com.travlytic.app.data.prefs.AppPreferences
import com.travlytic.app.engine.GeminiAgent
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.first
import java.util.Calendar
import java.util.Collections
import javax.inject.Inject

private const val TAG = "UniversalListener"
private const val WHATSAPP_PACKAGE = "com.whatsapp"
private const val WHATSAPP_BUSINESS_PACKAGE = "com.whatsapp.w4b"
private const val FB_MESSENGER_PACKAGE = "com.facebook.orca"
private const val IG_DIRECT_PACKAGE = "com.instagram.android"
private const val MINITO_CHANNEL_ID = "minito_service"
private const val ALERTS_CHANNEL_ID = "minito_alerts"

@AndroidEntryPoint
class UniversalListenerService : NotificationListenerService() {

    @Inject lateinit var geminiAgent: GeminiAgent
    @Inject lateinit var responseLogDao: ResponseLogDao
    @Inject lateinit var escalationLogDao: EscalationLogDao
    @Inject lateinit var appPreferences: AppPreferences

    private val serviceScope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    // ─── Motor Anti-Bucle ──────────────────────────────────────────────
    private val recentlyReplied = mutableMapOf<String, Long>()
    private val REPLY_COOLDOWN_MS = 2_000L

    // Semáforos por contacto para evitar carreras en Bienvenida
    private val welcomeMutexMap = Collections.synchronizedMap(mutableMapOf<String, Any>())

    // Caché circular estricto (últimos 30 mensajes) para Anti-Bucle
    private val recentResponseHashes = object : LinkedHashMap<Int, Long>(30, 0.75f, true) {
        override fun removeEldestEntry(eldest: MutableMap.MutableEntry<Int, Long>?): Boolean = size > 30
    }
    private val ANTI_LOOP_COOLDOWN_MS = 45_000L // 45 segundos de inmunidad a ecos

    private val activeReminders = mutableMapOf<String, Job>()

    /**
     * Limpia el texto de prefijos de autoría comunes que generan bucles
     */
    private fun normalizeForAntiLoop(text: String): String {
        return text.lowercase()
            .replace(Regex("^(yo|tú|tu|me|you|bot|mini-to|minito|trv):\\s*", RegexOption.IGNORE_CASE), "")
            .replace(Regex("[^\\p{L}\\p{N}]"), "") // Solo letras y números
            .trim()
    }

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        startForeground(1, buildForegroundNotification())
    }

    override fun onDestroy() {
        super.onDestroy()
        serviceScope.cancel()
    }

    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        sbn ?: return

        serviceScope.launch {
            try {
                val pkg = sbn.packageName
                val isWhatsappEnabled = appPreferences.channelWhatsApp.first()
                val isFbEnabled = appPreferences.channelFbMessenger.first()
                val isIgEnabled = appPreferences.channelIgDirect.first()

                val isAllowedPackage = when (pkg) {
                    WHATSAPP_PACKAGE, WHATSAPP_BUSINESS_PACKAGE -> isWhatsappEnabled
                    FB_MESSENGER_PACKAGE -> isFbEnabled
                    IG_DIRECT_PACKAGE -> isIgEnabled
                    else -> false
                }
                if (!isAllowedPackage) return@launch

                val manualEnabled = appPreferences.botEnabled.first()
                val scheduleValue = isWithinSchedule()
                
                // El bot se activa si: (Manual está ON) O (Programación está ON y es hora activa)
                if (!manualEnabled && !scheduleValue) return@launch

                val apiKey = appPreferences.geminiApiKey.first()
                if (apiKey.isBlank()) return@launch

                val notification = sbn.notification ?: return@launch
                val extras = notification.extras ?: return@launch
                
                val contactName = extras.getString("android.title") ?: return@launch
                val messageText = extras.getCharSequence(Notification.EXTRA_TEXT)?.toString()?.trim() ?: ""

                if (messageText.isBlank() || contactName.isBlank()) return@launch

                // ─── FILTRO 1: Auto-Notificaciones (Detección de Propietario) ───
                val myName = appPreferences.profileUserName.first()
                if (contactName.equals(myName, ignoreCase = true) || contactName.lowercase().contains("yo")) {
                    Log.d(TAG, "Detectada auto-notificación de '$contactName'. Ignorando.")
                    return@launch
                }

                // ─── FILTRO 2: Anti-Bucle con Normalización Inteligente ───
                val normalizedMsg = normalizeForAntiLoop(messageText)
                val msgHash = normalizedMsg.hashCode()
                val lastSeen = recentResponseHashes[msgHash]
                val now = System.currentTimeMillis()

                if (lastSeen != null && (now - lastSeen < ANTI_LOOP_COOLDOWN_MS)) {
                    Log.w(TAG, "⛔ BLINDAJE: Eco detectado (Hash: $msgHash). Bloqueando bucle.")
                    return@launch
                }

                if ((notification.flags and Notification.FLAG_GROUP_SUMMARY) != 0) return@launch

                val template = extras.getString(NotificationCompat.EXTRA_TEMPLATE)
                val isMessagingStyle = template?.contains("MessagingStyle") == true
                if (!isMessagingStyle && pkg != IG_DIRECT_PACKAGE) return@launch

                val lastReplied = recentlyReplied[contactName] ?: 0L
                if (now - lastReplied < REPLY_COOLDOWN_MS) return@launch

                activeReminders[contactName]?.cancel()
                activeReminders.remove(contactName)

                // ─── LÓGICA DE BIENVENIDA (ATÓMICA) ───
                val logCount = responseLogDao.getLogCountForContact(contactName)
                val isFirstInteraction = logCount == 0

                if (isFirstInteraction) {
                    val mutex = welcomeMutexMap.getOrPut(contactName) { Any() }
                    synchronized(mutex) {
                        // Re-verificar dentro del synchronized
                        val refreshedCount = runBlocking { responseLogDao.getLogCountForContact(contactName) }
                        if (refreshedCount == 0) {
                            val welcomeMsg = runBlocking { appPreferences.welcomeMessage.first() }
                            if (welcomeMsg.isNotBlank()) {
                                sendUniversalReply(sbn, welcomeMsg)
                                val welcomeHash = normalizeForAntiLoop(welcomeMsg).hashCode()
                                recentResponseHashes[welcomeHash] = System.currentTimeMillis()
                                
                                runBlocking {
                                    responseLogDao.insert(ResponseLog(
                                        contact = contactName,
                                        incomingMessage = messageText,
                                        sentResponse = welcomeMsg,
                                        timestamp = System.currentTimeMillis()
                                    ))
                                }
                                Thread.sleep(1500)
                            }
                        }
                    }
                    welcomeMutexMap.remove(contactName)
                }

                // Extracción de audio...
                var audioBytes: ByteArray? = null
                val messagingStyle = NotificationCompat.MessagingStyle.extractMessagingStyleFromNotification(notification)
                messagingStyle?.messages?.lastOrNull()?.let { lastMsg ->
                    if (lastMsg.dataMimeType?.startsWith("audio/") == true) {
                        lastMsg.dataUri?.let { uri ->
                            try {
                                contentResolver.openInputStream(uri)?.use { stream -> audioBytes = stream.readBytes() }
                            } catch (e: Exception) { Log.e(TAG, "Error audio", e) }
                        }
                    }
                }

                val delayMs = appPreferences.autoReplyDelayMs.first()
                delay(delayMs)

                // Generar respuesta con IA Inmutable
                val response = geminiAgent.generateResponse(
                    apiKey = apiKey,
                    systemPrompt = appPreferences.systemPrompt.first(),
                    contactName = contactName,
                    userMessage = messageText,
                    userName = appPreferences.profileUserName.first(),
                    businessName = appPreferences.profileBusinessName.first(),
                    tone = appPreferences.profileTone.first(),
                    audioData = audioBytes,
                    internetSearchEnabled = appPreferences.internetSearchEnabled.first(),
                    isFirstInteraction = isFirstInteraction
                )

                if (response.isNullOrBlank()) return@launch

                if (response.contains("ESCALATE_REQUIRED")) {
                    val escalationMsg = appPreferences.escalationMessage.first()
                    if (sendUniversalReply(sbn, escalationMsg)) {
                        escalationLogDao.insert(EscalationLog(contact = contactName, originalMessage = messageText, timestamp = System.currentTimeMillis()))
                        recentResponseHashes[normalizeForAntiLoop(escalationMsg).hashCode()] = System.currentTimeMillis()
                        showLocalEscalationNotification(contactName, messageText)
                    }
                    return@launch
                }

                val sent = sendUniversalReply(sbn, response)
                if (sent) {
                    recentResponseHashes[normalizeForAntiLoop(response).hashCode()] = System.currentTimeMillis()
                    recentlyReplied[contactName] = System.currentTimeMillis()
                    responseLogDao.insert(ResponseLog(contact = contactName, incomingMessage = messageText, sentResponse = response, timestamp = System.currentTimeMillis()))
                    
                    // Auto-Recordatorio (Amable)
                    val reminderEnabled = appPreferences.autoReminderEnabled.first()
                    if (reminderEnabled) {
                        val reminderMessage = appPreferences.autoReminderMessage.first()
                        if (reminderMessage.isNotBlank()) {
                            activeReminders[contactName] = serviceScope.launch {
                                delay(5 * 60 * 1000L)
                                if (sendUniversalReply(sbn, reminderMessage)) {
                                    recentResponseHashes[normalizeForAntiLoop(reminderMessage).hashCode()] = System.currentTimeMillis()
                                    responseLogDao.insert(ResponseLog(contact = contactName, incomingMessage = "[Recordatorio]", sentResponse = reminderMessage, timestamp = System.currentTimeMillis()))
                                }
                            }
                        }
                    }
                }
            } catch (e: Exception) { Log.e(TAG, "Critical error", e) }
        }
    }

    private fun sendUniversalReply(sbn: StatusBarNotification, replyText: String): Boolean {
        val actions = sbn.notification?.actions ?: return false
        for (action in actions) {
            action.remoteInputs?.forEach { remoteInput ->
                if (remoteInput.allowFreeFormInput) {
                    try {
                        val intent = Intent().apply {
                            val bundle = Bundle().apply { putCharSequence(remoteInput.resultKey, replyText) }
                            RemoteInput.addResultsToIntent(arrayOf(remoteInput), this, bundle)
                        }
                        action.actionIntent.send(this, 0, intent)
                        return true
                    } catch (e: Exception) { Log.e(TAG, "Reply failed", e) }
                }
            }
        }
        return false
    }

    private fun showLocalEscalationNotification(contact: String, message: String) {
        val intent = Intent(this, com.travlytic.app.MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }
        val pendingIntent = PendingIntent.getActivity(this, 0, intent, PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)

        val notification = NotificationCompat.Builder(this, ALERTS_CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_escalation_alert)
            .setContentTitle("⚠️ Intervención Requerida")
            .setContentText("Escalado: $contact")
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .build()

        (getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager).notify(contact.hashCode(), notification)
    }

    private fun createNotificationChannel() {
        val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        manager.createNotificationChannel(NotificationChannel(MINITO_CHANNEL_ID, "MINI-TO Bot", NotificationManager.IMPORTANCE_LOW))
        manager.createNotificationChannel(NotificationChannel(ALERTS_CHANNEL_ID, "MINI-TO Alertas", NotificationManager.IMPORTANCE_HIGH).apply {
            enableVibration(true)
            setShowBadge(true)
        })
    }

    private fun buildForegroundNotification(): Notification {
        return NotificationCompat.Builder(this, MINITO_CHANNEL_ID)
            .setContentTitle("MINI-TO activo")
            .setContentText("Asistente listo")
            .setSmallIcon(R.drawable.ic_bot_active)
            .setOngoing(true)
            .build()
    }

    private suspend fun isWithinSchedule(): Boolean {
        if (!appPreferences.scheduleEnabled.first()) return false
        val now = Calendar.getInstance()
        val currentMins = now.get(Calendar.HOUR_OF_DAY) * 60 + now.get(Calendar.MINUTE)
        val dayNum = if (now.get(Calendar.DAY_OF_WEEK) == Calendar.SUNDAY) 7 else now.get(Calendar.DAY_OF_WEEK) - 1
        
        val activeDays = appPreferences.scheduleDays.first()
        if (dayNum !in activeDays) return false
        
        val ranges = appPreferences.scheduleList.first()
        if (ranges.isEmpty()) return false
        
        return ranges.any { range ->
            val startMins = range.startHour * 60 + range.startMinute
            val endMins = range.endHour * 60 + range.endMinute
            
            if (endMins > startMins) {
                currentMins in startMins..endMins
            } else {
                currentMins >= startMins || currentMins <= endMins
            }
        }
    }
}
