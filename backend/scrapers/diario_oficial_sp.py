import requests
import sqlite3
from bs4 import BeautifulSoup
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from parser import (
    extrair_salario,
    extrair_frequencia,
    detectar_cargo
)

BASE_URL = "https://www.in.gov.br/en/web/dou/-/busca"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

TERMOS = [
    "concurso",
    "processo seletivo",
    "professor",
    "instituto federal",
    "universidade federal",
    "técnico administrativo"
]


def texto_valido(texto: str) -> bool:
    t = texto.lower()
    return any(p in t for p in TERMOS)


def rodar():
    print("📘 Diário Oficial da União – Busca")

    conn = sqlite3.connect("dados.db")
    cursor = conn.cursor()

    inseridos = 0

    for termo in TERMOS[:4]:  # limite de segurança
        print(f"🔍 Buscando: {termo}")

        r = requests.get(
            BASE_URL,
            headers=HEADERS,
            params={"q": termo},
            timeout=20
        )
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "lxml")

        # 🔑 ESTE É O SELETOR CORRETO
        resultados = soup.select("li.resultado-busca")

        print(f"📦 Resultados encontrados: {len(resultados)}")

        for item in resultados:
            titulo = item.get_text(" ", strip=True)

            link_tag = item.find("a", href=True)
            if not link_tag:
                continue

            link = str(link_tag["href"])
            if not link.startswith("http"):
                link = "https://www.in.gov.br" + link

            if not texto_valido(titulo):
                continue

            cursor.execute(
                "SELECT 1 FROM publicacoes WHERE link = ?",
                (link,)
            )
            if cursor.fetchone():
                continue

            salario = extrair_salario(titulo) or "Não informado"
            frequencia = extrair_frequencia(titulo) or "Não informado"

            cursor.execute("""
                INSERT INTO publicacoes
                (instituicao, salario, frequencia, ambito, cargo, link)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                titulo[:250],
                salario,
                frequencia,
                "Federal",
                detectar_cargo(titulo),
                link
            ))

            conn.commit()
            inseridos += 1
            print("✅ Inserido:", titulo[:80])

    conn.close()
    print(f"🏁 DOU finalizado. Total inserido: {inseridos}")


if __name__ == "__main__":
    rodar()
