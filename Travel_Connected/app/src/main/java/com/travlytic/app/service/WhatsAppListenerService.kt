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

private const val TAG = "WhatsAppListener"
private const val WHATSAPP_PACKAGE = "com.whatsapp"
private const val WHATSAPP_BUSINESS_PACKAGE = "com.whatsapp.w4b"
private const val TRAVLYTIC_CHANNEL_ID = "travlytic_service"

@AndroidEntryPoint
class WhatsAppListenerService : NotificationListenerService() {

    @Inject lateinit var geminiAgent: GeminiAgent
    @Inject lateinit var responseLogDao: ResponseLogDao
    @Inject lateinit var appPreferences: AppPreferences

    private val serviceScope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    // Mapa para evitar responder al mismo contacto/mensaje dos veces
    private val recentlyReplied = mutableMapOf<String, Long>()
    private val REPLY_COOLDOWN_MS = 30_000L // 30 segundos de cooldown por contacto

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "WhatsAppListenerService iniciado")
        createNotificationChannel()
        startForeground(1, buildForegroundNotification())
    }

    override fun onDestroy() {
        super.onDestroy()
        serviceScope.cancel()
        Log.d(TAG, "WhatsAppListenerService detenido")
    }

    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        sbn ?: return

        // Solo procesar notificaciones de WhatsApp (normal o Business)
        val pkg = sbn.packageName
        if (pkg != WHATSAPP_PACKAGE && pkg != WHATSAPP_BUSINESS_PACKAGE) return

        serviceScope.launch {
            try {
                // Verificar que el bot está habilitado
                val botEnabled = appPreferences.botEnabled.first()
                if (!botEnabled) return@launch

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
                val extras = notification.extras ?: return@launch

                // Extraer contacto y mensaje
                val contactName = extras.getString("android.title") ?: return@launch
                val messageText = extras.getCharSequence("android.text")?.toString() ?: return@launch

                // Ignorar mensajes grupales (contienen ":" en el título normalmente) y mensajes vacíos
                if (messageText.isBlank()) return@launch
                if (contactName.isBlank()) return@launch

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

                // Obtener el system prompt
                val systemPrompt = appPreferences.systemPrompt.first()

                // Generar respuesta con Gemini
                val response = geminiAgent.generateResponse(
                    apiKey = apiKey,
                    systemPrompt = systemPrompt,
                    contactName = contactName,
                    userMessage = messageText
                )

                if (response.isNullOrBlank()) {
                    Log.w(TAG, "Gemini no generó respuesta para '$contactName'")
                    return@launch
                }

                // Enviar la respuesta por WhatsApp usando RemoteInput
                val sent = sendWhatsAppReply(sbn, response)

                if (sent) {
                    // Marcar cooldown
                    recentlyReplied[contactName] = now

                    // Guardar en log
                    responseLogDao.insert(
                        ResponseLog(
                            contact = contactName,
                            incomingMessage = messageText,
                            sentResponse = response,
                            timestamp = now
                        )
                    )
                    Log.d(TAG, "Respuesta enviada a '$contactName': $response")
                }

            } catch (e: Exception) {
                Log.e(TAG, "Error procesando notificación", e)
            }
        }
    }

    /**
     * Envía una respuesta usando la acción RemoteInput de la notificación de WhatsApp.
     */
    private fun sendWhatsAppReply(sbn: StatusBarNotification, replyText: String): Boolean {
        val notification = sbn.notification ?: return false
        val actions = notification.actions ?: return false

        // Buscar la acción de "Responder"
        val replyAction = actions.firstOrNull { action ->
            action.remoteInputs != null && action.remoteInputs.isNotEmpty()
        } ?: run {
            Log.w(TAG, "No se encontró acción de reply en la notificación")
            return false
        }

        return try {
            val remoteInput = replyAction.remoteInputs.first()
            val intent = Intent()
            val bundle = Bundle()
            bundle.putCharSequence(remoteInput.resultKey, replyText)
            androidx.core.app.RemoteInput.addResultsToIntent(
                arrayOf(
                    androidx.core.app.RemoteInput.Builder(remoteInput.resultKey).build()
                ),
                intent,
                bundle
            )

            replyAction.actionIntent.send(this, 0, intent)
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
