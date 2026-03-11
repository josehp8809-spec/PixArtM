package com.travlytic.app.data.db.dao

import androidx.room.*
import com.travlytic.app.data.db.entities.EscalationLog
import kotlinx.coroutines.flow.Flow

@Dao
interface EscalationLogDao {
    @Query("SELECT * FROM escalation_logs ORDER BY timestamp DESC")
    fun getAllFlow(): Flow<List<EscalationLog>>

    @Query("SELECT * FROM escalation_logs WHERE isResolved = 0 ORDER BY timestamp DESC")
    fun getPendingFlow(): Flow<List<EscalationLog>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(log: EscalationLog): Long

    @Update
    suspend fun update(log: EscalationLog)

    @Delete
    suspend fun delete(log: EscalationLog)
}
