package com.travlytic.app.data.db.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Representa un Google Sheet registrado por el usuario en la app.
 */
@Entity(tableName = "registered_sheets")
data class RegisteredSheet(
    @PrimaryKey
    val spreadsheetId: String,
    val title: String,
    val lastSynced: Long = 0L,
    val rowCount: Int = 0,
    val isEnabled: Boolean = true
)
