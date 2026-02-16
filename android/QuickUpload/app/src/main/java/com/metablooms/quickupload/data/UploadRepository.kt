package com.metablooms.quickupload.data

import android.content.Context
import android.net.Uri
import android.provider.OpenableColumns
import com.metablooms.quickupload.data.auth.TokenStore
import com.metablooms.quickupload.data.db.AppDatabase
import com.metablooms.quickupload.data.db.RepoProfile
import com.metablooms.quickupload.data.db.UploadItem
import com.metablooms.quickupload.data.db.UploadStatus
import com.metablooms.quickupload.data.github.GitHubClient
import com.metablooms.quickupload.data.github.model.GitHubRepo
import com.metablooms.quickupload.worker.UploadScheduler
import kotlinx.coroutines.flow.Flow
import java.security.MessageDigest
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class UploadRepository(private val context: Context) {

    private val db = AppDatabase.getInstance(context)
    private val tokenStore = TokenStore(context)
    private val api = GitHubClient.createApi { tokenStore.accessToken }

    val uploadItems: Flow<List<UploadItem>> = db.uploadItemDao().observeAll()
    val repoProfiles: Flow<List<RepoProfile>> = db.repoProfileDao().observeAll()

    // --- Upload Queue ---

    suspend fun enqueueFile(
        uri: Uri,
        repoFullName: String,
        branch: String,
        targetFolder: String,
        commitMessage: String? = null
    ): Long {
        val fileInfo = getFileInfo(uri)
        val displayName = fileInfo.first
        val sizeBytes = fileInfo.second

        val dateFolder = SimpleDateFormat("yyyy-MM-dd", Locale.US).format(Date())
        val folder = targetFolder.trimEnd('/')
        val targetPath = "$folder/$dateFolder/$displayName"

        val contentSha = computeContentSha(uri)

        val message = commitMessage ?: "Upload $displayName"

        val item = UploadItem(
            uri = uri.toString(),
            displayName = displayName,
            sizeBytes = sizeBytes,
            contentSha256 = contentSha,
            repoFullName = repoFullName,
            branch = branch,
            targetPath = targetPath,
            commitMessage = message
        )

        val id = db.uploadItemDao().insert(item)
        UploadScheduler.enqueueUploadWork(context)
        return id
    }

    suspend fun enqueueFiles(
        uris: List<Uri>,
        repoFullName: String,
        branch: String,
        targetFolder: String
    ): List<Long> {
        return uris.map { uri ->
            enqueueFile(uri, repoFullName, branch, targetFolder)
        }
    }

    suspend fun retryFailed(itemId: Long) {
        db.uploadItemDao().updateStatus(itemId, UploadStatus.QUEUED)
        UploadScheduler.enqueueUploadWork(context)
    }

    suspend fun removeItem(itemId: Long) {
        db.uploadItemDao().delete(itemId)
    }

    suspend fun clearCompleted() {
        db.uploadItemDao().clearCompleted()
    }

    // --- Repos ---

    suspend fun fetchUserRepos(): Result<List<GitHubRepo>> {
        return try {
            val response = api.listUserRepos()
            if (response.isSuccessful) {
                Result.success(response.body() ?: emptyList())
            } else {
                Result.failure(Exception("Failed to fetch repos: ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun saveRepoProfile(profile: RepoProfile) {
        db.repoProfileDao().upsert(profile)
    }

    suspend fun getMostRecentRepo(): RepoProfile? {
        return db.repoProfileDao().getMostRecent()
    }

    // --- Helpers ---

    private fun getFileInfo(uri: Uri): Pair<String, Long> {
        var name = "unknown"
        var size = 0L
        context.contentResolver.query(uri, null, null, null, null)?.use { cursor ->
            if (cursor.moveToFirst()) {
                val nameIndex = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                val sizeIndex = cursor.getColumnIndex(OpenableColumns.SIZE)
                if (nameIndex >= 0) name = cursor.getString(nameIndex) ?: "unknown"
                if (sizeIndex >= 0) size = cursor.getLong(sizeIndex)
            }
        }
        return Pair(name, size)
    }

    private fun computeContentSha(uri: Uri): String? {
        return try {
            val digest = MessageDigest.getInstance("SHA-256")
            context.contentResolver.openInputStream(uri)?.use { input ->
                val buffer = ByteArray(8192)
                var bytesRead: Int
                while (input.read(buffer).also { bytesRead = it } != -1) {
                    digest.update(buffer, 0, bytesRead)
                }
            }
            digest.digest().joinToString("") { "%02x".format(it) }
        } catch (e: Exception) {
            null
        }
    }
}
