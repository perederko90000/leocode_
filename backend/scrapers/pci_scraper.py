import requests
import sqlite3
import re
from bs4 import BeautifulSoup

from ..parser import (
    extrair_salario,
    extrair_frequencia,
    detectar_cargo,
    detectar_ambito,
    extrair_datas,
    detectar_status
)

BASE_URL = "https://www.pciconcursos.com.br"

URLS = [
    "https://www.pciconcursos.com.br/concursos/",
    "https://www.pciconcursos.com.br/concursos/educacao/",
    "https://www.pciconcursos.com.br/concursos/administracao/",
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
    if href.startswith("https//"):
        href = href.replace("https//", "https://", 1)
    if href.startswith("http"):
        return href
    if href.startswith("/"):
        return BASE_URL + href
    return None

# LIMPEZA DO BANCO
def limpar_publicacoes(cursor):
    cursor.execute("""
        DELETE FROM publicacoes
        WHERE
            status IS NULL
            OR status NOT IN ('aberto', 'previsto')
            OR (
                status = 'aberto'
                AND data_inscricao IS NOT NULL
                AND date(
                    substr(data_inscricao, 7, 4) || '-' ||
                    substr(data_inscricao, 4, 2) || '-' ||
                    substr(data_inscricao, 1, 2)
                ) < date('now')
            )
    """)

def rodar():
    conn = sqlite3.connect("dados.db")
    cursor = conn.cursor()

    limpar_publicacoes(cursor)
    conn.commit()

    inseridos = 0

    for url in URLS:
        print(f"🔍 Acessando: {url}")
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "lxml")
        blocos = soup.select(".ca")

        for bloco in blocos:
            texto = limpar_texto(bloco.get_text(" ", strip=True))
            if len(texto) < 40:
                continue

            status = detectar_status(texto)
            if not status:
                continue

            cargo = detectar_cargo(texto)
            if not cargo:
                continue

            a = bloco.find("a", href=True)
            if not a:
                continue

            link = normalizar_link(str(a.get("href")))
            if not link:
                continue

          

            cursor.execute("SELECT 1 FROM publicacoes WHERE link = ?", (link,))
            if cursor.fetchone():
                continue

            salario = extrair_salario(texto)
            frequencia = extrair_frequencia(texto)
            ambito = detectar_ambito(texto, link)
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
                    status,
                    fonte,
                    link
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                instituicao,
                cargo,
                ambito,
                salario,
                frequencia,
                None,
                data_inscricao,
                status,
                "PCI Concursos",
                link
            ))

            inseridos += 1
            print(f"✅ [{status}] [{cargo}] {instituicao[:60]}")

        conn.commit()

    conn.close()
    print(f"\n🏁 PCI finalizado. Total inserido: {inseridos}")


if __name__ == "__main__":
    rodar()


