## Portfolio (Start here)

If you are reviewing this repository as a portfolio project, start here:

- **docs/portfolio/README.md**

This repo is a monorepo containing:

- a crash-safe Firestore → PostgreSQL migration engine
- a minimal FastAPI backend for admin/read access

# Firebase to PostgreSQL Admin

Creature management system migrated from Firebase to PostgreSQL with Admin UI.

## Project Structure

```
firebase-to-postgres-admin/
├── app/                    # Main application
│   ├── main.py            # FastAPI app entry point
│   ├── config.py          # Configuration
│   ├── database.py        # Database connection
│   ├── models/            # Pydantic models
│   ├── services/          # Business logic
│   └── routers/           # API endpoints
├── static/                # Static files (Admin UI)
├── scripts/               # Utility scripts
│   ├── init_db.py        # Database initialization
│   ├── check_schema.py   # Schema checker
│   └── test_endpoints.py # API tester
├── manage.py              # Server management script
└── requirements.txt       # Dependencies
```

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. Initialize database:

```bash
python scripts/init_db.py
```

4. Start server:

```bash
python manage.py start
# or
start.bat
```

## API Endpoints

- `GET /creatures` - List all creatures (with filters)
- `GET /creatures/{id}` - Get creature details
- `POST /creatures` - Create new creature
- `PUT /creatures/{id}` - Update creature
- `DELETE /creatures/{id}` - Delete creature
- `POST /creatures/stats` - Create/update level stats

API Documentation: http://127.0.0.1:8000/docs

## Server Management

```bash
python manage.py start      # Start server
python manage.py stop       # Stop server
python manage.py restart    # Restart server
python manage.py status     # Check server status
```

## Security Notes

- Never commit `.env` file
- Use environment variables for sensitive data
- CORS is currently set to allow all origins (change for production)

## Development Status

This is a prototype version. Next steps:

- [ ] Admin UI implementation
- [ ] Firestore migration script
- [ ] Image upload handling
- [ ] Authentication/Authorization
- [ ] Production CORS configuration
