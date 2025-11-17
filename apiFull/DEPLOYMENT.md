# Guía de Despliegue en Producción

## 1. Preparación

### 1.1 Requisitos del Servidor

- Ubuntu 20.04 LTS o superior
- Python 3.9+
- 2GB RAM mínimo (4GB recomendado)
- 20GB disco
- Acceso root o sudo

### 1.2 Paquetes necesarios
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nginx redis-server mysql-server
```

## 2. Instalación

### 2.1 Crear usuario para la aplicación
```bash
sudo useradd -m -s /bin/bash apiuser
sudo su - apiuser
```

### 2.2 Clonar y configurar
```bash
cd /home/apiuser
git clone <tu-repo> api_flask
cd api_flask

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2.3 Configurar variables de entorno
```bash
cp .env.example .env
nano .env

# Configurar valores de producción:
# - SECRET_KEY: generar con: python -c "import secrets; print(secrets.token_hex(32))"
# - JWT_SECRET_KEY: generar con: python -c "import secrets; print(secrets.token_hex(32))"
# - FLASK_ENV=production
# - DEBUG=False
```

### 2.4 Inicializar base de datos
```bash
python scripts/init_db.py
```

## 3. Systemd Service

### 3.1 Crear archivo de servicio
```bash
sudo nano /etc/systemd/system/api-flask.service
```

Contenido:
```ini
[Unit]
Description=API Flask con Gunicorn
After=network.target

[Service]
Type=notify
User=apiuser
Group=apiuser
WorkingDirectory=/home/apiuser/api_flask
Environment="PATH=/home/apiuser/api_flask/venv/bin"
ExecStart=/home/apiuser/api_flask/venv/bin/gunicorn -c gunicorn_config.py "app:create_app()"
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3.2 Habilitar y arrancar
```bash
sudo systemctl daemon-reload
sudo systemctl enable api-flask
sudo systemctl start api-flask
sudo systemctl status api-flask
```

## 4. Nginx como Reverse Proxy

### 4.1 Configurar Nginx
```bash
sudo nano /etc/nginx/sites-available/api-flask
```

Contenido:
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:5000/health;
    }
}
```

### 4.2 Habilitar sitio
```bash
sudo ln -s /etc/nginx/sites-available/api-flask /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 5. SSL con Let's Encrypt
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

## 6. Monitoreo y Logs

### 6.1 Ver logs en tiempo real
```bash
# Logs de la aplicación
tail -f /home/apiuser/api_flask/logs/api.log

# Logs de systemd
sudo journalctl -u api-flask -f

# Logs de Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 6.2 Configurar rotación de logs
```bash
sudo nano /etc/logrotate.d/api-flask
```