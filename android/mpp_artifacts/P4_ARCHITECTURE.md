# P4 PLAN — Tier B Architecture: QuickUpload Android

## Core Decision: Hybrid API-first + WorkManager

- **GitHub Contents API** for small/medium files and commit-by-file operations
- **Git Data API** optional for PR flow (future)
- **WorkManager** with foreground-mode for long uploads and persistent queue

## Modules

### 1. UI (Jetpack Compose)
- Home: Repo selector + Quick Upload button
- Upload Queue: per-file progress + states (Queued/Uploading/Retrying/Failed/Done)
- Repo Settings: default branch, target folder, overwrite policy, PR policy
- Auth: Sign in with GitHub (device flow) + revoke/logout
- Help: battery optimization guidance + troubleshooting

### 2. Storage Layer
- SAF picker for files and folders
- Persist URI permissions for chosen roots
- Keep small "trusted locations" list with pruning

### 3. Queue + State Machine (Room DB)
- `UploadItem(id, uri, displayName, sizeBytes, repo, branch, targetPath, status, attempts, lastError, createdAt)`
- `RepoProfile(repoFullName, defaultBranch, defaultFolder, overwritePolicy, prPolicy)`
- Idempotency: compute content_sha256 locally; deduplicate

### 4. Background Engine (WorkManager)
- CoroutineWorker with network constraint
- Exponential backoff with jitter
- Foreground-mode for long tasks with progress notification

### 5. GitHub Client
- Device flow auth with polling interval compliance
- File operations: fetch SHA for updates, PUT for create/update
- Rate-limit aware (read headers, throttle)

## UX Flows

### Flow 1: Share-sheet Upload
Share → QuickUpload target → pick RepoProfile → confirm path + message → enqueue → background worker

### Flow 2: In-app Pick Files
Select files via SAF → choose repo/branch/path → message template → enqueue

### Flow 3: Conflict Resolution
On SHA mismatch: Overwrite / Rename / New branch + PR / Cancel
Default safe: Rename or New branch + PR when branch protected

## Defaults
- Default path: `/uploads/YYYY-MM-DD/` (toggleable)
- Default policy: Never overwrite silently
- Always show: repo + branch + full target path, file size + warnings, next retry time on failures
