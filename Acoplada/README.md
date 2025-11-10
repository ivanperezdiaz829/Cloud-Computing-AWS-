# **Infraestructuras Acoplada y Desacoplada mediante AWS**

<h4 style="text-weight: bold">Diagrama de la Infraestructura:</h4>

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
