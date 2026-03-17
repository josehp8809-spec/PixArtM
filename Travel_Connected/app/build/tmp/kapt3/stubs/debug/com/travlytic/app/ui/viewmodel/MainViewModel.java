package com.travlytic.app.ui.viewmodel;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\u00d0\u0001\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0010\u000b\n\u0002\b\u001d\n\u0002\u0018\u0002\n\u0002\b\b\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0006\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0004\n\u0002\u0010\u0002\n\u0002\b\t\n\u0002\u0018\u0002\n\u0002\b\t\n\u0002\u0018\u0002\n\u0002\b\u0011\n\u0002\u0018\u0002\n\u0002\b\u0011\n\u0002\u0010\"\n\u0002\b\u0003\n\u0002\u0010\u0007\n\u0002\b\u0010\n\u0002\u0018\u0002\n\u0000\b\u0007\u0018\u00002\u00020\u0001BQ\b\u0007\u0012\b\b\u0001\u0010\u0002\u001a\u00020\u0003\u0012\u0006\u0010\u0004\u001a\u00020\u0005\u0012\u0006\u0010\u0006\u001a\u00020\u0007\u0012\u0006\u0010\b\u001a\u00020\t\u0012\u0006\u0010\n\u001a\u00020\u000b\u0012\u0006\u0010\f\u001a\u00020\r\u0012\u0006\u0010\u000e\u001a\u00020\u000f\u0012\u0006\u0010\u0010\u001a\u00020\u0011\u0012\u0006\u0010\u0012\u001a\u00020\u0013\u00a2\u0006\u0002\u0010\u0014J&\u0010S\u001a\u00020T2\u0006\u0010U\u001a\u00020V2\u0006\u0010W\u001a\u00020V2\u0006\u0010X\u001a\u00020V2\u0006\u0010Y\u001a\u00020VJ \u0010Z\u001a\u00020[2\u0006\u0010\\\u001a\u00020\u00192\u0006\u0010]\u001a\u00020\u00192\b\u0010^\u001a\u0004\u0018\u00010\u0019J\u0006\u0010_\u001a\u00020[J\u0006\u0010`\u001a\u00020[J\u0006\u0010a\u001a\u00020[J\u0006\u0010b\u001a\u00020[J\u000e\u0010c\u001a\u00020[2\u0006\u0010d\u001a\u00020eJ\u000e\u0010f\u001a\u00020[2\u0006\u0010g\u001a\u00020JJ\u0006\u0010h\u001a\u00020[J\u0006\u0010i\u001a\u00020[J\u0006\u0010j\u001a\u00020[J\u000e\u0010k\u001a\u00020[2\u0006\u0010l\u001a\u00020\u0019J\u0016\u0010m\u001a\u00020[2\u0006\u0010n\u001a\u00020o2\u0006\u0010p\u001a\u00020\u0019J\u0010\u0010q\u001a\u00020\"2\u0006\u0010r\u001a\u00020@H\u0002J\u0006\u0010s\u001a\u00020\"J\b\u0010t\u001a\u00020[H\u0002J\b\u0010u\u001a\u00020[H\u0002J\b\u0010v\u001a\u00020[H\u0002J\b\u0010w\u001a\u00020[H\u0002J\b\u0010x\u001a\u00020[H\u0002J\b\u0010y\u001a\u00020[H\u0014J\u000e\u0010z\u001a\u00020[2\u0006\u0010\u0002\u001a\u00020\u0003J\u000e\u0010{\u001a\u00020T2\u0006\u0010|\u001a\u00020VJ\u0006\u0010}\u001a\u00020[J\u0006\u0010~\u001a\u00020[J\u0010\u0010\u007f\u001a\u00020[2\b\u0010\u0080\u0001\u001a\u00030\u0081\u0001J\u0010\u0010\u0082\u0001\u001a\u00020[2\u0007\u0010\u0083\u0001\u001a\u00020\"J\u0010\u0010\u0084\u0001\u001a\u00020[2\u0007\u0010\u0085\u0001\u001a\u00020\u0019J\u0010\u0010\u0086\u0001\u001a\u00020[2\u0007\u0010\u0085\u0001\u001a\u00020\u0019J\u0010\u0010\u0087\u0001\u001a\u00020[2\u0007\u0010\u0088\u0001\u001a\u00020\u0019J\u0010\u0010\u0089\u0001\u001a\u00020[2\u0007\u0010\u0083\u0001\u001a\u00020\"J\"\u0010\u008a\u0001\u001a\u00020[2\u0007\u0010\u008b\u0001\u001a\u00020\u00192\u0007\u0010\u008c\u0001\u001a\u00020\u00192\u0007\u0010\u008d\u0001\u001a\u00020\u0019J\u0010\u0010\u008e\u0001\u001a\u00020[2\u0007\u0010\u008f\u0001\u001a\u00020\u0019J\u0010\u0010\u0090\u0001\u001a\u00020[2\u0007\u0010\u0085\u0001\u001a\u00020\u0019J\u0017\u0010\u0091\u0001\u001a\u00020T2\u000e\u0010\u0092\u0001\u001a\t\u0012\u0004\u0012\u00020V0\u0093\u0001J\u0010\u0010\u0094\u0001\u001a\u00020T2\u0007\u0010\u0083\u0001\u001a\u00020\"J\u0011\u0010\u0095\u0001\u001a\u00020[2\b\u0010\u0096\u0001\u001a\u00030\u0097\u0001J\u0010\u0010\u0098\u0001\u001a\u00020[2\u0007\u0010\u0099\u0001\u001a\u00020\u0019J\u0012\u0010\u009a\u0001\u001a\u00020[2\u0007\u0010\u0085\u0001\u001a\u00020\u0019H\u0002J\u0007\u0010\u009b\u0001\u001a\u00020[J\u0007\u0010\u009c\u0001\u001a\u00020[J\u0010\u0010\u009d\u0001\u001a\u00020[2\u0007\u0010\u0085\u0001\u001a\u00020\u0019J\u0010\u0010\u009e\u0001\u001a\u00020[2\u0007\u0010\u0083\u0001\u001a\u00020\"J\u0010\u0010\u009f\u0001\u001a\u00020T2\u0007\u0010\u0083\u0001\u001a\u00020\"J\u0010\u0010\u00a0\u0001\u001a\u00020T2\u0007\u0010\u0083\u0001\u001a\u00020\"J\u0010\u0010\u00a1\u0001\u001a\u00020T2\u0007\u0010\u0083\u0001\u001a\u00020\"J\u0018\u0010\u00a2\u0001\u001a\u00020[2\u0006\u0010d\u001a\u00020e2\u0007\u0010\u0083\u0001\u001a\u00020\"J\u0010\u0010\u00a3\u0001\u001a\u00020T2\u0007\u0010\u00a4\u0001\u001a\u00020VJ\u000f\u0010\u00a5\u0001\u001a\u00020[2\u0006\u0010g\u001a\u00020JJ\u0019\u0010\u00a6\u0001\u001a\u00020T2\u0006\u0010|\u001a\u00020V2\b\u0010\u00a7\u0001\u001a\u00030\u00a8\u0001R\u0014\u0010\u0015\u001a\b\u0012\u0004\u0012\u00020\u00170\u0016X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0016\u0010\u0018\u001a\n\u0012\u0006\u0012\u0004\u0018\u00010\u00190\u0016X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0014\u0010\u001a\u001a\b\u0012\u0004\u0012\u00020\u001b0\u0016X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0014\u0010\u001c\u001a\b\u0012\u0004\u0012\u00020\u001d0\u0016X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0014\u0010\u001e\u001a\b\u0012\u0004\u0012\u00020\u001f0\u0016X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0004\u001a\u00020\u0005X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0017\u0010 \u001a\b\u0012\u0004\u0012\u00020\"0!\u00a2\u0006\b\n\u0000\u001a\u0004\b#\u0010$R\u0017\u0010%\u001a\b\u0012\u0004\u0012\u00020\u00190!\u00a2\u0006\b\n\u0000\u001a\u0004\b&\u0010$R\u0017\u0010\'\u001a\b\u0012\u0004\u0012\u00020\"0!\u00a2\u0006\b\n\u0000\u001a\u0004\b(\u0010$R\u0017\u0010)\u001a\b\u0012\u0004\u0012\u00020\"0!\u00a2\u0006\b\n\u0000\u001a\u0004\b*\u0010$R\u0017\u0010+\u001a\b\u0012\u0004\u0012\u00020\"0!\u00a2\u0006\b\n\u0000\u001a\u0004\b,\u0010$R\u0017\u0010-\u001a\b\u0012\u0004\u0012\u00020\"0!\u00a2\u0006\b\n\u0000\u001a\u0004\b.\u0010$R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0017\u0010/\u001a\b\u0012\u0004\u0012\u00020\u00170!\u00a2\u0006\b\n\u0000\u001a\u0004\b0\u0010$R\u000e\u0010\b\u001a\u00020\tX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0017\u00101\u001a\b\u0012\u0004\u0012\u00020\u00190!\u00a2\u0006\b\n\u0000\u001a\u0004\b2\u0010$R\u0019\u00103\u001a\n\u0012\u0006\u0012\u0004\u0018\u00010\u00190!\u00a2\u0006\b\n\u0000\u001a\u0004\b4\u0010$R\u000e\u0010\u000e\u001a\u00020\u000fX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0017\u00105\u001a\b\u0012\u0004\u0012\u00020\u00190!\u00a2\u0006\b\n\u0000\u001a\u0004\b6\u0010$R\u0017\u00107\u001a\b\u0012\u0004\u0012\u00020\"0!\u00a2\u0006\b\n\u0000\u001a\u0004\b8\u0010$R\u000e\u0010\u0006\u001a\u00020\u0007X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0017\u00109\u001a\b\u0012\u0004\u0012\u00020\u00190!\u00a2\u0006\b\n\u0000\u001a\u0004\b:\u0010$R\u0017\u0010;\u001a\b\u0012\u0004\u0012\u00020\u00190!\u00a2\u0006\b\n\u0000\u001a\u0004\b<\u0010$R\u0017\u0010=\u001a\b\u0012\u0004\u0012\u00020\u00190!\u00a2\u0006\b\n\u0000\u001a\u0004\b>\u0010$R\u000e\u0010\n\u001a\u00020\u000bX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0017\u0010?\u001a\b\u0012\u0004\u0012\u00020@0!\u00a2\u0006\b\n\u0000\u001a\u0004\bA\u0010$R\u000e\u0010\u0010\u001a\u00020\u0011X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0017\u0010B\u001a\b\u0012\u0004\u0012\u00020\u001b0!\u00a2\u0006\b\n\u0000\u001a\u0004\bC\u0010$R\u0017\u0010D\u001a\b\u0012\u0004\u0012\u00020\u00190!\u00a2\u0006\b\n\u0000\u001a\u0004\bE\u0010$R\u0017\u0010F\u001a\b\u0012\u0004\u0012\u00020\u001d0!\u00a2\u0006\b\n\u0000\u001a\u0004\bG\u0010$R\u000e\u0010\f\u001a\u00020\rX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u001d\u0010H\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020J0I0!\u00a2\u0006\b\n\u0000\u001a\u0004\bK\u0010$R\u000e\u0010\u0012\u001a\u00020\u0013X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0017\u0010L\u001a\b\u0012\u0004\u0012\u00020M0!\u00a2\u0006\b\n\u0000\u001a\u0004\bN\u0010$R\u0017\u0010O\u001a\b\u0012\u0004\u0012\u00020\u001f0!\u00a2\u0006\b\n\u0000\u001a\u0004\bP\u0010$R\u0017\u0010Q\u001a\b\u0012\u0004\u0012\u00020\u00190!\u00a2\u0006\b\n\u0000\u001a\u0004\bR\u0010$\u00a8\u0006\u00a9\u0001"}, d2 = {"Lcom/travlytic/app/ui/viewmodel/MainViewModel;", "Landroidx/lifecycle/ViewModel;", "context", "Landroid/content/Context;", "appPreferences", "Lcom/travlytic/app/data/prefs/AppPreferences;", "knowledgeRepository", "Lcom/travlytic/app/data/repository/KnowledgeRepository;", "escalationLogDao", "Lcom/travlytic/app/data/db/dao/EscalationLogDao;", "responseLogDao", "Lcom/travlytic/app/data/db/dao/ResponseLogDao;", "trainingRuleDao", "Lcom/travlytic/app/data/db/dao/TrainingRuleDao;", "geminiAgent", "Lcom/travlytic/app/engine/GeminiAgent;", "summaryGenerator", "Lcom/travlytic/app/engine/SummaryGenerator;", "ttsManager", "Lcom/travlytic/app/engine/TtsManager;", "(Landroid/content/Context;Lcom/travlytic/app/data/prefs/AppPreferences;Lcom/travlytic/app/data/repository/KnowledgeRepository;Lcom/travlytic/app/data/db/dao/EscalationLogDao;Lcom/travlytic/app/data/db/dao/ResponseLogDao;Lcom/travlytic/app/data/db/dao/TrainingRuleDao;Lcom/travlytic/app/engine/GeminiAgent;Lcom/travlytic/app/engine/SummaryGenerator;Lcom/travlytic/app/engine/TtsManager;)V", "_dashboardState", "Lkotlinx/coroutines/flow/MutableStateFlow;", "Lcom/travlytic/app/ui/viewmodel/DashboardState;", "_exportEvent", "", "_summaryUiState", "Lcom/travlytic/app/ui/viewmodel/SummaryUiState;", "_testMsgState", "Lcom/travlytic/app/ui/viewmodel/TestMessageState;", "_uiState", "Lcom/travlytic/app/ui/viewmodel/UiState;", "autoReminderEnabled", "Lkotlinx/coroutines/flow/StateFlow;", "", "getAutoReminderEnabled", "()Lkotlinx/coroutines/flow/StateFlow;", "autoReminderMessage", "getAutoReminderMessage", "botEnabled", "getBotEnabled", "channelFbMessenger", "getChannelFbMessenger", "channelIgDirect", "getChannelIgDirect", "channelWhatsApp", "getChannelWhatsApp", "dashboardState", "getDashboardState", "escalationMessage", "getEscalationMessage", "exportEvent", "getExportEvent", "geminiApiKey", "getGeminiApiKey", "internetSearchEnabled", "getInternetSearchEnabled", "profileBusinessName", "getProfileBusinessName", "profileTone", "getProfileTone", "profileUserName", "getProfileUserName", "scheduleState", "Lcom/travlytic/app/ui/viewmodel/ScheduleState;", "getScheduleState", "summaryUiState", "getSummaryUiState", "systemPrompt", "getSystemPrompt", "testMsgState", "getTestMsgState", "trainingRules", "", "Lcom/travlytic/app/data/db/entities/TrainingRule;", "getTrainingRules", "ttsState", "Lcom/travlytic/app/engine/TtsState;", "getTtsState", "uiState", "getUiState", "welcomeMessage", "getWelcomeMessage", "addScheduleRange", "Lkotlinx/coroutines/Job;", "startH", "", "startM", "endH", "endM", "addTrainingRule", "", "type", "input", "output", "clearExportEvent", "clearLogs", "clearSnackbar", "clearTestMessage", "deleteKnowledgeItem", "item", "Lcom/travlytic/app/data/db/entities/KnowledgeItem;", "deleteTrainingRule", "rule", "exportConfiguration", "forceSync", "generateSummary", "importConfiguration", "jsonString", "importExcelKnowledge", "uri", "Landroid/net/Uri;", "reference", "isInsideSchedule", "state", "isNotificationListenerEnabled", "observeDashboard", "observeEscalationLogs", "observeKnowledgeItems", "observeRecentLogs", "observeServiceStatus", "onCleared", "openNotificationSettings", "removeScheduleRange", "index", "resetSystemPrompt", "resetToDefaultSettings", "resolveEscalation", "log", "Lcom/travlytic/app/data/db/entities/EscalationLog;", "saveAutoReminderEnabled", "enabled", "saveAutoReminderMessage", "message", "saveEscalationMessage", "saveGeminiApiKey", "key", "saveInternetSearchEnabled", "saveProfileInfo", "userName", "businessName", "tone", "saveSystemPrompt", "prompt", "saveWelcomeMessage", "setScheduleDays", "days", "", "setScheduleEnabled", "setSpeechRate", "rate", "", "setSummaryPeriod", "period", "showSnackbar", "speakSummary", "stopSpeaking", "testMessage", "toggleBot", "toggleChannelFbMessenger", "toggleChannelIgDirect", "toggleChannelWhatsApp", "toggleKnowledgeItem", "toggleScheduleDay", "day", "toggleTrainingRule", "updateScheduleRange", "range", "Lcom/travlytic/app/data/model/TimeRange;", "app_debug"})
@dagger.hilt.android.lifecycle.HiltViewModel()
public final class MainViewModel extends androidx.lifecycle.ViewModel {
    @org.jetbrains.annotations.NotNull()
    private final android.content.Context context = null;
    @org.jetbrains.annotations.NotNull()
    private final com.travlytic.app.data.prefs.AppPreferences appPreferences = null;
    @org.jetbrains.annotations.NotNull()
    private final com.travlytic.app.data.repository.KnowledgeRepository knowledgeRepository = null;
    @org.jetbrains.annotations.NotNull()
    private final com.travlytic.app.data.db.dao.EscalationLogDao escalationLogDao = null;
    @org.jetbrains.annotations.NotNull()
    private final com.travlytic.app.data.db.dao.ResponseLogDao responseLogDao = null;
    @org.jetbrains.annotations.NotNull()
    private final com.travlytic.app.data.db.dao.TrainingRuleDao trainingRuleDao = null;
    @org.jetbrains.annotations.NotNull()
    private final com.travlytic.app.engine.GeminiAgent geminiAgent = null;
    @org.jetbrains.annotations.NotNull()
    private final com.travlytic.app.engine.SummaryGenerator summaryGenerator = null;
    @org.jetbrains.annotations.NotNull()
    private final com.travlytic.app.engine.TtsManager ttsManager = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<com.travlytic.app.ui.viewmodel.UiState> _uiState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<com.travlytic.app.ui.viewmodel.UiState> uiState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<com.travlytic.app.ui.viewmodel.SummaryUiState> _summaryUiState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<com.travlytic.app.ui.viewmodel.SummaryUiState> summaryUiState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<com.travlytic.app.engine.TtsState> ttsState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<java.lang.String> geminiApiKey = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<java.lang.String> systemPrompt = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<java.lang.String> welcomeMessage = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<java.lang.String> escalationMessage = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<java.lang.Boolean> autoReminderEnabled = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<java.lang.String> autoReminderMessage = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<java.lang.Boolean> botEnabled = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<java.lang.Boolean> internetSearchEnabled = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<java.lang.String> profileUserName = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<java.lang.String> profileBusinessName = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<java.lang.String> profileTone = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<java.lang.Boolean> channelWhatsApp = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<java.lang.Boolean> channelFbMessenger = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<java.lang.Boolean> channelIgDirect = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<com.travlytic.app.ui.viewmodel.ScheduleState> scheduleState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<com.travlytic.app.ui.viewmodel.DashboardState> _dashboardState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<com.travlytic.app.ui.viewmodel.DashboardState> dashboardState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<com.travlytic.app.ui.viewmodel.TestMessageState> _testMsgState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<com.travlytic.app.ui.viewmodel.TestMessageState> testMsgState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<java.util.List<com.travlytic.app.data.db.entities.TrainingRule>> trainingRules = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<java.lang.String> _exportEvent = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<java.lang.String> exportEvent = null;
    
    @javax.inject.Inject()
    public MainViewModel(@dagger.hilt.android.qualifiers.ApplicationContext()
    @org.jetbrains.annotations.NotNull()
    android.content.Context context, @org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.prefs.AppPreferences appPreferences, @org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.repository.KnowledgeRepository knowledgeRepository, @org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.dao.EscalationLogDao escalationLogDao, @org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.dao.ResponseLogDao responseLogDao, @org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.dao.TrainingRuleDao trainingRuleDao, @org.jetbrains.annotations.NotNull()
    com.travlytic.app.engine.GeminiAgent geminiAgent, @org.jetbrains.annotations.NotNull()
    com.travlytic.app.engine.SummaryGenerator summaryGenerator, @org.jetbrains.annotations.NotNull()
    com.travlytic.app.engine.TtsManager ttsManager) {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<com.travlytic.app.ui.viewmodel.UiState> getUiState() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<com.travlytic.app.ui.viewmodel.SummaryUiState> getSummaryUiState() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<com.travlytic.app.engine.TtsState> getTtsState() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<java.lang.String> getGeminiApiKey() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<java.lang.String> getSystemPrompt() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<java.lang.String> getWelcomeMessage() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<java.lang.String> getEscalationMessage() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<java.lang.Boolean> getAutoReminderEnabled() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<java.lang.String> getAutoReminderMessage() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<java.lang.Boolean> getBotEnabled() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<java.lang.Boolean> getInternetSearchEnabled() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<java.lang.String> getProfileUserName() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<java.lang.String> getProfileBusinessName() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<java.lang.String> getProfileTone() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<java.lang.Boolean> getChannelWhatsApp() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<java.lang.Boolean> getChannelFbMessenger() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<java.lang.Boolean> getChannelIgDirect() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<com.travlytic.app.ui.viewmodel.ScheduleState> getScheduleState() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<com.travlytic.app.ui.viewmodel.DashboardState> getDashboardState() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<com.travlytic.app.ui.viewmodel.TestMessageState> getTestMsgState() {
        return null;
    }
    
    private final void observeEscalationLogs() {
    }
    
    private final void observeKnowledgeItems() {
    }
    
    private final void observeRecentLogs() {
    }
    
    private final void observeServiceStatus() {
    }
    
    private final boolean isInsideSchedule(com.travlytic.app.ui.viewmodel.ScheduleState state) {
        return false;
    }
    
    private final void observeDashboard() {
    }
    
    public final void testMessage(@org.jetbrains.annotations.NotNull()
    java.lang.String message) {
    }
    
    public final void clearTestMessage() {
    }
    
    public final void resolveEscalation(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.entities.EscalationLog log) {
    }
    
    public final void importExcelKnowledge(@org.jetbrains.annotations.NotNull()
    android.net.Uri uri, @org.jetbrains.annotations.NotNull()
    java.lang.String reference) {
    }
    
    public final void toggleKnowledgeItem(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.entities.KnowledgeItem item, boolean enabled) {
    }
    
    public final void deleteKnowledgeItem(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.entities.KnowledgeItem item) {
    }
    
    public final void forceSync() {
    }
    
    public final void saveWelcomeMessage(@org.jetbrains.annotations.NotNull()
    java.lang.String message) {
    }
    
    public final void saveEscalationMessage(@org.jetbrains.annotations.NotNull()
    java.lang.String message) {
    }
    
    public final void saveAutoReminderEnabled(boolean enabled) {
    }
    
    public final void saveAutoReminderMessage(@org.jetbrains.annotations.NotNull()
    java.lang.String message) {
    }
    
    public final void saveInternetSearchEnabled(boolean enabled) {
    }
    
    public final void resetToDefaultSettings() {
    }
    
    public final void clearLogs() {
    }
    
    public final void toggleBot(boolean enabled) {
    }
    
    public final void openNotificationSettings(@org.jetbrains.annotations.NotNull()
    android.content.Context context) {
    }
    
    public final void saveGeminiApiKey(@org.jetbrains.annotations.NotNull()
    java.lang.String key) {
    }
    
    public final void saveSystemPrompt(@org.jetbrains.annotations.NotNull()
    java.lang.String prompt) {
    }
    
    public final void resetSystemPrompt() {
    }
    
    public final void saveProfileInfo(@org.jetbrains.annotations.NotNull()
    java.lang.String userName, @org.jetbrains.annotations.NotNull()
    java.lang.String businessName, @org.jetbrains.annotations.NotNull()
    java.lang.String tone) {
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.Job toggleChannelWhatsApp(boolean enabled) {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.Job toggleChannelFbMessenger(boolean enabled) {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.Job toggleChannelIgDirect(boolean enabled) {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<java.util.List<com.travlytic.app.data.db.entities.TrainingRule>> getTrainingRules() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<java.lang.String> getExportEvent() {
        return null;
    }
    
    public final void clearExportEvent() {
    }
    
    public final void addTrainingRule(@org.jetbrains.annotations.NotNull()
    java.lang.String type, @org.jetbrains.annotations.NotNull()
    java.lang.String input, @org.jetbrains.annotations.Nullable()
    java.lang.String output) {
    }
    
    public final void toggleTrainingRule(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.entities.TrainingRule rule) {
    }
    
    public final void deleteTrainingRule(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.entities.TrainingRule rule) {
    }
    
    public final void exportConfiguration() {
    }
    
    public final void importConfiguration(@org.jetbrains.annotations.NotNull()
    java.lang.String jsonString) {
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.Job setScheduleEnabled(boolean enabled) {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.Job addScheduleRange(int startH, int startM, int endH, int endM) {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.Job removeScheduleRange(int index) {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.Job updateScheduleRange(int index, @org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.model.TimeRange range) {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.Job setScheduleDays(@org.jetbrains.annotations.NotNull()
    java.util.Set<java.lang.Integer> days) {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.Job toggleScheduleDay(int day) {
        return null;
    }
    
    public final void generateSummary() {
    }
    
    public final void speakSummary() {
    }
    
    public final void stopSpeaking() {
    }
    
    public final void setSpeechRate(float rate) {
    }
    
    public final void setSummaryPeriod(@org.jetbrains.annotations.NotNull()
    java.lang.String period) {
    }
    
    @java.lang.Override()
    protected void onCleared() {
    }
    
    private final void showSnackbar(java.lang.String message) {
    }
    
    public final void clearSnackbar() {
    }
    
    public final boolean isNotificationListenerEnabled() {
        return false;
    }
}