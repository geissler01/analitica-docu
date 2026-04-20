# Documentación del Pipeline ETL - RetailCo

Este documento explica el diseño técnico realizado para el Ejercicio 6, donde se implementó un flujo automatizado de datos con un modelo estrella paralelo.

## ¿ETL o ELT?
Este proceso es principalmente un flujo **ETL (Extract, Transform, Load)** por las siguientes razones:
1.  **Transform**: Los datos se limpian y transforman (deduplicación, manejo de nulos, cálculo de nuevas métricas como `ticket_promedio`) en la memoria de Python (Pandas) **antes** de enviarlos a su destino final.
2.  **Load**: Solo los datos ya procesados y "curados" se insertan en las tablas finales de PostgreSQL.

Sin embargo, tiene un componente de **ELT** al utilizar una tabla de `staging_ventas` dentro de la base de datos para realizar los `JOINs` de las dimensiones mediante SQL, aprovechando la potencia del motor de base de datos para las uniones complejas.

## Manejo de Datos en Streaming
Si los datos llegaran en tiempo real (streaming) en lugar de archivos CSV:
1.  **Herramientas**: Usaría una arquitectura basada en **Apache Kafka** o **AWS Kinesis** para capturar los eventos.
2.  **Procesamiento**: Cambiaría Pandas por un framework de streaming como **Apache Flink**, **Spark Streaming** o **Faust** (en Python).
3.  **Base de Datos**: Podría usar una base de datos más orientada a series de tiempo o mantener Postgres pero escalando la capacidad de escritura (Ingest Rate).

## Orquestación en Producción
Para orquestar este pipeline en un entorno real, usaría **Apache Airflow**.

**¿Por qué Airflow?**
-   **Programación**: Permite definir dependencias claras (ej: no cargar ventas si la dimensión tiempo falló).
-   **Monitoreo**: Ofrece una interfaz visual para ver si el pipeline falló y reintentar tareas automáticamente.
-   **Escalabilidad**: Puede manejar cientos de pipelines de forma centralizada.

## Modelo Paralelo (dw_)
Se creó el esquema `dw_` para demostrar la **Idempotencia**. 
-   **Regla de Negocio**: A diferencia del modelo original, aquí el `Order ID` es único. 
-   **Resultado**: Esto evita duplicados accidentales si el mismo archivo se carga varias veces, manteniendo la integridad financiera del reporte.
