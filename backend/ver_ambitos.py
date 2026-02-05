import sqlite3

conn = sqlite3.connect("dados.db")
cursor = conn.cursor()

cursor.execute(
    "SELECT ambito, COUNT(*) FROM publicacoes GROUP BY ambito"
)

print(cursor.fetchall())

conn.close()