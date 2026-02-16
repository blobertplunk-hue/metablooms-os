package com.metablooms.quickupload.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.metablooms.quickupload.BuildConfig
import com.metablooms.quickupload.data.auth.DeviceFlowAuth
import com.metablooms.quickupload.data.auth.TokenStore
import com.metablooms.quickupload.data.github.GitHubClient
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class AuthUiState(
    val isLoggedIn: Boolean = false,
    val username: String? = null,
    val avatarUrl: String? = null,
    val isLoading: Boolean = false,
    val userCode: String? = null,
    val verificationUri: String? = null,
    val error: String? = null
)

class AuthViewModel(application: Application) : AndroidViewModel(application) {

    private val tokenStore = TokenStore(application)
    private val authApi = GitHubClient.createAuthApi()
    private val deviceFlowAuth = DeviceFlowAuth(authApi, BuildConfig.GITHUB_CLIENT_ID)

    private val _uiState = MutableStateFlow(
        AuthUiState(
            isLoggedIn = tokenStore.isLoggedIn,
            username = tokenStore.username,
            avatarUrl = tokenStore.avatarUrl
        )
    )
    val uiState: StateFlow<AuthUiState> = _uiState

    fun startDeviceFlow() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)

            val codeResult = deviceFlowAuth.requestDeviceCode()
            codeResult.fold(
                onSuccess = { codeResponse ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        userCode = codeResponse.userCode,
                        verificationUri = codeResponse.verificationUri
                    )

                    // Start polling in background
                    val tokenResult = deviceFlowAuth.pollForToken(
                        codeResponse.deviceCode,
                        codeResponse.interval
                    )

                    when (tokenResult) {
                        is DeviceFlowAuth.AuthResult.Success -> {
                            tokenStore.accessToken = tokenResult.accessToken
                            fetchAndStoreUser()
                        }
                        is DeviceFlowAuth.AuthResult.Error -> {
                            _uiState.value = _uiState.value.copy(
                                error = tokenResult.message,
                                userCode = null,
                                verificationUri = null
                            )
                        }
                        else -> {}
                    }
                },
                onFailure = { error ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = "Failed to start sign-in: ${error.message}"
                    )
                }
            )
        }
    }

    fun loginWithPat(token: String) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            tokenStore.accessToken = token
            fetchAndStoreUser()
        }
    }

    fun logout() {
        tokenStore.clear()
        _uiState.value = AuthUiState(isLoggedIn = false)
    }

    private suspend fun fetchAndStoreUser() {
        try {
            val api = GitHubClient.createApi { tokenStore.accessToken }
            val response = api.getAuthenticatedUser()
            if (response.isSuccessful) {
                val user = response.body()!!
                tokenStore.username = user.login
                tokenStore.avatarUrl = user.avatarUrl
                _uiState.value = AuthUiState(
                    isLoggedIn = true,
                    username = user.login,
                    avatarUrl = user.avatarUrl
                )
            } else {
                tokenStore.clear()
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = "Invalid token: ${response.code()}"
                )
            }
        } catch (e: Exception) {
            tokenStore.clear()
            _uiState.value = _uiState.value.copy(
                isLoading = false,
                error = "Network error: ${e.message}"
            )
        }
    }
}
