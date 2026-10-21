from django.contrib import messages
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, render

from .forms import UrgenciaForm
from .models import Proyecto

# Apartados de listado: traduce la palabra de la URL al código guardado en la base de datos.
# Urgencias no está aquí porque tiene su propia página (sirve para crear, no para buscar).
TIPOS = {
    'obras': {'codigo': 'OBR', 'titulo': 'Obras', 'imagen': 'img/categorias/obras.jpg'},
    'intervenciones': {'codigo': 'INT', 'titulo': 'Intervenciones', 'imagen': 'img/categorias/intervenciones.jpg'},
    'mantenimientos': {'codigo': 'MAN', 'titulo': 'Mantenimientos', 'imagen': 'img/categorias/mantenimientos.jpg'},
}


def index(request):
    return render(request, 'gestion/index.html', {'tipos': TIPOS})


def lista_proyectos(request, tipo):
    if tipo not in TIPOS:
        raise Http404('Tipo de proyecto no válido')

    datos_tipo = TIPOS[tipo]
    proyectos = Proyecto.objects.filter(tipo=datos_tipo['codigo'], abierto=True).order_by('-fecha_inicio')

    busqueda = request.GET.get('q', '').strip()
    if busqueda:
        proyectos = proyectos.filter(
            Q(nombre__icontains=busqueda) | Q(descripcion__icontains=busqueda)
        )

    return render(request, 'gestion/lista_proyectos.html', {
        'proyectos': proyectos,
        'titulo': datos_tipo['titulo'],
        'busqueda': busqueda,
    })


def urgencias(request):
    if request.method == 'POST':
        formulario = UrgenciaForm(request.POST)
        if formulario.is_valid():
            urgencia = formulario.save(commit=False)
            urgencia.tipo = 'URG'
            urgencia.creado_por = request.user
            urgencia.save()
            autor = request.user.get_full_name() or request.user.username
            messages.success(
                request,
                f'Urgencia «{urgencia.nombre}» creada por {autor} el {urgencia.fecha_inicio:%d/%m/%Y}.'
            )
            return redirect('urgencias')
    else:
        formulario = UrgenciaForm()

    abiertas = Proyecto.objects.filter(tipo='URG', abierto=True).select_related('creado_por').order_by('-fecha_inicio', '-id')

    return render(request, 'gestion/urgencias.html', {
        'formulario': formulario,
        'urgencias': abiertas,
    })
