-- schema_sqlite.sql
-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de establecimientos
CREATE TABLE IF NOT EXISTS establecimientos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clee TEXT,
    nom_estab TEXT,
    raz_social TEXT,
    codigo_act TEXT,
    nombre_act TEXT,
    per_ocu INTEGER,
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
    latitud REAL,
    longitud REAL,
    fecha_alta TEXT
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_municipio ON establecimientos(municipio);
CREATE INDEX IF NOT EXISTS idx_cod_postal ON establecimientos(cod_postal);
CREATE INDEX IF NOT EXISTS idx_latlong ON establecimientos(latitud, longitud);