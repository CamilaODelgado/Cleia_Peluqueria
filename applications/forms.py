from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User  # Tu modelo personalizado

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['nombre', 'apellido', 'email', 'password1', 'password2']
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'email': 'Correo electrónico',
        }
        
from django import forms
from .models import User, Cliente, Empleado

class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['nombre', 'apellido', 'email']

class EditarClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['dni', 'fecha_nacimiento', 'telefono', 'domicilio']

class EditarEmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        # ahora el campo se llama 'puestos'
        fields = ['dni', 'fecha_nacimiento', 'telefono', 'domicilio', 'puestos']