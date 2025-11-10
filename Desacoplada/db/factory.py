import os
from .postgres_db import PostgresDB

class DatabaseFactory:
    """
    Factory para crear una instancia de la base de datos basada en
    la variable de entorno DB_TYPE.
    """

    @staticmethod
    def create():
        db_type = os.environ.get('DB_TYPE')

        if db_type == 'postgres':
            return PostgresDB()
        
        # Si la variable no está configurada o es desconocida, falla.
        raise ValueError(f"Tipo de base de datos '{db_type}' no soportado o no configurado.")