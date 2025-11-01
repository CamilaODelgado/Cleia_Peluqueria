from django.contrib import admin

# Register your models here.
from .models import Cliente, Empleado, Servicios, Turnos, User



admin.site.register(Cliente)
admin.site.register(Empleado)
admin.site.register(Servicios)
admin.site.register(Turnos)
admin.site.register(User)

