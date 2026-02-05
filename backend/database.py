import sqlite3

conn = sqlite3.connect("dados.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS publicacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    instituicao TEXT,
    cargo TEXT,
    ambito TEXT,

    salario TEXT,
    frequencia TEXT,

    local TEXT,
    data_inscricao TEXT,

    fonte TEXT,
    link TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Índices para performance (busca rápida)
cursor.execute("CREATE INDEX IF NOT EXISTS idx_instituicao ON publicacoes(instituicao)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_ambito ON publicacoes(ambito)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_cargo ON publicacoes(cargo)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_fonte ON publicacoes(fonte)")

conn.commit()
conn.close()

print("✅ Banco criado com schema final.")
