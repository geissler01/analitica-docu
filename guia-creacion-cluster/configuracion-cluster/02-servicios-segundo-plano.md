# Guía: Airflow en Segundo Plano (Servicios systemd)

Este documento explica cómo configurar los componentes de Airflow como servicios del sistema en Ubuntu. Esto garantiza que Airflow se inicie automáticamente al arrancar la instancia EC2 y se mantenga ejecutándose en segundo plano.

---

## 🏗️ ¿Qué es systemd?
**systemd** es el administrador de sistema y servicios estándar en Ubuntu. Permite registrar aplicaciones como "Unidades de Servicio" para que el sistema las controle.

### Ventajas:
*   **Auto-reinicio**: Si Airflow falla por un error de sistema, Ubuntu intentará levantarlo solo.
*   **Logs centralizados**: Puedes ver todos los errores con un solo comando.
*   **Independencia de la terminal**: Ya no necesitas dejar ventanas de SSH abiertas.

---

## 1. Identificación de Rutas (El Plano)
Para que los servicios funcionen, los archivos deben conocer las rutas absolutas:
*   **Directorio del Proyecto**: `/home/ubuntu/airflow-cluster`
*   **Entorno Virtual (Binarios)**: `/home/ubuntu/airflow-cluster/.venv/bin/airflow`
*   **Carpeta de Datos (AIRFLOW_HOME)**: `/home/ubuntu/airflow-cluster/airflow_data`

---

## 2. Creación de los Archivos de Servicio
Debes crear 3 archivos en la carpeta `/etc/systemd/system/`. Necesitarás usar `sudo`.

### A. Servicio de la Interfaz Web (API Server)
Crea el archivo: `sudo nano /etc/systemd/system/airflow-webserver.service`
```ini
[Unit]
Description=Airflow Webserver (API Server)
After=network.target postgresql.service rabbitmq-server.service
Wants=postgresql.service rabbitmq-server.service

[Service]
User=ubuntu
Group=ubuntu
Type=simple
WorkingDirectory=/home/ubuntu/airflow-cluster
Environment="AIRFLOW_HOME=/home/ubuntu/airflow-cluster/airflow_data"
ExecStart=/home/ubuntu/airflow-cluster/.venv/bin/airflow api-server
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

### B. Servicio del Scheduler (Programador)
Crea el archivo: `sudo nano /etc/systemd/system/airflow-scheduler.service`
```ini
[Unit]
Description=Airflow Scheduler
After=network.target postgresql.service rabbitmq-server.service
Wants=postgresql.service rabbitmq-server.service

[Service]
User=ubuntu
Group=ubuntu
Type=simple
WorkingDirectory=/home/ubuntu/airflow-cluster
Environment="AIRFLOW_HOME=/home/ubuntu/airflow-cluster/airflow_data"
ExecStart=/home/ubuntu/airflow-cluster/.venv/bin/airflow scheduler
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

### C. Servicio del Worker (Ejecutor)
Crea el archivo: `sudo nano /etc/systemd/system/airflow-worker.service`
```ini
[Unit]
Description=Airflow Celery Worker
After=network.target postgresql.service rabbitmq-server.service
Wants=postgresql.service rabbitmq-server.service

[Service]
User=ubuntu
Group=ubuntu
Type=simple
WorkingDirectory=/home/ubuntu/airflow-cluster
Environment="AIRFLOW_HOME=/home/ubuntu/airflow-cluster/airflow_data"
ExecStart=/home/ubuntu/airflow-cluster/.venv/bin/airflow celery worker
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

---

## 3. Activar y Arrancar los Servicios

Una vez creados los archivos, ejecuta los siguientes comandos para poner todo en marcha:

```bash
# 1. Recargar el sistema para que reconozca los nuevos archivos
sudo systemctl daemon-reload

# 2. Habilitar los servicios (para que inicien solos al bootear)
sudo systemctl enable airflow-webserver
sudo systemctl enable airflow-scheduler
sudo systemctl enable airflow-worker

# 3. Iniciar los servicios ahora mismo
sudo systemctl start airflow-webserver
sudo systemctl start airflow-scheduler
sudo systemctl start airflow-worker
```

---

## 4. Comandos de Control Diario

| Acción | Comando |
| :--- | :--- |
| **Ver estado** | `sudo systemctl status airflow-*` |
| **Reiniciar todo** | `sudo systemctl restart airflow-webserver airflow-scheduler airflow-worker` |
| **Detener todo** | `sudo systemctl stop airflow-*` |
| **Ver Logs en vivo** | `sudo journalctl -u airflow-webserver -f` |

---

## ❓ Preguntas Frecuentes

### ¿Y RabbitMQ? 
RabbitMQ no necesita un archivo manual porque al instalarse con `apt`, Ubuntu ya crea su propio servicio llamado `rabbitmq-server.service`. Puedes verificarlo con:
`sudo systemctl status rabbitmq-server`

### ¿Cómo sé si algo falló?
Si un servicio no arranca (sale en rojo), usa este comando para ver el error exacto:
`sudo journalctl -u airflow-webserver -n 50 --no-pager`

---

> [!IMPORTANT]
> **Nota sobre Airflow 3.x:** Esta configuración utiliza `airflow api-server` para la interfaz. Asegúrate de que el puerto **8080** siga abierto en tu instancia EC2.
