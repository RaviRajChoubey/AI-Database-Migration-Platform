import os
from dotenv import load_dotenv

load_dotenv()

SOURCE_DB = {
    "type": "mssql",
    "host": "localhost\\MSSQLSERVER01",
    "database": "source_mssql",
    "driver": "ODBC Driver 18 for SQL Server"
}

TARGET_DB = {
    "host": os.getenv("NEON_HOST"),
    "port": int(os.getenv("NEON_PORT")),
    "user": os.getenv("NEON_USER"),
    "password": os.getenv("NEON_PASSWORD"),
    "database": os.getenv("NEON_DATABASE")
}