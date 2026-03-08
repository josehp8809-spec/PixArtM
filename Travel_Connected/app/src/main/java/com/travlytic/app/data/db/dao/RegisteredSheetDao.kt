package com.travlytic.app.data.db.dao

import androidx.room.*
import com.travlytic.app.data.db.entities.RegisteredSheet
import kotlinx.coroutines.flow.Flow

@Dao
interface RegisteredSheetDao {

    @Query("SELECT * FROM registered_sheets ORDER BY lastSynced DESC")
    fun observeAll(): Flow<List<RegisteredSheet>>

    @Query("SELECT * FROM registered_sheets")
    suspend fun getAll(): List<RegisteredSheet>

    @Query("SELECT * FROM registered_sheets WHERE spreadsheetId = :spreadsheetId LIMIT 1")
    suspend fun getById(spreadsheetId: String): RegisteredSheet?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(sheet: RegisteredSheet)

    @Update
    suspend fun update(sheet: RegisteredSheet)

    @Query("DELETE FROM registered_sheets WHERE spreadsheetId = :spreadsheetId")
    suspend fun deleteById(spreadsheetId: String)

    @Query("SELECT COUNT(*) FROM registered_sheets")
    suspend fun count(): Int
}
