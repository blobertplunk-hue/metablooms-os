package com.metablooms.quickupload.data.db

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import androidx.room.Update
import kotlinx.coroutines.flow.Flow

@Dao
interface UploadItemDao {

    @Insert
    suspend fun insert(item: UploadItem): Long

    @Insert
    suspend fun insertAll(items: List<UploadItem>): List<Long>

    @Update
    suspend fun update(item: UploadItem)

    @Query("SELECT * FROM upload_items ORDER BY createdAt DESC")
    fun observeAll(): Flow<List<UploadItem>>

    @Query("SELECT * FROM upload_items WHERE status IN ('QUEUED', 'RETRYING') ORDER BY createdAt ASC")
    suspend fun getPending(): List<UploadItem>

    @Query("SELECT * FROM upload_items WHERE id = :id")
    suspend fun getById(id: Long): UploadItem?

    @Query("UPDATE upload_items SET status = :status, lastError = :error, attempts = attempts + 1, updatedAt = :now WHERE id = :id")
    suspend fun updateStatus(id: Long, status: UploadStatus, error: String? = null, now: Long = System.currentTimeMillis())

    @Query("UPDATE upload_items SET status = 'DONE', remoteSha = :sha, updatedAt = :now WHERE id = :id")
    suspend fun markDone(id: Long, sha: String, now: Long = System.currentTimeMillis())

    @Query("DELETE FROM upload_items WHERE id = :id")
    suspend fun delete(id: Long)

    @Query("DELETE FROM upload_items WHERE status = 'DONE'")
    suspend fun clearCompleted()

    @Query("SELECT EXISTS(SELECT 1 FROM upload_items WHERE contentSha256 = :sha AND repoFullName = :repo AND targetPath = :path AND status != 'FAILED')")
    suspend fun isDuplicate(sha: String, repo: String, path: String): Boolean
}
