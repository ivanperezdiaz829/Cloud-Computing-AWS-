import json
import os
from db.factory import DatabaseFactory
from psycopg2 import OperationalError

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
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token'
}

def handler(event, context):
    """
    Maneja las peticiones GET para /items y /items/{id}.
    """
    if db is None:
        return {
            'statusCode': 503,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Servicio no disponible por error de configuración de BD.'})
        }

    try:
        # --- Ruta: GET /items/{id} ---
        if event.get('pathParameters') and event['pathParameters'].get('id'):
            item_id = event['pathParameters']['id']
            print(f"Buscando item con ID: {item_id}")
            
            item = db.get_item(item_id)
            
            if item:
                return {
                    'statusCode': 200,
                    'headers': CORS_HEADERS,
                    'body': item.model_dump_json()
                }
            else:
                return {
                    'statusCode': 404,
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': 'Item no encontrado'})
                }
        
        # --- Ruta: GET /items ---
        else:
            print("Buscando todos los items...")
            items = db.get_all_items()
            
            body = json.dumps([item.model_dump() for item in items])
            
            return {
                'statusCode': 200,
                'headers': CORS_HEADERS,
                'body': body
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