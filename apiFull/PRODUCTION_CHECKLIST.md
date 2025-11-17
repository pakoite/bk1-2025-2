# Checklist para Producción

## Seguridad ✅

- [ ] Cambiar `SECRET_KEY` en .env por una clave fuerte y aleatoria
- [ ] Cambiar `JWT_SECRET_KEY` por una clave diferente y fuerte
- [ ] Configurar `ALLOWED_ORIGINS` con los dominios reales
- [ ] Configurar HTTPS/SSL
- [ ] Revisar permisos de archivos (database.db, logs/)
- [ ] Deshabilitar DEBUG en .env (`DEBUG=False`)
- [ ] Configurar `FLASK_ENV=production`

## Base de Datos ✅

- [ ] Configurar backups automáticos
- [ ] Verificar índices en tablas grandes
- [ ] Configurar límites de conexión apropiados
- [ ] Testear restore de backups
- [ ] Configurar replicación (opcional)

## Performance ✅

- [ ] Configurar Redis para cache y rate limiting
- [ ] Ajustar workers de Gunicorn según CPU disponible
- [ ] Configurar CDN para archivos estáticos (si aplica)
- [ ] Implementar compresión Gzip
- [ ] Monitorear uso de memoria

## Monitoreo ✅

- [ ] Configurar alertas de errores
- [ ] Implementar APM (New Relic, DataDog, etc.)
- [ ] Configurar rotación de logs
- [ ] Monitorear métricas de CPU/RAM/Disco
- [ ] Health checks automáticos

## Deployment ✅

- [ ] Configurar CI/CD pipeline
- [ ] Documentar proceso de deployment
- [ ] Configurar rollback automático
- [ ] Testear en ambiente de staging
- [ ] Preparar runbook para incidentes

## Testing ✅

- [ ] Ejecutar todos los tests
- [ ] Verificar cobertura > 80%
- [ ] Tests de carga/stress
- [ ] Tests de seguridad
- [ ] Validar todos los endpoints

## Documentación ✅

- [ ] README actualizado
- [ ] Swagger/OpenAPI completo
- [ ] Documentar variables de entorno
- [ ] Documentar proceso de instalación
- [ ] Documentar troubleshooting común

## Legal/Compliance ✅

- [ ] Política de privacidad
- [ ] Términos de servicio
- [ ] GDPR compliance (si aplica)
- [ ] Registros de auditoría
- [ ] Rate limiting apropiado