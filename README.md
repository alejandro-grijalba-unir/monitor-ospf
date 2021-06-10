# Monitor OSPF

Esta herramienta permite supervisar y hacer consultas sobre redes OSPF.

Para su funcionamiento requiere de al menos un router con API RouterOS integrado en la red OSPF.

Ha sido desarrollada como un Trabajo de Fin de Grado para el Grado en Informática de la Universidad Internacional de La Rioja (UNIR).


## Instalacion

Requiere de Python 3.6 y Django 3.2.

```
git clone https://github.com/alejandro-grijalba-unir/monitor-ospf.git
git pull && python3 manage.py makemigrations && python3 manage.py migrate --run-syncdb
python3 manage.py createsuperuser
```

## Ejecucion

`python3 manage.py runserver`

## Configuración

1. Acceder a http://localhost:8000/admin/monitor/router/
2. Dar de alta un router que tenga habilitada la API
3. Ir a la seccion principal y generar una instantánea de la red http://localhost:8000/

A partir de ahí se puede analizar la red.
