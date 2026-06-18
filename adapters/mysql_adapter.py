import mysql.connector

from config import SOURCE_DB
from adapters.base_adapter import BaseAdapter


class MySQLAdapter(BaseAdapter):

    def __init__(self):

        self.database = SOURCE_DB["database"]

        self.conn = mysql.connector.connect(
            host=SOURCE_DB["host"],
            port=SOURCE_DB["port"],
            user=SOURCE_DB["user"],
            password=SOURCE_DB["password"],
            database=self.database
        )

    def get_tables(self):

        cursor = self.conn.cursor(
            dictionary=True,
        )

        query = f"""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = '{self.database}'
        AND TABLE_TYPE = 'BASE TABLE'
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return [row["TABLE_NAME"] for row in rows]
    
    def get_columns(self, table):

        cursor = self.conn.cursor(
            dictionary=True,
            buffered=True
        )

        cursor.execute(f"DESCRIBE {table}")

        rows = cursor.fetchall()

        cursor.close()

        return rows
    
    def get_indexes(self, table):

        cursor = self.conn.cursor(
            dictionary=True,
            buffered=True
        )

        cursor.execute(
            f"SHOW INDEX FROM {table}"
        )

        rows = cursor.fetchall()

        cursor.close()

        return rows
    
    def get_views(self):

        cursor = self.conn.cursor(
            dictionary=True,
            buffered=True
        )

        query = f"""
        SELECT
            TABLE_NAME,
            VIEW_DEFINITION
        FROM INFORMATION_SCHEMA.VIEWS
        WHERE TABLE_SCHEMA =
        '{self.database}'
        """ 

        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    
    def get_triggers(self):

        cursor = self.conn.cursor(
            dictionary=True,
            buffered=True
        )

        query = f"""
        SELECT
            TRIGGER_NAME,
            EVENT_OBJECT_TABLE,
            ACTION_TIMING,
            EVENT_MANIPULATION,
            ACTION_STATEMENT
        FROM INFORMATION_SCHEMA.TRIGGERS
        WHERE TRIGGER_SCHEMA =
        '{self.database}'
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    
    def get_procedures(self):

        cursor = self.conn.cursor(
            dictionary=True,
            buffered=True
        )

        query = f"""
        SELECT
            ROUTINE_NAME,
            ROUTINE_TYPE,
            CREATED,
            LAST_ALTERED
        FROM INFORMATION_SCHEMA.ROUTINES
        WHERE ROUTINE_SCHEMA =
        '{self.database}'
        AND ROUTINE_TYPE = 'PROCEDURE'
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    
    def get_functions(self):

        cursor = self.conn.cursor(
            dictionary=True,
            buffered=True
        )

        query = f"""
        SELECT
            ROUTINE_NAME,
            ROUTINE_TYPE,
            CREATED,
            LAST_ALTERED
        FROM INFORMATION_SCHEMA.ROUTINES
        WHERE ROUTINE_SCHEMA =
        '{self.database}'
        AND ROUTINE_TYPE = 'FUNCTION'
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    
    def get_foreign_keys(self, table):

        cursor = self.conn.cursor(
            dictionary=True,
            buffered=True
            )

        query = f"""
        SELECT
            COLUMN_NAME,
            REFERENCED_TABLE_NAME,
            REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = '{self.database}'
        AND TABLE_NAME = '{table}'
        AND REFERENCED_TABLE_NAME IS NOT NULL
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    
    def get_check_constraints(self, table):

        cursor = self.conn.cursor(
            dictionary=True,
            buffered=True
        )

        query = f"""
        SELECT
            tc.CONSTRAINT_NAME,
            cc.CHECK_CLAUSE
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
        JOIN INFORMATION_SCHEMA.CHECK_CONSTRAINTS cc
            ON tc.CONSTRAINT_NAME =
            cc.CONSTRAINT_NAME
        WHERE tc.TABLE_SCHEMA =
            '{self.database}'
        AND tc.TABLE_NAME = '{table}'
        AND tc.CONSTRAINT_TYPE = 'CHECK'
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    
    def get_row_count(self, table):

        self.cursor.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        return self.cursor.fetchone()[0]

    def get_default_values(self, table):
        cursor = self.conn.cursor(
            dictionary=True,
            buffered=True
        )

        query = f"""
        SELECT
            COLUMN_NAME,
            COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA =
            '{self.database}'
        AND TABLE_NAME = '{table}'
        AND COLUMN_DEFAULT IS NOT NULL
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_unique_constraints(self, table):

        cursor = self.conn.cursor(
            dictionary=True,
            buffered=True
        )

        query = f"""
        SELECT
            CONSTRAINT_NAME,
            COLUMN_NAME
        FROM
            INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE
            TABLE_SCHEMA = '{self.database}'
            AND TABLE_NAME = '{table}'
            AND CONSTRAINT_NAME != 'PRIMARY'
            AND REFERENCED_TABLE_NAME IS NULL
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    

    def get_connection(self):
        return self.conn

    def close(self):
        if self.conn.is_connected():
            self.conn.close()