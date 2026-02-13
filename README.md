# Database Setup & Migrations (MySQL + Flask + Alembic)

## This Project Uses

- Flask-SQLAlchemy
- MySQL
- Alembic CLI
- python-dotenv
- pymysql

---

## Required Libraries

```bash
pip install flask flask-sqlalchemy alembic pymysql python-dotenv
```

Library explanations:

- flask - Web framework  
- flask-sqlalchemy - ORM integration with Flask  
- alembic - Database migration tool  
- pymysql - MySQL driver for SQLAlchemy  
- python-dotenv - Loads .env variables  

---

## Environment Configuration

Create a `.env` file in the project root:

```env
DB_USERNAME=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=kannada_tattvapada
```

---

## Initialize Alembic (First Time Only)

```bash
alembic init migrations
```

Creates the `migrations/` folder and `alembic.ini` file.

---

## Create Migration (After Model Changes)

```bash
alembic revision --autogenerate -m "migration message"
```

Generates a new migration file by comparing models with the current database schema.

---

## Apply Migration

```bash
alembic upgrade head
```

Applies the latest migration to the database.

---

## Check Current Version

```bash
alembic current
```

Shows current applied migration version in the database.

---

## View Migration History

```bash
alembic history
```

Displays all migration revisions in order.

---

## Downgrade Last Migration

```bash
alembic downgrade -1
```

Reverts the last applied migration.

---

## First-Time Setup (Fresh Project)

```bash
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
```

Creates initial schema and applies all tables to MySQL.

---

## Important Notes

- All models must be imported inside `app/models/__init__.py`
- Do not manually delete the `alembic_version` table
- Always review generated migration file before upgrading
- Database uses `utf8mb4` for full Kannada Unicode support
- Alembic reads database credentials from `.env`

---

## Tables Managed by Alembic

- sampadakar_documents
- tatvapada
- tatvapada_author_info
- tatvapadakarara_vivara
- paribhashika_padavivarana
- arthakosha
- shopping_tatvapada
- shopping_books
- alembic_version

---

## Recommended Migration Workflow

1. Modify SQLAlchemy model  
2. Run `alembic revision --autogenerate`  
3. Review generated file  
4. Run `alembic upgrade head`  
5. Commit migration file to Git  

---
