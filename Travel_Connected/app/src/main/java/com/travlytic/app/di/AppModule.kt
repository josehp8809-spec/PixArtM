package com.travlytic.app.di

import android.content.Context
import androidx.room.Room
import com.travlytic.app.data.db.AppDatabase
import com.travlytic.app.data.db.dao.RegisteredSheetDao
import com.travlytic.app.data.db.dao.ResponseLogDao
import com.travlytic.app.data.db.dao.SheetDataDao
import com.travlytic.app.data.db.dao.TrainingRuleDao
import com.travlytic.app.data.prefs.AppPreferences
import com.travlytic.app.data.sheets.SheetsRepository
import com.travlytic.app.engine.GeminiAgent
import com.travlytic.app.engine.SummaryGenerator
import com.travlytic.app.engine.TtsManager
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideAppDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "travlytic_database"
        ).fallbackToDestructiveMigration().build()
    }

    @Provides @Singleton
    fun provideSheetDataDao(db: AppDatabase): SheetDataDao = db.sheetDataDao()

    @Provides @Singleton
    fun provideRegisteredSheetDao(db: AppDatabase): RegisteredSheetDao = db.registeredSheetDao()

    @Provides @Singleton
    fun provideResponseLogDao(db: AppDatabase): ResponseLogDao = db.responseLogDao()

    @Provides @Singleton
    fun provideTrainingRuleDao(db: AppDatabase): TrainingRuleDao = db.trainingRuleDao()

    @Provides @Singleton
    fun provideAppPreferences(@ApplicationContext context: Context): AppPreferences =
        AppPreferences(context)

    @Provides @Singleton
    fun provideSheetsRepository(
        @ApplicationContext context: Context,
        sheetDataDao: SheetDataDao,
        registeredSheetDao: RegisteredSheetDao
    ): SheetsRepository = SheetsRepository(context, sheetDataDao, registeredSheetDao)

    @Provides @Singleton
    fun provideGeminiAgent(
        sheetDataDao: SheetDataDao,
        registeredSheetDao: RegisteredSheetDao,
        trainingRuleDao: TrainingRuleDao
    ): GeminiAgent = GeminiAgent(sheetDataDao, registeredSheetDao, trainingRuleDao)

    @Provides @Singleton
    fun provideSummaryGenerator(): SummaryGenerator = SummaryGenerator()

    @Provides @Singleton
    fun provideTtsManager(@ApplicationContext context: Context): TtsManager = TtsManager(context)
}
