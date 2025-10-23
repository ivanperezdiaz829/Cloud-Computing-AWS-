from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
import re

PUESTOS_VALIDOS = Literal['desarrollador', 'administrativo', 'notario', 'comercial']

class Item(BaseModel):
    """
    Representa un Item (una persona) con sus atributos principales.
    El DNI actúa como el ID principal del recurso.
    """
    id: str = Field(..., min_length=9, max_length=9, description="DNI o NIF de la persona.")
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre de pila.")
    apellidos: str = Field(..., min_length=1, max_length=150, description="Apellidos.")
    numero_telefono: Optional[str] = Field(None, min_length=9, max_length=20, description="Número de teléfono de contacto.")
    puesto_trabajo: PUESTOS_VALIDOS = Field(..., description="Puesto de trabajo de la persona.")

    
    # --- Validadores (Opcionales pero recomendados para Pydantic) ---
    @field_validator('id', mode='before')
    @classmethod
    def validate_dni(cls, value: str) -> str:
        """Valida que el campo 'id' (DNI) tenga un formato básico de 8 dígitos y 1 letra."""
        if not re.match(r'^\d{8}[A-Z]$', value.upper()):
            raise ValueError('El DNI debe tener 8 números seguidos de 1 letra (ej: 12345678A).')
        return value.upper()

    @field_validator('numero_telefono', mode='before')
    @classmethod
    def clean_phone_number(cls, value: Optional[str]) -> Optional[str]:
        """Limpia caracteres comunes en el teléfono antes de la validación."""
        if value is None:
            return None
        # Elimina espacios, guiones y paréntesis para almacenamiento limpio
        cleaned_value = re.sub(r'[()\s-]', '', value)
        if not re.match(r'^\+?\d{9,15}$', cleaned_value):
             raise ValueError('El número de teléfono debe contener solo dígitos y el prefijo opcional "+".')
        return cleaned_value
    
    # --- Configuración y Ejemplo ---
    class Config:
        json_schema_extra = {
            "example": {
                "id": "12345678A",
                "nombre": "Ana",
                "apellidos": "García Pérez",
                "numero_telefono": "600112233",
                "puesto_trabajo": "desarrollador"
            }
        }