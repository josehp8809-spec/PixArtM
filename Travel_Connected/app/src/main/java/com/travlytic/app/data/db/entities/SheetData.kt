package com.travlytic.app.data.db.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Representa una fila de datos proveniente de un Google Sheet.
 * Cada fila se almacena como un string JSON con todas sus columnas.
 */
@Entity(tableName = "sheet_data")
data class SheetData(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val spreadsheetId: String,
    val sheetName: String,
    val rowIndex: Int,
    val content: String // Fila serializada como JSON: {"col0":"val0","col1":"val1",...}
)
