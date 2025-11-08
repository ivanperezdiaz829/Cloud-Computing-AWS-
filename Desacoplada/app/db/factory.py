import os
from typing import Dict, Type
from .db import Database
from .postgres_db import PostgresDatabase


class DatabaseFactory:
    """
    Factoría para crear instancias de la clase Database. 
    Se ha simplificado para solo soportar PostgreSQL, dado el requisito del proyecto.
    """
    
    _databases: Dict[str, Type[Database]] = {
        'postgres': PostgresDatabase,
    }
    
    @classmethod
    def create(cls, db_type: str = None) -> Database:
        """
        Crea y retorna una instancia de PostgresDatabase.
        Ignora el argumento db_type, pero valida que no sea un valor no soportado.
        """
        if db_type is not None and db_type.lower() != 'postgres':
            raise ValueError(
                f"DB_TYPE '{db_type}' no es compatible. Esta factoría solo soporta 'postgres'."
            )

        return cls._databases['postgres']()
    
    @classmethod
    def get_available_databases(cls) -> list:
        """Retorna una lista con los nombres de las bases de datos disponibles."""
        return list(cls._databases.keys())