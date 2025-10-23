from abc import ABC, abstractmethod
from typing import List, Optional
from models.item import Item 

class Database(ABC):
    """
    Clase abstracta que define el contrato de la capa de persistencia (CRUD) 
    para el recurso 'Item' (que representa a una persona en la DB PostgreSQL).
    """
    @abstractmethod
    def initialize(self):
        """Inicializa la conexión y/o la estructura de la base de datos (ej. crea tablas)."""
        pass
    
    # --- Operaciones CRUD para el recurso 'Item' ---
    @abstractmethod
    def create_item(self, item: Item) -> Item:
        """Crea y persiste un nuevo item en la base de datos."""
        pass
    
    @abstractmethod
    def get_item(self, item_id: str) -> Optional[Item]:
        """Obtiene un solo item usando su ID (DNI)."""
        pass
    
    @abstractmethod
    def get_all_items(self) -> List[Item]:
        """Obtiene una lista de todos los items."""
        pass
    
    @abstractmethod
    def update_item(self, item_id: str, item: Item) -> Optional[Item]:
        """Actualiza un item existente. Retorna el item actualizado o None si no se encuentra."""
        pass
    
    @abstractmethod
    def delete_item(self, item_id: str) -> bool:
        """Elimina un item usando su ID. Retorna True si fue exitoso, False en caso contrario."""
        pass