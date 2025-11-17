import sqlite3
from contextlib import contextmanager
import threading

class SQLitePool:
    """Pool de conexiones para SQLite"""
    
    def __init__(self, database, max_connections=5):
        self.database = database
        self.max_connections = max_connections
        self._pool = []
        self._lock = threading.Lock()
    
    def get_connection(self):
        """Obtener una conexión del pool"""
        with self._lock:
            if self._pool:
                return self._pool.pop()
            return sqlite3.connect(self.database)
    
    def return_connection(self, conn):
        """Devolver una conexión al pool"""
        with self._lock:
            if len(self._pool) < self.max_connections:
                self._pool.append(conn)
            else:
                conn.close()
    
    @contextmanager
    def connection(self):
        """Context manager para usar conexiones"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.return_connection(conn)

# Pool global
pool = None

def init_pool(database='database.db', max_connections=10):
    """Inicializar pool de conexiones"""
    global pool
    pool = SQLitePool(database, max_connections)
    return pool

def get_pool():
    """Obtener pool de conexiones"""
    global pool
    if pool is None:
        pool = init_pool()
    return pool