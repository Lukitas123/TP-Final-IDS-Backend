# Backend - TP-Final 

Este repositorio contiene el **backend del proyecto Hotel Bugbusters**, desarrollado como parte del TP final de Introducción al Desarrollo de Software (FIUBA).  
Es una base de datos PostgreSQL hosteada en linea que contiene los datos de un hotel.
Entre ellos se encuentra las habitaciones, paquetes, precios. También es capaz de almacenar los distintos tipos de reservaciones que se pueden hacer.

**Integrantes**
- Florian Lucchini
- Lukas Peneff
- Harold Montaño
- Lautaro Cosentino
- Santino Salvatori

## Objetivo del Backend

- Almacenar las tablas con los distintos datos.
- Poder ser consultado y devolver los datos de las tablas almacenadas.
- Poder recibir nuevos datos y almacenarlos en las tablas designadas.
- Contener la business logic del proyecto.

## Tecnologías utilizadas
Utilizamos la convención [snake_case](https://developer.mozilla.org/en-US/docs/Glossary/Snake_case) para los nombres de variables.
- Python + Flask 
- Flask_cors
- Jinja2 
- Psycopg2
- Requests
- Docker
- Git
- itsdangerous
- MarkupSafe
- dotenv
- Werkzeug

## Inicialización
**Crear entorno virtual**<br>
Desde la carpeta de cada proyecto TP-Final-IDS-Frontend y 'TP-Final-IDS-Backend'.
<br>
```
# Linux 
python3 -m venv .venv

# Windows
python -m venv .venv
```


**Activar el entorno virtual**
```
# Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

**Instalar dependencias**
```
pip install -r requirements.txt
```
**Iniciar el servidor de desarrollo**
```
flask run
```

**Desactivar el entorno virtual**
```
# Linux
deactivate .venv/bin/activate

# Windows
deactivate .venv\Scripts\activate
```
