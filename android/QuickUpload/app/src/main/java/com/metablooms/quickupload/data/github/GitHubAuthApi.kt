package com.metablooms.quickupload.data.github

import com.metablooms.quickupload.data.github.model.AccessTokenResponse
import com.metablooms.quickupload.data.github.model.DeviceCodeResponse
import retrofit2.Response
import retrofit2.http.Field
import retrofit2.http.FormUrlEncoded
import retrofit2.http.Headers
import retrofit2.http.POST

/**
 * Separate Retrofit interface for github.com auth endpoints (not api.github.com).
 */
interface GitHubAuthApi {

    @FormUrlEncoded
    @Headers("Accept: application/json")
    @POST("login/device/code")
    suspend fun requestDeviceCode(
        @Field("client_id") clientId: String,
        @Field("scope") scope: String = "repo"
    ): Response<DeviceCodeResponse>

    @FormUrlEncoded
    @Headers("Accept: application/json")
    @POST("login/oauth/access_token")
    suspend fun pollAccessToken(
        @Field("client_id") clientId: String,
        @Field("device_code") deviceCode: String,
        @Field("grant_type") grantType: String = "urn:ietf:params:oauth:grant-type:device_code"
    ): Response<AccessTokenResponse>
}
