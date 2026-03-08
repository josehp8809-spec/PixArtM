package com.travlytic.app.data.db.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "training_rules")
data class TrainingRule(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val type: String, // "RULE" o "EXAMPLE"
    val input: String, // Regla o Mensaje del usuario
    val output: String? = null, // Respuesta ideal (solo para ejemplos)
    val isActive: Boolean = true
)
