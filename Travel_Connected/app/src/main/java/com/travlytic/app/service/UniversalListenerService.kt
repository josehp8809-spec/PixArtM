package com.travlytic.app.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.service.notification.NotificationListenerService
import android.os.Bundle
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.core.app.RemoteInput
import com.travlytic.app.R
import com.travlytic.app.data.db.dao.ResponseLogDao
import com.travlytic.app.data.db.entities.ResponseLog
import com.travlytic.app.data.prefs.AppPreferences
import com.travlytic.app.engine.GeminiAgent
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.first
import java.util.Calendar
import javax.inject.Inject

private const val TAG = "UniversalListener"
private const val WHATSAPP_PACKAGE = "com.whatsapp"
private const val WHATSAPP_BUSINESS_PACKAGE = "com.whatsapp.w4b"
private const val FB_MESSENGER_PACKAGE = "com.facebook.orca"
private const val IG_DIRECT_PACKAGE = "com.instagram.android"
private const val TRAVLYTIC_CHANNEL_ID = "travlytic_service"

@AndroidEntryPoint
class UniversalListenerService : NotificationListenerService() {

    @Inject lateinit var geminiAgent: GeminiAgent
    @Inject lateinit var responseLogDao: ResponseLogDao
    @Inject lateinit var appPreferences: AppPreferences

    private val serviceScope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    // ─── Motor Anti-Bucle ──────────────────────────────────────────────
    private val recentlyReplied = mutableMapOf<String, Long>()
    private val REPLY_COOLDOWN_MS = 30_000L // 30 segundos de cooldown por contacto

    // Caché circular estricto (últimos 15 mensajes) para Anti-Bucle de IA a IA
    private val recentResponseHashes = object : LinkedHashMap<Int, Long>(15, 0.75f, true) {
        override fun removeEldestEntry(eldest: MutableMap.MutableEntry<Int, Long>?): Boolean {
            return size > 15
        }
    }
    private val ANTI_LOOP_COOLDOWN_MS = 30_000L // 30 segundos IGNORANDO ecos

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "UniversalListenerService iniciado")
        createNotificationChannel()
        startForeground(1, buildForegroundNotification())
    }

    override fun onDestroy() {
        super.onDestroy()
        serviceScope.cancel()
        Log.d(TAG, "UniversalListenerService detenido")
    }

    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        sbn ?: return

        serviceScope.launch {
            try {
                // Verificar que el bot global está habilitado
                val botEnabled = appPreferences.botEnabled.first()
                if (!botEnabled) return@launch

                val pkg = sbn.packageName
                
                // Verificar qué canales están permitidos
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
                // Verificar horario programado
                if (!isWithinSchedule()) {
                    Log.d(TAG, "Fuera del horario programado, ignorando mensaje")
                    return@launch
                }

                // Verificar que tenemos API Key
                val apiKey = appPreferences.geminiApiKey.first()
                if (apiKey.isBlank()) {
                    Log.w(TAG, "API Key de Gemini no configurada, omitiendo respuesta")
                    return@launch
                }

                val notification = sbn.notification ?: return@launch
                
                // ─── Motor Anti-Bucle: Filtros de Seguridad ─────────────────
                
                // 1. Descartar sumarios (historias o "Tienes 4 mensajes de 2 chats")
                if ((notification.flags and Notification.FLAG_GROUP_SUMMARY) != 0) {
                    Log.d(TAG, "Ignorando notificación de tipo GROUP_SUMMARY")
                    return@launch
                }

                // 2. Extraer extras
                val extras = notification.extras ?: return@launch
                val contactName = extras.getString("android.title") ?: return@launch
                val messageText = extras.getCharSequence("android.text")?.toString() ?: return@launch

                // 3. Checar mensajes vacíos o nulos
                if (messageText.isBlank()) return@launch
                if (contactName.isBlank()) return@launch

                // 4. Asegurarnos que viene como MENSAJE (Evita intentos de historias o estados)
                val template = extras.getString(NotificationCompat.EXTRA_TEMPLATE)
                val isMessagingStyle = template == "androidx.core.app.NotificationCompat\$MessagingStyle" || 
                                       template == "android.app.Notification\$MessagingStyle"

                if (!isMessagingStyle && pkg != IG_DIRECT_PACKAGE) {
                    // IG no siempre usa MessagingStyle para nuevos mensajes.
                    // Pero para WP y FB obligamos MessagingStyle
                    Log.d(TAG, "Ignorando porque NO es un mensaje directo (Template: $template)")
                    return@launch
                }

                // 5. Anti-Bucle estricto: ¿Este mensaje es uno de nuestros ECOS recientes?
                val messageHash = messageText.hashCode()
                val lastTimeSeenRaw = recentResponseHashes[messageHash]
                val now = System.currentTimeMillis()
                
                if (lastTimeSeenRaw != null && (now - lastTimeSeenRaw < ANTI_LOOP_COOLDOWN_MS)) {
                    Log.w(TAG, "⛔ AUTO-CHECK: Este mensaje coincide con uno que mandamos recientemente. Bloqueando Bucle.")
                    return@launch
                }

                // Cooldown: evitar spam de respuestas al mismo contacto
                val now = System.currentTimeMillis()
                val lastReplied = recentlyReplied[contactName] ?: 0L
                if (now - lastReplied < REPLY_COOLDOWN_MS) {
                    Log.d(TAG, "Cooldown activo para '$contactName', ignorando mensaje")
                    return@launch
                }

                Log.d(TAG, "Mensaje de '$contactName': $messageText")

                // Delay configurable (simula que alguien está escribiendo)
                val delayMs = appPreferences.autoReplyDelayMs.first()
                delay(delayMs)

                // Obtener el system prompt y datos de perfil
                val systemPrompt = appPreferences.systemPrompt.first()
                val usrName = appPreferences.profileUserName.first()
                val busName = appPreferences.profileBusinessName.first()
                val tne = appPreferences.profileTone.first()

                // Generar respuesta con Gemini
                val response = geminiAgent.generateResponse(
                    apiKey = apiKey,
                    systemPrompt = systemPrompt,
                    contactName = contactName,
                    userMessage = messageText,
                    userName = usrName,
                    businessName = busName,
                    tone = tne
                )

                if (response.isNullOrBlank()) {
                    Log.w(TAG, "Gemini no generó respuesta para '$contactName'")
                    return@launch
                }

                // Enviar la respuesta usando RemoteInput (Universal)
                val sent = sendUniversalReply(sbn, response)

                if (sent) {
                    // Registrar en la caché Anti-Bucle el HASH de NUESTRA PROPIA RESPUESTA
                    // Esto evita que si la otra pantalla nos refleja, le re-contestemos.
                    recentResponseHashes[response.hashCode()] = System.currentTimeMillis()

                    // Marcar cooldown clásico
                    recentlyReplied[contactName] = System.currentTimeMillis()

                    // Guardar en log
                    responseLogDao.insert(
                        ResponseLog(
                            contact = contactName,
                            incomingMessage = messageText,
                            sentResponse = response,
                            timestamp = System.currentTimeMillis()
                        )
                    )
                    Log.d(TAG, "Respuesta enviada a '$contactName' [$pkg]: $response")
                }

            } catch (e: Exception) {
                Log.e(TAG, "Error procesando notificación", e)
            }
        }
    }

    /**
     * Envía una respuesta de vuelta buscando RECURSIVAMENTE cualquier RemoteInput válido en las Actions
     */
    private fun sendUniversalReply(sbn: StatusBarNotification, replyText: String): Boolean {
        val notification = sbn.notification ?: return false
        val actions = notification.actions ?: return false

        // 1. Buscar recursivamente el Action con RemoteInput
        var targetAction: Notification.Action? = null
        var targetRemoteInput: RemoteInput? = null

        for (action in actions) {
            val remoteInputs = action.remoteInputs
            if (remoteInputs != null) {
                for (remoteInput in remoteInputs) {
                    if (remoteInput.allowFreeFormInput) {
                        targetAction = action
                        targetRemoteInput = remoteInput
                        break
                    }
                }
            }
            if (targetAction != null) break
        }

        if (targetAction == null || targetRemoteInput == null) {
            Log.w(TAG, "No se encontró ningún RemoteInput (Botón Responder) en la notificación")
            return false
        }

        // 2. Ejecutar la acción
        return try {
            val intent = Intent()
            val bundle = Bundle()
            bundle.putCharSequence(targetRemoteInput.resultKey, replyText)
            
            RemoteInput.addResultsToIntent(
                arrayOf(targetRemoteInput),
                intent,
                bundle
            )

            targetAction.actionIntent.send(this, 0, intent)
            true
        } catch (e: PendingIntent.CanceledException) {
            Log.e(TAG, "PendingIntent cancelado al intentar responder", e)
            false
        } catch (e: Exception) {
            Log.e(TAG, "Error enviando reply", e)
            false
        }
    }

    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            TRAVLYTIC_CHANNEL_ID,
            "Travlytic Bot",
            NotificationManager.IMPORTANCE_LOW
        ).apply {
            description = "Servicio activo de respuesta automática"
        }
        val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        manager.createNotificationChannel(channel)
    }

    private fun buildForegroundNotification(): Notification {
        return NotificationCompat.Builder(this, TRAVLYTIC_CHANNEL_ID)
            .setContentTitle("Travlytic activo")
            .setContentText("Respondiendo mensajes automáticamente")
            .setSmallIcon(R.drawable.ic_bot_active)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setOngoing(true)
            .build()
    }

    /**
     * Verifica si el momento actual está dentro del horario programado.
     * Si el schedule no está habilitado, siempre retorna true (24/7).
     */
    private suspend fun isWithinSchedule(): Boolean {
        val scheduleEnabled = appPreferences.scheduleEnabled.first()
        if (!scheduleEnabled) return true

        val now = Calendar.getInstance()
        val currentHour = now.get(Calendar.HOUR_OF_DAY)
        val currentMinute = now.get(Calendar.MINUTE)
        // Calendar.DAY_OF_WEEK: 1=Dom, 2=Lun... Normalizamos a 1=Lun, 7=Dom
        val calDay = now.get(Calendar.DAY_OF_WEEK)
        val dayNum = if (calDay == Calendar.SUNDAY) 7 else calDay - 1

        val activeDays = appPreferences.scheduleDays.first()
        if (dayNum !in activeDays) return false

        val startH = appPreferences.scheduleStartHour.first()
        val startM = appPreferences.scheduleStartMinute.first()
        val endH   = appPreferences.scheduleEndHour.first()
        val endM   = appPreferences.scheduleEndMinute.first()

        val currentMins = currentHour * 60 + currentMinute
        val startMins   = startH * 60 + startM
        val endMins     = endH * 60 + endM

        return if (endMins > startMins) {
            // Rango normal: ej 08:00 → 20:00
            currentMins in startMins..endMins
        } else {
            // Rango nocturno: ej 22:00 → 06:00
            currentMins >= startMins || currentMins <= endMins
        }
    }
}
