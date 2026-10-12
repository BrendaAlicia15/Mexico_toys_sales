import os
import pandas as pd
import sqlite3

def cargar_y_limpiar_datos(path_data: str = "data", db_path: str = "mexico_toy_sales.db"):
    print("Iniciando proceso de carga y auditoría de datos...")
    
    # Validar existencia de la ruta de datos
    if not os.path.exists(path_data):
        print(f"[ADVERTENCIA] No se encuentra la carpeta '{path_data}'. Asegúrate de colocar ahí los archivos CSV.")
        return

    try:
        sales = pd.read_csv(os.path.join(path_data, "sales.csv"))
        products = pd.read_csv(os.path.join(path_data, "products.csv"))
        stores = pd.read_csv(os.path.join(path_data, "stores.csv"))
        inventory = pd.read_csv(os.path.join(path_data, "inventory.csv"))
    except FileNotFoundError as e:
        print(f"[ERROR] Falta algún archivo CSV requerido: {e}")
        return

    # Limpieza de columnas monetarias en products ($ y comas si las hubiera)
    for col in ['Product_Cost', 'Product_Price']:
        if col in products.columns and products[col].dtype == 'object':
            products[col] = products[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).astype(float)

    # Conversión de fechas
    sales['Date'] = pd.to_datetime(sales['Date'])
    stores['Store_Open_Date'] = pd.to_datetime(stores['Store_Open_Date'])

    # Auditoría de fechas exigida en el planteamiento
    min_date = sales['Date'].min()
    max_date = sales['Date'].max()
    print("==========================================")
    print(f"[AUDITORÍA DE FECHAS] Rango detectado en sales.csv:")
    print(f"  - Fecha Mínima: {min_date.strftime('%Y-%m-%d')}")
    print(f"  - Fecha Máxima: {max_date.strftime('%Y-%m-%d')}")
    print("==========================================")

    # Ingesta a base de datos SQLite
    conn = sqlite3.connect(db_path)
    sales.to_sql('sales', conn, if_exists='replace', index=False)
    products.to_sql('products', conn, if_exists='replace', index=False)
    stores.to_sql('stores', conn, if_exists='replace', index=False)
    inventory.to_sql('inventory', conn, if_exists='replace', index=False)
    conn.close()
    
    print(f"[ÉXITO] Datos limpios e integrados correctamente en la base de datos: {db_path}")

if __name__ == "__main__":
    cargar_y_limpiar_datos()