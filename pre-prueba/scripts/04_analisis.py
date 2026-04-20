import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from pathlib import Path

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

def obtener_engine():
    """Crea un motor de conexión SQLAlchemy para PostgreSQL."""
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db = os.getenv("DB_NAME")
    
    # Formato: postgresql://usuario:contraseña@host:port/database
    # conn_string = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    conn_string = f"postgresql://{user}:{password}@{host}:{port}/{db}" # los esta sacando de las variables anteriores
    return create_engine(conn_string)

def ejecutar_analisis():
    """Realiza las consultas analíticas requeridas por el negocio."""
    print("\n" + "="*50)
    print("INICIANDO ANÁLISIS COMERCIAL (RETAILCO)")
    print("="*50)
    
    engine = obtener_engine()
    
    try:
        # Abrimos la conexión usando el motor (best practice con Pandas)
        with engine.connect() as conn:
            # 1. Top 10 SKU por revenue total
            print("\n1. TOP 10 SKU POR REVENUE TOTAL")
            query1 = """
                SELECT 
                    p.sku, 
                    p.category,
                    SUM(f.amount) as revenue_total
                FROM fact_ventas f
                JOIN dim_producto p ON f.id_producto = p.id_producto
                GROUP BY p.sku, p.category
                ORDER BY revenue_total DESC
                LIMIT 10;
            """
            df_top_sku = pd.read_sql(query1, conn) # aqui se realiza la consulta mediante pandas, es decir, se ejecuta la consulta SQL y se devuelve un dataframe con el resultado
            print(df_top_sku.to_string(index=False)) # to_string() convierte el dataframe en un string y index=False evita que se muestre el indice del dataframe

            # 2. Ventas totales por mes
            print("\n2. VENTAS TOTALES POR MES")
            query2 = """
                SELECT 
                    t.anio,
                    t.mes,
                    SUM(f.amount) as ventas_totales
                FROM fact_ventas f
                JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
                GROUP BY t.anio, t.mes
                ORDER BY t.anio, t.mes DESC;
            """
            df_ventas_mes = pd.read_sql(query2, conn)
            print(df_ventas_mes.to_string(index=False))

            # 3. Ticket promedio por categoría de producto
            print("\n3. TICKET PROMEDIO POR CATEGORÍA")
            query3 = """
                SELECT 
                    p.category,
                    AVG(f.ticket_promedio) as ticket_promedio_categoria
                FROM fact_ventas f
                JOIN dim_producto p ON f.id_producto = p.id_producto
                GROUP BY p.category
                ORDER BY ticket_promedio_categoria DESC;
            """
            df_ticket_cat = pd.read_sql(query3, conn)
            print(df_ticket_cat.to_string(index=False))

            # 4. Revenue por canal de venta  (ship-service-level)
            print("\n4. REVENUE POR CANAL DE VENTA")
            query4 = """
                SELECT 
                    e.ship_service_level as canal,
                    SUM(f.amount) as revenue_total
                FROM fact_ventas f
                JOIN dim_envio e ON f.id_envio = e.id_envio
                GROUP BY e.ship_service_level
                ORDER BY revenue_total DESC;
            """
            df_revenue_canal = pd.read_sql(query4, conn)
            print(df_revenue_canal.to_string(index=False))

    except Exception as e:
        print(f"Error durante el análisis: {e}")
    finally:
        print("\n" + "="*50)
        print("ANÁLISIS COMPLETADO")
        print("="*50)

if __name__ == "__main__":
    ejecutar_analisis()
