package com.travlytic.app.data.db

import androidx.room.Database
import androidx.room.RoomDatabase
import com.travlytic.app.data.db.dao.RegisteredSheetDao
import com.travlytic.app.data.db.dao.ResponseLogDao
import com.travlytic.app.data.db.dao.SheetDataDao
import com.travlytic.app.data.db.dao.TrainingRuleDao
import com.travlytic.app.data.db.entities.RegisteredSheet
import com.travlytic.app.data.db.entities.ResponseLog
import com.travlytic.app.data.db.entities.SheetData
import com.travlytic.app.data.db.entities.TrainingRule

@Database(
    entities = [
        SheetData::class,
        RegisteredSheet::class,
        ResponseLog::class,
        TrainingRule::class
    ],
    version = 2,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun sheetDataDao(): SheetDataDao
    abstract fun registeredSheetDao(): RegisteredSheetDao
    abstract fun responseLogDao(): ResponseLogDao
    abstract fun trainingRuleDao(): TrainingRuleDao
}
