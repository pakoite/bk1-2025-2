from functools import wraps
from flask import request, jsonify
from auth.jwt_handler import JWTHandler

def token_required(f):
    """
    Decorador para proteger endpoints que requieren autenticación
    
    Uso:
        @app.route('/protected')
        @token_required
        def protected_route(current_user):
            return {'user': current_user['username']}
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({
                    'success': False,
                    'message': 'Formato de token inválido. Use: Bearer <token>'
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token de autenticación requerido'
            }), 401
        
        payload = JWTHandler.decode_token(token)
        
        if 'error' in payload:
            return jsonify({
                'success': False,
                'message': payload['error']
            }), 401
        
        return f(current_user=payload, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """
    Decorador para endpoints que requieren rol de administrador
    
    Uso:
        @app.route('/admin/users')
        @admin_required
        def manage_users(current_user):
            return {'users': [...]}
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({
                    'success': False,
                    'message': 'Formato de token inválido'
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token requerido'
            }), 401
        
        payload = JWTHandler.decode_token(token)
        
        if 'error' in payload:
            return jsonify({
                'success': False,
                'message': payload['error']
            }), 401
        
        if payload.get('role') != 'admin':
            return jsonify({
                'success': False,
                'message': 'Se requieren permisos de administrador'
            }), 403
        
        return f(current_user=payload, *args, **kwargs)
    
    return decorated