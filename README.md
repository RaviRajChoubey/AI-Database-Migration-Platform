# 🚀 AI Database Migration Platform

### Enterprise Database Migration, AI-Powered Schema Analysis, Validation & Self-Healing

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Target-336791?logo=postgresql&logoColor=white)
![Throughput](https://img.shields.io/badge/Throughput-50%2C000%2B%20rows%2Fsec-brightgreen)

An **enterprise-grade database migration platform** designed to automate and simplify migration from heterogeneous relational databases such as **Microsoft SQL Server (MSSQL)**, **MySQL**, and **Oracle** to **PostgreSQL**.

The platform combines **high-performance data migration**, **AI-powered schema analysis**, **automatic type mapping**, **self-healing schema translation**, **routine conversion**, **cryptographic validation**, **reconciliation**, **data-quality scoring**, **rollback generation**, **audit tracking**, **real-time monitoring**, and **scheduled migrations** into a unified platform.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Supported Migration Paths](#-supported-migration-paths)
- [Key Highlights](#-key-highlights)
- [Project Architecture](#-project-architecture)
- [Phase 1 — High-Performance Core Engine & Validation](#-phase-1--high-performance-core-engine--validation)
- [Phase 2 — Database Expansion & Responsive UI](#-phase-2--database-expansion--responsive-ui)
- [Phase 3 — AI Intelligence](#-phase-3--ai-intelligence)
- [Key Features](#-key-features)
- [Reporting](#-reporting)
- [Scheduler](#-scheduler)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Database Tables](#-database-tables)
- [Configuration](#-configuration)
- [API Endpoints](#-api-endpoints)
- [Core Migration Functions](#-core-migration-functions)
- [Dashboard](#-dashboard)
- [Running the Project](#-running-the-project)
- [Migration Workflow](#-migration-workflow)
- [Enterprise Reliability Features](#-enterprise-reliability-features)
- [Security Considerations](#-security-considerations)
- [Performance Considerations](#-performance-considerations)
- [Future Scope](#-future-scope)
- [Known Limitations](#-known-limitations)
- [Project Use Case](#-project-use-case)
- [Contributors](#-contributors)
- [License](#-license)

---

## 📖 Overview

Traditional database migration requires significant **manual effort** for:

- Schema conversion
- Data type mapping
- Foreign key handling
- Stored procedure conversion
- Trigger conversion
- Function conversion
- Data validation
- Reconciliation
- Error recovery
- Migration monitoring

The **AI Database Migration Platform** automates these processes through a **modular migration engine**, **AI-assisted schema intelligence**, and **automated validation**.

---

## 🔀 Supported Migration Paths

```text
MSSQL  ───────────┐
                  │
MySQL  ───────────┼──>  AI Migration Engine  ──>  PostgreSQL
                  │
Oracle ───────────┘
```

---

## ⭐ Key Highlights

- ⚡ **High-performance PostgreSQL COPY based data loading**
- 🚀 **50,000+ rows/sec** data loading benchmark
- 🔄 Automatic fallback to batched inserts for binary columns
- **MSSQL → PostgreSQL** migration
- **MySQL → PostgreSQL** migration
- **Oracle → PostgreSQL** migration
- Table, view, index and constraint migration
- Stored procedure and function migration
- Trigger migration
- 🤖 **AI-powered schema analysis**
- Foreign key detection
- Schema risk analysis
- Column rename recommendations
- Automatic data type mapping
- 🩹 **Self-healing PostgreSQL schema engine**
- AI-powered routine translation
- 🔐 **SHA-256 checksum verification**
- Cell-by-cell reconciliation
- 📊 Data quality scoring from **0–100%**
- Rollback script generation
- Resume interrupted migrations
- Incremental migration support
- Migration scheduling
- Retry mechanism
- Real-time migration monitoring
- Audit trail
- Detailed migration history
- Validation and reconciliation reports
- Responsive dashboard
- Swagger API documentation

---

## 🏗️ Project Architecture

```text
                     ┌──────────────────────┐
                     │   Source Databases   │
                     │                      │
                     │ MSSQL / MySQL /      │
                     │ Oracle               │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │  Database Adapters   │
                     │                      │
                     │ MSSQL Adapter        │
                     │ MySQL Adapter        │
                     │ Oracle Adapter       │
                     └──────────┬───────────┘
                                │
                                ▼
                ┌──────────────────────────────┐
                │      AI Schema Analysis      │
                │                              │
                │ • FK Detection               │
                │ • Risk Analysis              │
                │ • Type Mapping               │
                │ • Rename Suggestions         │
                │ • Migration Readiness        │
                └──────────────┬───────────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │    Self-Healing AI Engine    │
                │                              │
                │ • DDL Error Recovery         │
                │ • SQL Translation            │
                │ • Schema Memory              │
                │ • Automatic Rule Learning    │
                └──────────────┬───────────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │       Migration Engine       │
                │                              │
                │ • Schema Migration           │
                │ • COPY Streaming             │
                │ • Batch Fallback             │
                │ • Incremental Migration      │
                │ • Resume Migration           │
                └──────────────┬───────────────┘
                               │
                               ▼
                     ┌──────────────────────┐
                     │  PostgreSQL Target   │
                     └──────────┬───────────┘
                                │
             ┌──────────────────┼──────────────────┐
             ▼                  ▼                  ▼
    ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
    │  Validation    │ │ Reconciliation │ │  Data Quality  │
    │  Engine        │ │ Engine         │ │  Engine        │
    └───────┬────────┘ └───────┬────────┘ └───────┬────────┘
            │                  │                  │
            └──────────────────┼──────────────────┘
                               ▼
                     ┌──────────────────────┐
                     │  Reporting & Audit   │
                     │                      │
                     │ • Validation Report  │
                     │ • Checksum Report    │
                     │ • Audit Report       │
                     │ • Reconciliation     │
                     │ • Rollback           │
                     │ • Migration History  │
                     └──────────────────────┘
```

---

# 🔥 Phase 1 — High-Performance Core Engine & Validation

## 1. PostgreSQL COPY Protocol Integration

The migration engine uses PostgreSQL's **COPY protocol** for high-throughput data loading.

Instead of relying only on:

```python
execute_values()
```

the platform can stream data using:

```text
copy_expert()
     ↓
io.StringIO
     ↓
TSV Streaming
     ↓
PostgreSQL COPY
```

### ✅ Benefits

- High-throughput bulk loading
- Reduced SQL statement overhead
- Reduced network round trips
- Efficient memory usage through buffered streaming
- Better performance for large datasets

### 📈 Performance Benchmark

> **50,000+ rows/sec** for supported bulk-loading workloads.

The implementation is designed to provide performance comparable to high-performance migration utilities such as **pgloader** for suitable workloads.

---

## 2. Automatic Binary Column Fallback

Some tables may contain **binary / bytea** data. For such tables, the migration engine automatically falls back from COPY streaming to the safer batched insertion mechanism.

```text
            Migration
                │
                ▼
         Binary Columns?
          /           \
        YES            NO
         │              │
         ▼              ▼
  execute_values()   COPY Protocol
```

This allows the system to maintain compatibility while still using high-performance streaming wherever possible.

---

## 3. Cryptographic Checksum Validation

The platform generates **SHA-256** based row-content hashes for source and target records.

```text
Source Row
    │
    ▼
Canonical Row Representation
    │
    ▼
SHA-256 Hash
    │
    ▼
Source Checksum
```

The same process is performed on the PostgreSQL target.

```text
Source Checksum ──┐
                  ├──> Compare ──> Validation Result
Target Checksum ──┘
```

### Validation helps identify

- Modified records
- Missing records
- Extra records
- Data corruption
- Inconsistent migration results

---

## 4. Cell-by-Cell Reconciliation

The reconciliation engine performs detailed comparison between source and target data.

It identifies:

- ✅ **Matched Records**
- ❌ **Missing Records**
- ➕ **Extra Records**
- ⚠️ **Mismatched Values**

The generated reconciliation report provides detailed information about migration discrepancies.

---

# 🔥 Phase 2 — Database Expansion & Responsive UI

## 5. Oracle Database Support

Oracle has been added as a supported source database through:

```text
backend/adapters/oracle_adapter.py
```

The Oracle adapter extracts metadata required for migration.

### Supported Oracle Metadata

- Tables
- Views
- Indexes
- Default values
- Check constraints
- Columns
- Data types

---

## 6. Oracle → PostgreSQL Type Mapping

The migration engine provides automatic Oracle-to-PostgreSQL mappings.

| Oracle     | PostgreSQL  |
|------------|-------------|
| `VARCHAR2` | `VARCHAR`   |
| `NUMBER`   | `NUMERIC`   |
| `DATE`     | `TIMESTAMP` |
| `CLOB`     | `TEXT`      |
| `BLOB`     | `BYTEA`     |

Example:

```text
Oracle VARCHAR2  ──>  PostgreSQL VARCHAR
Oracle NUMBER    ──>  PostgreSQL NUMERIC
```

---

## 7. Responsive Dashboard

The frontend has been refactored to support different screen sizes.

```text
Supported Viewport Range

320px ─────────────────────────────── 1920px
Mobile          Tablet          Desktop
```

### Responsive improvements

- Fluid layouts
- Dynamic CSS grids
- `clamp()` based typography
- Auto-fitting cards
- Responsive tables
- Flexible dashboard sections
- Mobile-friendly forms
- Reduced horizontal overflow
- Improved dashboard spacing

Example responsive grid:

```css
grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
```

The UI has been refactored across:

```text
Dashboard.jsx
MigrationForm.jsx
Header.jsx
LogViewer.jsx
DownloadCenter.jsx
MigrationHistory.jsx
StatsCard.jsx
```

---

# 🔥 Phase 3 — AI Intelligence

## 8. Self-Healing Schema Engine

The platform includes a self-healing schema engine implemented in:

```text
backend/ai_translator.py
```

The engine intercepts PostgreSQL execution errors during schema migration and attempts to **automatically repair incompatible SQL**.

### Self-Healing Workflow

```text
Source SQL
    │
    ▼
PostgreSQL Execution
    │
    ▼
Error Detected?
  ├── NO ──────────────────────────────┐
  │                                    │
  └── YES                              │
        │                              │
        ▼                              │
  AI / Heuristic Analysis              │
        │                              │
        ▼                              │
  Generate Corrected SQL               │
        │                              │
        ▼                              │
  Validate using SAVEPOINT             │
        │                              │
        ▼                              │
    Successful?                        │
     ├── YES ──> Commit ───────────────┤
     │                                 │
     └── NO ───> Retry / Report        │
                                       │
                                       ▼
                              Continue Migration
```

---

## 9. Self-Healing SQL Rules

The engine can handle common database dialect differences.

| Source     | Source Syntax    | PostgreSQL Result                  |
|------------|------------------|------------------------------------|
| SQL Server | `GETDATE()`      | `CURRENT_TIMESTAMP`                |
| SQL Server | `DATETIME2`      | `TIMESTAMP`                        |
| MySQL      | `AUTO_INCREMENT` | `GENERATED ALWAYS AS IDENTITY`     |
| MySQL      | `` `customer_id` `` | `"customer_id"`                 |

The engine can use:

- 🤖 **AI models**
- 📏 **Built-in heuristic rules**
- 🧠 **Previously learned schema mappings**

---

## 10. Schema Memory

Learned or successfully applied migration rules are stored in:

```text
mappings/schema_memory.json
```

This allows the migration engine to **reuse previously learned mappings** in future migrations.

```text
Migration Error
      │
      ▼
Repair Rule
      │
      ▼
Validation
      │
      ▼
schema_memory.json
      │
      ▼
Future Migration
      │
      ▼
Automatic Rule Reuse
```

---

## 11. Self-Healing Audit Report

Self-healing actions are recorded in:

```text
self_healing_report.json
```

The report provides traceability for automatically repaired schema operations.

This improves:

- Debugging
- Auditability
- Migration transparency
- Operational monitoring

---

## 12. AI Routine Translator

The platform includes a **RoutineTranslator** in:

```text
backend/ai_translator.py
```

It translates database routines into PostgreSQL-compatible **PL/pgSQL**.

### Supported routine categories

- Stored procedures
- Functions
- Triggers

```text
MSSQL T-SQL
     │
     ▼
AI Routine Translator
     │
     ▼
PostgreSQL PL/pgSQL
```

Example target structure:

```sql
CREATE OR REPLACE FUNCTION function_name(...)
RETURNS ... AS $$
BEGIN
    ...
END;
$$ LANGUAGE plpgsql;
```

Translated routines can be deployed directly to the PostgreSQL target database.

---

## 13. Routine Reports

The platform generates JSON reports for translated database routines.

```text
procedure_report.json
trigger_report.json
function_report.json
```

These reports provide visibility into routine migration and deployment.

---

## 14. Automated Data Quality Scoring

The platform includes:

```text
backend/data_quality.py
```

which implements the **`DataQualityScorer`**.

The system evaluates data quality using factors such as:

- Row completeness
- Schema completeness
- Column null ratios

The result is converted into a composite score:

```text
0% ─────────────────────────────── 100%
```

### Data Quality Classification

| Result              | Classification |
|---------------------|----------------|
| High quality        | 🟢 `EXCELLENT`    |
| Acceptable quality  | 🟡 `GOOD`         |
| Requires investigation | 🔴 `NEEDS_REVIEW` |

The generated report is:

```text
data_quality_report.json
```

---

## 15. New AI & Data Quality APIs

| Purpose               | Method | Endpoint                          | Description                                              |
|-----------------------|--------|-----------------------------------|----------------------------------------------------------|
| Self-Healing Report   | `GET`  | `/migration/self-healing-report`  | Returns the self-healing execution report                |
| Data Quality Report   | `GET`  | `/migration/data-quality-report`  | Returns the calculated data quality report               |
| Schema Memory         | `GET`  | `/migration/schema-memory`        | Returns learned schema transformation rules              |
| Routine Translation   | `POST` | `/migration/translate-routines`   | Translates supported routines into PostgreSQL routines   |

---

## ✨ Key Features

### 🗄️ Database Migration

- MSSQL → PostgreSQL
- MySQL → PostgreSQL
- Oracle → PostgreSQL
- Table migration
- View migration
- Index migration
- Constraint migration
- Stored procedure migration
- Function migration
- Trigger migration
- Incremental migration
- Resume interrupted migration

### 🤖 AI-Powered Analysis

- Foreign key detection
- Schema risk analysis
- Migration readiness assessment
- Column rename suggestions
- Automatic type mapping
- AI migration summary
- Self-healing schema correction
- Schema memory
- AI routine translation
- Data quality scoring

### ⚡ High-Performance Migration

- PostgreSQL COPY protocol
- Streaming data loading
- TSV buffer processing
- `io.StringIO`
- Automatic binary-column fallback
- Batched `execute_values()` fallback
- Large dataset optimization
- **50,000+ rows/sec** benchmark for supported workloads

### ✅ Validation Engine

- Row count validation
- Source vs target verification
- SHA-256 checksums
- Cell-by-cell reconciliation
- Missing record detection
- Extra record detection
- Data integrity checks
- Data quality scoring

### 📡 Monitoring & Tracking

- Real-time migration progress
- Migration status
- Audit trail
- Migration history
- Scheduler monitoring
- Scheduled jobs
- Execution logs
- Self-healing logs
- Routine translation reports

---

## 📄 Reporting

The platform generates:

- Validation Report
- Audit Report
- Checksum Report
- Reconciliation Report
- Migration Report
- Rollback Script
- Procedure Report
- Trigger Report
- Function Report
- Self-Healing Report
- Data Quality Report
- Schema Memory

---

## ⏰ Scheduler

The platform provides **automated migration scheduling**.

### Supported scheduling modes

- One-time migration
- Daily migration
- Weekly migration
- Monthly migration
- Yearly migration

### Additional scheduler capabilities

- Retry mechanism
- Execution tracking
- Failure logging
- Scheduler monitoring
- Enable / disable scheduled jobs
- Scheduled migration history

---

## 🧰 Technology Stack

### Backend

- Python 3.13
- FastAPI
- APScheduler
- Psycopg2
- PyODBC
- SQLAlchemy
- Pandas
- Oracle database connectivity
- PostgreSQL COPY protocol

### Frontend

- React
- Vite
- Axios
- React Icons
- CSS
- Responsive CSS Grid
- Responsive Forms

### Databases

| Role   | Database             |
|--------|----------------------|
| Source | Microsoft SQL Server |
| Source | MySQL                |
| Source | Oracle               |
| Target | PostgreSQL           |

### AI Components

- AI Schema Analyzer
- Foreign Key Detection Engine
- Rename Recommendation Engine
- Migration Risk Assessment
- Self-Healing Schema Engine
- Routine Translation Engine
- Schema Memory
- Data Quality Scoring Engine

---

## 📁 Project Structure

```text
AI-Database-Migration-Platform/
│
├── backend/
│   ├── adapters/
│   │   └── oracle_adapter.py
│   │
│   ├── routes/
│   │   └── migration.py
│   │
│   ├── ai_translator.py
│   ├── data_quality.py
│   ├── scheduler.py
│   ├── migration_tool.py
│   ├── postgres_connector.py
│   ├── config.py
│   └── main.py
│
├── mappings/
│   ├── mysql_to_postgres.json
│   ├── mssql_to_postgres.json
│   ├── oracle_to_postgres.json
│   └── schema_memory.json
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── MigrationForm.jsx
│   │   │   ├── Header.jsx
│   │   │   ├── LogViewer.jsx
│   │   │   ├── DownloadCenter.jsx
│   │   │   ├── MigrationHistory.jsx
│   │   │   └── StatsCard.jsx
│   │   │
│   │   ├── services/
│   │   │   └── api.js
│   │   │
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   │
│   ├── package.json
│   └── vite.config.js
│
├── reports/
│   ├── validation_report.json
│   ├── checksum_report.json
│   ├── reconciliation_report.json
│   ├── audit_report.json
│   ├── procedure_report.json
│   ├── trigger_report.json
│   ├── function_report.json
│   ├── self_healing_report.json
│   └── data_quality_report.json
│
├── rollback/
├── requirements.txt
└── README.md
```

---

## 🗃️ Database Tables

The platform maintains internal PostgreSQL tables for migration management and monitoring.

### `migration_profiles`

Stores reusable migration configurations.

```text
profile_id, profile_name, source_type, source_server, source_database,
source_user, source_password, target_host, target_database,
target_user, target_password, created_at
```

### `migration_scheduler`

Stores scheduled migration jobs.

```text
schedule_id, schedule_name, scheduled_time, weekday,
retry_count, profile_id, is_active, created_at
```

### `scheduler_execution_log`

Stores scheduler execution history.

```text
execution_id, schedule_id, execution_time, status,
duration_seconds, error_message
```

### `migration_history`

Stores completed migration executions.

```text
id, source, target, status, rows_migrated, started_at, completed_at
```

### `migration_audit_trail`

Stores detailed migration audit records.

```text
audit_id, started_at, completed_at, source_db, target_db,
tables_processed, rows_processed, validation_status, audit_status,
checksum_status, reconciliation_status, rollback_generated, report_generated
```

---

## ⚙️ Configuration

### MSSQL Source Configuration

```text
Source Type     : MSSQL
Source Server   : localhost\MSSQLSERVER01
Source Database : source_mssql
Username        : <your_username>
Password        : <your_password>
```

### MySQL Source Configuration

```text
Source Type     : MySQL
Source Server   : localhost
Source Database : source_mysql
Username        : <your_username>
Password        : <your_password>
```

### Oracle Source Configuration

```text
Source Type  : Oracle
Source Server: <oracle_host>
Port         : 1521
Service Name : <service_name>
Username     : <oracle_username>
Password     : <oracle_password>
```

### PostgreSQL Target Configuration

```text
Host     : <postgres_host>
Port     : 5432
Database : <database_name>
Username : <postgres_user>
Password : <postgres_password>
SSL Mode : require
```

For **local PostgreSQL**:

```text
Host     : localhost
Port     : 5432
Database : target_db
Username : postgres
Password : <postgres_password>
```

### Environment Variables

Create a `.env` file:

```env
POSTGRES_HOST=
POSTGRES_PORT=5432
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=

OPENAI_API_KEY=<api_key>
```

> ⚠️ **Never commit real credentials or API keys to GitHub.**

### Migration Profile Example

```json
{
  "profileName": "MSSQL_to_PostgreSQL",
  "sourceType": "mssql",
  "sourceServer": "localhost\\MSSQLSERVER01",
  "sourceDatabase": "source_mssql",
  "sourceUser": "",
  "sourcePassword": "",
  "targetHost": "<postgres_host>",
  "targetDatabase": "target_db",
  "targetUser": "<postgres_user>",
  "targetPassword": "<postgres_password>"
}
```

---

## 🔌 API Endpoints

### Connection & Migration

| Action           | Method | Endpoint                     | Description                              |
|------------------|--------|------------------------------|------------------------------------------|
| Test Connection  | `POST` | `/migration/test-connection` | Tests source and target connectivity     |
| Start Migration  | `POST` | `/migration/start`           | Starts a database migration              |
| Resume Migration | `POST` | `/migration/resume`          | Resumes an interrupted migration         |

### Migration Profiles

| Action         | Method | Endpoint               |
|----------------|--------|------------------------|
| Create Profile | `POST` | `/migration/profile`   |
| Get Profiles   | `GET`  | `/migration/profiles`  |

### Progress, Analysis & Audit

| Action             | Method | Endpoint                        | Description                        |
|--------------------|--------|---------------------------------|------------------------------------|
| Migration Progress | `GET`  | `/migration/progress`           | Returns current migration progress |
| Schema Analysis    | `GET`  | `/migration/schema-analysis`    | AI-powered schema analysis         |
| Validation Report  | `GET`  | `/migration/validation-report`  | Returns validation results         |
| Audit Trail        | `GET`  | `/migration/audit-trail`        | Detailed audit records             |
| Migration History  | `GET`  | `/migration/migration-history`  | Past migration executions          |

### Scheduler

| Action          | Method | Endpoint                     |
|-----------------|--------|------------------------------|
| Create Schedule | `POST` | `/migration/schedule`        |
| Get Schedules   | `GET`  | `/migration/schedules`       |
| Scheduler Logs  | `GET`  | `/migration/scheduler/logs`  |

### AI Intelligence APIs

| Action              | Method | Endpoint                          |
|---------------------|--------|-----------------------------------|
| Self-Healing Report | `GET`  | `/migration/self-healing-report`  |
| Data Quality Report | `GET`  | `/migration/data-quality-report`  |
| Schema Memory       | `GET`  | `/migration/schema-memory`        |
| Translate Routines  | `POST` | `/migration/translate-routines`   |

### Download APIs

| Report                | Method | Endpoint                    |
|-----------------------|--------|-----------------------------|
| Validation Report     | `GET`  | `/download/validation`      |
| Audit Report          | `GET`  | `/download/audit`           |
| Checksum Report       | `GET`  | `/download/checksum`        |
| Reconciliation Report | `GET`  | `/download/reconciliation`  |

---

## 🧠 Core Migration Functions

### `start_migration()`

Starts the complete migration workflow.

**Responsibilities:**

- Connect to source database
- Connect to PostgreSQL
- Extract schema metadata
- Analyze source schema
- Generate mappings
- Create target schema
- Migrate tables
- Migrate data
- Migrate views
- Migrate indexes
- Migrate constraints
- Migrate procedures
- Migrate functions
- Migrate triggers
- Validate migration
- Generate checksums
- Generate reconciliation report
- Generate rollback scripts
- Generate audit records

### `resume_migration()`

Resumes an interrupted migration from the **last completed migration stage**.

### `migrate_table()`

Migrates table structure and data. Supports high-performance PostgreSQL loading through `COPY`, with fallback to `execute_values()` when required.

### `migrate_views()`

Migrates database views.

### `migrate_procedures()`

Migrates stored procedures.

### `migrate_functions()`

Migrates database functions.

### `migrate_triggers()`

Migrates database triggers.

---

### 🩹 Self-Healing Engine — `SelfHealingAgent`

The `SelfHealingAgent` detects migration-related PostgreSQL errors and attempts to generate corrected SQL.

**Responsibilities include:**

- DDL error detection
- Constraint error handling
- View translation
- Default expression translation
- Data type conversion
- SQL dialect correction
- Rule reuse through schema memory
- Savepoint-based SQL validation
- Self-healing audit logging

### 🔁 Routine Translation Engine — `RoutineTranslator`

The `RoutineTranslator` handles conversion of source database routines into PostgreSQL-compatible PL/pgSQL.

```text
Source Routine
      │
      ▼
Dialect Detection
      │
      ▼
AI Translation
      │
      ▼
PL/pgSQL Generation
      │
      ▼
PostgreSQL Validation
      │
      ▼
Deployment
      │
      ▼
Routine Report
```

### 📊 Data Quality Engine — `DataQualityScorer`

Evaluates migrated data using:

- Row completeness
- Schema completeness
- Null ratio analysis
- Migration consistency

```text
Data Quality Score ──> 0 – 100% ──> Classification
```

Generated report: `data_quality_report.json`

---

### ✅ Validation Engine

| Function                            | Purpose                                                                    |
|-------------------------------------|----------------------------------------------------------------------------|
| `validate_counts()`                 | Validates source and target row counts                                     |
| `generate_checksum_report()`        | Generates SHA-256 checksum validation results                              |
| `generate_reconciliation_report()`  | Identifies matching, missing, extra records and data mismatches            |

### 📝 Audit Engine

| Function                    | Purpose                                                          |
|-----------------------------|------------------------------------------------------------------|
| `save_audit_trail()`        | Stores detailed migration audit information                      |
| `save_history()`            | Stores migration execution history                               |
| `generate_rollback_script()`| Generates SQL to reverse migration operations where supported    |

### ⏱️ Scheduler Engine

| Function                    | Purpose                                   |
|-----------------------------|-------------------------------------------|
| `schedule_migration()`      | Creates scheduled migration jobs          |
| `run_scheduled_migration()` | Executes scheduled migrations             |
| `save_execution_log()`      | Stores scheduler execution details        |

---

## 📋 Reports Generated

| Report                | Contains                                                                                   |
|-----------------------|--------------------------------------------------------------------------------------------|
| **Validation Report** | Source row counts, target row counts, validation status                                    |
| **Audit Report**      | Migration metadata, execution timestamps, source/target database, status information       |
| **Checksum Report**   | Source checksum, target checksum, verification result                                      |
| **Reconciliation**    | Matching records, missing records, extra records, validation summary                       |
| **Rollback Script**   | SQL scripts required to revert supported migration operations                              |
| **Procedure Report**  | Source procedure info, translated PostgreSQL procedure/function, deployment status         |
| **Trigger Report**    | Trigger translation and deployment information                                             |
| **Function Report**   | Function translation and deployment information                                            |
| **Self-Healing Report** | Detected errors, applied corrections, corrected SQL, validation status, migration context |
| **Data Quality Report** | Data quality score, completeness metrics, null-ratio analysis, classification            |

---

## 🖥️ Dashboard

The frontend provides a centralized migration dashboard.

```text
KPI Cards
 ├── Total Migrations
 ├── Rows Migrated
 ├── Validation Status
 └── Scheduled Jobs
        │
        ▼
Migration Dashboard
 ├── Tables
 ├── Rows
 ├── Views
 ├── Procedures
 ├── Functions
 └── AI Risk
        │
        ▼
Migration Progress
        │
        ▼
Audit Trail + Migration Summary
        │
        ▼
Validation Summary
        │
        ▼
Checksum Validation
        │
        ▼
Reconciliation Report
        │
        ▼
Migration Scheduler
 ├── Scheduler Monitoring
 └── Scheduled Jobs
        │
        ▼
AI Summary
 ├── Foreign Keys
 └── Rename Suggestions
        │
        ▼
Download Center
        │
        ▼
Logs
        │
        ▼
Migration History
```

---

## ▶️ Running the Project

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at: **http://localhost:8000**

### Swagger Documentation

Open: **http://localhost:8000/docs**

FastAPI automatically provides interactive API documentation.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## 🔄 Migration Workflow

```text
Configure Source Database
          │
          ▼
Configure PostgreSQL Target
          │
          ▼
Test Connection
          │
          ▼
Extract Database Metadata
          │
          ▼
AI Schema Analysis
          │
          ▼
Automatic Type Mapping
          │
          ▼
Foreign Key Detection
          │
          ▼
Schema Risk Assessment
          │
          ▼
Self-Healing / SQL Translation
          │
          ▼
Create Target Schema
          │
          ▼
High-Performance Data Migration
          │
          ▼
Routine Migration
          │
          ▼
Validation
          │
          ▼
SHA-256 Checksum Verification
          │
          ▼
Cell-by-Cell Reconciliation
          │
          ▼
Data Quality Scoring
          │
          ▼
Report Generation
          │
          ▼
Audit Logging
          │
          ▼
Migration History
```

---

## 🛡️ Enterprise Reliability Features

The platform is designed around **four major reliability principles**.

### 1️⃣ Validation

```text
Row Counts + Checksums + Reconciliation + Data Quality
```

### 2️⃣ Recoverability

```text
Resume Migration + Incremental Migration + Rollback Generation
```

### 3️⃣ Observability

```text
Real-Time Progress + Logs + Audit Trail + Migration History + Scheduler Logs
```

### 4️⃣ Intelligent Error Handling

```text
Schema Analysis + Automatic Mapping + Self-Healing + Routine Translation + Schema Memory
```

---

## ✔️ Current Capabilities

- ✅ MSSQL → PostgreSQL
- ✅ MySQL → PostgreSQL
- ✅ Oracle → PostgreSQL
- ✅ PostgreSQL COPY Streaming
- ✅ 50,000+ rows/sec benchmark
- ✅ Binary Column Fallback
- ✅ AI Schema Analysis
- ✅ Foreign Key Detection
- ✅ Schema Risk Analysis
- ✅ Column Rename Suggestions
- ✅ Automatic Type Mapping
- ✅ Self-Healing Schema Engine
- ✅ Schema Memory
- ✅ AI Routine Translation
- ✅ Procedure Translation
- ✅ Function Translation
- ✅ Trigger Translation
- ✅ SHA-256 Checksum Verification
- ✅ Cell-by-Cell Reconciliation
- ✅ Data Quality Scoring
- ✅ Validation Reports
- ✅ Audit Reports
- ✅ Reconciliation Reports
- ✅ Rollback Generation
- ✅ Resume Migration
- ✅ Incremental Migration
- ✅ Migration Scheduler
- ✅ Retry Mechanism
- ✅ Scheduler Monitoring
- ✅ Real-Time Migration Monitoring
- ✅ Responsive Dashboard

---

## 🔒 Security Considerations

The platform is designed to support secure database migration workflows.

**Recommended practices:**

- Store credentials in environment variables
- Never commit passwords to Git
- Never commit API keys
- Use encrypted database connections where supported
- Restrict database users to required permissions
- Use PostgreSQL SSL for remote deployments
- Protect generated reports containing sensitive information
- Restrict access to migration logs
- Use separate credentials for development and production

Example:

```env
POSTGRES_PASSWORD=
OPENAI_API_KEY=<api_key>
```

> ⚠️ Do not replace these placeholders with real production credentials in the repository.

---

## ⚡ Performance Considerations

For large migrations, performance depends on:

- Source database performance
- Target PostgreSQL performance
- Network bandwidth
- Row size
- Number of columns
- Number of indexes
- Constraint complexity
- Binary data
- Transformation complexity

The platform uses **PostgreSQL COPY streaming** where applicable to maximize bulk-loading performance. For binary-heavy tables, the system can automatically use the safer batched insertion path.

---

## 🔮 Future Scope

### Infrastructure

- Dockerized deployment
- Kubernetes deployment
- Horizontal scaling
- Distributed migration workers
- Cloud-native deployment

### Database Support

- MongoDB migration
- MariaDB migration
- AWS RDS migration
- Azure SQL migration
- Additional Oracle migration enhancements

### AI & Automation

- AI-generated ETL pipelines
- Automatic conflict resolution
- Advanced schema evolution
- Intelligent migration planning
- Predictive migration failure detection
- Advanced anomaly detection

### Enterprise Platform

- User authentication
- Role-Based Access Control
- Multi-tenant architecture
- Team workspaces
- Email notifications
- Slack integration
- Microsoft Teams integration
- Centralized migration management

---

## ⚠️ Known Limitations

- Migration performance depends on source, target, network, and dataset characteristics.
- Binary-heavy tables may use the batched insertion fallback instead of COPY.
- Complex database-specific procedures may require manual review after translation.
- Complex functions may require manual review.
- Self-healing rules are dependent on the type and context of the migration error.
- Local scheduler deployment is currently the primary deployment model.
- Production deployments require additional authentication and access-control layers.

---

## 🎯 Project Use Case

The platform is designed for organizations that need to migrate legacy or heterogeneous databases into PostgreSQL while maintaining:

> **Data Integrity + Validation + Auditability + Recoverability + Performance + Automation**

**Typical use cases include:**

- Legacy database modernization
- SQL Server → PostgreSQL migration
- MySQL → PostgreSQL migration
- Oracle → PostgreSQL migration
- Enterprise database consolidation
- Database modernization projects
- Development and staging migrations
- Large-scale data migration
- Schema compatibility analysis

### Project Outcomes

The platform aims to reduce manual migration effort by combining:

> **Database Engineering + AI + Automation + Validation + Observability**

Instead of treating database migration as a simple data-copy operation, the platform treats migration as a **complete lifecycle**:

```text
Analyze ──> Plan ──> Map ──> Migrate ──> Validate ──> Reconcile ──> Score ──> Audit ──> Monitor
```

---

## 👨‍💻 Contributors

**Ravi Raj Choubey**
B.Tech Data Science — VIT Chennai

**Project:** AI Database Migration Platform
*Enterprise Database Migration, Validation, Performance Optimization and AI-Powered Schema Intelligence*

---

## 📜 License

This project is intended for **educational, research, and enterprise database migration purposes**.
