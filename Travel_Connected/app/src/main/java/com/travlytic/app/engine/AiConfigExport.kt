package com.travlytic.app.engine

import com.travlytic.app.data.db.entities.TrainingRule

/**
 * Modelo de datos utilizado para Exportar e Importar la configuración del agente en fomato JSON.
 */
data class AiConfigExport(
    val version: Int = 1,
    val version: Int = 1,
    val systemPrompt: String,
    val profileUserName: String? = null,
    val profileBusinessName: String? = null,
    val profileTone: String? = null,
    val trainingRules: List<TrainingRule>
)
