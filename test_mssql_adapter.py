from adapters.factory import get_adapter

source = get_adapter("mssql")

print("TABLES:")
print(source.get_tables())

print("\nCOLUMNS:")
print(source.get_columns("customers"))

print("\nINDEXES:")
print(source.get_indexes("customers"))

print("\nFOREIGN KEYS:")
print(source.get_foreign_keys("orders"))

print("\nVIEWS:")
print(source.get_views())

print("\nTRIGGERS:")
print(source.get_triggers())

print("\nPROCEDURES:")
print(source.get_procedures())

print("\nFUNCTIONS:")
print(source.get_functions())

print("\nCHECK CONSTRAINTS:")
print(source.get_check_constraints("products"))

print("\nDEFAULT VALUES:")
print(source.get_default_values("customers"))

print("\nUNIQUE CONSTRAINTS:")
print(source.get_unique_constraints("customers"))