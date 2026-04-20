import os
import pandas as pd
import psycopg2
from psycopg2 import extras
from dotenv import load_dotenv
from pathlib import Path

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "archive" / "Amazon Sale Report.csv"
SCHEMA_PATH = BASE_DIR / "schema.sql"

def limpiar_y_transformar_en_python(df):
    """
    EN ESTA FASE HACEMOS EL 'EXTRACT' Y EL 'TRANSFORM' (ETL)
    Limpiamos lo básico en Python antes de subirlo a la base de datos.
    """
    print("\n--- PASO 1: LIMPIEZA Y TRANSFORMACIÓN EN PYTHON ---")
    
    # Standardizar nombres de columnas a la versión de SQL (minúsculas y sin espacios)
    df.columns = df.columns.str.strip().str.replace('-', '_').str.replace(' ', '_').str.lower() # convierte las columnas en texto, les quita los espacios, los guiones al medio y los pone en minusculas
    
    # 1. Tratar nulos básicos
    nulos_amount = df['amount'].isna().sum()
    df['amount'] = df['amount'].fillna(0.0) # llena los nulos de la columna amount (monto) con 0.0
    
    nulos_qty = df['qty'].isna().sum()
    df['qty'] = df['qty'].fillna(0).astype(int) # llena los nulos de la columna qty (cantidad) con 0 y convierte la columna a entero
    print(f"Limpieza inicial: {nulos_amount} nulos en amount y {nulos_qty} en qty corregidos.")
    
    # 2. Limpiar columnas de texto (evitar nulos y float mismatches)
    cols_texto = ['sku', 'style', 'category', 'size', 'asin', 'status', 'courier_status', 'fulfilment', 'sales_channel', 'ship_service_level', 'ship_city', 'ship_state', 'ship_postal_code', 'ship_country']
    
    total_unknown = 0
    for col in cols_texto:
        if col in df.columns:
            # Convertimos a texto, quitamos .0 y limpiamos espacios
            df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            # Contamos cuántos se van a marcar como Unknown
            nulos_identificados = df[col].isin(['nan', 'None', 'nan.0']).sum()
            df[col] = df[col].replace(['nan', 'None', 'nan.0'], 'Unknown') # reemplazamos los diferentes valores nulos por la palabra 'Unknown'
            total_unknown += nulos_identificados
    
    print(f"Limpieza de texto: {total_unknown} valores nulos/vacíos marcados como 'Unknown' en {len(cols_texto)} columnas.")

    # 3. Arreglar fechas y columnas derivadas
    df['fecha'] = pd.to_datetime(df['date'], errors='coerce', format='%m-%d-%y')
    
    # Contamos cuántos registros se eliminan por fecha inválida
    filas_antes = len(df)
    df = df.dropna(subset=['fecha']) # eliminamos las filas que tengan nulos en la columna fecha, porque estos registros no tienen sentido y fallaran cuando se intente subir a la db postgres
    filas_eliminadas = filas_antes - len(df)
    print(f"Registros eliminados por fecha inválida: {filas_eliminadas}")
    
    df['dia'] = df['fecha'].dt.day.astype(int)
    df['mes'] = df['fecha'].dt.month.astype(int)
    df['anio'] = df['fecha'].dt.year.astype(int)
    df['trimestre'] = df['fecha'].dt.quarter.astype(int)
    df['semana_del_anio'] = df['fecha'].dt.isocalendar().week.astype(int)
    
    # 4. Cálculo de Ticket Promedio (Monto total dividido por cantidad)
    # Usamos .apply(axis=1) para recorrer cada fila y calcular el promedio.
    # El 'if x['qty'] > 0' es una medida de seguridad para evitar errores de división por cero.
    df['ticket_promedio'] = df.apply(
        lambda x: x['amount'] / x['qty'] if x['qty'] > 0 else 0.0, axis=1
    )

    # Solo nos quedamos con las columnas que definimos en staging_ventas en schema.sql
    # --- AUDITORÍA DE COLUMNAS ---
    columnas_totales = df.columns.tolist()
    
    columnas_finales = [
        'order_id', 'sku', 'style', 'category', 'size', 'asin', 'status', 'courier_status',
        'fulfilment', 'sales_channel', 'ship_service_level', 'ship_city', 'ship_state',
        'ship_postal_code', 'ship_country', 'b2b', 'fecha', 'qty', 'amount', 
        'ticket_promedio', 'dia', 'mes', 'anio', 'trimestre', 'semana_del_anio'
    ]
    
    columnas_excluidas = [c for c in columnas_totales if c not in columnas_finales]
    
    print(f"\n--- RESUMEN DE SELECCIÓN DE COLUMNAS ---")
    print(f"Seleccionadas ({len(columnas_finales)}): {columnas_finales}")
    print(f"Excluidas ({len(columnas_excluidas)}): {columnas_excluidas}")
    
    # Creamos el dataframe final para el modelo estrella
    df_final = df[columnas_finales].copy()
    
    # TRADUCTOR FINAL: Convertimos NaN de Pandas a None de Python.
    # Esto es CRÍTICO para que la base de datos reconozca los nulos como NULL en SQL.
    df_final = df_final.where(pd.notnull(df_final), None)
    
    print(f"Datos listos para subir: {len(df_final)} registros.")
    return df_final

def ejecutar_carga_elt(df):
    """
    EN ESTA FASE HACEMOS EL 'LOAD' Y LA DISTRIBUCIÓN FINAL (ETL/ELT)
    """
    print("\n--- PASO 2: CARGA A POSTGRESQL (USANDO STAGING) ---")
    load_dotenv(BASE_DIR / ".env")
    
    try:
        # ESTABLECER LA CONEXIÓN (Abrimos el puente con la base de datos)
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        # EL CURSOR: Es el objeto que realmente ejecuta los comandos SQL y recorre los resultados
        cur = conn.cursor()
        
        # 1. Resetear todas las tablas ejecutando schema.sql
        print("Ejecutando schema.sql (Reset total)...")
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            cur.execute(f.read()) # read() lee el archivo completo y lo convierte en un string
            # cur.execute() ejecuta el string SQL en la base de datos
        
        # 2. Cargar el DataFrame completo a la tabla de STAGING
        print("Subiendo datos a staging_ventas...")
        cols = list(df.columns)
        # Creamos la consulta dinámica con los nombres de las columnas
        query_staging = f"INSERT INTO staging_ventas ({', '.join(cols)}) VALUES %s"
        # extras es una funcion importada al principio del codigo
        # execute_values es una función de alto rendimiento para insertar miles de filas a la vez
        extras.execute_values(cur, query_staging, [tuple(x) for x in df.values]) # esto hace una tupla con los valores de cada fila, es decir, tantas tuplas como filas, lo cual queda como un listado de tuplas que serian los valores a insertar en la tabla staging_ventas
        
        # 3. Distribuir a Dimensiones usando SQL (Lo más seguro y rápido)
        print("Poblando dimensiones desde staging...")
        
        # dim_producto (Carga única de productos)
        # cur.execute() ejecuta el string SQL en la base de datos
        # INSERT INTO dim_producto (sku, style, category, size, asin)
        # SELECT DISTINCT sku, style, category, size, asin FROM staging_ventas
        # ON CONFLICT (sku) DO NOTHING; en caso de que mañana se quiera volver a ejecutar el script con datos actualizados, no se duplicaran los datos
        # 
        cur.execute("""
            INSERT INTO dim_producto (sku, style, category, size, asin)
            SELECT DISTINCT sku, style, category, size, asin FROM staging_ventas
            ON CONFLICT (sku) DO NOTHING;
        """)
        
        # dim_tiempo
        cur.execute("""
            INSERT INTO dim_tiempo (fecha_completa, dia, mes, anio, trimestre, semana_del_anio)
            SELECT DISTINCT fecha, dia, mes, anio, trimestre, semana_del_anio FROM staging_ventas
            ON CONFLICT (fecha_completa) DO NOTHING;
        """)
        
        # dim_cliente
        cur.execute("""
            INSERT INTO dim_cliente (b2b)
            SELECT DISTINCT b2b FROM staging_ventas
            ON CONFLICT (b2b) DO NOTHING;
        """)
        
        # dim_envio
        cur.execute("""
            INSERT INTO dim_envio (status, courier_status, fulfilment, sales_channel, ship_service_level, ship_city, ship_state, ship_postal_code, ship_country)
            SELECT DISTINCT status, courier_status, fulfilment, sales_channel, ship_service_level, ship_city, ship_state, ship_postal_code, ship_country FROM staging_ventas
            ON CONFLICT ON CONSTRAINT unique_envio DO NOTHING;
        """)
        
        # 4. Llenar la Tabla de Hechos (fact_ventas) usando JOINS con las dimensiones
        print("Llenando tabla de hechos (fact_ventas) mediante SQL Joins...")
        cur.execute("""
            INSERT INTO fact_ventas (order_id, id_producto, id_envio, id_cliente, id_tiempo, qty, amount, ticket_promedio)
            SELECT 
                s.order_id, p.id_producto, e.id_envio, c.id_cliente, t.id_tiempo, s.qty, s.amount, s.ticket_promedio
            FROM staging_ventas s
            JOIN dim_producto p ON s.sku = p.sku
            JOIN dim_tiempo t ON s.fecha = t.fecha_completa
            JOIN dim_cliente c ON s.b2b = c.b2b
            JOIN dim_envio e ON 
                s.status = e.status AND 
                s.courier_status = e.courier_status AND 
                s.fulfilment = e.fulfilment AND 
                s.sales_channel = e.sales_channel AND 
                s.ship_service_level = e.ship_service_level AND 
                s.ship_city = e.ship_city AND 
                s.ship_state = e.ship_state AND 
                s.ship_postal_code = e.ship_postal_code AND 
                s.ship_country = e.ship_country;
        """)
        
        # 5. Borrar la tabla de staging para dejar la base limpia
        print("Borrando tabla de staging...")
        cur.execute("DROP TABLE staging_ventas;")
        
        conn.commit()
        
        # Reporte final
        print("\n--- REPORTE FINAL ---")
        for tabla in ['dim_producto', 'dim_tiempo', 'dim_cliente', 'dim_envio', 'fact_ventas']:
            cur.execute(f"SELECT COUNT(*) FROM {tabla}")
            print(f"Tabla {tabla}: {cur.fetchone()[0]} registros.") # fetchone() devuelve una tupla con el resultado, en este caso el conteo de registros
            
        cur.close()
        conn.close()
        print("\n¡ETL Completado con éxito! Carga 100% íntegra.")
        
    except Exception as e:
        print(f"Error en el proceso de carga: {e}")
        if 'conn' in locals() and conn: conn.rollback()

if __name__ == "__main__":
    df_raw = pd.read_csv(CSV_PATH, low_memory=False)
    df_limpio = limpiar_y_transformar_en_python(df_raw)
    ejecutar_carga_elt(df_limpio)
