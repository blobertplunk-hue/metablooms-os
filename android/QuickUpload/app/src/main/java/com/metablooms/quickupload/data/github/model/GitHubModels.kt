package com.metablooms.quickupload.data.github.model

import com.google.gson.annotations.SerializedName

// --- Device Flow Auth ---

data class DeviceCodeRequest(
    @SerializedName("client_id") val clientId: String,
    val scope: String = "repo"
)

data class DeviceCodeResponse(
    @SerializedName("device_code") val deviceCode: String,
    @SerializedName("user_code") val userCode: String,
    @SerializedName("verification_uri") val verificationUri: String,
    @SerializedName("expires_in") val expiresIn: Int,
    val interval: Int
)

data class AccessTokenRequest(
    @SerializedName("client_id") val clientId: String,
    @SerializedName("device_code") val deviceCode: String,
    @SerializedName("grant_type") val grantType: String = "urn:ietf:params:oauth:grant-type:device_code"
)

data class AccessTokenResponse(
    @SerializedName("access_token") val accessToken: String?,
    @SerializedName("token_type") val tokenType: String?,
    val scope: String?,
    val error: String?,
    @SerializedName("error_description") val errorDescription: String?,
    val interval: Int?
)

// --- GitHub User ---

data class GitHubUser(
    val login: String,
    @SerializedName("avatar_url") val avatarUrl: String?,
    val name: String?
)

// --- Repository ---

data class GitHubRepo(
    @SerializedName("full_name") val fullName: String,
    val name: String,
    val private: Boolean,
    @SerializedName("default_branch") val defaultBranch: String,
    val permissions: RepoPermissions?
)

data class RepoPermissions(
    val push: Boolean,
    val pull: Boolean,
    val admin: Boolean
)

// --- Contents API ---

data class GitHubContent(
    val name: String,
    val path: String,
    val sha: String,
    val size: Long,
    val type: String // "file" or "dir"
)

data class CreateOrUpdateFileRequest(
    val message: String,
    val content: String, // Base64-encoded
    val branch: String,
    val sha: String? = null // required for updates
)

data class CreateOrUpdateFileResponse(
    val content: GitHubContent?,
    val commit: CommitInfo
)

data class CommitInfo(
    val sha: String,
    val message: String
)

// --- Branch ---

data class GitHubBranch(
    val name: String,
    val commit: BranchCommit
)

data class BranchCommit(
    val sha: String
)

data class CreateBranchRequest(
    val ref: String, // "refs/heads/branch-name"
    val sha: String
)

// --- Rate Limit ---

data class RateLimitResponse(
    val resources: RateLimitResources
)

data class RateLimitResources(
    val core: RateLimit
)

data class RateLimit(
    val limit: Int,
    val remaining: Int,
    val reset: Long
)
