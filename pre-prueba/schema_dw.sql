-- ==============================================================================
-- MODELO DE ESTRELLA PARALELO (DEDUP BY ORDER_ID) - PostgreSQL
-- ==============================================================================
-- Este esquema se usa para el Ejercicio 6 (Pipeline Automatizado).
-- La diferencia clave es que aquí aplicamos una restricción estricta de 
-- unicidad sobre el ORDER_ID en la tabla de hechos.

-- ==============================================================================
-- 0. TABLA DE STAGING (Carga temporal)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS dw_staging_ventas (
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

-- Dimensión Producto
CREATE TABLE IF NOT EXISTS dw_dim_producto (
    id_producto SERIAL PRIMARY KEY,
    SKU VARCHAR(255) UNIQUE NOT NULL,
    style VARCHAR(255),
    category VARCHAR(255),
    size VARCHAR(50),
    ASIN VARCHAR(255)
);

-- Dimensión Envío
CREATE TABLE IF NOT EXISTS dw_dim_envio (
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
    CONSTRAINT unique_dw_envio UNIQUE (status, courier_status, fulfilment, sales_channel, ship_service_level, ship_city, ship_state, ship_postal_code, ship_country)
);

-- Dimensión Cliente
CREATE TABLE IF NOT EXISTS dw_dim_cliente (
    id_cliente SERIAL PRIMARY KEY,
    b2b BOOLEAN UNIQUE NOT NULL
);

-- Dimensión Tiempo
CREATE TABLE IF NOT EXISTS dw_dim_tiempo (
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
CREATE TABLE IF NOT EXISTS dw_fact_ventas (
    id_venta SERIAL PRIMARY KEY,
    order_id VARCHAR(255) UNIQUE NOT NULL, -- REGLA: Un solo registro por Order ID
    id_producto INT REFERENCES dw_dim_producto(id_producto),
    id_envio INT REFERENCES dw_dim_envio(id_envio),
    id_cliente INT REFERENCES dw_dim_cliente(id_cliente),
    id_tiempo INT REFERENCES dw_dim_tiempo(id_tiempo),
    qty INT DEFAULT 0,
    amount DECIMAL(15, 2) DEFAULT 0.00,
    ticket_promedio DECIMAL(15, 2) DEFAULT 0.00
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_dw_fact_producto ON dw_fact_ventas(id_producto);
CREATE INDEX IF NOT EXISTS idx_dw_fact_tiempo ON dw_fact_ventas(id_tiempo);
