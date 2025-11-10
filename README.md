# INFRAESTRUCTURA ACOPLADA Y DESACOPLADA CON AWS

El proyecto consiste en dos partes principales, ambdas implementan el mismo sistema final para el usuario, una aplicación para la gestión empresarial de personas y departamentos haciendo uso de una base de datos de tipo PostgreSQL.

La primera de las partes consiste en la realización de ficha aplicación en base a una infraestructura ECS monolítica de AWS.
- Ver la documentación de la parte acoplada: [link](/Acoplada/) 

La segunda de las partes consiste en la realización de la misma aplicación pero de manera desacoplada usando lambdas para sustituir el diseño monolítico de ECS, como es una aplicación muy simple, las lambdas se crean para las funciones del CRUD de la aplicación:
- Ver la documentación de la parte desacoplada: [link](/Desacoplada/) 