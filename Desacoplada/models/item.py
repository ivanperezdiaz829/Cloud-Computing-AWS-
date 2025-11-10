from pydantic import BaseModel

class Item(BaseModel):
    """
    Define el esquema de datos para un "Item" (un registro de personal).
    Pydantic se usa para validar automáticamente los datos de la API
    que vienen en el 'body' de las peticiones POST y PUT.
    """
    
    id: str                 # El DNI/ID, es obligatorio
    nombre: str             # El nombre, es obligatorio
    apellidos: str          # Los apellidos, son obligatorios
    puesto_trabajo: str     # El puesto, es obligatorio
    
    # Este campo es opcional y por defecto será None si no se proporciona
    numero_telefono: str | None = None