#!/bin/bash
BACKUP_DIR="/home/apiuser/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup de base de datos
cp /home/apiuser/api_flask/database.db $BACKUP_DIR/database_$DATE.db

# Mantener solo últimos 7 días
find $BACKUP_DIR -name "database_*.db" -mtime +7 -delete

echo "Backup completado: $DATE"