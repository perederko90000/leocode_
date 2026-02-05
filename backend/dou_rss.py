import feedparser
import requests
import pdfplumber
import sqlite3
import re
from io import BytesIO
from bs4 import BeautifulSoup
import time

RSS_URL = "https://www.in.gov.br/rss"

PALAVRAS_CHAVE = [
    "educação", "educacional", "ensino", "docente", "professor",
    "magistério", "instituto federal", "universidade", "campus",
    "concurso", "processo seletivo", "edital", "contratação",
    "professor substituto", "educação básica", "educação infantil"
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

def extrair_links_pdf(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, "lxml")

    pdfs = []
    for a in soup.find_all("a", href=True):
        if ".pdf" in a["href"].lower():
            pdfs.append(a["href"])

    return pdfs

def extrair_texto_pdf(url_pdf):
    r = requests.get(url_pdf, headers=HEADERS, timeout=30)
    texto = ""

    with pdfplumber.open(BytesIO(r.content)) as pdf:
        for page in pdf.pages:
            texto += page.extract_text() or ""

    return texto.lower()

def rodar():
    print("🔍 Lendo RSS do DOU...")
    feed = feedparser.parse(RSS_URL)
    print(f"📡 Itens encontrados: {len(feed.entries)}")

    conn = sqlite3.connect("dados.db")
    cursor = conn.cursor()
    inseridos = 0

    for entry in feed.entries[:30]:
        titulo = entry.title.lower()
        link = entry.link

        print("\n➡️ Analisando:", entry.title)

        if not any(p in titulo for p in PALAVRAS_CHAVE):
            print("⏭️ Ignorado pelo título")
            continue

        cursor.execute(
            "SELECT 1 FROM publicacoes WHERE instituicao = ?",
            (entry.title,)
        )
        if cursor.fetchone():
            print("♻️ Já existe no banco")
            continue

        try:
            time.sleep(2)

            pdfs = extrair_links_pdf(link)
            if not pdfs:
                print("⚠️ Nenhum PDF encontrado")
                continue

            texto = ""
            for pdf in pdfs:
                print("📄 Lendo PDF:", pdf)
                texto += extrair_texto_pdf(pdf)

            salario = re.search(r"r\$ ?[\d\.]+,\d{2}", texto)
            frequencia = re.search(r"(20|30|40)\s?h", texto)

            cursor.execute("""
                INSERT INTO publicacoes (instituicao, salario, frequencia, fonte)
                VALUES (?, ?, ?, ?)
            """, (
                entry.title,
                salario.group(0) if salario else "Não informado",
                frequencia.group(0) if frequencia else "Não informado",
                "Federal"
            ))

            conn.commit()
            inseridos += 1
            print("🎯 INSERIDO COM SUCESSO")

        except Exception as e:
            print("❌ Erro:", e)

    conn.close()
    print(f"\n🏁 Finalizado. Total inserido: {inseridos}")

if __name__ == "__main__":
    rodar()
