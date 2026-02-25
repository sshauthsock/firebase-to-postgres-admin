# Architecture

## High-Level Flow

Firestore
│
│ (ordered batch read, **name**)
▼
Docker one-shot migrator
│
├── UPSERT into PostgreSQL (JSONB)
│
└── Update checkpoint (migration_state) AFTER batch success
│
▼
migration_state table

## Reliability Model

### Idempotency

- All writes use UPSERT
- Re-running the job does not create duplicates

### Crash Safety

- Checkpoint updated only after a full successful batch
- If container crashes mid-batch, previous checkpoint remains intact

### Resume Strategy

- Read `last_doc_id`
- Continue from `start_after(snapshot)`
- Safe pagination via Firestore `__name__`

## Security Model

- Service account key is NOT stored in the repository
- Key is mounted read-only via Docker
- Image does not bake secrets

## Verification Strategy

- Verification only runs when no documents remain
- Firestore streaming count (safe for <10k docs)
- PostgreSQL COUNT(\*)
- Print match result

## Tradeoffs

- JSONB chosen over full normalization for safety and flexibility
- Aggregation API removed due to SDK compatibility issues
