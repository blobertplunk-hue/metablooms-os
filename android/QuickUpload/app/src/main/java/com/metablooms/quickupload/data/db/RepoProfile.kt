package com.metablooms.quickupload.data.db

import androidx.room.Entity
import androidx.room.PrimaryKey

enum class OverwritePolicy {
    NEVER,
    ASK,
    ALWAYS
}

enum class PrPolicy {
    DIRECT_PUSH,
    ALWAYS_PR,
    PR_IF_PROTECTED
}

@Entity(tableName = "repo_profiles")
data class RepoProfile(
    @PrimaryKey val repoFullName: String,
    val defaultBranch: String = "main",
    val defaultFolder: String = "/uploads",
    val useDateFolder: Boolean = true,
    val overwritePolicy: OverwritePolicy = OverwritePolicy.NEVER,
    val prPolicy: PrPolicy = PrPolicy.PR_IF_PROTECTED,
    val lastUsedAt: Long = System.currentTimeMillis()
)
