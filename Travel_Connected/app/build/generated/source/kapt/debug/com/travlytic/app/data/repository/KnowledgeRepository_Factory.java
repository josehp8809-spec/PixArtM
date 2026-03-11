package com.travlytic.app.data.repository;

import android.content.Context;
import com.travlytic.app.data.db.dao.KnowledgeItemDao;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata("javax.inject.Singleton")
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
public final class KnowledgeRepository_Factory implements Factory<KnowledgeRepository> {
  private final Provider<KnowledgeItemDao> daoProvider;

  private final Provider<Context> contextProvider;

  public KnowledgeRepository_Factory(Provider<KnowledgeItemDao> daoProvider,
      Provider<Context> contextProvider) {
    this.daoProvider = daoProvider;
    this.contextProvider = contextProvider;
  }

  @Override
  public KnowledgeRepository get() {
    return newInstance(daoProvider.get(), contextProvider.get());
  }

  public static KnowledgeRepository_Factory create(Provider<KnowledgeItemDao> daoProvider,
      Provider<Context> contextProvider) {
    return new KnowledgeRepository_Factory(daoProvider, contextProvider);
  }

  public static KnowledgeRepository newInstance(KnowledgeItemDao dao, Context context) {
    return new KnowledgeRepository(dao, context);
  }
}
