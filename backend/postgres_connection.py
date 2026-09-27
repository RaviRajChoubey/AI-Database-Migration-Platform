import psycopg2
from config import TARGET_DB

def get_pg_connection(target_config=None):
    cfg = target_config if target_config is not None else TARGET_DB
    kwargs = {
        "host": cfg["host"],
        "port": cfg["port"],
        "database": cfg["database"],
        "user": cfg["user"],
        "password": cfg["password"]
    }
    if "sslmode" in cfg and cfg["sslmode"]:
        kwargs["sslmode"] = cfg["sslmode"]
    return psycopg2.connect(**kwargs)