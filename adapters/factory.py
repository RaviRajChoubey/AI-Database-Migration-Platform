from adapters.mysql_adapter import MySQLAdapter
from adapters.mssql_adapter import MSSQLAdapter

def get_adapter(source_type):

    if source_type == "mysql":
        return MySQLAdapter()

    elif source_type == "mssql":
        return MSSQLAdapter()

    raise ValueError(
        f"Unsupported source type: {source_type}"
    )