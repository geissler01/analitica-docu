# RetailCo Analytics: Pipeline ETL y Business Intelligence

![Status](https://img.shields.io/badge/Status-Complete-success?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue?style=for-the-badge&logo=postgresql)
![Python](https://img.shields.io/badge/Language-Python%203.12-yellow?style=for-the-badge&logo=python)

## Sobre el Proyecto
Este proyecto es una solución integral de analítica de datos para **RetailCo**, una empresa de comercio electrónico en India. El sistema extrae datos de ventas crudos (CSV), los transforma mediante un pipeline automatizado y los carga en un **Modelo Estrella** optimizado en PostgreSQL, culminando en un dashboard ejecutivo de alta fidelidad en Power BI.

### Hallazgos Principales (Resumen Ejecutivo)
1. **Dominio de Categorías**: El 92% del revenue es impulsado por solo 2 categorías: 'Set' y 'kurta'.
2. **Eficiencia de Venta**: El ticket promedio ($597) superó el objetivo en un 37%, validando el poder adquisitivo del segmento.
3. **Pico Estacional**: Abril fue el mes récord ($26.9M), seguido de una desaceleración estacional en mayo/junio.
4. **Concentración Regional**: Maharashtra y Karnataka representan los hubs de mayor rentabilidad.
5. **Integridad de Datos**: Se logró una trazabilidad del 100% (120,378 órdenes únicas) tras una limpieza técnica profunda.

---

## Guía de Inicio Rápido

Si es tu primera vez aquí, sigue estos pasos para replicar el entorno:

### 1. Requisitos Previos
- **Python 3.12+** instalado.
- **PostgreSQL** corriendo localmente o en la nube.
- Ganas de analizar datos.

### 2. Configuración del Entorno
Copia el archivo de ejemplo y configura tus credenciales de base de datos:
```bash
cp .env.example .env
# Abre .env y pon tu usuario, contraseña y nombre de la DB
```

Instala las dependencias:
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt # o usa 'uv sync'
```

### 3. Ejecución del Pipeline (Orden Obligatorio)
Para que el sistema funcione, debes ejecutar los scripts en este orden:

1. **Crear Base de Datos**: Ejecuta `schema.sql` y `schema_dw.sql` en tu cliente de PostgreSQL (pgAdmin/DBeaver).
2. **Pipeline de Carga**: 
   ```bash
   python scripts/pipeline.py
   ```
   *Este script limpia los datos, elimina duplicados y carga el modelo estrella dw_.*
3. **Análisis SQL**:
   ```bash
   python scripts/05_sql_pandas.py
   ```
   *Ejecuta consultas avanzadas (CTE/Vistas) para validar los resultados.*

---

## Estructura del Repositorio
- `archive/`: Contiene el dataset original `Amazon Sale Report.csv`.
- `scripts/`: La inteligencia del proyecto.
    - `01_python_puro.py`: Exploración inicial.
    - `pipeline.py`: El corazón del ETL automatizado.
    - `05_sql_pandas.py`: Consultas analíticas avanzadas.
- `docs/`: Reportes detallados de EDA, Storytelling y Dashboard.
- `queries.sql`: Las sentencias SQL analíticas puras.
- `schema_dw.sql`: Definición del modelo estrella paralelo.

---

## Decisiones Técnicas
- **Modelo Estrella (DW)**: Elegido por su velocidad de consulta y facilidad de conexión con herramientas de BI.
- **Deduplicación**: Implementamos lógica en Python para asegurar que cada `Order ID` sea único, eliminando el ruido de los datos crudos.
- **Integridad**: Los valores nulos se transformaron en 'Unknown' para evitar la pérdida de registros durante los JOINs.

---
*Desarrollado por RetailCo Data Team.*
