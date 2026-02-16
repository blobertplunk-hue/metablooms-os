package com.metablooms.quickupload.data.github

import com.metablooms.quickupload.data.github.model.*
import retrofit2.Response
import retrofit2.http.*

interface GitHubApi {

    // --- Contents API ---

    @GET("repos/{owner}/{repo}/contents/{path}")
    suspend fun getContents(
        @Path("owner") owner: String,
        @Path("repo") repo: String,
        @Path("path", encoded = true) path: String,
        @Query("ref") ref: String? = null
    ): Response<GitHubContent>

    @PUT("repos/{owner}/{repo}/contents/{path}")
    suspend fun createOrUpdateFile(
        @Path("owner") owner: String,
        @Path("repo") repo: String,
        @Path("path", encoded = true) path: String,
        @Body body: CreateOrUpdateFileRequest
    ): Response<CreateOrUpdateFileResponse>

    // --- Repos ---

    @GET("user/repos")
    suspend fun listUserRepos(
        @Query("sort") sort: String = "pushed",
        @Query("per_page") perPage: Int = 30,
        @Query("page") page: Int = 1,
        @Query("affiliation") affiliation: String = "owner,collaborator,organization_member"
    ): Response<List<GitHubRepo>>

    @GET("repos/{owner}/{repo}")
    suspend fun getRepo(
        @Path("owner") owner: String,
        @Path("repo") repo: String
    ): Response<GitHubRepo>

    // --- Branches ---

    @GET("repos/{owner}/{repo}/branches/{branch}")
    suspend fun getBranch(
        @Path("owner") owner: String,
        @Path("repo") repo: String,
        @Path("branch") branch: String
    ): Response<GitHubBranch>

    @POST("repos/{owner}/{repo}/git/refs")
    suspend fun createBranch(
        @Path("owner") owner: String,
        @Path("repo") repo: String,
        @Body body: CreateBranchRequest
    ): Response<Any>

    // --- Git Data API (Blobs, Trees, Commits) ---

    @POST("repos/{owner}/{repo}/git/blobs")
    suspend fun createBlob(
        @Path("owner") owner: String,
        @Path("repo") repo: String,
        @Body body: CreateBlobRequest
    ): Response<CreateBlobResponse>

    @POST("repos/{owner}/{repo}/git/trees")
    suspend fun createTree(
        @Path("owner") owner: String,
        @Path("repo") repo: String,
        @Body body: CreateTreeRequest
    ): Response<CreateTreeResponse>

    @POST("repos/{owner}/{repo}/git/commits")
    suspend fun createCommit(
        @Path("owner") owner: String,
        @Path("repo") repo: String,
        @Body body: CreateCommitRequest
    ): Response<CreateCommitResponse>

    @PATCH("repos/{owner}/{repo}/git/refs/heads/{branch}")
    suspend fun updateRef(
        @Path("owner") owner: String,
        @Path("repo") repo: String,
        @Path("branch") branch: String,
        @Body body: UpdateRefRequest
    ): Response<Any>

    // --- User ---

    @GET("user")
    suspend fun getAuthenticatedUser(): Response<GitHubUser>

    // --- Rate Limit ---

    @GET("rate_limit")
    suspend fun getRateLimit(): Response<RateLimitResponse>
}
