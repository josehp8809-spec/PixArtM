package com.travlytic.app.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log

private const val TAG = "BootReceiver"

/**
 * Se ejecuta cuando el dispositivo arranca.
 * El NotificationListenerService de Android se reinicia automáticamente,
 * pero este receiver puede usarse para futuras acciones de inicio.
 */
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            Log.d(TAG, "Dispositivo reiniciado. Travlytic listo.")
        }
    }
}
