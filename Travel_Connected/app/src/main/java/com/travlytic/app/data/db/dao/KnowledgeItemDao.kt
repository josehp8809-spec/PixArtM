package com.travlytic.app.data.db.dao

import androidx.room.*
import com.travlytic.app.data.db.entities.KnowledgeItem
import kotlinx.coroutines.flow.Flow

@Dao
interface KnowledgeItemDao {
    @Query("SELECT * FROM knowledge_items")
    fun getAllFlow(): Flow<List<KnowledgeItem>>

    @Query("SELECT * FROM knowledge_items WHERE isEnabled = 1")
    suspend fun getEnabledItems(): List<KnowledgeItem>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: KnowledgeItem): Long

    @Update
    suspend fun update(item: KnowledgeItem)

    @Delete
    suspend fun delete(item: KnowledgeItem)

    @Query("SELECT * FROM knowledge_items WHERE type = 'url'")
    suspend fun getUrlItems(): List<KnowledgeItem>

    @Query("DELETE FROM knowledge_items WHERE type = 'excel'")
    suspend fun deleteAllExcelItems()
}
