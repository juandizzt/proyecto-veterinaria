# citas/forms.py
from django import forms
from .models import Cita
from datetime import date

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = [
            "mascota",
            "tipo_mascota",
            "tipo_servicio",
            "fecha_cita",
            "hora_cita",
            "descripcion",
            "telefono",
            "email",
        ]
        widgets = {
            "fecha_cita": forms.DateInput(
                attrs={
                    "type": "date",
                    "min": date.today().isoformat(),
                    "class": "form-control",
                }
            ),
            "hora_cita": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"}
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Describe los síntomas o motivo de la consulta...",
                    "class": "form-control",
                }
            ),
            "mascota": forms.TextInput(
                attrs={"placeholder": "Nombre de tu mascota", "class": "form-control"}
            ),
            "tipo_mascota": forms.TextInput(
                attrs={
                    "placeholder": "Ej: Perro, Gato, Conejo, etc.",
                    "class": "form-control",
                }
            ),
            "tipo_servicio": forms.Select(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(
                attrs={"placeholder": "Número de contacto", "class": "form-control"}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "correo@ejemplo.com", "class": "form-control"}
            ),
        }
        labels = {
            "mascota": "Nombre de la Mascota",
            "tipo_mascota": "Tipo de Mascota",
            "tipo_servicio": "Servicio Solicitado",
            "fecha_cita": "Fecha Deseada",
            "hora_cita": "Hora Deseada",
            "descripcion": "Motivo de la Consulta",
        }

    def clean_fecha_cita(self):
        fecha = self.cleaned_data["fecha_cita"]
        if fecha < date.today():
            raise forms.ValidationError("No puedes agendar citas en fechas pasadas.")
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get("fecha_cita")
        hora = cleaned_data.get("hora_cita")

        if fecha and hora:
            # Verificar si ya existe una cita en esa fecha y hora
            citas_existentes = Cita.objects.filter(fecha_cita=fecha, hora_cita=hora)
            if self.instance:
                citas_existentes = citas_existentes.exclude(pk=self.instance.pk)

            if citas_existentes.exists():
                raise forms.ValidationError(
                    "Ya existe una cita agendada para esta fecha y hora."
                )

        return cleaned_data

# COMENTAR O ELIMINAR ESTE FORMULARIO YA QUE NO EXISTE EL CAMPO 'estado'
# class CambiarEstadoForm(forms.ModelForm):
#     class Meta:
#         model = Cita
#         fields = ['estado']
#         widgets = {
#             'estado': forms.Select(attrs={'class': 'form-control'})
#         }
#         labels = {
#             'estado': 'Cambiar Estado'
#         }