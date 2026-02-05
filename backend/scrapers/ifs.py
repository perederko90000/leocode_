""" import requests
import sqlite3
from bs4 import BeautifulSoup

from parser import (
    extrair_salario,
    extrair_frequencia,
    detectar_cargo,
    extrair_datas,
    edital_relevante
)

URL = "https://concursopublico.ifsp.edu.br/editais"
BASE = "https://concursopublico.ifsp.edu.br"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def rodar():
    print("🔍 IFSP – Editais Oficiais")

    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")
    conn = sqlite3.connect("dados.db")
    cursor = conn.cursor()

    inseridos = 0

    # cada bloco de edital aparece em tabela ou lista de cards
    for a in soup.select("a[href]"):
        texto = a.get_text(" ", strip=True)
        href =str (a["href"])

        if not texto or not href:
            continue

        # filtro inteligente
        if not edital_relevante(texto):
            continue

        # normaliza link
        if href.startswith("http"):
            link = href
        else:
            link = BASE + href

        # evita duplicar
        cursor.execute(
            "SELECT 1 FROM publicacoes WHERE link = ?",
            (link,)
        )
        if cursor.fetchone():
            continue

        salario = extrair_salario(texto) or "Consultar edital"
        frequencia = extrair_frequencia(texto) or "Consultar edital"
        cargo = detectar_cargo(texto)
        datas = extrair_datas(texto)
        data_inscricao = datas[0] if datas else None

        cursor.execute("""
          """   INSERT INTO publicacoes (
                instituicao,
                cargo,
                ambito,
                salario,
                frequencia,
                local,
                data_inscricao,
                fonte,
                link
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) """
        """, (
            "Instituto Federal de São Paulo (IFSP)",
            cargo,
            "Federal",
            salario,
            frequencia,
            None,
            data_inscricao,
            "IFSP",
            link
        ))

        inseridos += 1
        print("✅ Inserido:", texto[:80])

    conn.commit()
    conn.close()
    print(f"🏁 IFSP finalizado. Total inserido: {inseridos}")
 """