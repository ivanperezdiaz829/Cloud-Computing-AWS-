import json
import os
from db.factory import DatabaseFactory
from psycopg2 import OperationalError, IntegrityError

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
    'Access-Control-Allow-Methods': 'DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token'
}

def handler(event, context):
    """
    Maneja la petición DELETE para eliminar un item por su ID.
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
                'statusCode': 400, # Bad Request
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'El ID del item es requerido en la URL.'})
            }

        # 2. Llamar a la base de datos para eliminar el item
        deleted = db.delete_item(item_id)

        # 3. Devolver la respuesta
        if deleted:
            return {
                'statusCode': 204,
                'headers': CORS_HEADERS,
                'body': '' # No se devuelve contenido
            }
        else:
            return {
                'statusCode': 404,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Item no encontrado'})
            }

    except IntegrityError as e:
        return {
            'statusCode': 409, # Conflict
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Conflicto al eliminar el recurso', 'details': str(e)})
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