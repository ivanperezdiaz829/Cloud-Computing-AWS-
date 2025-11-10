import os
import psycopg2
from psycopg2.extras import DictCursor
from models.item import Item

class PostgresDB:
    """
    Implementación de la lógica de base de datos para PostgreSQL.
    Maneja la conexión y las operaciones CRUD para la tabla 'items'.
    """

    def __init__(self):
        """
        Carga las credenciales de la base de datos desde las variables de entorno.
        """
        self.db_host = os.environ.get('DB_HOST')
        self.db_name = os.environ.get('DB_NAME')
        self.db_user = os.environ.get('DB_USER')
        self.db_pass = os.environ.get('DB_PASS')
        
        if not all([self.db_host, self.db_name, self.db_user, self.db_pass]):
            # Este error es crítico y debe detener la inicialización de la Lambda
            raise ValueError("Las variables de entorno de la base de datos (DB_HOST, DB_NAME, DB_USER, DB_PASS) no están configuradas.")
            
        self.conn = None

    def _get_connection(self):
        """
        Establece o reutiliza una conexión a la base de datos.
        Configura autocommit=True, que es ideal para funciones Lambda.
        """
        try:
            # Reutiliza la conexión si está "caliente" (warm start)
            if self.conn is None or self.conn.closed != 0:
                print("Estableciendo nueva conexión a la base de datos...")
                self.conn = psycopg2.connect(
                    host=self.db_host,
                    database=self.db_name,
                    user=self.db_user,
                    password=self.db_pass
                )
                # Autocommit es preferible en Lambda para evitar transacciones colgadas
                self.conn.autocommit = True
            return self.conn
        except psycopg2.OperationalError as e:
            print(f"ERROR: No se pudo conectar a la base de datos: {e}")
            raise # Lanza el error para que la Lambda falle y lo registre

    def initialize(self):
        """
        Llamado una vez al inicio. Se asegura de que la tabla 'items' exista.
        Esto reemplaza la necesidad de ejecutar postgres.sql manualmente.
        """
        print("Inicializando base de datos...")
        conn = self._get_connection()
        
        # La lógica de tu archivo postgres.sql
        create_table_query = """
        CREATE TABLE IF NOT EXISTS items (
            id VARCHAR(255) PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            apellidos VARCHAR(255) NOT NULL,
            puesto_trabajo VARCHAR(255) NOT NULL,
            numero_telefono VARCHAR(20)
        );
        """
        try:
            with conn.cursor() as cursor:
                cursor.execute(create_table_query)
            print("Tabla 'items' verificada/creada exitosamente.")
        except psycopg2.Error as e:
            print(f"ERROR: No se pudo crear la tabla 'items': {e}")
            raise

    def create_item(self, item: Item) -> Item:
        """
        Inserta un nuevo item en la base de datos y devuelve el item creado.
        """
        query = """
        INSERT INTO items (id, nombre, apellidos, puesto_trabajo, numero_telefono)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *;
        """
        conn = self._get_connection()
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (
                item.id, 
                item.nombre, 
                item.apellidos, 
                item.puesto_trabajo, 
                item.numero_telefono
            ))
            created_record = cursor.fetchone()
            # Convierte el registro de la BD (un dict) de nuevo a un modelo Pydantic
            return Item(**created_record)

    def get_item(self, item_id: str) -> Item | None:
        """
        Obtiene un solo item por su ID.
        """
        query = "SELECT * FROM items WHERE id = %s;"
        conn = self._get_connection()
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (item_id,))
            record = cursor.fetchone()
            if record:
                return Item(**record)
            return None # Retorna None si no se encontró

    def get_all_items(self) -> list[Item]:
        """
        Obtiene una lista de todos los items en la base de datos.
        """
        query = "SELECT * FROM items ORDER BY id;"
        conn = self._get_connection()
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            records = cursor.fetchall()
            # Convierte la lista de dicts en una lista de modelos Item
            return [Item(**record) for record in records]

    def update_item(self, item_id: str, item: Item) -> Item | None:
        """
        Actualiza un item existente (identificado por item_id) con los datos del objeto item.
        """
        query = """
        UPDATE items
        SET nombre = %s, apellidos = %s, puesto_trabajo = %s, numero_telefono = %s
        WHERE id = %s
        RETURNING *;
        """
        conn = self._get_connection()
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (
                item.nombre, 
                item.apellidos, 
                item.puesto_trabajo, 
                item.numero_telefono,
                item_id  # Usa el item_id de la URL para el WHERE
            ))
            updated_record = cursor.fetchone()
            if updated_record:
                return Item(**updated_record)
            return None # No se encontró el item para actualizar

    def delete_item(self, item_id: str) -> bool:
        """
        Elimina un item por su ID. Devuelve True si se eliminó, False si no se encontró.
        """
        query = "DELETE FROM items WHERE id = %s;"
        conn = self._get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, (item_id,))
            # Cuántas filas fueron afectadas
            return cursor.rowcount > 0