import sqlite3
import pandas as pd
import os

def ejecutar_eda_financiero():
    db_path = os.path.join("data", "toys.db")
    
    if not os.path.exists(db_path):
        print(f"Error: No se encontró la base de datos en {db_path}.")
        return

    print("Conectando a la base de datos para el Análisis Financiero...\n")
    conn = sqlite3.connect(db_path)

    # 1. Métricas financieras globales (Ingresos y Ganancias totales)
    query_global = """
    SELECT 
        SUM(s.units) as total_unidades,
        SUM(s.units * p.product_price) as ingresos_totales,
        SUM(s.units * (p.product_price - p.product_cost)) as ganancia_total,
        ROUND((SUM(s.units * (p.product_price - p.product_cost)) / SUM(s.units * p.product_price)) * 100, 2) as margen_ganancia_pct
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    """
    df_global = pd.read_sql(query_global, conn)
    print("--- [RESUMEN FINANCIERO GLOBAL] ---")
    print(df_global.to_string(index=False))
    print("\n" + "="*60 + "\n")

    # 2. Rendimiento Financiero por Categoría de Producto
    query_cat_fin = """
    SELECT 
        p.product_category,
        SUM(s.units) as unidades_vendidas,
        ROUND(SUM(s.units * p.product_price), 2) as ingresos,
        ROUND(SUM(s.units * (p.product_price - p.product_cost)), 2) as ganancias
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY p.product_category
    ORDER BY ingresos DESC
    """
    df_cat_fin = pd.read_sql(query_cat_fin, conn)
    print("--- [RENDIMIENTO FINANCIERO POR CATEGORÍA] ---")
    print(df_cat_fin.to_string(index=False))
    print("\n" + "="*60 + "\n")

    # 3. Top 5 Tiendas con mayores Ingresos y Ganancias
    query_tiendas_fin = """
    SELECT 
        st.store_name,
        st.store_city,
        ROUND(SUM(s.units * p.product_price), 2) as ingresos,
        ROUND(SUM(s.units * (p.product_price - p.product_cost)), 2) as ganancias
    FROM sales s
    JOIN stores st ON s.store_id = st.store_id
    JOIN products p ON s.product_id = p.product_id
    GROUP BY st.store_id, st.store_name, st.store_city
    ORDER BY ingresos DESC
    LIMIT 5
    """
    df_tiendas_fin = pd.read_sql(query_tiendas_fin, conn)
    print("--- [TOP 5 TIENDAS POR INGRESOS Y GANANCIAS] ---")
    print(df_tiendas_fin.to_string(index=False))
    print("\n" + "="*60 + "\n")

    conn.close()
    print("¡Análisis financiero completado con éxito!")

if __name__ == "__main__":
    ejecutar_financiero = ejecutar_eda_financiero()