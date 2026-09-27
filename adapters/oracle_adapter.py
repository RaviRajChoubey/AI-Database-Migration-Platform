import logging
from adapters.base_adapter import BaseAdapter
from config import SOURCE_DB

class OracleAdapter(BaseAdapter):

    def __init__(self, config=None):
        self.config = config if config else SOURCE_DB
        self.conn = None
        self.connect()

    def connect(self):
        try:
            try:
                import oracledb
                oracle_driver = oracledb
            except ImportError:
                import cx_Oracle
                oracle_driver = cx_Oracle

            user = self.config.get("user")
            password = self.config.get("password")
            dsn = self.config.get("dsn") or f"{self.config.get('host')}:{self.config.get('port', 1521)}/{self.config.get('database')}"

            self.conn = oracle_driver.connect(
                user=user,
                password=password,
                dsn=dsn
            )
            logging.info("Connected to Oracle Database successfully.")
        except Exception as e:
            logging.error(f"Oracle Connection Failed: {e}")
            self.conn = None

    def get_connection(self):
        return self.conn

    def get_tables(self):
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        cursor.execute("SELECT table_name FROM user_tables ORDER BY table_name")
        tables = [row[0].lower() for row in cursor.fetchall()]
        cursor.close()
        return tables

    def get_columns(self, table):
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        query = """
            SELECT 
                column_name, 
                data_type, 
                data_length, 
                nullable, 
                data_default
            FROM user_tab_columns 
            WHERE lower(table_name) = :tbl
            ORDER BY column_id
        """
        cursor.execute(query, tbl=table.lower())
        columns = []
        pks = self.get_primary_keys(table)

        for row in cursor.fetchall():
            col_name = row[0].lower()
            data_type = row[1].lower()
            data_len = row[2]
            nullable = row[3]
            default_val = row[4]

            if data_type in ["varchar2", "nvarchar2", "char"]:
                type_str = f"varchar({data_len})"
            elif data_type == "number":
                type_str = "numeric"
            elif data_type == "date":
                type_str = "timestamp"
            elif data_type == "clob":
                type_str = "text"
            elif data_type == "blob":
                type_str = "bytea"
            else:
                type_str = data_type

            columns.append({
                "Field": col_name,
                "Type": type_str,
                "Null": "YES" if nullable == "Y" else "NO",
                "Default": str(default_val) if default_val else None,
                "Extra": "",
                "Key": "PRI" if col_name in [pk.lower() for pk in pks] else ""
            })

        cursor.close()
        return columns

    def get_primary_keys(self, table):
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        query = """
            SELECT cols.column_name
            FROM user_constraints cons
            JOIN user_cons_columns cols ON cons.constraint_name = cols.constraint_name
            WHERE cons.constraint_type = 'P' AND lower(cons.table_name) = :tbl
        """
        cursor.execute(query, tbl=table.lower())
        pks = [row[0].lower() for row in cursor.fetchall()]
        cursor.close()
        return pks

    def get_foreign_keys(self, table):
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        query = """
            SELECT 
                a.column_name,
                c_pk.table_name r_table_name,
                b.column_name r_column_name,
                a.constraint_name
            FROM user_cons_columns a
            JOIN user_constraints c ON a.constraint_name = c.constraint_name
            JOIN user_constraints c_pk ON c.r_constraint_name = c_pk.constraint_name
            JOIN user_cons_columns b ON c_pk.constraint_name = b.constraint_name
            WHERE c.constraint_type = 'R' AND lower(a.table_name) = :tbl
        """
        cursor.execute(query, tbl=table.lower())
        fks = []
        for row in cursor.fetchall():
            fks.append({
                "COLUMN_NAME": row[0].lower(),
                "REFERENCED_TABLE_NAME": row[1].lower(),
                "REFERENCED_COLUMN_NAME": row[2].lower(),
                "CONSTRAINT_NAME": row[3].lower()
            })
        cursor.close()
        return fks

    def get_indexes(self, table):
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        query = """
            SELECT i.index_name, c.column_name, i.uniqueness
            FROM user_indexes i
            JOIN user_ind_columns c ON i.index_name = c.index_name
            WHERE lower(i.table_name) = :tbl
        """
        cursor.execute(query, tbl=table.lower())
        indexes = []
        for row in cursor.fetchall():
            indexes.append({
                "Key_name": row[0].lower(),
                "Column_name": row[1].lower(),
                "Non_unique": 0 if row[2] == "UNIQUE" else 1
            })
        cursor.close()
        return indexes

    def get_unique_constraints(self, table):
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        query = """
            SELECT cons.constraint_name, cols.column_name
            FROM user_constraints cons
            JOIN user_cons_columns cols ON cons.constraint_name = cols.constraint_name
            WHERE cons.constraint_type = 'U' AND lower(cons.table_name) = :tbl
        """
        cursor.execute(query, tbl=table.lower())
        unique = [{"CONSTRAINT_NAME": r[0].lower(), "COLUMN_NAME": r[1].lower()} for r in cursor.fetchall()]
        cursor.close()
        return unique

    def get_check_constraints(self, table):
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        query = """
            SELECT constraint_name, search_condition
            FROM user_constraints
            WHERE constraint_type = 'C' AND lower(table_name) = :tbl
        """
        cursor.execute(query, tbl=table.lower())
        checks = [{"CONSTRAINT_NAME": r[0].lower(), "CHECK_CLAUSE": str(r[1])} for r in cursor.fetchall()]
        cursor.close()
        return checks

    def get_views(self):
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        cursor.execute("SELECT view_name, text FROM user_views")
        views = [{"TABLE_NAME": r[0].lower(), "VIEW_DEFINITION": str(r[1])} for r in cursor.fetchall()]
        cursor.close()
        return views

    def get_procedures(self):
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        cursor.execute("SELECT object_name FROM user_objects WHERE object_type = 'PROCEDURE'")
        procs = [{"ROUTINE_NAME": r[0].lower()} for r in cursor.fetchall()]
        cursor.close()
        return procs

    def get_triggers(self):
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        cursor.execute("SELECT trigger_name, table_name, trigger_body FROM user_triggers")
        trigs = [{"TRIGGER_NAME": r[0].lower(), "EVENT_OBJECT_TABLE": r[1].lower(), "ACTION_STATEMENT": str(r[2])} for r in cursor.fetchall()]
        cursor.close()
        return trigs

    def get_functions(self):
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        cursor.execute("SELECT object_name FROM user_objects WHERE object_type = 'FUNCTION'")
        funcs = [{"ROUTINE_NAME": r[0].lower()} for r in cursor.fetchall()]
        cursor.close()
        return funcs

    def get_row_count(self, table):
        if not self.conn:
            return 0
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        cursor.close()
        return count

    def fetch_rows(self, table, offset, limit):
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        query = f"SELECT * FROM {table} OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def close(self):
        if self.conn:
            self.conn.close()
            logging.info("Oracle connection closed.")
