package com.travlytic.app.data.db.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Registro de cada respuesta automática enviada por Travlytic.
 */
@Entity(tableName = "response_log")
data class ResponseLog(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val contact: String,
    val incomingMessage: String,
    val sentResponse: String,
    val timestamp: Long = System.currentTimeMillis(),
    val sheetsUsed: String = "" // IDs de sheets usados (separados por coma)
)
