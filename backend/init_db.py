import sqlite3

DB_NAME = "dados.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
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

    conn.commit()
    conn.close()

    print("✅ Banco de dados inicializado com sucesso.")

if __name__ == "__main__":
    init_db()
