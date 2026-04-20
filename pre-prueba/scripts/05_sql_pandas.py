import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# 1. Definición de rutas absolutas seguras usando __file__
# BASE_DIR apunta a la raíz del proyecto, permitiendo encontrar queries.sql siempre
BASE_DIR = Path(__file__).resolve().parent.parent
QUERIES_PATH = BASE_DIR / "queries.sql"

# 2. Configuración del motor de base de datos
load_dotenv(BASE_DIR / ".env")
url_db = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME')}"
engine = create_engine(url_db)

def ejecutar_ejercicio():
    # 3. 'with open' es un Context Manager: abre el archivo y LO CIERRA automáticamente
    with open(QUERIES_PATH, 'r', encoding='utf-8') as f:
        # split('-- SEPARADOR') corta el texto en una lista
        # [b.strip() for b in ... if b.strip()] limpia espacios y quita bloques vacíos
        bloques = [b.strip() for b in f.read().split('-- SEPARADOR') if b.strip()]

    # Diccionario para que el código sea muy claro y ordenado
    queries = {
        'mensual': bloques[0],
        'comparativa': bloques[1],
        'crear_vista': bloques[2],
        'participacion': bloques[3]
    }

    # 4. 'with engine.connect()' también cierra la conexión a la DB al terminar el bloque
    with engine.connect() as conn:
        print("\n--- [1] VENTAS MENSUALES ---")
        print(pd.read_sql(text(queries['mensual']), conn))

        print("\n--- [2] COMPARATIVA SKU VS PROMEDIO ---")
        print(pd.read_sql(text(queries['comparativa']), conn))

        print("\n--- [3] CREANDO VISTA Y CONSULTANDO CATEGORÍAS ---")
        # El bloque de la vista incluye el DROP y el CREATE
        conn.execute(text(queries['crear_vista']))
        conn.commit()
        print(pd.read_sql(text("SELECT * FROM ventas_por_categoria"), conn))

        print("\n--- [4] PARTICIPACIÓN POR ESTADO (TOP 5) ---")
        print(pd.read_sql(text(queries['participacion']), conn))

if __name__ == "__main__":
    ejecutar_ejercicio()
