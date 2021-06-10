from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
import pickle
from pathlib import Path


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

   context = {
     'nombre': LSDB.objects.get(pk=archivo).nombre,
     'lsdb' : lsdb,
   }

      
   #for lsa in lsdb:
   #  if (lsa['area'] == 'backbone'):
   #    print(lsa['id'], lsa['type'] , lsa['originator'] , lsa['area'], lsa['body'])
   
   return render(request, 'myapp/index.html', context)
   

def generar(request):
   if request.POST:
      lsdb = LSDB(nombre=request.POST['nombre'])
      lsdb.save()
      return HttpResponse("Generando archivo LSDB " + request.POST['nombre'])
      
