package com.metablooms.quickupload.viewmodel

import android.app.Application
import android.net.Uri
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.metablooms.quickupload.data.UploadRepository
import com.metablooms.quickupload.data.db.RepoProfile
import com.metablooms.quickupload.data.github.model.GitHubRepo
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class HomeUiState(
    val repos: List<GitHubRepo> = emptyList(),
    val selectedRepo: RepoProfile? = null,
    val isLoadingRepos: Boolean = false,
    val selectedFiles: List<Uri> = emptyList(),
    val commitMessage: String = "",
    val isEnqueuing: Boolean = false,
    val error: String? = null,
    val enqueueSuccess: Boolean = false
)

class HomeViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = UploadRepository(application)

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState

    init {
        loadLastRepo()
    }

    fun loadRepos() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoadingRepos = true, error = null)
            repository.fetchUserRepos().fold(
                onSuccess = { repos ->
                    _uiState.value = _uiState.value.copy(
                        repos = repos,
                        isLoadingRepos = false
                    )
                },
                onFailure = { error ->
                    _uiState.value = _uiState.value.copy(
                        isLoadingRepos = false,
                        error = "Failed to load repos: ${error.message}"
                    )
                }
            )
        }
    }

    fun selectRepo(repo: GitHubRepo) {
        val profile = RepoProfile(
            repoFullName = repo.fullName,
            defaultBranch = repo.defaultBranch
        )
        viewModelScope.launch {
            repository.saveRepoProfile(profile)
            _uiState.value = _uiState.value.copy(selectedRepo = profile)
        }
    }

    fun setSelectedFiles(uris: List<Uri>) {
        _uiState.value = _uiState.value.copy(
            selectedFiles = uris,
            enqueueSuccess = false
        )
    }

    fun setCommitMessage(message: String) {
        _uiState.value = _uiState.value.copy(commitMessage = message)
    }

    fun enqueueUpload() {
        val state = _uiState.value
        val repo = state.selectedRepo ?: return
        val files = state.selectedFiles
        if (files.isEmpty()) return

        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isEnqueuing = true, error = null)
            try {
                repository.enqueueFiles(
                    uris = files,
                    repoFullName = repo.repoFullName,
                    branch = repo.defaultBranch,
                    targetFolder = repo.defaultFolder
                )
                _uiState.value = _uiState.value.copy(
                    isEnqueuing = false,
                    selectedFiles = emptyList(),
                    commitMessage = "",
                    enqueueSuccess = true
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isEnqueuing = false,
                    error = "Failed to enqueue: ${e.message}"
                )
            }
        }
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }

    private fun loadLastRepo() {
        viewModelScope.launch {
            val lastRepo = repository.getMostRecentRepo()
            _uiState.value = _uiState.value.copy(selectedRepo = lastRepo)
        }
    }
}
