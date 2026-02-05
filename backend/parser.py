import re
from urllib.parse import urlparse
PALAVRAS_VALIDAS = [
    "professor",
    "docente",
    "magistério",
    "educação",
    "pedagógico",
    "pedagogia",
    "ensino",
    "técnico administrativo",
    "técnico-administrativo",
    "tae",
    "assistente em educação",
    "técnico em assuntos educacionais",
    "educacional"
]
PALAVRAS_EXCLUIDAS = [
    "estágio",
    "bolsa",
    "pesquisa",
    "extensão",
    "residência",
    "monitoria",
    "voluntário",
    "temporário sem vínculo",
    "curso",
    "capacitação"
]


INSTITUICOES_ESTADUAIS_FIXAS = [
    "secretaria de educação",
    "secretaria estadual de educação"
]

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

def detectar_cargo(texto):
    t = texto.lower()
    if any(p in t for p in ["professor","docente","pedagogo","educador","tutor"]):
        return "Professor"
    if any(p in t for p in ["administrativo","técnico administrativo","assistente"]):
        return "Administrativo"
    return "Educação"

def detectar_ambito_por_link(link: str | None) -> str | None:
    if not link:
        return None

    try:
        dominio = urlparse(link).netloc.lower()
    except:
        return None

    # FEDERAL
    if dominio.endswith("gov.br") or ".edu.br" in dominio:
        return "Federal"

    # ESTADUAL (ex: sp.gov.br, mg.gov.br)
    if dominio.count(".gov.br") == 2:
        return "Estadual"

    # MUNICIPAL
    if any(p in dominio for p in [
        "prefeitura",
        "municipio",
        "municipal"
    ]):
        return "Municipal"

    return None
def edital_relevante(texto: str) -> bool:
    t = texto.lower()

    if any(p in t for p in PALAVRAS_EXCLUIDAS):
        return False

    if any(p in t for p in PALAVRAS_VALIDAS):
        return True

    return False

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

    # 🔚 FALLBACK FINAL (PCI → Federal)
    return "Federal"

