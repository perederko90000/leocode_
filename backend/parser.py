import re
from urllib.parse import urlparse
from datetime import datetime


def detectar_status(texto: str) -> str | None:
    t = texto.lower()
    hoje = datetime.today().date()

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

    datas = re.findall(r"\d{2}/\d{2}/\d{4}", t)

    if datas:
        try:
            data_fim = max(datetime.strptime(d, "%d/%m/%Y").date() for d in datas)
            if data_fim >= hoje:
                return "aberto"
            return None
        except:
            return None

    if any(p in t for p in [
        "concurso",
        "processo seletivo",
        "seleção",
        "edital",
        "vagas"
    ]):
        return "previsto"

    return None


def detectar_cargo(texto: str) -> str | None:
    t = texto.lower()

    if any(p in t for p in ["professor", "docente", "pedagogo", "educador", "magistério"]):
        return "Professor"

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

    if any(p in t for p in [
        "vários cargos",
        "diversos cargos",
        "cadastro reserva",
        "cadastro de reserva"
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
        "if ", "if-", "enap",
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

