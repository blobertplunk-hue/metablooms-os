# MetaBlooms OS Contract (Public) — V1

This document defines the minimum, non-negotiable behavioral contract for a production MetaBlooms OS.

## 1) Authorities
- **Authoritative OS bytes**: the OS ZIP bundle and its manifests (immutable).
- **Working OS root (zroot)**: a materialized filesystem tree derived from the authoritative OS bytes.
- **Persistent state**: stored outside zroot; never overwritten by OS upgrades.

## 2) Canonical Roots
- Working OS root: `/mnt/data/_mb_zroot/`
- Persistent state root: `/mnt/data/_mb_state/`
- Exports root: `/mnt/data/_mb_exports/`

## 3) Boot / Materialization
- The system MUST ensure zroot exists and matches the authoritative OS source fingerprint.
- The system MUST NOT reason about OS contents until zroot exists and is validated.

## 4) Evidence Discipline
- The system MUST NOT claim state unless it has byte evidence.
- The system MUST record materialization attempts and rehydration breadcrumbs.

## 5) Gates
- **P0** gates BLOCK progress.
- **P1** gates WARN by default.
- **P2** gates LOG only.

## 6) User Isolation
- State is isolated per user by default.
- Shared state requires explicit opt-in configuration.

## 7) Exports
- Every export MUST include a manifest and checksums tying it to source zroot and state snapshot.
