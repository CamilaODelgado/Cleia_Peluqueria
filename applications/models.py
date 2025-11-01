from django.db import models
from datetime import date

#################################################################
# MODELO DE USUARIO PERSONALIZADO Y DEMAS MODELOS
#################################################################

from django.contrib.auth.models import AbstractUser, BaseUserManager

# Para las señales de crear perfil automático 
from django.db.models.signals import post_save
from django.dispatch import receiver

# ==============================
# MANAGER PERSONALIZADO
# ==============================

class CustomUserManager(BaseUserManager):
    ############### Crear usuario normal
    def create_user(self, email, password=None, **extra_fields):
        # Email es el campo obligatorio
        if not email:
            raise ValueError('El campo Email es obligatorio.')

        email = self.normalize_email(email)

        # Por defecto, todo usuario creado desde la web será cliente
        extra_fields.setdefault('is_cliente', True)
        extra_fields.setdefault('is_empleado', False)
        extra_fields.setdefault('is_admin', False)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        # Crear el usuario con los campos proporcionados
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    ############### Crear superusuario
    def create_superuser(self, email, password=None, **extra_fields):
        
        # Asegurarse de que los campos necesarios para un superusuario estén establecidos en True
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_empleado', True)
        extra_fields.setdefault('is_cliente', False)
        
        # Validar que los campos estén correctamente establecidos
        if extra_fields.get('is_admin') is not True:
            raise ValueError('El superusuario debe tener is_admin=True.')

        return self.create_user(email, password, **extra_fields)

# ==============================
# MODELO DE USUARIO PERSONALIZADO
# ==============================

class User(AbstractUser):
    
    # Eliminar los campos username, first_name y last_name de AbstractUser
    username = None
    first_name = None
    last_name = None

    # Definir email como el campo único de identificación
    email = models.EmailField('Correo electrónico', unique=True)
    
    
    nombre = models.CharField('Nombre', max_length=50)
    apellido = models.CharField('Apellido', max_length=50)
    
    # Campos para diferenciar roles
    is_cliente = models.BooleanField(default=False)
    is_empleado = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    def get_full_name(self):
        return f"{self.nombre} {self.apellido}".strip()

    def get_short_name(self):
        return self.nombre

    def __str__(self):
        rol = "Empleado" if self.is_empleado else (
                "Cliente" if self.is_cliente else "Usuario"
            )
        
        return f"{self.get_full_name()} ({rol}) - {self.email}"

# ==============================
# MODELOS DE LA APLICACION
# ==============================

class Cliente(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='cliente',
        limit_choices_to={'is_cliente': True}, # solo usuarios con is_cliente=True
        )
    
    dni = models.CharField(max_length=8, verbose_name='DNI', null=True, blank=True)
    fecha_nacimiento = models.DateField('Fecha de nacimiento', default='2000-01-01')
    telefono = models.CharField(max_length=15, null=True, blank=True)
    domicilio = models.CharField('Domicilio', max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.user.email} "

    def edad(self):
        today = date.today()
        return (
            today.year - self.fecha_nacimiento.year
            - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        )

class Servicios(models.Model):
    tipo_servicio = models.CharField('Tipo de servicio', max_length=50)
    costo = models.DecimalField('Costo', max_digits=8, decimal_places=2)
    observaciones = models.TextField('Observaciones', null=True, blank=True)

    def __str__(self):
        return f"{self.tipo_servicio} (${self.costo})"

class Empleado(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='empleado',
        limit_choices_to={'is_empleado': True}, # solo usuarios con is_empleado=True
        )
    dni = models.CharField(max_length=8, verbose_name='DNI', null=True, blank=True)
    fecha_nacimiento = models.DateField('Fecha de nacimiento', default='2000-01-01')
    telefono = models.CharField(max_length=15, null=True, blank=True)
    domicilio = models.CharField('Domicilio', max_length=100, null=True, blank=True)
    puestos = models.ManyToManyField(Servicios, blank=True)

    def __str__(self):
        servicios = ", ".join([s.tipo_servicio for s in self.puestos.all()])
        return f"{self.user.get_full_name()} - {servicios} - {self.user.email}"

    def edad(self):
        today = date.today()
        return (
            today.year - self.fecha_nacimiento.year
            - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        )

class Turnos(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicios, on_delete=models.CASCADE)
    fecha = models.DateField('Fecha', default='2000-01-01')
    hora = models.TimeField('Hora', default="09:00")
    observaciones = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return (
            f"Turno del Cliente ''{self.cliente.user.get_full_name()}'' con "
            f" el Empleado ''{self.empleado.user.get_full_name()} ''"
            f" para el Servicio ''{self.servicio.tipo_servicio}'' el dia {self.fecha} a las {self.hora}"
        )

# =======================================
# PARA CREAR PERFIL AUTOMÁTICO
# =======================================

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        if instance.is_cliente:
            Cliente.objects.create(user=instance)
        elif instance.is_empleado:
            Empleado.objects.create(user=instance)
