package com.travlytic.app.data.sheets

import android.content.Context
import android.util.Log
import com.google.api.client.googleapis.extensions.android.gms.auth.GoogleAccountCredential
import com.google.api.client.http.javanet.NetHttpTransport
import com.google.api.client.json.gson.GsonFactory
import com.google.api.services.sheets.v4.Sheets
import com.google.api.services.sheets.v4.SheetsScopes
import com.google.gson.Gson
import com.travlytic.app.data.db.dao.RegisteredSheetDao
import com.travlytic.app.data.db.dao.SheetDataDao
import com.travlytic.app.data.db.entities.RegisteredSheet
import com.travlytic.app.data.db.entities.SheetData
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import javax.inject.Inject
import javax.inject.Singleton

private const val TAG = "SheetsRepository"
private const val APP_NAME = "Travlytic"

sealed class SyncResult {
    data class Success(val rowCount: Int, val sheetTitle: String) : SyncResult()
    data class Error(val message: String) : SyncResult()
}

@Singleton
class SheetsRepository @Inject constructor(
    private val context: Context,
    private val sheetDataDao: SheetDataDao,
    private val registeredSheetDao: RegisteredSheetDao
) {
    private val gson = Gson()

    /**
     * Extrae el ID del spreadsheet desde una URL o ID directo.
     * Soporta:
     *  - ID directo: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms"
     *  - URL: "https://docs.google.com/spreadsheets/d/ID/edit#gid=0"
     */
    fun extractSpreadsheetId(input: String): String? {
        val trimmed = input.trim()
        // Si ya es un ID (no contiene /)
        if (!trimmed.contains("/")) return trimmed.ifBlank { null }
        // Si es una URL de Google Sheets
        val regex = Regex("/spreadsheets/d/([a-zA-Z0-9-_]+)")
        return regex.find(trimmed)?.groupValues?.get(1)
    }

    /**
     * Registra un nuevo Sheet en la base de datos local.
     * No sincroniza todavía, solo guarda el ID para sincronizar después.
     */
    suspend fun registerSheet(spreadsheetId: String, title: String = "Sheet sin título") {
        val existing = registeredSheetDao.getById(spreadsheetId)
        if (existing == null) {
            registeredSheetDao.insert(
                RegisteredSheet(
                    spreadsheetId = spreadsheetId,
                    title = title,
                    lastSynced = 0L,
                    rowCount = 0,
                    isEnabled = true
                )
            )
            Log.d(TAG, "Sheet registrado: $spreadsheetId")
        }
    }

    /**
     * Elimina un Sheet de la DB local junto con todos sus datos.
     */
    suspend fun removeSheet(spreadsheetId: String) {
        registeredSheetDao.deleteById(spreadsheetId)
        sheetDataDao.deleteBySpreadsheet(spreadsheetId)
        Log.d(TAG, "Sheet eliminado: $spreadsheetId")
    }

    /**
     * Sincroniza un Sheet específico con Google Sheets API v4.
     * Descarga TODAS las pestañas del spreadsheet y las guarda en Room.
     *
     * @param spreadsheetId ID del spreadsheet
     * @param accountEmail Email de la cuenta Google autenticada
     */
    suspend fun syncSheet(spreadsheetId: String, accountEmail: String): SyncResult {
        return withContext(Dispatchers.IO) {
            try {
                val credential = GoogleAccountCredential
                    .usingOAuth2(context, listOf(SheetsScopes.SPREADSHEETS_READONLY))
                    .apply { selectedAccountName = accountEmail }

                val sheetsService = Sheets.Builder(
                    NetHttpTransport(),
                    GsonFactory.getDefaultInstance(),
                    credential
                ).setApplicationName(APP_NAME).build()

                // Obtener metadatos del spreadsheet (nombre y pestañas)
                val spreadsheet = sheetsService.spreadsheets()
                    .get(spreadsheetId)
                    .execute()

                val spreadsheetTitle = spreadsheet.properties.title ?: "Sin título"
                val sheets = spreadsheet.sheets ?: emptyList()

                var totalRowCount = 0
                val allSheetData = mutableListOf<SheetData>()

                // Por cada pestaña, leer todos los datos
                for (sheet in sheets) {
                    val sheetTitle = sheet.properties.title ?: continue
                    val range = "$sheetTitle!A1:ZZ"

                    try {
                        val response = sheetsService.spreadsheets().values()
                            .get(spreadsheetId, range)
                            .execute()

                        val values = response.getValues() ?: continue
                        if (values.isEmpty()) continue

                        // Primera fila como encabezados
                        val headers = values[0].map { it.toString() }

                        // Filas de datos (desde la fila 1 en adelante)
                        for ((rowIndex, row) in values.drop(1).withIndex()) {
                            val rowMap = mutableMapOf<String, String>()
                            headers.forEachIndexed { colIndex, header ->
                                val cellValue = row.getOrNull(colIndex)?.toString() ?: ""
                                if (header.isNotBlank()) {
                                    rowMap[header] = cellValue
                                }
                            }

                            if (rowMap.values.any { it.isNotBlank() }) {
                                allSheetData.add(
                                    SheetData(
                                        spreadsheetId = spreadsheetId,
                                        sheetName = sheetTitle,
                                        rowIndex = rowIndex,
                                        content = gson.toJson(rowMap)
                                    )
                                )
                                totalRowCount++
                            }
                        }
                        Log.d(TAG, "Pestaña '$sheetTitle': ${values.size - 1} filas leídas")

                    } catch (e: Exception) {
                        Log.w(TAG, "Error leyendo pestaña '$sheetTitle': ${e.message}")
                    }
                }

                // Guardar en Room (reemplazando datos anteriores de este sheet)
                sheetDataDao.deleteBySpreadsheet(spreadsheetId)
                sheetDataDao.insertAll(allSheetData)

                // Actualizar metadata del sheet registrado
                val existing = registeredSheetDao.getById(spreadsheetId)
                if (existing != null) {
                    registeredSheetDao.update(
                        existing.copy(
                            title = spreadsheetTitle,
                            lastSynced = System.currentTimeMillis(),
                            rowCount = totalRowCount
                        )
                    )
                }

                Log.d(TAG, "Sync exitoso: $spreadsheetTitle → $totalRowCount filas guardadas")
                SyncResult.Success(totalRowCount, spreadsheetTitle)

            } catch (e: Exception) {
                Log.e(TAG, "Error sincronizando sheet $spreadsheetId", e)
                SyncResult.Error(e.message ?: "Error desconocido")
            }
        }
    }

    /**
     * Sincroniza TODOS los Sheets habilitados.
     */
    suspend fun syncAll(accountEmail: String): Map<String, SyncResult> {
        val sheets = registeredSheetDao.getAll().filter { it.isEnabled }
        val results = mutableMapOf<String, SyncResult>()

        for (sheet in sheets) {
            results[sheet.spreadsheetId] = syncSheet(sheet.spreadsheetId, accountEmail)
        }

        return results
    }

    /**
     * Intenta obtener el título del spreadsheet sin sincronizarlo completo.
     */
    suspend fun fetchSheetTitle(spreadsheetId: String, accountEmail: String): String? {
        return withContext(Dispatchers.IO) {
            try {
                val credential = GoogleAccountCredential
                    .usingOAuth2(context, listOf(SheetsScopes.SPREADSHEETS_READONLY))
                    .apply { selectedAccountName = accountEmail }

                val sheetsService = Sheets.Builder(
                    NetHttpTransport(),
                    GsonFactory.getDefaultInstance(),
                    credential
                ).setApplicationName(APP_NAME).build()

                val spreadsheet = sheetsService.spreadsheets()
                    .get(spreadsheetId)
                    .setFields("properties.title")
                    .execute()

                spreadsheet.properties.title
            } catch (e: Exception) {
                Log.e(TAG, "Error obteniendo título del sheet", e)
                null
            }
        }
    }
}
