import requests
import sqlite3
import re
from bs4 import BeautifulSoup

from .parser import (
    extrair_salario,
    extrair_frequencia,
    detectar_cargo,
    detectar_ambito,
    extrair_datas
)

BASE_URL = "https://www.pciconcursos.com.br"
URLS = [
    "https://www.pciconcursos.com.br/concursos/educacao/",
    "https://www.pciconcursos.com.br/concursos/administracao/"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def limpar_texto(t):
    return re.sub(r"\s+", " ", t).strip()

def normalizar_link(href: str) -> str | None:
    if not href:
        return None

    href = href.strip()

    # Corrige casos tipo "https//site.com"
    if href.startswith("https//"):
        href = href.replace("https//", "https://", 1)

    # Link absoluto válido
    if href.startswith("http://") or href.startswith("https://"):
        return href

    # Link relativo
    if href.startswith("/"):
        return "https://www.pciconcursos.com.br" + href

    return None

def rodar():
    conn = sqlite3.connect("dados.db")
    cursor = conn.cursor()

    inseridos = 0

    for url in URLS:
        print(f"🔍 Acessando: {url}")
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "lxml")
        blocos = soup.select(".ca")
        print(f"📦 Blocos encontrados: {len(blocos)}")

        for bloco in blocos:
            texto = limpar_texto(bloco.get_text(" ", strip=True))
            if len(texto) < 30:
                continue

            a = bloco.find("a", href=True)
            if not a:
                continue

            href = str(a.get("href"))
            link = normalizar_link(href)

            if not link:
                    continue

            # evita duplicar
            cursor.execute(
                "SELECT 1 FROM publicacoes WHERE link = ?",
                (link,)
            )
            if cursor.fetchone():
                continue

            salario = extrair_salario(texto) or "Não informado"
            frequencia = extrair_frequencia(texto) or "Não informado"
            cargo = detectar_cargo(texto)
            ambito = detectar_ambito(texto)
            datas = extrair_datas(texto)

            data_inscricao = datas[0] if datas else None

            instituicao = texto[:180]

            cursor.execute("""
                INSERT INTO publicacoes (
                    instituicao,
                    cargo,
                    ambito,
                    salario,
                    frequencia,
                    local,
                    data_inscricao,
                    fonte,
                    link
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                instituicao,
                cargo,
                ambito,
                salario,
                frequencia,
                None,
                data_inscricao,
                "PCI Concursos",
                link
            ))

            inseridos += 1
            print("✅ Inserido:", instituicao[:80])

        conn.commit()

    conn.close()
    print(f"\n🏁 PCI finalizado. Total inserido: {inseridos}")

if __name__ == "__main__":
    rodar()

