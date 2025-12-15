# usuarios/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UsuariosRoles  # ← CAMBIAR de User a UsuariosRoles

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ejemplo@correo.com'
        })
    )
    
    # Campo adicional para nombre completo
    nombre_completo = forms.CharField(
        max_length=150,
        label="Nombre Completo",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Juan Diego Pérez González'
        }),
        help_text="Tu nombre completo (puede contener espacios)"
    )
    
    # Campo para teléfono (adicional)
    telefono = forms.CharField(
        max_length=15,
        label="Teléfono",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 3001234567'
        })
    )
    
    # Modificar el campo username para que sea más amigable
    username = forms.CharField(
        max_length=150,
        label="Nombre de Usuario para Iniciar Sesión",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: juan.diego, juan123, juan_diego'
        }),
        help_text='''
        <div class="help-text requirement-list">
            <strong>Requerido para iniciar sesión.</strong> 150 caracteres como máximo.<br>
            <strong>Puede contener:</strong>
            <ul>
                <li>Letras (a-z, A-Z)</li>
                <li>Números (0-9)</li>
                <li>Los caracteres especiales: @ . + - _</li>
                <li><strong>NO se permiten espacios</strong></li>
            </ul>
            <strong>Ejemplos:</strong> juan.diego, juan123, juan_diego
        </div>
        '''
    )
    
    class Meta:
        model = UsuariosRoles  # ← CAMBIAR de User a UsuariosRoles
        fields = ("nombre_completo", "username", "email", "telefono", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Mejorar las etiquetas
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar Contraseña'
        
        # Definir el orden de los campos explícitamente
        self.order_fields(['nombre_completo', 'username', 'email', 'telefono', 'password1', 'password2'])
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Verificar que no tenga espacios
        if ' ' in username:
            # Sugerir alternativas
            suggestions = [
                username.replace(' ', ''),
                username.replace(' ', '_'),
                username.replace(' ', '.'),
                username.split(' ')[0].lower() + '123'
            ]
            
            raise forms.ValidationError(
                f'El nombre de usuario no puede contener espacios. '
                f'Sugerencias: {", ".join([f"{s}" for s in suggestions if s])}'
            )
        
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UsuariosRoles.objects.filter(email=email).exists():  # ← CAMBIAR aquí
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        
        # Guardar nombre completo en first_name
        nombre_completo = self.cleaned_data.get('nombre_completo')
        if nombre_completo:
            user.first_name = nombre_completo
        
        # Guardar teléfono si existe
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            user.telefono = telefono
        
        if commit:
            user.save()
        return user