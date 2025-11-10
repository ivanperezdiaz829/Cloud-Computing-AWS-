# **Infraestructuras Acoplada y Desacoplada mediante AWS**

Versión Acoplada de una infraestuctura con base de datos PostgreSQL y que crea una aplicacion FlasK de gestión de empresa (personas, DNIs, departamento, etc) haciendo uso de un balanceador de carga y con un diseño monolítico con ECS (Elastic Container Service).

<h3 style="text-weight: bold">Diagrama de la Infraestructura:</h3>

<img src="/Acoplada/Diagrama_Acoplada.jpeg">


## Paso 1: Construir y Subir la imagen Docker

```bash
# El nombre y la región se modificará dependiendo de la imagen y la cuenta
aws ecr create-repository --repository-name acoplada --region us-east-1
```

```bash
# Iniciar sesión de Docker en ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 211125679469.dkr.ecr.us-east-1.amazonaws.com
# Debería aparecer -> Login Succeeded
```

```bash
# Construir imagen
docker build -t acoplada:latest .
```

```bash
# Etiquetar la imagen para ECR
docker tag acoplada:latest 211125679469.dkr.ecr.us-east-1.amazonaws.com/acoplada:latest
```

```bash
# Subir (Push) la imagen a ECR
docker push 211125679469.dkr.ecr.us-east-1.amazonaws.com/acoplada:latest
```

Tras lo anterior se deben ubicar dos nuevas imágenes en Docker, una con el nombre completo y la otra con el nombre elegido, en este caso "acoplada", aún teniendo diferente nombre, el image ID es el mismo dado que en realidad el nombre es un TAG que se ha puesto para diferenciar más comodamente las imágenes.

## Paso 2: Lanzar el Stack de CloudFormation

Entrar a VPC y obtener la el ID del VPC, de las subnets.

Obtener el host, nombre, usuario y contraseña de la Base de datos PostgreSQL a partir del db_postgres.yaml. Para ello, primero se ha de inicializar la Base de Datos mediante la interfaz gráfica usando la creación de Stacks y cargando la plantilla .yaml.

Para crear el Stack del main.yaml usar el siguiente comando

```bash
aws cloudformation create-stack `
--stack-name mi-app-temporal `
--template-body file://main.yaml `
--parameters file://parametros_main.json `
--capabilities CAPABILITY_IAM
```

## Componentes principales

- **API Gateway (REST)**: expone los recursos `items` e `item` y enruta al backend vía VPC Link. Protegido con API Key.
- **VPC Link + NLB**: el VPC Link conecta API Gateway con un Network Load Balancer interno que apunta al servicio de ECS.
- **ECS Fargate**: ejecuta el contenedor de la app Flask definido en `Dockerfile` y `main.yml`.
- **Bases de datos**:
  - **PostgreSQL (Amazon RDS)** en el VPC, con SG de acceso al puerto 5432.
- **Amazon ECR**: repositorio para la imagen del contenedor.

## Estructura del proyecto

```bash
Acoplada
      > app
          > db
                db.py
                factory.py
                postgres_db.py
          > models
                item.py
          main.py
    db_postgres.yaml
    Diagrama_Acoplada.jpeg
    Dockerfile
    ecr.yaml
    frontend.html
    main.yaml
    parametros_main.json
    postgres.sql
    README.md
    requirements.txt
```

<h4 style="text-weight: bold">Directorio Acoplada:</h4>

- **[db_postgres.yaml](/Acoplada/db_postgres.yaml):** Plantilla para RDS PostgreSQL.
- **[Diagrama_Acoplada.jpeg](/Acoplada/Diagrama_Acoplada.jpeg):** Diagrama de la Infraestructura del proyecto Acoplado con los componentes interconectados.
- **[Dockerfile](/Acoplada/Dockerfile):** Imagen de la aplicación.
- **[ecr.yaml](/Acoplada/ecr.yaml):** Plantilla del sistema monolítico para el repositorio ECR.
- **[frontend.html](/Acoplada/frontend.html):** HTML básico para probar la API vía API Gateway (pide la API Key y el API Endpoint para acceder).
- **[main.yaml](/Acoplada/main.yaml):** Plantilla CloudFormation para API Gateway + VPC Link + NLB + ECS Fargate (CRUD).
- **[parametros_main.json](/Acoplada/parametros_main.json):** Fichero JSON con todos los parámetros necesarios para lanzar el stack.
- **[postgres.sql](/Acoplada/postgres.sql):** Crea una tabla localmente con la información necesaria para la base de datos.
- **[README.md](/Acoplada/README.md):** Es el documento actual que explica la infraestructura del proyecto y define el funcionamiento.
- **[requirements.txt](/Acoplada/requirements.txt):** Dependencias necesarias para que todo fucione correctamente.

<h4 style="text-weight: bold">Directorio Acoplada/app:</h4>

- **[main.py](/Acoplada/app/main.py):** Aplicación Flask con los Middlewares y los Endpoints.

<h4 style="text-weight: bold">Directorio Acoplada/app/models:</h4>

- **[item.py](/Acoplada/app/models/item.py):** Tiene la definición de una persona (campos y validación).

<h4 style="text-weight: bold">Directorio Acoplada/app/db:</h4>

- **[postgres_db.py](/Desacoplada/db/postgres_db.py):** Implementación PostgreSQL.
- **[factory.py](/Acoplada/app/db/factory.py):** Si en un futuro se quisiera implementar otro tipo de DB, aquí se puede seleccionar.
- **[db.py](/Acoplada/app/db/db.py):** Clase abstracta que define las operaciones del CRUD de item (Persona).

## API

- **POST** `/items`: crea un ticket.
- **GET** `/items`: lista de tickets.
- **GET** `/items/{ticket_id}`: obtiene un ticket.
- **PUT** `/items/{ticket_id}`: actualiza un ticket.
- **DELETE** `/items/{ticket_id}`: borra un ticket.
- **GET** `/health`: comprobación de vida.

Las respuestas de error gestionan validación (`pydantic`), integridad/operación de PostgreSQL y errores de DynamoDB.

## Variables de entorno

- **DB_TYPE**: `postgres` (por defecto) o `dynamodb`.
- Si `DB_TYPE=postgres`:
  - **DB_HOST**, **DB_NAME**, **DB_USER**, **DB_PASS**.
- Si `DB_TYPE=dynamodb`:
  - **DB_DYNAMONAME**: nombre de la tabla (por defecto `tickets`).

### Ejecución local (opcional)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Ejemplo usando PostgreSQL local
export DB_TYPE=postgres DB_HOST=localhost DB_NAME=ticketsdb DB_USER=postgres DB_PASS=postgres
python app/main.py
# La API quedará en http://localhost:8080
```

### Contenedor

```bash
# Construir
docker build -t tickets-app:latest .
# Ejecutar
docker run --rm -p 8080:8080 \
  -e DB_TYPE=postgres \
  -e DB_HOST=host.docker.internal -e DB_NAME=ticketsdb -e DB_USER=postgres -e DB_PASS=postgres \
  tickets-app:latest
```

### Despliegue en AWS (CloudFormation)

Orden recomendado de plantillas:

1. `ecr.yml` → crea el repositorio y subir la imagen.
2. `db_postgres.yml` o `db_dynamodb.yml` → crea la base de datos elegida.
3. `main.yml` → despliega VPC Link, NLB, ECS Fargate, API Gateway y enlaza la imagen y variables.

Parámetros clave de `main.yml`:

- **ImageName**: `<repo>:<tag>` en ECR.
- **VpcId**, **SubnetIds**: VPC y subredes existentes.
- **DBType**: `postgres` o `dynamodb`.
- Campos de DB correspondientes: `DBHost`, `DBName`, `DBUser`, `DBPass` o `DBDynamoName`.

### Probar con `frontend.html`

`frontend.html` es una página estática que consume los endpoints del API Gateway usando `fetch` y la cabecera `x-api-key`.

Uso rápido:

1. Abrir el archivo `frontend.html` en el navegador (doble clic o `file:///...`).
2. En el modal de configuración inicial, introducir:
   - **API URL**: la URL del Stage (por ejemplo, `https://<rest-api-id>.execute-api.us-east-1.amazonaws.com/prod`).
   - **API Key**: el valor de la API Key creada por `main.yml`.
3. Pulsar “Conectar”.
4. Crear/editar/mover tickets en el tablero. Las operaciones llaman a `POST /items`, `GET /items`, `PUT /items/{id}` y `DELETE /items/{id}` del API Gateway.

Notas:

- La configuración (URL y API Key) se guarda en `localStorage` del navegador.
- Si la API Key no es válida o el CORS falla, la app mostrará un mensaje de error.

### Notas

- La región de las prácticas es `us-east-1`.
- El contenedor expone el puerto 8080 y el NLB escucha en el mismo puerto.
- Se deja tanto el grupo de seguridad de la tarea de ECS como de la BBDD abierto para que los alumnos puedan acceder desde fuera para validar su trabajo. Permitiéndoles debuggear de forma sencilla.