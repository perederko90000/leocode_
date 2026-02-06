from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

from .init_db import init_db
from .runner import iniciar_scrapers

app = FastAPI(title="Alerta de Concursos API")

# CORS (liberado)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
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
    status: str = "aberto",   # 🔒 default = aberto
    salario_min: int = 0,
    ordenacao: str = "",
    page: int = 1,
    limit: int = 9
):
    offset = (page - 1) * limit

    conn = sqlite3.connect("dados.db")
    cursor = conn.cursor()

    # ORDENACAO
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

    # QUERY BASE (STATUS APLICADO)
    query = """
        SELECT
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
        FROM publicacoes
        WHERE status = ?
    """
    params = [status]

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

    # TOTAL CORRETO (mesmo filtro)
    cursor.execute(
        "SELECT COUNT(*) FROM publicacoes WHERE status = ?",
        (status,)
    )
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
                "status": r[7],
                "fonte": r[8],
                "link": r[9],
            }
            for r in rows
            if salario_num(r[3]) >= salario_min
        ]
    }


@app.post("/atualizar")
def atualizar(background_tasks: BackgroundTasks):
    background_tasks.add_task(iniciar_scrapers)
    return {"status": "Atualização iniciada"}


@app.on_event("startup")
def start_background_tasks():
    init_db()
    iniciar_scrapers()
