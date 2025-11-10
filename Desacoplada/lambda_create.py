import json
import os
from pydantic import ValidationError
from models.item import Item
from db.factory import DatabaseFactory
from psycopg2 import OperationalError, IntegrityError
from json import JSONDecodeError # Importante para capturar JSON malformado

# --- Inicialización ---
try:
    db = DatabaseFactory.create()
    db.initialize()
except Exception as e:
    print(f"ERROR: No se pudo inicializar la conexión a la BD: {e}")
    db = None

# --- Headers de CORS ---
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token'
}

def handler(event, context):
    """
    Maneja la petición POST para crear un nuevo item.
    """
    if db is None:
        return {
            'statusCode': 503,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Servicio no disponible por error de configuración de BD.'})
        }

    try:
        # 1. Parsear el body de la petición (de forma segura)
        body = event.get('body')
        if not body:
            raise ValueError("El cuerpo de la petición (body) está vacío.")
        
        data = json.loads(body)

        # 2. Validar los datos con Pydantic
        item = Item(**data)

        # 3. Llamar a la base de datos para crear el item
        created_item = db.create_item(item)

        # 4. Devolver la respuesta de éxito (201 Created)
        return {
            'statusCode': 201,
            'headers': CORS_HEADERS,
            'body': created_item.model_dump_json()
        }

    except (JSONDecodeError, TypeError, ValueError) as e:
        # Error si el body es nulo, no es JSON válido, o está vacío
        return {
            'statusCode': 400, # Bad Request
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Cuerpo (body) de la petición inválido', 'details': str(e)})
        }
    except ValidationError as e:
        return {
            'statusCode': 400, # Bad Request
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Validation error', 'details': e.errors()})
        }
    except IntegrityError as e:
        return {
            'statusCode': 409, # Conflict
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Database integrity error (ID already exists)', 'details': str(e)})
        }
    except OperationalError as e:
        print(f"ERROR de conexión a BD: {e}")
        return {
            'statusCode': 503, # Service Unavailable
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Error de conexión con la base de datos.'})
        }
    except Exception as e:
        print(f"ERROR inesperado: {e}")
        return {
            'statusCode': 500, # Internal Server Error
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Error interno del servidor.', 'details': str(e)})
        }