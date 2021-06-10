from django.urls import path

from . import views

app_name = 'myapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:archivo>/visor/', views.visor, name='visor'),
    path('generar', views.generar, name='generar'),
]
