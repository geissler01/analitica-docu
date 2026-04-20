# Guía de Instalación: Clúster de Airflow 3.2.0 en AWS EC2 (Ubuntu)

Esta guía detalla el proceso completo para configurar un clúster de Apache Airflow 3.2.0 sobre instancias EC2 de AWS con Ubuntu, utilizando `uv` para una gestión de paquetes rápida y eficiente.

---

## 📑 Tabla de Contenidos
1. [Prerrequisitos](#prerrequisitos)
2. [Creación de Memoria Virtual (Swap)](#creación-de-memoria-virtual-swap)
3. [Instalar uv y Preparar la Consola](#1-instalar-uv-y-preparar-la-consola)
4. [Configurar el Entorno Virtual](#2-configurar-el-entorno-virtual)
5. [Preparación del Sistema para Airflow](#3-preparación-del-sistema-para-airflow)
6. [Instalación y Configuración de RabbitMQ](#35-instalación-y-configuración-de-rabbitmq)
7. [Instalación de Airflow 3.2.0](#4-instalación-de-airflow-320)
8. [Configuración de Airflow (airflow.cfg)](#5-configuración-de-airflow-airflowcfg)
9. [Migración de Base de Datos](#6-migración- de-base-de-datos)
10. [Creación de Usuario y Despliegue](#7-creación-de-usuario-y-despliegue)

---

## 🛠 Prerrequisitos
* Una instancia **EC2 de AWS** con Ubuntu (22.04 LTS o superior recomendado).
* Conexión SSH establecida (ej. mediante **Termius**).
* Acceso a un servidor **PostgreSQL** (externa o local).
* Instalación de **RabbitMQ** como Broker de mensajes.

---

## Creación de Memoria Virtual (Swap)
Si tu instancia EC2 tiene pocos recursos (ej: `t3.micro`), es vital asignar memoria virtual del disco duro para evitar que Airflow se detenga por falta de RAM.

### Pasos para crear 4GB de RAM Virtual (Swap)

1. **Crear el archivo gigante en el disco duro:**
   ```bash
   sudo fallocate -l 4G /swapfile
   ```

2. **Darle los permisos de seguridad (Solo el sistema puede leerlo):**
   ```bash
   sudo chmod 600 /swapfile
   ```

3. **Formatearlo para que funcione como RAM:**
   ```bash
   sudo mkswap /swapfile
   ```

4. **¡Encender la memoria Swap!:**
   ```bash
   sudo swapon /swapfile
   ```

5. **Hacerlo permanente (Para que sobreviva a los reinicios):**
   ```bash
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```

**Verificación:**
```bash
free -h
```
Deberías ver una sección llamada `Swap:` con un tamaño aproximado de `4.0Gi`.

---

## 3. Instalar uv y Preparar la Consola
Utilizaremos `uv` por su velocidad extrema y eficiencia en la gestión de entornos de Python.

### Paso 1: Instalar uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Paso 2: Configurar el PATH
Agregamos la ruta de los binarios locales a nuestra sesión y aseguramos que se cargue automáticamente.

```bash
# Agregar al PATH en la sesión actual
export PATH="$HOME/.local/bin:$PATH"

# Persistir en el .bashrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Refrescar la configuración
source ~/.bashrc
```

> [!TIP]
> Si en algún momento necesitas reiniciar la instancia EC2, puedes usar `sudo reboot`.

---

## 4. Configurar el Entorno Virtual

### Crear carpeta del proyecto
```bash
mkdir airflow-cluster && cd airflow-cluster
```

### Inicializar el proyecto
Esto creará un archivo `pyproject.toml` esencial para replicar la instalación en los Workers del clúster.

```bash
uv init --no-workspace
```

### Crear entorno virtual con Python 3.12
```bash
uv venv --python 3.12
# Activar el entorno
source .venv/bin/activate
```

> [!NOTE]
> Deberías ver `(.venv)` al inicio de tu línea de comandos tras la activación.

> [!TIP]
> **¿`airflow` o `uv run airflow`?**
> - Si tu entorno virtual está **activado** (ves el `(.venv)`), puedes usar `airflow` directamente.
> - Si **no quieres activar** el entorno manualmente cada vez, puedes usar `uv run airflow`. `uv` se encargará de encontrar el entorno correcto por ti. En esta guía, asumiremos que el entorno está activado.

---

## 5. Preparación del Sistema para Airflow

### Instalar dependencias del sistema
Necesitamos los conectores de PostgreSQL y herramientas de compilación.

```bash
sudo apt update && sudo apt install -y libpq-dev build-essential
```

### Estructura de Carpetas Sugerida
Para que tu proyecto sea profesional y fácil de subir a GitHub, usaremos esta estructura. El objetivo es mantener el **código** (DAGs) separado de la **configuración** (Data).

```text
airflow-cluster/
├── dags/                  # <--- AQUÍ pones tus scripts .py
│   ├── .gitkeep           # Archivo oculto para rastrear la carpeta
│   └── mi_primer_dag.py
├── airflow_data/          # <--- AQUÍ vive la configuración
│   ├── .gitkeep
│   ├── airflow.cfg        # El archivo que editaremos
│   └── logs/              # Logs locales de Airflow
├── pyproject.toml         # Control de dependencias (uv)
├── .gitignore             # Filtro para no subir basura a Git
└── .venv/                 # Entorno virtual (ignorado por Git)
```

### Comandos de Creación
Ejecuta esto en la raíz de tu proyecto (`~/airflow-cluster`):

```bash
# 1. Crear las carpetas base
mkdir -p dags
mkdir -p airflow_data

# 2. Crear los archivos .gitkeep para que Git no ignore las carpetas vacías
touch dags/.gitkeep
touch airflow_data/.gitkeep

# 3. Definir AIRFLOW_HOME en la carpeta de configuraciones
echo "export AIRFLOW_HOME=$(pwd)/airflow_data" >> ~/.bashrc
source ~/.bashrc
```

### Configuración de .gitignore
Este archivo le dice a Git qué **NO** subir. Es vital para no exponer tus contraseñas en GitHub. 
`nano .gitignore`

```text
# Ignorar el entorno virtual de uv
.venv/
__pycache__/
*.pyc

# Ignorar TODO en airflow_data excepto el archivo .gitkeep
# (Así nos aseguramos de que no subas tu airflow.cfg por error)
airflow_data/*
!airflow_data/.gitkeep

# Ignorar logs y archivos temporales
logs/
airflow_data/logs/
*.db
```

---

## 6. Instalación y Configuración de RabbitMQ
RabbitMQ es el motor de mensajería (Broker) que permite la comunicación entre el Scheduler y los Workers. A diferencia de Redis, es un servicio especializado en gestionar colas de mensajería distribuida de forma robusta.

### 🧠 Conceptos que debes conocer:

1.  **¿Qué es un "Vhost" (Virtual Host)?**
    Imagina que RabbitMQ es un edificio de oficinas. Un **Vhost** es como una oficina privada dentro de ese edificio. Al crear un vhost llamado `airflow_vhost`, estamos creando un espacio aislado solo para Airflow. Esto evita que los mensajes de diferentes aplicaciones se mezclen entre sí.
2.  **Diferencia Crítica de Credenciales:** 
    *   **Usuario RabbitMQ (`rabbitmq_airflow`):** Es una credencial de **sistema**. Sirve para que el "software" de Airflow pueda hablar con el "software" de RabbitMQ.
    *   **Usuario Airflow Web:** Es una credencial de **humano**. Es la que crearás en el Paso 7 para entrar tú a la página web de Airflow. **No tienen por qué ser iguales.**

### Paso 1: Instalar el servidor en el OS
```bash
sudo apt update && sudo apt install -y rabbitmq-server
```

### Paso 2: Configurar Seguridad (Usuario y Oficina Virtual)
Configuraremos un usuario propio para que Airflow tenga su propia "llave" y su propia "oficina" (vhost).

```bash
# Iniciar y habilitar el servicio para que arranque con el servidor
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server

# 1. Crear el usuario de sistema para RabbitMQ
# (Sintaxis: sudo rabbitmqctl add_user <nombre> <contraseña>)
sudo rabbitmqctl add_user rabbitmq_airflow rabbitmq_airflow_pass

# 2. Crear la "oficina privada" (Virtual Host)
sudo rabbitmqctl add_vhost airflow_vhost

# 3. Dar permisos (Permitir que el usuario entre y trabaje en esa oficina)
sudo rabbitmqctl set_permissions -p airflow_vhost rabbitmq_airflow ".*" ".*" ".*"

# 4. (Opcional) Activar el Panel Visual
# Esto permite ver las colas de mensajes desde el navegador.
sudo rabbitmqctl set_user_tags rabbitmq_airflow administrator
sudo rabbitmq-plugins enable rabbitmq_management
```

> [!TIP]
> Si activaste el Panel Visual, abre el puerto **15672** en el Security Group de AWS y entra en: `http://TU_IP_EC2:15672`. Usa el usuario `rabbitmq_airflow` para monitorizar tus tareas.

---

## 7. Instalación de Airflow 3.2.0

Para la versión 3.x, es **indispensable** instalar el núcleo junto con el proveedor **FAB** para mantener la interfaz clásica y la gestión de usuarios.

```bash
uv add "apache-airflow[postgres,celery]==3.2.0" \
       "apache-airflow-providers-fab" \
       --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.2.0/constraints-3.12.txt"
```

### Detalle de componentes:
* **`postgres`**: Conector para la base de datos de metadatos.
* **`celery`**: El ejecutor distribuido que reparte tareas a los Workers.
* **`rabbitmq`**: (Soportado por defecto en Celery) El Broker que gestiona la cola de mensajes.
* **`fab`**: Módulo de seguridad y administración de la interfaz web (Flask AppBuilder).

---

## 8. Configuración de Airflow (airflow.cfg)

### Generar archivo base
Ejecuta el siguiente comando para forzar la creación de la carpeta de datos y el archivo de configuración:

```bash
airflow info
```
> [!NOTE]
> Es normal que veas errores en este punto; el objetivo es generar el archivo `airflow.cfg`.

### Editar la configuración
Abre el archivo con `nano`:
```bash
nano $AIRFLOW_HOME/airflow.cfg
```

Modifica las siguientes **5 líneas clave**:

```ini
# 1. Conexión a la base de datos
sql_alchemy_conn = postgresql+psycopg2://usuario:contraseña@host:5432/nombre_db

# 2. Motor de ejecución para clúster
executor = CeleryExecutor

# 3. URL del Broker (RabbitMQ)
# Formato: amqp://usuario:contraseña@host:puerto/vhost
broker_url = amqp://rabbitmq_airflow:rabbitmq_airflow_pass@localhost:5672/airflow_vhost

# 4. Almacén de resultados (Result Backend)
result_backend = db+postgresql://usuario:contraseña@host:5432/nombre_db

# 5. Gestor de Autenticación (Bajo la sección [core])
auth_manager = airflow.providers.fab.auth_manager.fab_auth_manager.FabAuthManager
```

> [!IMPORTANT]
> Recuerda guardar con `Ctrl + O` -> `Enter` y salir con `Ctrl + X`.
> Puedes usar `Ctrl + w` para buscar en el editor de nano.

---

## 9. Migración de Base de Datos
Con las credenciales listas, procedemos a crear las tablas necesarias en PostgreSQL.

```bash
airflow db migrate
```

---

## 10. Creación de Usuario y Despliegue

### Paso 1: Crear Usuario Administrador
```bash
airflow users create \
    --username admin \
    --firstname TuNombre \
    --lastname TuApellido \
    --role Admin \
    --email correo@ejemplo.com \
    --password tu_contraseña
```

### Paso 2: Iniciar Servicios
Abre dos terminales (o usa `tmux`), activa el entorno virtual en ambas y ejecuta:

#### Terminal 1: Interfaz Web
```bash
airflow api-server
```

#### Terminal 2: Scheduler (Programador)
```bash
airflow scheduler
```

#### Terminal 3: Worker (Ejecutor de tareas)
**Crucial:** Sin un worker activo, las tareas permanecerán en cola.
```bash
airflow celery worker
```

---

## 8. Consideraciones Finales y Seguridad en AWS

Para que el clúster sea accesible y seguro, recuerda configurar lo siguiente:

### 🔒 Grupos de Seguridad (AWS Security Groups)
Debes abrir los siguientes puertos en la consola de AWS:
*   **8080 (TCP):** Acceso a la Interfaz Web de Airflow.
*   **15672 (TCP):** Acceso al Panel de Control de RabbitMQ (opcional).
*   **5672 (TCP):** Solo si planeas conectar workers que estén en *otras* instancias EC2 diferentes a la principal.

### 🚀 Escalabilidad
Si el trabajo aumenta, puedes clonar tu instancia de Worker (AMI) y lanzarla en una nueva EC2. Como ya configuramos el `broker_url` apuntando a la IP de la instancia principal, el nuevo worker se conectará automáticamente a la cola de RabbitMQ y empezará a ayudar con las tareas.

---

> [!SUCCESS]
> ¡Tu clúster de Airflow 3.2.0 con RabbitMQ está listo y operativo! 
