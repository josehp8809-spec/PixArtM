package com.travlytic.app.di;

import com.travlytic.app.data.db.AppDatabase;
import com.travlytic.app.data.db.dao.ResponseLogDao;
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
public final class AppModule_ProvideResponseLogDaoFactory implements Factory<ResponseLogDao> {
  private final Provider<AppDatabase> dbProvider;

  public AppModule_ProvideResponseLogDaoFactory(Provider<AppDatabase> dbProvider) {
    this.dbProvider = dbProvider;
  }

  @Override
  public ResponseLogDao get() {
    return provideResponseLogDao(dbProvider.get());
  }

  public static AppModule_ProvideResponseLogDaoFactory create(Provider<AppDatabase> dbProvider) {
    return new AppModule_ProvideResponseLogDaoFactory(dbProvider);
  }

  public static ResponseLogDao provideResponseLogDao(AppDatabase db) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideResponseLogDao(db));
  }
}
