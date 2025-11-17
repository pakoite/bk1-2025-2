# mysql_source.py
from flask import Blueprint, jsonify, request
import mysql.connector

mysql_bp = Blueprint('mysql', __name__)

def get_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',
        database='establecimientos_db'
    )

@mysql_bp.route('/', methods=['GET'])
def get_all():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM establecimientos')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

@mysql_bp.route('/<int:id>', methods=['GET'])
def get_by_id(id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM establecimientos WHERE id = %s', (id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row is None:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(row)

@mysql_bp.route('/', methods=['POST'])
def create():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO establecimientos (clee, nom_estab, raz_social, codigo_act, nombre_act, per_ocu, tipo_vial, nom_vial, tipo_v_e_1, nom_v_e_1, tipo_v_e_2, nom_v_e_2, tipo_v_e_3, nom_v_e_3, numero_ext, letra_ext, edificio, edificio_e, numero_int, letra_int, tipo_asent, nomb_asent, tipoCenCom, nom_CenCom, num_local, cod_postal, cve_ent, entidad, cve_mun, municipio, cve_loc, localidad, ageb, manzana, telefono, correoelec, www, tipoUniEco, latitud, longitud, fecha_alta) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
    (data.get('clee'), data.get('nom_estab'), data.get('raz_social'), data.get('codigo_act'), data.get('nombre_act'), data.get('per_ocu'), data.get('tipo_vial'), data.get('nom_vial'), data.get('tipo_v_e_1'), data.get('nom_v_e_1'), data.get('tipo_v_e_2'), data.get('nom_v_e_2'), data.get('tipo_v_e_3'), data.get('nom_v_e_3'), data.get('numero_ext'), data.get('letra_ext'), data.get('edificio'), data.get('edificio_e'), data.get('numero_int'), data.get('letra_int'), data.get('tipo_asent'), data.get('nomb_asent'), data.get('tipoCenCom'), data.get('nom_CenCom'), data.get('num_local'), data.get('cod_postal'), data.get('cve_ent'), data.get('entidad'), data.get('cve_mun'), data.get('municipio'), data.get('cve_loc'), data.get('localidad'), data.get('ageb'), data.get('manzana'), data.get('telefono'), data.get('correoelec'), data.get('www'), data.get('tipoUniEco'), data.get('latitud'), data.get('longitud'), data.get('fecha_alta')))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({'id': new_id}), 201

@mysql_bp.route('/<int:id>', methods=['PUT'])
def update(id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''UPDATE establecimientos SET clee=%s, nom_estab=%s, raz_social=%s, codigo_act=%s, nombre_act=%s, per_ocu=%s, tipo_vial=%s, nom_vial=%s, tipo_v_e_1=%s, nom_v_e_1=%s, tipo_v_e_2=%s, nom_v_e_2=%s, tipo_v_e_3=%s, nom_v_e_3=%s, numero_ext=%s, letra_ext=%s, edificio=%s, edificio_e=%s, numero_int=%s, letra_int=%s, tipo_asent=%s, nomb_asent=%s, tipoCenCom=%s, nom_CenCom=%s, num_local=%s, cod_postal=%s, cve_ent=%s, entidad=%s, cve_mun=%s, municipio=%s, cve_loc=%s, localidad=%s, ageb=%s, manzana=%s, telefono=%s, correoelec=%s, www=%s, tipoUniEco=%s, latitud=%s, longitud=%s, fecha_alta=%s WHERE id=%s''',
    (data.get('clee'), data.get('nom_estab'), data.get('raz_social'), data.get('codigo_act'), data.get('nombre_act'), data.get('per_ocu'), data.get('tipo_vial'), data.get('nom_vial'), data.get('tipo_v_e_1'), data.get('nom_v_e_1'), data.get('tipo_v_e_2'), data.get('nom_v_e_2'), data.get('tipo_v_e_3'), data.get('nom_v_e_3'), data.get('numero_ext'), data.get('letra_ext'), data.get('edificio'), data.get('edificio_e'), data.get('numero_int'), data.get('letra_int'), data.get('tipo_asent'), data.get('nomb_asent'), data.get('tipoCenCom'), data.get('nom_CenCom'), data.get('num_local'), data.get('cod_postal'), data.get('cve_ent'), data.get('entidad'), data.get('cve_mun'), data.get('municipio'), data.get('cve_loc'), data.get('localidad'), data.get('ageb'), data.get('manzana'), data.get('telefono'), data.get('correoelec'), data.get('www'), data.get('tipoUniEco'), data.get('latitud'), data.get('longitud'), data.get('fecha_alta'), id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Updated'})

@mysql_bp.route('/<int:id>', methods=['DELETE'])
def delete(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM establecimientos WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Deleted'})
