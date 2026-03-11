package com.travlytic.app.di;

import com.travlytic.app.data.db.AppDatabase;
import com.travlytic.app.data.db.dao.TrainingRuleDao;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
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
public final class AppModule_ProvideTrainingRuleDaoFactory implements Factory<TrainingRuleDao> {
  private final Provider<AppDatabase> dbProvider;

  public AppModule_ProvideTrainingRuleDaoFactory(Provider<AppDatabase> dbProvider) {
    this.dbProvider = dbProvider;
  }

  @Override
  public TrainingRuleDao get() {
    return provideTrainingRuleDao(dbProvider.get());
  }

  public static AppModule_ProvideTrainingRuleDaoFactory create(Provider<AppDatabase> dbProvider) {
    return new AppModule_ProvideTrainingRuleDaoFactory(dbProvider);
  }

  public static TrainingRuleDao provideTrainingRuleDao(AppDatabase db) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideTrainingRuleDao(db));
  }
}
