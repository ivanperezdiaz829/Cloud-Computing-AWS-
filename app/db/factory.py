import os
from typing import Dict, Type
from .db import Database
from .postgres_db import PostgresDatabase


class DatabaseFactory:
    """
    Factoría para crear instancias de la clase Database. 
    Selecciona la base de datos a utilizar (PostgreSQL o DynamoDB) 
    basándose en la variable de entorno DB_TYPE.
    """
    
    _databases: Dict[str, Type[Database]] = {
        # Mantener PostgreSQL como opción principal
        'postgres': PostgresDatabase,
    }
    
    @classmethod
    def create(cls, db_type: str = None) -> Database:
        """
        Crea y retorna una instancia de la base de datos solicitada.
        Si db_type es None, usa la variable de entorno DB_TYPE, por defecto 'postgres'.
        """
        if db_type is None:
            # db_type se toma de la variable de entorno DB_TYPE, por defecto 'postgres'
            db_type = os.getenv('DB_TYPE', 'postgres')
        
        db_type = db_type.lower()
        
        database_class = cls._databases.get(db_type)
        
        if database_class is None:
            available = ', '.join(cls._databases.keys())
            raise ValueError(
                f"DB_TYPE '{db_type}' no válido. "
                f"Opciones disponibles: {available}"
            )
        return database_class()
    
    @classmethod
    def get_available_databases(cls) -> list:
        """Retorna una lista con los nombres de las bases de datos disponibles."""
        return list(cls._databases.keys())