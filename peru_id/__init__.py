"""Validacion de identificadores peruanos (RUC, DNI, CCI, telefono) y datos de prueba ficticios.

Solo se implementa lo que se pudo verificar. Ver README para los limites.
"""
import csv
import random
import re
from importlib import resources

__version__ = "0.1.0"

_PESOS_RUC = (5, 4, 3, 2, 7, 6, 5, 4, 3, 2)
PREFIJOS_RUC = {"10": "persona natural", "15": "persona natural (no domiciliada)", "16": "persona natural (otro)",
                "17": "persona natural (otro)", "20": "persona juridica / entidad"}


def _solo_digitos(s) -> str:
    return re.sub(r"[\s.-]", "", str(s or ""))


# ---------------------------------------------------------------- RUC
def digito_ruc(diez: str) -> int:
    """Digito verificador SUNAT (modulo 11, pesos 5-4-3-2-7-6-5-4-3-2). Verificado contra 205,005 RUC reales."""
    s = sum(int(a) * b for a, b in zip(diez, _PESOS_RUC))
    d = 11 - (s % 11)
    return d % 10 if d >= 10 else d


def validar_ruc(ruc: str) -> dict:
    r = _solo_digitos(ruc)
    if not re.fullmatch(r"\d{11}", r):
        return {"valido": False, "ruc": r, "motivo": "Debe tener 11 digitos"}
    if r[:2] not in PREFIJOS_RUC:
        return {"valido": False, "ruc": r, "motivo": f"Prefijo {r[:2]} no usado en RUC (10, 15, 16, 17, 20)"}
    esperado = digito_ruc(r[:10])
    if esperado != int(r[10]):
        return {"valido": False, "ruc": r, "motivo": f"Digito verificador incorrecto (deberia ser {esperado})"}
    return {"valido": True, "ruc": r, "tipo": PREFIJOS_RUC[r[:2]],
            "nota": "Valida el formato y el digito verificador; no prueba que el RUC exista en SUNAT."}


def generar_ruc_prueba(n: int = 1, semilla=None) -> list:
    """RUC de empresa ficticios: prefijo 20 + '99' + 6 digitos al azar + digito verificador valido.

    El rango 209xxxxxxxx no existe en el Padron Reducido de SUNAT (6-oct-2026, 18.4 millones de RUC), pero SUNAT
    podria asignarlo en el futuro: son para pruebas de formato, no garantizan que no exista.
    """
    rnd = random.Random(semilla)
    out = []
    for _ in range(n):
        base = "2099" + "".join(rnd.choice("0123456789") for _ in range(6))
        out.append(base + str(digito_ruc(base)))
    return out


# ---------------------------------------------------------------- DNI
def validar_dni(dni: str) -> dict:
    d = _solo_digitos(dni)
    if not re.fullmatch(r"\d{8}", d):
        return {"valido": False, "dni": d, "motivo": "Debe tener 8 digitos"}
    return {"valido": True, "dni": d,
            "nota": "Solo se valida el formato (8 digitos). El digito de verificacion de RENIEC no se verifica: algoritmo no confirmado."}


# ---------------------------------------------------------------- CCI
def _bancos() -> dict:
    with resources.files("peru_id").joinpath("bancos.csv").open("r", encoding="utf-8", newline="") as f:
        return {r["codigo"]: r for r in csv.DictReader(f)}


def validar_cci(cci: str) -> dict:
    c = _solo_digitos(cci)
    if not re.fullmatch(r"\d{20}", c):
        return {"valido": False, "cci": c, "motivo": "Debe tener 20 digitos"}
    banco = _bancos().get(c[:3])
    out = {
        "valido": True, "cci": c,
        "entidad": {"codigo": c[:3], "nombre": banco["nombre"] if banco else None,
                    "verificado": bool(banco and banco["verificado"] == "si")},
        "oficina": c[3:6], "cuenta": c[6:18], "digitos_control": c[18:],
        "nota": "Solo se valida la estructura (20 digitos). Los 2 digitos de control no se verifican: algoritmo no confirmado.",
    }
    if banco is None:
        out["aviso"] = "Codigo de entidad no incluido en la tabla local (no implica que sea invalido)."
    elif banco["verificado"] != "si":
        out["aviso"] = "Nombre de la entidad tomado de una fuente secundaria; confirmar con el listado oficial del BCRP."
    return out


# ---------------------------------------------------------------- Telefono
def validar_telefono(tel: str) -> dict:
    t = re.sub(r"[\s().-]", "", str(tel or ""))
    t = re.sub(r"^(\+51|0051)", "", t)
    # "51" sin signo solo se quita si lo que queda es un movil (9...) o un fijo de Lima (1...);
    # si no, podria ser el prefijo 51 de Puno
    if re.fullmatch(r"519\d{8}", t) or re.fullmatch(r"511\d{7}", t):
        t = t[2:]
    if re.fullmatch(r"9\d{8}", t):
        return {"valido": True, "tipo": "movil", "numero": t, "internacional": "+51" + t}
    if re.fullmatch(r"0?1\d{7}", t):
        n = t.lstrip("0")
        return {"valido": True, "tipo": "fijo Lima", "numero": n, "internacional": "+51" + n}
    if re.fullmatch(r"0?[2-8]\d\d{6}", t):
        n = t.lstrip("0")
        return {"valido": True, "tipo": "fijo provincia", "numero": n, "internacional": "+51" + n,
                "nota": "Solo formato: prefijo de 2 digitos + 6; no se valida que el prefijo exista."}
    return {"valido": False, "numero": t,
            "motivo": "Formatos admitidos: movil 9 digitos que empieza en 9; fijo Lima 1 + 7 digitos; fijo provincia prefijo(2) + 6 digitos"}
