package com.travlytic.app.service;

import com.travlytic.app.data.db.dao.EscalationLogDao;
import com.travlytic.app.data.db.dao.ResponseLogDao;
import com.travlytic.app.data.prefs.AppPreferences;
import com.travlytic.app.engine.GeminiAgent;
import dagger.MembersInjector;
import dagger.internal.DaggerGenerated;
import dagger.internal.InjectedFieldSignature;
import dagger.internal.QualifierMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

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
public final class UniversalListenerService_MembersInjector implements MembersInjector<UniversalListenerService> {
  private final Provider<GeminiAgent> geminiAgentProvider;

  private final Provider<ResponseLogDao> responseLogDaoProvider;

  private final Provider<EscalationLogDao> escalationLogDaoProvider;

  private final Provider<AppPreferences> appPreferencesProvider;

  public UniversalListenerService_MembersInjector(Provider<GeminiAgent> geminiAgentProvider,
      Provider<ResponseLogDao> responseLogDaoProvider,
      Provider<EscalationLogDao> escalationLogDaoProvider,
      Provider<AppPreferences> appPreferencesProvider) {
    this.geminiAgentProvider = geminiAgentProvider;
    this.responseLogDaoProvider = responseLogDaoProvider;
    this.escalationLogDaoProvider = escalationLogDaoProvider;
    this.appPreferencesProvider = appPreferencesProvider;
  }

  public static MembersInjector<UniversalListenerService> create(
      Provider<GeminiAgent> geminiAgentProvider, Provider<ResponseLogDao> responseLogDaoProvider,
      Provider<EscalationLogDao> escalationLogDaoProvider,
      Provider<AppPreferences> appPreferencesProvider) {
    return new UniversalListenerService_MembersInjector(geminiAgentProvider, responseLogDaoProvider, escalationLogDaoProvider, appPreferencesProvider);
  }

  @Override
  public void injectMembers(UniversalListenerService instance) {
    injectGeminiAgent(instance, geminiAgentProvider.get());
    injectResponseLogDao(instance, responseLogDaoProvider.get());
    injectEscalationLogDao(instance, escalationLogDaoProvider.get());
    injectAppPreferences(instance, appPreferencesProvider.get());
  }

  @InjectedFieldSignature("com.travlytic.app.service.UniversalListenerService.geminiAgent")
  public static void injectGeminiAgent(UniversalListenerService instance, GeminiAgent geminiAgent) {
    instance.geminiAgent = geminiAgent;
  }

  @InjectedFieldSignature("com.travlytic.app.service.UniversalListenerService.responseLogDao")
  public static void injectResponseLogDao(UniversalListenerService instance,
      ResponseLogDao responseLogDao) {
    instance.responseLogDao = responseLogDao;
  }

  @InjectedFieldSignature("com.travlytic.app.service.UniversalListenerService.escalationLogDao")
  public static void injectEscalationLogDao(UniversalListenerService instance,
      EscalationLogDao escalationLogDao) {
    instance.escalationLogDao = escalationLogDao;
  }

  @InjectedFieldSignature("com.travlytic.app.service.UniversalListenerService.appPreferences")
  public static void injectAppPreferences(UniversalListenerService instance,
      AppPreferences appPreferences) {
    instance.appPreferences = appPreferences;
  }
}
