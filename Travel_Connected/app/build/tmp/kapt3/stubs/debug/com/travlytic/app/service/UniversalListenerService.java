package com.travlytic.app.service;

@dagger.hilt.android.AndroidEntryPoint()
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000|\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\t\n\u0002\b\u0002\n\u0002\u0010%\n\u0002\u0010\u000e\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0005\n\u0002\u0018\u0002\n\u0002\b\u0005\n\u0002\u0018\u0002\n\u0002\b\u0005\n\u0002\u0018\u0002\n\u0002\u0010\b\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0005\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u0000\n\u0002\u0010$\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u0002\n\u0000\n\u0002\u0010\u000b\n\u0002\b\u0007\n\u0002\u0018\u0002\n\u0002\b\u0006\b\u0007\u0018\u00002\u00020\u0001B\u0005\u00a2\u0006\u0002\u0010\u0002J\b\u0010,\u001a\u00020-H\u0002J\b\u0010.\u001a\u00020/H\u0002J\u000e\u00100\u001a\u000201H\u0082@\u00a2\u0006\u0002\u00102J\u0010\u00103\u001a\u00020\b2\u0006\u00104\u001a\u00020\bH\u0002J\b\u00105\u001a\u00020/H\u0016J\b\u00106\u001a\u00020/H\u0016J\u0012\u00107\u001a\u00020/2\b\u00108\u001a\u0004\u0018\u000109H\u0016J\u0018\u0010:\u001a\u0002012\u0006\u00108\u001a\u0002092\u0006\u0010;\u001a\u00020\bH\u0002J\u0018\u0010<\u001a\u00020/2\u0006\u0010=\u001a\u00020\b2\u0006\u0010>\u001a\u00020\bH\u0002R\u000e\u0010\u0003\u001a\u00020\u0004X\u0082D\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0005\u001a\u00020\u0004X\u0082D\u00a2\u0006\u0002\n\u0000R\u001a\u0010\u0006\u001a\u000e\u0012\u0004\u0012\u00020\b\u0012\u0004\u0012\u00020\t0\u0007X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u001e\u0010\n\u001a\u00020\u000b8\u0006@\u0006X\u0087.\u00a2\u0006\u000e\n\u0000\u001a\u0004\b\f\u0010\r\"\u0004\b\u000e\u0010\u000fR\u001e\u0010\u0010\u001a\u00020\u00118\u0006@\u0006X\u0087.\u00a2\u0006\u000e\n\u0000\u001a\u0004\b\u0012\u0010\u0013\"\u0004\b\u0014\u0010\u0015R\u001e\u0010\u0016\u001a\u00020\u00178\u0006@\u0006X\u0087.\u00a2\u0006\u000e\n\u0000\u001a\u0004\b\u0018\u0010\u0019\"\u0004\b\u001a\u0010\u001bR\u001a\u0010\u001c\u001a\u000e\u0012\u0004\u0012\u00020\u001e\u0012\u0004\u0012\u00020\u00040\u001dX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u001a\u0010\u001f\u001a\u000e\u0012\u0004\u0012\u00020\b\u0012\u0004\u0012\u00020\u00040\u0007X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u001e\u0010 \u001a\u00020!8\u0006@\u0006X\u0087.\u00a2\u0006\u000e\n\u0000\u001a\u0004\b\"\u0010#\"\u0004\b$\u0010%R\u000e\u0010&\u001a\u00020\'X\u0082\u0004\u00a2\u0006\u0002\n\u0000RN\u0010(\u001aB\u0012\f\u0012\n )*\u0004\u0018\u00010\b0\b\u0012\f\u0012\n )*\u0004\u0018\u00010*0* )* \u0012\f\u0012\n )*\u0004\u0018\u00010\b0\b\u0012\f\u0012\n )*\u0004\u0018\u00010*0*\u0018\u00010+0\u0007X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006?"}, d2 = {"Lcom/travlytic/app/service/UniversalListenerService;", "Landroid/service/notification/NotificationListenerService;", "()V", "ANTI_LOOP_COOLDOWN_MS", "", "REPLY_COOLDOWN_MS", "activeReminders", "", "", "Lkotlinx/coroutines/Job;", "appPreferences", "Lcom/travlytic/app/data/prefs/AppPreferences;", "getAppPreferences", "()Lcom/travlytic/app/data/prefs/AppPreferences;", "setAppPreferences", "(Lcom/travlytic/app/data/prefs/AppPreferences;)V", "escalationLogDao", "Lcom/travlytic/app/data/db/dao/EscalationLogDao;", "getEscalationLogDao", "()Lcom/travlytic/app/data/db/dao/EscalationLogDao;", "setEscalationLogDao", "(Lcom/travlytic/app/data/db/dao/EscalationLogDao;)V", "geminiAgent", "Lcom/travlytic/app/engine/GeminiAgent;", "getGeminiAgent", "()Lcom/travlytic/app/engine/GeminiAgent;", "setGeminiAgent", "(Lcom/travlytic/app/engine/GeminiAgent;)V", "recentResponseHashes", "Ljava/util/LinkedHashMap;", "", "recentlyReplied", "responseLogDao", "Lcom/travlytic/app/data/db/dao/ResponseLogDao;", "getResponseLogDao", "()Lcom/travlytic/app/data/db/dao/ResponseLogDao;", "setResponseLogDao", "(Lcom/travlytic/app/data/db/dao/ResponseLogDao;)V", "serviceScope", "Lkotlinx/coroutines/CoroutineScope;", "welcomeMutexMap", "kotlin.jvm.PlatformType", "", "", "buildForegroundNotification", "Landroid/app/Notification;", "createNotificationChannel", "", "isWithinSchedule", "", "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "normalizeForAntiLoop", "text", "onCreate", "onDestroy", "onNotificationPosted", "sbn", "Landroid/service/notification/StatusBarNotification;", "sendUniversalReply", "replyText", "showLocalEscalationNotification", "contact", "message", "app_debug"})
public final class UniversalListenerService extends android.service.notification.NotificationListenerService {
    @javax.inject.Inject()
    public com.travlytic.app.engine.GeminiAgent geminiAgent;
    @javax.inject.Inject()
    public com.travlytic.app.data.db.dao.ResponseLogDao responseLogDao;
    @javax.inject.Inject()
    public com.travlytic.app.data.db.dao.EscalationLogDao escalationLogDao;
    @javax.inject.Inject()
    public com.travlytic.app.data.prefs.AppPreferences appPreferences;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.CoroutineScope serviceScope = null;
    @org.jetbrains.annotations.NotNull()
    private final java.util.Map<java.lang.String, java.lang.Long> recentlyReplied = null;
    private final long REPLY_COOLDOWN_MS = 2000L;
    private final java.util.Map<java.lang.String, java.lang.Object> welcomeMutexMap = null;
    @org.jetbrains.annotations.NotNull()
    private final java.util.LinkedHashMap<java.lang.Integer, java.lang.Long> recentResponseHashes = null;
    private final long ANTI_LOOP_COOLDOWN_MS = 45000L;
    @org.jetbrains.annotations.NotNull()
    private final java.util.Map<java.lang.String, kotlinx.coroutines.Job> activeReminders = null;
    
    public UniversalListenerService() {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.travlytic.app.engine.GeminiAgent getGeminiAgent() {
        return null;
    }
    
    public final void setGeminiAgent(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.engine.GeminiAgent p0) {
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.travlytic.app.data.db.dao.ResponseLogDao getResponseLogDao() {
        return null;
    }
    
    public final void setResponseLogDao(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.dao.ResponseLogDao p0) {
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.travlytic.app.data.db.dao.EscalationLogDao getEscalationLogDao() {
        return null;
    }
    
    public final void setEscalationLogDao(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.dao.EscalationLogDao p0) {
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.travlytic.app.data.prefs.AppPreferences getAppPreferences() {
        return null;
    }
    
    public final void setAppPreferences(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.prefs.AppPreferences p0) {
    }
    
    /**
     * Limpia el texto de prefijos de autoría comunes que generan bucles
     */
    private final java.lang.String normalizeForAntiLoop(java.lang.String text) {
        return null;
    }
    
    @java.lang.Override()
    public void onCreate() {
    }
    
    @java.lang.Override()
    public void onDestroy() {
    }
    
    @java.lang.Override()
    public void onNotificationPosted(@org.jetbrains.annotations.Nullable()
    android.service.notification.StatusBarNotification sbn) {
    }
    
    private final boolean sendUniversalReply(android.service.notification.StatusBarNotification sbn, java.lang.String replyText) {
        return false;
    }
    
    private final void showLocalEscalationNotification(java.lang.String contact, java.lang.String message) {
    }
    
    private final void createNotificationChannel() {
    }
    
    private final android.app.Notification buildForegroundNotification() {
        return null;
    }
    
    private final java.lang.Object isWithinSchedule(kotlin.coroutines.Continuation<? super java.lang.Boolean> $completion) {
        return null;
    }
}