package com.travlytic.app

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class MinitoApp : Application() {
    override fun onCreate() {
        super.onCreate()
    }
}
