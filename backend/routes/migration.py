from fastapi import APIRouter
from migration_tool import MigrationTool
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
import os
import pyodbc
import psycopg2
from fastapi.responses import FileResponse
from config import TARGET_DB
from postgres_connection import get_pg_connection
router = APIRouter()

class ConnectionRequest(
    BaseModel
):

    sourceType: str
    sourceServer: str
    sourceDatabase: str
    sourceUser: str
    sourcePassword: str

    targetHost: str
    targetDatabase: str
    targetUser: str
    targetPassword: str

class ProfileRequest(BaseModel):

    profileName: str

    sourceType: str

    sourceServer: str

    sourceDatabase: str

    sourceUser: str

    sourcePassword: str

    targetHost: str

    targetDatabase: str

    targetUser: str

    targetPassword: str

class ScheduleRequest(
    BaseModel
):

    schedule_name: str

    schedule_type: str

    scheduled_date: str | None = None

    scheduled_time: str

    weekday: str | None = None

    retry_count: int

    profile_id: int

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

@router.get("/status")
def migration_status():

    return {
        "status": "Ready"
    }


@router.post("/start")
def start_migration(
    request: ConnectionRequest
):

    try:

        tool = MigrationTool(
            request.model_dump()
        )

        tool.run()

        return {
            "status": "SUCCESS",
            "message": "Migration completed"
        }

    except Exception as e:

        return {
            "status": "FAILED",
            "error": str(e)
        }
    
@router.get("/report")
def get_report():

    report_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "..",
        "migration_report.json"
    )

    with open(report_file, "r") as f:

        report = json.load(f)

    return report

@router.get("/download-report")
def download_report():

    return FileResponse(
        "../migration_report.json",
        filename="migration_report.json"
    )


@router.get("/download-rollback")
def download_rollback():

    return FileResponse(
        "../rollback.sql",
        filename="rollback.sql"
    )


@router.get("/download-procedures")
def download_procedures():

    return FileResponse(
        "../procedure_report.json",
        filename="procedure_report.json"
    )


@router.get("/download-functions")
def download_functions():

    return FileResponse(
        "../function_report.json",
        filename="function_report.json"
    )

@router.get("/logs")
def get_logs():

    with open(
        "../migration.log",
        "r"
    ) as f:

        logs = f.readlines()

    return {
        "logs": logs[-50:]
    }

@router.post("/test-connection")
def test_connection(
    request: ConnectionRequest
):

    try:

        # ==========================
        # SOURCE DATABASE VALIDATION
        # ==========================

        if request.sourceType == "mssql":

            if request.sourceUser.strip():

                source_conn = pyodbc.connect(

                    f"""
                    DRIVER={{ODBC Driver 17 for SQL Server}};
                    SERVER={request.sourceServer};
                    DATABASE={request.sourceDatabase};
                    UID={request.sourceUser};
                    PWD={request.sourcePassword};
                    TrustServerCertificate=yes;
                    """,

                    timeout=5

                )

            else:

                source_conn = pyodbc.connect(

                    f"""
                    DRIVER={{ODBC Driver 17 for SQL Server}};
                    SERVER={request.sourceServer};
                    DATABASE={request.sourceDatabase};
                    Trusted_Connection=yes;
                    TrustServerCertificate=yes;
                    """,

                    timeout=5

                )

            source_conn.close()

        # ==========================
        # MYSQL VALIDATION
        # ==========================

        elif request.sourceType == "mysql":

            import pymysql

            source_conn = pymysql.connect(

                host=request.sourceServer,
                user=request.sourceUser,
                password=request.sourcePassword,
                database=request.sourceDatabase,

                connect_timeout=5

            )

            source_conn.close()

        # ==========================
        # POSTGRES VALIDATION
        # ==========================

        pg_conn = psycopg2.connect(

            host=request.targetHost,

            database=request.targetDatabase,

            user=request.targetUser,

            password=request.targetPassword,

            connect_timeout=5

        )

        pg_conn.close()

        return {

            "status": "SUCCESS",

            "message":
            "Source and Target connections successful"

        }

    except Exception as e:

        return {

            "status": "FAILED",

            "message": str(e)

        }
    
@router.get("/progress")
def get_progress():

    progress_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "migration_progress.json"
    )

    print("PROGRESS FILE:", progress_file)
    print("EXISTS:", os.path.exists(progress_file))

    if not os.path.exists(progress_file):

        return {
            "progress": 0,
            "current_table": "",
            "status": "IDLE"
        }

    with open(progress_file, "r") as f:
        progress = json.load(f)

    return progress

@router.get("/history")
def get_history():

    conn = psycopg2.connect(

        host=TARGET_DB["host"],
        port=TARGET_DB["port"],
        user=TARGET_DB["user"],
        password=TARGET_DB["password"],
        dbname=TARGET_DB["database"]

    )

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            id,
            source_db,
            target_db,
            tables_count,
            rows_count,
            status,
            migration_time

        FROM migration_history

        ORDER BY id DESC

    """)

    rows = cursor.fetchall()

    history = []

    for row in rows:

        history.append({

            "id": row[0],

            "source_db": row[1],

            "target_db": row[2],

            "tables_count": row[3],

            "rows_count": row[4],

            "status": row[5],

            "migration_time": str(row[6])

        })

    cursor.close()

    conn.close()

    return history

@router.post("/resume")
def resume_migration():

    try:

        tool = MigrationTool()

        tool.run()

        return {
            "status": "SUCCESS",
            "message": "Migration resumed"
        }

    except Exception as e:

        return {
            "status": "FAILED",
            "error": str(e)
        }
    
@router.post("/reset-table/{table_name}")
def reset_table(table_name: str):

    try:

        conn = psycopg2.connect(
            host=TARGET_DB["host"],
            port=TARGET_DB["port"],
            user=TARGET_DB["user"],
            password=TARGET_DB["password"],
            dbname=TARGET_DB["database"]
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM migration_status
            WHERE table_name = %s
            """,
            (table_name,)
        )

        cursor.execute(
            """
            DELETE FROM migration_stages
            WHERE table_name = %s
            """,
            (table_name,)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "SUCCESS",
            "message": f"{table_name} reset successfully"
        }

    except Exception as e:

        return {
            "status": "FAILED",
            "error": str(e)
        }
    
@router.get("/schema-mapping")
def get_schema_mapping():

    report_file = os.path.join(
        os.path.dirname(
            os.path.dirname(__file__)
        ),
        "schema_mapping_report.json"
    )

    with open(
        report_file,
        "r",
        encoding="utf-8"
    ) as f:

       return json.load(f)
    
@router.get("/schema-analysis")
def get_schema_analysis():

    report_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "schema_mapping_report.json"
    )

    print("READING:", report_file)

    with open(report_file, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/regenerate-report")
def regenerate_report():

    try:

        config = {

            "sourceType": "mysql",
            "targetHost": TARGET_DB["host"],
            "targetUser": TARGET_DB["user"],
            "targetPassword": TARGET_DB["password"],
            "targetDatabase": TARGET_DB["database"]

        }

        tool = MigrationTool(config)

        tool.generate_Eschema_mapping_report()

        return {
            "status": "SUCCESS"
        }

    except Exception as e:

        return {
            "status": "FAILED",
            "error": str(e)
        }
    
@router.get("/validation-report")
def get_validation_report():

    report_file = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)
            )
        ),
        "validation_report.json"
    )

    with open(
        report_file,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)
    
@router.get("/metrics-report")
def get_metrics_report():

    with open(
        "metrics_report.json",
        "r"
    ) as f:

        return json.load(f)
    
@router.get("/audit-report")
def get_audit_report():

    report_file = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)
            )
        ),
        "audit_report.json"
    )

    with open(
        report_file,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)
    
@router.get("/checksum-report")
def get_checksum_report():

    report_file = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)
            )
        ),
        "checksum_report.json"
    )

    with open(
        report_file,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)
    
@router.get("/reconciliation-report")
def get_reconciliation_report():

    report_file = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)
            )
        ),
        "reconciliation_report.json"
    )

    with open(
        report_file,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)
    
@router.get("/audit-trail")
def get_audit_trail():

    conn = get_pg_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM migration_audit_trail
        ORDER BY audit_id DESC
        """
    )

    rows = cursor.fetchall()

    result = []

    for row in rows:

        result.append({

            "audit_id": row[0],
            "started_at": str(row[1]),
            "completed_at": str(row[2]),
            "source_db": row[3],
            "target_db": row[4],
            "tables_processed": row[5],
            "rows_processed": row[6],
            "validation_status": row[7],
            "audit_status": row[8],
            "checksum_status": row[9],
            "reconciliation_status": row[10]

        })

    cursor.close()
    conn.close()

    return result

@router.get("/download/validation")
def download_validation():

    return FileResponse(
        os.path.join(
            PROJECT_ROOT,
            "validation_report.json"
        ),
        filename="validation_report.json"
    )

@router.get("/download/audit")
def download_audit():

    return FileResponse(
        os.path.join(
            PROJECT_ROOT,
            "audit_report.json",
        ),
        filename="audit_report.json"
    )

@router.get("/download/checksum")
def download_checksum():

    return FileResponse(
        os.path.join(
            PROJECT_ROOT,
            "checksum_report.json",
        ),
        filename="checksum_report.json"
    )

@router.get("/download/reconciliation")
def download_reconciliation():

    return FileResponse(
        os.path.join(
            PROJECT_ROOT,
            "reconciliation_report.json",
        ),
        filename="reconciliation_report.json"
    )

@router.get("/migration-history")
def get_migration_history():

    conn = get_pg_connection()

    cursor = conn.cursor()

    cursor.execute(

        """

        SELECT

            audit_id,

            source_db,

            target_db,

            tables_processed,

            rows_processed,

            validation_status,

            started_at,

            completed_at

        FROM migration_audit_trail

        ORDER BY audit_id DESC

        LIMIT 20

        """

    )

    rows = cursor.fetchall()

    columns = [

        desc[0]

        for desc in cursor.description

    ]

    result = [

        dict(zip(columns, row))

        for row in rows

    ]

    cursor.close()

    conn.close()

    return result

@router.post("/schedule")
def create_schedule(
    request: ScheduleRequest
):

    conn = psycopg2.connect(

        host=TARGET_DB["host"],
        database=TARGET_DB["database"],
        user=TARGET_DB["user"],
        password=TARGET_DB["password"]

    )

    cursor = conn.cursor()

    cursor.execute(

        """

        INSERT INTO migration_scheduler (

            schedule_name,
            schedule_type,
            scheduled_date,
            scheduled_time,
            weekday,
            retry_count,
            profile_id
        )

        VALUES (

            %s,%s,%s,%s,%s,%s,%s
        )

        """,

        (
            request.schedule_name,
            request.schedule_type,
            request.scheduled_date,
            request.scheduled_time,
            request.weekday,
            request.retry_count,
            request.profile_id
        )

    )

    conn.commit()

    cursor.close()

    conn.close()

    # RELOAD APSCHEDULER
    from scheduler import register_jobs

    register_jobs()

    return {

        "status": "SUCCESS"

    }

@router.get("/schedules")
def get_schedules():

    conn = psycopg2.connect(

        host=TARGET_DB["host"],
        database=TARGET_DB["database"],
        user=TARGET_DB["user"],
        password=TARGET_DB["password"]

    )

    cursor = conn.cursor()

    cursor.execute(

        """

        SELECT *

        FROM migration_scheduler

        ORDER BY schedule_id DESC

        """

    )

    rows = cursor.fetchall()

    columns = [

        desc[0]

        for desc in cursor.description

    ]

    result = [

        dict(zip(columns, row))

        for row in rows

    ]

    cursor.close()

    conn.close()

    return result

@router.delete("/schedule/{schedule_id}")
def delete_schedule(

    schedule_id: int

):

    conn = psycopg2.connect(

        host=TARGET_DB["host"],
        database=TARGET_DB["database"],
        user=TARGET_DB["user"],
        password=TARGET_DB["password"]

    )

    cursor = conn.cursor()

    cursor.execute(

        """

        DELETE FROM migration_scheduler

        WHERE schedule_id = %s

        """,

        (schedule_id,)

    )

    conn.commit()

    cursor.close()

    conn.close()

    return {

        "status": "SUCCESS"

    }

@router.put("/schedule/toggle/{schedule_id}")
def toggle_schedule(

    schedule_id: int

):

    conn = psycopg2.connect(

        host=TARGET_DB["host"],
        database=TARGET_DB["database"],
        user=TARGET_DB["user"],
        password=TARGET_DB["password"]

    )

    cursor = conn.cursor()

    cursor.execute(

        """

        UPDATE migration_scheduler

        SET is_active = NOT is_active

        WHERE schedule_id = %s

        """,

        (schedule_id,)

    )

    conn.commit()

    cursor.close()

    conn.close()

    return {

        "status": "SUCCESS"

    }

@router.post("/profile")
def save_profile(

    request: ProfileRequest

):

    conn = psycopg2.connect(

        host=TARGET_DB["host"],
        database=TARGET_DB["database"],
        user=TARGET_DB["user"],
        password=TARGET_DB["password"]

    )

    cursor = conn.cursor()

    cursor.execute(

        """

        INSERT INTO migration_profiles (

            profile_name,

            source_type,
            source_server,
            source_database,
            source_user,
            source_password,

            target_host,
            target_database,
            target_user,
            target_password

        )

        VALUES (

            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s

        )

        """,

        (

            request.profileName,

            request.sourceType,
            request.sourceServer,
            request.sourceDatabase,
            request.sourceUser,
            request.sourcePassword,

            request.targetHost,
            request.targetDatabase,
            request.targetUser,
            request.targetPassword

        )

    )

    conn.commit()

    cursor.close()

    conn.close()

    return {

        "status": "SUCCESS"

    }

@router.get("/scheduler/logs")
def get_scheduler_logs():

    conn = psycopg2.connect(

        host=TARGET_DB["host"],
        database=TARGET_DB["database"],
        user=TARGET_DB["user"],
        password=TARGET_DB["password"]

    )

    cursor = conn.cursor()

    cursor.execute(

        """

        SELECT *

        FROM scheduler_execution_log

        ORDER BY execution_id DESC

        """

    )

    rows = cursor.fetchall()

    cursor.close()

    conn.close()

    return rows

@router.get("/scheduler/logs")
def get_scheduler_logs():

    conn = psycopg2.connect(

        host=TARGET_DB["host"],
        database=TARGET_DB["database"],
        user=TARGET_DB["user"],
        password=TARGET_DB["password"]

    )

    cursor = conn.cursor()

    cursor.execute(

        """

        SELECT

            execution_id,
            schedule_id,
            execution_time,
            status,
            duration_seconds,
            error_message

        FROM scheduler_execution_log

        ORDER BY execution_id DESC

        """

    )

    rows = cursor.fetchall()

    cursor.close()

    conn.close()

    return rows

@router.get("/profiles")
def get_profiles():

    conn = psycopg2.connect(

        host=TARGET_DB["host"],
        database=TARGET_DB["database"],
        user=TARGET_DB["user"],
        password=TARGET_DB["password"]

    )

    cursor = conn.cursor()

    cursor.execute(

        """

        SELECT *

        FROM migration_profiles

        ORDER BY profile_id DESC

        """

    )

    rows = cursor.fetchall()
    print("GET PROFILES CALLED")
    print("ROWS:", rows)

    columns = [

        desc[0]

        for desc in cursor.description

    ]

    result = [

        dict(zip(columns, row))

        for row in rows

    ]

    cursor.close()

    conn.close()

    return result