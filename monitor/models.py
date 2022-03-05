from django.db import models
import routeros_api
from pathlib import Path
from datetime import datetime
import json


class Router(models.Model):
   ip = models.CharField(max_length=15)
   nombre = models.CharField(max_length=64)
   usuario = models.CharField(max_length=64)
   password = models.CharField(max_length=64)
