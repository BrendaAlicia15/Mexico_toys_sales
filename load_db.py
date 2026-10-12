"""
load_db.py - Carga los CSV de Mexico Toy Sales (Maven Analytics) a SQLite.

Uso:
    python load_db.py --data-dir data/raw --db data/toys.db

Qué hace:
  1. Busca los 4 CSV (products, stores, sales, inventory) por nombre de archivo.
  2. Normaliza nombres de columnas a minusculas_con_guion_bajo.
  3. Limpia columnas de dinero ("$9.99 " -> 9.99) y convierte fechas a ISO (YYYY-MM-DD).
  4. Crea la base SQLite con indices.
  5. Imprime un reporte de calidad de datos.

IMPORTANTE: los nombres de columna que usan las consultas SQL (sql/consultas_semana1.sql)
son los esperados del dataset. Este script imprime el esquema real: si algo
difiere, ajusta las consultas, no el script.
"""
import argparse
import re
import sqlite3
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    sys.exit("Falta pandas. Instalalo con: pip install pandas")

TABLAS = ["products", "stores", "sales", "inventory"]


def normalizar_columna(nombre: str) -> str:
    nombre = nombre.strip().lower()
    nombre = re.sub(r"[^a-z0-9]+", "_", nombre)
    return nombre.strip("_")


def encontrar_csv(data_dir: Path, tabla: str) -> Path:
    candidatos = [p for p in data_dir.glob("*.csv") if tabla in p.name.lower()]
    if not candidatos:
        sys.exit(f"No encontre un CSV para '{tabla}' en {data_dir}. "
                 f"Archivos presentes: {[p.name for p in data_dir.glob('*.csv')]}")
    return sorted(candidatos)[0]


def limpiar_dinero(serie: pd.Series) -> pd.Series:
    limpio = (serie.astype(str)
              .str.replace(r"[\$,\s]", "", regex=True)
              .replace({"": None, "nan": None}))
    return pd.to_numeric(limpio, errors="coerce")


def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [normalizar_columna(c) for c in df.columns]
    for col in df.columns:
        if any(k in col for k in ("cost", "price")) and not pd.api.types.is_numeric_dtype(df[col]):
            df[col] = limpiar_dinero(df[col])
        if "date" in col or col == "fecha":
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")
    return df


def reporte_calidad(con: sqlite3.Connection) -> None:
    print("\n=== REPORTE DE CALIDAD ===")
    for t in TABLAS:
        n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        cols = [r[1] for r in con.execute(f"PRAGMA table_info({t})")]
        print(f"\n[{t}] {n:,} filas | columnas: {cols}")
        for c in cols:
            nulos = con.execute(f"SELECT COUNT(*) FROM {t} WHERE {c} IS NULL").fetchone()[0]
            if nulos:
                print(f"   - {c}: {nulos:,} nulos")

    cols_sales = [r[1] for r in con.execute("PRAGMA table_info(sales)")]
    col_fecha = next((c for c in cols_sales if "date" in c), None)
    if col_fecha:
        mn, mx = con.execute(f"SELECT MIN({col_fecha}), MAX({col_fecha}) FROM sales").fetchone()
        print(f"\nRango de fechas en sales: {mn} a {mx}   <-- documentalo en tu README")

    checks = {
        "ventas con product_id inexistente":
            "SELECT COUNT(*) FROM sales s LEFT JOIN products p USING(product_id) WHERE p.product_id IS NULL",
        "ventas con store_id inexistente":
            "SELECT COUNT(*) FROM sales s LEFT JOIN stores t USING(store_id) WHERE t.store_id IS NULL",
        "inventario con product_id inexistente":
            "SELECT COUNT(*) FROM inventory i LEFT JOIN products p USING(product_id) WHERE p.product_id IS NULL",
        "productos sin ninguna venta":
            "SELECT COUNT(*) FROM products p WHERE p.product_id NOT IN (SELECT DISTINCT product_id FROM sales)",
    }
    print("\nIntegridad referencial:")
    for nombre, q in checks.items():
        try:
            print(f"   - {nombre}: {con.execute(q).fetchone()[0]:,}")
        except sqlite3.Error as e:
            print(f"   - {nombre}: no se pudo evaluar ({e})")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data/raw")
    ap.add_argument("--db", default="data/toys.db")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(args.db)

    for tabla in TABLAS:
        ruta = encontrar_csv(data_dir, tabla)
        df = limpiar(pd.read_csv(ruta))
        df.to_sql(tabla, con, if_exists="replace", index=False)
        print(f"Cargada {tabla:<10} <- {ruta.name} ({len(df):,} filas)")

    for t, c in [("sales", "store_id"), ("sales", "product_id"),
                 ("inventory", "store_id"), ("inventory", "product_id"),
                 ("products", "product_id"), ("stores", "store_id")]:
        try:
            con.execute(f"CREATE INDEX IF NOT EXISTS idx_{t}_{c} ON {t}({c})")
        except sqlite3.Error:
            pass
    con.commit()

    reporte_calidad(con)
    con.close()
    print(f"\nListo. Base creada en {args.db}")


if __name__ == "__main__":
    main()
