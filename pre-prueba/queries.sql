
-- SEPARADOR
-- 1. Ventas y órdenes por mes
SELECT 
    t.anio, t.mes, 
    SUM(f.amount) AS total_revenue, 
    COUNT(DISTINCT f.order_id) AS total_ordenes
FROM dw_fact_ventas f
JOIN dw_dim_tiempo t ON f.id_tiempo = t.id_tiempo
GROUP BY t.anio, t.mes
ORDER BY t.anio DESC, t.mes DESC;

-- SEPARADOR
-- 2. SKUs con ventas superiores al promedio (CTE)
WITH PromedioHistorico AS (
    SELECT id_producto, AVG(amount) AS avg_mensual
    FROM (SELECT id_producto, id_tiempo, sum(amount) as amount 
        FROM dw_fact_ventas 
        GROUP BY id_producto, id_tiempo) sub
    GROUP BY id_producto
),
UltimoMes AS (
    SELECT f.id_producto, SUM(f.amount) AS ventas_mes
    FROM dw_fact_ventas f 
    JOIN dw_dim_tiempo t ON f.id_tiempo = t.id_tiempo
    WHERE t.anio = (SELECT MAX(anio) FROM dw_dim_tiempo) -- measegura el ultimo año
      AND t.mes = (SELECT MAX(mes) FROM dw_dim_tiempo WHERE anio = (SELECT MAX(anio) FROM dw_dim_tiempo)) -- measegura el ultimo mes
    GROUP BY f.id_producto
)
SELECT p.sku, p.category, um.ventas_mes, ph.avg_mensual
FROM UltimoMes um 
JOIN PromedioHistorico ph ON um.id_producto = ph.id_producto
JOIN dw_dim_producto p ON um.id_producto = p.id_producto
WHERE um.ventas_mes > ph.avg_mensual
ORDER BY 3 DESC LIMIT 5;

-- SEPARADOR
-- 3. Vista de ventas por categoría (Reset y creación)
DROP VIEW IF EXISTS ventas_por_categoria;
CREATE VIEW ventas_por_categoria AS
SELECT p.category, SUM(f.amount) AS revenue_total, SUM(f.qty) AS unidades_totales
FROM dw_fact_ventas f 
JOIN dw_dim_producto p ON f.id_producto = p.id_producto
GROUP BY p.category;

-- SEPARADOR
-- 4. Participación por estado (Window Function)
SELECT 
    ship_state, revenue_estado, 
    ROUND((revenue_estado / total_nacional) * 100, 2) AS pct
FROM (
    SELECT e.ship_state, SUM(f.amount) AS revenue_estado, SUM(SUM(f.amount)) OVER() AS total_nacional
    FROM dw_fact_ventas f 
    JOIN dw_dim_envio e ON f.id_envio = e.id_envio
    GROUP BY e.ship_state
) sub
ORDER BY revenue_estado DESC LIMIT 5;
