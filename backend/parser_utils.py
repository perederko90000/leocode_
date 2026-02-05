import re

ESTADOS = {
    "AC":"Acre","AL":"Alagoas","AP":"Amapá","AM":"Amazonas","BA":"Bahia",
    "CE":"Ceará","DF":"Distrito Federal","ES":"Espírito Santo","GO":"Goiás",
    "MA":"Maranhão","MT":"Mato Grosso","MS":"Mato Grosso do Sul","MG":"Minas Gerais",
    "PA":"Pará","PB":"Paraíba","PR":"Paraná","PE":"Pernambuco","PI":"Piauí",
    "RJ":"Rio de Janeiro","RN":"Rio Grande do Norte","RS":"Rio Grande do Sul",
    "RO":"Rondônia","RR":"Roraima","SC":"Santa Catarina","SP":"São Paulo",
    "SE":"Sergipe","TO":"Tocantins"
}

def extrair_salario(texto):
    valores = re.findall(r"R\$ ?[\d\.]+,\d{2}", texto)
    if valores:
        return valores[0]
    return "Não informado"

def extrair_carga(texto):
    cargas = re.findall(r"(20|30|40)\s?h", texto)
    if cargas:
        return f"{cargas[0]}h"
    return "Não informado"

def extrair_local(texto):
    texto = texto.upper()
    for uf, nome in ESTADOS.items():
        if uf in texto or nome.upper() in texto:
            return f"{nome} ({uf})"
    return "Não informado"