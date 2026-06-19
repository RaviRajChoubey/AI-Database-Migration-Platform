# AI Database Migration Platform

## Overview

AI Database Migration Platform is an enterprise-grade database migration solution designed to automate and simplify the migration of databases from MSSQL, MySQL, and other relational database systems to PostgreSQL.

The platform combines AI-powered schema analysis, automated validation, checksum verification, reconciliation reporting, rollback generation, audit tracking, and migration scheduling into a single dashboard.

Developed as part of a Database Migration Automation initiative, the system focuses on reliability, transparency, validation, and operational safety.

---

# Configuration

## Source Database Configuration

The platform supports MSSQL and MySQL as source databases(till now).

### MSSQL Example

```text
Source Type      : MSSQL
Source Server    : localhost\MSSQLSERVER01
Source Database  : source_mssql
Username         : <your_username>
Password         : <your_password>
```

### MySQL Example

```text
Source Type      : MySQL
Source Server    : localhost
Source Database  : source_mysql
Username         : <your_username>
Password         : <your_password>
```

---

## Target PostgreSQL Configuration

### Neon PostgreSQL Example

```text
Host             : <neon_host>
Port             : 5432
Database         : neondb
Username         : <postgres_user>
Password         : <postgres_password>
SSL Mode         : require
```

---

## Environment Variables

Create a `.env` file:

```env
POSTGRES_HOST=<host>
POSTGRES_PORT=5432
POSTGRES_DB=<database>
POSTGRES_USER=<user>
POSTGRES_PASSWORD=<password>

OPENAI_API_KEY=<api_key>
```

---

## Migration Profile Example

```json
{
  "profileName": "MSSQL_to_PostgreSQL",
  "sourceType": "mssql",
  "sourceServer": "localhost\\MSSQLSERVER01",
  "sourceDatabase": "source_mssql",
  "sourceUser": "<username>",
  "sourcePassword": "<password>",
  "targetHost": "<postgres_host>",
  "targetDatabase": "neondb",
  "targetUser": "<postgres_user>",
  "targetPassword": "<postgres_password>"
}
```

---

## Default Development Setup

### Frontend

```text
http://localhost:5173
```

### Backend

```text
http://localhost:8000
```

### Swagger

```text
http://localhost:8000/docs
```

## Key Features

### Database Migration
- MSSQL to PostgreSQL Migration
- MySQL to PostgreSQL Migration
- Table Migration
- View Migration
- Stored Procedure Migration
- Function Migration
- Incremental Migration Support
- Resume Interrupted Migration

### AI-Powered Analysis
- Foreign Key Detection
- Schema Risk Analysis
- Migration Readiness Assessment
- Column Rename Suggestions
- AI Migration Summary

### Validation Engine
- Row Count Validation
- Source vs Target Verification
- Checksum Validation
- Reconciliation Reports
- Data Integrity Checks

### Monitoring & Tracking
- Real-Time Migration Progress
- Audit Trail
- Migration History
- Scheduler Monitoring
- Scheduled Jobs Dashboard
- Execution Logs

### Reporting
- Validation Report
- Audit Report
- Checksum Report
- Reconciliation Report
- Migration Report
- Rollback Script
- Procedure Report
- Function Report

### Scheduler
- Daily Scheduled Migration
- Weekly Scheduled Migration
- Retry Mechanism
- Execution Tracking
- Failure Logging

---

# System Architecture

```text
Source Database
(MSSQL / MySQL)
        |
        |
        V
AI Analysis Engine
        |
        |
        V
Validation Engine
        |
        |
        V
Migration Engine
        |
        |
        V
PostgreSQL Target Database
        |
        +---- Audit Trail
        |
        +---- Checksum Validation
        |
        +---- Reconciliation Report
        |
        +---- Rollback Script
        |
        +---- Metrics Report
```

---

# Technology Stack

## Backend

- Python 3.13
- FastAPI
- APScheduler
- Psycopg2
- PyODBC
- SQLAlchemy
- Pandas

## Frontend

- React
- Vite
- Axios
- React Icons

## Databases

- PostgreSQL
- Microsoft SQL Server
- MySQL

## AI Components

- AI Schema Analyzer
- Foreign Key Detection Engine
- Rename Recommendation Engine
- Migration Risk Assessment Engine

---

# Project Structure

```text
db-migration-tool/
│
├── backend/
│   ├── routes/
│   │   └── migration.py
│   │
│   ├── scheduler.py
│   ├── migration_tool.py
│   ├── postgres_connector.py
│   ├── config.py
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api.js
│   │   └── App.jsx
│
├── reports/
│
├── rollback/
│
├── requirements.txt
│
└── README.md
```

---

# Database Tables

The platform maintains the following PostgreSQL tables.

## migration_profiles

Stores reusable migration profiles.

```text
profile_id
profile_name
source_type
source_server
source_database
source_user
source_password
target_host
target_database
target_user
target_password
created_at
```

---

## migration_scheduler

Stores scheduled migration jobs.

```text
schedule_id
schedule_name
scheduled_time
weekday
retry_count
profile_id
is_active
created_at
```

---

## scheduler_execution_log

Stores execution history of scheduler jobs.

```text
execution_id
schedule_id
execution_time
status
duration_seconds
error_message
```

---

## migration_history

Stores completed migration executions.

```text
id
source
target
status
rows_migrated
started_at
completed_at
```

---

## migration_audit_trail

Stores detailed migration audit records.

```text
audit_id
started_at
completed_at
source_db
target_db
tables_processed
rows_processed
validation_status
audit_status
checksum_status
reconciliation_status
rollback_generated
report_generated
```

---

# API Endpoints

## Connection & Migration

### Test Connection

```http
POST /migration/test-connection
```

Tests source and target database connectivity.

---

### Start Migration

```http
POST /migration/start
```

Starts database migration.

---

### Resume Migration

```http
POST /migration/resume
```

Resumes interrupted migration.

---

# Migration Profiles

### Create Profile

```http
POST /migration/profile
```

---

### Get Profiles

```http
GET /migration/profiles
```

---

# Progress

### Migration Progress

```http
GET /migration/progress
```

Returns current migration progress.

---

# Audit

### Audit Trail

```http
GET /migration/audit-trail
```

---

### Migration History

```http
GET /migration/migration-history
```

---

# Scheduler

### Create Schedule

```http
POST /migration/schedule
```

---

### Get Schedules

```http
GET /migration/schedules
```

---

### Scheduler Logs

```http
GET /migration/scheduler/logs
```

---

# Downloads

### Validation Report

```http
GET /download/validation
```

---

### Audit Report

```http
GET /download/audit
```

---

### Checksum Report

```http
GET /download/checksum
```

---

### Reconciliation Report

```http
GET /download/reconciliation
```

---

# Core Functions

## Migration Engine

### start_migration()

Starts migration workflow.

Responsibilities:

- Connect source database
- Connect PostgreSQL
- Create schema
- Migrate tables
- Migrate views
- Migrate procedures
- Migrate functions
- Generate reports

---

### resume_migration()

Resumes interrupted migrations.

---

### migrate_table()

Migrates table structure and data.

---

### migrate_views()

Migrates database views.

---

### migrate_procedures()

Migrates stored procedures.

---

### migrate_functions()

Migrates database functions.

---

# Validation Engine

### validate_counts()

Validates source and target row counts.

---

### generate_checksum_report()

Generates checksum validation report.

---

### generate_reconciliation_report()

Generates reconciliation report.

---

# Audit Engine

### save_audit_trail()

Stores audit records.

---

### save_history()

Stores migration history.

---

### generate_rollback_script()

Creates rollback scripts.

---

# Scheduler Engine

### schedule_migration()

Creates migration schedules.

---

### run_scheduled_migration()

Executes scheduled migrations.

---

### save_execution_log()

Stores scheduler execution logs.

---

# Reports Generated

The platform automatically generates:

## Validation Report

Contains:

- Source row counts
- Target row counts
- Validation status

---

## Audit Report

Contains:

- Migration metadata
- Execution timestamps
- Status information

---

## Checksum Report

Contains:

- Source checksum
- Target checksum
- Verification result

---

## Reconciliation Report

Contains:

- Missing records
- Extra records
- Validation summary

---

## Rollback Script

Contains SQL scripts required to revert migration.

---

## Procedure Report

Contains migrated procedures.

---

## Function Report

Contains migrated functions.

---

# Running the Project

## Backend

```bash
cd backend

pip install -r requirements.txt

uvicorn main:app --reload
```

Backend URL:

```text
http://localhost:8000
```

Swagger Documentation:

```text
http://localhost:8000/docs
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

---

# Migration Workflow

```text
1. Connect Source Database
        |
        V
2. Test Connection
        |
        V
3. AI Schema Analysis
        |
        V
4. Auto Mapping
        |
        V
5. Start Migration
        |
        V
6. Validation
        |
        V
7. Checksum Verification
        |
        V
8. Reconciliation
        |
        V
9. Report Generation
        |
        V
10. Audit Logging
```

---

# Current Capabilities

✔ MSSQL Migration

✔ MySQL Migration

✔ PostgreSQL Target

✔ Scheduler

✔ Audit Trail

✔ Migration History

✔ Validation Reports

✔ Checksum Verification

✔ Reconciliation Reports

✔ Rollback Generation

✔ Resume Migration

✔ AI Analysis

✔ Live Monitoring

---

# Future Scope

## Phase 2

- Oracle Migration Support
- MongoDB Migration
- MariaDB Migration
- AWS RDS Migration
- Azure SQL Migration

---

## Phase 3

- AI-Based ETL Pipeline Generation
- AI Data Quality Scoring
- Automatic Conflict Resolution
- Smart Schema Evolution

---

## Phase 4

- Kubernetes Deployment
- Dockerized Architecture
- Multi-Tenant SaaS Platform
- User Authentication
- Role-Based Access Control
- Team Workspaces
- Email Notifications
- Slack Integration
- Microsoft Teams Integration

---

# Known Limitations

- Oracle migration not implemented
- No authentication layer currently
- Scheduler supports local deployment only
- Procedure conversion may require manual review
- Function conversion may require manual review

---

# Contributors

### Ravi Raj Choubey

B.Tech Data Science  
VIT Chennai

### Project

AI Database Migration Platform

Enterprise Database Migration, Validation and AI-Powered Schema Analysis

---

# License

This project is intended for educational, research, and enterprise database migration purposes.