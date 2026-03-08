package com.travlytic.app.data.db.dao

import androidx.room.*
import com.travlytic.app.data.db.entities.SheetData
import kotlinx.coroutines.flow.Flow

@Dao
interface SheetDataDao {

    @Query("SELECT * FROM sheet_data WHERE spreadsheetId = :spreadsheetId")
    suspend fun getBySpreadsheet(spreadsheetId: String): List<SheetData>

    @Query("SELECT * FROM sheet_data")
    suspend fun getAll(): List<SheetData>

    @Query("SELECT * FROM sheet_data")
    fun observeAll(): Flow<List<SheetData>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(entries: List<SheetData>)

    @Query("DELETE FROM sheet_data WHERE spreadsheetId = :spreadsheetId")
    suspend fun deleteBySpreadsheet(spreadsheetId: String)

    @Query("DELETE FROM sheet_data")
    suspend fun deleteAll()

    @Query("SELECT COUNT(*) FROM sheet_data WHERE spreadsheetId = :spreadsheetId")
    suspend fun countBySpreadsheet(spreadsheetId: String): Int
}
