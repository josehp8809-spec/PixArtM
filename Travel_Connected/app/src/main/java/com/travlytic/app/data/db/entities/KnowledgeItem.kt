package com.travlytic.app.data.db.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "knowledge_items")
data class KnowledgeItem(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val type: String,           // "excel" | "url"
    val reference: String,      // Label descriptivo: "Precios", "Horarios"
    val source: String,         // path del .xlsx o URL
    val content: String,        // contenido scrapeado / parseado (texto plano)
    val lastUpdated: Long = 0L,
    val isEnabled: Boolean = true
)
