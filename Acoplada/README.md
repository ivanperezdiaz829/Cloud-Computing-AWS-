# **INFRAESTRUCTURA ACOPLADA DE ECS CON AWS**

Versión Acoplada de una infraestuctura con base de datos PostgreSQL y que crea una aplicacion FlasK de gestión de empresa (personas, DNIs, departamento, etc) haciendo uso de un balanceador de carga y con un diseño monolítico con ECS (Elastic Container Service).

<h3 style="text-weight: bold">Diagrama de la Infraestructura:</h3>

<img src="/Acoplada/Diagrama_Acoplada.jpeg">

## ÍNDICE

- [Componentes principales](#componentes-principales)
- [Estructura del proyecto](#estructura-del-proyecto)
- [API](#api)
- [Proceso de creación](#proceso-de-creación)
- [Presupuesto y gastos de la infraestructura](#presupuesto-y-gatos-de-la-infraestructura)
- [Fuentes y documentación](#fuentes-y-documentación)

## COMPONENTES PRINCIPALES

- **API Gateway (REST)**: Expone los recursos `items` e `item` (Personas individuales o en grupo) y enruta al backend vía VPC Link. Protegido con API Key.
- **VPC Link y NLB**: El VPC Link conecta API Gateway con un Network Load Balancer interno que apunta al servicio de ECS.
- **ECS Fargate**: Ejecuta el contenedor de la app Flask definido en `Dockerfile` y `main.yml`.
- **Base de datos**: PostgreSQL (Amazon RDS) en el VPC, con SG de acceso al puerto 5432.
- **Amazon ECR**: Repositorio para la imagen del contenedor de Docker.

## ESTRUCTURA DEL PROYECTO

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

<h4 style="text-weight: bold">Directorio /Acoplada/:</h4>

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

La API posee los siguientes métodos para realizar peticiones mediante la aplicación.

  - **PostItemsMethod:** Crea nuevos items (Personas) con los parámetros que los componen.
  - **GetItemsMethod:** Obtiene todas los items (Obtiene lista de personas).
  - **GetItemMethod:** Obtiene un solo item (Obtiene Persona).
  - **PutItemMethod:** Modifica el item seleccionado (Edita Persona).
  - **DeleteItemMethod:** Elimina el item seleccionado (Elimina Persona).
  - **OptionsItemsMethod:** Es el uno de los Options que se usan para el CORS.
  - **OptionsItemMethod:** Es el otro de los Options que se usan para el CORS.

Los errores y respuestas se validan mediante *pydantic* y vienen definidas en el fichero [main.py](/Acoplada/app/main.py) explicado anteriormente.

## PROCESO DE CREACIÓN

Primeramente y para poder realizar pasos posteriores como el crear repositorios ECR con la imagen de Docker para crear el stack dentro de AWS, se van a realizar los siguientes pasos:

1. Iniciar el laboratorio de AWS y entrar al apartado llamado: *"AWS Details"*.

2. En el terminal del dispositivo que se esté usando instalar *amazon cli* (en caso de no tenerlo instalado).

3. En el mismo terminal hacer el siguiente comando: `aws configure`. Pedirá diferentes parámetros y claves que se pueden encontrar en el punto 1. Los datos pedidos son:
      - AWS Access Key ID
      - AWS Secret Access Key.
      - Default region name (pulsar enter sin modificar nada).
      - Default output format (pulsar enter sin modificar nada).

4. Copiar toda la información que aparece en AWS CLI y pegarla dentro de la ruta `~/.aws/credentials`. Guardar lo anterior.

Tras lo anterior y como primer paso para la creación de la infraestructura de acoplada se procede a la creación de la base de datos, para ello y haciendo uso de la consola de CloudFormation se va a crear un nuevo stack cargando la plantilla [db_postgres.yaml](/Acoplada/db_postgres.yaml) y poniendo como contraseña (necesario poner la misma para este proyecto dado que es uno de los parámetros del [parametros_main.json](/Acoplada/parametros_main.json)) "Entra123". Las subnets seleccionadas se han de guardar para ponerlas también en el mismo fichero [parametros_main.json](/Acoplada/parametros_main.json) y también la VPC. Una vez realizados los pasos anteriores, se lanza el stack con la base de datos.

Una vez ponga **CREATE_COMPLETE** se puede pasar al siguiente paso.

Para este paso es necesario crear el repositorio **ECR** que lance la aplicación a través de Docker, y para ello se han de utilizar los siguientes comandos (el número que aparece en algunos de ellos al principio de una cadena tal que "NÚMERO".dkr.):

1. Crear el repositorio ECR:

      ```bash
      # El nombre y la región se modificará dependiendo de la imagen y la cuenta
      aws ecr create-repository --repository-name acoplada --region us-east-1
      ```

2. Iniciar sesión de Docker en ECR:

      ```bash
      # Debería aparecer -> Login Succeeded
      aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 098189193517.dkr.ecr.us-east-1.amazonaws.com
      ```

3. Contruir imagen:

      ```bash
      docker build -t acoplada:latest .
      ```

4. Etiquetar la imagen para ECR:

      ```bash
      # Etiquetar la imagen para ECR
      docker tag acoplada:latest 098189193517.dkr.ecr.us-east-1.amazonaws.com/acoplada:latest
      ```

5. Subir al imagen a ECR:

      ```bash
      # Subir (Push) la imagen a ECR
      docker push 098189193517.dkr.ecr.us-east-1.amazonaws.com/acoplada:latest
      ```

6. Lanzar el Stack de Cloud Formation:

      ```bash
      aws cloudformation create-stack `
      --stack-name mi-app-temporal `
      --template-body file://main.yaml `
      --parameters file://parametros_main.json `
      --capabilities CAPABILITY_IAM
      ```

Una vez el Stack lanzado ponga **CREATE_COMPLETE** ya se ha completado el lanzamiento de la infraestructura, para probar la misma se va a hacer uso del [frontend.html](/Acoplada/frontend.html), que se ha de lanzar mediante cualquier método de su preferencia, nada más entrar, pedirá la **API KEY** y el **API ENDPOINT**. Para el primero, se ha de ir a la consola de AWS llamada *API Gateway* y en donde pone *Claves API*, seleccionar la del proyecto y copiar la clave. Para el segundo, en el propio stack en la consola de CloudFormation seleccionando el stack creado y tras moverse al apartado *Salidas*, copiar la URL que aparece.

Con todo lo anterior, se podrá entrar dentro de la aplicación final y gestionar los items (personas) haciendo peticiones a la API de CREATE, READ, UPDATE y DELETE.


## PRESUPUESTO Y GASTOS DE LA INFRAESTRUCTURA

La infraestructura lanzada no es gratis de mantener, teniendo un costo por uso o por existencia en el tiempo, todos estos gastos son necesarios conocerlos para crear una infraestructura económica y que supla los requerimientos.

- **Precio e instancia de la Base de datos:** Se usa la **t3.micro** (temas de que es temporalmente gratis para la capa gratuita) que cuesta una cantidad de 0.0104$ por hora, 0.2496$ por día, 1.7472$ por semana, 6.9888$ por mes y 83.8656$ por año. En caso de no tener la capa gratuita que da cierto tiempo gratis, es mucho más económico usar otro tipo de instancia como la **t2.nano** o **t3.nano**. Con la **t2.nano** el precio sería: 0.0058$ por hora, 0.1392$ por día, 0.9744$ por semana, 3.8976$ por mes y 46.7712$ por año.

- **Precio del AWS Fargate:** En el proyecto reserva 24/7 una cantidad de 0.25 de vCPU y 0.5GB de memoria.
  - Costo CPU: 0.25 * 0.04048$ por hora, 0.2428$ por día, 1.6996$ por semana, 6.7984$ por mes y 81.5808$ por año.
  - Costo Memoria: 0.5 * 0.004445 por hora, 0.05347$ por día, 0.3743$ por semana, 1.4972$ por mes y 17.9664$ por año.

- **Precio del NLB (Network Load Manager):** El NLB tiene un precio fijo de 0.0225$ por hora, por lo tanto, en un día cuesta 0.54$, 3.78$ por semana, 15.12$ al mes y 181.44$ al año.

- **Costos variables:** Adicionalmente, el proyecto tiene ciertos costos que son por el uso, son los siguientes:
  - API Gateway: Se paga por cada millón de peticiones al mes (con la capa gratuita, si no habría que especificar Quota y calcular los precios).
  - NLB (Procesamiento): Además del costo fijo, el NLB cobra por los datos que procesa (por NLCU-hora).
  - Transferencia de Datos: Cualquier dato que salga de AWS a Internet (ej. las respuestas de la API) tiene un costo.

Por lo tanto, los precios totales de la infraestructura son los siguientes (para los cálculos se va a usar la t2.nano dado que sería la que usaría sin la capa gratuita):

- **Coste por hora global:** 0.0406425$.
- **Coste por día global:** 0.97547$.
- **Coste por semana global:** 6.8283$.
- **Coste por mes global:** 27.3132$.
- **Coste por año global:** 327.7584$.

**NOTA:** No se están contemplando los precios variables en el cálculo de los totales.

## FUENTES Y DOCUMENTACIÓN

- **Internet:** Se ha utilizado internet para buscar diversos recursos, además de hacer mucho uso de la documentación propia de AWS ([AWS documentation](https://docs.aws.amazon.com)). Adicionalmente, se ha utilizado la página [Lucidchart](https://lucid.app) para realizar la creación del diagrama de la infraestructura creada.

- **Inteligencia Artificial Generativa (ChatGPT, Gemini):** Se ha utilizado la inteligencia artificial generativa para preguntar diversas dudas acerca de la creación de la propia infraestructura, funcionamiento de AWS y Docker, se ha utilizado para generar un código base, que posteriormente ha sido revisado y estudiado para modificar los campos y recursos para obtener la infraestructura con los requisitos necesarios y se ha utilizado para realizar revisiones explicativas y ejemplos de uso para comprender el funcionamiento de ciertos recursos.

- **Enlaces:**
    - https://docs.aws.amazon.com
    - https://lucid.app
    - https://aws.amazon.com/es/
    - https://chatgpt.com/
    - https://gemini.google.com
    - https://awsacademy.instructure.com

Para ver la versión desacoplada del proyecto, véase el direcotorio [Desacoplada](/Desacoplada/).