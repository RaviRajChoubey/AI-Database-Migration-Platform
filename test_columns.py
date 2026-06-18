from adapters.factory import get_adapter

source = get_adapter("mssql")

print("COLUMNS:")
print(
    source.get_columns(
        "customers"
    )
)