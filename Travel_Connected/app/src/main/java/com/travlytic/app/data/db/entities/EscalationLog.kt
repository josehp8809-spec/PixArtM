package com.travlytic.app.data.db.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "escalation_logs")
data class EscalationLog(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val contact: String,
    val originalMessage: String,
    val timestamp: Long,
    val isResolved: Boolean = false
)
