import sqlite3

conn = sqlite3.connect("dados.db")
cursor = conn.cursor()

cursor.execute("ALTER TABLE publicacoes ADD COLUMN local TEXT")
conn.commit()
conn.close()

print("✅ Coluna 'local' adicionada")
