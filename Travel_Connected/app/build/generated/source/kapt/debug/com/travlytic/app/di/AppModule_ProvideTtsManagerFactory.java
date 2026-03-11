package com.travlytic.app.di;

import android.content.Context;
import com.travlytic.app.engine.TtsManager;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
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
public final class AppModule_ProvideTtsManagerFactory implements Factory<TtsManager> {
  private final Provider<Context> contextProvider;

  public AppModule_ProvideTtsManagerFactory(Provider<Context> contextProvider) {
    this.contextProvider = contextProvider;
  }

  @Override
  public TtsManager get() {
    return provideTtsManager(contextProvider.get());
  }

  public static AppModule_ProvideTtsManagerFactory create(Provider<Context> contextProvider) {
    return new AppModule_ProvideTtsManagerFactory(contextProvider);
  }

  public static TtsManager provideTtsManager(Context context) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideTtsManager(context));
  }
}
