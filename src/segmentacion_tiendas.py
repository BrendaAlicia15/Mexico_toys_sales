import sqlite3
import pandas as pd

def ejecutar_segmentacion():
    # Conexión a la base de datos SQLite
    conn = sqlite3.connect('data/Mexico_toy_sales.db')
    
    print("==================================================")
    print("ANÁLISIS DE SEGMENTACIÓN Y RENDIMIENTO (SEMANA 3)")
    print("==================================================\n")
    
    # 1. Tiendas con ingresos por debajo del promedio general
    query_tiendas = """
    WITH IngresosPorTienda AS (
        SELECT 
            st.store_id,
            st.store_name,
            st.store_city,
            st.store_location,
            ROUND(SUM(s.units * p.product_price), 2) as ingresos_totales
        FROM sales s
        JOIN stores st ON s.store_id = st.store_id
        JOIN products p ON s.product_id = p.product_id
        GROUP BY st.store_id, st.store_name, st.store_city, st.store_location
    ),
    PromedioGeneral AS (
        SELECT AVG(ingresos_totales) as promedio_ingresos FROM IngresosPorTienda
    )
    SELECT 
        i.store_id,
        i.store_name,
        i.store_city,
        i.store_location,
        i.ingresos_totales,
        ROUND(p.promedio_ingresos, 2) as promedio_general,
        ROUND(i.ingresos_totales - p.promedio_ingresos, 2) as diferencia_vs_promedio
    FROM IngresosPorTienda i
    CROSS JOIN PromedioGeneral p
    WHERE i.ingresos_totales < p.promedio_ingresos
    ORDER BY ingresos_totales ASC;
    """
    
    df_tiendas = pd.read_sql_query(query_tiendas, conn)
    print("--- TIENDAS CON RENDIMIENTO POR DEBAJO DEL PROMEDIO ---")
    print(df_tiendas.to_string(index=False))
    print("\n" + "-"*50 + "\n")
    
    # 2. Productos con menor rendimiento (Bottom 10)
    query_productos = """
    SELECT 
        p.product_id,
        p.product_name,
        p.product_category,
        SUM(s.units) as total_unidades_vendidas,
        ROUND(SUM(s.units * p.product_price), 2) as ingresos_totales
    FROM sales s
    RIGHT JOIN products p ON s.product_id = p.product_id
    GROUP BY p.product_id, p.product_name, p.product_category
    ORDER BY ingresos_totales ASC
    LIMIT 10;
    """
    
    df_productos = pd.read_sql_query(query_productos, conn)
    print("--- TOP 10 PRODUCTOS CON MENOR RENDIMIENTO (CRÍTICOS) ---")
    print(df_productos.to_string(index=False))
    print("\n==================================================")
    
    conn.close()

if __name__ == "__main__":
    ejecutar_segmentacion()