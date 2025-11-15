# API Flask Multi-Source

API REST desarrollada en Flask que integra múltiples fuentes de datos: Excel, SQLite y MySQL.

## Características

- **Excel**: Endpoints de solo lectura
- **SQLite**: CRUD completo
- **MySQL**: CRUD completo

## Estructura del Proyecto

```
.
├── app.py
├── excel_source.py
├── sqlite_source.py
├── mysql_source.py
├── requirements.txt
├── data.xlsx
├── database.db
└── README.md
```

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

### SQLite

Crear la tabla en `database.db`:

```sql
CREATE TABLE establecimientos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clee TEXT,
    nom_estab TEXT,
    raz_social TEXT,
    codigo_act TEXT,
    nombre_act TEXT,
    per_ocu TEXT,
    tipo_vial TEXT,
    nom_vial TEXT,
    tipo_v_e_1 TEXT,
    nom_v_e_1 TEXT,
    tipo_v_e_2 TEXT,
    nom_v_e_2 TEXT,
    tipo_v_e_3 TEXT,
    nom_v_e_3 TEXT,
    numero_ext TEXT,
    letra_ext TEXT,
    edificio TEXT,
    edificio_e TEXT,
    numero_int TEXT,
    letra_int TEXT,
    tipo_asent TEXT,
    nomb_asent TEXT,
    tipoCenCom TEXT,
    nom_CenCom TEXT,
    num_local TEXT,
    cod_postal TEXT,
    cve_ent TEXT,
    entidad TEXT,
    cve_mun TEXT,
    municipio TEXT,
    cve_loc TEXT,
    localidad TEXT,
    ageb TEXT,
    manzana TEXT,
    telefono TEXT,
    correoelec TEXT,
    www TEXT,
    tipoUniEco TEXT,
    latitud TEXT,
    longitud TEXT,
    fecha_alta TEXT
);
```

### MySQL

Configurar credenciales en `mysql_source.py`:

```python
host='localhost'
user='root'
password='password'
database='establecimientos_db'
```

Crear la base de datos y tabla:

```sql
CREATE DATABASE establecimientos_db;
USE establecimientos_db;

CREATE TABLE establecimientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    clee VARCHAR(255),
    nom_estab VARCHAR(255),
    raz_social VARCHAR(255),
    codigo_act VARCHAR(255),
    nombre_act VARCHAR(255),
    per_ocu VARCHAR(255),
    tipo_vial VARCHAR(255),
    nom_vial VARCHAR(255),
    tipo_v_e_1 VARCHAR(255),
    nom_v_e_1 VARCHAR(255),
    tipo_v_e_2 VARCHAR(255),
    nom_v_e_2 VARCHAR(255),
    tipo_v_e_3 VARCHAR(255),
    nom_v_e_3 VARCHAR(255),
    numero_ext VARCHAR(255),
    letra_ext VARCHAR(255),
    edificio VARCHAR(255),
    edificio_e VARCHAR(255),
    numero_int VARCHAR(255),
    letra_int VARCHAR(255),
    tipo_asent VARCHAR(255),
    nomb_asent VARCHAR(255),
    tipoCenCom VARCHAR(255),
    nom_CenCom VARCHAR(255),
    num_local VARCHAR(255),
    cod_postal VARCHAR(255),
    cve_ent VARCHAR(255),
    entidad VARCHAR(255),
    cve_mun VARCHAR(255),
    municipio VARCHAR(255),
    cve_loc VARCHAR(255),
    localidad VARCHAR(255),
    ageb VARCHAR(255),
    manzana VARCHAR(255),
    telefono VARCHAR(255),
    correoelec VARCHAR(255),
    www VARCHAR(255),
    tipoUniEco VARCHAR(255),
    latitud VARCHAR(255),
    longitud VARCHAR(255),
    fecha_alta VARCHAR(255)
);
```

### Excel

Colocar archivo `data.xlsx` en la raíz del proyecto con las columnas especificadas.

## Ejecución

```bash
python app.py
```

La API estará disponible en `http://localhost:5000`

## Endpoints

### Excel (Solo Lectura)

```
GET /api/excel/           - Obtener todos los registros
GET /api/excel/<id>       - Obtener registro por ID
```

### SQLite (CRUD Completo)

```
GET    /api/sqlite/       - Obtener todos los registros
GET    /api/sqlite/<id>   - Obtener registro por ID
POST   /api/sqlite/       - Crear nuevo registro
PUT    /api/sqlite/<id>   - Actualizar registro
DELETE /api/sqlite/<id>   - Eliminar registro
```

### MySQL (CRUD Completo)

```
GET    /api/mysql/        - Obtener todos los registros
GET    /api/mysql/<id>    - Obtener registro por ID
POST   /api/mysql/        - Crear nuevo registro
PUT    /api/mysql/<id>    - Actualizar registro
DELETE /api/mysql/<id>    - Eliminar registro
```

## Ejemplos de Uso

### Obtener todos los registros (Excel)

```bash
curl http://localhost:5000/api/excel/
```

### Crear registro (SQLite)

```bash
curl -X POST http://localhost:5000/api/sqlite/ \
  -H "Content-Type: application/json" \
  -d '{"clee":"123","nom_estab":"Establecimiento 1","raz_social":"Razón Social"}'
```

### Actualizar registro (MySQL)

```bash
curl -X PUT http://localhost:5000/api/mysql/1 \
  -H "Content-Type: application/json" \
  -d '{"nom_estab":"Nuevo Nombre"}'
```

### Eliminar registro (SQLite)

```bash
curl -X DELETE http://localhost:5000/api/sqlite/1
```
