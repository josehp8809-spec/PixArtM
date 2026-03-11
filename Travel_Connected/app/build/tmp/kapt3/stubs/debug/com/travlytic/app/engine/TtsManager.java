package com.travlytic.app.engine;

@javax.inject.Singleton()
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000H\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u0007\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000b\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\u0002\n\u0002\b\b\n\u0002\u0010\u000e\n\u0002\b\u0002\b\u0007\u0018\u00002\u00020\u0001B\u0011\b\u0007\u0012\b\b\u0001\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\u0002\u0010\u0004J\u0006\u0010\u0014\u001a\u00020\u0015J\b\u0010\u0016\u001a\u00020\u0015H\u0002J\u0006\u0010\u0017\u001a\u00020\u000bJ\u0006\u0010\u0018\u001a\u00020\u0015J\u000e\u0010\u0019\u001a\u00020\u00152\u0006\u0010\u001a\u001a\u00020\u0007J\b\u0010\u001b\u001a\u00020\u0015H\u0002J\u000e\u0010\u001c\u001a\u00020\u00152\u0006\u0010\u001d\u001a\u00020\u001eJ\u0006\u0010\u001f\u001a\u00020\u0015R\u0014\u0010\u0005\u001a\b\u0012\u0004\u0012\u00020\u00070\u0006X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0014\u0010\b\u001a\b\u0012\u0004\u0012\u00020\t0\u0006X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\n\u001a\u00020\u000bX\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u0017\u0010\f\u001a\b\u0012\u0004\u0012\u00020\u00070\r\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000e\u0010\u000fR\u0010\u0010\u0010\u001a\u0004\u0018\u00010\u0011X\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u0017\u0010\u0012\u001a\b\u0012\u0004\u0012\u00020\t0\r\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0013\u0010\u000f\u00a8\u0006 "}, d2 = {"Lcom/travlytic/app/engine/TtsManager;", "", "context", "Landroid/content/Context;", "(Landroid/content/Context;)V", "_progress", "Lkotlinx/coroutines/flow/MutableStateFlow;", "", "_ttsState", "Lcom/travlytic/app/engine/TtsState;", "isInitialized", "", "progress", "Lkotlinx/coroutines/flow/StateFlow;", "getProgress", "()Lkotlinx/coroutines/flow/StateFlow;", "tts", "Landroid/speech/tts/TextToSpeech;", "ttsState", "getTtsState", "destroy", "", "initialize", "isSpeaking", "pause", "setSpeechRate", "rate", "setupProgressListener", "speak", "text", "", "stop", "app_debug"})
public final class TtsManager {
    @org.jetbrains.annotations.NotNull()
    private final android.content.Context context = null;
    @org.jetbrains.annotations.Nullable()
    private android.speech.tts.TextToSpeech tts;
    private boolean isInitialized = false;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<com.travlytic.app.engine.TtsState> _ttsState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<com.travlytic.app.engine.TtsState> ttsState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<java.lang.Float> _progress = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<java.lang.Float> progress = null;
    
    @javax.inject.Inject()
    public TtsManager(@dagger.hilt.android.qualifiers.ApplicationContext()
    @org.jetbrains.annotations.NotNull()
    android.content.Context context) {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<com.travlytic.app.engine.TtsState> getTtsState() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<java.lang.Float> getProgress() {
        return null;
    }
    
    private final void initialize() {
    }
    
    private final void setupProgressListener() {
    }
    
    /**
     * Lee el texto en voz alta.
     * @param text Texto a leer (puede ser largo, TTS lo maneja en chunks)
     */
    public final void speak(@org.jetbrains.annotations.NotNull()
    java.lang.String text) {
    }
    
    /**
     * Pausa la reproducción
     */
    public final void pause() {
    }
    
    /**
     * Detiene completamente
     */
    public final void stop() {
    }
    
    /**
     * Cambia velocidad de habla
     */
    public final void setSpeechRate(float rate) {
    }
    
    public final boolean isSpeaking() {
        return false;
    }
    
    public final void destroy() {
    }
}