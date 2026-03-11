package com.travlytic.app.engine;

/**
 * Modelo de datos utilizado para Exportar e Importar la configuración del agente en fomato JSON.
 */
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000,\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\b\n\u0000\n\u0002\u0010\u000e\n\u0002\b\u0004\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0002\b\u0012\n\u0002\u0010\u000b\n\u0002\b\u0004\b\u0086\b\u0018\u00002\u00020\u0001BI\u0012\b\b\u0002\u0010\u0002\u001a\u00020\u0003\u0012\u0006\u0010\u0004\u001a\u00020\u0005\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0005\u0012\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\u0005\u0012\n\b\u0002\u0010\b\u001a\u0004\u0018\u00010\u0005\u0012\f\u0010\t\u001a\b\u0012\u0004\u0012\u00020\u000b0\n\u00a2\u0006\u0002\u0010\fJ\t\u0010\u0016\u001a\u00020\u0003H\u00c6\u0003J\t\u0010\u0017\u001a\u00020\u0005H\u00c6\u0003J\u000b\u0010\u0018\u001a\u0004\u0018\u00010\u0005H\u00c6\u0003J\u000b\u0010\u0019\u001a\u0004\u0018\u00010\u0005H\u00c6\u0003J\u000b\u0010\u001a\u001a\u0004\u0018\u00010\u0005H\u00c6\u0003J\u000f\u0010\u001b\u001a\b\u0012\u0004\u0012\u00020\u000b0\nH\u00c6\u0003JQ\u0010\u001c\u001a\u00020\u00002\b\b\u0002\u0010\u0002\u001a\u00020\u00032\b\b\u0002\u0010\u0004\u001a\u00020\u00052\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u00052\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\u00052\n\b\u0002\u0010\b\u001a\u0004\u0018\u00010\u00052\u000e\b\u0002\u0010\t\u001a\b\u0012\u0004\u0012\u00020\u000b0\nH\u00c6\u0001J\u0013\u0010\u001d\u001a\u00020\u001e2\b\u0010\u001f\u001a\u0004\u0018\u00010\u0001H\u00d6\u0003J\t\u0010 \u001a\u00020\u0003H\u00d6\u0001J\t\u0010!\u001a\u00020\u0005H\u00d6\u0001R\u0013\u0010\u0007\u001a\u0004\u0018\u00010\u0005\u00a2\u0006\b\n\u0000\u001a\u0004\b\r\u0010\u000eR\u0013\u0010\b\u001a\u0004\u0018\u00010\u0005\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000f\u0010\u000eR\u0013\u0010\u0006\u001a\u0004\u0018\u00010\u0005\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0010\u0010\u000eR\u0011\u0010\u0004\u001a\u00020\u0005\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0011\u0010\u000eR\u0017\u0010\t\u001a\b\u0012\u0004\u0012\u00020\u000b0\n\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0012\u0010\u0013R\u0011\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0014\u0010\u0015\u00a8\u0006\""}, d2 = {"Lcom/travlytic/app/engine/AiConfigExport;", "", "version", "", "systemPrompt", "", "profileUserName", "profileBusinessName", "profileTone", "trainingRules", "", "Lcom/travlytic/app/data/db/entities/TrainingRule;", "(ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/util/List;)V", "getProfileBusinessName", "()Ljava/lang/String;", "getProfileTone", "getProfileUserName", "getSystemPrompt", "getTrainingRules", "()Ljava/util/List;", "getVersion", "()I", "component1", "component2", "component3", "component4", "component5", "component6", "copy", "equals", "", "other", "hashCode", "toString", "app_debug"})
public final class AiConfigExport {
    private final int version = 0;
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String systemPrompt = null;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.String profileUserName = null;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.String profileBusinessName = null;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.String profileTone = null;
    @org.jetbrains.annotations.NotNull()
    private final java.util.List<com.travlytic.app.data.db.entities.TrainingRule> trainingRules = null;
    
    public AiConfigExport(int version, @org.jetbrains.annotations.NotNull()
    java.lang.String systemPrompt, @org.jetbrains.annotations.Nullable()
    java.lang.String profileUserName, @org.jetbrains.annotations.Nullable()
    java.lang.String profileBusinessName, @org.jetbrains.annotations.Nullable()
    java.lang.String profileTone, @org.jetbrains.annotations.NotNull()
    java.util.List<com.travlytic.app.data.db.entities.TrainingRule> trainingRules) {
        super();
    }
    
    public final int getVersion() {
        return 0;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String getSystemPrompt() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String getProfileUserName() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String getProfileBusinessName() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String getProfileTone() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.travlytic.app.data.db.entities.TrainingRule> getTrainingRules() {
        return null;
    }
    
    public final int component1() {
        return 0;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String component2() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String component3() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String component4() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String component5() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.travlytic.app.data.db.entities.TrainingRule> component6() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.travlytic.app.engine.AiConfigExport copy(int version, @org.jetbrains.annotations.NotNull()
    java.lang.String systemPrompt, @org.jetbrains.annotations.Nullable()
    java.lang.String profileUserName, @org.jetbrains.annotations.Nullable()
    java.lang.String profileBusinessName, @org.jetbrains.annotations.Nullable()
    java.lang.String profileTone, @org.jetbrains.annotations.NotNull()
    java.util.List<com.travlytic.app.data.db.entities.TrainingRule> trainingRules) {
        return null;
    }
    
    @java.lang.Override()
    public boolean equals(@org.jetbrains.annotations.Nullable()
    java.lang.Object other) {
        return false;
    }
    
    @java.lang.Override()
    public int hashCode() {
        return 0;
    }
    
    @java.lang.Override()
    @org.jetbrains.annotations.NotNull()
    public java.lang.String toString() {
        return null;
    }
}