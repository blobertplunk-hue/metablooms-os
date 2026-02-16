package com.metablooms.quickupload.data.db

import androidx.room.Entity
import androidx.room.PrimaryKey

enum class UploadStatus {
    QUEUED,
    UPLOADING,
    RETRYING,
    FAILED,
    DONE
}

@Entity(tableName = "upload_items")
data class UploadItem(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val uri: String,
    val displayName: String,
    val sizeBytes: Long,
    val contentSha256: String? = null,
    val repoFullName: String,
    val branch: String,
    val targetPath: String,
    val commitMessage: String,
    val status: UploadStatus = UploadStatus.QUEUED,
    val attempts: Int = 0,
    val lastError: String? = null,
    val remoteSha: String? = null,
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
)
