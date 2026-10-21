from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('proyectos/<slug:tipo>/', views.lista_proyectos, name='lista_proyectos'),
    path('urgencias/', views.urgencias, name='urgencias'),
]