package com.travlytic.app.data.repository

import android.content.Context
import android.net.Uri
import com.travlytic.app.data.db.dao.KnowledgeItemDao
import com.travlytic.app.data.db.entities.KnowledgeItem
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.apache.poi.ss.usermodel.WorkbookFactory
import java.io.InputStream
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class KnowledgeRepository @Inject constructor(
    private val dao: KnowledgeItemDao,
    @ApplicationContext private val context: Context
) {

    val knowledgeItemsFlow = dao.getAllFlow()

    suspend fun getEnabledContextString(): String {
        return withContext(Dispatchers.IO) {
            val items = dao.getEnabledItems()
            if (items.isEmpty()) return@withContext ""
            
            val sb = java.lang.StringBuilder()
            for (item in items) {
                sb.appendLine("=== Fuente: ${item.reference} ===")
                sb.appendLine(item.content)
                sb.appendLine()
            }
            sb.toString()
        }
    }

    suspend fun importExcel(uri: Uri, reference: String) {
        withContext(Dispatchers.IO) {
            try {
                val content = StringBuilder()
                var isCsv = false

                // Intento 1: Leer como texto plano (CSV básico)
                try {
                    context.contentResolver.openInputStream(uri)?.use { inputStream ->
                        val text = inputStream.bufferedReader().readText()
                        // Verificamos si es texto y no un binario zip (.xlsx empiezan con PK)
                        if (text.isNotBlank() && !text.startsWith("PK")) {
                            val lines = text.split("\n", "\r")
                            for (line in lines) {
                                if (line.isNotBlank()) content.appendLine(line.replace(",", " | ").replace(";", " | "))
                            }
                            if (content.length > 10) isCsv = true
                        }
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                }

                // Intento 2: POI para Excel Binario (.xlsx / .xls)
                if (!isCsv) {
                    content.clear()
                    context.contentResolver.openInputStream(uri)?.use { inputStream ->
                        val workbook = WorkbookFactory.create(inputStream)
                        val sheet = workbook.getSheetAt(0)
                        for (row in sheet) {
                            val rowValues = mutableListOf<String>()
                            for (cell in row) {
                                rowValues.add(cell.toString())
                            }
                            val rowStr = rowValues.joinToString(" | ")
                            if (rowStr.isNotBlank()) {
                                content.appendLine(rowStr)
                            }
                        }
                        workbook.close()
                    }
                }

                if (content.isEmpty()) throw Exception("El documento está vacío o no soportado")

                val item = KnowledgeItem(
                    type = "excel",
                    reference = reference,
                    source = uri.toString(),
                    content = content.toString(),
                    lastUpdated = System.currentTimeMillis()
                )
                dao.insert(item)
            } catch (e: Exception) {
                e.printStackTrace()
                throw e
            }
        }
    }

    suspend fun toggleItem(item: KnowledgeItem, enabled: Boolean) {
        withContext(Dispatchers.IO) {
            dao.update(item.copy(isEnabled = enabled))
        }
    }

    suspend fun deleteItem(item: KnowledgeItem) {
        withContext(Dispatchers.IO) {
            dao.delete(item)
        }
    }
    
    suspend fun deleteAllExcelItems() {
        withContext(Dispatchers.IO) {
            dao.deleteAllExcelItems()
        }
    }
}
