import sqlite3
import pandas as pd
import os

def ejecutar_eda():
    db_path = os.path.join("data", "toys.db")
    
    if not os.path.exists(db_path):
        print(f"Error: No se encontró la base de datos en {db_path}. Ejecuta primero el script de carga.")
        return

    print("Conectando a la base de datos para el Análisis Exploratorio (EDA)...\n")
    conn = sqlite3.connect(db_path)

    # 1. Resumen general de ventas
    query_resumen = """
    SELECT 
        COUNT(s.sale_id) as total_transacciones,
        SUM(s.units) as total_unidades_vendidas,
        MIN(s.date) as fecha_minima,
        MAX(s.date) as fecha_maxima
    FROM sales s
    """
    df_resumen = pd.read_sql(query_resumen, conn)
    print("--- [RESUMEN GENERAL DE VENTAS] ---")
    print(df_resumen.to_string(index=False))
    print("\n" + "="*50 + "\n")

    # 2. Top 5 Categorías de productos más rentables o vendidas
    query_categorias = """
    SELECT 
        p.product_category,
        SUM(s.units) as unidades_vendidas
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY p.product_category
    ORDER BY unidades_vendidas DESC
    """
    df_categorias = pd.read_sql(query_categorias, conn)
    print("--- [VENTAS POR CATEGORÍA DE PRODUCTO] ---")
    print(df_categorias.to_string(index=False))
    print("\n" + "="*50 + "\n")

    # 3. Top 5 Tiendas por volumen de unidades vendidas
    query_tiendas = """
    SELECT 
        st.store_name,
        st.store_city,
        st.store_location,
        SUM(s.units) as unidades_totales
    FROM sales s
    JOIN stores st ON s.store_id = st.store_id
    GROUP BY st.store_id, st.store_name, st.store_city, st.store_location
    ORDER BY unidades_totales DESC
    LIMIT 5
    """
    df_tiendas = pd.read_sql(query_tiendas, conn)
    print("--- [TOP 5 TIENDAS CON MAYOR VOLUMEN] ---")
    print(df_tiendas.to_string(index=False))
    print("\n" + "="*50 + "\n")

    conn.close()
    print("¡EDA inicial completado con éxito!")

if __name__ == "__main__":
    ejecutar_eda()