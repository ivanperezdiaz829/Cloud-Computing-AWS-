# **INFRAESTRUCTURA DESACOPLADA DE LAMBDAS CON AWS**

Versión desacoplada de la infraestructura con un diseño basado en lambdas (4 de ellas) que se dividen las tareas del CRUD de la aplicación a crear.

<h3 style="text-weight: bold">Diagrama de la Infraestructura:</h3>

<img src="/Desacoplada/Diagrama_Desacoplada.jpeg">

## ÍNDICE

- [Componentes principales](#componentes-principales)
- [Estructura del proyecto](#estructura-del-proyecto)
- [API](#api)
- [Proceso de creación](#proceso-de-creación)
- [Presupuesto y gastos de la infraestructura](#presupuesto-y-gatos-de-la-infraestructura)
- [Fuentes y documentación](#fuentes-y-documentación)

## COMPONENTES PRINCIPALES

- **API Gateway (REST)**: Expone los recursos `items` e `item` (Personas individuales o en grupo) y enruta al backend vía VPC Link. Protegido con API Key.
- **Proxy**: Gestiona las peticiones a la base de datos y controla el tráfico de las peticiones de las lambdas.
- **4 lambdas**: Cada una posee su propio Dockerfile y .
- **Base de datos**: PostgreSQL (Amazon RDS) en el VPC, con SG de acceso al puerto 5432.
- **Amazon ECR**: Repositorio para la imagen del contenedor de Docker.

## ESTRUCTURA DEL PROYECTO

```bash
Desacoplada
    > db
          factory.py
          postgres_db.py
    > models
          item.py
    db_postgres.yaml
    Diagrama_Descoplada.jpeg
    Dockerfile.create
    Dockerfile.delete
    Dockerfile.get
    Dockerfile.update
    frontend.html
    lambda_create.py
    lambda_delete.py
    lambda_get.py
    lambda_update.py
    main.yaml
    parametros_desacoplada.json
    postgres.sql
    README.md
    requirements.txt
```

<h4 style="text-weight: bold">Directorio /Desacoplada/:</h4>

- **[db_postgres.yaml](/Desacoplada/db_postgres.yaml):** Plantilla para RDS PostgreSQL.
- **[Diagrama_Desacoplada.jpeg](/Desacoplada/Diagrama_Desacoplada.jpeg):** Diagrama de la Infraestructura del proyecto Acoplado con los componentes interconectados.
- **[Dockerfile.create](/Desacoplada/Dockerfile.create):** Imagen de la lambda que se ocupa de los **CREATE**.
- **[Dockerfile.delete](/Desacoplada/Dockerfile.delete):** Imagen de la lambda que se ocupa de los **DELETE**.
- **[Dockerfile.get](/Desacoplada/Dockerfile.get):** Imagen de la lambda que se ocupa de los **READ**.
- **[Dockerfile.update](/Desacoplada/Dockerfile.update):** Imagen de la lambda que se ocupa de los **UPDATE**.
- **[frontend.html](/Desacoplada/frontend.html):** HTML básico para probar la API vía API Gateway (pide la API Key y el API Endpoint para acceder).
- **[lambda_create.py](/Desacoplada/lambda_create.py):** Es la definición de la lambda que se encarga de las operaciones **CREATE**.
- **[lambda_delete.py](/Desacoplada/lambda_delete.py):** Es la definición de la lambda que se encarga de las operaciones **DELETE**.
- **[lambda_get.py](/Desacoplada/lambda_get.py):** Es la definición de la lambda que se encarga de las operaciones **READ**.
- **[lambda_update.py](/Desacoplada/lambda_update.py):** Es la definición de la lambda que se encarga de las operaciones **UPDATE**.
- **[main.yaml](/Desacoplada/lambda_update.py):** Es el fichero de definición que lanza la infraestructura.
- **[parametros_desacoplada.json](/Desacoplada/parametros_desacoplada.json):** Fichero JSON con todos los parámetros necesarios para lanzar el stack.
- **[postgres.sql](/Desacoplada/postgres.sql):** Crea una tabla localmente con la información necesaria para la base de datos.
- **[README.md](/Desacoplada/README.md):** Es el documento actual que explica la infraestructura del proyecto y define el funcionamiento.
- **[requirements.txt](/Desacoplada/requirements.txt):** Dependencias necesarias para que todo fucione correctamente.

<h4 style="text-weight: bold">Directorio Desacoplada/models:</h4>

- **[item.py](/Desacoplada/models/item.py):** Tiene la definición de una persona (campos y validación).

<h4 style="text-weight: bold">Directorio Desacoplada/db:</h4>

- **[postgres_db.py](/Desacoplada/db/postgres_db.py):** Implementación PostgreSQL.
- **[factory.py](/Desacoplada/db/factory.py):** Si en un futuro se quisiera implementar otro tipo de DB, aquí se puede seleccionar.

## API

La API posee los siguientes métodos para realizar peticiones mediante la aplicación.

  - **PostItemsMethod:** Crea nuevos items (Personas) con los parámetros que los componen.
  - **GetItemsMethod:** Obtiene todas los items (Obtiene lista de personas).
  - **GetItemMethod:** Obtiene un solo item (Obtiene Persona).
  - **PutItemMethod:** Modifica el item seleccionado (Edita Persona).
  - **DeleteItemMethod:** Elimina el item seleccionado (Elimina Persona).
  - **OptionsItemsMethod:** Es el uno de los Options que se usan para el CORS.
  - **OptionsItemMethod:** Es el otro de los Options que se usan para el CORS.

Los errores y respuestas se validan mediante *pydantic* y vienen definidas en los ficheros de las lambdas, [lambda_create.py](/Desacoplada/lambda_create.py), [lambda_delete.py](/Desacoplada/lambda_delete.py), [lambda_get.py](/Desacoplada/lambda_get.py), [lambda_update.py](/Desacoplada/lambda_update.py). 

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

Tras lo anterior y como primer paso para la creación de la infraestructura de desacoplada se procede a la creación de la base de datos, para ello y haciendo uso de la consola de CloudFormation se va a crear un nuevo stack cargando la plantilla [db_postgres.yaml](/Desacoplada/db_postgres.yaml) y poniendo como contraseña (necesario poner la misma para este proyecto dado que es uno de los parámetros del [parametros_desacoplada.json](/Desacoplada/parametros_desacoplada.json)) "entra123". Las subnets seleccionadas se han de guardar para ponerlas también en el mismo fichero [parametros_main.json](/Acoplada/parametros_main.json) y también la VPC. Una vez realizados los pasos anteriores, se lanza el stack con la base de datos.

Una vez ponga **CREATE_COMPLETE** se puede pasar al siguiente paso.

Para este paso es necesario crear el repositorio **ECR** que lance la aplicación a través de Docker, y para ello se han de utilizar los siguientes comandos (el número que aparece en algunos de ellos al principio de una cadena tal que "NÚMERO".dkr.):

1. Crear los repositorios ECR (1 por cada lambda):

      ```bash
      # El nombre y la región se modificará dependiendo de la imagen y la cuenta
      aws ecr create-repository --repository-name lambda-create --region us-east-1
      aws ecr create-repository --repository-name lambda-get --region us-east-1
      aws ecr create-repository --repository-name lambda-update --region us-east-1
      aws ecr create-repository --repository-name lambda-delete --region us-east-1
      ```

2. Iniciar sesión de Docker en ECR:

      ```bash
      # Debería aparecer -> Login Succeeded
      aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 098189193517.dkr.ecr.us-east-1.amazonaws.com
      ```

3. Contruir imagenes de las lambdas y subir la imagenes a ECR:

      ```bash
      # dockerfile create
      docker buildx build --platform linux/amd64 --provenance=false -f Dockerfile.create -t 098189193517.dkr.ecr.us-east-1.amazonaws.com/lambda-create:latest --load .
      docker push 098189193517.dkr.ecr.us-east-1.amazonaws.com/lambda-create:latest
      ```

      ```bash
      # dockerfile get
      docker buildx build --platform linux/amd64 --provenance=false -f Dockerfile.get -t 098189193517.dkr.ecr.us-east-1.amazonaws.com/lambda-get:latest --load .
      docker push 098189193517.dkr.ecr.us-east-1.amazonaws.com/lambda-get:latest
      ```

      ```bash
      # dockerfile update
      docker buildx build --platform linux/amd64 --provenance=false -f Dockerfile.update -t 098189193517.dkr.ecr.us-east-1.amazonaws.com/lambda-update:latest --load .
      docker push 098189193517.dkr.ecr.us-east-1.amazonaws.com/lambda-update:latest
      ```

      ```bash
      # dokerfile delete
      docker buildx build --platform linux/amd64 --provenance=false -f Dockerfile.delete -t 098189193517.dkr.ecr.us-east-1.amazonaws.com/lambda-delete:latest --load .
      docker push 098189193517.dkr.ecr.us-east-1.amazonaws.com/lambda-delete:latest
      ```

4. Lanzar el Stack de Cloud Formation:

      ```bash
      aws cloudformation create-stack `
      --stack-name mi-app-desacoplada `
      --template-body file://main.yaml `
      --parameters file://parametros_desacoplada.json `
      --capabilities CAPABILITY_IAM
      ```

Una vez el Stack lanzado ponga **CREATE_COMPLETE** y antes de dar por terminada la versión desacoplada, se va a crear un grupo de seguridad y el *Proxy* que se encargará de manejar los datos de la base de datos mediante las solicitudes de las lambdas. Para crear el grupo de seguiridad, se puede hacer directamente desde la consola de *EC2*, al grupo de seguridad de le ha de poner como grupo de entrada el de la aplicación recien lanzada y tras esto, en el apartado de la consola *Aurora RDS* llamado *Proxies* se crea el proxy con el grupo de seguridad y las subredes anteriormente mencionadas.

Con todo lo anterior, se podrá entrar dentro de la aplicación final y gestionar los items (personas) haciendo peticiones a la API de CREATE, READ, UPDATE y DELETE pero con una infraestructurea gestionada de manera desacoplada.

## PRESUPUESTO Y GASTOS DE LA INFRAESTRUCTURA

La infraestructura lanzada no es gratis de mantener, teniendo un costo por uso o por existencia en el tiempo, todos estos gastos son necesarios conocerlos para crear una infraestructura económica y que supla los requerimientos.

- **Precio e instancia de la Base de datos:** Se usa la **t3.micro** (temas de que es temporalmente gratis para la capa gratuita) que cuesta una cantidad de 0.0104$ por hora, 0.2496$ por día, 1.7472$ por semana, 6.9888$ por mes y 83.8656$ por año. En caso de no tener la capa gratuita que da cierto tiempo gratis, es mucho más económico usar otro tipo de instancia como la **t2.nano** o **t3.nano**. Con la **t2.nano** el precio sería: 0.0058$ por hora, 0.1392$ por día, 0.9744$ por semana, 3.8976$ por mes y 46.7712$ por año.

- **Precio de las lambdas:** Las lambdas de por si no tienen un coste fijo sino que se empiezan a cobrar a partir del millón de invocaciones al mes.

- **Proxy RDS:** Dependiendo de la máquina de la base de datos el precio del proxy cambia, en este caso, se va a suponer que se usa la t2.nano por lo que los costos quedarán tal que: 0.0116$ por hora, 0.2784$ por día, 1.9488$ por semana, 7.7952$ por mes y 93.5424$ por año.

- **Costos variables:** Adicionalmente, el proyecto tiene ciertos costos que son por el uso, son los siguientes:
  - API Gateway: Se paga por cada millón de peticiones al mes (con la capa gratuita, si no habría que especificar Quota y calcular los precios).
  - Transferencia de Datos: Cualquier dato que salga de AWS a Internet (ej. las respuestas de la API) tiene un costo.

Por lo tanto, los precios totales de la infraestructura son los siguientes (para los cálculos se va a usar la t2.nano dado que sería la que usaría sin la capa gratuita):

- **Coste por hora global:** 0.0174$.
- **Coste por día global:** 0.4176$.
- **Coste por semana global:** 2.9232$.
- **Coste por mes global:** 11.6928$.
- **Coste por año global:** 140.3136$.

**NOTA:** No se están contemplando los precios variables en el cálculo de los totales y se están tomando en cuenta los cálculos con la t2.nano (en el proyecto se usa la t3.micro que es gratis 12 meses con la capa gratuita).

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

Para ver la versión acoplada del proyecto, véase el direcotorio [Acoplada](/Acoplada/).