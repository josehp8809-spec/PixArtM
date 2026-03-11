package com.travlytic.app.engine;

import com.travlytic.app.data.db.dao.ResponseLogDao;
import com.travlytic.app.data.db.dao.TrainingRuleDao;
import com.travlytic.app.data.repository.KnowledgeRepository;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata("javax.inject.Singleton")
@QualifierMetadata
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
public final class GeminiAgent_Factory implements Factory<GeminiAgent> {
  private final Provider<KnowledgeRepository> knowledgeRepositoryProvider;

  private final Provider<TrainingRuleDao> trainingRuleDaoProvider;

  private final Provider<ResponseLogDao> responseLogDaoProvider;

  public GeminiAgent_Factory(Provider<KnowledgeRepository> knowledgeRepositoryProvider,
      Provider<TrainingRuleDao> trainingRuleDaoProvider,
      Provider<ResponseLogDao> responseLogDaoProvider) {
    this.knowledgeRepositoryProvider = knowledgeRepositoryProvider;
    this.trainingRuleDaoProvider = trainingRuleDaoProvider;
    this.responseLogDaoProvider = responseLogDaoProvider;
  }

  @Override
  public GeminiAgent get() {
    return newInstance(knowledgeRepositoryProvider.get(), trainingRuleDaoProvider.get(), responseLogDaoProvider.get());
  }

  public static GeminiAgent_Factory create(
      Provider<KnowledgeRepository> knowledgeRepositoryProvider,
      Provider<TrainingRuleDao> trainingRuleDaoProvider,
      Provider<ResponseLogDao> responseLogDaoProvider) {
    return new GeminiAgent_Factory(knowledgeRepositoryProvider, trainingRuleDaoProvider, responseLogDaoProvider);
  }

  public static GeminiAgent newInstance(KnowledgeRepository knowledgeRepository,
      TrainingRuleDao trainingRuleDao, ResponseLogDao responseLogDao) {
    return new GeminiAgent(knowledgeRepository, trainingRuleDao, responseLogDao);
  }
}
