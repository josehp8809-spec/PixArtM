package com.travlytic.app.ui.viewmodel;

import android.content.Context;
import com.travlytic.app.data.db.dao.EscalationLogDao;
import com.travlytic.app.data.db.dao.ResponseLogDao;
import com.travlytic.app.data.db.dao.TrainingRuleDao;
import com.travlytic.app.data.prefs.AppPreferences;
import com.travlytic.app.data.repository.KnowledgeRepository;
import com.travlytic.app.engine.GeminiAgent;
import com.travlytic.app.engine.SummaryGenerator;
import com.travlytic.app.engine.TtsManager;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata
@QualifierMetadata("dagger.hilt.android.qualifiers.ApplicationContext")
@DaggerGenerated
@Generated(
    value = "dagger.internal.codegen.ComponentProcessor",
    comments = "https://dagger.dev"
)
@SuppressWarnings({
    "unchecked",
    "rawtypes",
    "KotlinInternal",
    "KotlinInternalInJava",
    "cast"
})
public final class MainViewModel_Factory implements Factory<MainViewModel> {
  private final Provider<Context> contextProvider;

  private final Provider<AppPreferences> appPreferencesProvider;

  private final Provider<KnowledgeRepository> knowledgeRepositoryProvider;

  private final Provider<EscalationLogDao> escalationLogDaoProvider;

  private final Provider<ResponseLogDao> responseLogDaoProvider;

  private final Provider<TrainingRuleDao> trainingRuleDaoProvider;

  private final Provider<GeminiAgent> geminiAgentProvider;

  private final Provider<SummaryGenerator> summaryGeneratorProvider;

  private final Provider<TtsManager> ttsManagerProvider;

  public MainViewModel_Factory(Provider<Context> contextProvider,
      Provider<AppPreferences> appPreferencesProvider,
      Provider<KnowledgeRepository> knowledgeRepositoryProvider,
      Provider<EscalationLogDao> escalationLogDaoProvider,
      Provider<ResponseLogDao> responseLogDaoProvider,
      Provider<TrainingRuleDao> trainingRuleDaoProvider, Provider<GeminiAgent> geminiAgentProvider,
      Provider<SummaryGenerator> summaryGeneratorProvider,
      Provider<TtsManager> ttsManagerProvider) {
    this.contextProvider = contextProvider;
    this.appPreferencesProvider = appPreferencesProvider;
    this.knowledgeRepositoryProvider = knowledgeRepositoryProvider;
    this.escalationLogDaoProvider = escalationLogDaoProvider;
    this.responseLogDaoProvider = responseLogDaoProvider;
    this.trainingRuleDaoProvider = trainingRuleDaoProvider;
    this.geminiAgentProvider = geminiAgentProvider;
    this.summaryGeneratorProvider = summaryGeneratorProvider;
    this.ttsManagerProvider = ttsManagerProvider;
  }

  @Override
  public MainViewModel get() {
    return newInstance(contextProvider.get(), appPreferencesProvider.get(), knowledgeRepositoryProvider.get(), escalationLogDaoProvider.get(), responseLogDaoProvider.get(), trainingRuleDaoProvider.get(), geminiAgentProvider.get(), summaryGeneratorProvider.get(), ttsManagerProvider.get());
  }

  public static MainViewModel_Factory create(Provider<Context> contextProvider,
      Provider<AppPreferences> appPreferencesProvider,
      Provider<KnowledgeRepository> knowledgeRepositoryProvider,
      Provider<EscalationLogDao> escalationLogDaoProvider,
      Provider<ResponseLogDao> responseLogDaoProvider,
      Provider<TrainingRuleDao> trainingRuleDaoProvider, Provider<GeminiAgent> geminiAgentProvider,
      Provider<SummaryGenerator> summaryGeneratorProvider,
      Provider<TtsManager> ttsManagerProvider) {
    return new MainViewModel_Factory(contextProvider, appPreferencesProvider, knowledgeRepositoryProvider, escalationLogDaoProvider, responseLogDaoProvider, trainingRuleDaoProvider, geminiAgentProvider, summaryGeneratorProvider, ttsManagerProvider);
  }

  public static MainViewModel newInstance(Context context, AppPreferences appPreferences,
      KnowledgeRepository knowledgeRepository, EscalationLogDao escalationLogDao,
      ResponseLogDao responseLogDao, TrainingRuleDao trainingRuleDao, GeminiAgent geminiAgent,
      SummaryGenerator summaryGenerator, TtsManager ttsManager) {
    return new MainViewModel(context, appPreferences, knowledgeRepository, escalationLogDao, responseLogDao, trainingRuleDao, geminiAgent, summaryGenerator, ttsManager);
  }
}
