from adapters.mysql_adapter import MySQLAdapter
from adapters.mssql_adapter import MSSQLAdapter
from adapters.oracle_adapter import OracleAdapter

def get_adapter(source_type):

    if source_type == "mysql":
        return MySQLAdapter()

    elif source_type == "mssql":
        return MSSQLAdapter()

    elif source_type == "oracle":
        return OracleAdapter()

    raise ValueError(
        f"Unsupported source type: {source_type}"
    )