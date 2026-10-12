-- =====================================================================
-- Mexico Toy Sales - Consultas Semana 1
-- Motor: SQLite 3.25+ (soporta window functions)
--
-- Columnas esperadas (confirmalas con el reporte de load_db.py):
--   products(product_id, product_name, product_category, product_cost, product_price)
--   stores(store_id, store_name, store_city, store_location, store_open_date)
--   sales(sale_id, date, store_id, product_id, units)
--   inventory(store_id, product_id, stock_on_hand)
-- Si un nombre difiere, reemplazalo aqui.
-- =====================================================================


-- ---------------------------------------------------------------------
-- Q1. Resumen general: periodo, volumen, ingreso y utilidad totales
-- Pregunta: ¿De que tamano es el negocio y que periodo cubren los datos?
-- ---------------------------------------------------------------------
SELECT
    MIN(s.date)                                         AS primera_venta,
    MAX(s.date)                                         AS ultima_venta,
    COUNT(*)                                            AS transacciones,
    SUM(s.units)                                        AS unidades,
    ROUND(SUM(s.units * p.product_price), 2)            AS ingreso,
    ROUND(SUM(s.units * (p.product_price - p.product_cost)), 2) AS utilidad,
    ROUND(100.0 * SUM(s.units * (p.product_price - p.product_cost))
          / SUM(s.units * p.product_price), 1)          AS margen_pct
FROM sales s
JOIN products p USING (product_id);


-- ---------------------------------------------------------------------
-- Q2. Ingreso, utilidad y margen por categoria
-- Pregunta: ¿Que categorias generan mas utilidad? (pregunta oficial #1)
-- Ojo: la categoria con mas ingreso no siempre es la de mas utilidad.
-- ---------------------------------------------------------------------
SELECT
    p.product_category                                  AS categoria,
    SUM(s.units)                                        AS unidades,
    ROUND(SUM(s.units * p.product_price), 2)            AS ingreso,
    ROUND(SUM(s.units * (p.product_price - p.product_cost)), 2) AS utilidad,
    ROUND(100.0 * SUM(s.units * (p.product_price - p.product_cost))
          / SUM(s.units * p.product_price), 1)          AS margen_pct,
    ROUND(100.0 * SUM(s.units * (p.product_price - p.product_cost))
          / SUM(SUM(s.units * (p.product_price - p.product_cost))) OVER (), 1) AS pct_de_utilidad_total
FROM sales s
JOIN products p USING (product_id)
GROUP BY p.product_category
ORDER BY utilidad DESC;


-- ---------------------------------------------------------------------
-- Q3. Rendimiento por tipo de ubicacion (normalizado por # de tiendas)
-- Pregunta: ¿Que tipo de ubicacion conviene replicar? (base para expansion)
-- Comparar utilidad POR TIENDA, no total: si no, gana quien tiene mas tiendas.
-- ---------------------------------------------------------------------
WITH utilidad_tienda AS (
    SELECT
        t.store_id,
        t.store_location,
        SUM(s.units * (p.product_price - p.product_cost)) AS utilidad
    FROM sales s
    JOIN products p USING (product_id)
    JOIN stores   t USING (store_id)
    GROUP BY t.store_id, t.store_location
)
SELECT
    store_location                                      AS tipo_ubicacion,
    COUNT(*)                                            AS num_tiendas,
    ROUND(SUM(utilidad), 2)                             AS utilidad_total,
    ROUND(AVG(utilidad), 2)                             AS utilidad_por_tienda
FROM utilidad_tienda
GROUP BY store_location
ORDER BY utilidad_por_tienda DESC;


-- ---------------------------------------------------------------------
-- Q4. Top 3 productos por utilidad en cada tienda (RANK + CTE)
-- Pregunta: ¿Son los mismos productos estrella en todas las tiendas?
-- ---------------------------------------------------------------------
WITH utilidad_prod_tienda AS (
    SELECT
        s.store_id,
        s.product_id,
        SUM(s.units * (p.product_price - p.product_cost)) AS utilidad
    FROM sales s
    JOIN products p USING (product_id)
    GROUP BY s.store_id, s.product_id
),
ranking AS (
    SELECT
        store_id, product_id, utilidad,
        RANK() OVER (PARTITION BY store_id ORDER BY utilidad DESC) AS pos
    FROM utilidad_prod_tienda
)
SELECT
    t.store_name, r.pos, p.product_name, p.product_category,
    ROUND(r.utilidad, 2) AS utilidad
FROM ranking r
JOIN stores   t USING (store_id)
JOIN products p USING (product_id)
WHERE r.pos <= 3
ORDER BY t.store_name, r.pos;


-- ---------------------------------------------------------------------
-- Q5. Crecimiento mensual de utilidad (LAG)
-- Pregunta: ¿El negocio crece o se estanca? Ojo con meses incompletos
-- al inicio o al final del periodo: pueden distorsionar el crecimiento.
-- ---------------------------------------------------------------------
WITH mensual AS (
    SELECT
        strftime('%Y-%m', s.date)                       AS mes,
        SUM(s.units * (p.product_price - p.product_cost)) AS utilidad
    FROM sales s
    JOIN products p USING (product_id)
    GROUP BY strftime('%Y-%m', s.date)
)
SELECT
    mes,
    ROUND(utilidad, 2)                                  AS utilidad,
    ROUND(LAG(utilidad) OVER (ORDER BY mes), 2)         AS utilidad_mes_previo,
    ROUND(100.0 * (utilidad - LAG(utilidad) OVER (ORDER BY mes))
          / LAG(utilidad) OVER (ORDER BY mes), 1)       AS crecimiento_pct
FROM mensual
ORDER BY mes;


-- ---------------------------------------------------------------------
-- Q6. Utilidad acumulada por categoria a lo largo del tiempo
-- Pregunta: ¿Alguna categoria esta ganando terreno? (ventana acumulada)
-- ---------------------------------------------------------------------
WITH mensual_cat AS (
    SELECT
        strftime('%Y-%m', s.date)                       AS mes,
        p.product_category                              AS categoria,
        SUM(s.units * (p.product_price - p.product_cost)) AS utilidad
    FROM sales s
    JOIN products p USING (product_id)
    GROUP BY mes, categoria
)
SELECT
    mes, categoria,
    ROUND(utilidad, 2) AS utilidad_mes,
    ROUND(SUM(utilidad) OVER (PARTITION BY categoria ORDER BY mes), 2) AS utilidad_acumulada
FROM mensual_cat
ORDER BY categoria, mes;


-- ---------------------------------------------------------------------
-- Q7. Estacionalidad: utilidad promedio por mes del ano
-- Pregunta: ¿Hay temporada alta? (pregunta oficial #2)
-- Si hay mas de un ano de datos, el promedio por mes evita sesgo.
-- ---------------------------------------------------------------------
WITH mes_anio AS (
    SELECT
        strftime('%Y', s.date) AS anio,
        strftime('%m', s.date) AS mes,
        SUM(s.units * (p.product_price - p.product_cost)) AS utilidad
    FROM sales s
    JOIN products p USING (product_id)
    GROUP BY anio, mes
)
SELECT
    mes,
    COUNT(*)                         AS anios_con_datos,
    ROUND(AVG(utilidad), 2)          AS utilidad_promedio
FROM mes_anio
GROUP BY mes
ORDER BY mes;


-- ---------------------------------------------------------------------
-- Q8. Pareto de productos: ¿cuantos productos explican el 80% de la utilidad?
-- Tecnica: utilidad acumulada con window function sobre ranking.
-- ---------------------------------------------------------------------
WITH util_prod AS (
    SELECT
        p.product_name,
        p.product_category,
        SUM(s.units * (p.product_price - p.product_cost)) AS utilidad
    FROM sales s
    JOIN products p USING (product_id)
    GROUP BY p.product_id, p.product_name, p.product_category
)
SELECT
    product_name, product_category,
    ROUND(utilidad, 2) AS utilidad,
    ROUND(100.0 * SUM(utilidad) OVER (ORDER BY utilidad DESC)
          / SUM(utilidad) OVER (), 1) AS pct_acumulado
FROM util_prod
ORDER BY utilidad DESC;


-- ---------------------------------------------------------------------
-- Q9. Capital inmovilizado en inventario (valuado a costo) por categoria
-- Pregunta: ¿Cuanto dinero hay parado en inventario? (pregunta oficial #4)
-- ---------------------------------------------------------------------
SELECT
    p.product_category                                  AS categoria,
    SUM(i.stock_on_hand)                                AS unidades_en_stock,
    ROUND(SUM(i.stock_on_hand * p.product_cost), 2)     AS valor_inventario_a_costo
FROM inventory i
JOIN products p USING (product_id)
GROUP BY p.product_category
ORDER BY valor_inventario_a_costo DESC;


-- ---------------------------------------------------------------------
-- Q10. Cobertura de inventario en dias, por tienda y producto
-- cobertura = stock actual / venta diaria promedio de los ultimos 90 dias
-- Pregunta: ¿Donde hay riesgo de faltante (cobertura baja) o exceso (alta)?
-- Aproximacion: el inventario es una sola foto, no un historial.
-- Los 90 dias se cuentan hacia atras desde la ultima fecha de venta.
-- ---------------------------------------------------------------------
WITH fin AS (
    SELECT MAX(date) AS ultima FROM sales
),
venta_reciente AS (
    SELECT
        s.store_id, s.product_id,
        SUM(s.units) / 90.0 AS venta_diaria
    FROM sales s, fin
    WHERE s.date > date(fin.ultima, '-90 day')
    GROUP BY s.store_id, s.product_id
)
SELECT
    t.store_name, p.product_name, p.product_category,
    i.stock_on_hand,
    ROUND(v.venta_diaria, 2) AS venta_diaria,
    CASE
        WHEN COALESCE(v.venta_diaria, 0) = 0 THEN NULL
        ELSE ROUND(i.stock_on_hand / v.venta_diaria, 1)
    END AS cobertura_dias,
    CASE
        WHEN i.stock_on_hand = 0 AND COALESCE(v.venta_diaria, 0) > 0 THEN 'FALTANTE'
        WHEN COALESCE(v.venta_diaria, 0) = 0 AND i.stock_on_hand > 0   THEN 'SIN ROTACION'
        WHEN i.stock_on_hand / v.venta_diaria < 7                      THEN 'RIESGO (<7 dias)'
        WHEN i.stock_on_hand / v.venta_diaria > 90                     THEN 'EXCESO (>90 dias)'
        ELSE 'OK'
    END AS estado
FROM inventory i
JOIN products p USING (product_id)
JOIN stores   t USING (store_id)
LEFT JOIN venta_reciente v USING (store_id, product_id)
ORDER BY
    CASE estado
        WHEN 'FALTANTE' THEN 1 WHEN 'RIESGO (<7 dias)' THEN 2
        WHEN 'EXCESO (>90 dias)' THEN 3 WHEN 'SIN ROTACION' THEN 4 ELSE 5 END,
    cobertura_dias;
