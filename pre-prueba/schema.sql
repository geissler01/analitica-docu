-- ==============================================================================
-- MODELO DE ESTRELLA PARA RETAILCO - PostgreSQL
-- ==============================================================================
-- IMPORTANTE: El orden de eliminación y creación es crítico.
-- Primero se eliminan las tablas de Hechos, y luego las de Dimensiones.
-- Al crear, primero se crean las Dimensiones, y por último la de Hechos.

DROP TABLE IF EXISTS fact_ventas CASCADE;
DROP TABLE IF EXISTS dim_producto CASCADE;
DROP TABLE IF EXISTS dim_envio CASCADE;
DROP TABLE IF EXISTS dim_cliente CASCADE;
DROP TABLE IF EXISTS dim_tiempo CASCADE;
DROP TABLE IF EXISTS staging_ventas CASCADE;

-- ==============================================================================
-- 0. TABLA DE STAGING (Carga temporal)
-- ==============================================================================
CREATE TABLE staging_ventas (
    order_id VARCHAR(255),
    sku VARCHAR(255),
    style VARCHAR(255),
    category VARCHAR(255),
    size VARCHAR(50),
    asin VARCHAR(255),
    status VARCHAR(255),
    courier_status VARCHAR(255),
    fulfilment VARCHAR(100),
    sales_channel VARCHAR(100),
    ship_service_level VARCHAR(100),
    ship_city VARCHAR(255),
    ship_state VARCHAR(255),
    ship_postal_code VARCHAR(100),
    ship_country VARCHAR(100),
    b2b BOOLEAN,
    fecha DATE,
    qty INT,
    amount DECIMAL(15, 2),
    ticket_promedio DECIMAL(15, 2),
    dia INT,
    mes INT,
    anio INT,
    trimestre INT,
    semana_del_anio INT
);

-- Dimensión Producto (Qué se vendió)
CREATE TABLE dim_producto (
    id_producto SERIAL PRIMARY KEY,
    SKU VARCHAR(255) UNIQUE NOT NULL,
    style VARCHAR(255),
    category VARCHAR(255),
    size VARCHAR(50),
    ASIN VARCHAR(255)
);

-- Dimensión Envío (Cómo y dónde se entregó)
-- Agregamos una restricción UNIQUE sobre todas las columnas para evitar duplicados en cargas repetidas
CREATE TABLE dim_envio (
    id_envio SERIAL PRIMARY KEY,
    status VARCHAR(255),
    courier_status VARCHAR(255),
    fulfilment VARCHAR(100),
    sales_channel VARCHAR(100),
    ship_service_level VARCHAR(100),
    ship_city VARCHAR(255),
    ship_state VARCHAR(255),
    ship_postal_code VARCHAR(100),
    ship_country VARCHAR(100),
    CONSTRAINT unique_envio UNIQUE (status, courier_status, fulfilment, sales_channel, ship_service_level, ship_city, ship_state, ship_postal_code, ship_country)
);

-- Dimensión Cliente (A quién se le vendió)
CREATE TABLE dim_cliente (
    id_cliente SERIAL PRIMARY KEY,
    b2b BOOLEAN UNIQUE NOT NULL
);

-- Dimensión Tiempo (Cuándo se vendió)
CREATE TABLE dim_tiempo (
    id_tiempo SERIAL PRIMARY KEY,
    fecha_completa DATE UNIQUE NOT NULL,
    dia INT,
    mes INT,
    anio INT,
    trimestre INT,
    semana_del_anio INT
);

-- ==============================================================================
-- 2. TABLA DE HECHOS (Fact Table)
-- ==============================================================================

CREATE TABLE fact_ventas (
    id_venta SERIAL PRIMARY KEY,
    order_id VARCHAR(255) NOT NULL,
    id_producto INT REFERENCES dim_producto(id_producto),
    id_envio INT REFERENCES dim_envio(id_envio),
    id_cliente INT REFERENCES dim_cliente(id_cliente),
    id_tiempo INT REFERENCES dim_tiempo(id_tiempo),
    qty INT DEFAULT 0,
    amount DECIMAL(15, 2) DEFAULT 0.00,
    ticket_promedio DECIMAL(15, 2) DEFAULT 0.00
);

-- ==============================================================================
-- ÍNDICES (Opcional pero muy recomendado para reportes rápidos en OLAP)
-- ==============================================================================

CREATE INDEX idx_fact_producto ON fact_ventas(id_producto);
CREATE INDEX idx_fact_envio ON fact_ventas(id_envio);
CREATE INDEX idx_fact_cliente ON fact_ventas(id_cliente);
CREATE INDEX idx_fact_tiempo ON fact_ventas(id_tiempo);
CREATE INDEX idx_fact_order_id ON fact_ventas(order_id);
