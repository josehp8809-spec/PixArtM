package com.travlytic.app.engine;

import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
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
public final class SummaryGenerator_Factory implements Factory<SummaryGenerator> {
  @Override
  public SummaryGenerator get() {
    return newInstance();
  }

  public static SummaryGenerator_Factory create() {
    return InstanceHolder.INSTANCE;
  }

  public static SummaryGenerator newInstance() {
    return new SummaryGenerator();
  }

  private static final class InstanceHolder {
    private static final SummaryGenerator_Factory INSTANCE = new SummaryGenerator_Factory();
  }
}
