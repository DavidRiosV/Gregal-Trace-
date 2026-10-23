from datetime import date

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import DecimalField, F, Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ConsumoForm, UrgenciaForm
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
    proyectos = Proyecto.objects.filter(tipo=datos_tipo['codigo']).order_by('-fecha_inicio', '-id')

    # Filtro por estado: en proceso (por defecto), terminados o todos
    estado = request.GET.get('estado', 'PRO')
    if estado not in ('PRO', 'TER', 'todos'):
        estado = 'PRO'
    if estado != 'todos':
        proyectos = proyectos.filter(estado=estado)

    busqueda = request.GET.get('q', '').strip()
    if busqueda:
        proyectos = proyectos.filter(
            Q(nombre__icontains=busqueda) | Q(descripcion__icontains=busqueda)
        )

    return render(request, 'gestion/lista_proyectos.html', {
        'proyectos': proyectos,
        'titulo': datos_tipo['titulo'],
        'slug': tipo,
        'busqueda': busqueda,
        'estado_actual': estado,
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

    abiertas = Proyecto.objects.filter(tipo='URG', estado='PRO').select_related('creado_por').order_by('-fecha_inicio', '-id')

    return render(request, 'gestion/urgencias.html', {
        'formulario': formulario,
        'urgencias': abiertas,
    })


def es_oficina(usuario):
    """Oficina (y el superusuario) ven los precios; los operarios no."""
    if usuario.is_superuser:
        return True
    perfil = getattr(usuario, 'perfil', None)
    return perfil is not None and perfil.rol == 'OFI'


def detalle_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto.objects.select_related('creado_por'), pk=pk)

    if request.method == 'POST' and not proyecto.esta_terminado():
        formulario = ConsumoForm(request.POST)
        if formulario.is_valid():
            consumo = formulario.save(commit=False)
            consumo.proyecto = proyecto
            consumo.trabajador = request.user
            consumo.precio_unitario = consumo.material.precio
            consumo.save()
            messages.success(
                request,
                f'Apuntado: {consumo.cantidad:g} {consumo.material.abreviatura()} de {consumo.material.nombre}.'
            )
            return redirect('detalle_proyecto', pk=proyecto.pk)
    else:
        formulario = ConsumoForm()

    consumos = proyecto.consumos.select_related('material', 'trabajador').order_by('-fecha', '-id')
    horas = consumos.filter(material__unidad='H').aggregate(total=Sum('cantidad'))['total'] or 0

    # Página a la que vuelve el botón de volver
    if proyecto.tipo == 'URG':
        url_volver, texto_volver = 'urgencias', 'Urgencias'
    else:
        slug = next(s for s, datos in TIPOS.items() if datos['codigo'] == proyecto.tipo)
        url_volver, texto_volver = 'lista_proyectos', TIPOS[slug]['titulo']

    contexto = {
        'proyecto': proyecto,
        'formulario': formulario,
        'consumos': consumos,
        'es_oficina': es_oficina(request.user),
        'url_volver': url_volver,
        'slug_volver': None if proyecto.tipo == 'URG' else slug,
        'texto_volver': texto_volver,
        'horas': horas,
        # Marca en el menú el apartado al que pertenece el proyecto
        'seccion': 'urgencias' if proyecto.tipo == 'URG' else slug,
    }

    if contexto['es_oficina']:
        total = consumos.aggregate(
            total=Sum(F('cantidad') * F('precio_unitario'),
                      output_field=DecimalField(max_digits=12, decimal_places=2))
        )['total']
        contexto['coste_total'] = total or 0

    return render(request, 'gestion/detalle_proyecto.html', contexto)


@require_POST
def cambiar_estado(request, pk):
    """Oficina marca un proyecto como terminado o lo vuelve a poner en proceso."""
    if not es_oficina(request.user):
        raise PermissionDenied('Solo Oficina puede cambiar el estado de un proyecto.')

    proyecto = get_object_or_404(Proyecto, pk=pk)
    if proyecto.esta_terminado():
        proyecto.estado = 'PRO'
        proyecto.fecha_fin = None
        messages.success(request, f'«{proyecto.nombre}» vuelve a estar en proceso.')
    else:
        proyecto.estado = 'TER'
        proyecto.fecha_fin = date.today()
        messages.success(request, f'«{proyecto.nombre}» marcado como terminado.')
    proyecto.save()
    return redirect('detalle_proyecto', pk=proyecto.pk)
