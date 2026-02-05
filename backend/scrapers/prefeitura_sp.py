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

URL = "https://educacao.sme.prefeitura.sp.gov.br/concursos-sme/?status=Em+Aberto&view=all"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

KEYWORDS_VALIDAS = [
    "professor",
    "auxiliar",
    "técnico",
    "edital",
    "processo seletivo",
    "vagas"
]


def texto_valido(texto: str) -> bool:
    t = texto.lower()
    return any(k in t for k in KEYWORDS_VALIDAS)


def eh_link_generico(titulo: str) -> bool:
    t = titulo.lower()
    return any(p in t for p in [
        "confira",
        "veja",
        "todos os concursos",
        "concursos abertos",
        "clique aqui",
        "página"
    ])

def pagina_eh_edital(url: str) -> bool:
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        texto = r.text.lower()

        sinais = [
            "edital",
            "inscrição",
            "vagas",
            "data",
            "prova",
            "processo seletivo"
        ]

        pontos = sum(1 for s in sinais if s in texto)
        return pontos >= 2
    except:
        return False

def rodar():
    print("🏛️ SME São Paulo – Concursos Oficiais")

    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")

    conn = sqlite3.connect("dados.db")
    cursor = conn.cursor()
# 🔥 NOVO: entra no edital e valida
    
    
    inseridos = 0

    for a in soup.find_all("a", href=True):
        titulo = a.get_text(" ", strip=True)
        link = str(a["href"])
        if not pagina_eh_edital(link):
                continue
        if not titulo or len(titulo) < 30:
            continue

        if eh_link_generico(titulo):
            continue

        if not texto_valido(titulo):
            continue

        if "/concursos-sme/" not in link:
            continue

        if not link.startswith("http"):
            link = "https://educacao.sme.prefeitura.sp.gov.br" + link

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
            "Municipal",
            detectar_cargo(titulo),
            link
        ))

        conn.commit()
        inseridos += 1
        print("✅ Inserido:", titulo[:90])

    conn.close()
    print(f"🏁 SME finalizado. Total inserido: {inseridos}")


if __name__ == "__main__":
    rodar()
