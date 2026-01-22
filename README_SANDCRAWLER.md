# Sandcrawler (Minimal)

This OS includes a **queue-only** Sandcrawler module.

- It **does not** browse the web by itself.
- It creates `sandcrawler_jobs/*.job.json` job files which an external runner (e.g., a chat tool harness)
  can execute using `web.run`, then save results into `sandcrawler_outputs/*.result.json`.

This keeps the OS fail-closed: no fabricated evidence, only queued requests + recorded results.
