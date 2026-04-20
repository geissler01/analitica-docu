Aquí tienes la guía definitiva y estructurada desde cero absoluto. Este es el manual exacto para levantar tu nodo principal con **Airflow 3.2.0**, usando **uv**, Python 3.12 y **PostgreSQL**.

Sigue estos pasos en orden secuencial dentro de tu terminal.

### ---

**Fase 1: Preparación del Entorno y Carpetas**

Vamos a aislar todo el proyecto para que no interfiera con el sistema operativo.

**1\. Crea la estructura de carpetas:**

Bash

\# Crea la carpeta principal del proyecto y entra en ella  
mkdir mi\_cluster\_airflow  
cd mi\_cluster\_airflow

\# Crea la carpeta interna que Airflow usará como su "casa"  
mkdir airflow\_home

**2\. Inicializa el entorno con uv:**

Bash

\# Inicia el proyecto (esto crea el archivo pyproject.toml)  
uv init

\# Fuerza a que el entorno use Python 3.12  
uv python pin 3.12

**3\. Define la variable de entorno AIRFLOW\_HOME:**

Bash

\# Le dice a tu terminal actual dónde está la casa de Airflow  
export AIRFLOW\_HOME=$(pwd)/airflow\_home

\# (Opcional pero recomendado) Hazlo permanente para futuras sesiones  
echo "export AIRFLOW\_HOME=$(pwd)/airflow\_home" \>\> \~/.bashrc

### ---

**Fase 2: Instalación de Dependencias**

**1\. Instala librerías del sistema operativo:**

Postgres necesita ciertas librerías en Ubuntu para compilar el driver de Python.

Bash

sudo apt update  
sudo apt install \-y libpq-dev

**2\. Instala Airflow 3.2.0 con uv:**

Descargamos la versión exacta con los conectores necesarios.

Bash

uv add "apache-airflow\[postgres,celery\]==3.2.0" \--constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.2.0/constraints-3.12.txt"

**3\. Genera los archivos de configuración base:**

Ejecuta este comando solo para que Airflow lea la variable AIRFLOW\_HOME y cree el archivo airflow.cfg vacío.

Bash

uv run airflow info

### ---

**Fase 3: Seguridad y Credenciales (Nuevo estándar v3)**

Airflow 3 ya no usa comandos en la terminal para crear usuarios básicos; lee un archivo físico.

**1\. Crea el archivo de contraseñas:**

Bash

\# Entra a la carpeta home de Airflow  
cd airflow\_home

\# Crea el archivo JSON con tu usuario y contraseña  
cat \<\<EOF \> simple\_auth\_manager\_passwords.json  
{  
  "admin": "admin123"  
}  
EOF

\# Regresa a la carpeta principal del proyecto  
cd ..

### ---

**Fase 4: Edición del Archivo de Configuración Maestra**

Abre el archivo airflow\_home/airflow.cfg en tu editor (Visual Studio Code) y realiza **únicamente** los siguientes cambios.

**En la sección \[core\]:**

1. **Cambia el ejecutor:**  
   Ini, TOML  
   executor \= CeleryExecutor

2. **Apunta a Postgres:**  
   *(Reemplaza tu\_usuario, tu\_password y tu\_db por los reales de tu Postgres).*  
   Ini, TOML  
   sql\_alchemy\_conn \= postgresql+psycopg2://tu\_usuario:tu\_password@localhost:5432/tu\_db

3. **Activa el gestor de usuarios v3:**  
   Ini, TOML  
   auth\_manager \= airflow.api\_fastapi.auth.managers.simple.simple\_auth\_manager.SimpleAuthManager

4. **Define qué usuarios tienen permisos de administrador:**  
   Ini, TOML  
   simple\_auth\_manager\_users \= admin:admin

5. **Apunta al archivo JSON que creaste en la Fase 3:**  
   *(Debes poner la ruta absoluta o completa de tu servidor. Ejemplo: /home/ubuntu/mi\_cluster\_airflow/airflow\_home/simple\_auth\_manager\_passwords.json)*  
   Ini, TOML  
   simple\_auth\_manager\_passwords\_file \= /RUTA/COMPLETA/HASTA/TU/simple\_auth\_manager\_passwords.json

**En la sección \[celery\]:**

1. **Apunta el backend a Postgres:**  
   Ini, TOML  
   result\_backend \= db+postgresql+psycopg2://tu\_usuario:tu\_password@localhost:5432/tu\_db

### ---

**Fase 5: Inicialización de la Base de Datos**

Ahora que Airflow sabe dónde está Postgres y cómo conectarse, le ordenamos que construya su estructura interna.

Bash

\# Asegúrate de estar en la carpeta principal 'mi\_cluster\_airflow'  
uv run airflow db migrate

### ---

**Fase 6: Arranque del Nodo**

Para que el servidor funcione de forma continua, necesitas ejecutar dos procesos en terminales separadas.

**Abre la Terminal 1 (La Interfaz Gráfica / API):**

Bash

uv run airflow api-server \--port 8080

**Abre la Terminal 2 (El Cerebro de Tareas):**

Bash

uv run airflow scheduler

Finalmente, abre tu navegador, ingresa a tu IP pública en el puerto 8080 e inicia sesión con el usuario admin y la contraseña admin123.