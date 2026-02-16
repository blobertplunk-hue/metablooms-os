package com.metablooms.quickupload.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.metablooms.quickupload.data.db.UploadItem
import com.metablooms.quickupload.data.db.UploadStatus

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun QueueScreen(
    items: List<UploadItem>,
    onRetry: (Long) -> Unit,
    onRemove: (Long) -> Unit,
    onClearCompleted: () -> Unit
) {
    Column(modifier = Modifier.fillMaxSize()) {
        if (items.isEmpty()) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(
                        Icons.Default.CloudQueue,
                        contentDescription = null,
                        modifier = Modifier.size(64.dp),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f)
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        "No uploads yet",
                        style = MaterialTheme.typography.bodyLarge,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        "Files you upload will appear here",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
                    )
                }
            }
        } else {
            // Header with clear button
            val completedCount = items.count { it.status == UploadStatus.DONE }
            if (completedCount > 0) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 8.dp),
                    horizontalArrangement = Arrangement.End
                ) {
                    TextButton(onClick = onClearCompleted) {
                        Icon(Icons.Default.ClearAll, contentDescription = null, modifier = Modifier.size(18.dp))
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("Clear completed ($completedCount)")
                    }
                }
            }

            LazyColumn(
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(items, key = { it.id }) { item ->
                    UploadItemCard(
                        item = item,
                        onRetry = { onRetry(item.id) },
                        onRemove = { onRemove(item.id) }
                    )
                }
            }
        }
    }
}

@Composable
private fun UploadItemCard(
    item: UploadItem,
    onRetry: () -> Unit,
    onRemove: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = when (item.status) {
                UploadStatus.DONE -> MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
                UploadStatus.FAILED -> MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.3f)
                UploadStatus.UPLOADING -> MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.3f)
                else -> MaterialTheme.colorScheme.surfaceVariant
            }
        )
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                StatusIcon(item.status)
                Spacer(modifier = Modifier.width(12.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = item.displayName,
                        style = MaterialTheme.typography.titleSmall,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                    Text(
                        text = "${item.repoFullName} · ${item.targetPath}",
                        style = MaterialTheme.typography.bodySmall,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                // Actions
                when (item.status) {
                    UploadStatus.FAILED, UploadStatus.RETRYING -> {
                        IconButton(onClick = onRetry) {
                            Icon(Icons.Default.Refresh, contentDescription = "Retry")
                        }
                    }
                    UploadStatus.UPLOADING -> {
                        CircularProgressIndicator(modifier = Modifier.size(20.dp))
                    }
                    else -> {}
                }
                IconButton(onClick = onRemove) {
                    Icon(
                        Icons.Default.Close,
                        contentDescription = "Remove",
                        modifier = Modifier.size(18.dp)
                    )
                }
            }

            // Error message
            item.lastError?.let { error ->
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = error,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.error
                )
            }

            // Size info
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = formatFileSize(item.sizeBytes) +
                    if (item.attempts > 0) " · Attempt ${item.attempts}" else "",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
            )
        }
    }
}

@Composable
private fun StatusIcon(status: UploadStatus) {
    val (icon, tint) = when (status) {
        UploadStatus.QUEUED -> Icons.Default.Schedule to MaterialTheme.colorScheme.onSurfaceVariant
        UploadStatus.UPLOADING -> Icons.Default.CloudUpload to MaterialTheme.colorScheme.primary
        UploadStatus.RETRYING -> Icons.Default.Refresh to MaterialTheme.colorScheme.tertiary
        UploadStatus.FAILED -> Icons.Default.Error to MaterialTheme.colorScheme.error
        UploadStatus.DONE -> Icons.Default.CheckCircle to MaterialTheme.colorScheme.secondary
    }
    Icon(icon, contentDescription = status.name, tint = tint, modifier = Modifier.size(24.dp))
}

private fun formatFileSize(bytes: Long): String {
    return when {
        bytes < 1024 -> "$bytes B"
        bytes < 1024 * 1024 -> "${bytes / 1024} KB"
        else -> "${"%.1f".format(bytes / (1024.0 * 1024.0))} MB"
    }
}
