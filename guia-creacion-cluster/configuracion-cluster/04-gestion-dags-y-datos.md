# Guía: Gestión de DAGs y Datos en el Clúster

Una vez que el clúster está conectado, el siguiente gran reto es asegurar que **todos los nodos vean el mismo código y los mismos datos**. En Airflow, esto es fundamental porque el Master decide *qué* hacer, pero los Workers son los que *ejecutan* el código.

---

## 📂 1. Sincronización de DAGs (El Código)

Para que un DAG se ejecute correctamente, el archivo `.py` debe existir **exactamente en la misma ruta** en el Master y en todos los Workers.

### Opción Recomendada: Git Pull
Como ya configuramos GitHub, la forma más limpia es:
1.  **En tu PC/Master**: Escribes el código, haces `git commit` y `git push`.
2.  **En los Workers**: Ejecutas un `git pull` (puedes hacerlo en los 3 a la vez con el modo transmisión de Termius).

> [!TIP]
> **Sincronización de Librerías:**
> Si tu nuevo DAG usa una librería de Python que no estaba instalada (ej: `pandas`), recuerda ejecutar `uv sync` en todos los nodos después del `git pull`.

---

## 💾 2. Gestión de Datos (La Información)

Aquí es donde los DAGs leen y escriben archivos. Tenemos tres escenarios comunes:

### A. Datos en Base de Datos (Postgres/RDS)
Es la opción más sencilla para clústeres.
*   **Cómo funciona:** El DAG no lee archivos del disco, sino que hace un `SELECT` a la base de datos externa.
*   **Ventaja:** Todos los nodos ven lo mismo instantáneamente.
*   **Configuración:** Solo necesitas asegurar que los Workers tengan permiso en el Security Group de la base de datos.

### B. Datos Locales (Carpetas compartidas)
Si necesitas procesar archivos CSV o Parquet que están en el disco:
*   **El problema:** Si el Master guarda un archivo en `~/datos/`, el Worker no podrá verlo porque tiene su propio disco duro independiente.
*   **Solución manual:** Usar `git` para subir también los archivos de datos (no recomendado para archivos grandes).
*   **Solución profesional**: Montar un sistema de archivos compartido como **Amazon EFS** (Elastic File System) en `/mnt/data`. Así, todas las instancias ven la misma carpeta "nube" como si fuera local.

### C. Datos en la Nube (Amazon S3)
Es el estándar de la industria para Big Data.
*   **Cómo funciona:** El DAG descarga el archivo de S3, lo procesa y lo vuelve a subir.
*   **Configuración:** Necesitas instalar el proveedor de Amazon en Airflow:
    ```bash
    uv add apache-airflow-providers-amazon
    ```
*   **Permisos:** La instancia EC2 debe tener un **IAM Role** que le permita leer/escribir en el bucket de S3.

---

## 🛠️ 3. Creación Manual de Carpetas (Plan B)

Si por algún motivo Git no creó las carpetas o necesitas crearlas desde cero en un nuevo nodo, usa estos comandos:

```bash
# Crear la estructura base manualmente
mkdir -p ~/airflow-cluster/dags
mkdir -p ~/airflow-cluster/airflow_data

# Asegurar que Airflow las reconozca
export AIRFLOW_HOME=~/airflow-cluster/airflow_data
```

---

---

## 🚀 4. Ejercicio: El Gran Estreno del Clúster

Para confirmar que tu clúster está operando al 100%, vamos a ejecutar un DAG que reparta 6 tareas pesadas entre tus 3 Workers.

### Paso 1: Crear el script del DAG (En el MASTER)
Crea el archivo: `nano ~/airflow-cluster/dags/test_distribucion.py`

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import socket
import time

def check_worker():
    # Obtiene el nombre de la máquina donde se ejecuta la tarea
    hostname = socket.gethostname()
    print(f"🚀 Tarea ejecutada en el nodo: {hostname}")
    # Simula un trabajo de 20 segundos para ver la concurrencia
    time.sleep(20)

with DAG(
    dag_id='test_distribucion_cluster',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=['distribucion']
) as dag:

    # Creamos 6 tareas paralelas
    for i in range(1, 7):
        PythonOperator(
            task_id=f'tarea_paralela_{i}',
            python_callable=check_worker
        )
```

### Paso 2: Sincronizar con los Workers (Modo Transmisión)
Recuerda que los Workers necesitan tener el **mismo archivo** en la **misma ruta**.
1.  En el Master: `git add . && git commit -m "Add test dag" && git push`
2.  En los Workers: `git pull`

---

## 🔍 5. Verificación Estricta (Desde Termius)

Si Airflow ignora tus DAGs, usa estos comandos en el **MASTER** para forzar el reconocimiento:

```bash
# 1. Listar DAGs registrados (Debería aparecer 'test_distribucion_cluster')
airflow dags list

# 2. Ver si hay errores de sintaxis en el archivo
airflow dags report

# 3. Forzar al Scheduler a escanear de nuevo
sudo systemctl restart airflow-scheduler
```

### ¿Cómo ver la distribución en vivo?
1.  **En la Web de Airflow**: Entra al DAG, actívalo (Off -> On) y presiona **Trigger DAG**.
2.  **Vista de Gráfica (Graph)**: Verás los 6 cuadrados en verde claro (Running).
3.  **Logs de Tarea**: Entra al log de la `tarea_paralela_1` y luego a la `tarea_paralela_6`. El nombre del `hostname` debería ser diferente entre ellas si se repartieron en distintos workers.

#### Monitoreo de Logs en Workers (Opcional):
Si quieres ver los mensajes "volar" en directo, corre esto en los Workers:
```bash
sudo journalctl -u airflow-worker -f
```

---

## 🏁 Conclusión del Clúster

Con estas 4 guías, has construido un sistema de grado de producción:
1.  **Instalación Rápida** con `uv`.
2.  **Mensajería Robusta** con RabbitMQ.
3.  **Disponibilidad** con servicios de `systemd` en segundo plano.
4.  **Escalabilidad** con Workers sincronizados por Git y conectividad API-less.

> [!SUCCESS]
> ¡Tu clúster de Airflow 3.2.0 está operando a máxima capacidad!
