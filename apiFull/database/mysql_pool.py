import mysql.connector
from mysql.connector import pooling
from contextlib import contextmanager

class MySQLPool:
    """Pool de conexiones para MySQL"""
    
    def __init__(self, pool_name, pool_size, **config):
        self.pool = pooling.MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=pool_size,
            pool_reset_session=True,
            **config
        )
    
    @contextmanager
    def connection(self):
        """Context manager para usar conexiones"""
        conn = self.pool.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

# Pool global
mysql_pool = None

def init_mysql_pool(config):
    """Inicializar pool de MySQL"""
    global mysql_pool
    try:
        mysql_pool = MySQLPool(
            pool_name="api_pool",
            pool_size=10,
            host=config.get('MYSQL_HOST'),
            user=config.get('MYSQL_USER'),
            password=config.get('MYSQL_PASSWORD'),
            database=config.get('MYSQL_DB'),
            port=config.get('MYSQL_PORT', 3306)
        )
    except Exception:
        # Si falla la conexión, no detener la app
        pass
    return mysql_pool

def get_mysql_pool():
    """Obtener pool de MySQL"""
    global mysql_pool
    return mysql_pool