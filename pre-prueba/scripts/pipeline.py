import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "archive" / "Amazon Sale Report.csv"
SCHEMA_DW_PATH = BASE_DIR / "schema_dw.sql"

load_dotenv(BASE_DIR / ".env")

def extraer(ruta):
    """
    EXTRACT: Lee el archivo fuente CSV.
    """
    print(f"\n[EXTRAER] Leyendo archivo desde: {ruta}", flush=True)
    return pd.read_csv(ruta, low_memory=False)

def transformar(df):
    """
    TRANSFORM: Aplica limpieza, transformaciones y deduplicación.
    """
    print("[TRANSFORMAR] Iniciando limpieza y transformación...", flush=True)
    conteo_inicial = len(df)

    # 1. Normalizar columnas
    df.columns = df.columns.str.strip().str.replace('-', '_').str.replace(' ', '_').str.lower()

    # 2. Manejo de nulos básicos
    df['amount'] = df['amount'].fillna(0.0)
    df['qty'] = df['qty'].fillna(0).astype(int)

    # 3. Limpieza de texto
    cols_texto = ['sku', 'style', 'category', 'size', 'asin', 'status', 'courier_status', 
                  'fulfilment', 'sales_channel', 'ship_service_level', 'ship_city', 
                  'ship_state', 'ship_postal_code', 'ship_country']
    
    for col in cols_texto:
        if col in df.columns:
            # Primero normalizamos a string y quitamos espacios
            df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            # Luego manejamos los nulos que pudieron quedar como 'nan' o estar vacíos
            df[col] = df[col].replace(['nan', 'None', 'nan.0', '', 'null', 'NULL'], 'Unknown')
            df[col] = df[col].fillna('Unknown')

    # 4. Fechas y columnas derivadas
    df['fecha'] = pd.to_datetime(df['date'], errors='coerce', format='%m-%d-%y')
    df = df.dropna(subset=['fecha']).copy()

    df['dia'] = df['fecha'].dt.day.astype(int)
    df['mes'] = df['fecha'].dt.month.astype(int)
    df['anio'] = df['fecha'].dt.year.astype(int)
    df['trimestre'] = df['fecha'].dt.quarter.astype(int)
    df['semana_del_anio'] = df['fecha'].dt.isocalendar().week.astype(int)

    # 5. Cálculo de Ticket Promedio
    df['ticket_promedio'] = df.apply(
        lambda x: x['amount'] / x['qty'] if x['qty'] > 0 else 0.0, axis=1
    )

    # 6. DEDUPLICACIÓN REQUERIDA (Por Order ID)
    registros_antes_dedup = len(df)
    df = df.drop_duplicates(subset=['order_id'], keep='first').copy()
    eliminados = registros_antes_dedup - len(df)
    
    print(f"   - Registros iniciales: {conteo_inicial}", flush=True)
    print(f"   - Registros después de limpieza: {registros_antes_dedup}", flush=True)
    print(f"   - Registros eliminados por deduplicación (Order ID): {eliminados}", flush=True)
    print(f"   - Registros listos para cargar: {len(df)}", flush=True)
    
    return df

def cargar(df, engine):
    """
    LOAD: Carga los datos en el esquema paralelo 'dw_'.
    """
    print("[CARGAR] Iniciando carga incremental en PostgreSQL (esquema dw_)...", flush=True)
    
    with engine.begin() as conn:
        # 1. Asegurar que las tablas existan (sin borrarlas si ya tienen datos)
        with open(SCHEMA_DW_PATH, 'r', encoding='utf-8') as f:
            for statement in f.read().split(';'):
                if statement.strip():
                    conn.execute(text(statement))

        # LIMPIEZA PARA RE-TEST: Truncamos tablas dw_ para empezar de cero
        # print("   - Limpiando tablas para re-test...", flush=True)
        # conn.execute(text("TRUNCATE TABLE dw_fact_ventas CASCADE;"))
        # conn.execute(text("TRUNCATE TABLE dw_dim_producto CASCADE;"))
        # conn.execute(text("TRUNCATE TABLE dw_dim_envio CASCADE;"))
        # conn.execute(text("TRUNCATE TABLE dw_dim_cliente CASCADE;"))
        # conn.execute(text("TRUNCATE TABLE dw_dim_tiempo CASCADE;"))

        # 2. Carga a Staging Temporal (dw_staging_ventas)
        # Limpiamos el staging primero por seguridad en esta corrida
        conn.execute(text("TRUNCATE TABLE dw_staging_ventas;"))
        
        columnas_finales = [
            'order_id', 'sku', 'style', 'category', 'size', 'asin', 'status', 'courier_status',
            'fulfilment', 'sales_channel', 'ship_service_level', 'ship_city', 'ship_state',
            'ship_postal_code', 'ship_country', 'b2b', 'fecha', 'qty', 'amount', 
            'ticket_promedio', 'dia', 'mes', 'anio', 'trimestre', 'semana_del_anio'
        ]
        df_final = df[columnas_finales].copy()
        
        # Convertimos para SQL
        # df_final = df_final.where(pd.notnull(df_final), None) # Comentado para evitar pérdida de registros en el JOIN
        
        # Optimización: Carga masiva por lotes
        print("   - Subiendo datos a staging (Carga masiva)...", flush=True)
        df_final.to_sql('dw_staging_ventas', conn, if_exists='append', index=False, chunksize=1000, method='multi')

        # 3. Poblado de dimensiones e inserción en Hechos con manejo de conflictos
        print("   - Poblando dimensiones dw_...", flush=True)
        conn.execute(text("""
            INSERT INTO dw_dim_producto (sku, style, category, size, asin)
            SELECT DISTINCT sku, style, category, size, asin FROM dw_staging_ventas
            ON CONFLICT (sku) DO NOTHING;
            
            INSERT INTO dw_dim_tiempo (fecha_completa, dia, mes, anio, trimestre, semana_del_anio)
            SELECT DISTINCT fecha, dia, mes, anio, trimestre, semana_del_anio FROM dw_staging_ventas
            ON CONFLICT (fecha_completa) DO NOTHING;
            
            INSERT INTO dw_dim_cliente (b2b)
            SELECT DISTINCT b2b FROM dw_staging_ventas
            ON CONFLICT (b2b) DO NOTHING;
            
            INSERT INTO dw_dim_envio (status, courier_status, fulfilment, sales_channel, ship_service_level, ship_city, ship_state, ship_postal_code, ship_country)
            SELECT DISTINCT status, courier_status, fulfilment, sales_channel, ship_service_level, ship_city, ship_state, ship_postal_code, ship_country FROM dw_staging_ventas
            ON CONFLICT ON CONSTRAINT unique_dw_envio DO NOTHING;
        """))

        print("   - Insertando en dw_fact_ventas (Evitando duplicados de Order ID)...", flush=True)
        conn.execute(text("""
            INSERT INTO dw_fact_ventas (order_id, id_producto, id_envio, id_cliente, id_tiempo, qty, amount, ticket_promedio)
            SELECT 
                s.order_id, p.id_producto, e.id_envio, c.id_cliente, t.id_tiempo, s.qty, s.amount, s.ticket_promedio
            FROM dw_staging_ventas s
            JOIN dw_dim_producto p ON s.sku = p.sku
            JOIN dw_dim_tiempo t ON s.fecha = t.fecha_completa
            JOIN dw_dim_cliente c ON s.b2b = c.b2b
            JOIN dw_dim_envio e ON 
                s.status = e.status AND s.courier_status = e.courier_status AND 
                s.fulfilment = e.fulfilment AND s.sales_channel = e.sales_channel AND 
                s.ship_service_level = e.ship_service_level AND s.ship_city = e.ship_city AND 
                s.ship_state = e.ship_state AND s.ship_postal_code = e.ship_postal_code AND 
                s.ship_country = e.ship_country
            ON CONFLICT (order_id) DO NOTHING;
        """))
        
        # Limpiar staging
        conn.execute(text("TRUNCATE TABLE dw_staging_ventas;"))
        print("\n[CARGAR] Carga completada exitosamente.")
        print("\n[CARGAR] Carga completada exitosamente.")

if __name__ == "__main__":
    from sqlalchemy import create_engine
    
    # Configuración de base de datos
    user = os.getenv("DB_USER")
    pas = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db = os.getenv("DB_NAME")
    
    engine = create_engine(f"postgresql://{user}:{pas}@{host}:{port}/{db}")
    
    # EJECUCIÓN DEL PIPELINE
    print("="*60)
    print("PIPELINE ETL RETAILCO - MODELO PARALELO DW_")
    print("="*60)
    
    try:
        df_raw = extraer(CSV_PATH)
        df_limpio = transformar(df_raw)
        cargar(df_limpio, engine)
        
        print("\n--- RESUMEN FINAL DE LAS TABLAS DW_ ---")
        with engine.connect() as conn:
            for tabla in ['dw_dim_producto', 'dw_dim_tiempo', 'dw_fact_ventas']:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
                print(f"Tabla {tabla}: {count} registros.")
                
    except Exception as e:
        print(f"\n[ERROR] El pipeline falló: {e}")
    finally:
        print("\n" + "="*60)
        print("FIN DEL PROCESO")
        print("="*60)
