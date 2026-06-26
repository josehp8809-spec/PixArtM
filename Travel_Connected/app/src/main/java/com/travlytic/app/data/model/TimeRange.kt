package com.travlytic.app.data.model

data class TimeRange(
    val startHour: Int,
    val startMinute: Int,
    val endHour: Int,
    val endMinute: Int,
    val activeDays: Set<Int>? = setOf(1, 2, 3, 4, 5, 6, 7)
) {
    fun getSafeDays(): Set<Int> = activeDays ?: setOf(1, 2, 3, 4, 5, 6, 7)
}

