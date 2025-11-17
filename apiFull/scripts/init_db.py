#!/usr/bin/env python
"""
Script para inicializar la base de datos con datos de ejemplo
"""

import sqlite3
import sys

def init_database():
    """Inicializar base de datos con schema y datos de ejemplo"""
    
    print("Inicializando base de datos...")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Leer y ejecutar schema
        with open('schema_sqlite.sql', 'r') as f:
            cursor.executescript(f.read())
        
        print("✓ Schema creado exitosamente")
        
        # Insertar usuario admin de ejemplo
        from werkzeug.security import generate_password_hash
        
        admin_password = generate_password_hash('admin123', method='pbkdf2:sha256')
        
        cursor.execute(
            'INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)',
            ('admin', admin_password, 'admin@example.com', 'admin')
        )
        
        print("✓ Usuario admin creado (username: admin, password: admin123)")
        
        # Insertar algunos establecimientos de ejemplo
        establecimientos = [
            ('EST001', 'Establecimiento Demo 1', 'Ciudad de México', '01000', 19.4326, -99.1332),
            ('EST002', 'Establecimiento Demo 2', 'Guadalajara', '44100', 20.6597, -103.3496),
            ('EST003', 'Establecimiento Demo 3', 'Monterrey', '64000', 25.6866, -100.3161),
        ]
        
        for est in establecimientos:
            cursor.execute(
                'INSERT INTO establecimientos (clee, nom_estab, municipio, cod_postal, latitud, longitud) VALUES (?, ?, ?, ?, ?, ?)',
                est
            )
        
        print(f"✓ {len(establecimientos)} establecimientos de ejemplo creados")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Base de datos inicializada correctamente")
        print("\n📝 Credenciales de prueba:")
        print("   Username: admin")
        print("   Password: admin123")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error inicializando base de datos: {e}")
        return False

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)