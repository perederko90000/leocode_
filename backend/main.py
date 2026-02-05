from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from .init_db import init_db

import sqlite3

app = FastAPI(title="Alerta de Concursos API")

# CORS (frontend local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://leocode-fnpg.vercel.app",
        "https://leocode-fnpg.vercel.app",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def salario_num(v):
    try:
        return int(
            v.replace("R$", "")
             .replace(".", "")
             .replace(",", "")
             .strip()
        )
    except:
        return 0

@app.get("/dados")
def listar(
    q: str = "",
    ambito: str = "",
    cargo: str = "",
    salario_min: int = 0,
    ordenacao: str = "",
    page: int = 1,
    limit: int = 9
):
    offset = (page - 1) * limit

    conn = sqlite3.connect("dados.db")
    cursor = conn.cursor()

    order_sql = "created_at DESC"

    if ordenacao == "salario":
        order_sql = """
            CASE WHEN salario LIKE 'R$%' THEN 0 ELSE 1 END,
            CAST(REPLACE(REPLACE(REPLACE(salario,'R$',''),'.',''),',','') AS INTEGER) DESC
        """
    elif ordenacao == "frequencia":
        order_sql = """
            CASE
                WHEN frequencia LIKE '20%' THEN 1
                WHEN frequencia LIKE '30%' THEN 2
                WHEN frequencia LIKE '40%' THEN 3
                ELSE 9
            END ASC
        """

    query = f"""
        SELECT
            instituicao, cargo, ambito, salario, frequencia,
            local, data_inscricao, fonte, link
        FROM publicacoes
        WHERE 1=1
    """
    params = []

    if q:
        query += " AND instituicao LIKE ?"
        params.append(f"%{q}%")

    if ambito:
        query += " AND ambito = ?"
        params.append(ambito)

    if cargo:
        query += " AND cargo = ?"
        params.append(cargo)

    query += f" ORDER BY {order_sql} LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM publicacoes")
    total = cursor.fetchone()[0]

    conn.close()

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "results": [
            {
                "instituicao": r[0],
                "cargo": r[1],
                "ambito": r[2],
                "salario": r[3],
                "frequencia": r[4],
                "local": r[5],
                "data_inscricao": r[6],
                "fonte": r[7],
                "link": r[8],
            }
            for r in rows
            if salario_num(r[3]) >= salario_min
        ]
    }
from .runner import iniciar_scrapers

from fastapi import BackgroundTasks

@app.post("/atualizar")
def atualizar(background_tasks: BackgroundTasks):
    background_tasks.add_task(iniciar_scrapers)
    return {"status": "Atualização iniciada"}

@app.on_event("startup")
def start_background_tasks():
    init_db()
    iniciar_scrapers()




