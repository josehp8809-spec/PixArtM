package com.travlytic.app.di;

import android.content.Context;
import com.google.gson.Gson;
import com.travlytic.app.data.prefs.AppPreferences;
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
public final class AppModule_ProvideAppPreferencesFactory implements Factory<AppPreferences> {
  private final Provider<Context> contextProvider;

  private final Provider<Gson> gsonProvider;

  public AppModule_ProvideAppPreferencesFactory(Provider<Context> contextProvider,
      Provider<Gson> gsonProvider) {
    this.contextProvider = contextProvider;
    this.gsonProvider = gsonProvider;
  }

  @Override
  public AppPreferences get() {
    return provideAppPreferences(contextProvider.get(), gsonProvider.get());
  }

  public static AppModule_ProvideAppPreferencesFactory create(Provider<Context> contextProvider,
      Provider<Gson> gsonProvider) {
    return new AppModule_ProvideAppPreferencesFactory(contextProvider, gsonProvider);
  }

  public static AppPreferences provideAppPreferences(Context context, Gson gson) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideAppPreferences(context, gson));
  }
}
