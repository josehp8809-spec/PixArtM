package com.travlytic.app

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class TravlyticApp : Application() {
    override fun onCreate() {
        super.onCreate()
    }
}
