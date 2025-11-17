## 7.2 Cron para backups automáticos

crontab -e
````

Agregar:
````
0 2 * * * /home/apiuser/backup.sh >> /home/apiuser/backup.log 2>&1

## 8. Firewall

# Permitir HTTP y HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Permitir SSH
sudo ufw allow 22/tcp

# Habilitar firewall
sudo ufw enable

## 9. Comandos Útiles

# Reiniciar servicio
sudo systemctl restart api-flask

# Ver status
sudo systemctl status api-flask

# Reload (sin downtime)
sudo systemctl reload api-flask

# Ver logs
sudo journalctl -u api-flask -n 100

# Probar configuración Nginx
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

## 10. Troubleshooting

# La API no responde

bash
# Verificar que el servicio esté corriendo
sudo systemctl status api-flask

# Ver logs de error
sudo journalctl -u api-flask -n 50

# Verificar puerto
sudo netstat -tlnp | grep 5000

## Error 502 Bad Gateway
bash
# Verificar que Gunicorn esté corriendo
ps aux | grep gunicorn

# Verificar logs de Nginx
sudo tail -f /var/log/nginx/error.log

