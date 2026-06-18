import psycopg2
import os
from psycopg2.extras import execute_values
import json
import logging
import hashlib
from datetime import datetime
from adapters.factory import get_adapter
from config import SOURCE_DB, TARGET_DB

# Logging Configuration
logging.basicConfig(
    filename='migration.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class MigrationTool:

    def __init__(self,config):

        self.config = config

        self.pg_conn = psycopg2.connect(
            host=config["targetHost"],
            port=5432,
            user=config["targetUser"],
            password=config["targetPassword"],
            dbname=config["targetDatabase"]
        )

        self.source = get_adapter(
            config["sourceType"]
        )

        import os

        mapping_file = os.path.join(
            os.path.dirname(__file__),
            "mappings",
            "mysql_to_postgres.json"
        )

        with open(mapping_file) as f:
            self.mapping = json.load(f)

        self.report = []
        self.rollback_statements = []

        logging.info(
            f"Migration initialized: "
            f"{SOURCE_DB['type']} -> PostgreSQL"
        )
    
    def generate_risk_analysis(
        self,
        report,
        fk_suggestions,
        rename_suggestions
    ):

        risk_score = 0
        issues = []

    # Foreign Keys
        if fk_suggestions:

            risk_score += (
                len(fk_suggestions) * 5
            )

            issues.append(
                f"{len(fk_suggestions)} foreign keys detected"
            )

    # Rename Suggestions
        if rename_suggestions:

            risk_score += (
                len(rename_suggestions) * 2
            )

            issues.append(
                f"{len(rename_suggestions)} column rename recommendations"
            )

    # Manual Review Columns
        manual_review_count = sum(

            1

            for item in report

            if item["recommendation"]
            == "Manual review recommended"

        )

        if manual_review_count:

            risk_score += (
                manual_review_count * 10
            )

            issues.append(
                f"{manual_review_count} columns need manual review"
            )

    # Cap score at 100
        risk_score = min(
            risk_score,
            100
        )

    # Risk Level
        if risk_score <= 30:

            level = "LOW"

        elif risk_score <= 60:

            level = "MEDIUM"

        else:

            level = "HIGH"

        return {

            "overall_risk": level,

            "risk_score": risk_score,

            "issues": issues

        }

    def update_progress(
        self,
        progress,
        current_table,
        status
    ):
        print(
            f"PROGRESS UPDATE: "
            f"{progress}% "
            f"{current_table} "
            f"{status}"
        )
        import json

        with open(
            "migration_progress.json",
            "w"
        ) as f:

            json.dump(
                {
                    "progress": progress,
                    "current_table": current_table,
                    "status": status
                },
                f,
                indent=4
            )

    def convert_type(self, source_type_name):

        source_type_name = (
            source_type_name.lower()
        )

        for source_type, target_type in self.mapping.items():

            if source_type_name.startswith(
                source_type
            ):

                if source_type == "decimal":

                    import re

                    match = re.search(
                        r'decimal\((\d+),(\d+)\)',
                        source_type_name
                    )

                    if match:

                        precision = match.group(1)

                        scale = match.group(2)

                        return (
                            f"NUMERIC({precision},{scale})"
                        )

                return target_type

        logging.warning(
            f"Unknown source type: "
            f"{source_type_name}"
        )

        return "TEXT"

    def create_table(self, table):

        columns = self.source.get_columns(table)

        column_defs = []

        primary_keys = []

        for col in columns:

            col_name = col["Field"]

            pg_type = self.convert_type(
                col["Type"]
            )

            extra = str(
                col.get("Extra", "")
            ).lower()

            if "auto_increment" in extra:

                if pg_type == "INTEGER":

                    pg_type = "SERIAL"

                elif pg_type == "BIGINT":

                    pg_type = "BIGSERIAL"

            column_defs.append(
                f'"{col_name}" {pg_type}'
            )

            if col.get("Key") == "PRI":

                primary_keys.append(
                    col_name
                )

        foreign_keys = (
            self.source.get_foreign_keys(
                table
            )
        )

        fk_clauses = []

        for fk in foreign_keys:

            fk_clauses.append(
                f'FOREIGN KEY ("{fk["COLUMN_NAME"]}") '
                f'REFERENCES "{fk["REFERENCED_TABLE_NAME"]}" '
                f'("{fk["REFERENCED_COLUMN_NAME"]}")'
            )

        all_constraints = []

        if primary_keys:

            all_constraints.append(
                "PRIMARY KEY ("
                + ",".join(
                    [f'"{pk}"'
                    for pk in primary_keys]
                )
                + ")"
            )

        all_constraints.extend(
            fk_clauses
        )

        query = f'''
        CREATE TABLE IF NOT EXISTS "{table}" (
            {",".join(column_defs)}
            {"," if all_constraints else ""}
            {",".join(all_constraints)}
        );
        '''

        cur = self.pg_conn.cursor()

        try:

            cur.execute(query)

            self.pg_conn.commit()

            print(
                f"Created table: {table}"
            )

            logging.info(
                f"Created table: {table}"
            )

            self.rollback_statements.append(
                f'DROP TABLE IF EXISTS "{table}" CASCADE;'
            )

        except Exception as e:

            self.pg_conn.rollback()

            logging.error(
                f"Create table failed "
                f"for {table}: {e}"
            )

            raise

        finally:

            cur.close()

    def migrate_data(self, table):

        columns = self.source.get_columns(table)

        column_names = [
            col["Field"]
            for col in columns
        ]

        source_cur = self.source.get_connection().cursor()

        source_cur.execute(
            f"SELECT * FROM {table}"
        )

        pg_cur = self.pg_conn.cursor()

        pg_cur.execute(
            f'TRUNCATE TABLE "{table}" CASCADE'
        )

        batch_size = 10000

        total_rows = 0

        column_list = ",".join(
            [f'"{col}"' for col in column_names]
        )

        insert_sql = f'''
        INSERT INTO "{table}"
        ({column_list})
        VALUES %s
        '''

        while True:

            rows = source_cur.fetchmany(
                batch_size
            )

            if not rows:
                break

            execute_values(
                pg_cur,
                insert_sql,
                rows,
                page_size=batch_size
            )

            total_rows += len(rows)

            print(
                f"{table}: {total_rows} rows migrated"
            )

        self.pg_conn.commit()

        source_cur.close()
        pg_cur.close()

        print(
            f"Migrated {total_rows} rows from {table}"
        )

        logging.info(
            f"Migrated {total_rows} rows from {table}"
        )

        return total_rows

    def validate(self, table):

        source_cur = self.source.get_connection().cursor()

        source_cur.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        source_count = source_cur.fetchone()[0]

        pg_cur = self.pg_conn.cursor()

        pg_cur.execute(
            f'SELECT COUNT(*) FROM "{table}"'
        )

        pg_count = pg_cur.fetchone()[0]

        source_cur.close()
        pg_cur.close()
        print(
            f"{table}: Source={source_count}, PostgreSQL={pg_count}"
        )

        logging.info(
            f"{table}: Source={source_count}, PostgreSQL={pg_count}"
        )

        return source_count == pg_count
    
    def create_views(self):

        import re

        views = self.source.get_views()

        cur = self.pg_conn.cursor()

        for view in views:

            view_name = view["TABLE_NAME"]

            definition = view["VIEW_DEFINITION"]

            if definition is None:

                print(
                    f"Skipping view {view_name}: No definition found"
                )

                continue

            # MSSQL cleanup
            if SOURCE_DB["type"] == "mssql":

                definition = re.sub(
                    r'CREATE\s+VIEW\s+.*?\s+AS',
                    '',
                    definition,
                    flags=re.IGNORECASE | re.DOTALL
                )

                definition = definition.replace(
                    "[",
                    '"'
                ).replace(
                    "]",
                    '"'
                )

            # MySQL cleanup
            elif SOURCE_DB["type"] == "mysql":

                definition = re.sub(
                    rf'`{SOURCE_DB["database"]}`\.',
                    '',
                    definition
                )

                definition = definition.replace(
                    "`",
                    '"'
                )

            print("\nVIEW SQL:")
            print(definition)

            query = f'''
            CREATE OR REPLACE VIEW
            "{view_name}" AS
            {definition}
            '''

            try:

                cur.execute(query)

                print(
                    f"Created view: {view_name}"
                )

                self.rollback_statements.insert(
                    0,
                    f'DROP VIEW IF EXISTS "{view_name}" CASCADE;'
                )

            except Exception as e:

                self.pg_conn.rollback()

                print(
                    f"View error {view_name}: {e}"
                )

        self.pg_conn.commit()

        cur.close()

    def generate_rollback_script(self):

        try:

            with open(
                "rollback.sql",
                "w"
            ) as file:

                file.write(
                    "-- Auto Generated Rollback Script\n\n"
                )

                for statement in self.rollback_statements:

                    file.write(
                        statement + "\n"
                    )

            print(
                "Rollback Script Generated: rollback.sql"
            )

            logging.info(
                "Rollback script generated successfully"
            )

        except Exception as e:

            logging.error(
                f"Rollback script generation failed: {e}"
            )

            print(
                f"Rollback script generation failed: {e}"
            )

    def create_check_constraints(self, table):

        constraints = self.source.get_check_constraints(
            table
        )

        cur = self.pg_conn.cursor()

        for constraint in constraints:

            name = constraint[
                "CONSTRAINT_NAME"
            ]

            clause = constraint[
                "CHECK_CLAUSE"
            ]

            if SOURCE_DB["type"] == "mssql":

                clause = clause.replace(
                    "[",
                    ""
                )

                clause = clause.replace(
                    "]",
                    ""
                )


            if clause is None:

                continue

            # MySQL-specific cleanup
            if SOURCE_DB["type"] == "mysql":

                clause = clause.replace(
                    "`",
                    '"'
                )

                clause = clause.replace(
                    "''",
                    "'"
                )

            if SOURCE_DB["type"] == "mssql":

                clause = clause.replace("[", "")
                clause = clause.replace("]", "")

            query = f'''
            ALTER TABLE "{table}"

            ADD CONSTRAINT "{name}"

            CHECK ({clause});
            '''

            try:

                cur.execute(query)

            except Exception as e:

                self.pg_conn.rollback()

                if "already exists" in str(e).lower():

                    print(
                        f"{name} already exists"
                    )

                else:

                    print(
                        f"CHECK ERROR {table}: {e}"
                    )

                    logging.error(
                        f"CHECK ERROR {table}: {e}"
                    )

        self.pg_conn.commit()

        cur.close()

        print(
            f"Check constraints created for {table}"
        )

        logging.info(
            f"Check constraints created for {table}"
        )

    def export_triggers(self):

        try:

            triggers = self.source.get_triggers()

            with open(
                "trigger_report.json",
                "w"
            ) as f:

                json.dump(
                    triggers,
                    f,
                    indent=4,
                    default=str
                )

            print(
                f"Exported {len(triggers)} triggers"
            )

            logging.info(
                f"Exported {len(triggers)} triggers"
            )

        except Exception as e:

            logging.error(
                f"Trigger export failed: {e}"
            )

            print(
                f"Trigger export failed: {e}"
            )

    def create_default_values(self, table):

        defaults = self.source.get_default_values(
            table
        )

        cur = self.pg_conn.cursor()

        for item in defaults:

            column_name = item[
                "COLUMN_NAME"
            ]

            default_value = item[
                "COLUMN_DEFAULT"
            ]

            if default_value is None:

                continue

            default_value = str(
                default_value
            ).strip()

            # CURRENT_TIMESTAMP
            if default_value.upper() == \
                "CURRENT_TIMESTAMP":

                default_sql = \
                    "CURRENT_TIMESTAMP"

            # Numeric defaults
            elif default_value.replace(
                ".", "", 1
            ).isdigit():

                default_sql = default_value

            # Boolean defaults
            elif default_value.upper() in (
                "TRUE",
                "FALSE"
            ):

                default_sql = \
                    default_value.upper()

            # String defaults
            else:

                default_sql = (
                    "'" +
                    default_value.replace(
                        "'",
                        "''"
                    ) +
                    "'"
                )

            query = f'''
            ALTER TABLE "{table}"

            ALTER COLUMN "{column_name}"

            SET DEFAULT {default_sql};
            '''

            try:

                cur.execute(query)

            except Exception as e:

                self.pg_conn.rollback()

                print(
                    f"DEFAULT ERROR {table}: {e}"
                )

                logging.error(
                    f"DEFAULT ERROR {table}: {e}"
                )

        self.pg_conn.commit()

        cur.close()

        print(
            f"Default values created for {table}"
        )

        logging.info(
            f"Default values created for {table}"
        )

    def create_indexes(self, table):

        indexes = self.source.get_indexes(table)

        grouped_indexes = {}

        for idx in indexes:

            index_name = idx["Key_name"]

            if index_name == "PRIMARY":
                continue

            if index_name not in grouped_indexes:

                grouped_indexes[index_name] = {
                    "columns": [],
                    "unique": idx["Non_unique"] == 0
                }

            grouped_indexes[index_name]["columns"].append(
                idx["Column_name"]
            )

        cur = self.pg_conn.cursor()

        for index_name, details in grouped_indexes.items():

            columns = details["columns"]

            unique_clause = ""

            if details["unique"]:

                unique_clause = "UNIQUE"

            column_list = ",".join(
                [f'"{col}"' for col in columns]
            )

            query = f'''
            CREATE {unique_clause} INDEX IF NOT EXISTS
            "{index_name}"
            ON "{table}"
            ({column_list});
            '''
            try:

                cur.execute(query)

            except Exception as e:

                self.pg_conn.rollback()

                print(
                    f"INDEX ERROR {table}: {e}"
                )

                logging.error(
                    f"INDEX ERROR {table}: {e}"
                )

        self.pg_conn.commit()

        cur.close()

        print(
            f"Indexes created for {table}"
        )

        logging.info(
            f"Indexes created for {table}"
        )

    def export_procedures(self):

        procedures = self.source.get_procedures()

        with open(
            "procedure_report.json",
            "w"
        ) as f:

            json.dump(
                procedures,
                f,
                indent=4,
                default=str
            )

        print(
            f"Exported {len(procedures)} procedures"
        )

    def export_procedures(self):

        try:

            procedures = self.source.get_procedures()

            with open(
                "procedure_report.json",
                "w"
            ) as f:

                json.dump(
                    procedures,
                    f,
                    indent=4,
                    default=str
                )

            print(
                f"Exported {len(procedures)} procedures"
            )

            logging.info(
                f"Exported {len(procedures)} procedures"
            )

        except Exception as e:

            logging.error(
                f"Procedure export failed: {e}"
            )

            print(
                f"Procedure export failed: {e}"
            )

    def compare_data(self, table):

        source_cur = self.source.get_connection().cursor()

        pg_cur = self.pg_conn.cursor()

        source_cur.execute(
            f"SELECT * FROM {table}"
        )

        pg_cur.execute(
            f'SELECT * FROM "{table}"'
        )

        source_rows = source_cur.fetchall()

        pg_rows = pg_cur.fetchall()

        source_cur.close()

        pg_cur.close()

        if source_rows == pg_rows:

            print(
                f"{table}: DATA MATCHED"
            )

            logging.info(
                f"{table}: DATA MATCHED"
            )

            return True

        else:

            print(
                f"{table}: DATA MISMATCH"
            )

            logging.warning(
                f"{table}: DATA MISMATCH"
            )

            return False

    def generate_hash(self, rows):

        data = []

        for row in rows:

            values = []

            for value in row:

                if value is None:

                    values.append("NULL")

                else:

                    values.append(
                        str(value)
                    )

            data.append(
                "|".join(values)
            )

        final_data = "\n".join(data)

        return hashlib.sha256(
            final_data.encode("utf-8")
        ).hexdigest()

    def compare_data_hash(self, table):

        source_cur = self.source.get_connection().cursor()

        pg_cur = self.pg_conn.cursor()

        columns = self.source.get_columns(
            table
        )

        pk = columns[0]["Field"]

        source_cur.execute(
            f"""
            SELECT *
            FROM {table}
            ORDER BY {pk}
            """
        )

        pg_cur.execute(
            f'''
            SELECT *
            FROM "{table}"
            ORDER BY "{pk}"
            '''
        )

        source_rows = source_cur.fetchall()

        pg_rows = pg_cur.fetchall()

        source_hash = self.generate_hash(
            source_rows
        )

        pg_hash = self.generate_hash(
            pg_rows
        )   

        source_cur.close()

        pg_cur.close()

        print(f"{table}:")

        print(
            f"Source Hash: {source_hash}"
        )

        print(
            f"PostgreSQL Hash: {pg_hash}"
        )

        logging.info(
            f"{table}: Source Hash={source_hash}"
        )

        logging.info(
            f"{table}: PostgreSQL Hash={pg_hash}"
        )

        return source_hash == pg_hash

    def create_migration_status_table(self):

        cur = self.pg_conn.cursor()

        try:

            cur.execute("""
            CREATE TABLE IF NOT EXISTS migration_status (

                table_name VARCHAR(255)
                PRIMARY KEY,

                status VARCHAR(50),

                rows_migrated BIGINT,

                migrated_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

            )
            """)

            self.pg_conn.commit()

            print(
                "migration_status table created"
            )

            logging.info(
                "migration_status table created"
            )

        except Exception as e:

            self.pg_conn.rollback()

            print(
                f"migration_status table error: {e}"
            )

            logging.error(
                f"migration_status table error: {e}"
            )

            raise

        finally:

            cur.close()

    def save_migration_status(
    self,
    table,
    rows
):

        cur = self.pg_conn.cursor()

        try:

            cur.execute(
                """
                INSERT INTO migration_status
                (
                    table_name,
                    status,
                    rows_migrated
                )
                VALUES
                (%s,'SUCCESS',%s)

                ON CONFLICT(table_name)
                DO UPDATE SET

                status='SUCCESS',

                rows_migrated=
                EXCLUDED.rows_migrated
                """,
                (table, rows)
            )

            self.pg_conn.commit()

            logging.info(
                f"Migration status saved: "
                f"{table} ({rows} rows)"
            )   

        except Exception as e:

            self.pg_conn.rollback()

            logging.error(
                f"Failed to save migration status "
                f"for {table}: {e}"
            )

            print(
                f"Failed to save migration status "
                f"for {table}: {e}"
            )

            raise

        finally:

            cur.close()

    def save_failed_status(
    self,
    table,
    error
):

        cur = self.pg_conn.cursor()

        try:

            cur.execute(
                """
                INSERT INTO migration_status
                (
                    table_name,
                    status,
                    rows_migrated
                )
                VALUES
                (%s,'FAILED',0)

                ON CONFLICT(table_name)
                DO UPDATE SET

                status='FAILED'
                """,
                (table,)
            )

            self.pg_conn.commit()

            logging.error(
                f"Migration failed for "
                f"{table}: {error}"
            )

        except Exception as e:

            self.pg_conn.rollback()

            logging.error(
                f"Failed to save FAILED status "
                f"for {table}: {e}"
            )

            print(
                f"Failed to save FAILED status "
                f"for {table}: {e}"
            )

            raise

        finally:

            cur.close()

    def generate_report(self):

        import json

        report_data = {
            "tables": len(self.source.get_tables()),
            "views": len(self.source.get_views()),
            "procedures": len(
                self.source.get_procedures()
            ),
            "functions": len(
                self.source.get_functions()
            ),
            "status": "Completed"
        }

        with open(
            "migration_report.json",
            "w"
        ) as file:

            json.dump(
                report_data,
                file,
                indent=4
            )

        print(
            "Migration Report Generated: migration_report.json"
        )

    def create_stage_tracking_table(self):

        cur = self.pg_conn.cursor()

        try:

            cur.execute("""
            CREATE TABLE IF NOT EXISTS migration_stages (

                table_name VARCHAR(255)
                PRIMARY KEY,

                table_created BOOLEAN DEFAULT FALSE,

                indexes_created BOOLEAN DEFAULT FALSE,

                constraints_created BOOLEAN DEFAULT FALSE,

                data_migrated BOOLEAN DEFAULT FALSE,

                validated BOOLEAN DEFAULT FALSE,

                updated_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

            )
            """)

            self.pg_conn.commit()

            print(
                "migration_stages table created"
            )

            logging.info(
                "migration_stages table created"
            )

        except Exception as e:

            self.pg_conn.rollback()

            print(
                f"migration_stages table error: {e}"
            )

            logging.error(
                f"migration_stages table error: {e}"
            )

            raise

        finally:

            cur.close()

    def update_stage(
    self,
    table,
    stage
):

        valid_stages = [

            "table_created",

            "indexes_created",

            "constraints_created",

            "data_migrated",

            "validated"

        ]

        if stage not in valid_stages:

            raise ValueError(
                f"Invalid stage: {stage}"
            )

        cur = self.pg_conn.cursor()

        try:

            cur.execute(
                f"""
                INSERT INTO migration_stages
                (
                    table_name,
                    {stage}
                )
                VALUES
                (%s, TRUE)

                ON CONFLICT(table_name)

                DO UPDATE SET

                {stage}=TRUE,

                updated_at=CURRENT_TIMESTAMP
                """,
                (table,)
            )

            self.pg_conn.commit()

            logging.info(
                f"{table}: "
                f"{stage} updated"
            )   

        except Exception as e:

            self.pg_conn.rollback()

            logging.error(
                f"Failed updating "
                f"{stage} for {table}: {e}"
            )

            print(
                f"Failed updating "
                f"{stage} for {table}: {e}"
            )

            raise

        finally:

            cur.close()

    def generate_table_checksum(
    self,
    rows
):

        checksum = hashlib.md5()

        for row in rows:

            checksum.update(
                str(row).encode("utf-8")
            )

        return checksum.hexdigest()
    
    def generate_checksum_report(self):

        checksum_results = []

        tables = self.source.get_tables()

        for table in tables:

            print(
                f"CHECKSUM VALIDATION: {table}"
            )

            source_cur = (
                self.source
                .get_connection()
                .cursor()
            )

            source_cur.execute(
                f"SELECT * FROM {table}"
            )

            source_rows = (
                source_cur.fetchall()
            )

            source_cur.close()

            target_cur = (
                self.pg_conn.cursor()
            )

            target_cur.execute(
                f'SELECT * FROM "{table}"'
            )

            target_rows = (
                target_cur.fetchall()
            )

            target_cur.close()

            source_checksum = (
                self.generate_table_checksum(
                    source_rows
                )
            )

            target_checksum = (
                self.generate_table_checksum(
                    target_rows
                )
            )

            checksum_results.append({

                "table": table,

                "source_checksum":
                    source_checksum,

                "target_checksum":
                    target_checksum,

                "status":
                    "PASS"
                    if (
                        source_checksum
                        ==
                        target_checksum
                    )
                    else "FAIL"

            })

        report_file = os.path.join(
            os.path.dirname(__file__),
            "checksum_report.json"
        )

        with open(
            report_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                checksum_results,
                f,
                indent=4
            )

        print(
            "Checksum Report Generated"
        )

        return checksum_results

    def generate_reconciliation_report(self):

        reconciliation_results = []

        tables = self.source.get_tables()

        for table in tables:

            print(f"RECONCILING: {table}")

            columns = self.source.get_columns(table)

            pk_column = None

            for col in columns:

                if col["Key"] == "PRI":

                    pk_column = col["Field"]

                    break

            if not pk_column:

                continue

            source_cur = (
                self.source.get_connection().cursor()
            )

            source_cur.execute(
                f"SELECT * FROM {table}"
            )

            source_rows = source_cur.fetchall()

            source_cur.close()

            target_cur = self.pg_conn.cursor()

            target_cur.execute(
                f'SELECT * FROM "{table}"'
            )

            target_rows = target_cur.fetchall()

            target_cur.close()

            source_dict = {}

            for row in source_rows:

                source_dict[row[0]] = row

            target_dict = {}

            for row in target_rows:

                target_dict[row[0]] = row

            for pk in source_dict:

                if pk not in target_dict:

                    reconciliation_results.append({

                        "table": table,

                        "primary_key": pk,

                        "issue":
                            "Row Missing In Target"

                    })

                    continue

                source_row = source_dict[pk]

                target_row = target_dict[pk]

                for index in range(
                    len(source_row)
                ):

                    if (
                        str(source_row[index])
                        !=
                        str(target_row[index])
                    ):

                        reconciliation_results.append({

                            "table": table,

                            "primary_key": pk,

                            "column":
                                columns[index]["Field"],

                            "source_value":
                                str(source_row[index]),

                            "target_value":
                                str(target_row[index])

                        })

        report_file = os.path.join(

            os.path.dirname(__file__),

            "reconciliation_report.json"

        )

        if len(reconciliation_results) == 0:

            reconciliation_results = [
                {
                    "status": "PASS",
                    "message":
                    "No reconciliation issues detected"
                }

            ]

        with open(
            report_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                reconciliation_results,
                f,
                indent=4
            )

        print(
            "Reconciliation Report Generated"
        )

        return reconciliation_results

    def generate_schema_mapping_report(self):

        report = []

        tables = self.source.get_tables()

        for table in tables:

            columns = self.source.get_columns(table)

            for col in columns:

                source_type = str(
                    col["Type"]
                ).upper()

                suggestion = source_type

                recommendation = (
                    "No change required"
                )

            # ==========================
            # VARCHAR
            # ==========================

                if "VARCHAR" in source_type:

                    suggestion = source_type

                    recommendation = (
                        "Preserve length constraint"
                    )

            # ==========================
            # TEXT
            # ==========================

                elif source_type == "TEXT":

                    suggestion = "TEXT"

                    recommendation = (
                        "No change required"
                    )

            # ==========================
            # DATETIME
            # ==========================

                elif source_type == "DATETIME":

                    suggestion = "TIMESTAMP"

                    recommendation = (
                        "Convert DATETIME to TIMESTAMP"
                    )

            # ==========================
            # NUMBER (Oracle)
            # ==========================

                elif source_type == "NUMBER":

                    suggestion = "BIGINT"

                    recommendation = (
                        "Convert NUMBER to BIGINT"
                    )

            # ==========================
            # DECIMAL
            # ==========================

                elif "DECIMAL" in source_type:

                    suggestion = source_type

                    recommendation = (
                        "Preserve precision and scale"
                    )

            # ==========================
            # INT
            # ==========================

                elif source_type in [
                    "INT",
                    "INTEGER",
                    "BIGINT",
                    "SMALLINT"
                ]:

                    suggestion = source_type

                    recommendation = (
                        "No change required"
                    )

            # ==========================
            # DATE
            # ==========================

                elif source_type == "DATE":

                    suggestion = "DATE"

                    recommendation = (
                        "No change required"
                    )

            # ==========================
            # BOOLEAN
            # ==========================

                elif source_type in [
                    "BIT",
                    "BOOLEAN"
                ]:

                    suggestion = "BOOLEAN"

                    recommendation = (
                        "Convert to PostgreSQL BOOLEAN"
                    )

            # ==========================
            # UNKNOWN TYPES
            # ==========================

                else:

                    recommendation = (
                        "Manual review recommended"
                    )

                report.append({

                    "table": table,

                    "column": col["Field"],

                    "source_type": source_type,

                    "suggested_type": suggestion,

                    "recommendation": recommendation,

                    "is_primary_key":
                        col["Key"] == "PRI"

                })

        fk_suggestions = (
            self.detect_foreign_keys()
        )

        rename_suggestions = (
            self.detect_column_renames()
        )

        risk_analysis = (
            self.generate_risk_analysis(
                report,
                fk_suggestions,
                rename_suggestions
            )
        )

        ai_summary = (
            self.generate_ai_summary(
                len(fk_suggestions),
                len(rename_suggestions),
                risk_analysis["overall_risk"]
            )
        )

        import os

        report_file =os.path.join(
                os.path.dirname(__file__),
                "backend",
                "schema_mapping_report.json"
            )

        print("\n================================")
        print("REPORT FILE:", report_file)
        print("================================\n")
        print("AI SUMMARY:", ai_summary)

        with open(
            report_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                {
                    "schema_mapping": report,

                    "foreign_keys": fk_suggestions,

                    "rename_suggestions": rename_suggestions,
                    
                    "risk_analysis": risk_analysis,

                    "ai_summary": ai_summary

                },
                f,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"Generated AI schema mapping report with "
            f"{len(report)} recommendations"
        )

    def generate_metrics_report(
    self,
    start_time,
    end_time,
    total_rows,
    total_tables,
    failed_tables
):

        duration = (
            end_time - start_time
        ).total_seconds()

        total_rows = int(total_rows)

        metrics = {

            "migration_duration_seconds":
                duration,

            "rows_migrated":
                total_rows,

            "tables_processed":
                total_tables,

            "failed_tables":
                failed_tables,

            "rows_per_second":

                round(
                    total_rows / duration,
                    2
                )

                if duration > 0
                else 0

        }

        with open(
            "metrics_report.json",
            "w"
        ) as f:

            json.dump(
                metrics,
                f,
                indent=4
            )

        print(
            "Metrics Report Generated"
        )

        return metrics

    def detect_column_renames(self):

        suggestions = []

        rename_rules = {

            "cust": "customer",

            "prod": "product",

            "qty": "quantity",

            "addr": "address",

            "dob": "date_of_birth"

        }

        tables = self.source.get_tables()

        for table in tables:

            columns = self.source.get_columns(table)

            for col in columns:

                column_name = (
                    col["Field"]
                    .lower()
                )

                for short, full in (
                    rename_rules.items()
                ):

                    if (
                        column_name == short
                        or
                        column_name.startswith(
                            short + "_"
                        )
                    ):

                        suggested = (
                            column_name
                            .replace(
                                short,
                                full,
                                1
                            )
                        )

                        suggestions.append({

                            "table": table,

                            "column": col["Field"],

                            "suggested_name":
                                suggested

                        })

        return suggestions

    def detect_foreign_keys(self):

        suggestions = []

        tables = self.source.get_tables()

        table_columns = {}

        for table in tables:

            columns = self.source.get_columns(table)

            table_columns[table] = [

                col["Field"]

                for col in columns

            ]

        for table in tables:

            columns = table_columns[table]

            for column in columns:

                if column.lower().endswith("_id"):

                    base_name = (
                        column.lower()[:-3]
                    )

                    for other_table in tables:

                        if other_table == table:
                            continue

                        if (
                            other_table.lower().rstrip("s")
                            == base_name
                        ):  

                            print(
                                f"MATCH FOUND: "
                                f"{table}.{column}"
                            )

                            suggestions.append({

                                "table": table,

                                "column": column,

                                "suggestion":
                                f"Likely Foreign Key -> "
                                f"{other_table}.{column}"

                            })

        return suggestions

    def create_history_table(self):

        cursor = self.pg_conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migration_history (

                id SERIAL PRIMARY KEY,

                source_db VARCHAR(100),

                target_db VARCHAR(100),

                tables_count INTEGER,

                rows_count INTEGER,

                status VARCHAR(50),

                migration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )
        """)

        self.pg_conn.commit()

        cursor.close()

    print("migration_history table created")

    def reset_table(self, table_name):

        cursor = self.pg_conn.cursor()

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

        self.pg_conn.commit()

        cursor.close()

        print(f"{table_name} reset successfully")

    def get_completed_tables(self):

        cur = self.pg_conn.cursor()

        try:

            cur.execute("""
            SELECT table_name
            FROM migration_status
            WHERE status='SUCCESS'
            """)

            completed_tables = [
                row[0]
                for row in cur.fetchall()
            ]

            logging.info(
                f"Found "
                f"{len(completed_tables)} "
                f"completed tables"
            )

            return completed_tables

        except Exception as e:

            logging.error(
                f"Failed to fetch "
                f"completed tables: {e}"
            )

            print(
                f"Failed to fetch "
                f"completed tables: {e}"
            )

            return []

        finally:

            cur.close()

    def export_functions(self):

        try:

            functions = self.source.get_functions()

            with open(
                "function_report.json",
                "w"
            ) as f:

                json.dump(
                    functions,
                    f,
                    indent=4,
                    default=str
                )

            print(
                f"Exported {len(functions)} functions"
            )

        except Exception as e:

            print(
                f"Function export failed: {e}"
            )

    def save_history(
    self,
    tables_count,
    rows_count,
    status
):

        cursor = self.pg_conn.cursor()

        cursor.execute(

            """

            INSERT INTO migration_history(

                source_db,
                target_db,
                tables_count,
                rows_count,
                status

            )

            VALUES (%s,%s,%s,%s,%s)

            """,

            (

                SOURCE_DB["type"],
                "postgresql",
                tables_count,
                rows_count,
                status

            )

        )

        self.pg_conn.commit()

        cursor.close()

    def create_unique_constraints(self, table):

        constraints = self.source.get_unique_constraints(
            table
        )

        grouped = {}

        for item in constraints:

            constraint_name = item[
                "CONSTRAINT_NAME"
            ]

            column_name = item[
                "COLUMN_NAME"
            ]

            if constraint_name not in grouped:

                grouped[
                    constraint_name
                ] = []

            grouped[
                constraint_name
            ].append(column_name)

        cur = self.pg_conn.cursor()

        try:

            for constraint_name, columns in grouped.items():

                cols = ",".join(
                    [f'"{c}"' for c in columns]
                )

                query = f'''
                ALTER TABLE "{table}"

                ADD CONSTRAINT "{constraint_name}"

                UNIQUE ({cols});
                '''

                try:

                    cur.execute(query)

                except Exception as e:

                    self.pg_conn.rollback()

                    if "already exists" in str(e).lower():

                        print(
                            f"{constraint_name} already exists"
                        )

                    else:

                        logging.error(
                            f"UNIQUE CONSTRAINT ERROR "
                            f"{table}: {e}"
                        )

                        print(
                            f"UNIQUE CONSTRAINT ERROR "
                            f"{table}: {e}"
                        )

            self.pg_conn.commit()

            print(
                f"Unique constraints created for {table}"
            )

            logging.info(
                f"Unique constraints created for {table}"
            )

        except Exception as e:

            self.pg_conn.rollback()

            logging.error(
                f"Failed creating unique constraints "
                f"for {table}: {e}"
            )

            raise

        finally:

            cur.close()

    def get_total_rows_migrated(self):

        cursor = self.pg_conn.cursor()

        cursor.execute("""

            SELECT COALESCE(
                SUM(rows_migrated),
                0
            )

            FROM migration_status

            WHERE status = 'SUCCESS'

        """)

        total_rows = cursor.fetchone()[0]

        cursor.close()

        return total_rows

    def get_stage_status(self, table):

        cur = self.pg_conn.cursor()

        try:

            cur.execute(
                """
                SELECT
                    table_created,
                    indexes_created,
                    constraints_created,
                    data_migrated,
                    validated
                FROM migration_stages
                WHERE table_name=%s
                """,
                (table,)
            )

            result = cur.fetchone()

            if result:

                logging.info(
                    f"Stage status fetched "
                    f"for {table}"
                )

            else:

                logging.info(
                    f"No stage status found "
                    f"for {table}"
                )

            return result

        except Exception as e:

            logging.error(
                f"Failed fetching stage status "
                f"for {table}: {e}"
            )

            print(
                f"Failed fetching stage status "
                f"for {table}: {e}"
            )

            return None

        finally:

            cur.close()

    def validate_migration(self):

        print("RUNNING VALIDATION...")
        
        print("SOURCE OBJECT:", self.source)

        validation_results = []

        tables = self.source.get_tables()

        for table in tables:

            print("VALIDATING:", table)

            print("ADAPTER TYPE:", type(self.source))
            
            print("GET_ROW_COUNT FROM:", self.source.get_row_count.__qualname__)

            source_count = self.source.get_row_count(table)

            cur = self.pg_conn.cursor()

            cur.execute(
                f"SELECT COUNT(*) FROM {table}"
            )

            target_count = cur.fetchone()[0]

            cur.close()

            validation_results.append({

                "table": table,

                "source_rows": source_count,

                "target_rows": target_count,

                "status":
                    "PASSED"
                    if source_count == target_count
                    else "FAILED"

            })

        overall_status = (

            "PASSED"

            if all(
                r["status"] == "PASSED"
                for r in validation_results
            )

            else "FAILED"

        )

        report_file = os.path.join(
            os.path.dirname(__file__),
            "validation_report.json"
        )

        with open(
            report_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                {
                    "tables": validation_results,
                    "overall_status": overall_status
                },
                f,
                indent=4
            )

        return overall_status

    def generate_audit_report(self):

        audit_results = []

        tables = self.source.get_tables()

        for table in tables:

            source_count = self.source.get_row_count(table)

            cur = self.pg_conn.cursor()

            cur.execute(
                f"SELECT COUNT(*) FROM {table}"
            )

            target_count = cur.fetchone()[0]

            cur.close()

            audit_results.append({

                "table": table,

                "source_rows": source_count,

                "target_rows": target_count,

                "difference": (
                    source_count - target_count
                ),

                "audit_status":
                    "PASS"
                    if source_count == target_count
                    else "FAIL"
            })

        report_file = os.path.join(
            os.path.dirname(__file__),
            "audit_report.json"
        )

        with open(
            report_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                audit_results,
                f,
                indent=4
            )

        print(
            "Audit Report Generated"
        )

        return audit_results

    def save_audit_trail(

        self,

        start_time,

        end_time,

        total_rows,

        total_tables,

        validation_status,

        audit_status,

        checksum_status,

        reconciliation_status

    ):

        try:

            # print("SAVE_AUDIT_TRAIL EXECUTED")

            cursor = self.pg_conn.cursor()

            # print("INSERTING AUDIT RECORD")

            cursor.execute(

                """
                INSERT INTO migration_audit_trail (

                    started_at,
                    completed_at,
                    source_db,
                    target_db,
                    tables_processed,
                    rows_processed,
                    validation_status,
                    audit_status,
                    checksum_status,
                    reconciliation_status,
                    rollback_generated,
                    report_generated

                )

                VALUES (

                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s

                )
                """,    

                (

                    start_time,
                    end_time,
                    SOURCE_DB["type"],
                    "postgresql",
                    total_tables,
                    int(total_rows),
                    validation_status,
                    audit_status,
                    checksum_status,
                    reconciliation_status,
                    True,
                    True

                )

            )

            self.pg_conn.commit()

            # print("AUDIT RECORD COMMITTED")

            cursor.close()

            print("Audit Trail Saved")

        except Exception as e:

            print("AUDIT ERROR:", e)

    def generate_ai_summary(
    self,
    fk_count,
    rename_count,
    risk_level
):

        summary = []

        summary.append(
            f"{fk_count} foreign keys detected"
        )

        summary.append(
            f"{rename_count} rename recommendations"
        )

        if risk_level == "LOW":

            recommendation = (
                "Schema is safe for migration."
            )

        elif risk_level == "MEDIUM":

            recommendation = (
                "Migration can proceed with review."
            )

        else:

            recommendation = (
                "Manual review recommended."
            )

        return {

            "summary": summary,

            "recommendation":
            recommendation

        }

    def run(self):
        from datetime import datetime
        start_time = datetime.now()
        self.create_history_table()
        self.update_progress(
            0,
            "",
            "RUNNING"
        )
        self.generate_schema_mapping_report()
        self.create_migration_status_table()
        self.create_stage_tracking_table()
        tables = self.source.get_tables()
        
        completed_tables = (
            self.get_completed_tables()
        )
        print(f"\nFound {len(tables)} tables\n")

    # ====================================
    # STEP 1: CREATE ALL TABLES
    # ====================================

        print("\nCreating tables...\n")

        for table in tables:

            try:

                stage = self.get_stage_status(
                    table
                )

                if stage and stage[0]:

                    print(
                        f"Skipping table creation for {table}"
                    )

                    continue

                self.create_table(table)

                self.update_stage(
                    table,
                    "table_created"
                )

            except Exception as e:

                self.pg_conn.rollback()

                logging.error(
                    f"Error creating table {table}: {str(e)}"
                )

                print(
                    f"Error creating table {table}: {e}"
                )

    # ====================================
    # STEP 2: CREATE INDEXES
    # ====================================

        print("\nCreating indexes...\n")

        for table in tables:

            try:

                stage = self.get_stage_status(
                    table
                )

                if stage and stage[1]:

                    print(
                        f"Skipping indexes for {table}"
                    )

                    continue

                self.create_indexes(table)

                self.update_stage(
                    table,
                    "indexes_created"
                )

            except Exception as e:

                self.pg_conn.rollback()

                logging.error(
                    f"Error creating indexes for {table}: {str(e)}"
                )

                print(
                    f"Error creating indexes for {table}: {e}"
                )

    # ====================================
    # STEP 3: CREATE UNIQUE CONSTRAINTS
    # ====================================

        print("\nCreating unique constraints...\n")

        for table in tables:

            try:

                stage = self.get_stage_status(
                    table
                )

                if stage and stage[2]:

                    print(
                        f"Skipping constraints for {table}"
                    )

                    continue

                self.create_unique_constraints(
                    table
                )

                self.update_stage(
                    table,
                    "constraints_created"
                )
            except Exception as e:

                self.pg_conn.rollback()

                print(
                    f"Error creating constraints for {table}: {e}"
                )

        print("\nCreating check constraints...\n")

        for table in tables:

            try:

                self.create_check_constraints(
                    table
                )

            except Exception as e:

                self.pg_conn.rollback()

                print(
                    f"Check constraint error in {table}: {e}"
                )
    # ====================================
    # STEP 4: CREATE VIEWS
    # ====================================

        print("\nCreating views...\n")

        try:    

            self.create_views()

        except Exception as e:

            self.pg_conn.rollback()

            logging.error(
                f"View creation error: {str(e)}"
            )

            print(
                f"View creation error: {e}"
            )
    # ====================================
    # STEP 5: MIGRATE DATA
    # ====================================

        print("\nMigrating data...\n")

        for table in tables:

            stage = self.get_stage_status(
                table
            )

            if stage and stage[3]:

                print(
                    f"Skipping data migration for {table}"
                )

                continue

            if table in completed_tables:

                print(
                    f"Skipping {table}"
                )

                continue

            try:
                progress = int(
                    (
                        tables.index(table) + 1
                    )
                    /
                    len(tables)
                    * 100
                )

                self.update_progress(
                    progress,table,"RUNNING"
                )
                
                migrated_rows = self.migrate_data(table)
                self.update_stage(
                    table,
                    "data_migrated"
                )
                valid = self.validate(table)

                if valid:

                    self.save_migration_status(
                    table,
                    migrated_rows
                    )
                    self.update_stage(
                        table,
                        "validated"
                    )
                    print(
                        f"{table} validated\n"
                    )   

                else:

                    self.save_failed_status(
                    table,
                    "Validation Failed"
                )

                    print(
                        f"{table} validation failed\n"
                    )

                status = (
                    "SUCCESS"
                    if valid
                        else "FAILED"
                )

                self.report.append({
                    "table": table,
                    "rows_migrated": migrated_rows,
                    "status": status
                })

            except Exception as e:

                self.pg_conn.rollback()

                self.save_failed_status(
                    table,
                    str(e)
                )

                logging.error(
                    f"Error in {table}: {str(e)}"
                )

                self.report.append({
                    "table": table,
                    "rows_migrated": 0,
                    "status": "ERROR",
                    "error": str(e)
                })  

                print(
                    f"Error in {table}: {e}"
                )

    # ====================================
    # STEP : CREATE DEFAULT VALUES
    # ====================================

        print(
            "\nCreating default values...\n"
        )

        for table in tables:

            try:

                self.create_default_values(
                    table
                )

            except Exception as e:

                self.pg_conn.rollback()

                print(
                    f"Default value error in {table}: {e}"
                )

    # ====================================
    # GENERATE REPORT
    # ====================================
        self.export_triggers()
        self.export_procedures()
        self.export_functions()
        self.generate_rollback_script()
        self.generate_report()
        

        try:
            validation_status = self.validate_migration()
        except Exception as e:
            print("VALIDATION ERROR:", e)
            logging.error(f"Validation failed: {e}")
            validation_status = "FAILED"

        audit_results = (
            self.generate_audit_report()
        )

        checksum_results = (
            self.generate_checksum_report()
        )

        reconciliation_results = (
            self.generate_reconciliation_report()
        )

        
        end_time = datetime.now()

        total_rows = self.get_total_rows_migrated()

        failed_tables = len(

            [

                r

                for r in audit_results

                if r["audit_status"] == "FAIL"

            ]

        )

        self.generate_metrics_report(

            start_time,

            end_time,

            total_rows,

            len(tables),

            failed_tables

        )

        self.source.close()

        self.update_progress(
            100,
            "",
            "COMPLETED"
            if validation_status == "PASSED"
            else "VALIDATION_FAILED"
        )

        self.save_audit_trail(

            start_time,

            end_time,

            total_rows,

            len(tables),        

            validation_status,

            "PASS",

            "PASS",

            "PASS"

        )

        print("PG CONNECTION STATUS:", self.pg_conn.closed)
        
        self.save_history(

            len(tables),

            total_rows,

            "SUCCESS"

        )
        print("SAVE HISTORY COMPLETED")
        print("\nMigration Completed")

        logging.info(
            "Migration Completed"
        )
        
        self.pg_conn.close()
if __name__ == "__main__":

    MigrationTool().run()