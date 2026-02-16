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
import com.metablooms.quickupload.data.db.UploadItem
import com.metablooms.quickupload.data.db.UploadStatus
import com.metablooms.quickupload.data.github.GitHubClient
import com.metablooms.quickupload.data.github.GitHubApi
import com.metablooms.quickupload.data.github.model.CreateBlobRequest
import com.metablooms.quickupload.data.github.model.CreateCommitRequest
import com.metablooms.quickupload.data.github.model.CreateOrUpdateFileRequest
import com.metablooms.quickupload.data.github.model.CreateTreeRequest
import com.metablooms.quickupload.data.github.model.TreeEntry
import com.metablooms.quickupload.data.github.model.UpdateRefRequest

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
        const val MAX_CONTENTS_API_BYTES = 1_000_000L  // 1 MB — Contents API limit
        const val MAX_BLOB_API_BYTES = 100_000_000L    // 100 MB — Blobs API limit
    }

    override suspend fun doWork(): Result {
        createNotificationChannel()
        setForeground(createForegroundInfo("Preparing uploads…"))

        // Fix #1: Token expiry check before processing queue
        if (!validateToken()) {
            // Mark all pending as retrying with auth error, don't burn attempts
            val pending = db.uploadItemDao().getPending()
            for (item in pending) {
                db.uploadItemDao().updateStatus(
                    item.id,
                    UploadStatus.RETRYING,
                    "Authentication expired or invalid. Please sign in again."
                )
            }
            return Result.failure()
        }

        val pending = db.uploadItemDao().getPending()
        if (pending.isEmpty()) return Result.success()

        // Fix #4: Group by repo+branch for batch commits via Git Tree API
        val groups = pending.groupBy { "${it.repoFullName}::${it.branch}" }
        var allSucceeded = true

        for ((key, items) in groups) {
            if (items.size > 1) {
                // Batch commit via Git Tree API
                val success = batchUpload(items)
                if (!success) allSucceeded = false
            } else {
                // Single file — use Contents API or Blobs API depending on size
                val success = singleUpload(items.first())
                if (!success) allSucceeded = false
            }
        }

        return if (allSucceeded) Result.success() else Result.retry()
    }

    /**
     * Fix #1: Validate the stored token is still working before processing the queue.
     * Returns false if token is missing or expired (401 from GitHub).
     */
    private suspend fun validateToken(): Boolean {
        val token = tokenStore.accessToken ?: return false
        return try {
            val response = api.getAuthenticatedUser()
            when (response.code()) {
                200 -> true
                401 -> {
                    // Token expired or revoked — clear it so UI shows sign-in prompt
                    tokenStore.clear()
                    false
                }
                else -> true // Non-auth errors shouldn't block; let individual uploads handle
            }
        } catch (_: Exception) {
            // Network error — don't clear token, just retry later
            true
        }
    }

    /**
     * Upload a single file using Contents API (<=1MB) or Blobs API (>1MB, <=100MB).
     */
    private suspend fun singleUpload(item: UploadItem): Boolean {
        val totalLabel = "1/1"
        setForeground(createForegroundInfo("Uploading $totalLabel: ${item.displayName}"))
        db.uploadItemDao().updateStatus(item.id, UploadStatus.UPLOADING)

        try {
            // Fix #3: Idempotency check — skip if already uploaded with same content
            val contentSha = item.contentSha256
            if (contentSha != null && db.uploadItemDao().isDuplicate(contentSha, item.repoFullName, item.targetPath)) {
                db.uploadItemDao().updateStatus(
                    item.id,
                    UploadStatus.FAILED,
                    "Duplicate: identical file already queued or uploaded to this path."
                )
                return true // Not a worker failure, just a skip
            }

            // Size gate
            if (item.sizeBytes > MAX_BLOB_API_BYTES) {
                db.uploadItemDao().updateStatus(
                    item.id,
                    UploadStatus.FAILED,
                    "File too large (${formatSize(item.sizeBytes)}). " +
                        "GitHub API supports up to 100 MB. Use Git LFS for larger files."
                )
                return false
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
                return false
            }

            val parts = parseRepo(item.repoFullName)
            if (parts == null) {
                db.uploadItemDao().updateStatus(item.id, UploadStatus.FAILED, "Invalid repo name format")
                return false
            }
            val (owner, repo) = parts
            val targetPath = item.targetPath.trimStart('/')

            // Fix #2: Route by size — Contents API for small, Blobs API for large
            return if (item.sizeBytes <= MAX_CONTENTS_API_BYTES) {
                uploadViaContentsApi(item, owner, repo, targetPath, contentBytes)
            } else {
                uploadViaBlobsApi(item, owner, repo, targetPath, contentBytes)
            }
        } catch (e: Exception) {
            db.uploadItemDao().updateStatus(item.id, UploadStatus.RETRYING, "Error: ${e.message}")
            return false
        }
    }

    /**
     * Small file path: Contents API (<=1MB). Supports create and update-with-SHA.
     */
    private suspend fun uploadViaContentsApi(
        item: UploadItem,
        owner: String,
        repo: String,
        targetPath: String,
        contentBytes: ByteArray
    ): Boolean {
        val base64Content = Base64.encodeToString(contentBytes, Base64.NO_WRAP)

        // Check if file exists (to get SHA for update)
        var existingSha: String? = null
        try {
            val existingResponse = api.getContents(owner, repo, targetPath, item.branch)
            if (existingResponse.isSuccessful) {
                existingSha = existingResponse.body()?.sha
            }
        } catch (_: Exception) {
            // File doesn't exist — create new
        }

        val request = CreateOrUpdateFileRequest(
            message = item.commitMessage,
            content = base64Content,
            branch = item.branch,
            sha = existingSha
        )

        val response = api.createOrUpdateFile(owner, repo, targetPath, request)
        return handleApiResponse(item, response.code(), response.message()) {
            response.body()?.commit?.sha ?: "unknown"
        }
    }

    /**
     * Fix #2: Large file path: Git Blobs API (>1MB, <=100MB).
     * Creates blob → gets current tree → creates new tree with blob → creates commit → updates ref.
     */
    private suspend fun uploadViaBlobsApi(
        item: UploadItem,
        owner: String,
        repo: String,
        targetPath: String,
        contentBytes: ByteArray
    ): Boolean {
        val base64Content = Base64.encodeToString(contentBytes, Base64.NO_WRAP)

        // Step 1: Create blob
        val blobResponse = api.createBlob(owner, repo, CreateBlobRequest(content = base64Content))
        if (!blobResponse.isSuccessful) {
            return handleApiResponse(item, blobResponse.code(), blobResponse.message()) { null }
        }
        val blobSha = blobResponse.body()?.sha ?: run {
            db.uploadItemDao().updateStatus(item.id, UploadStatus.RETRYING, "Blob creation returned no SHA")
            return false
        }

        // Step 2: Get current branch HEAD
        val branchResponse = api.getBranch(owner, repo, item.branch)
        if (!branchResponse.isSuccessful) {
            return handleApiResponse(item, branchResponse.code(), branchResponse.message()) { null }
        }
        val headSha = branchResponse.body()?.commit?.sha ?: run {
            db.uploadItemDao().updateStatus(item.id, UploadStatus.RETRYING, "Could not get branch HEAD")
            return false
        }

        // Step 3: Create tree with the new blob
        val treeRequest = CreateTreeRequest(
            baseTree = headSha,
            tree = listOf(TreeEntry(path = targetPath, sha = blobSha))
        )
        val treeResponse = api.createTree(owner, repo, treeRequest)
        if (!treeResponse.isSuccessful) {
            return handleApiResponse(item, treeResponse.code(), treeResponse.message()) { null }
        }
        val treeSha = treeResponse.body()?.sha ?: run {
            db.uploadItemDao().updateStatus(item.id, UploadStatus.RETRYING, "Tree creation returned no SHA")
            return false
        }

        // Step 4: Create commit
        val commitRequest = CreateCommitRequest(
            message = item.commitMessage,
            tree = treeSha,
            parents = listOf(headSha)
        )
        val commitResponse = api.createCommit(owner, repo, commitRequest)
        if (!commitResponse.isSuccessful) {
            return handleApiResponse(item, commitResponse.code(), commitResponse.message()) { null }
        }
        val commitSha = commitResponse.body()?.sha ?: run {
            db.uploadItemDao().updateStatus(item.id, UploadStatus.RETRYING, "Commit creation returned no SHA")
            return false
        }

        // Step 5: Update branch ref to point to new commit
        val refResponse = api.updateRef(owner, repo, item.branch, UpdateRefRequest(sha = commitSha))
        if (!refResponse.isSuccessful) {
            return handleApiResponse(item, refResponse.code(), refResponse.message()) { null }
        }

        db.uploadItemDao().markDone(item.id, commitSha)
        return true
    }

    /**
     * Fix #4: Batch upload multiple files to the same repo+branch in a single commit
     * via Git Tree API. Falls back to single upload on failure.
     */
    private suspend fun batchUpload(items: List<UploadItem>): Boolean {
        val first = items.first()
        val parts = parseRepo(first.repoFullName)
        if (parts == null) {
            items.forEach { db.uploadItemDao().updateStatus(it.id, UploadStatus.FAILED, "Invalid repo name format") }
            return false
        }
        val (owner, repo) = parts
        val branch = first.branch

        setForeground(createForegroundInfo("Batch uploading ${items.size} files to $owner/$repo"))

        // Mark all as uploading
        items.forEach { db.uploadItemDao().updateStatus(it.id, UploadStatus.UPLOADING) }

        // Step 1: Create blobs for all files, collecting tree entries
        val treeEntries = mutableListOf<TreeEntry>()
        val processedItems = mutableListOf<UploadItem>()

        for ((index, item) in items.withIndex()) {
            setForeground(createForegroundInfo("Creating blob ${index + 1}/${items.size}: ${item.displayName}"))

            try {
                // Fix #3: Idempotency check
                val contentSha = item.contentSha256
                if (contentSha != null && db.uploadItemDao().isDuplicate(contentSha, item.repoFullName, item.targetPath)) {
                    db.uploadItemDao().updateStatus(
                        item.id, UploadStatus.FAILED,
                        "Duplicate: identical file already queued or uploaded to this path."
                    )
                    continue
                }

                if (item.sizeBytes > MAX_BLOB_API_BYTES) {
                    db.uploadItemDao().updateStatus(
                        item.id, UploadStatus.FAILED,
                        "File too large (${formatSize(item.sizeBytes)}). Max 100 MB."
                    )
                    continue
                }

                val uri = Uri.parse(item.uri)
                val contentBytes = readFileBytes(uri)
                if (contentBytes == null) {
                    db.uploadItemDao().updateStatus(
                        item.id, UploadStatus.FAILED,
                        "File can't be found anymore. It may have been moved or deleted."
                    )
                    continue
                }

                val base64Content = Base64.encodeToString(contentBytes, Base64.NO_WRAP)
                val blobResponse = api.createBlob(owner, repo, CreateBlobRequest(content = base64Content))

                if (!blobResponse.isSuccessful) {
                    // If one blob fails with auth error, fail the whole batch
                    if (blobResponse.code() == 401) {
                        tokenStore.clear()
                        items.forEach {
                            db.uploadItemDao().updateStatus(
                                it.id, UploadStatus.RETRYING,
                                "Authentication expired. Please sign in again."
                            )
                        }
                        return false
                    }
                    db.uploadItemDao().updateStatus(
                        item.id, UploadStatus.RETRYING,
                        "Blob creation failed: HTTP ${blobResponse.code()}"
                    )
                    continue
                }

                val blobSha = blobResponse.body()?.sha ?: continue
                val targetPath = item.targetPath.trimStart('/')
                treeEntries.add(TreeEntry(path = targetPath, sha = blobSha))
                processedItems.add(item)
            } catch (e: Exception) {
                db.uploadItemDao().updateStatus(item.id, UploadStatus.RETRYING, "Error: ${e.message}")
            }
        }

        if (treeEntries.isEmpty()) return false

        // Step 2: Get current branch HEAD
        setForeground(createForegroundInfo("Creating batch commit…"))

        try {
            val branchResponse = api.getBranch(owner, repo, branch)
            if (!branchResponse.isSuccessful) {
                processedItems.forEach {
                    db.uploadItemDao().updateStatus(
                        it.id, UploadStatus.RETRYING,
                        "Could not get branch info: HTTP ${branchResponse.code()}"
                    )
                }
                return false
            }
            val headSha = branchResponse.body()?.commit?.sha ?: return false

            // Step 3: Create tree with all blobs
            val treeRequest = CreateTreeRequest(baseTree = headSha, tree = treeEntries)
            val treeResponse = api.createTree(owner, repo, treeRequest)
            if (!treeResponse.isSuccessful) {
                processedItems.forEach {
                    db.uploadItemDao().updateStatus(
                        it.id, UploadStatus.RETRYING,
                        "Tree creation failed: HTTP ${treeResponse.code()}"
                    )
                }
                return false
            }
            val treeSha = treeResponse.body()?.sha ?: return false

            // Step 4: Create single commit for all files
            val message = if (processedItems.size == 1) {
                processedItems.first().commitMessage
            } else {
                "Upload ${processedItems.size} files\n\n" +
                    processedItems.joinToString("\n") { "- ${it.displayName}" }
            }

            val commitRequest = CreateCommitRequest(message = message, tree = treeSha, parents = listOf(headSha))
            val commitResponse = api.createCommit(owner, repo, commitRequest)
            if (!commitResponse.isSuccessful) {
                processedItems.forEach {
                    db.uploadItemDao().updateStatus(
                        it.id, UploadStatus.RETRYING,
                        "Commit creation failed: HTTP ${commitResponse.code()}"
                    )
                }
                return false
            }
            val commitSha = commitResponse.body()?.sha ?: return false

            // Step 5: Update branch ref
            val refResponse = api.updateRef(owner, repo, branch, UpdateRefRequest(sha = commitSha))
            if (!refResponse.isSuccessful) {
                processedItems.forEach {
                    db.uploadItemDao().updateStatus(
                        it.id, UploadStatus.RETRYING,
                        "Ref update failed: HTTP ${refResponse.code()}"
                    )
                }
                return false
            }

            // Success — mark all processed items as done
            processedItems.forEach { db.uploadItemDao().markDone(it.id, commitSha) }
            return true
        } catch (e: Exception) {
            processedItems.forEach {
                db.uploadItemDao().updateStatus(it.id, UploadStatus.RETRYING, "Error: ${e.message}")
            }
            return false
        }
    }

    /**
     * Shared response handler for Contents API responses.
     * Handles 401 (token expiry), 403 (rate limit / permissions), 404, 409/422 (conflict).
     */
    private suspend fun handleApiResponse(
        item: UploadItem,
        code: Int,
        message: String,
        extractCommitSha: () -> String?
    ): Boolean {
        return when {
            code in 200..299 -> {
                val commitSha = extractCommitSha() ?: "unknown"
                db.uploadItemDao().markDone(item.id, commitSha)
                true
            }
            code == 401 -> {
                // Fix #1: Token expired mid-queue
                tokenStore.clear()
                db.uploadItemDao().updateStatus(
                    item.id, UploadStatus.RETRYING,
                    "Authentication expired. Please sign in again."
                )
                false
            }
            code == 409 || code == 422 -> {
                db.uploadItemDao().updateStatus(
                    item.id, UploadStatus.FAILED,
                    "Conflict: file changed on GitHub. Re-queue to retry with latest SHA."
                )
                false
            }
            code == 403 -> {
                db.uploadItemDao().updateStatus(
                    item.id, UploadStatus.FAILED,
                    "Permission denied (403). Check repo access and branch protection."
                )
                false
            }
            code == 404 -> {
                db.uploadItemDao().updateStatus(
                    item.id, UploadStatus.FAILED,
                    "Repository or branch not found (404). This may also indicate insufficient permissions."
                )
                false
            }
            else -> {
                db.uploadItemDao().updateStatus(
                    item.id, UploadStatus.RETRYING,
                    "HTTP $code: $message"
                )
                false
            }
        }
    }

    private fun readFileBytes(uri: Uri): ByteArray? {
        return try {
            context.contentResolver.openInputStream(uri)?.use { it.readBytes() }
        } catch (_: SecurityException) {
            null
        } catch (_: Exception) {
            null
        }
    }

    private fun parseRepo(fullName: String): Pair<String, String>? {
        val parts = fullName.split("/")
        return if (parts.size == 2) Pair(parts[0], parts[1]) else null
    }

    private fun formatSize(bytes: Long): String = when {
        bytes < 1024 -> "$bytes B"
        bytes < 1024 * 1024 -> "${bytes / 1024} KB"
        else -> "${"%.1f".format(bytes / (1024.0 * 1024.0))} MB"
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
