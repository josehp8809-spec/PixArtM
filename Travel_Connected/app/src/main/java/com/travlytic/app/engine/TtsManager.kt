package com.travlytic.app.engine

import android.content.Context
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.util.Log
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.Locale
import javax.inject.Inject
import javax.inject.Singleton

private const val TAG = "TtsManager"
private const val UTTERANCE_ID = "travlytic_summary"

enum class TtsState { IDLE, SPEAKING, PAUSED, ERROR }

@Singleton
class TtsManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private var tts: TextToSpeech? = null
    private var isInitialized = false

    private val _ttsState = MutableStateFlow(TtsState.IDLE)
    val ttsState: StateFlow<TtsState> = _ttsState.asStateFlow()

    private val _progress = MutableStateFlow(0f) // 0.0 → 1.0
    val progress: StateFlow<Float> = _progress.asStateFlow()

    init {
        initialize()
    }

    private fun initialize() {
        tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                // Español latinoamericano, con fallback a español
                val result = tts?.setLanguage(Locale("es", "MX"))
                    ?: TextToSpeech.LANG_NOT_SUPPORTED

                if (result == TextToSpeech.LANG_MISSING_DATA ||
                    result == TextToSpeech.LANG_NOT_SUPPORTED) {
                    tts?.setLanguage(Locale("es", "ES"))
                }

                tts?.setSpeechRate(0.95f)  // Ligeramente más lento para claridad
                tts?.setPitch(1.0f)

                setupProgressListener()
                isInitialized = true
                Log.d(TAG, "TTS inicializado correctamente")
            } else {
                Log.e(TAG, "Error inicializando TTS: $status")
                _ttsState.value = TtsState.ERROR
            }
        }
    }

    private fun setupProgressListener() {
        tts?.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
            override fun onStart(utteranceId: String?) {
                _ttsState.value = TtsState.SPEAKING
                _progress.value = 0f
            }

            override fun onDone(utteranceId: String?) {
                _ttsState.value = TtsState.IDLE
                _progress.value = 1f
                Log.d(TAG, "TTS finalizado")
            }

            @Deprecated("Deprecated in Java")
            override fun onError(utteranceId: String?) {
                _ttsState.value = TtsState.ERROR
                Log.e(TAG, "Error en TTS")
            }

            override fun onRangeStart(utteranceId: String?, start: Int, end: Int, frame: Int) {
                // Actualizar progreso aproximado
            }
        })
    }

    /**
     * Lee el texto en voz alta.
     * @param text Texto a leer (puede ser largo, TTS lo maneja en chunks)
     */
    fun speak(text: String) {
        if (!isInitialized) {
            Log.w(TAG, "TTS no inicializado, reintentando...")
            initialize()
            return
        }

        // Limpiar cola anterior
        tts?.stop()

        // Dividir en párrafos para mejor entonación
        val chunks = text.split("\n").filter { it.isNotBlank() }

        if (chunks.size == 1) {
            tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, UTTERANCE_ID)
        } else {
            // Primer chunk reemplaza la cola, los demás se agregan
            chunks.forEachIndexed { index, chunk ->
                val mode = if (index == 0) TextToSpeech.QUEUE_FLUSH else TextToSpeech.QUEUE_ADD
                val uid = if (index == chunks.lastIndex) UTTERANCE_ID else "${UTTERANCE_ID}_$index"
                tts?.speak(chunk, mode, null, uid)
            }
        }

        _ttsState.value = TtsState.SPEAKING
        Log.d(TAG, "Reproduciendo texto (${text.length} chars)")
    }

    /** Pausa la reproducción */
    fun pause() {
        tts?.stop()
        _ttsState.value = TtsState.IDLE
    }

    /** Detiene completamente */
    fun stop() {
        tts?.stop()
        _ttsState.value = TtsState.IDLE
        _progress.value = 0f
    }

    /** Cambia velocidad de habla */
    fun setSpeechRate(rate: Float) {
        tts?.setSpeechRate(rate.coerceIn(0.5f, 2.0f))
    }

    fun isSpeaking() = _ttsState.value == TtsState.SPEAKING

    fun destroy() {
        tts?.stop()
        tts?.shutdown()
        tts = null
        isInitialized = false
    }
}
