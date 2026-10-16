# peru-id

Valida **RUC, DNI, CCI y teléfonos** del Perú y genera **RUC ficticios** para pruebas. Sin dependencias.
Incluye el atajo `cci` para validar cuentas interbancarias y detectar el banco.

```console
$ peru-id ruc 20522088073 20522088074
20522088073: valido · persona juridica / entidad
20522088074: NO valido: Digito verificador incorrecto (deberia ser 3)

$ cci 018-123-123456789012-34
valido · entidad 018 = Banco de la Nacion · oficina 123, cuenta 123456789012, control 34

$ peru-id telefono "+51 987 654 321"
$ peru-id generar-ruc -n 3 --semilla 7     # RUC ficticios con digito verificador valido
$ peru-id --json ruc 20522088073
```

El código de salida es 0 si todo es válido y 1 si algo no lo es (útil en scripts).

## Instalar

```bash
pip install .                    # comandos `peru-id` y `cci`
python -m peru_id ruc 20522088073
python -m unittest discover -s tests -t .
```

## Qué está verificado y qué no

| Dato | Qué valida | Verificación |
|---|---|---|
| **RUC** | 11 dígitos, prefijo (10, 15, 16, 17, 20) y dígito verificador (módulo 11) | Probado contra **461,262 RUC reales** del Padrón Reducido de SUNAT: 0 rechazos |
| **DNI** | Solo el formato (8 dígitos) | El dígito de verificación de RENIEC **no se valida**: no se pudo confirmar el algoritmo |
| **CCI** | 20 dígitos y su estructura (entidad 3 · oficina 3 · cuenta 12 · control 2) | Los 2 dígitos de control **no se validan**: algoritmo no confirmado |
| **Banco emisor** | Tabla `peru_id/bancos.csv` | Solo el Banco de la Nación (018) está marcado como verificado. 002 y 003 vienen de fuentes secundarias; **009 y 011 están en disputa** entre fuentes (Scotiabank vs BBVA) y se muestran como tales. El listado oficial del BCRP no se pudo obtener (bloquea las descargas) |
| **Teléfono** | Formato: móvil de 9 dígitos que empieza en 9; fijo de Lima (1 + 7); fijo de provincia (prefijo + 6) | No comprueba que la línea exista ni que el prefijo provincial sea real |

Que un RUC, DNI o CCI "sea válido" significa que tiene formato y dígito correctos; **no prueba que exista ni que pertenezca a alguien**.

### Para completar la tabla de bancos
Si consigue el listado oficial de códigos de entidades del BCRP (o de la SBS/CCE), complete `peru_id/bancos.csv` marcando `verificado=si`. Las contribuciones con la fuente citada son bienvenidas.

## Datos de prueba

- `generar-ruc` produce RUC con el prefijo `2099…`. Ese rango **no existe** en el Padrón Reducido del 6-oct-2026, pero SUNAT podría asignarlo en el futuro: sirven para probar formatos, no garantizan inexistencia.
- **No hay generadores de DNI, CCI ni teléfonos** a propósito: no existe un rango del que se pueda asegurar que no pertenece a una persona real. Para pruebas, use valores claramente falsos o los de su propio entorno.
- No se validan placas vehiculares (los formatos vigentes no se pudieron confirmar).
