import sys
import os
import time
import psycopg2

sys.path.append(
    os.path.abspath("..")
)

import psycopg2

from config import TARGET_DB

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

scheduler = BackgroundScheduler()


def test_job():

    print(
        f"JOB EXECUTED: {datetime.now()}"
    )

scheduler.add_job(

    test_job,

    "interval",

    minutes=1

)

def run_scheduled_migration(
    schedule_id,
    retry_count=0
):

    start_time = time.time()

    print(
        "SCHEDULED MIGRATION STARTED"
    )

    attempt = 0

    while attempt <= retry_count:

        try:

            config = {

                "sourceType": "mssql",

                "sourceServer": "localhost",

                "sourceDatabase": "your_source_db",

                "sourceUser": "sa",

                "sourcePassword": "your_password",

                "targetHost": TARGET_DB["host"],

                "targetDatabase": TARGET_DB["database"],

                "targetUser": TARGET_DB["user"],

                "targetPassword": TARGET_DB["password"]

            }

            from migration_tool import MigrationTool

            MigrationTool(config).run()

            duration = int(
                time.time() - start_time
            )

            save_execution_log(

                schedule_id,

                "SUCCESS",

                duration,

                None

            )

            print(
                "SCHEDULED MIGRATION COMPLETED"
            )

            return

        except Exception as e:

            attempt += 1

            print(

                f"ATTEMPT {attempt} FAILED:",

                e

            )

            if attempt > retry_count:

                duration = int(
                    time.time() - start_time
                )

                save_execution_log(

                    schedule_id,

                    "FAILED",

                    duration,

                    str(e)

                )

    print(

        "ALL RETRIES FAILED"

    )

def load_schedules():

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
    
            schedule_id,
            schedule_name,
            schedule_type,
            scheduled_date,
            scheduled_time,
            weekday,
            retry_count,
            profile_id

        FROM migration_scheduler

        WHERE is_active = TRUE

        """

    )

    rows = cursor.fetchall()

    cursor.close()

    conn.close()

    return rows

def save_execution_log(
    schedule_id,
    status,
    duration,
    error_message
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

        INSERT INTO scheduler_execution_log(

            schedule_id,
            execution_time,
            status,
            duration_seconds,
            error_message

        )

        VALUES(

            %s,
            NOW(),
            %s,
            %s,
            %s

        )

        """,

        (

            schedule_id,
            status,
            duration,
            error_message

        )

    )

    conn.commit()

    cursor.close()

    conn.close()

def register_jobs():

    scheduler.remove_all_jobs()

    print("REGISTER_JOBS EXECUTED")

    schedules = load_schedules()

    print("SCHEDULES:", schedules)

    for schedule in schedules:

        print("PROCESSING:", schedule)

        schedule_id = schedule[0]

        schedule_name = schedule[1]

        schedule_type = schedule[2]

        retry_count = schedule[6]

        scheduled_time = str(schedule[4])

        hour = int(
            scheduled_time.split(":")[0]
        )

        minute = int(
            scheduled_time.split(":")[1]
        )

        if schedule_type == "Daily":

            print(
                "REGISTERING:",
                schedule_id,
                retry_count
            )

            scheduler.add_job(

                run_scheduled_migration,

                trigger="cron",

                hour=hour,

                minute=minute,

                args=[schedule_id,retry_count],

                id=f"job_{schedule_id}",

                replace_existing=True

            )

            print(

                f"REGISTERED: {schedule_name}"

            )
        
        elif schedule_type == "Weekly":

            weekday = schedule[5]

            weekday_map = {

                "Sunday": "sun",
                "Monday": "mon",
                "Tuesday": "tue",
                "Wednesday": "wed",
                "Thursday": "thu",
                "Friday": "fri",
                "Saturday": "sat"

            }

            print(
                "REGISTERING:",
                schedule_id,
                retry_count
            )

            scheduler.add_job(

                run_scheduled_migration,

                trigger="cron",

                day_of_week=
                    weekday_map[weekday],

                hour=hour,

                minute=minute,

                args=[
                    schedule_id,
                    retry_count
                ],

                id=f"job_{schedule_id}",

                replace_existing=True

            )

            print(

                f"REGISTERED WEEKLY JOB: "
                f"{schedule_name}"

            )

        elif schedule_type == "Monthly":

            day = schedule[3].day

            print(
                "REGISTERING:",
                schedule_id,
                retry_count
            )

            scheduler.add_job(

                run_scheduled_migration,

                trigger="cron",

                day=day,

                hour=hour,

                minute=minute,
                
                args=[
                    schedule_id,
                    retry_count
                ],

                id=f"job_{schedule_id}",

                replace_existing=True

            )

            print(

                f"REGISTERED MONTHLY JOB: "
                f"{schedule_name}"

            )

        elif schedule_type == "Yearly":

            month = schedule[3].month

            day = schedule[3].day

            print(
                "REGISTERING:",
                schedule_id,
                retry_count
            )

            scheduler.add_job(

                run_scheduled_migration,

                trigger="cron",

                month=month,

                day=day,

                hour=hour,

                minute=minute,

                args=[
                    schedule_id,
                    retry_count
                ],

                id=f"job_{schedule_id}",

                replace_existing=True

            )

            print(

                f"REGISTERED YEARLY JOB: "
                f"{schedule_name}"

            )

        elif schedule_type == "One Time":

            scheduled_date = schedule[3]

            print(
                "REGISTERING:",
                schedule_id,
                retry_count
            )

            scheduler.add_job(

                run_scheduled_migration,

                trigger="date",

                run_date=f"{scheduled_date} {scheduled_time}",

                args=[
                    schedule_id,
                    retry_count
                ],

                id=f"job_{schedule_id}",

                replace_existing=True

            )

            print(
                f"REGISTERED ONE TIME JOB: {schedule_name}"
            )



print("STARTING APSCHEDULER")

scheduler.start()

print("CALLING REGISTER_JOBS")

register_jobs()