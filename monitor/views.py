from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
import pickle
from pathlib import Path
from os import walk
import re

from .models import LSDB

def index(request):
   #return HttpResponse("Hello, world. You're at the polls index.")
   #context = {'archivo': 'hola' }
   context = {'lsdb' : LSDB.objects.all()}
   return render(request, 'index.html', context)



def visor(request, archivo):
    BASE_DIR = Path(__file__).resolve().parent.parent
    ruta = BASE_DIR / 'lsdb' / (str(archivo) + '.pickle')
   
    try:
        with open(ruta, 'rb') as f:
            lsdb = pickle.load(f)
    except:
        return HttpResponse("Hubo un error al leer el archivo LSDB indicado")

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
                match = re.match(r"^ *link-type=Point-To-Point.* id=([0-9.]+)", l)
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

   

    context = {
        'nombre': LSDB.objects.get(pk=archivo).nombre,
        'grafo' : grafo,
    }

        
    #for lsa in lsdb:
    #  if (lsa['area'] == 'backbone'):
    #    print(lsa['id'], lsa['type'] , lsa['originator'] , lsa['area'], lsa['body'])
    
    return render(request, 'monitor/index.html', context)
    

# Generar archivo de volcado LSDB
def generar(request):
   if request.POST:
      lsdb = LSDB(nombre=request.POST['nombre'])
      lsdb.save()
      return HttpResponse("Generando archivo LSDB " + request.POST['nombre'])
      
