package com.travlytic.app.di;

@dagger.Module()
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000D\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\b\u00c7\u0002\u0018\u00002\u00020\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0002J\u0012\u0010\u0003\u001a\u00020\u00042\b\b\u0001\u0010\u0005\u001a\u00020\u0006H\u0007J\u0012\u0010\u0007\u001a\u00020\b2\b\b\u0001\u0010\u0005\u001a\u00020\u0006H\u0007J\u0010\u0010\t\u001a\u00020\n2\u0006\u0010\u000b\u001a\u00020\u0004H\u0007J\u0010\u0010\f\u001a\u00020\r2\u0006\u0010\u000b\u001a\u00020\u0004H\u0007J\u0010\u0010\u000e\u001a\u00020\u000f2\u0006\u0010\u000b\u001a\u00020\u0004H\u0007J\b\u0010\u0010\u001a\u00020\u0011H\u0007J\u0010\u0010\u0012\u001a\u00020\u00132\u0006\u0010\u000b\u001a\u00020\u0004H\u0007J\u0012\u0010\u0014\u001a\u00020\u00152\b\b\u0001\u0010\u0005\u001a\u00020\u0006H\u0007\u00a8\u0006\u0016"}, d2 = {"Lcom/travlytic/app/di/AppModule;", "", "()V", "provideAppDatabase", "Lcom/travlytic/app/data/db/AppDatabase;", "context", "Landroid/content/Context;", "provideAppPreferences", "Lcom/travlytic/app/data/prefs/AppPreferences;", "provideEscalationLogDao", "Lcom/travlytic/app/data/db/dao/EscalationLogDao;", "db", "provideKnowledgeItemDao", "Lcom/travlytic/app/data/db/dao/KnowledgeItemDao;", "provideResponseLogDao", "Lcom/travlytic/app/data/db/dao/ResponseLogDao;", "provideSummaryGenerator", "Lcom/travlytic/app/engine/SummaryGenerator;", "provideTrainingRuleDao", "Lcom/travlytic/app/data/db/dao/TrainingRuleDao;", "provideTtsManager", "Lcom/travlytic/app/engine/TtsManager;", "app_debug"})
@dagger.hilt.InstallIn(value = {dagger.hilt.components.SingletonComponent.class})
public final class AppModule {
    @org.jetbrains.annotations.NotNull()
    public static final com.travlytic.app.di.AppModule INSTANCE = null;
    
    private AppModule() {
        super();
    }
    
    @dagger.Provides()
    @javax.inject.Singleton()
    @org.jetbrains.annotations.NotNull()
    public final com.travlytic.app.data.db.AppDatabase provideAppDatabase(@dagger.hilt.android.qualifiers.ApplicationContext()
    @org.jetbrains.annotations.NotNull()
    android.content.Context context) {
        return null;
    }
    
    @dagger.Provides()
    @javax.inject.Singleton()
    @org.jetbrains.annotations.NotNull()
    public final com.travlytic.app.data.db.dao.KnowledgeItemDao provideKnowledgeItemDao(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.AppDatabase db) {
        return null;
    }
    
    @dagger.Provides()
    @javax.inject.Singleton()
    @org.jetbrains.annotations.NotNull()
    public final com.travlytic.app.data.db.dao.EscalationLogDao provideEscalationLogDao(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.AppDatabase db) {
        return null;
    }
    
    @dagger.Provides()
    @javax.inject.Singleton()
    @org.jetbrains.annotations.NotNull()
    public final com.travlytic.app.data.db.dao.ResponseLogDao provideResponseLogDao(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.AppDatabase db) {
        return null;
    }
    
    @dagger.Provides()
    @javax.inject.Singleton()
    @org.jetbrains.annotations.NotNull()
    public final com.travlytic.app.data.db.dao.TrainingRuleDao provideTrainingRuleDao(@org.jetbrains.annotations.NotNull()
    com.travlytic.app.data.db.AppDatabase db) {
        return null;
    }
    
    @dagger.Provides()
    @javax.inject.Singleton()
    @org.jetbrains.annotations.NotNull()
    public final com.travlytic.app.data.prefs.AppPreferences provideAppPreferences(@dagger.hilt.android.qualifiers.ApplicationContext()
    @org.jetbrains.annotations.NotNull()
    android.content.Context context) {
        return null;
    }
    
    @dagger.Provides()
    @javax.inject.Singleton()
    @org.jetbrains.annotations.NotNull()
    public final com.travlytic.app.engine.SummaryGenerator provideSummaryGenerator() {
        return null;
    }
    
    @dagger.Provides()
    @javax.inject.Singleton()
    @org.jetbrains.annotations.NotNull()
    public final com.travlytic.app.engine.TtsManager provideTtsManager(@dagger.hilt.android.qualifiers.ApplicationContext()
    @org.jetbrains.annotations.NotNull()
    android.content.Context context) {
        return null;
    }
}