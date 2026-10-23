from django.db import models
from django.conf import settings
from django.utils import timezone


class Perfil(models.Model):
    ROLES = [
        ('OPE', 'Operario'),
        ('OFI', 'Oficina'),
    ]
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rol = models.CharField(max_length=3, choices=ROLES, default='OPE')

    def __str__(self):
        return f"{self.usuario.username} ({self.get_rol_display()})"


class Proyecto(models.Model):
    TIPOS = [
        ('URG', 'Urgencia'),
        ('OBR', 'Obra'),
        ('INT', 'Intervención'),
        ('MAN', 'Mantenimiento'),
    ]
    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=3, choices=TIPOS, default='OBR')
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField(blank=True, null=True)
    ESTADOS = [
        ('PRO', 'En proceso'),
        ('TER', 'Terminado'),
    ]
    estado = models.CharField(max_length=3, choices=ESTADOS, default='PRO')
    notion_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    tipo_destino = models.CharField(max_length=3, choices=TIPOS, blank=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='proyectos_creados'
    )

    def esta_terminado(self):
        return self.estado == 'TER'

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class Material(models.Model):
    UNIDADES = [
        ('UD', 'Unidad'),
        ('M', 'Metro'),
        ('M2', 'Metro cuadrado'),
        ('KG', 'Kilogramo'),
        ('L', 'Litro'),
        ('H', 'Hora'),
    ]
    nombre = models.CharField(max_length=100, unique=True)
    unidad = models.CharField(max_length=2, choices=UNIDADES, default='UD')
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def abreviatura(self):
        """Unidad corta para mostrar junto a la cantidad: 2 h, 3 ud, 40 m."""
        return {'UD': 'ud', 'M': 'm', 'M2': 'm²', 'KG': 'kg', 'L': 'l', 'H': 'h'}.get(self.unidad, self.unidad.lower())

    def __str__(self):
        return f"{self.nombre} ({self.get_unidad_display()})"

class Consumo(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='consumos')
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name='consumos')
    trabajador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='consumos')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(default=timezone.now)

    def total(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} {self.material.nombre} - {self.proyecto.nombre}"


class Albaran(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='albaranes')
    archivo = models.FileField(upload_to='albaranes/%Y/%m/')
    subido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='albaranes')
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Albarán de {self.proyecto.nombre} ({self.fecha:%d/%m/%Y})"