package com.travlytic.app.di;

import com.travlytic.app.data.db.AppDatabase;
import com.travlytic.app.data.db.dao.EscalationLogDao;
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
public final class AppModule_ProvideEscalationLogDaoFactory implements Factory<EscalationLogDao> {
  private final Provider<AppDatabase> dbProvider;

  public AppModule_ProvideEscalationLogDaoFactory(Provider<AppDatabase> dbProvider) {
    this.dbProvider = dbProvider;
  }

  @Override
  public EscalationLogDao get() {
    return provideEscalationLogDao(dbProvider.get());
  }

  public static AppModule_ProvideEscalationLogDaoFactory create(Provider<AppDatabase> dbProvider) {
    return new AppModule_ProvideEscalationLogDaoFactory(dbProvider);
  }

  public static EscalationLogDao provideEscalationLogDao(AppDatabase db) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideEscalationLogDao(db));
  }
}
