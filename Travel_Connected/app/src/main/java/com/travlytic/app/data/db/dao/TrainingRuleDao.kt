package com.travlytic.app.data.db.dao

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.travlytic.app.data.db.entities.TrainingRule
import kotlinx.coroutines.flow.Flow

@Dao
interface TrainingRuleDao {
    @Query("SELECT * FROM training_rules ORDER BY type ASC, id DESC")
    fun observeAll(): Flow<List<TrainingRule>>

    @Query("SELECT * FROM training_rules WHERE isActive = 1 ORDER BY type ASC")
    suspend fun getActiveRules(): List<TrainingRule>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(rule: TrainingRule)
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(rules: List<TrainingRule>)

    @Update
    suspend fun update(rule: TrainingRule)

    @Delete
    suspend fun delete(rule: TrainingRule)
    
    @Query("DELETE FROM training_rules")
    suspend fun deleteAll()
}
