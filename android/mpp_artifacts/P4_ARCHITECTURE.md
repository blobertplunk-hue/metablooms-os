# P4 PLAN — Tier B Architecture: QuickUpload Android

## Core Decision: Hybrid API-first + WorkManager

- **GitHub Contents API** for single small files (<=1 MB): simple create/update with SHA
- **GitHub Git Blobs API** for large files (1–100 MB): blob → tree → commit → ref update
- **GitHub Git Tree API** for batch commits: N files to same repo+branch = 1 commit
- **WorkManager** with foreground-mode for long uploads and persistent queue

## Upload Routing Logic

```
File arrives in queue
  ├── Token valid? (GET /user → 200)
  │     └── No → mark all RETRYING, clear token, return failure
  │
  ├── Idempotency check (content_sha256 + repo + path)
  │     └── Duplicate → skip, mark as duplicate
  │
  ├── Group by repo+branch
  │     ├── Single file
  │     │     ├── <= 1 MB → Contents API (PUT /repos/:o/:r/contents/:path)
  │     │     └── > 1 MB, <= 100 MB → Blobs API pipeline
  │     │
  │     └── Multiple files → Batch commit via Git Tree API
  │           ├── Create blobs for each file
  │           ├── Get branch HEAD
  │           ├── Create tree with all blobs
  │           ├── Create single commit
  │           └── Update ref
  │
  └── > 100 MB → FAILED with LFS guidance
```

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
- `UploadItem(id, uri, displayName, sizeBytes, contentSha256, repo, branch, targetPath, status, attempts, lastError, remoteSha, createdAt, updatedAt)`
- `RepoProfile(repoFullName, defaultBranch, defaultFolder, overwritePolicy, prPolicy)`
- Idempotency: `isDuplicate(sha, repo, path)` query checked before every upload

### 4. Background Engine (WorkManager)
- CoroutineWorker with network constraint
- Exponential backoff with jitter
- Foreground-mode for long tasks with progress notification
- Token validation at worker start (before any uploads)
- 401 mid-queue → clear token, mark items RETRYING, return failure
- Batch grouping: items with same repo+branch → single Git Tree commit

### 5. GitHub Client
- Device flow auth with polling interval compliance
- Contents API: fetch SHA for updates, PUT for create/update (<=1 MB)
- Git Data API: create blob, create tree, create commit, update ref (>1 MB or batch)
- Rate-limit aware (read headers, throttle)

## UX Flows

### Flow 1: Share-sheet Upload
Share → QuickUpload target → pick RepoProfile → confirm path + message → enqueue → background worker

### Flow 2: In-app Pick Files
Select files via SAF → choose repo/branch/path → message template → enqueue

### Flow 3: Conflict Resolution
On SHA mismatch: Overwrite / Rename / New branch + PR / Cancel
Default safe: Rename or New branch + PR when branch protected

### Flow 4: Auth Expiry Recovery
Worker detects 401 → clears token → items stay in RETRYING → user sees "Sign in again" prompt → after re-auth, items auto-resume on next worker run

## Defaults
- Default path: `/uploads/YYYY-MM-DD/` (toggleable)
- Default policy: Never overwrite silently
- Always show: repo + branch + full target path, file size + warnings, next retry time on failures
- Batch: multiple files to same repo+branch always batched into single commit
