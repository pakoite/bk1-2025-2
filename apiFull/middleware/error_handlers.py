from flask import jsonify
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError
import sqlite3

def register_error_handlers(app):
    """
    Registra todos los manejadores de error en la aplicación
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'message': 'Solicitud incorrecta',
            'status_code': 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'message': 'No autenticado. Token requerido',
            'status_code': 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'message': 'Acceso denegado. Permisos insuficientes',
            'status_code': 403
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Recurso no encontrado',
            'status_code': 404
        }), 404
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        return jsonify({
            'success': False,
            'message': 'Demasiadas solicitudes. Intenta más tarde',
            'status_code': 429,
            'retry_after': error.description
        }), 429
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify({
            'success': False,
            'message': 'Error de validación',
            'status_code': 422,
            'errors': error.messages
        }), 422
    
    @app.errorhandler(sqlite3.IntegrityError)
    def handle_sqlite_integrity_error(error):
        return jsonify({
            'success': False,
            'message': 'Error de integridad de datos',
            'status_code': 409,
            'details': 'El registro ya existe o viola una restricción'
        }), 409
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({
            'success': False,
            'message': error.description,
            'status_code': error.code
        }), error.code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        app.logger.error(f'Excepción no manejada: {str(error)}', exc_info=True)
        
        if app.config.get('DEBUG'):
            message = str(error)
        else:
            message = 'Ocurrió un error interno'
        
        return jsonify({
            'success': False,
            'message': message,
            'status_code': 500
        }), 500