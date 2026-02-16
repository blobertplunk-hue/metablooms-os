package com.metablooms.quickupload.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.metablooms.quickupload.data.UploadRepository
import com.metablooms.quickupload.data.db.UploadItem
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class QueueViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = UploadRepository(application)

    val items: StateFlow<List<UploadItem>> = repository.uploadItems
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    fun retryItem(id: Long) {
        viewModelScope.launch {
            repository.retryFailed(id)
        }
    }

    fun removeItem(id: Long) {
        viewModelScope.launch {
            repository.removeItem(id)
        }
    }

    fun clearCompleted() {
        viewModelScope.launch {
            repository.clearCompleted()
        }
    }
}
