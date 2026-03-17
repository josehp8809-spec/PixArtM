package com.travlytic.app.engine;

@javax.inject.Singleton()
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000H\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0002\b\u0003\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0002\b\u0006\n\u0002\u0010\u000b\n\u0002\b\u0006\n\u0002\u0010\u0012\n\u0002\b\u0002\b\u0007\u0018\u00002\u00020\u0001B\u001f\b\u0007\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\u0006\u0010\u0004\u001a\u00020\u0005\u0012\u0006\u0010\u0006\u001a\u00020\u0007\u00a2\u0006\u0002\u0010\bJf\u0010\u000b\u001a\u00020\f2\u0006\u0010\r\u001a\u00020\f2\u0006\u0010\u000e\u001a\u00020\f2\f\u0010\u000f\u001a\b\u0012\u0004\u0012\u00020\u00110\u00102\u0006\u0010\u0012\u001a\u00020\f2\u0006\u0010\u0013\u001a\u00020\f2\u0006\u0010\u0014\u001a\u00020\f2\u0006\u0010\u0015\u001a\u00020\f2\u0006\u0010\u0016\u001a\u00020\f2\u0006\u0010\u0017\u001a\u00020\u00182\u0006\u0010\u0019\u001a\u00020\u00182\u0006\u0010\u001a\u001a\u00020\u0018H\u0002Jn\u0010\u001b\u001a\u0004\u0018\u00010\f2\u0006\u0010\u001c\u001a\u00020\f2\u0006\u0010\u001d\u001a\u00020\f2\u0006\u0010\u0012\u001a\u00020\f2\u0006\u0010\u0013\u001a\u00020\f2\b\b\u0002\u0010\u0014\u001a\u00020\f2\b\b\u0002\u0010\u0015\u001a\u00020\f2\b\b\u0002\u0010\u0016\u001a\u00020\f2\n\b\u0002\u0010\u001e\u001a\u0004\u0018\u00010\u001f2\b\b\u0002\u0010\u0019\u001a\u00020\u00182\b\b\u0002\u0010\u001a\u001a\u00020\u0018H\u0086@\u00a2\u0006\u0002\u0010 R\u000e\u0010\t\u001a\u00020\nX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0006\u001a\u00020\u0007X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0004\u001a\u00020\u0005X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006!"}, d2 = {"Lcom/travlytic/app/engine/GeminiAgent;", "", "knowledgeRepository", "Lcom/travlytic/app/data/repository/KnowledgeRepository;", "trainingRuleDao", "Lcom/travlytic/app/data/db/dao/TrainingRuleDao;", "responseLogDao", "Lcom/travlytic/app/data/db/dao/ResponseLogDao;", "(Lcom/travlytic/app/data/repository/KnowledgeRepository;Lcom/travlytic/app/data/db/dao/TrainingRuleDao;Lcom/travlytic/app/data/db/dao/ResponseLogDao;)V", "gson", "Lcom/google/gson/Gson;", "buildPrompt", "", "userSystemPrompt", "sheetContext", "activeRules", "", "Lcom/travlytic/app/data/db/entities/TrainingRule;", "contactName", "userMessage", "userName", "businessName", "tone", "hasAudio", "", "internetSearchEnabled", "isFirstInteraction", "generateResponse", "apiKey", "systemPrompt", "audioData", "", "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;[BZZLkotlin/coroutines/Continuation;)Ljava/lang/Object;", "app_debug"})
public final class GeminiAgent {
    @org.jetbrains.annotations.NotNull()
    private final com.travlytic.app.data.repository.KnowledgeRepository knowledgeRepository = null;
    @org.jetbrains.annotations.NotNull()
    private final com.travlytic.app.data.db.dao.TrainingRuleDao trainingRuleDao = null;
    @org.jetbrains.annotations.NotNull()
    private final com.travlytic.app.data.db.dao.ResponseLogDao responseLogDao = null;
    @org.jetbrains.annotations.NotNull()
    private final com.google.gson.Gson gson = null;
    
    @javax.inject.Inject()
    public GeminiAgent(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.repository.KnowledgeRepository knowledgeRepository, @org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.dao.TrainingRuleDao trainingRuleDao, @org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.dao.ResponseLogDao responseLogDao) {
        super();
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object generateResponse(@org.jetbrains.annotations.NotNull()
    java.lang.String apiKey, @org.jetbrains.annotations.NotNull()
    java.lang.String systemPrompt, @org.jetbrains.annotations.NotNull()
    java.lang.String contactName, @org.jetbrains.annotations.NotNull()
    java.lang.String userMessage, @org.jetbrains.annotations.NotNull()
    java.lang.String userName, @org.jetbrains.annotations.NotNull()
    java.lang.String businessName, @org.jetbrains.annotations.NotNull()
    java.lang.String tone, @org.jetbrains.annotations.Nullable()
    byte[] audioData, boolean internetSearchEnabled, boolean isFirstInteraction, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.lang.String> $completion) {
        return null;
    }
    
    private final java.lang.String buildPrompt(java.lang.String userSystemPrompt, java.lang.String sheetContext, java.util.List<com.travlytic.app.data.db.entities.TrainingRule> activeRules, java.lang.String contactName, java.lang.String userMessage, java.lang.String userName, java.lang.String businessName, java.lang.String tone, boolean hasAudio, boolean internetSearchEnabled, boolean isFirstInteraction) {
        return null;
    }
}