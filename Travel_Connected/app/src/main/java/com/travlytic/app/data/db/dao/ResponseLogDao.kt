package com.travlytic.app.data.db.dao

import androidx.room.*
import com.travlytic.app.data.db.entities.ResponseLog
import kotlinx.coroutines.flow.Flow

@Dao
interface ResponseLogDao {

    @Query("SELECT * FROM response_log ORDER BY timestamp DESC LIMIT :limit")
    fun observeRecent(limit: Int = 50): Flow<List<ResponseLog>>

    @Query("SELECT * FROM response_log ORDER BY timestamp DESC LIMIT :limit")
    suspend fun getRecent(limit: Int = 50): List<ResponseLog>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(log: ResponseLog)

    @Query("DELETE FROM response_log")
    suspend fun deleteAll()

    @Query("SELECT COUNT(*) FROM response_log")
    suspend fun count(): Int
}
