---

## 🛑 Paso 0: Preparación del Código (Desde tu PC Local)
Antes de tocar los Workers, asegúrate de que tu proyecto en el Master esté reflejado en la nube.
1.  **Subir a GitHub:** Asegúrate de que tu carpeta del Master (`~/airflow-cluster`) esté vinculada a un repositorio de GitHub y que hayas hecho `git push`.
2.  **IP Privada:** Anota la **IP Privada** de tu instancia Master. La usaremos para transferir archivos.

---

## 🏗️ 1. Preparación de Memoria Virtual (Swap)
> [!IMPORTANT]
> **CONSOLA ACTIVA:** Ejecutar en el modo de transmisión (Broadcast) de los **WORKERS**.

```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 🛠️ 2. Dependencias del Sistema y uv
> [!IMPORTANT]
> **CONSOLA ACTIVA:** Ejecutar en los **WORKERS**.

```bash
sudo apt update && sudo apt install -y libpq-dev build-essential
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

---

## 📂 3. Clonación con Nombre Exacto
> [!IMPORTANT]
> **CONSOLA ACTIVA:** Ejecutar en los **WORKERS**.

Es **crítico** que la carpeta se llame igual que en el Master para que las rutas de los servicios no fallen. 

```bash
# Método A: Clonar con el nombre de carpeta específico (RECOMENDADO)
# Sustituye 'airflow-cluster' por el nombre de tu proyecto
git clone git@github.com:USUARIO/TU_REPO.git ~/airflow-cluster

cd ~/airflow-cluster
uv sync
```

---

## ⚙️ 4. Sincronización de Configuración (SCP - Modo Jalar)
> [!CAUTION]
> **CONSOLA ACTIVA:** Debes estar parado físicamente en la terminal de los **WORKERS** (usando el modo transmisión).
> Vamos a **"Jalar" (PULL)** el archivo desde el Master hacia el Worker. Es mucho más eficiente para el modo transmisión de Termius.

```bash
# 1. Aseguramos que existe la carpeta de datos en el Worker
mkdir -p ~/airflow-cluster/airflow_data

# 2. Copiamos el archivo DESDE el Master (Usando su IP Privada) HACIA el Worker actual
# Formato: scp usuario@ORIGEN:RUTA_ARCHIVO DESTINO_LOCAL
# Reemplaza IP_PRIVADA_MASTER con la IP real de tu instancia Master (ej: 172.31.x.x)
scp ubuntu@IP_PRIVADA_MASTER:~/airflow-cluster/airflow_data/airflow.cfg ~/airflow-cluster/airflow_data/
```

> [!TIP]
> **¿Por qué fallaba tu comando anterior (Master -> Worker)?**
> Si lo hacías desde el Master "empujando" hacia los workers, cualquier cambio en la IP o fallo en el Agente de SSH detenía el proceso. Al hacerlo desde los Workers "jalando", centralizas la acción y aprovechas el Broadcast de Termius para hacerlo en los 3 a la vez con un solo comando.

---

## 🚀 5. Inicio y Segundo Plano (Background)
Para que los Workers funcionen sin que tengas que tener la consola abierta, debemos configurarlos como servicios de **systemd**.

### Opción A: Prueba Rápida (Consola abierta)
Si solo quieres probar que todo conecte:
```bash
source .venv/bin/activate
export AIRFLOW_HOME=$HOME/airflow-cluster/airflow_data
airflow celery worker
```

### Opción B: Segundo Plano Permanente (RECOMENDADO)
En los Workers solo necesitamos el servicio del **Worker**. No instales el scheduler ni el webserver aquí.

**1. Crear el archivo de servicio:**
Ejecuta esto en los Workers para abrir el editor:
```bash
sudo nano /etc/systemd/system/airflow-worker.service
```

**2. Pegar el siguiente contenido:**
(Asegúrate de que las rutas coincidan con tu usuario `ubuntu`)
```ini
[Unit]
Description=Airflow Celery Worker
After=network.target rabbitmq-server.service
Wants=rabbitmq-server.service

[Service]
User=ubuntu
Group=ubuntu
Type=simple
WorkingDirectory=/home/ubuntu/airflow-cluster
Environment="AIRFLOW_HOME=/home/ubuntu/airflow-cluster/airflow_data"
ExecStart=/home/ubuntu/airflow-cluster/.venv/bin/airflow celery worker
Restart=always
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

**3. Activar y Validar:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable airflow-worker
sudo systemctl start airflow-worker

# Comprobar que está "active (running)"
sudo systemctl status airflow-worker
```

---

---

## ⚙️ 6. Sincronización Quirúrgica del `airflow.cfg` (Arquitectura 3.x)

En Airflow 3.x, los Workers son "ligeros": no necesitan acceso directo a la base de datos, solo se comunican con el Master a través de su API. Para evitar confusiones, aquí tienes el detalle de qué debe ir en cada máquina.

---

---

### 🏛️ Bloque A: Configuración en el MASTER
Este archivo es el que "manda". Debe tener conexión total.

| Parámetro | Valor Sugerido | ¿Por qué? |
| :--- | :--- | :--- |
| **`executor`** | `CeleryExecutor` | El Master reparte las tareas. |
| **`sql_alchemy_conn`**| `postgresql://...@IP_DB:5432/db`| El Master **SÍ** habla con la DB. |
| **`dags_folder`** | `/home/ubuntu/airflow-cluster/dags` | La ruta de tus scripts .py. |
| **`internal_api_url`**| `http://localhost:8080` | Para su comunicación interna. |
| **`broker_url`** | `amqp://...@localhost:5672/`| El Broker (Rabbit) está aquí mismo. |
| **`base_url`** | `http://IP_PUBLICA:8080`| La identidad para tu navegador. |

**Líneas completas para el Master:**
```ini
executor = CeleryExecutor
dags_folder = /home/ubuntu/airflow-cluster/dags
sql_alchemy_conn = postgresql+psycopg2://usuario:password@IP_DB_EXTERNA:5432/nombre_db
internal_api_url = http://localhost:8080
broker_url = amqp://rabbitmq_airflow:rabbitmq_airflow_pass@localhost:5672/airflow_vhost
result_backend = db+postgresql://usuario:password@IP_DB_EXTERNA:5432/nombre_db
base_url = http://IP_PUBLICA_O_TAILSCALE:8080
```

---

### 🔧 Bloque B: Configuración en los WORKERS
Este archivo es minimalista. El Worker no necesita tocar la base de datos de Postgres.

| Parámetro | Valor Sugerido | ¿Por qué? |
| :--- | :--- | :--- |
| **`executor`** | `CeleryExecutor` | Debe coincidir con el Master. |
| **`sql_alchemy_conn`**| **(Dejar vacío o comentar)** | El Worker usa la API, no la DB. |
| **`dags_folder`** | `/home/ubuntu/airflow-cluster/dags` | Debe ser idéntica a la del Master. |
| **`internal_api_url`**| `http://IP_PRIVADA_MASTER:8080`| Habla con el Master para todo. |
| **`broker_url`** | `amqp://...@IP_PRIVADA_MASTER:5672`| Busca al cartero en el Master. |
| **`base_url`** | `http://IP_PUBLICA:8080`| Debe ser igual que en el Master. |

**Líneas completas para los Workers:**
```ini
executor = CeleryExecutor
dags_folder = /home/ubuntu/airflow-cluster/dags
# sql_alchemy_conn =  (Comentado: el worker no necesita acceso directo a la DB)
internal_api_url = http://IP_PRIVADA_MASTER:8080
broker_url = amqp://rabbitmq_airflow:rabbitmq_airflow_pass@IP_PRIVADA_MASTER:5672/airflow_vhost
result_backend = db+postgresql://usuario:password@IP_DB_EXTERNA:5432/nombre_db
base_url = http://IP_PUBLICA_O_TAILSCALE:8080
```

---

## 🛠️ 7. Aplicando los cambios (Paso a Paso)

### 1. En el Master
Abre el archivo: `nano ~/airflow-cluster/airflow_data/airflow.cfg`.
Busca y ajusta los valores del **Bloque A**. Guarda con `Ctrl+O`.

### 2. En los Workers (Usando Transmisión)
En tus 3 terminales de Workers, abre el archivo y aplica los valores del **Bloque B**.
No olvides comentar la línea de la base de datos con un `#`:
`# sql_alchemy_conn = postgresql://...`

---

## ⚠️ Checklist de Conectividad (Antes de encender)

Para que esto no falle, verifica:
1.  **Security Group de la DB**: Debe aceptar conexiones desde las IPs privadas del Master y de los 3 Workers en el puerto **5432**.
2.  **Security Group del Master**: Debe aceptar conexiones de los 3 Workers en el puerto **5672** (RabbitMQ).
3.  **Usuario de DB**: Asegúrate de que el usuario de PostgreSQL tenga permisos para crear tablas (ya que Airflow las creará durante la migración).

> [!TIP]
> **Próximo Paso: El Terreno Nuevo (DAGs y Datos)**
> Una vez que reinicies los servicios con `sudo systemctl restart airflow-*`, el clúster estará unido. Ahora podemos hablar de cómo sincronizar tus archivos `.py` (DAGs) y los datos que procesan.
