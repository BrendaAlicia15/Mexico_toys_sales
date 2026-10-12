# Semana 1: Datos y SQL (Mexico Toy Sales)

## Pasos

1. Descarga el dataset (gratis, dominio público):
   https://mavenanalytics.io/data-playground/mexico-toy-sales
2. Descomprime los 4 CSV en `data/raw/` (products, stores, sales, inventory).
3. Instala pandas: `pip install pandas`
4. Crea la base: `python load_db.py --data-dir data/raw --db data/toys.db`
5. Lee el **reporte de calidad** que imprime el script.
6. Abre `data/toys.db` en DB Browser for SQLite (gratis) o desde Python y ejecuta
   las consultas de `sql/consultas_semana1.sql` una por una.

## Antes de ejecutar las consultas

Las consultas asumen estos nombres de columna (los esperados del dataset):

- products: product_id, product_name, product_category, product_cost, product_price
- stores: store_id, store_name, store_city, store_location, store_open_date
- sales: sale_id, date, store_id, product_id, units
- inventory: store_id, product_id, stock_on_hand

El reporte te muestra los nombres reales. Si alguno difiere, reemplázalo en el `.sql`.
Los scripts se probaron con datos sintéticos de esta misma estructura, no con el
archivo original.

## Tareas de la semana (entregables)

- [ ] Base SQLite creada y reporte de calidad guardado en `reports/calidad_datos.md`
- [ ] Rango de fechas real documentado (las fuentes no coinciden entre sí)
- [ ] Las 10 consultas ejecutadas, con 2 o 3 hallazgos escritos en lenguaje de negocio
- [ ] Una consulta propia nueva (por ejemplo, ticket promedio por tipo de ubicación)
- [ ] Primer commit en GitHub con mensaje descriptivo

## Qué mirar en cada consulta

| Consulta | Pregunta | Ojo con |
|---|---|---|
| Q2 | Categoría con más utilidad | Ingreso alto no es igual a utilidad alta |
| Q3 | Mejor tipo de ubicación | Comparar por tienda, no el total |
| Q5 | Crecimiento mensual | Meses incompletos al inicio o fin |
| Q7 | Estacionalidad | Con un solo año por mes, el patrón puede ser coincidencia |
| Q10 | Cobertura de inventario | El inventario es una foto de un solo día |
