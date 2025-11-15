# sqlite_source.py
from flask import Blueprint, jsonify, request
import sqlite3

sqlite_bp = Blueprint('sqlite', __name__)

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@sqlite_bp.route('/', methods=['GET'])
def get_all():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM establecimientos')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@sqlite_bp.route('/<int:id>', methods=['GET'])
def get_by_id(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM establecimientos WHERE id = ?', (id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(dict(row))

@sqlite_bp.route('/', methods=['POST'])
def create():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO establecimientos (clee, nom_estab, raz_social, codigo_act, nombre_act, per_ocu, tipo_vial, nom_vial, tipo_v_e_1, nom_v_e_1, tipo_v_e_2, nom_v_e_2, tipo_v_e_3, nom_v_e_3, numero_ext, letra_ext, edificio, edificio_e, numero_int, letra_int, tipo_asent, nomb_asent, tipoCenCom, nom_CenCom, num_local, cod_postal, cve_ent, entidad, cve_mun, municipio, cve_loc, localidad, ageb, manzana, telefono, correoelec, www, tipoUniEco, latitud, longitud, fecha_alta) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
    (data.get('clee'), data.get('nom_estab'), data.get('raz_social'), data.get('codigo_act'), data.get('nombre_act'), data.get('per_ocu'), data.get('tipo_vial'), data.get('nom_vial'), data.get('tipo_v_e_1'), data.get('nom_v_e_1'), data.get('tipo_v_e_2'), data.get('nom_v_e_2'), data.get('tipo_v_e_3'), data.get('nom_v_e_3'), data.get('numero_ext'), data.get('letra_ext'), data.get('edificio'), data.get('edificio_e'), data.get('numero_int'), data.get('letra_int'), data.get('tipo_asent'), data.get('nomb_asent'), data.get('tipoCenCom'), data.get('nom_CenCom'), data.get('num_local'), data.get('cod_postal'), data.get('cve_ent'), data.get('entidad'), data.get('cve_mun'), data.get('municipio'), data.get('cve_loc'), data.get('localidad'), data.get('ageb'), data.get('manzana'), data.get('telefono'), data.get('correoelec'), data.get('www'), data.get('tipoUniEco'), data.get('latitud'), data.get('longitud'), data.get('fecha_alta')))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': new_id}), 201

@sqlite_bp.route('/<int:id>', methods=['PUT'])
def update(id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''UPDATE establecimientos SET clee=?, nom_estab=?, raz_social=?, codigo_act=?, nombre_act=?, per_ocu=?, tipo_vial=?, nom_vial=?, tipo_v_e_1=?, nom_v_e_1=?, tipo_v_e_2=?, nom_v_e_2=?, tipo_v_e_3=?, nom_v_e_3=?, numero_ext=?, letra_ext=?, edificio=?, edificio_e=?, numero_int=?, letra_int=?, tipo_asent=?, nomb_asent=?, tipoCenCom=?, nom_CenCom=?, num_local=?, cod_postal=?, cve_ent=?, entidad=?, cve_mun=?, municipio=?, cve_loc=?, localidad=?, ageb=?, manzana=?, telefono=?, correoelec=?, www=?, tipoUniEco=?, latitud=?, longitud=?, fecha_alta=? WHERE id=?''',
    (data.get('clee'), data.get('nom_estab'), data.get('raz_social'), data.get('codigo_act'), data.get('nombre_act'), data.get('per_ocu'), data.get('tipo_vial'), data.get('nom_vial'), data.get('tipo_v_e_1'), data.get('nom_v_e_1'), data.get('tipo_v_e_2'), data.get('nom_v_e_2'), data.get('tipo_v_e_3'), data.get('nom_v_e_3'), data.get('numero_ext'), data.get('letra_ext'), data.get('edificio'), data.get('edificio_e'), data.get('numero_int'), data.get('letra_int'), data.get('tipo_asent'), data.get('nomb_asent'), data.get('tipoCenCom'), data.get('nom_CenCom'), data.get('num_local'), data.get('cod_postal'), data.get('cve_ent'), data.get('entidad'), data.get('cve_mun'), data.get('municipio'), data.get('cve_loc'), data.get('localidad'), data.get('ageb'), data.get('manzana'), data.get('telefono'), data.get('correoelec'), data.get('www'), data.get('tipoUniEco'), data.get('latitud'), data.get('longitud'), data.get('fecha_alta'), id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Updated'})

@sqlite_bp.route('/<int:id>', methods=['DELETE'])
def delete(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM establecimientos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Deleted'})
