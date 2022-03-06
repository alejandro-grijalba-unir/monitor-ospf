from django.urls import path

from . import views

app_name = 'monitor'

urlpatterns = [
    path('', views.index, name='index'),
    path('visor/<str:archivo>', views.visor, name='visor'),
    path('visorestadisticas/<str:archivo>', views.visorestadisticas, name='visorestadisticas'),
    path('generar', views.generar, name='generar'),
]
