import argparse
import json
import sys

from . import (__version__, generar_ruc_prueba, validar_cci, validar_dni, validar_ruc, validar_telefono)

VALIDADORES = {"ruc": validar_ruc, "dni": validar_dni, "cci": validar_cci, "telefono": validar_telefono}


def _texto(r: dict) -> str:
    if not r["valido"]:
        return "NO valido: " + r["motivo"]
    partes = ["valido"]
    if "tipo" in r:
        partes.append(r["tipo"])
    if "entidad" in r:
        e = r["entidad"]
        partes.append(f'entidad {e["codigo"]}' + (f' = {e["nombre"]}' if e["nombre"] else " (desconocida)"))
        partes.append(f'oficina {r["oficina"]}, cuenta {r["cuenta"]}, control {r["digitos_control"]}')
    txt = " · ".join(partes)
    for k in ("aviso", "nota"):
        if r.get(k):
            txt += f"\n  {k}: {r[k]}"
    return txt


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="peru-id", description="Valida RUC, DNI, CCI y telefonos del Peru; genera RUC de prueba.")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--version", action="version", version=f"peru-id {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for nombre in VALIDADORES:
        p = sub.add_parser(nombre, help=f"valida un {nombre} (exit 0 si es valido)")
        p.add_argument("valor", nargs="+")
    g = sub.add_parser("generar-ruc", help="RUC de empresa ficticios para pruebas (digito verificador valido)")
    g.add_argument("-n", type=int, default=5)
    g.add_argument("--semilla", type=int)
    a = ap.parse_args(argv)

    if a.cmd == "generar-ruc":
        rucs = generar_ruc_prueba(a.n, a.semilla)
        print(json.dumps(rucs) if a.json else "\n".join(rucs))
        return 0
    resultados = [VALIDADORES[a.cmd](v) for v in a.valor]
    if a.json:
        print(json.dumps(resultados if len(resultados) > 1 else resultados[0], ensure_ascii=False, indent=2))
    else:
        for v, r in zip(a.valor, resultados):
            print(f"{v}: {_texto(r)}")
    return 0 if all(r["valido"] for r in resultados) else 1


def main_cci(argv=None) -> int:
    """Atajo: `cci <numero>` equivale a `peru-id cci <numero>`."""
    return main(["cci"] + list(sys.argv[1:] if argv is None else argv))


if __name__ == "__main__":
    sys.exit(main())
