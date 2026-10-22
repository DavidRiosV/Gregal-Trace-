from django import forms

from .models import Consumo, Proyecto


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


class ConsumoForm(forms.ModelForm):
    class Meta:
        model = Consumo
        fields = ['material', 'cantidad', 'fecha']
        labels = {
            'material': 'Material u horas',
            'cantidad': 'Cantidad',
            'fecha': 'Fecha',
        }
        widgets = {
            'cantidad': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'inputmode': 'decimal'}),
            'fecha': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['material'].empty_label = 'Elige material u horas'

    def clean_cantidad(self):
        cantidad = self.cleaned_data['cantidad']
        if cantidad <= 0:
            raise forms.ValidationError('La cantidad tiene que ser mayor que 0.')
        return cantidad
