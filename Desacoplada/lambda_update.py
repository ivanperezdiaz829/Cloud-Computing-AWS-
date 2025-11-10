import json
import os
from pydantic import ValidationError
from models.item import Item
from db.factory import DatabaseFactory
from psycopg2 import OperationalError, IntegrityError
from json import JSONDecodeError # Importar para manejo de JSON

# --- Inicialización ---
try:
    db = DatabaseFactory.create()
    db.initialize()
except Exception as e:
    print(f"ERROR: No se pudo inicializar la conexión a la BD: {e}")
    db = None

# --- Headers de CORS ---
# Definir los headers fuera del handler para reutilizarlos
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*', # Permite cualquier origen
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token'
}


def handler(event, context):
    """
    Maneja la petición PUT para actualizar un item existente.
    """
    if db is None:
        return {
            'statusCode': 503,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Servicio no disponible por error de configuración de BD.'})
        }

    try:
        # 1. Obtener el ID de los parámetros de la URL (de forma segura)
        item_id = event.get('pathParameters', {}).get('id')
        if not item_id:
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'El ID del item es requerido en la URL.'})
            }
        
        # 2. Parsear el body de la petición (de forma segura)
        body = event.get('body')
        if not body:
            raise ValueError("El cuerpo de la petición (body) está vacío.")
        
        data = json.loads(body)

        # 3. Añadir el 'id' de la URL al 'data' antes de validar
        data['id'] = item_id
        
        # 4. Validar los datos con Pydantic
        item = Item(**data)

        # 5. Llamar a la base de datos para actualizar
        updated_item = db.update_item(item_id, item)

        # 6. Devolver la respuesta
        if updated_item:
            return {
                'statusCode': 200,
                'headers': CORS_HEADERS,
                'body': updated_item.model_dump_json()
            }
        else:
            return {
                'statusCode': 404,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Item no encontrado'})
            }

    except (JSONDecodeError, TypeError, ValueError) as e:
        # Error si el body es nulo, no es JSON válido, o está vacío
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Cuerpo (body) de la petición inválido', 'details': str(e)})
        }
    except ValidationError as e:
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Validation error', 'details': e.errors()})
        }
    except IntegrityError as e:
        return {
            'statusCode': 409,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Database integrity error', 'details': str(e)})
        }
    except OperationalError as e:
        print(f"ERROR de conexión a BD: {e}")
        return {
            'statusCode': 503,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Error de conexión con la base de datos.'})
        }
    except Exception as e:
        print(f"ERROR inesperado: {e}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Error interno del servidor.', 'details': str(e)})
        }