from flask import Flask, request, jsonify
from pydantic import ValidationError
import psycopg2
from botocore.exceptions import ClientError # Mirar desacoplado
from models.item import Item 
from db.factory import DatabaseFactory

app = Flask(__name__)

# --- Inicialización de la Base de Datos ---
try:
    db = DatabaseFactory.create()
    db.initialize() 

except ValueError as e:
    raise RuntimeError(f"Error initializing DB: {e}") from e

# --- Middlewares ---
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,x-api-key'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response

# --- Endpoints CRUD ---
@app.route('/items', methods=['POST'])
def create_item():
    """Crea un nuevo item (persona)."""
    try:
        data = request.get_json()
        item = Item(**data)
        created = db.create_item(item)
        return jsonify(created.model_dump()), 201
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 400
    except psycopg2.IntegrityError as e:
        return jsonify({'error': 'Database integrity error (ID already exists)', 'details': str(e)}), 409
    except psycopg2.OperationalError as e:
        return jsonify({'error': 'Database connection error', 'details': str(e)}), 503
    except psycopg2.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@app.route('/items/<item_id>', methods=['GET']) 
def get_item(item_id):
    """Obtiene un item (persona) por su ID (DNI)."""
    try:
        item = db.get_item(item_id)
        if item:
            return jsonify(item.model_dump()), 200
        return jsonify({'error': 'Item no encontrado'}), 404
    except psycopg2.OperationalError as e:
        return jsonify({'error': 'Database connection error', 'details': str(e)}), 503
    except psycopg2.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@app.route('/items', methods=['GET'])
def get_all_items():
    """Obtiene todos los items (personas)."""
    try:
        items = db.get_all_items()
        return jsonify([item.model_dump() for item in items]), 200
    except psycopg2.OperationalError as e:
        return jsonify({'error': 'Database connection error', 'details': str(e)}), 503
    except psycopg2.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@app.route('/items/<item_id>', methods=['PUT']) 
def update_item(item_id):
    """Actualiza un item (persona) por su ID (DNI)."""
    try:
        data = request.get_json()
        data.pop('id', None) 
        data.pop('created_at', None) 
        
        # --- CORRECCIÓN ---
        # Añadimos el 'id' de la URL al diccionario 'data'
        # para que Pydantic pueda validar el modelo 'Item' completo.
        data['id'] = item_id
        # --- FIN DE LA CORRECCIÓN ---
        
        item = Item(**data) # Ahora la validación funcionará
        updated = db.update_item(item_id, item)
        
        if updated:
            return jsonify(updated.model_dump()), 200
        return jsonify({'error': 'Item no encontrado'}), 404
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 400
    except psycopg2.IntegrityError as e:
        return jsonify({'error': 'Database integrity error', 'details': str(e)}), 409
    except psycopg2.OperationalError as e:
        return jsonify({'error': 'Database connection error', 'details': str(e)}), 503
    except psycopg2.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@app.route('/items/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Elimina un item (persona) por su ID (DNI)."""
    try:
        if db.delete_item(item_id):
            return '', 204
        return jsonify({'error': 'Item no encontrado'}), 404
    except psycopg2.OperationalError as e:
        return jsonify({'error': 'Database connection error', 'details': str(e)}), 503
    except psycopg2.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Endpoint simple para verificar que el servicio está activo."""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)