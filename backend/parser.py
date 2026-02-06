import re
from urllib.parse import urlparse

# ===============================
# STATUS (PCI REAL)
# ===============================
from datetime import datetime

def detectar_status(texto: str) -> str | None:
    t = texto.lower()

    # ❌ ignorar resultados e comunicados
    if any(p in t for p in [
        "resultado",
        "gabarito",
        "homologação",
        "homologado",
        "classificação",
        "convocação",
        "nomeação",
        "retificação",
        "comunicado"
    ]):
        return None

    # 🟢 ABERTO → verificar data de inscrição
    if "inscrição até" in t:
        datas = re.findall(r"\d{2}/\d{2}/\d{4}", t)
        if datas:
            try:
                data_fim = datetime.strptime(datas[0], "%d/%m/%Y").date()
                hoje = datetime.today().date()

                if data_fim >= hoje:
                    return "aberto"
                else:
                    return None  # ⛔ inscrição vencida
            except:
                return None

    # 🟡 PREVISTO → concurso sem data
    if any(p in t for p in [
        "concurso",
        "processo seletivo",
        "seleção",
        "edital",
        "vagas"
    ]):
        return "previsto"

    return None



# ===============================
# CARGO (SOMENTE OS DESEJADOS)
# ===============================

def detectar_cargo(texto: str) -> str | None:
    t = texto.lower()

    # 🎓 PROFESSOR
    if any(p in t for p in [
        "professor",
        "docente",
        "pedagogo",
        "educador",
        "magistério"
    ]):
        return "Professor"

    # 🧾 TÉCNICO ADMINISTRATIVO
    if any(p in t for p in [
        "técnico administrativo",
        "tecnico administrativo",
        "técnico-administrativo",
        "assistente administrativo",
        "assistente em educação",
        "administrativo",
        "tae"
    ]):
        return "Técnico Administrativo"

    # 📦 VÁRIOS CARGOS (PCI)
    if any(p in t for p in [
        "vários cargos",
        "diversos cargos",
        "cadastro reserva",
        "cadastro de reserva",
        "nível médio / técnico / superior",
        "nível médio e superior",
        "médio / técnico / superior"
    ]):
        return "Vários Cargos"

    return None


# ===============================
# EXTRAÇÕES
# ===============================

def extrair_salario(texto):
    m = re.search(r"r\$ ?[\d\.]+,\d{2}", texto.lower())
    return m.group(0).upper() if m else "Não informado"


def extrair_frequencia(texto):
    m = re.search(r"(20|30|40)\s?h", texto.lower())
    return m.group(0) if m else "Não informado"


def extrair_datas(texto):
    return re.findall(r"\d{2}/\d{2}/\d{4}", texto)


def extrair_local(texto):
    estados = [
        "acre","alagoas","amapá","amazonas","bahia","ceará","distrito federal",
        "espírito santo","goiás","maranhão","mato grosso","mato grosso do sul",
        "minas gerais","pará","paraíba","paraná","pernambuco","piauí",
        "rio de janeiro","rio grande do norte","rio grande do sul",
        "rondônia","roraima","santa catarina","são paulo","sergipe","tocantins"
    ]
    t = texto.lower()
    for e in estados:
        if e in t:
            return e.title()
    return "Não informado"


# ===============================
# ÂMBITO
# ===============================

def detectar_ambito_por_link(link: str | None) -> str | None:
    if not link:
        return None

    try:
        dominio = urlparse(link).netloc.lower()
    except:
        return None

    if dominio.endswith("gov.br") or ".edu.br" in dominio:
        return "Federal"

    if dominio.count(".gov.br") == 2:
        return "Estadual"

    if any(p in dominio for p in ["prefeitura", "municipio", "municipal"]):
        return "Municipal"

    return None


def detectar_ambito(instituicao: str, link: str | None = None) -> str:
    ambito_link = detectar_ambito_por_link(link)
    if ambito_link:
        return ambito_link

    inst = instituicao.lower()

    if any(p in inst for p in [
        "ministério", "mec", "fnde", "inep",
        "instituto federal", "universidade federal",
        "if ", "if-", "ines", "enap",
        "exército", "marinha", "aeronáutica",
        "conselho federal"
    ]):
        return "Federal"

    if "conselho regional" in inst:
        return "Federal"

    if any(p in inst for p in ["secretaria estadual", "seduc", "see"]):
        return "Estadual"

    if "prefeitura" in inst:
        return "Municipal"

    return "Federal"

