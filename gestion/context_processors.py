from django.db.models import Count

from .models import Proyecto
from .views import TIPOS, es_oficina


def navegacion(request):
    """Datos del menú que necesitan todas las páginas: contadores y sección activa."""
    if not request.user.is_authenticated:
        return {}

    conteo = {}
    for fila in Proyecto.objects.values('tipo', 'estado').annotate(n=Count('id')):
        conteo[(fila['tipo'], fila['estado'])] = fila['n']

    nav_tipos = {}
    for slug, datos in TIPOS.items():
        nav_tipos[slug] = {
            **datos,
            'en_proceso': conteo.get((datos['codigo'], 'PRO'), 0),
            'terminados': conteo.get((datos['codigo'], 'TER'), 0),
        }

    seccion = 'inicio'
    match = request.resolver_match
    if match and match.url_name == 'lista_proyectos':
        seccion = match.kwargs.get('tipo')
    elif match and match.url_name == 'urgencias':
        seccion = 'urgencias'

    return {
        'nav_tipos': nav_tipos,
        'nav_urgencias': conteo.get(('URG', 'PRO'), 0),
        'seccion': seccion,
        'usuario_oficina': es_oficina(request.user),
    }
