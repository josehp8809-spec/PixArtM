package com.travlytic.app.di;

import com.travlytic.app.data.db.AppDatabase;
import com.travlytic.app.data.db.dao.KnowledgeItemDao;
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
public final class AppModule_ProvideKnowledgeItemDaoFactory implements Factory<KnowledgeItemDao> {
  private final Provider<AppDatabase> dbProvider;

  public AppModule_ProvideKnowledgeItemDaoFactory(Provider<AppDatabase> dbProvider) {
    this.dbProvider = dbProvider;
  }

  @Override
  public KnowledgeItemDao get() {
    return provideKnowledgeItemDao(dbProvider.get());
  }

  public static AppModule_ProvideKnowledgeItemDaoFactory create(Provider<AppDatabase> dbProvider) {
    return new AppModule_ProvideKnowledgeItemDaoFactory(dbProvider);
  }

  public static KnowledgeItemDao provideKnowledgeItemDao(AppDatabase db) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideKnowledgeItemDao(db));
  }
}
