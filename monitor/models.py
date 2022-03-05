from django.db import models
import routeros_api
from pathlib import Path
from datetime import datetime
import pickle

class LSDB(models.Model):
   archivo = models.IntegerField(primary_key=True)
   nombre = models.CharField(max_length=64)
   
  
   # TODO: Deberia haber un formulario donde se escoja router y nombre de la captura
   def save(self, *args, **kwargs):
      if self._state.adding and self.archivo is None:
         self.archivo = int(datetime.now().timestamp())
      
         router = Router.objects.first()
         connection = routeros_api.RouterOsApiPool(router.ip, username=router.usuario, password=router.password, plaintext_login=True)
         api = connection.get_api()
         lsdb = api.get_resource('/routing/ospf/lsa')
         
         BASE_DIR = Path(__file__).resolve().parent.parent
         ruta = BASE_DIR / 'lsdb' / (str(self.archivo) + '.pickle')
         with open(ruta, 'wb') as f:
            pickle.dump(lsdb.get(), f, pickle.HIGHEST_PROTOCOL)

      super().save(*args, **kwargs)
   

class Router(models.Model):
   ip = models.CharField(max_length=15)
   nombre = models.CharField(max_length=64)
   usuario = models.CharField(max_length=64)
   password = models.CharField(max_length=64)
