# Firestore → PostgreSQL Migration + Admin API (Monorepo)

## What this is

A monorepo that contains:

- **Migration engine**: crash-safe, resume-safe Firestore → PostgreSQL migration
- **API/Admin backend**: FastAPI service to read and manage migrated data

## Why it exists

Firestore was a convenient starting point, but we needed:

- relational querying and operational control in PostgreSQL
- repeatable, safe migration that can resume after crashes
- a minimal admin/API layer for downstream usage

## Key guarantees (Migration engine)

- **Idempotent writes** via UPSERT (safe to re-run)
- **Crash-safe checkpointing** (checkpoint updated only after successful batch)
- **Resume-safe paging** using Firestore `__name__` ordering
- **Security-first secret handling** (service account key is never baked into images; mounted read-only)

## Architecture (high level)

Firestore → (Docker one-shot migrator) → PostgreSQL(JSONB)
↘ checkpoint table (migration_state)

## Verification strategy

- Run verification only when migration finishes:
  - Firestore streaming count (safe for <10k docs)
  - PostgreSQL count
  - Print match result

## Notable issues & decisions

- Dropped Firestore Aggregation API due to SDK type mismatch issues
- Stored full documents as **JSONB** first for safety and flexibility

## How to run (local)

- Start services:
  - `docker compose up -d postgres api`
- Run migration:
  - `docker compose run --rm migrator`

## Links

- Internal docs: `docs/internal/`
