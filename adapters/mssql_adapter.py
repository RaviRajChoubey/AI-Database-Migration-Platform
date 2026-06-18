import pyodbc

from config import SOURCE_DB
from adapters.base_adapter import BaseAdapter


class MSSQLAdapter(BaseAdapter):

    def __init__(self):

        self.database = SOURCE_DB["database"]

        self.conn = pyodbc.connect(
            f"""
            DRIVER={{{SOURCE_DB["driver"]}}};
            SERVER={SOURCE_DB["host"]};
            DATABASE={SOURCE_DB["database"]};
            Trusted_Connection=yes;
            TrustServerCertificate=yes;
            MARS_Connection=yes;
            """
        )

    def get_tables(self):

        cursor = self.conn.cursor()

        query = """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        cursor.close()

        return [row[0] for row in rows]
    
    def get_columns(self, table):

        cursor = self.conn.cursor()

        query = f"""
        SELECT
            c.COLUMN_NAME,
            c.DATA_TYPE,
            c.CHARACTER_MAXIMUM_LENGTH,
            c.IS_NULLABLE,
            c.COLUMN_DEFAULT,
            CASE
                WHEN k.COLUMN_NAME IS NOT NULL
                THEN 'PRI'
                ELSE ''
            END AS KEY_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS c

        LEFT JOIN (

            SELECT ku.COLUMN_NAME

            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc

            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE ku
                ON tc.CONSTRAINT_NAME =
                ku.CONSTRAINT_NAME

            WHERE tc.TABLE_NAME = '{table}'
            AND tc.CONSTRAINT_TYPE =
                'PRIMARY KEY'

        ) k

        ON c.COLUMN_NAME = k.COLUMN_NAME

        WHERE c.TABLE_NAME = '{table}'

        ORDER BY c.ORDINAL_POSITION
        """

        cursor.execute(query)

        columns = []

        for row in cursor.fetchall():

            data_type = row[1]

            if (
                row[1].lower() == "varchar"
                and row[2]
                and row[2] > 0
            ):

                data_type = (
                    f"VARCHAR({row[2]})"
                )

            columns.append({

                "Field": row[0],

                "Type": data_type,

                "Null": row[3],

                "Default": row[4],

                "Extra": "",

                "Key": row[5]

            })

        cursor.close()

        return columns
    
    def get_foreign_keys(self, table):

        cursor = self.conn.cursor()

        query = f"""
        SELECT
            kcu.COLUMN_NAME,
            ccu.TABLE_NAME AS REFERENCED_TABLE_NAME,
            ccu.COLUMN_NAME AS REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
            ON rc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
        JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE ccu
            ON rc.UNIQUE_CONSTRAINT_NAME = ccu.CONSTRAINT_NAME
        WHERE kcu.TABLE_NAME = '{table}'
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        cursor.close()

        return [
            {
                "COLUMN_NAME": row[0],
                "REFERENCED_TABLE_NAME": row[1],
                "REFERENCED_COLUMN_NAME": row[2]
            }
            for row in rows
        ]

    def get_indexes(self, table):

        cursor = self.conn.cursor()

        query = f"""
        SELECT
            i.name AS INDEX_NAME,
            c.name AS COLUMN_NAME,
            i.is_unique
        FROM sys.indexes i
        INNER JOIN sys.index_columns ic
            ON i.object_id = ic.object_id
            AND i.index_id = ic.index_id
        INNER JOIN sys.columns c
            ON ic.object_id = c.object_id
            AND ic.column_id = c.column_id
        INNER JOIN sys.tables t
            ON i.object_id = t.object_id
        WHERE t.name = '{table}'
        AND i.is_primary_key = 0
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        indexes = []

        for row in rows:

            indexes.append({
                "Key_name": row[0],
                "Column_name": row[1],
                "Non_unique": 0 if row[2] else 1
            })

        cursor.close()

        return indexes
    
    def get_views(self):

        cursor = self.conn.cursor()

        query = """
        SELECT
            TABLE_NAME,
            VIEW_DEFINITION
        FROM INFORMATION_SCHEMA.VIEWS
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        views = []

        for row in rows:

            views.append({
                "TABLE_NAME": row[0],
                "VIEW_DEFINITION": row[1]
            })

        cursor.close()

        return views

    def get_row_count(self, table):

        print(">>> MSSQLAdapter.get_row_count EXECUTED")

        cursor = self.conn.cursor()

        cursor.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        count = cursor.fetchone()[0]

        cursor.close()

        return count

    def get_triggers(self):

        cursor = self.conn.cursor()

        query = """
        SELECT
            name,
            OBJECT_NAME(parent_id)
        FROM sys.triggers
        WHERE parent_class = 1
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        triggers = []

        for row in rows:

            triggers.append({
                "TRIGGER_NAME": row[0],
                "TABLE_NAME": row[1]
            })

        cursor.close()

        return triggers

    def get_procedures(self):

        cursor = self.conn.cursor()

        query = """
        SELECT
            ROUTINE_NAME,
            CREATED,
            LAST_ALTERED
        FROM INFORMATION_SCHEMA.ROUTINES
        WHERE ROUTINE_TYPE = 'PROCEDURE'
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        procedures = []

        for row in rows:

            procedures.append({
                "ROUTINE_NAME": row[0],
                "CREATED": row[1],
                "LAST_ALTERED": row[2]
            })

        cursor.close()

        return procedures

    def get_functions(self):

        cursor = self.conn.cursor()

        query = """
        SELECT
            ROUTINE_NAME,
            CREATED,
            LAST_ALTERED
        FROM INFORMATION_SCHEMA.ROUTINES
        WHERE ROUTINE_TYPE = 'FUNCTION'
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        functions = []

        for row in rows:

            functions.append({
                "ROUTINE_NAME": row[0],
                "CREATED": row[1],
                "LAST_ALTERED": row[2]
            })

        cursor.close()

        return functions

    def get_check_constraints(self, table):

        cursor = self.conn.cursor()

        query = f"""
        SELECT
            cc.name,
            cc.definition
        FROM sys.check_constraints cc
        INNER JOIN sys.tables t
            ON cc.parent_object_id = t.object_id
        WHERE t.name = '{table}'
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        constraints = []

        for row in rows:

            constraints.append({
                "CONSTRAINT_NAME": row[0],
                "CHECK_CLAUSE": row[1]
            })

        cursor.close()

        return constraints

    def get_default_values(self, table):

        cursor = self.conn.cursor()

        query = f"""
        SELECT
            c.name,
            dc.definition
        FROM sys.default_constraints dc
        INNER JOIN sys.columns c
            ON dc.parent_object_id = c.object_id
            AND dc.parent_column_id = c.column_id
        INNER JOIN sys.tables t
            ON c.object_id = t.object_id
        WHERE t.name = '{table}'
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        defaults = []

        for row in rows:

            defaults.append({
                "COLUMN_NAME": row[0],
                "COLUMN_DEFAULT": row[1]
            })

        cursor.close()

        return defaults

    def get_unique_constraints(self, table):

        cursor = self.conn.cursor()

        query = f"""
        SELECT
            kc.name,
            c.name
        FROM sys.key_constraints kc
        INNER JOIN sys.index_columns ic
            ON kc.parent_object_id = ic.object_id
            AND kc.unique_index_id = ic.index_id
        INNER JOIN sys.columns c
            ON ic.object_id = c.object_id
            AND ic.column_id = c.column_id
        INNER JOIN sys.tables t
            ON kc.parent_object_id = t.object_id
        WHERE kc.type = 'UQ'
        AND t.name = '{table}'
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        constraints = []

        for row in rows:

            constraints.append({
                "CONSTRAINT_NAME": row[0],
                "COLUMN_NAME": row[1]
            })

        cursor.close()

        return constraints
    
    def get_connection(self):
        return self.conn

    def close(self):

        self.conn.close()