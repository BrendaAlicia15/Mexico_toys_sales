-- =====================================================================
-- PROYECTO: Mexico Toy Sales
-- DESCRIPCIÓN: Repositorio central de consultas SQL (Semanas 1 y 2)
-- =====================================================================

-- ---------------------------------------------------------------------
-- PARTE 1: AUDITORÍA E INTEGRIDAD DE DATOS (Semana 1)
-- ---------------------------------------------------------------------

-- 1. Validación de rangos de fechas en ventas
SELECT 
    MIN(date) as fecha_minima, 
    MAX(date) as fecha_maxima 
FROM sales;

-- 2. Conteo total de registros por tabla para auditoría inicial
SELECT 'sales' as tabla, COUNT(*) as total FROM sales
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'stores', COUNT(*) FROM stores;


-- ---------------------------------------------------------------------
-- PARTE 2: ANÁLISIS EXPLORATORIO Y MÉTRICAS FINANCIERAS (Semana 2)
-- ---------------------------------------------------------------------

-- 1. Resumen general de ventas y finanzas globales
SELECT 
    COUNT(s.sale_id) as total_transacciones,
    SUM(s.units) as total_unidades_vendidas,
    ROUND(SUM(s.units * p.product_price), 2) as ingresos_totales,
    ROUND(SUM(s.units * (p.product_price - p.product_cost)), 2) as ganancia_total,
    ROUND((SUM(s.units * (p.product_price - p.product_cost)) / SUM(s.units * p.product_price)) * 100, 2) as margen_ganancia_pct
FROM sales s
JOIN products p ON s.product_id = p.product_id;

-- 2. Rendimiento financiero por categoría de producto
SELECT 
    p.product_category,
    SUM(s.units) as unidades_vendidas,
    ROUND(SUM(s.units * p.product_price), 2) as ingresos,
    ROUND(SUM(s.units * (p.product_price - p.product_cost)), 2) as ganancias,
    ROUND((SUM(s.units * (p.product_price - p.product_cost)) / SUM(s.units * p.product_price)) * 100, 2) as margen_pct
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.product_category
ORDER BY ingresos DESC;

-- 3. Top 5 tiendas por ingresos y ganancias
SELECT 
    st.store_name,
    st.store_city,
    st.store_location,
    SUM(s.units) as unidades_totales,
    ROUND(SUM(s.units * p.product_price), 2) as ingresos,
    ROUND(SUM(s.units * (p.product_price - p.product_cost)), 2) as ganancias
FROM sales s
JOIN stores st ON s.store_id = st.store_id
JOIN products p ON s.product_id = p.product_id
GROUP BY st.store_id, st.store_name, st.store_city, st.store_location
ORDER BY ingresos DESC
LIMIT 5;

-- 4. Tendencia y estacionalidad mensual (2022 - 2023)
SELECT 
    strftime('%Y-%m', s.date) as anio_mes,
    SUM(s.units) as unidades_vendidas,
    ROUND(SUM(s.units * p.product_price), 2) as ingresos,
    ROUND(SUM(s.units * (p.product_price - p.product_cost)), 2) as ganancias
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY anio_mes
ORDER BY anio_mes ASC;

-- =====================================================================
-- PARTE 3: SEGMENTACIÓN Y RENDIMIENTO CRÍTICO (Semana 3)
-- =====================================================================

-- 1. Tiendas con ingresos por debajo del promedio general
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

-- 2. Productos con menor rendimiento en ventas e ingresos (Bottom 10)
SELECT 
    p.product_id,
    p.product_name,
    p.product_category,
    SUM(s.units) as total_unidades_vendidas,
    ROUND(SUM(s.units * p.product_price), 2) as ingresos_totales,
    ROUND(SUM(s.units * (p.product_price - p.product_cost)), 2) as ganancia_total
FROM sales s
RIGHT JOIN products p ON s.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.product_category
ORDER BY ingresos_totales ASC
LIMIT 10;
