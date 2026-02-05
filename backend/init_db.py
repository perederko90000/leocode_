import sqlite3

conn = sqlite3.connect("dados.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS publicacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instituicao TEXT,
    salario TEXT,
    frequencia TEXT,
    fonte TEXT
)
""")

conn.commit()
conn.close()

print("✅ Banco e tabela 'publicacoes' criados com sucesso")
