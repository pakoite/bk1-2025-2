from flask import Blueprint, jsonify, request
import pandas as pd
from flask import current_app
from validators.schemas import PaginationSchema
from marshmallow import ValidationError

excel_bp = Blueprint('excel', __name__)

cache = None

def init_cache(cache_instance):
    """Inicializar cache para este módulo"""
    global cache
    cache = cache_instance

@excel_bp.route('/', methods=['GET'])
def get_all():
    """
    Obtener todos los registros del Excel con paginación
    ---
    tags:
      - Excel
    parameters:
      - name: page
        in: query
        type: integer
        description: Número de página
      - name: per_page
        in: query
        type: integer
        description: Registros por página (max 100)
    responses:
      200:
        description: Lista de establecimientos
      400:
        description: Parámetros inválidos
    """
    try:
        # Validar parámetros de paginación
        schema = PaginationSchema()
        params = schema.load(request.args)
        
        page = params['page']
        per_page = params['per_page']
        
        # Leer Excel
        df = pd.read_excel(current_app.config['EXCEL_PATH'])
        
        # Calcular paginación
        total = len(df)
        offset = (page - 1) * per_page
        
        # Obtener datos de la página
        paginated_df = df.iloc[offset:offset + per_page]
        
        total_pages = (total + per_page - 1) // per_page
        
        return jsonify({
            'success': True,
            'data': paginated_df.to_dict(orient='records'),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }), 200
        
    except FileNotFoundError:
        current_app.logger.error(f'Archivo Excel no encontrado: {current_app.config["EXCEL_PATH"]}')
        return jsonify({
            'success': False,
            'message': 'Archivo Excel no encontrado'
        }), 404
    except ValidationError as err:
        return jsonify({
            'success': False,
            'message': 'Parámetros inválidos',
            'errors': err.messages
        }), 400
    except Exception as e:
        current_app.logger.error(f'Error leyendo Excel: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Error al leer archivo Excel'
        }), 500

@excel_bp.route('/<int:id>', methods=['GET'])
def get_by_id(id):
    """
    Obtener registro por ID
    ---
    tags:
      - Excel
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Registro encontrado
      404:
        description: Registro no encontrado
    """
    try:
        df = pd.read_excel(current_app.config['EXCEL_PATH'])
        record = df[df['id'] == id]
        
        if record.empty:
            return jsonify({
                'success': False,
                'message': 'Registro no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': record.to_dict(orient='records')[0]
        }), 200
        
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'message': 'Archivo Excel no encontrado'
        }), 404
    except Exception as e:
        current_app.logger.error(f'Error leyendo Excel: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Error al leer archivo'
        }), 500

@excel_bp.route('/search', methods=['GET'])
def search():
    """
    Buscar registros por municipio o código postal
    ---
    tags:
      - Excel
    parameters:
      - name: municipio
        in: query
        type: string
      - name: cod_postal
        in: query
        type: string
    responses:
      200:
        description: Resultados de búsqueda
    """
    try:
        df = pd.read_excel(current_app.config['EXCEL_PATH'])
        
        municipio = request.args.get('municipio')
        cod_postal = request.args.get('cod_postal')
        
        if municipio:
            df = df[df['municipio'].str.contains(municipio, case=False, na=False)]
        
        if cod_postal:
            df = df[df['cod_postal'] == cod_postal]
        
        return jsonify({
            'success': True,
            'data': df.to_dict(orient='records'),
            'count': len(df)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Error en búsqueda: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Error en búsqueda'
        }), 500