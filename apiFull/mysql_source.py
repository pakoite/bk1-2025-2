from flask import Blueprint, jsonify, request, current_app
from database.mysql_pool import get_mysql_pool
from validators.schemas import EstablecimientoSchema, EstablecimientoUpdateSchema, PaginationSchema
from marshmallow import ValidationError
from auth.decorators import token_required

mysql_bp = Blueprint('mysql', __name__)

cache = None

def init_cache(cache_instance):
    """Inicializar cache"""
    global cache
    cache = cache_instance

@mysql_bp.route('/', methods=['GET'])
def get_all():
    """
    Obtener todos los establecimientos con paginación
    ---
    tags:
      - MySQL
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
        
        pool = get_mysql_pool()
        if pool is None:
            return jsonify({
                'success': False,
                'message': 'Pool de MySQL no inicializado'
            }), 500
        
        with pool.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Total de registros
            cursor.execute('SELECT COUNT(*) as total FROM establecimientos')
            total = cursor.fetchone()['total']
            
            # Datos paginados
            cursor.execute(
                'SELECT * FROM establecimientos LIMIT %s OFFSET %s',
                (per_page, offset)
            )
            rows = cursor.fetchall()
            cursor.close()
            
            total_pages = (total + per_page - 1) // per_page
            
            return jsonify({
                'success': True,
                'data': rows,
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

@mysql_bp.route('/<int:id>', methods=['GET'])
def get_by_id(id):
    """Obtener establecimiento por ID"""
    try:
        pool = get_mysql_pool()
        with pool.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM establecimientos WHERE id = %s', (id,))
            row = cursor.fetchone()
            cursor.close()
            
            if row is None:
                return jsonify({
                    'success': False,
                    'message': 'Establecimiento no encontrado'
                }), 404
            
            return jsonify({
                'success': True,
                'data': row
            }), 200
            
    except Exception as e:
        current_app.logger.error(f'Error: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Error al obtener establecimiento'
        }), 500

@mysql_bp.route('/', methods=['POST'])
@token_required
def create(current_user):
    """Crear nuevo establecimiento"""
    schema = EstablecimientoSchema()
    
    try:
        validated_data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            'success': False,
            'errors': err.messages
        }), 422
    
    try:
        pool = get_mysql_pool()
        with pool.connection() as conn:
            cursor = conn.cursor()
            
            columns = ', '.join(validated_data.keys())
            placeholders = ', '.join(['%s' for _ in validated_data])
            values = list(validated_data.values())
            
            cursor.execute(
                f'INSERT INTO establecimientos ({columns}) VALUES ({placeholders})',
                values
            )
            
            new_id = cursor.lastrowid
            cursor.close()
            
            current_app.logger.info(
                f'Usuario {current_user["username"]} creó establecimiento {new_id}'
            )
            
            return jsonify({
                'success': True,
                'message': 'Establecimiento creado exitosamente',
                'data': {'id': new_id}
            }), 201
            
    except Exception as e:
        current_app.logger.error(f'Error: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Error al crear establecimiento'
        }), 500

@mysql_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update(current_user, id):
    """Actualizar establecimiento"""
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
        pool = get_mysql_pool()
        with pool.connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM establecimientos WHERE id = %s', (id,))
            if cursor.fetchone() is None:
                cursor.close()
                return jsonify({
                    'success': False,
                    'message': 'Establecimiento no encontrado'
                }), 404
            
            set_clause = ', '.join([f'{key} = %s' for key in validated_data.keys()])
            values = list(validated_data.values()) + [id]
            
            cursor.execute(
                f'UPDATE establecimientos SET {set_clause} WHERE id = %s',
                values
            )
            cursor.close()
            
            current_app.logger.info(
                f'Usuario {current_user["username"]} actualizó establecimiento {id}'
            )
            
            return jsonify({
                'success': True,
                'message': 'Establecimiento actualizado exitosamente'
            }), 200
            
    except Exception as e:
        current_app.logger.error(f'Error: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Error al actualizar establecimiento'
        }), 500

@mysql_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete(current_user, id):
    """Eliminar establecimiento"""
    try:
        pool = get_mysql_pool()
        with pool.connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM establecimientos WHERE id = %s', (id,))
            if cursor.fetchone() is None:
                cursor.close()
                return jsonify({
                    'success': False,
                    'message': 'Establecimiento no encontrado'
                }), 404
            
            cursor.execute('DELETE FROM establecimientos WHERE id = %s', (id,))
            cursor.close()
            
            current_app.logger.info(
                f'Usuario {current_user["username"]} eliminó establecimiento {id}'
            )
            
            return jsonify({
                'success': True,
                'message': 'Establecimiento eliminado exitosamente'
            }), 200
            
    except Exception as e:
        current_app.logger.error(f'Error: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Error al eliminar establecimiento'
        }), 500