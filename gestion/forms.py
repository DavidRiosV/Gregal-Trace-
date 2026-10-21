from django import forms

from .models import Proyecto


class UrgenciaForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['nombre', 'tipo_destino', 'descripcion']
        labels = {
            'nombre': 'Nombre o dirección del trabajo',
            'tipo_destino': '¿Qué es?',
            'descripcion': 'Descripción',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo puede convertirse en Obra, Intervención o Mantenimiento, y es obligatorio
        self.fields['tipo_destino'].choices = [
            ('', 'Elige una opción'),
            ('OBR', 'Obra'),
            ('INT', 'Intervención'),
            ('MAN', 'Mantenimiento'),
        ]
        self.fields['tipo_destino'].required = True
