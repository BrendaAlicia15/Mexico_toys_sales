import sqlite3
import pandas as pd
import os

def ejecutar_estacionalidad():
    db_path = os.path.join("data", "toys.db")
    
    if not os.path.exists(db_path):
        print(f"Error: No se encontró la base de datos en {db_path}.")
        return

    print("Analizando la estacionalidad y tendencias mensuales...\n")
    conn = sqlite3.connect(db_path)

    # 1. Ventas y rendimiento financiero agrupado por Año y Mes
    query_mensual = """
    SELECT 
        strftime('%Y-%m', s.date) as anio_mes,
        SUM(s.units) as unidades_vendidas,
        ROUND(SUM(s.units * p.product_price), 2) as ingresos,
        ROUND(SUM(s.units * (p.product_price - p.product_cost)), 2) as ganancias
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY anio_mes
    ORDER BY anio_mes ASC
    """
    df_mensual = pd.read_sql(query_mensual, conn)
    
    print("--- [TENDENCIA MENSUAL DE VENTAS (2022 - 2023)] ---")
    print(df_mensual.to_string(index=False))
    print("\n" + "="*60 + "\n")

    # 2. Identificar los 3 meses con mayores ingresos históricos
    query_top_meses = """
    SELECT 
        strftime('%Y-%m', s.date) as anio_mes,
        ROUND(SUM(s.units * p.product_price), 2) as ingresos
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY anio_mes
    ORDER BY ingresos DESC
    LIMIT 3
    """
    df_top_meses = pd.read_sql(query_top_meses, conn)
    print("--- [TOP 3 MESES CON MAYOR FACTURACIÓN HISTÓRICA] ---")
    print(df_top_meses.to_string(index=False))
    print("\n" + "="*60 + "\n")

    conn.close()
    print("¡Análisis de estacionalidad completado con éxito!")

if __name__ == "__main__":
    ejecutar_estacionalidad()