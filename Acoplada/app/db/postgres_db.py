import os
import psycopg2
import psycopg2.extras
import json # Mirar por si desacoplado
from typing import List, Optional
from .db import Database
from models.item import Item 

DB_URL = os.getenv('DATABASE_URL')

class PostgresDatabase(Database):
    """
    Implementación de la interfaz Database para PostgreSQL,
    gestionando la tabla 'items' (personas).
    """

    def __init__(self):
        # NOTA: Evitar establecer la conexión en __init__ para aplicaciones Fargate/Lambda.
        # Es mejor usar un pool o establecer la conexión por método, pero por simplicidad
        # de laboratorio, la mantendremos aquí y usaremos una función helper.
        pass

    def _get_connection(self):
        """Método helper para obtener una nueva conexión a la DB a partir de la URL."""
        if not DB_URL:
            # En Fargate, esta URL se debe construir a partir de HOST, USER, PASS, etc.
            # o pasarse completa como variable de entorno.
            host = os.getenv('DB_HOST')
            user = os.getenv('DB_USER')
            password = os.getenv('DB_PASS')
            database = os.getenv('DB_NAME')
            if not all([host, user, password, database]):
                 raise ValueError("Faltan variables de entorno de PostgreSQL (DB_HOST, etc.)")
            return psycopg2.connect(
                host=host, user=user, password=password, database=database
            )
        else:
            return psycopg2.connect(DB_URL)

    def initialize(self):
        """Inicializa la DB, creando la tabla 'items' si no existe."""
        conn = None
        try:
            conn = self._get_connection()
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS items (
                        id VARCHAR(15) PRIMARY KEY, -- DNI como clave primaria
                        nombre VARCHAR(100) NOT NULL,
                        apellidos VARCHAR(150) NOT NULL,
                        numero_telefono VARCHAR(20),
                        puesto_trabajo VARCHAR(50) NOT NULL 
                            CHECK (puesto_trabajo IN ('desarrollador', 'administrativo', 'notario', 'comercial'))
                    );
                """)
            print("Tabla 'items' verificada/creada exitosamente.")
        except psycopg2.Error as e:
            print(f"Error al inicializar la base de datos: {e}")
            raise
        finally:
            if conn:
                conn.close()

    # --- Operaciones CRUD ---
    def create_item(self, item: Item) -> Item:
        """4. Inserta un nuevo item (persona) en la tabla 'items'."""
        conn = None
        try:
            conn = self._get_connection()
            conn.autocommit = True
            with conn.cursor() as cursor:
                sql = """
                INSERT INTO items 
                (id, nombre, apellidos, numero_telefono, puesto_trabajo)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    item.id, 
                    item.nombre, 
                    item.apellidos, 
                    item.numero_telefono, 
                    item.puesto_trabajo,
                ))
            return item
        except psycopg2.Error:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def get_item(self, item_id: str) -> Optional[Item]:
        """4. Obtiene un item (persona) por su ID (DNI)."""
        conn = None
        try:
            conn = self._get_connection()
            # Usamos RealDictCursor para obtener resultados como diccionario
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                sql = "SELECT id, nombre, apellidos, numero_telefono, puesto_trabajo FROM items WHERE id = %s"
                cursor.execute(sql, (item_id,))
                record = cursor.fetchone()
                
                if record:
                    return Item(**record)
                return None
        except psycopg2.Error:
            raise
        finally:
            if conn:
                conn.close()
    
    def get_all_items(self) -> List[Item]:
        """4. Obtiene una lista de todos los items (personas)."""
        conn = None
        items = []
        try:
            conn = self._get_connection()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                sql = "SELECT id, nombre, apellidos, numero_telefono, puesto_trabajo FROM items"
                cursor.execute(sql)
                records = cursor.fetchall()
                
                for row in records:
                    items.append(Item(**row))
                return items
        except psycopg2.Error:
            raise
        finally:
            if conn:
                conn.close()
    
    def update_item(self, item_id: str, item: Item) -> Optional[Item]:
        """4. Actualiza un item (persona) existente por su ID (DNI)."""
        conn = None
        try:
            conn = self._get_connection()
            conn.autocommit = True
            with conn.cursor() as cursor:
                sql = """
                    UPDATE items 
                    SET nombre=%s, apellidos=%s, numero_telefono=%s, puesto_trabajo=%s
                    WHERE id=%s
                """
                cursor.execute(sql, (
                    item.nombre, 
                    item.apellidos, 
                    item.numero_telefono, 
                    item.puesto_trabajo,
                    item_id # Se usa el ID de la URL
                ))
                
                if cursor.rowcount > 0:
                    # El ID original no se cambia en la actualización.
                    item.id = item_id 
                    return item
                return None
        except psycopg2.Error:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def delete_item(self, item_id: str) -> bool:
        """4. Elimina un item (persona) por su ID (DNI)."""
        conn = None
        try:
            conn = self._get_connection()
            conn.autocommit = True
            with conn.cursor() as cursor:
                sql = "DELETE FROM items WHERE id = %s"
                cursor.execute(sql, (item_id,))
                return cursor.rowcount > 0
        except psycopg2.Error:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()