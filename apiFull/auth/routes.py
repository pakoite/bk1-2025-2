from flask import Blueprint, request, jsonify
from auth.jwt_handler import JWTHandler
from auth.decorators import token_required, admin_required
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from validators.schemas import UserSchema, UserLoginSchema
from marshmallow import ValidationError

auth_bp = Blueprint('auth', __name__)

def get_db():
    """Obtener conexión a base de datos"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Endpoint para registrar nuevos usuarios
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
            - email
          properties:
            username:
              type: string
            password:
              type: string
            email:
              type: string
    responses:
      201:
        description: Usuario creado exitosamente
      400:
        description: Datos inválidos
      409:
        description: Usuario ya existe
    """
    schema = UserSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            'success': False,
            'message': 'Error de validación',
            'errors': err.messages
        }), 422
    
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)',
            (data['username'], hashed_password, data.get('email'), 'user')
        )
        conn.commit()
        user_id = cursor.lastrowid
        
        return jsonify({
            'success': True,
            'message': 'Usuario registrado exitosamente',
            'data': {'user_id': user_id, 'username': data['username']}
        }), 201
        
    except sqlite3.IntegrityError:
        return jsonify({
            'success': False,
            'message': 'El usuario ya existe'
        }), 409
    finally:
        conn.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Endpoint para autenticar usuarios
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login exitoso
      401:
        description: Credenciales incorrectas
      404:
        description: Usuario no encontrado
    """
    schema = UserLoginSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            'success': False,
            'message': 'Error de validación',
            'errors': err.messages
        }), 422
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM users WHERE username = ?',
        (data['username'],)
    )
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return jsonify({
            'success': False,
            'message': 'Usuario no encontrado'
        }), 404
    
    if not check_password_hash(user['password'], data['password']):
        return jsonify({
            'success': False,
            'message': 'Contraseña incorrecta'
        }), 401
    
    token = JWTHandler.generate_token(user['id'], user['username'], user['role'])
    
    return jsonify({
        'success': True,
        'message': 'Login exitoso',
        'data': {
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
        }
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """
    Obtener perfil del usuario autenticado
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Perfil del usuario
      401:
        description: No autenticado
    """
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT id, username, email, role, created_at FROM users WHERE id = ?',
        (current_user['user_id'],)
    )
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return jsonify({
            'success': False,
            'message': 'Usuario no encontrado'
        }), 404
    
    return jsonify({
        'success': True,
        'data': dict(user)
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Actualizar perfil del usuario"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        'UPDATE users SET email = ? WHERE id = ?',
        (data.get('email'), current_user['user_id'])
    )
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'Perfil actualizado exitosamente'
    }), 200

@auth_bp.route('/admin/users', methods=['GET'])
@admin_required
def list_users(current_user):
    """Listar todos los usuarios (solo admin)"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, email, role, created_at FROM users')
    users = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'success': True,
        'data': [dict(user) for user in users]
    }), 200