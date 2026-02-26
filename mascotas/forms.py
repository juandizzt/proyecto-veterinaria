from django import forms
from .models import Mascota

class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['nombre', 'dueño', 'especie', 'raza', 'edad', 'peso', 'observaciones']
        
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej: Max'}),
            'dueño': forms.Select(),
            'especie': forms.Select(choices=[
                ('', 'Seleccionar especie...'),
                ('Perro', 'Perro'),
                ('Gato', 'Gato'),
                ('Ave', 'Ave'),
                ('Otro', 'Otro'),
            ]),
            'raza': forms.TextInput(attrs={'placeholder': 'Ej: Labrador'}),
            'edad': forms.NumberInput(attrs={'step': '0.1'}),
            'peso': forms.NumberInput(attrs={'step': '0.1'}),
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super(MascotaForm, self).__init__(*args, **kwargs)
        # Configuramos el label vacío del dueño de forma segura
        if 'dueño' in self.fields:
            self.fields['dueño'].empty_label = "Seleccionar dueño..."
        
        # Aplicamos la clase 'custom-input' a TODOS los campos para el diseño centrado
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'custom-input'})