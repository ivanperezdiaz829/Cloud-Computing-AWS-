# **Infraestructuras Acoplada y Desacoplada mediante AWS**

<h4 style="text-weight: bold">Diagrama de la Infraestructura:</h4>

<img src="/Acoplada/Diagrama_Desacoplada.jpeg">

## Paso 1: Construir y Subir la imagen Docker Hacerlo con cada lambda

```bash
# El nombre y la región se modificará dependiendo de la imagen y la cuenta
aws ecr create-repository --repository-name lambda-create --region us-east-1
aws ecr create-repository --repository-name lambda-get --region us-east-1
aws ecr create-repository --repository-name lambda-update --region us-east-1
aws ecr create-repository --repository-name lambda-delete --region us-east-1
```

```bash
# Iniciar sesión de Docker en ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 098189193517.dkr.ecr.us-east-1.amazonaws.com
# Debería aparecer -> Login Succeeded
```

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

Tras lo anterior se deben ubicar dos nuevas imágenes en Docker, una con el nombre completo y la otra con el nombre elegido, en este caso "acoplada", aún teniendo diferente nombre, el image ID es el mismo dado que en realidad el nombre es un TAG que se ha puesto para diferenciar más comodamente las imágenes.

## Paso 2: Lanzar el Stack de CloudFormation

Entrar a VPC y obtener la el ID del VPC, de las subnets.

Obtener el host, nombre, usuario y contraseña de la Base de datos PostgreSQL a partir del db_postgres.yaml. Para ello, primero se ha de inicializar la Base de Datos mediante la interfaz gráfica usando la creación de Stacks y cargando la plantilla .yaml.

Para crear el Stack del main.yaml usar el siguiente comando

```bash
aws cloudformation create-stack `
--stack-name mi-app-desacoplada `
--template-body file://main.yaml `
--parameters file://parametros_desacoplada.json `
--capabilities CAPABILITY_IAM
```
