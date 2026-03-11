package com.travlytic.app.data.db

import androidx.room.Database
import androidx.room.RoomDatabase
import com.travlytic.app.data.db.dao.EscalationLogDao
import com.travlytic.app.data.db.dao.KnowledgeItemDao
import com.travlytic.app.data.db.dao.ResponseLogDao
import com.travlytic.app.data.db.dao.TrainingRuleDao
import com.travlytic.app.data.db.entities.EscalationLog
import com.travlytic.app.data.db.entities.KnowledgeItem
import com.travlytic.app.data.db.entities.ResponseLog
import com.travlytic.app.data.db.entities.TrainingRule

@Database(
    entities = [
        KnowledgeItem::class,
        EscalationLog::class,
        ResponseLog::class,
        TrainingRule::class
    ],
    version = 3,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun knowledgeItemDao(): KnowledgeItemDao
    abstract fun escalationLogDao(): EscalationLogDao
    abstract fun responseLogDao(): ResponseLogDao
    abstract fun trainingRuleDao(): TrainingRuleDao
}
