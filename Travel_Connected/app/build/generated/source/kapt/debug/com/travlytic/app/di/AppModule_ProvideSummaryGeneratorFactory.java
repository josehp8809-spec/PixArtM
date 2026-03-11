package com.travlytic.app.di;

import com.travlytic.app.engine.SummaryGenerator;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;

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
public final class AppModule_ProvideSummaryGeneratorFactory implements Factory<SummaryGenerator> {
  @Override
  public SummaryGenerator get() {
    return provideSummaryGenerator();
  }

  public static AppModule_ProvideSummaryGeneratorFactory create() {
    return InstanceHolder.INSTANCE;
  }

  public static SummaryGenerator provideSummaryGenerator() {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideSummaryGenerator());
  }

  private static final class InstanceHolder {
    private static final AppModule_ProvideSummaryGeneratorFactory INSTANCE = new AppModule_ProvideSummaryGeneratorFactory();
  }
}
