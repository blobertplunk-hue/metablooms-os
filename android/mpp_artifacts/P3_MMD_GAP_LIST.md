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
- **Detect:** Size threshold exceeded; API limitation behaviors
- **Message:** "This file is too large for direct API upload."
- **Remediate:** Offer (a) Git LFS guidance, (b) alternate storage, or (c) disclaimer

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
