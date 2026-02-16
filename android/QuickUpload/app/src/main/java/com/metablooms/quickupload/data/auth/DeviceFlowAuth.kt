package com.metablooms.quickupload.data.auth

import com.metablooms.quickupload.data.github.GitHubAuthApi
import com.metablooms.quickupload.data.github.model.DeviceCodeResponse
import kotlinx.coroutines.delay

/**
 * Implements GitHub OAuth device flow.
 * User sees a code, opens github.com/login/device, enters it.
 * We poll until authorized or expired.
 */
class DeviceFlowAuth(
    private val authApi: GitHubAuthApi,
    private val clientId: String
) {

    sealed class AuthResult {
        data class PendingUserAction(
            val userCode: String,
            val verificationUri: String,
            val expiresInSeconds: Int
        ) : AuthResult()

        data class Success(val accessToken: String) : AuthResult()
        data class Error(val message: String) : AuthResult()
    }

    /**
     * Step 1: Request device code from GitHub.
     */
    suspend fun requestDeviceCode(): Result<DeviceCodeResponse> {
        return try {
            val response = authApi.requestDeviceCode(clientId = clientId)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Device code request failed: ${response.code()} ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Step 2: Poll for access token. Respects server-provided interval.
     * This is a suspending function that blocks until success, expiry, or error.
     */
    suspend fun pollForToken(deviceCode: String, initialInterval: Int): AuthResult {
        var interval = initialInterval.toLong()

        while (true) {
            delay(interval * 1000)

            try {
                val response = authApi.pollAccessToken(
                    clientId = clientId,
                    deviceCode = deviceCode
                )
                val body = response.body()

                if (body == null) {
                    return AuthResult.Error("Empty response from GitHub")
                }

                when {
                    body.accessToken != null -> {
                        return AuthResult.Success(body.accessToken)
                    }
                    body.error == "authorization_pending" -> {
                        // User hasn't entered code yet, keep polling
                        continue
                    }
                    body.error == "slow_down" -> {
                        // Server says slow down; increase interval
                        interval = (body.interval?.toLong() ?: (interval + 5))
                        continue
                    }
                    body.error == "expired_token" -> {
                        return AuthResult.Error("Authorization expired. Please try again.")
                    }
                    body.error == "access_denied" -> {
                        return AuthResult.Error("Authorization was denied.")
                    }
                    else -> {
                        return AuthResult.Error(body.errorDescription ?: body.error ?: "Unknown error")
                    }
                }
            } catch (e: Exception) {
                return AuthResult.Error("Network error: ${e.message}")
            }
        }
    }
}
