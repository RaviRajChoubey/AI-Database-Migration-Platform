import psycopg2

conn = psycopg2.connect(
    host="ep-muddy-rain-aoftgafo-pooler.c-2.ap-southeast-1.aws.neon.tech",
    port=5432,
    database="neondb",
    user="neondb_owner",
    password="npg_pvg0wBQkOyc7",
    sslmode="require"
)

print("Connected Successfully")

conn.close()