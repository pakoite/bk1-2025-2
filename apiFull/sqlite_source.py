from flask import Blueprint, jsonify, request, current_app
from database.sqlite_pool import get_pool
from validators.schemas import EstablecimientoSchema, EstablecimientoUpdateSchema, PaginationSchema
from marshmallow import ValidationError
from auth.decorators import token_required

sqlite_bp = Blueprint('sqlite', __name__)

cache = None

def init_cache(cache_instance):
    """Inicializar cache"""
    global cache
    cache = cache_instance

@sqlite_bp.route('/', methods=['GET'])
def get_all():
    """
    Obtener todos los establecimientos con paginación
    ---
    tags:
      - SQLite
    parameters:
      - name: page
        in: query
        type: integer
      - name: per_page
        in: query
        type: integer
    responses:
      200:
        description: Lista de establecimientos
    """
    try:
        schema = PaginationSchema()
        params = schema.load(request.args)
        
        page = params['page']
        per_page = params['per_page']
        offset = (page - 1) * per_page
        
        pool = get_pool()
        with pool.connection() as conn:
            cursor = conn.cursor()
            
            # Total de registros
            cursor.execute('SELECT COUNT(*) FROM establecimientos')
            total = cursor.fetchone()[0]
            
            # Datos paginados
            cursor.execute(
                'SELECT * FROM establecimientos LIMIT ? OFFSET ?',
                (per_page, offset)
            )
            rows = cursor.fetchall()
            
            total_pages = (total + per_page - 1) // per_page
            
            return jsonify({
                'success': True,
                'data': [dict(row) for row in rows],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                }
            }), 200
            
    except ValidationError as err:
        return jsonify({
            'success': False,
            'errors': err.messages
        }), 400
    except Exception as e:
        current_app.logger.error(f'Error obteniendo establecimientos: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Error al obtener datos'
        }), 500

@sqlite_bp.route('/<int:id>', methods=['GET'])
def get_by_id(id):
    """
    Obtener establecimiento por ID
    ---
    tags:
      - SQLite
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Establecimiento encontrado
      404:
        description: No encontrado
    """
    try:
        pool = get_pool()
        with pool.connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM establecimientos WHERE id = ?', (id,))
            row = cursor.fetchone()
            
            if row is None:
                return jsonify({
                    'success': False,
                    'message': 'Establecimiento no encontrado'
                }), 404
            
            return jsonify({
                'success': True,
                'data': dict(row)
            }), 200
            
    except Exception as e:
        current_app.logger.error(f'Error obteniendo establecimiento {id}: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Error al obtener establecimiento'
        }), 500

@sqlite_bp.route('/', methods=['POST'])
@token_required
def create(current_user):
    """
    Crear nuevo establecimiento
    ---
    tags:
      - SQLite
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
    responses:
      201:
        description: Creado exitosamente
      422:
        description: Error de validación
    """
    schema = EstablecimientoSchema()
    
    try:
        validated_data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            'success': False,
            'message': 'Error de validación',
            'errors': err.messages
        }), 422
    
    try:
        pool = get_pool()
        with pool.connection() as conn:
            cursor = conn.cursor()
            
            # Construir query dinámicamente
            columns = ', '.join(validated_data.keys())
            placeholders = ', '.join(['?' for _ in validated_data])
            values = list(validated_data.values())
            
            cursor.execute(
                f'INSERT INTO establecimientos ({columns}) VALUES ({placeholders})',
                values
            )
            
            new_id = cursor.lastrowid
            
            current_app.logger.info(
                f'Usuario {current_user["username"]} creó establecimiento {new_id}'
            )
            
            return jsonify({
                'success': True,
                'message': 'Establecimiento creado exitosamente',
                'data': {'id': new_id}
            }), 201
            
    except Exception as e:
        current_app.logger.error(f'Error creando establecimiento: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Error al crear establecimiento'
        }), 500

@sqlite_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update(current_user, id):
    """
    Actualizar establecimiento
    ---
    tags:
      - SQLite
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
    responses:
      200:
        description: Actualizado exitosamente
      404:
        description: No encontrado
    """
    schema = EstablecimientoUpdateSchema()
    
    try:
        validated_data = schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify({
            'success': False,
            'errors': err.messages
        }), 422
    
    if not validated_data:
        return jsonify({
            'success': False,
            'message': 'No hay datos para actualizar'
        }), 400
    
    try:
        pool = get_pool()
        with pool.connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que existe
            cursor.execute('SELECT id FROM establecimientos WHERE id = ?', (id,))
            if cursor.fetchone() is None:
                return jsonify({
                    'success': False,
                    'message': 'Establecimiento no encontrado'
                }), 404
            
            # Construir query de actualización
            set_clause = ', '.join([f'{key} = ?' for key in validated_data.keys()])
            values = list(validated_data.values()) + [id]
            
            cursor.execute(
                f'UPDATE establecimientos SET {set_clause} WHERE id = ?',
                values
            )
            
            current_app.logger.info(
                f'Usuario {current_user["username"]} actualizó establecimiento {id}'
            )
            
            return jsonify({
                'success': True,
                'message': 'Establecimiento actualizado exitosamente'
            }), 200
            
    except Exception as e:
        current_app.logger.error(f'Error actualizando establecimiento {id}: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Error al actualizar establecimiento'
        }), 500

@sqlite_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete(current_user, id):
    """
    Eliminar establecimiento
    ---
    tags:
      - SQLite
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Eliminado exitosamente
      404:
        description: No encontrado
    """
    try:
        pool = get_pool()
        with pool.connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que existe
            cursor.execute('SELECT id FROM establecimientos WHERE id = ?', (id,))
            if cursor.fetchone() is None:
                return jsonify({
                    'success': False,
                    'message': 'Establecimiento no encontrado'
                }), 404
            
            cursor.execute('DELETE FROM establecimientos WHERE id = ?', (id,))
            
            current_app.logger.info(
                f'Usuario {current_user["username"]} eliminó establecimiento {id}'
            )
            
            return jsonify({
                'success': True,
                'message': 'Establecimiento eliminado exitosamente'
            }), 200
            
    except Exception as e:
        current_app.logger.error(f'Error eliminando establecimiento {id}: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Error al eliminar establecimiento'
        }), 500