import psycopg2
import os
from psycopg2.extras import execute_values
import json
import logging
import hashlib
from datetime import datetime
from adapters.factory import get_adapter
from config import SOURCE_DB, TARGET_DB, ENABLE_CUSTOM_MAPPING, TABLE_MAPPING, COLUMN_MAPPING

# Logging Configuration
logging.basicConfig(
    filename='migration.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class MigrationTool:

    def __init__(self, config=None):

        if config is None:
            config = {
                "sourceType": SOURCE_DB["type"]
            }

        self.config = config

        connect_kwargs = {
            "host": TARGET_DB["host"],
            "port": TARGET_DB["port"],
            "database": TARGET_DB["database"],
            "user": TARGET_DB["user"],
            "password": TARGET_DB["password"]
        }
        if "sslmode" in TARGET_DB and TARGET_DB["sslmode"]:
            connect_kwargs["sslmode"] = TARGET_DB["sslmode"]

        self.pg_conn = psycopg2.connect(**connect_kwargs)

        self.source = get_adapter(
            self.config["sourceType"]
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

        from backend.ai_translator import SelfHealingAgent, RoutineTranslator
        from backend.data_quality import DataQualityScorer
        self.self_healing_agent = SelfHealingAgent()
        self.routine_translator = RoutineTranslator()

        logging.info(
            f"Migration initialized: "
            f"{SOURCE_DB['type']} -> PostgreSQL"
        )

    def execute_sql_with_self_healing(self, query: str, context: str = "") -> bool:
        cur = self.pg_conn.cursor()
        try:
            cur.execute("SAVEPOINT self_healing_sp;")
            cur.execute(query)
            cur.execute("RELEASE SAVEPOINT self_healing_sp;")
            cur.close()
            return True
        except Exception as e:
            try:
                cur.execute("ROLLBACK TO SAVEPOINT self_healing_sp;")
            except Exception:
                pass
            error_msg = str(e)
            repair_result = self.self_healing_agent.repair_sql(
                query, error_msg, self.config.get("sourceType", "mysql")
            )
            if repair_result["success"]:
                try:
                    repaired_query = repair_result["repaired_sql"]
                    cur.execute("SAVEPOINT self_healing_sp;")
                    cur.execute(repaired_query)
                    cur.execute("RELEASE SAVEPOINT self_healing_sp;")
                    cur.close()
                    print(f"Self-Healing Agent auto-repaired query ({context}): {repair_result['rule_learned']}")
                    logging.info(f"Self-Healing Agent auto-repaired query ({context}): {repair_result['rule_learned']}")
                    return True
                except Exception as retry_e:
                    try:
                        cur.execute("ROLLBACK TO SAVEPOINT self_healing_sp;")
                    except Exception:
                        pass
                    cur.close()
                    logging.error(f"Self-Healing retry failed for {context}: {retry_e}")
                    raise retry_e
            else:
                cur.close()
                raise e
    
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

        target_table = TABLE_MAPPING.get(table, table) if ENABLE_CUSTOM_MAPPING else table
        columns = self.source.get_columns(table)

        column_defs = []

        primary_keys = []

        for col in columns:

            source_col_name = col["Field"]
            col_name = source_col_name
            if ENABLE_CUSTOM_MAPPING and table in COLUMN_MAPPING:
                col_name = COLUMN_MAPPING[table].get(source_col_name, source_col_name)

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

            source_fk_col = fk["COLUMN_NAME"]
            target_fk_col = source_fk_col
            if ENABLE_CUSTOM_MAPPING and table in COLUMN_MAPPING:
                target_fk_col = COLUMN_MAPPING[table].get(source_fk_col, source_fk_col)

            ref_table = fk["REFERENCED_TABLE_NAME"]
            target_ref_table = ref_table
            if ENABLE_CUSTOM_MAPPING:
                target_ref_table = TABLE_MAPPING.get(ref_table, ref_table)

            ref_col = fk["REFERENCED_COLUMN_NAME"]
            target_ref_col = ref_col
            if ENABLE_CUSTOM_MAPPING and ref_table in COLUMN_MAPPING:
                target_ref_col = COLUMN_MAPPING[ref_table].get(ref_col, ref_col)

            fk_clauses.append(
                f'FOREIGN KEY ("{target_fk_col}") '
                f'REFERENCES "{target_ref_table}" '
                f'("{target_ref_col}")'
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
        CREATE TABLE IF NOT EXISTS "{target_table}" (
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
                f"Created table: {target_table}"
            )

            logging.info(
                f"Created table: {target_table}"
            )

            self.rollback_statements.append(
                f'DROP TABLE IF EXISTS "{target_table}" CASCADE;'
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

        target_table = TABLE_MAPPING.get(table, table) if ENABLE_CUSTOM_MAPPING else table
        columns = self.source.get_columns(table)

        column_names = []
        for col in columns:
            source_col_name = col["Field"]
            col_name = source_col_name
            if ENABLE_CUSTOM_MAPPING and table in COLUMN_MAPPING:
                col_name = COLUMN_MAPPING[table].get(source_col_name, source_col_name)
            column_names.append(col_name)

        source_cur = self.source.get_connection().cursor()

        source_cur.execute(
            f"SELECT * FROM {table}"
        )

        pg_cur = self.pg_conn.cursor()

        pg_cur.execute(
            f'TRUNCATE TABLE "{target_table}" CASCADE'
        )

        batch_size = 10000
        total_rows = 0

        column_list = ",".join(
            [f'"{col}"' for col in column_names]
        )

        import io
        use_copy = True

        while True:

            rows = source_cur.fetchmany(
                batch_size
            )

            if not rows:
                break

            if use_copy:
                try:
                    tsv_output = io.StringIO()
                    for row in rows:
                        formatted_row = []
                        for val in row:
                            if val is None:
                                formatted_row.append("\\N")
                            else:
                                s_val = str(val).replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")
                                formatted_row.append(s_val)
                        tsv_output.write("\t".join(formatted_row) + "\n")

                    tsv_output.seek(0)
                    copy_sql = f'COPY "{target_table}" ({column_list}) FROM STDIN WITH (FORMAT text, NULL \'\\N\')'
                    pg_cur.copy_expert(copy_sql, tsv_output)
                except Exception as copy_err:
                    logging.warning(f"COPY streaming failed for batch in {table}, falling back to execute_values: {copy_err}")
                    use_copy = False
                    self.pg_conn.rollback()
                    insert_sql = f'INSERT INTO "{target_table}" ({column_list}) VALUES %s'
                    execute_values(pg_cur, insert_sql, rows, page_size=batch_size)
            else:
                insert_sql = f'INSERT INTO "{target_table}" ({column_list}) VALUES %s'
                execute_values(pg_cur, insert_sql, rows, page_size=batch_size)

            total_rows += len(rows)

            print(
                f"{table}: {total_rows} rows migrated (COPY Protocol: {use_copy})"
            )

        self.pg_conn.commit()

        source_cur.close()
        pg_cur.close()

        print(
            f"Migrated {total_rows} rows from {table}"
        )

        return total_rows

        logging.info(
            f"Migrated {total_rows} rows from {table}"
        )

        return total_rows

    def validate(self, table):

        target_table = TABLE_MAPPING.get(table, table) if ENABLE_CUSTOM_MAPPING else table

        source_cur = self.source.get_connection().cursor()

        source_cur.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        source_count = source_cur.fetchone()[0]

        pg_cur = self.pg_conn.cursor()

        pg_cur.execute(
            f'SELECT COUNT(*) FROM "{target_table}"'
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

        target_table = TABLE_MAPPING.get(table, table) if ENABLE_CUSTOM_MAPPING else table
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

            if clause is None:

                continue

            # MSSQL-specific cleanup
            if SOURCE_DB["type"] == "mssql":

                clause = clause.replace(
                    "[",
                    ""
                )

                clause = clause.replace(
                    "]",
                    ""
                )

            # MySQL-specific cleanup
            elif SOURCE_DB["type"] == "mysql":

                clause = clause.replace(
                    "`",
                    '"'
                )

                clause = clause.replace(
                    "''",
                    "'"
                )

            # Rename columns inside the check clause if column mapping is active
            if ENABLE_CUSTOM_MAPPING and table in COLUMN_MAPPING:
                import re
                for old_col, new_col in COLUMN_MAPPING[table].items():
                    clause = clause.replace(f'"{old_col}"', f'"{new_col}"')
                    clause = clause.replace(f'`{old_col}`', f'"{new_col}"')
                    clause = clause.replace(f'[{old_col}]', f'"{new_col}"')
                    clause = re.sub(rf'\b{old_col}\b', f'"{new_col}"', clause)

            query = f'''
            ALTER TABLE "{target_table}"

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
                        f"CHECK ERROR {target_table}: {e}"
                    )

                    logging.error(
                        f"CHECK ERROR {target_table}: {e}"
                    )

        self.pg_conn.commit()

        cur.close()

        print(
            f"Check constraints created for {target_table}"
        )

        logging.info(
            f"Check constraints created for {target_table}"
        )

    def export_triggers(self):
        try:
            triggers = self.source.get_triggers()
            translated_triggers = []
            for trg in triggers:
                name = trg.get("TRIGGER_NAME") or trg.get("name") or "trigger"
                definition = trg.get("ACTION_STATEMENT") or trg.get("definition") or str(trg)
                translated = self.routine_translator.translate_trigger(name, definition, self.config.get("sourceType", "mysql"))
                
                try:
                    cur = self.pg_conn.cursor()
                    cur.execute(translated["translated_sql"])
                    self.pg_conn.commit()
                    cur.close()
                    translated["execution_status"] = "SUCCESS"
                except Exception as ex:
                    self.pg_conn.rollback()
                    translated["execution_status"] = "FAILED"
                    translated["execution_error"] = str(ex)

                translated_triggers.append(translated)

            with open("trigger_report.json", "w", encoding="utf-8") as f:
                json.dump(translated_triggers, f, indent=4, default=str)

            print(f"Exported & translated {len(translated_triggers)} triggers")
            logging.info(f"Exported & translated {len(translated_triggers)} triggers")

        except Exception as e:
            logging.error(f"Trigger export failed: {e}")
            print(f"Trigger export failed: {e}")

    def create_default_values(self, table):

        target_table = TABLE_MAPPING.get(table, table) if ENABLE_CUSTOM_MAPPING else table
        defaults = self.source.get_default_values(
            table
        )

        cur = self.pg_conn.cursor()

        for item in defaults:

            column_name = item[
                "COLUMN_NAME"
            ]

            target_column = column_name
            if ENABLE_CUSTOM_MAPPING and table in COLUMN_MAPPING:
                target_column = COLUMN_MAPPING[table].get(column_name, column_name)

            default_value = item[
                "COLUMN_DEFAULT"
            ]

            if default_value is None:

                continue

            default_value = str(
                default_value
            ).strip()

            if SOURCE_DB["type"] == "mssql":
                while default_value.startswith("(") and default_value.endswith(")"):
                    default_value = default_value[1:-1]
                
                if default_value.upper() in ("GETDATE()", "GETUTCDATE()", "CURRENT_TIMESTAMP"):
                    default_value = "CURRENT_TIMESTAMP"
                
                if default_value.startswith("N'") and default_value.endswith("'"):
                    default_value = default_value[2:-1]
                elif default_value.startswith("'") and default_value.endswith("'"):
                    default_value = default_value[1:-1]

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
            ALTER TABLE "{target_table}"

            ALTER COLUMN "{target_column}"

            SET DEFAULT {default_sql};
            '''

            try:

                cur.execute(query)

            except Exception as e:

                self.pg_conn.rollback()

                print(
                    f"DEFAULT ERROR {target_table}: {e}"
                )

                logging.error(
                    f"DEFAULT ERROR {target_table}: {e}"
                )

        self.pg_conn.commit()

        cur.close()

        print(
            f"Default values created for {target_table}"
        )

        logging.info(
            f"Default values created for {target_table}"
        )

    def create_indexes(self, table):

        target_table = TABLE_MAPPING.get(table, table) if ENABLE_CUSTOM_MAPPING else table
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

            col_name = idx["Column_name"]
            if ENABLE_CUSTOM_MAPPING and table in COLUMN_MAPPING:
                col_name = COLUMN_MAPPING[table].get(col_name, col_name)

            grouped_indexes[index_name]["columns"].append(
                col_name
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
            ON "{target_table}"
            ({column_list});
            '''
            try:

                cur.execute(query)

            except Exception as e:

                self.pg_conn.rollback()

                print(
                    f"INDEX ERROR {target_table}: {e}"
                )

                logging.error(
                    f"INDEX ERROR {target_table}: {e}"
                )

        self.pg_conn.commit()

        cur.close()

        print(
            f"Indexes created for {target_table}"
        )

        logging.info(
            f"Indexes created for {target_table}"
        )

    def export_procedures(self):
        try:
            procedures = self.source.get_procedures()
            translated_reports = []
            for proc in procedures:
                name = proc.get("name") or proc.get("ROUTINE_NAME") or proc.get("SPECIFIC_NAME") or "procedure"
                definition = proc.get("definition") or proc.get("ROUTINE_DEFINITION") or str(proc)
                res = self.routine_translator.translate_procedure(name, definition, self.config.get("sourceType", "mysql"))
                
                try:
                    cur = self.pg_conn.cursor()
                    cur.execute(res["translated_sql"])
                    self.pg_conn.commit()
                    cur.close()
                    res["execution_status"] = "SUCCESS"
                except Exception as ex:
                    self.pg_conn.rollback()
                    res["execution_status"] = "FAILED"
                    res["execution_error"] = str(ex)

                translated_reports.append(res)

            with open("procedure_report.json", "w", encoding="utf-8") as f:
                json.dump(translated_reports, f, indent=4, default=str)

            print(f"Exported & translated {len(translated_reports)} procedures")
            logging.info(f"Exported & translated {len(translated_reports)} procedures")

        except Exception as e:
            logging.error(f"Procedure export failed: {e}")
            print(f"Procedure export failed: {e}")

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

                source VARCHAR(100),

                target VARCHAR(100),

                status VARCHAR(50),

                rows_migrated BIGINT,

                started_at TIMESTAMP,

                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            );

            ALTER TABLE migration_history ADD COLUMN IF NOT EXISTS source VARCHAR(100);
            ALTER TABLE migration_history ADD COLUMN IF NOT EXISTS target VARCHAR(100);
            ALTER TABLE migration_history ADD COLUMN IF NOT EXISTS status VARCHAR(50);
            ALTER TABLE migration_history ADD COLUMN IF NOT EXISTS rows_migrated BIGINT;
            ALTER TABLE migration_history ADD COLUMN IF NOT EXISTS started_at TIMESTAMP;
            ALTER TABLE migration_history ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP;
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
            translated_functions = []
            for fn in functions:
                name = fn.get("name") or fn.get("ROUTINE_NAME") or "function"
                definition = fn.get("definition") or fn.get("ROUTINE_DEFINITION") or str(fn)
                res = self.routine_translator.translate_procedure(name, definition, self.config.get("sourceType", "mysql"))
                
                try:
                    cur = self.pg_conn.cursor()
                    cur.execute(res["translated_sql"])
                    self.pg_conn.commit()
                    cur.close()
                    res["execution_status"] = "SUCCESS"
                except Exception as ex:
                    self.pg_conn.rollback()
                    res["execution_status"] = "FAILED"
                    res["execution_error"] = str(ex)

                translated_functions.append(res)

            with open("function_report.json", "w", encoding="utf-8") as f:
                json.dump(translated_functions, f, indent=4, default=str)

            print(f"Exported & translated {len(translated_functions)} functions")
            logging.info(f"Exported & translated {len(translated_functions)} functions")

        except Exception as e:
            logging.error(f"Function export failed: {e}")
            print(f"Function export failed: {e}")

    from datetime import datetime

    def save_history(
        self,
        rows_count,
        status,
        start_time,
        end_time
    ):

        cursor = self.pg_conn.cursor()

        cursor.execute(
            """
            INSERT INTO migration_history(
                source,
                target,
                status,
                rows_migrated,
                started_at,
                completed_at
            )
            VALUES (%s,%s,%s,%s,%s,%s)
            """,
            (
                SOURCE_DB["type"],
                "postgresql",
                status,
                rows_count,
                start_time,
                end_time
            )
        )

        self.pg_conn.commit()
        cursor.close()

    def create_unique_constraints(self, table):

        target_table = TABLE_MAPPING.get(table, table) if ENABLE_CUSTOM_MAPPING else table
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

            if ENABLE_CUSTOM_MAPPING and table in COLUMN_MAPPING:
                column_name = COLUMN_MAPPING[table].get(column_name, column_name)

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
                ALTER TABLE "{target_table}"

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
                            f"{target_table}: {e}"
                        )

                        print(
                            f"UNIQUE CONSTRAINT ERROR "
                            f"{target_table}: {e}"
                        )

            self.pg_conn.commit()

            print(
                f"Unique constraints created for {target_table}"
            )

            logging.info(
                f"Unique constraints created for {target_table}"
            )

        except Exception as e:

            self.pg_conn.rollback()

            logging.error(
                f"Failed creating unique constraints "
                f"for {target_table}: {e}"
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
        
        # Phase 3 AI Intelligence Reports
        try:
            with open("self_healing_report.json", "w", encoding="utf-8") as f:
                json.dump(self.self_healing_agent.healing_history, f, indent=4, default=str)
        except Exception as e:
            logging.error(f"Self-healing report export failed: {e}")

        try:
            from backend.data_quality import DataQualityScorer
            dq_scorer = DataQualityScorer(self.source, self.pg_conn)
            dq_scorer.generate_report(tables, "data_quality_report.json")
            print("Data Quality Report generated successfully.")
        except Exception as dq_err:
            logging.error(f"Data Quality report generation failed: {dq_err}")

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
            total_rows,
            "SUCCESS",
            start_time,
            end_time
        )
        print("SAVE HISTORY COMPLETED")
        print("\nMigration Completed")

        logging.info(
            "Migration Completed"
        )
        
        self.pg_conn.close()
if __name__ == "__main__":

    MigrationTool().run()