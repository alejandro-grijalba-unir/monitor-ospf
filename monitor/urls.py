from django.urls import path

from . import views

app_name = 'monitor'

urlpatterns = [
    path('', views.index, name='index'),
    path('visor/<str:archivo>', views.visor, name='visor'),
    path('generar', views.generar, name='generar'),
]
