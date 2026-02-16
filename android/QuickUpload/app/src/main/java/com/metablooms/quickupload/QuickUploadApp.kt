package com.metablooms.quickupload

import android.app.Application
import androidx.work.Configuration
import com.metablooms.quickupload.data.db.AppDatabase

class QuickUploadApp : Application(), Configuration.Provider {

    lateinit var database: AppDatabase
        private set

    override fun onCreate() {
        super.onCreate()
        database = AppDatabase.getInstance(this)
    }

    override val workManagerConfiguration: Configuration
        get() = Configuration.Builder()
            .setMinimumLoggingLevel(android.util.Log.INFO)
            .build()
}
