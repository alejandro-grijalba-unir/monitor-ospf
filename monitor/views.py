from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
import json
from pathlib import Path
from os import walk
import re
import glob
import routeros_api
from datetime import datetime

from .models import Router

def index(request):
    #return HttpResponse("Hello, world. You're at the polls index.")
    #context = {'archivo': 'hola' }
    #context = {'lsdb' : LSDB.objects.all()}
    
    lista = glob.glob("lsdb/*.json")
    archivos = []
    for archivo in lista:
      nombre = re.sub(r'lsdb.(.*)\.json', r'\1', archivo)
      archivo={'nombre': nombre, 'archivo': nombre}
      archivos.append(archivo)
    context = {'lsdb' : archivos}
    print(context)
    return render(request, 'index.html', context)



def visor(request, archivo):
    BASE_DIR = Path(__file__).resolve().parent.parent
    ruta = BASE_DIR / 'lsdb' / (str(archivo) + '.json')
   
    try:
        with open(ruta, 'r') as f:
            contenido = json.load(f)
        lsdb = contenido['lsdb']
    except Exception as e:
        return HttpResponse("Hubo un error al leer el archivo LSDB indicado: " + str(e))

    grafo = {"routers": {}, "networks": {}}

    for lsa in lsdb:
        t = lsa["type"]
        
        if t == "router":
            idrouter = lsa["id"]
            #print(idrouter)
            if not idrouter in grafo['routers']:
                grafo['routers'][idrouter]=[]

            #print("type=" + lsa['type'])

            body = lsa["body"].splitlines()
            for l in body:
                # Routeros ~6.43
                match = re.match(r"^ *link-type=Point-To-Point.* id=([0-9.]+)", l)
                if not match:
                    # RouterOS ~6.49
                    match = re.match(r"^ *Point-To-Point ([0-9.]+)", l)
                if match:
                    vecino = match.group(1)
                    if not vecino in grafo['routers']  or not idrouter in grafo['routers'][vecino]:
                        grafo['routers'][idrouter].append(vecino)
                        #print(idrouter2.group(1))
                        pass
            #print("")
            
        elif t == "network":
            idnetwork = lsa["id"]
            
            if not idnetwork in grafo['networks']:
                grafo['networks'][idnetwork]=[]

            #print("type=" + lsa['type'])

            body = lsa["body"].splitlines()
            for l in body:
                match = re.match(r"^ *routerId=([0-9.]+)", l)
                if match:
                    vecino = match.group(1)
                    grafo['networks'][idnetwork].append(vecino)
                    #print(l)
                    pass
            #print("")

    fecha = re.sub(r' .*', '', contenido['fecha'])

    context = {
        'nombre': archivo,
        'contenido': contenido,
        'fecha': fecha,
        'grafo' : grafo,
    }

        
    #for lsa in lsdb:
    #  if (lsa['area'] == 'backbone'):
    #    print(lsa['id'], lsa['type'] , lsa['originator'] , lsa['area'], lsa['body'])
    
    return render(request, 'monitor/index.html', context)
    

# Generar archivo de volcado LSDB
def generar(request):
   if request.POST:
         archivo = request.POST['nombre']
     
         # TODO: Elegir router
         router = Router.objects.first()
         connection = routeros_api.RouterOsApiPool(router.ip, username=router.usuario, password=router.password, plaintext_login=True)
         api = connection.get_api()
         lsdb = api.get_resource('/routing/ospf/lsa')

         contenido = {
            'autor': request.user.username,
            'descripcion': '',
            'router': router.nombre,
            'fecha': datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S (%Z)"),
            'lsdb': lsdb.get(),
         }
         
         BASE_DIR = Path(__file__).resolve().parent.parent
         ruta = BASE_DIR / 'lsdb' / (str(archivo) + '.json')
         with open(ruta, 'w') as f:
            json.dump(contenido, f, indent=2)


         return HttpResponse("Generando archivo LSDB " + request.POST['nombre'])
      
