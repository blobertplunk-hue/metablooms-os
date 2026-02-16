package com.metablooms.quickupload.ui.screens

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.metablooms.quickupload.data.db.RepoProfile
import com.metablooms.quickupload.data.github.model.GitHubRepo
import com.metablooms.quickupload.viewmodel.HomeUiState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    uiState: HomeUiState,
    isLoggedIn: Boolean,
    onNavigateToAuth: () -> Unit,
    onLoadRepos: () -> Unit,
    onSelectRepo: (GitHubRepo) -> Unit,
    onFilesSelected: (List<Uri>) -> Unit,
    onCommitMessageChanged: (String) -> Unit,
    onUpload: () -> Unit,
    onClearError: () -> Unit
) {
    var showRepoDialog by remember { mutableStateOf(false) }

    val filePickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenMultipleDocuments()
    ) { uris: List<Uri> ->
        if (uris.isNotEmpty()) {
            onFilesSelected(uris)
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Sign-in prompt if not logged in
        if (!isLoggedIn) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.secondaryContainer
                )
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Default.AccountCircle, contentDescription = null)
                    Spacer(modifier = Modifier.width(12.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text("Sign in to GitHub", style = MaterialTheme.typography.titleSmall)
                        Text(
                            "Required to upload files",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSecondaryContainer
                        )
                    }
                    FilledTonalButton(onClick = onNavigateToAuth) {
                        Text("Sign in")
                    }
                }
            }
            Spacer(modifier = Modifier.height(16.dp))
        }

        // Repo selector
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Repository", style = MaterialTheme.typography.labelLarge)
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedButton(
                    onClick = {
                        showRepoDialog = true
                        onLoadRepos()
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = isLoggedIn
                ) {
                    Icon(Icons.Default.FolderOpen, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = uiState.selectedRepo?.repoFullName ?: "Select a repository",
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }
                uiState.selectedRepo?.let { repo ->
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "Branch: ${repo.defaultBranch} · Folder: ${repo.defaultFolder}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // File picker
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Files", style = MaterialTheme.typography.labelLarge)
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedButton(
                    onClick = { filePickerLauncher.launch(arrayOf("*/*")) },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = isLoggedIn && uiState.selectedRepo != null
                ) {
                    Icon(Icons.Default.AttachFile, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        if (uiState.selectedFiles.isEmpty()) "Pick files"
                        else "${uiState.selectedFiles.size} file(s) selected"
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Commit message
        if (uiState.selectedFiles.isNotEmpty()) {
            OutlinedTextField(
                value = uiState.commitMessage,
                onValueChange = onCommitMessageChanged,
                label = { Text("Commit message (optional)") },
                placeholder = { Text("Upload files") },
                modifier = Modifier.fillMaxWidth(),
                maxLines = 3
            )
            Spacer(modifier = Modifier.height(16.dp))
        }

        // Upload button
        Button(
            onClick = onUpload,
            modifier = Modifier.fillMaxWidth(),
            enabled = isLoggedIn
                && uiState.selectedRepo != null
                && uiState.selectedFiles.isNotEmpty()
                && !uiState.isEnqueuing
        ) {
            if (uiState.isEnqueuing) {
                CircularProgressIndicator(
                    modifier = Modifier.size(20.dp),
                    color = MaterialTheme.colorScheme.onPrimary
                )
            } else {
                Icon(Icons.Default.CloudUpload, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Upload to GitHub")
            }
        }

        // Success message
        if (uiState.enqueueSuccess) {
            Spacer(modifier = Modifier.height(12.dp))
            Card(
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            ) {
                Text(
                    text = "Files queued for upload! Check the Queue tab for progress.",
                    modifier = Modifier.padding(16.dp),
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )
            }
        }

        // Error display
        uiState.error?.let { error ->
            Spacer(modifier = Modifier.height(12.dp))
            Card(
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.errorContainer
                )
            ) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = error,
                        modifier = Modifier.weight(1f),
                        color = MaterialTheme.colorScheme.onErrorContainer,
                        style = MaterialTheme.typography.bodySmall
                    )
                    IconButton(onClick = onClearError) {
                        Icon(Icons.Default.Close, contentDescription = "Dismiss")
                    }
                }
            }
        }
    }

    // Repo selection dialog
    if (showRepoDialog) {
        RepoPickerDialog(
            repos = uiState.repos,
            isLoading = uiState.isLoadingRepos,
            onSelect = { repo ->
                onSelectRepo(repo)
                showRepoDialog = false
            },
            onDismiss = { showRepoDialog = false }
        )
    }
}

@Composable
private fun RepoPickerDialog(
    repos: List<GitHubRepo>,
    isLoading: Boolean,
    onSelect: (GitHubRepo) -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Select Repository") },
        text = {
            if (isLoading) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(200.dp),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            } else if (repos.isEmpty()) {
                Text("No repositories found.")
            } else {
                LazyColumn(modifier = Modifier.heightIn(max = 400.dp)) {
                    items(repos) { repo ->
                        ListItem(
                            headlineContent = { Text(repo.fullName) },
                            supportingContent = {
                                Text("Branch: ${repo.defaultBranch}")
                            },
                            leadingContent = {
                                Icon(
                                    if (repo.private) Icons.Default.Lock else Icons.Default.Public,
                                    contentDescription = null
                                )
                            },
                            modifier = Modifier.clickable { onSelect(repo) },
                            colors = ListItemDefaults.colors(
                                containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f)
                            )
                        )
                    }
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}
