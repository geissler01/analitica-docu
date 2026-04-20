# Prueba de desempeño — Analítica de datos Jr
**Caso de negocio:** RetailCo — empresa de comercio electrónico  
**Dataset:** E-Commerce Sales Dataset (128.975 filas, 31 columnas)  
🔗 https://www.kaggle.com/datasets/thedevastator/unlock-profits-with-e-commerce-sales-data

**Total:** 100 puntos | **Tiempo estimado:** 4–5 horas  
**Entrega:** Repositorio público en GitHub

---

## Contexto del caso

RetailCo es una tienda online con operaciones en Colombia, México y Argentina. El equipo de liderazgo necesita entender el comportamiento de ventas, la calidad de sus datos y construir un dashboard para tomar decisiones. Tú eres el analista de datos Jr encargado de construir todo el flujo: desde el modelado del Data Warehouse hasta la visualización ejecutiva.

---

## Ejercicio 1 — Modelado OLAP: esquema estrella en PostgreSQL
**Puntos:** 10 | **Temas:** Modelado dimensional · SQL DDL · PostgreSQL

### Contexto
Antes de cargar cualquier dato, el equipo necesita una estructura analítica bien diseñada en PostgreSQL. Analiza las columnas del dataset de Kaggle e identifica las dimensiones y la tabla de hechos que componen el modelo.

### Entregables

**1. Diagrama del esquema estrella** (usa dbdiagram.io, draw.io o similar — exporta como imagen `star_schema.png`)

El modelo debe incluir como mínimo:

- `fact_ventas` — tabla de hechos con las métricas numéricas: `amount`, `qty`, `ticket_promedio` y las llaves foráneas hacia cada dimensión
- `dim_producto` — SKU, nombre, categoría, talla (size)
- `dim_cliente` — información del comprador si está disponible, o del destinatario
- `dim_envio` — canal de servicio (ship-service-level), estado de envío (ship-state), ciudad, país
- `dim_tiempo` — fecha completa, día, mes, trimestre, año, semana del año

**2. Script `schema.sql`** con los `CREATE TABLE` en PostgreSQL para todas las tablas, incluyendo:
- Llave primaria (`SERIAL PRIMARY KEY`) en cada dimensión
- Llaves foráneas en `fact_ventas` referenciando cada dimensión
- Tipos de dato correctos: `VARCHAR`, `INT`, `DECIMAL(12,2)`, `DATE`, etc.
- Al menos un índice en `fact_ventas` sobre la columna de fecha

**3. Documento `modelado_docs.md`** que responda:
- ¿Por qué se eligió un esquema estrella y no una tabla plana o un esquema copo de nieve?
- ¿Qué diferencia hay entre una base OLTP y una base OLAP, y por qué RetailCo necesita ambas?
- ¿Qué columnas del dataset original quedaron fuera del modelo y por qué?

---

## Ejercicio 2 — Python puro: carga inicial y validación
**Puntos:** 10 | **Temas:** Python · Estructuras de datos · Manejo de errores

### Contexto
Antes de usar Pandas ni PostgreSQL, el equipo quiere que demuestres que entiendes qué ocurre por debajo cuando se lee y procesa un archivo. Todo con Python puro.

### Entregables

**Archivo `01_python_puro.py`:**

- Lee el CSV usando solo el módulo `csv` de Python (sin Pandas, sin librerías externas)
- Almacena los datos en una lista de diccionarios
- Calcula el total de ventas (`Amount`) usando comprensión de listas — implementa `try/except` para valores no numéricos e imprime cuántos registros fallaron
- Filtra los 5 productos (`SKU`) con mayor cantidad vendida (`Qty`) usando código eficiente, sin loops innecesarios
- Escribe en un nuevo archivo `ordenes_filtradas.csv` solo las columnas: `Order ID`, `SKU`, `Amount`, `Qty`

---

## Ejercicio 3 — EDA con Pandas
**Puntos:** 10 | **Temas:** EDA · Pandas · Calidad de datos

### Contexto
El equipo de negocio sospecha que el dataset tiene problemas. Tu trabajo es confirmarlos o descartarlos antes de cualquier análisis. Sin notebooks — todo en scripts Python.

### Entregables

**Archivo `02_eda.py`** (entorno UV — incluye `pyproject.toml` en el repo):

- Carga el dataset con Pandas e imprime en consola: `shape`, `dtypes` por columna y porcentaje de nulos por columna
- Identifica al menos 3 problemas de calidad de datos (tipos incorrectos, nulos, valores imposibles, duplicados, etc.)
- Imprime un resumen de estadísticas descriptivas de las columnas numéricas clave

**Archivo `eda_reporte.md`:**

- Documenta cada problema encontrado: qué es, en qué columna está y cuál es su impacto potencial en el análisis
- Responde: ¿qué columnas tienen el tipo de dato incorrecto y por qué eso es crítico para el análisis?

---

## Ejercicio 4 — Limpieza, transformación y carga a PostgreSQL
**Puntos:** 10 | **Temas:** Limpieza · Transformación · PostgreSQL · psycopg2

### Contexto
Con los problemas identificados en el EDA, corrígelos y carga los datos limpios directamente en el esquema estrella que diseñaste en el ejercicio 1. La base de datos destino es PostgreSQL.

### Entregables

**Archivo `03_limpieza_carga.py`:**

- Elimina duplicados e imprime en consola cuántos eliminaste y con qué criterio los identificaste
- Trata los valores nulos: justifica en comentarios del código si eliminaste, reemplazaste o dejaste cada nulo (no hay respuesta única — justifica con criterio analítico)
- Convierte columnas de fecha al tipo correcto y genera las columnas derivadas: `mes`, `semana_del_año`, `trimestre`
- Crea la columna `ticket_promedio` = `Amount / Qty` con manejo explícito de división por cero
- Conecta a PostgreSQL usando `psycopg2`, crea las tablas con el `schema.sql` del ejercicio 1 si no existen, y carga los datos limpios en las tablas correspondientes (`dim_producto`, `dim_tiempo`, `dim_envio`, `fact_ventas`, etc.)
- Al finalizar imprime cuántos registros quedaron en cada tabla

**Archivo `.env`** (agrégalo al `.gitignore` — no lo subas al repo) con las credenciales de conexión: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`. El script debe leer las credenciales desde variables de entorno, no hardcodeadas.

---

## Ejercicio 5 — Análisis con Pandas y Power BI
**Puntos:** 12 | **Temas:** Pandas · pd.read_sql · Power BI

### Contexto
El director comercial hizo 4 preguntas concretas. Respóndelas primero en Pandas (para validar los números) y luego construye las visualizaciones en Power BI conectando directamente a PostgreSQL.

### Entregables

**Parte A — `04_analisis.py`:**

- Lee desde PostgreSQL usando `psycopg2` + `pd.read_sql()` (no desde el CSV)
- Calcula y muestra en consola:
  - Top 10 SKU por revenue total
  - Ventas totales por mes
  - Ticket promedio por categoría de producto
  - Revenue por canal de venta (`ship-service-level`)

**Parte B — `dashboard_analisis.pbix` + `graficos_docs.md`:**

- Conecta Power BI a PostgreSQL y construye 4 visualizaciones:
  - Top 10 SKU por revenue → barras horizontales
  - Evolución mensual de ventas → líneas con anotación del mes pico
  - Ticket promedio por categoría → barras verticales
  - Revenue por canal → tipo a tu elección (justifica en el markdown)
- En `graficos_docs.md` justifica el tipo de gráfico elegido para cada pregunta (ej: "usé barras porque comparo categorías discretas, no una tendencia en el tiempo")

---

## Ejercicio 6 — Pipeline ETL estructurado
**Puntos:** 12 | **Temas:** ETL/ELT · Pipelines · Automatización

### Contexto
El equipo quiere automatizar el proceso completo para que se ejecute con nuevos archivos sin intervención manual.

### Entregables

**Archivo `pipeline.py`:**

- Estructura el código en 3 funciones: `extraer(ruta)`, `transformar(df)`, `cargar(df, conn)`
- `transformar` aplica toda la limpieza del ejercicio 4
- `cargar` inserta en PostgreSQL — si un registro ya existe (mismo `Order ID`), no lo duplica
- El pipeline imprime logs de cada paso: registros entrantes → registros después de limpieza → registros insertados en BD

**Archivo `pipeline_docs.md`:**

- ¿Este proceso es ETL o ELT? ¿Por qué?
- ¿Qué cambiaría en el diseño si los datos llegaran en streaming en lugar de archivos CSV?
- ¿Qué herramienta usarías para orquestar este pipeline en producción y por qué?

---

## Ejercicio 7 — SQL analítico ejecutado desde Pandas
**Puntos:** 12 | **Temas:** SQL · CTE · Vistas · pd.read_sql

### Contexto
Escribe las queries en SQL sobre el esquema estrella en PostgreSQL y ejecútalas desde Python con `pd.read_sql()`. Sin notebooks — todo en scripts.

### Entregables

**Archivo `queries.sql`** con las 4 consultas comentadas.

**Archivo `05_sql_pandas.py`** que las ejecuta y muestra los DataFrames:

1. **Consulta simple:** total de ventas (`SUM(amount)`) y cantidad de órdenes (`COUNT(*)`) por mes — agrupa desde `dim_tiempo` haciendo JOIN con `fact_ventas`
2. **Consulta con CTE:** identifica los SKU cuyas ventas del último mes disponible superan su promedio histórico — usa una CTE para calcular el promedio por SKU antes del filtro final
3. **Vista:** crea `ventas_por_categoria` con `CREATE OR REPLACE VIEW` — debe mostrar `amount` total, `qty` total y `ticket_promedio` por categoría; luego consúltala con `pd.read_sql()` y muestra el resultado
4. **Análisis de participación:** top 5 estados (`ship-state`) por revenue con su porcentaje del total calculado directamente en SQL usando una subquery o `SUM() OVER()`

---

## Ejercicio 8 — Dashboard ejecutivo en Power BI
**Puntos:** 12 | **Temas:** Power BI · Visualización · BI

### Contexto
El director general tiene 90 segundos para revisar el estado del negocio. Construye el dashboard que usará en esa reunión. Este es el dashboard completo — el ejercicio 5 solo tenía las 4 visualizaciones de análisis.

### Entregables

**Archivo `dashboard_ejecutivo.pbix`** conectado a PostgreSQL + **`dashboard_docs.md`:**

- El dashboard debe responder de un vistazo: ¿cómo van las ventas totales?, ¿qué categoría lidera?, ¿cuál es la tendencia mensual?, ¿hay alguna alerta o anomalía?
- Incluye al menos: 1 KPI card, 1 gráfico de tendencia temporal, 1 gráfico de comparación por categoría y 1 filtro interactivo por mes o categoría
- En el markdown documenta: justificación de cada tipo de gráfico elegido + 3 buenas prácticas de visualización que aplicaste (jerarquía visual, consistencia de colores, eliminación de ruido)

---

## Ejercicio 9 — Storytelling con datos
**Puntos:** 12 | **Temas:** Storytelling · Comunicación · Negocio

### Contexto
El análisis está hecho y el dashboard construido. Ahora tienes que comunicar qué encontraste de forma que el equipo directivo pueda tomar una decisión concreta.

### Entregables

**Presentación de 5 slides exportada como PDF** + **`storytelling_docs.md`:**

- **Slide 1 — Contexto:** ¿qué pregunta de negocio responde este análisis?
- **Slide 2 — Hallazgo principal:** el insight más importante, con el gráfico que mejor lo comunica
- **Slide 3 — Soporte:** 2 hallazgos adicionales que refuerzan o matizan el hallazgo principal
- **Slide 4 — Alerta o riesgo:** algo en los datos que el negocio debería vigilar
- **Slide 5 — Recomendación:** 1 acción concreta que propones basada en los datos

En `storytelling_docs.md` responde: ¿qué tipo de pregunta de negocio estás respondiendo (descriptiva, diagnóstica o predictiva)? ¿Cómo guiaste al lector hacia la conclusión?

---

## Entrega

### Estructura del repositorio

```
retailco-analysis/
├── schema.sql
├── star_schema.png
├── scripts/
│   ├── 01_python_puro.py
│   ├── 02_eda.py
│   ├── 03_limpieza_carga.py
│   ├── 04_analisis.py
│   ├── 05_sql_pandas.py
│   └── pipeline.py
├── queries.sql
├── docs/
│   ├── modelado_docs.md
│   ├── eda_reporte.md
│   ├── graficos_docs.md
│   ├── dashboard_docs.md
│   ├── pipeline_docs.md
│   └── storytelling_docs.md
├── outputs/
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

### Criterios generales

- **El README debe incluir:** instrucciones para reproducir el entorno con UV, cómo configurar el `.env` con las credenciales de PostgreSQL, descripción de cada script y los hallazgos principales en máximo 5 líneas.
- **Hilo conductor obligatorio:** cada ejercicio consume lo que produjo el anterior. El coder que rompa la cadena (ej: leer el CSV en vez de PostgreSQL en el ejercicio 5) perderá puntos en consistencia.
- **Bono +2 pts:** el pipeline del ejercicio 6 se ejecuta sobre un archivo CSV nuevo sin modificar el código, inserta correctamente en PostgreSQL y Power BI refleja los datos actualizados sin intervención manual.

---

*100 puntos base + 2 de bono · Modelado 10 · Python 10 · EDA 10 · Limpieza/Carga 10 · Análisis 12 · Pipeline 12 · SQL 12 · Dashboard 12 · Storytelling 12*
