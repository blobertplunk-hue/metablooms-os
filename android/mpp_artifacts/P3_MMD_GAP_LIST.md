# P3 MMD — Gap List (Failure-Causing "Missing Middles")

Each item includes detection, user message, and remediation.

## 1. Persisted URI grants exceed cap / stale URIs after reboot
- **Detect:** SecurityException / openFileDescriptor fails; persisted grants count high
- **Message:** "I no longer have permission to that folder. Please reselect it."
- **Remediate:** Re-open SAF picker; prune old grants; keep "recent locations" limited

## 2. OEM kills background work
- **Detect:** Worker repeatedly stopped; retry loop without progress
- **Message:** "Your phone is stopping uploads in the background. Turn off battery optimization for QuickUpload."
- **Remediate:** In-app "Battery help" screen; use foreground-mode worker for uploads

## 3. Branch protections prevent direct push
- **Detect:** API returns 403/422; checks show protected branch
- **Message:** "This branch is protected. Create a new branch + PR instead?"
- **Remediate:** Offer "Create branch & PR" flow; store as setting per repo

## 4. Update requires SHA; remote changed
- **Detect:** Existing file SHA mismatch; 409/422 conflict on update; remote head moved
- **Message:** "This file changed on GitHub since you selected it."
- **Remediate:** Offer overwrite (fetch new SHA), rename, or new branch

## 5. Large files
- **Detect:** Size > 1 MB routes to Blobs API; size > 100 MB triggers hard gate
- **Message (1-100 MB):** "Using extended upload for large file…" (transparent to user)
- **Message (>100 MB):** "This file is too large for GitHub API (max 100 MB). Use Git LFS."
- **Remediate:** Blobs API path handles 1-100 MB automatically; >100 MB shows LFS guidance

## 6. Rate limiting
- **Detect:** 403 with rate limit headers
- **Message:** "GitHub rate limit reached. Retrying later."
- **Remediate:** Backoff, batch, show next retry time

## 7. Device flow polling too aggressive
- **Detect:** OAuth error about polling interval
- **Message:** "Waiting for authorization…"
- **Remediate:** Obey server-provided interval

## 8. User picks file, then moves/deletes it
- **Detect:** URI open fails
- **Message:** "That file can't be found anymore."
- **Remediate:** Remove from queue; prompt to re-add

## 9. Token expires or is revoked during background queue processing
- **Detect:** 401 response from any GitHub API call; token validation fails at worker start
- **Message:** "Authentication expired or invalid. Please sign in again."
- **Remediate:** Clear stored token → UI shows sign-in prompt; all pending items marked RETRYING (not FAILED, so no attempt count burned); re-queue automatically after re-auth
- **Batch behavior:** If 401 occurs mid-batch blob creation, entire batch aborts to RETRYING state

## 10. Duplicate upload (idempotency failure)
- **Detect:** content_sha256 matches an existing queued/completed item for same repo+path
- **Message:** "Duplicate: identical file already queued or uploaded to this path."
- **Remediate:** Skip and mark as duplicate; user can force re-upload by removing the original item first

## 11. Multi-file upload creates N commits (API chatter)
- **Detect:** Multiple files queued for same repo+branch
- **Message:** (none — transparent optimization)
- **Remediate:** Batch via Git Tree API: create blobs → single tree → single commit → update ref. N files = 1 commit instead of N commits. Reduces API calls and keeps commit history clean.
