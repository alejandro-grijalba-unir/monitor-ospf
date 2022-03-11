from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
import json
from pathlib import Path
from os import walk
import re
import glob
import routeros_api
from datetime import datetime
from ipaddress import IPv4Network, IPv4Address
import os.path

from .models import Router

def index(request):
   
    # Listar archivos
    lista = glob.glob("lsdb/*.json")
    lista.sort()
    archivos = []
    for archivo in lista:
      nombre = re.sub(r'lsdb.(.*)\.json', r'\1', archivo)
      res, contenido, lsdb = cargar(request, nombre)
      if contenido and 'fecha' in contenido:
          fecha = contenido['fecha']
      else:
          fecha=""
      archivo={'nombre': nombre, 'archivo': nombre, 'fecha': fecha}
      archivos.append(archivo)
    context = {'lsdb' : archivos}

    #print(context)
    return render(request, 'index.html', context)


def cargar(request, archivo):
    BASE_DIR = Path(__file__).resolve().parent.parent
    ruta = BASE_DIR / 'lsdb' / (str(archivo) + '.json')
   
    try:
        with open(ruta, 'r') as f:
            contenido = json.load(f)
        lsdb = contenido['lsdb']
    except FileNotFoundError as e:
        return HttpResponse("No existe el archivo LSDB indicado."), None, None
    except Exception as e:
        return HttpResponse("Hubo un error al leer el archivo LSDB indicado.\n<br/><br/>Error: <pre>" + str(e) + "</pre>"), None, None

    return None, contenido, lsdb


def visor(request, archivo):
    res, contenido, lsdb = cargar(request, archivo)
    if res:
        return res

    # El grafo a dibujar
    #  Cada router contiene una lista de routers vecinos
    #  Cada red broadcast contiene una lista de routers vecinos
    grafo = {
                "routers": {},
                "networks": {},
    }
    

    # Analizar cada entrada LSA
    for lsa in lsdb:
        t = lsa["type"]
        
        # LSA de tipo ROUTER
        if t == "router":
            idrouter = lsa["id"]

            # Añadir el router a la lista si no estaba
            if not idrouter in grafo['routers']:
                grafo['routers'][idrouter]={'vecinos':[], 'subredes':[]}

            # Analizar el cuerpo del LSA
            body = lsa["body"].splitlines()
            for l in body:
                # Link PTP
                # Routeros ~6.43
                match = re.match(r"^ *link-type=Point-To-Point.* id=([0-9.]+)", l)
                if not match:
                    # RouterOS ~6.49
                    match = re.match(r"^ *Point-To-Point ([0-9.]+)", l)
                if match:
                    vecino = match.group(1)
                    # Añadir vecino (ptp) si no se ha añadido antes
                    if not vecino in grafo['routers']  or not idrouter in grafo['routers'][vecino]:
                        grafo['routers'][idrouter]['vecinos'].append(vecino)

                # Link STUB
                # Routeros ~6.43
                match = re.match(r"^ *link-type=Stub.* id=([0-9.]+) data=([0-9.]+)", l)
                if not match:
                    # RouterOS ~6.49
                    match = re.match(r"^ *Stub ([0-9.]+) ([0-9.]+)", l)
                if match:
                    mascara = match.group(2)
                    prefijo = IPv4Network('0.0.0.0/' + mascara).prefixlen
                    subred = match.group(1) + "/" + str(prefijo)
                    grafo['routers'][idrouter]['subredes'].append(subred)

        # LSA de tipo NETWORK
        elif t == "network":
            idnetwork = lsa["id"]
           
            # Añadir la red al grafo como un nodo
            if not idnetwork in grafo['networks']:
                grafo['networks'][idnetwork]={'vecinos':[]}


            # Analizar el cuerpo del LSA
            body = lsa["body"].splitlines()
            for l in body:
                match = re.match(r"^ *routerId=([0-9.]+)", l)
                if match:
                    # Añadir el router vecino
                    vecino = match.group(1)
                    grafo['networks'][idnetwork]['vecinos'].append(vecino)

    fecha = re.sub(r' .*', '', contenido['fecha'])

    context = {
        'nombre': archivo,
        'contenido': contenido,
        'fecha': fecha,
        'grafo' : grafo,
    }
    
    return render(request, 'monitor/index.html', context)


def visorestadisticas(request, archivo):
    res, contenido, lsdb = cargar(request, archivo)
    if res:
        return res

    grafo = {"routers": {}, "networks": {}}

    num_routers = 0
    num_ptp = 0
    num_bcast = 0
    num_subredes = 0

    subredes = []
    vecinos = []

    # Analizar cada entrada LSA
    for lsa in lsdb:
        t = lsa["type"]
        
        # LSA de tipo ROUTER
        if t == "router":
            num_routers = num_routers + 1
            idrouter = lsa["id"]

            # Añadir el router a la lista si no estaba
            if not idrouter in grafo['routers']:
                grafo['routers'][idrouter]=[]

            # Analizar el cuerpo del LSA
            body = lsa["body"].splitlines()
            for l in body:
                # Link PTP
                # Routeros ~6.43
                match = re.match(r"^ *link-type=Point-To-Point.* id=([0-9.]+) data=([0-9.]+)", l)
                if not match:
                    # RouterOS ~6.49
                    match = re.match(r"^ *Point-To-Point ([0-9.]+) ([0-9.]+)", l)
                if match:
                    vecino = match.group(1)
                    vecinos.append(match.group(2))
                    # Añadir vecino (ptp) si no se ha añadido antes
                    if not vecino in grafo['routers']  or not idrouter in grafo['routers'][vecino]:
                        num_ptp = num_ptp + 1
                        grafo['routers'][idrouter].append(vecino)

                # Link STUB
                # Routeros ~6.43
                match = re.match(r"^ *link-type=Stub.* id=([0-9.]+) data=([0-9.]+)", l)
                if not match:
                    # RouterOS ~6.49
                    match = re.match(r"^ *Stub ([0-9.]+) ([0-9.]+)", l)
                if match:
                    mascara = match.group(2)
                    prefijo = IPv4Network('0.0.0.0/' + mascara).prefixlen
                    subred = match.group(1) + "/" + str(prefijo)
                    #if not subred in subredes:
                    subredes.append(subred)
                    #num_subredes = num_subredes + 1
           
        # LSA de tipo NETWORK
        elif t == "network":
            idnetwork = lsa["id"]
            
            # Añadir la red al grafo como un nodo
            if not idnetwork in grafo['networks']:
                num_bcast = num_bcast + 1
                grafo['networks'][idnetwork]=[]


            # Analizar el cuerpo del LSA
            body = lsa["body"].splitlines()
            for l in body:
                match = re.match(r"^ *routerId=([0-9.]+)", l)
                if match:
                    vecino = match.group(1)
                    grafo['networks'][idnetwork].append(vecino)

    fecha = re.sub(r' .*', '', contenido['fecha'])

    # Buscar redes duplicadas
    #  1. No tener en cuenta las redes ptp
    for vecino in vecinos:
        for subred in subredes:
            if IPv4Network(vecino + '/32').subnet_of(IPv4Network(subred)):
                subredes.remove(subred)

    num_subredes = len(subredes)

    duplicados = []
    #  2. Ver si hay duplicados
    for i in range(0,len(subredes)):
        for j in range(i+1, len(subredes)):
            if IPv4Network(subredes[i]).subnet_of(IPv4Network(subredes[j])):
                duplicados.append(subredes[i])

    context = {
        'nombre': archivo,
        'contenido': contenido,
        'fecha': fecha,
        'num_routers': num_routers,
        'num_ptp': num_ptp,
        'num_bcast': num_bcast,
        'num_subredes': num_subredes,
        'duplicados': duplicados,
        'grafo' : grafo,
    }
    
    return render(request, 'monitor/visorestadisticas.html', context)


# Vista para la generacion de una instantanea
def generar(request):
    context = { 
            'routers': Router.objects.all()
    }
    return render(request, 'monitor/generar.html', context)


# Generar archivo de volcado LSDB
def generar_post(request):
   if request.POST:
         archivo_original = request.POST['nombre']
         archivo = re.sub(r'[^A-Za-z0-9]+', '_', archivo_original)

         # Comprobar ruta vacia
         if len(archivo) < 1:
             return HttpResponse("Error! Debe especificar un nombre de archivo<br/><br/><a href='#' onclick='history.back()'>Volver</a>")
     
         BASE_DIR = Path(__file__).resolve().parent.parent
         ruta = BASE_DIR / 'lsdb' / (str(archivo) + '.json')

         # Comprobar ruta
         if os.path.exists(ruta):
             return HttpResponse("Error! El archivo " + archivo + " ya existe<br/><br/><a href='#' onclick='history.back()'>Volver</a>")

      
         # Comprobar router
         try:
            router = Router.objects.get(pk=int(request.POST['router']))
         except Router.DoesNotExist:
             return HttpResponse("Error! Debe seleccionar un router válido<br/><br/><a href='#' onclick='history.back()'>Volver</a>")


         # Generar instantanea
         try:
             connection = routeros_api.RouterOsApiPool(router.ip, username=router.usuario, password=router.password, plaintext_login=True)
             api = connection.get_api()
             lsdb = api.get_resource('/routing/ospf/lsa')
         except Exception as e:
             return HttpResponse("Error! Hubo un error al intentar generar la instantanea: <pre>"+ str(e) +"</pre><br/><br/><a href='#' onclick='history.back()'>Volver</a>")


         contenido = {
            'autor': request.user.username,
            'descripcion': '',
            'router': router.nombre,
            'fecha': datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S (%Z)"),
            'lsdb': lsdb.get(),
         }
         

         with open(ruta, 'w') as f:
            json.dump(contenido, f, indent=2)


         return HttpResponse("Generado archivo LSDB " + archivo + "<br/><br/><a href='/'>Inicio</a>")
      
