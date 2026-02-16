package com.metablooms.quickupload.data.db

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import kotlinx.coroutines.flow.Flow

@Dao
interface RepoProfileDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(profile: RepoProfile)

    @Update
    suspend fun update(profile: RepoProfile)

    @Query("SELECT * FROM repo_profiles ORDER BY lastUsedAt DESC")
    fun observeAll(): Flow<List<RepoProfile>>

    @Query("SELECT * FROM repo_profiles ORDER BY lastUsedAt DESC LIMIT 1")
    suspend fun getMostRecent(): RepoProfile?

    @Query("SELECT * FROM repo_profiles WHERE repoFullName = :name")
    suspend fun getByName(name: String): RepoProfile?

    @Query("DELETE FROM repo_profiles WHERE repoFullName = :name")
    suspend fun delete(name: String)
}
