import requests
from bs4 import BeautifulSoup
import sqlite3
import time

URL = "https://www.in.gov.br/leiturajornal"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
}

PALAVRAS = ["educação", "professor", "docente"]

def rodar():
    try:
        time.sleep(2)  # respeita o servidor
        r = requests.get(URL, headers=HEADERS, timeout=30)

        if r.status_code != 200:
            print("⚠️ Resposta inesperada:", r.status_code)
            return

        soup = BeautifulSoup(r.text, "lxml")
        texto = soup.get_text(" ").lower()

        if any(p in texto for p in PALAVRAS):
            conn = sqlite3.connect("dados.db")
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO publicacoes (instituicao, salario, frequencia, fonte)
            VALUES (?, ?, ?, ?)
            """, (
                "Diário Oficial da União",
                "Não informado",
                "Não informado",
                "Federal"
            ))

            conn.commit()
            conn.close()

            print("✅ Publicação do DOU registrada")
        else:
            print("ℹ️ Nenhuma publicação relevante encontrada")

    except requests.exceptions.RequestException as e:
        print("❌ Erro de conexão:", e)

if __name__ == "__main__":
    rodar()
