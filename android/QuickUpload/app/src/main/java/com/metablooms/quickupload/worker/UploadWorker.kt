package com.metablooms.quickupload.worker

import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.net.Uri
import android.util.Base64
import androidx.core.app.NotificationCompat
import androidx.work.CoroutineWorker
import androidx.work.ForegroundInfo
import androidx.work.WorkerParameters
import com.metablooms.quickupload.R
import com.metablooms.quickupload.data.auth.TokenStore
import com.metablooms.quickupload.data.db.AppDatabase
import com.metablooms.quickupload.data.db.UploadStatus
import com.metablooms.quickupload.data.github.GitHubClient
import com.metablooms.quickupload.data.github.model.CreateOrUpdateFileRequest
import java.security.MessageDigest

class UploadWorker(
    private val context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    private val db = AppDatabase.getInstance(context)
    private val tokenStore = TokenStore(context)
    private val api = GitHubClient.createApi { tokenStore.accessToken }

    companion object {
        const val WORK_NAME = "upload_queue"
        const val NOTIFICATION_CHANNEL_ID = "upload_channel"
        const val NOTIFICATION_ID = 1001
        const val MAX_DIRECT_UPLOAD_BYTES = 1_000_000L // 1 MB via Contents API
    }

    override suspend fun doWork(): Result {
        createNotificationChannel()
        setForeground(createForegroundInfo("Preparing uploads…"))

        val pending = db.uploadItemDao().getPending()
        if (pending.isEmpty()) return Result.success()

        var allSucceeded = true

        for ((index, item) in pending.withIndex()) {
            val progress = "${index + 1}/${pending.size}"
            setForeground(createForegroundInfo("Uploading $progress: ${item.displayName}"))

            db.uploadItemDao().updateStatus(item.id, UploadStatus.UPLOADING)

            try {
                // Size gate
                if (item.sizeBytes > MAX_DIRECT_UPLOAD_BYTES) {
                    db.uploadItemDao().updateStatus(
                        item.id,
                        UploadStatus.FAILED,
                        "File too large for direct API upload (${item.sizeBytes} bytes). " +
                            "Consider using Git LFS for files over 1 MB."
                    )
                    allSucceeded = false
                    continue
                }

                // Read file content
                val uri = Uri.parse(item.uri)
                val contentBytes = readFileBytes(uri)
                if (contentBytes == null) {
                    db.uploadItemDao().updateStatus(
                        item.id,
                        UploadStatus.FAILED,
                        "File can't be found anymore. It may have been moved or deleted."
                    )
                    allSucceeded = false
                    continue
                }

                val base64Content = Base64.encodeToString(contentBytes, Base64.NO_WRAP)

                // Parse owner/repo
                val parts = item.repoFullName.split("/")
                if (parts.size != 2) {
                    db.uploadItemDao().updateStatus(item.id, UploadStatus.FAILED, "Invalid repo name format")
                    allSucceeded = false
                    continue
                }
                val (owner, repo) = parts

                // Clean target path (remove leading /)
                val targetPath = item.targetPath.trimStart('/')

                // Check if file exists (to get SHA for update)
                var existingSha: String? = null
                try {
                    val existingResponse = api.getContents(owner, repo, targetPath, item.branch)
                    if (existingResponse.isSuccessful) {
                        existingSha = existingResponse.body()?.sha
                    }
                } catch (_: Exception) {
                    // File doesn't exist, that's fine — create new
                }

                // Create or update file
                val request = CreateOrUpdateFileRequest(
                    message = item.commitMessage,
                    content = base64Content,
                    branch = item.branch,
                    sha = existingSha
                )

                val response = api.createOrUpdateFile(owner, repo, targetPath, request)

                when {
                    response.isSuccessful -> {
                        val commitSha = response.body()?.commit?.sha ?: "unknown"
                        db.uploadItemDao().markDone(item.id, commitSha)
                    }
                    response.code() == 409 || response.code() == 422 -> {
                        // Conflict — file changed on remote
                        db.uploadItemDao().updateStatus(
                            item.id,
                            UploadStatus.FAILED,
                            "Conflict: file changed on GitHub. Re-queue to retry with latest SHA."
                        )
                        allSucceeded = false
                    }
                    response.code() == 403 -> {
                        val rateLimitRemaining = response.headers()["x-ratelimit-remaining"]?.toIntOrNull()
                        if (rateLimitRemaining != null && rateLimitRemaining <= 0) {
                            val resetTime = response.headers()["x-ratelimit-reset"]?.toLongOrNull()
                            db.uploadItemDao().updateStatus(
                                item.id,
                                UploadStatus.RETRYING,
                                "Rate limited. Resets at ${resetTime ?: "unknown"}."
                            )
                        } else {
                            db.uploadItemDao().updateStatus(
                                item.id,
                                UploadStatus.FAILED,
                                "Permission denied (403). Check repo access and branch protection."
                            )
                        }
                        allSucceeded = false
                    }
                    response.code() == 404 -> {
                        db.uploadItemDao().updateStatus(
                            item.id,
                            UploadStatus.FAILED,
                            "Repository or branch not found (404). This may also indicate insufficient permissions."
                        )
                        allSucceeded = false
                    }
                    else -> {
                        db.uploadItemDao().updateStatus(
                            item.id,
                            UploadStatus.RETRYING,
                            "HTTP ${response.code()}: ${response.message()}"
                        )
                        allSucceeded = false
                    }
                }
            } catch (e: Exception) {
                db.uploadItemDao().updateStatus(
                    item.id,
                    UploadStatus.RETRYING,
                    "Error: ${e.message}"
                )
                allSucceeded = false
            }
        }

        return if (allSucceeded) Result.success() else Result.retry()
    }

    private fun readFileBytes(uri: Uri): ByteArray? {
        return try {
            context.contentResolver.openInputStream(uri)?.use { it.readBytes() }
        } catch (e: SecurityException) {
            // Persisted URI grant revoked or stale
            null
        } catch (e: Exception) {
            null
        }
    }

    private fun createForegroundInfo(message: String): ForegroundInfo {
        val notification = NotificationCompat.Builder(context, NOTIFICATION_CHANNEL_ID)
            .setContentTitle("QuickUpload")
            .setContentText(message)
            .setSmallIcon(R.drawable.ic_upload)
            .setOngoing(true)
            .build()
        return ForegroundInfo(NOTIFICATION_ID, notification)
    }

    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            NOTIFICATION_CHANNEL_ID,
            "Upload Progress",
            NotificationManager.IMPORTANCE_LOW
        ).apply {
            description = "Shows upload progress for GitHub file uploads"
        }
        val manager = context.getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(channel)
    }
}
