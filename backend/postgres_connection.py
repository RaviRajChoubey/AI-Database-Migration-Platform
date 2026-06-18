import psycopg2

from config import TARGET_DB

def get_pg_connection():

    return psycopg2.connect(
        host=TARGET_DB["host"],
        database=TARGET_DB["database"],
        user=TARGET_DB["user"],
        password=TARGET_DB["password"]
    )