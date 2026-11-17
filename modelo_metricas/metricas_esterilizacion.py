"""
Modelo de métricas de esterilización de perros y gatos por comuna.

Pregunta de investigación:
    ¿Cuántos perros y gatos están esterilizados por comuna en la base de datos
    del Registro Nacional de Mascotas (RNAC, julio 2026)?

Uso:
    python metricas_esterilizacion.py                       # excluye fallecidos (por defecto)
    python metricas_esterilizacion.py --incluir-fallecidos
    python metricas_esterilizacion.py --excel "otra_base.xlsx"

Salidas (carpeta resultados/):
    metricas_esterilizacion.xlsx  -> hojas: Por comuna, Por región, Nacional, Calidad de datos
    metricas_por_comuna.csv
"""

from __future__ import annotations

import argparse
import math
import time
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
EXCEL_POR_DEFECTO = BASE_DIR.parent / "RNAC julio 2026.xlsx"
DIR_RESULTADOS = BASE_DIR / "resultados"
DIR_CACHE = BASE_DIR / "cache"

COLUMNAS_EXCEL = [
    "nombre", "especie", "raza", "sexo", "color", "patron", "fecha_nacimiento",
    "estado_reproductivo", "tipo_tenencia", "tipo_identificacion", "modo_de_obtencion",
    "razon_tenencia", "estado", "comunitario", "potencialmente_peligroso", "fecha_registro",
    "comuna", "Fecha de Fallecimiento", "descripcion",
]
COLUMNAS = ["especie", "estado_reproductivo", "tipo_tenencia", "estado", "comuna", "descripcion"]
HOJAS_EXCLUIDAS = {"léame primero"}
ESPECIES = ["Perro", "Gato"]
Z_95 = 1.959964


# ---------------------------------------------------------------- carga
def cargar_datos(ruta_excel: Path) -> pd.DataFrame:
    """Lee todas las hojas de datos del Excel y las une. Usa caché para no releer el Excel."""
    DIR_CACHE.mkdir(exist_ok=True)
    cache = DIR_CACHE / f"{ruta_excel.stem}.pkl"
    if cache.exists() and cache.stat().st_mtime >= ruta_excel.stat().st_mtime:
        print(f"Cargando caché {cache.name}")
        return pd.read_pickle(cache)

    hojas = [h for h in pd.ExcelFile(ruta_excel, engine="calamine").sheet_names
             if h.strip().lower() not in HOJAS_EXCLUIDAS]
    partes = []
    for hoja in hojas:
        t = time.time()
        df = pd.read_excel(ruta_excel, sheet_name=hoja, engine="calamine", dtype=str)
        if list(df.columns) != COLUMNAS_EXCEL:
            # Algunas hojas (p. ej. "SUR 2") traen encabezados genéricos "Column1..19":
            # se asignan los nombres por posición, tras verificar que el ancho coincide.
            if len(df.columns) != len(COLUMNAS_EXCEL):
                raise ValueError(f"Hoja '{hoja}': {len(df.columns)} columnas, se esperaban {len(COLUMNAS_EXCEL)}")
            print(f"  hoja '{hoja.strip()}': encabezados no estándar, se asignan por posición")
            df.columns = COLUMNAS_EXCEL
        # huella de la fila completa para detectar registros duplicados entre hojas
        df = df.apply(lambda s: s.str.strip())
        huella = pd.util.hash_pandas_object(df, index=False)
        df = df[COLUMNAS].copy()
        df["huella"] = huella.values
        df["hoja"] = hoja.strip()
        partes.append(df)
        print(f"  hoja '{hoja.strip()}': {len(df):,} filas ({time.time() - t:.0f}s)")

    datos = pd.concat(partes, ignore_index=True)
    for c in COLUMNAS + ["hoja"]:
        datos[c] = datos[c].astype("category")
    datos = datos.rename(columns={"descripcion": "region"})
    datos.to_pickle(cache)
    return datos


# ---------------------------------------------------------------- métricas
def ic_wilson(exitos: int, n: int, z: float = Z_95) -> tuple[float, float]:
    """Intervalo de confianza de Wilson (95 %) para una proporción."""
    if n == 0:
        return (math.nan, math.nan)
    p = exitos / n
    den = 1 + z**2 / n
    centro = (p + z**2 / (2 * n)) / den
    margen = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / den
    return (centro - margen, centro + margen)


def calcular_metricas(df: pd.DataFrame, nivel: list[str]) -> pd.DataFrame:
    """Para cada unidad (comuna, región o país) calcula totales, esterilizados, % e IC 95 %."""
    d = df.assign(esterilizado=(df["estado_reproductivo"] == "Esterilizado").astype(int))
    agrupar = nivel if nivel else (lambda _: "Chile")
    filas = []
    for clave, g in d.groupby(agrupar, observed=True):
        clave = clave if isinstance(clave, tuple) else (clave,)
        fila = dict(zip(nivel or ["pais"], clave))
        for esp in ESPECIES + ["Total"]:
            sub = g if esp == "Total" else g[g["especie"] == esp]
            n, e = len(sub), int(sub["esterilizado"].sum())
            lo, hi = ic_wilson(e, n)
            sufijo = esp.lower()
            fila[f"{sufijo}_registrados"] = n
            fila[f"{sufijo}_esterilizados"] = e
            fila[f"{sufijo}_enteros"] = n - e
            fila[f"{sufijo}_pct_esterilizados"] = round(100 * e / n, 2) if n else math.nan
            fila[f"{sufijo}_ic95_inf"] = round(100 * lo, 2) if n else math.nan
            fila[f"{sufijo}_ic95_sup"] = round(100 * hi, 2) if n else math.nan
        # esterilización en animales sin dueño (indicador de control poblacional)
        sd = g[g["tipo_tenencia"] == "Sin dueño"]
        fila["sin_dueno_registrados"] = len(sd)
        fila["sin_dueno_pct_esterilizados"] = round(100 * sd["esterilizado"].mean(), 2) if len(sd) else math.nan
        filas.append(fila)

    res = pd.DataFrame(filas).sort_values("total_registrados", ascending=False, ignore_index=True)
    res["confiable_n>=30"] = (res["perro_registrados"] >= 30) & (res["gato_registrados"] >= 30)
    return res


def calidad_de_datos(bruto: pd.DataFrame, usado: pd.DataFrame, incluir_fallecidos: bool) -> pd.DataFrame:
    filas = [
        ("Registros totales en el Excel", len(bruto)),
        ("Registros usados en las métricas", len(usado)),
        ("Fallecidos " + ("incluidos" if incluir_fallecidos else "excluidos"),
         int((bruto["estado"] == "Fallecido").sum())),
        ("Especie distinta de Perro/Gato (excluidos)", int((~bruto["especie"].isin(ESPECIES)).sum())),
        ("Estado reproductivo vacío o desconocido (excluidos)",
         int((~bruto["estado_reproductivo"].isin(["Esterilizado", "Entero"])).sum())),
        ("Comuna vacía (excluidos)", int(bruto["comuna"].isna().sum() + (bruto["comuna"] == "").sum())),
        ("Filas idénticas en las 19 columnas (posibles duplicados, NO excluidos)",
         int(bruto["huella"].duplicated().sum())),
        ("Comunas distintas", usado["comuna"].nunique()),
        ("Regiones distintas", usado["region"].nunique()),
    ]
    for estado, n in bruto["estado"].value_counts().items():
        filas.append((f"Estado del animal: {estado}", int(n)))
    return pd.DataFrame(filas, columns=["indicador", "valor"])


# ---------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--excel", type=Path, default=EXCEL_POR_DEFECTO)
    ap.add_argument("--incluir-fallecidos", action="store_true")
    args = ap.parse_args()

    t0 = time.time()
    print(f"Leyendo {args.excel.name} ...")
    bruto = cargar_datos(args.excel)

    usado = bruto[
        bruto["especie"].isin(ESPECIES)
        & bruto["estado_reproductivo"].isin(["Esterilizado", "Entero"])
        & bruto["comuna"].notna() & (bruto["comuna"] != "")
    ]
    if not args.incluir_fallecidos:
        usado = usado[usado["estado"] != "Fallecido"]

    por_comuna = calcular_metricas(usado, ["region", "comuna"])
    por_region = calcular_metricas(usado, ["region"])
    nacional = calcular_metricas(usado, [])
    calidad = calidad_de_datos(bruto, usado, args.incluir_fallecidos)

    DIR_RESULTADOS.mkdir(exist_ok=True)
    sufijo = "_con_fallecidos" if args.incluir_fallecidos else ""
    xlsx = DIR_RESULTADOS / f"metricas_esterilizacion{sufijo}.xlsx"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as w:
        por_comuna.to_excel(w, sheet_name="Por comuna", index=False)
        por_region.to_excel(w, sheet_name="Por región", index=False)
        nacional.to_excel(w, sheet_name="Nacional", index=False)
        calidad.to_excel(w, sheet_name="Calidad de datos", index=False)
        for ws in w.book.worksheets:
            ws.freeze_panes = "C2" if ws.title == "Por comuna" else "B2"
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = max(12, min(40, len(str(col[0].value)) + 2))
    por_comuna.to_csv(DIR_RESULTADOS / f"metricas_por_comuna{sufijo}.csv", index=False, encoding="utf-8-sig")

    n = nacional.iloc[0]
    print("\n=== Resumen nacional ===")
    for esp in ["perro", "gato", "total"]:
        print(f"{esp.capitalize():6}: {n[f'{esp}_esterilizados']:>10,} esterilizados de {n[f'{esp}_registrados']:>10,}"
              f"  ({n[f'{esp}_pct_esterilizados']:.1f} %)")
    print(f"Comunas: {len(por_comuna)} | Regiones: {len(por_region)}")
    print(calidad.to_string(index=False))
    print(f"\nResultados en {xlsx}  ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
