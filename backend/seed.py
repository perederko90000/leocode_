import sqlite3

conn = sqlite3.connect("dados.db")
cursor = conn.cursor()

dados = [
    ("Prefeitura de Campinas", "R$ 4.320,00", "40h", "Municipal"),
    ("Secretaria da Educação SP", "R$ 3.900,00", "30h", "Estadual"),
    ("Instituto Federal de SP", "R$ 6.356,00", "40h", "Federal")
]

cursor.executemany("""
INSERT INTO publicacoes (instituicao, salario, frequencia, fonte)
VALUES (?, ?, ?, ?)
""", dados)

conn.commit()
conn.close()

print("✅ Dados de teste inseridos")
    