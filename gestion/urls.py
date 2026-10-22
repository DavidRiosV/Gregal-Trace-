from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('proyectos/<slug:tipo>/', views.lista_proyectos, name='lista_proyectos'),
    path('urgencias/', views.urgencias, name='urgencias'),
    path('proyecto/<int:pk>/', views.detalle_proyecto, name='detalle_proyecto'),
    path('proyecto/<int:pk>/estado/', views.cambiar_estado, name='cambiar_estado'),
]