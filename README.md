# Firestore → PostgreSQL Migration + Admin API (Monorepo)

## Portfolio (Start Here)

If you are reviewing this repository as a portfolio project, please start here:

👉 **docs/portfolio/README.md**

This repository demonstrates:

- A **crash-safe, resume-safe Firestore → PostgreSQL migration engine**
- A minimal **FastAPI backend** for admin/read access
- Security-first secret handling with Docker
- End-to-end data lifecycle from NoSQL → relational storage → API layer

---

# Project Overview

This project began as a Firebase-based creature management system and evolved into:

1. A reliable migration pipeline to PostgreSQL
2. A relational backend service with admin capabilities

The focus of this repository is not just CRUD functionality,
but **data reliability, migration safety, and operational correctness.**

---

# Architecture Summary

High-level data flow:

Firestore  
→ (Docker one-shot migrator)  
→ PostgreSQL (JSONB)  
→ FastAPI backend  
→ Admin/API consumers

Key components:

- `app/migrations/` – Migration engine (idempotent, crash-safe)
- `app/` – FastAPI backend
- `docs/portfolio/` – Reviewer-friendly technical documentation
- `docs/internal/` – Development notes and technical explorations

---

# Migration Engine (Core Highlight)

The migration engine guarantees:

- **Idempotent writes** via UPSERT
- **Crash-safe checkpointing** using `migration_state`
- **Resume-safe pagination** via Firestore `__name__` ordering
- **Read-only secret mounting** (no secrets baked into images)
- End-of-run verification (Firestore count vs PostgreSQL count)

Run migration:

```bash
docker compose run --rm migrator
```

# Backend (FastAPI)

### Start services:

```
docker compose up -d postgres api
```

### API documentation:

```
http://127.0.0.1:8000/docs
```

### Main endpoints:

- GET /creatures
- GET /creatures/{id}
- POST /creatures
- PUT /creatures/{id}
- DELETE /creatures/{id}

# Security Model

- Service account keys are not stored in the repository

- Keys are mounted from WSL home directory as read-only

- `.env` files are excluded via .gitignore

- Docker images do not bake secrets

# Design Decisions

- JSONB chosen for safe full-document migration

- Aggregation API removed due to SDK compatibility issues

- Checkpoint updated only after full batch success

- Streaming verification used for <10k documents

# Repository Structure

```
firebase-to-postgres-admin/
├── app/
│   ├── migrations/
│   ├── routers/
│   ├── services/
│   └── models/
├── scripts/
│   └── windows/
├── docs/
│   ├── portfolio/
│   └── internal/
├── docker-compose.yml
└── README.md
```
