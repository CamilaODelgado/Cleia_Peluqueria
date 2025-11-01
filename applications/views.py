from django.shortcuts import render

#---------------------------------- LOGIN y demas en uso ----------------------------------
#from del registro
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
##para poner mensajes
from django.contrib import messages
##
from .forms import CustomUserCreationForm
from django.shortcuts import redirect
from datetime import datetime

from .forms import EditarUsuarioForm, EditarClienteForm, EditarEmpleadoForm

##############################################################################
# VIEWS DE LA APLICACIONES
##############################################################################
from .models import Cliente, Empleado, Servicios, Turnos

# -------------------------------------------
# LISTAS
# -------------------------------------------



def lista_servicios(request):
    servicios = Servicios.objects.all()
    return render(request, 'servicios/servicios.html', {'servicios': servicios})


def agregar_turno(request):
    usuario = request.user
    servicios = Servicios.objects.all()
    empleados = Empleado.objects.all()
    servicio_seleccionado = None
    empleado_seleccionado = None

    # ======== Valores iniciales ========
    nombre = usuario.nombre if usuario.is_authenticated else ''
    apellido = usuario.apellido if usuario.is_authenticated else ''
    email = usuario.email if usuario.is_authenticated else ''
    telefono = ''
    observaciones = ''

    # Autocompletar teléfono según el tipo de usuario logeado
    if usuario.is_authenticated:
        if hasattr(usuario, 'cliente') and usuario.cliente.telefono:
            telefono = usuario.cliente.telefono
        elif hasattr(usuario, 'empleado') and usuario.empleado.telefono:
            telefono = usuario.empleado.telefono

    # ======== Manejo de formularios ========
    if request.method == 'POST':

        if 'servicio' in request.POST and 'guardar' not in request.POST:
            # Recuperar los datos ya escritos antes de recargar
            nombre = request.POST.get('nombre', '').strip()
            apellido = request.POST.get('apellido', '').strip()
            email = request.POST.get('email', '').strip()
            telefono = request.POST.get('telefono', '').strip()
            observaciones = request.POST.get('observaciones', '').strip()

            servicio_id = request.POST.get('servicio')
            empleado_id = request.POST.get('empleado')

            if servicio_id:
                try:
                    servicio_seleccionado = Servicios.objects.get(id=servicio_id)
                    empleados = Empleado.objects.filter(puestos=servicio_seleccionado)
                except Servicios.DoesNotExist:
                    servicio_seleccionado = None

            # Si ya había un empleado elegido, mantenerlo seleccionado
            if empleado_id:
                try:
                    empleado_seleccionado = Empleado.objects.get(id=empleado_id)
                except Empleado.DoesNotExist:
                    empleado_seleccionado = None

            # volver a mostrar el formulario filtrado sin perder los datos
            return render(request, 'turnos/turnos.html', {
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'telefono': telefono,
                'observaciones': observaciones,
                'servicios': servicios,
                'empleados': empleados,
                'servicio_seleccionado': servicio_seleccionado,
                'empleado_seleccionado': empleado_seleccionado,
                'usuario_logeado': usuario.is_authenticated,
            })

        # --- Si presiona cancelar ---
        if 'cancelar' in request.POST:
            messages.info(request, "Se canceló la creación del turno.")
            return redirect('home')

        # --- Si presiona guardar ---
        if 'guardar' in request.POST:
            if not usuario.is_authenticated:
                messages.warning(request, "Debes registrarte o iniciar sesión para agendar un turno.")
                return redirect('register')

            nombre = request.POST.get('nombre', '').strip()
            apellido = request.POST.get('apellido', '').strip()
            email = request.POST.get('email', '').strip()
            telefono = request.POST.get('telefono', '').strip()
            servicio_id = request.POST.get('servicio')
            empleado_id = request.POST.get('empleado')
            fecha_hora_str = request.POST.get('fecha_hora')
            observaciones = request.POST.get('observaciones', '').strip()

            if not servicio_id or not empleado_id:
                messages.error(request, "Por favor selecciona un servicio y un empleado.")
            else:
                try:
                    servicio_seleccionado = Servicios.objects.get(id=servicio_id)
                    empleado = Empleado.objects.get(id=empleado_id)
                    fecha_hora = datetime.strptime(fecha_hora_str, '%Y-%m-%dT%H:%M')

                    # --- Obtener o crear cliente ---
                    if hasattr(usuario, 'cliente'):
                        cliente = usuario.cliente
                        cliente.telefono = telefono
                        cliente.save()
                    else:
                        cliente = Cliente.objects.create(user=usuario, telefono=telefono)

                    # --- Crear el turno ---
                    Turnos.objects.create(
                        cliente=cliente,
                        empleado=empleado,
                        servicio=servicio_seleccionado,
                        fecha=fecha_hora.date(),
                        hora=fecha_hora.time(),
                        observaciones=observaciones
                    )

                    messages.success(request, f'Turno agendado correctamente con {empleado.user.get_full_name()}')
                    return redirect('home')

                except Exception as e:
                    messages.error(request, f"Error al guardar el turno: {e}")

    # ======== Render final ========
    return render(request, 'turnos/turnos.html', {
        'nombre': nombre,
        'apellido': apellido,
        'email': email,
        'telefono': telefono,
        'observaciones': observaciones,
        'servicios': servicios,
        'empleados': empleados,
        'servicio_seleccionado': servicio_seleccionado,
        'empleado_seleccionado': empleado_seleccionado,
        'usuario_logeado': usuario.is_authenticated,
    })
    
@login_required
def lista_turnos(request):
    usuario = request.user

    turnos_cliente = Turnos.objects.none()
    turnos_empleado = Turnos.objects.none()

    # Turnos del cliente logueado
    if usuario.is_cliente:
        cliente = getattr(usuario, 'cliente', None)
        if cliente:
            turnos_cliente = Turnos.objects.filter(cliente=cliente).order_by('-fecha', '-hora')

    # Turnos del empleado logueado: todos los turnos que tienen su servicio asignado
    elif usuario.is_empleado:
        empleado = getattr(usuario, 'empleado', None)
        if empleado:
            turnos_empleado = Turnos.objects.filter(empleado=empleado).order_by('-fecha', '-hora')

    return render(request, 'turnos/lista_turnos.html', {
        'turnos_cliente': turnos_cliente,
        'turnos_empleado': turnos_empleado,
        'user': usuario
    })



@login_required
def detalle_turno(request, turno_id):
    try:
        turno = Turnos.objects.get(id=turno_id)
    except Turnos.DoesNotExist:
        messages.error(request, "El turno no existe.")
        return redirect('datos_personales')

    usuario = request.user
    # Validar permisos: solo cliente dueño o empleado asignado
    if usuario.is_cliente and turno.cliente.user != usuario:
        messages.error(request, "No tienes permiso para ver este turno.")
        return redirect('datos_personales')
    elif usuario.is_empleado and turno.empleado.user != usuario:
        messages.error(request, "No tienes permiso para ver este turno.")
        return redirect('datos_personales')

    return render(request, 'turnos/detalle_turno.html', {'turno': turno})



def coloracion (request):
    return render(request, 'coloracion/coloracion.html')

def corte (request):
    return render(request, 'corte/corte.html')

def tratamiento (request):
    return render(request, 'tratamiento/tratamiento.html')

def home(request):
    return render(request, "index/index.html")





def datos(request):
    usuario = request.user

    # Obtenemos el perfil de Cliente relacionado al usuario
    try:
        cliente = usuario.cliente
    except Cliente.DoesNotExist:
        messages.error(request, "No se encontró el perfil del cliente.")
        return redirect('home')

    if request.method == 'POST':
        # Actualizamos los datos del usuario
        usuario.nombre = request.POST.get('nombre', usuario.nombre)
        usuario.apellido = request.POST.get('apellido', usuario.apellido)
        usuario.email = request.POST.get('email', usuario.email)
        usuario.save()

        # Actualizamos los datos del perfil Cliente
        cliente.dni = request.POST.get('dni', cliente.dni)
        cliente.telefono = request.POST.get('telefono', cliente.telefono)
        cliente.domicilio = request.POST.get('domicilio', cliente.domicilio)
        fecha_nac = request.POST.get('fecha_nacimiento')
        if fecha_nac:
            cliente.fecha_nacimiento = fecha_nac
        cliente.save()

        messages.success(request, "Tus datos personales han sido actualizados correctamente.")
        return redirect('home')  # Después de guardar, redirige al home

    # Renderizamos el formulario con datos autocompletados
    return render(request, 'registro/datos.html', {
        'usuario': usuario,
        'cliente': cliente
    })
    

@login_required
def datos_personales(request):
    usuario = request.user
    perfil = None
    turnos_cliente = Turnos.objects.none()
    turnos_empleado = Turnos.objects.none()

    # 🔹 Determinar tipo de usuario y obtener su perfil
    if usuario.is_cliente:
        perfil = getattr(usuario, 'cliente', None)
        if perfil:
            turnos_cliente = Turnos.objects.filter(cliente=perfil).order_by('-fecha', '-hora')

    elif usuario.is_empleado:
        perfil = getattr(usuario, 'empleado', None)
        if perfil:
            turnos_empleado = Turnos.objects.filter(empleado=perfil).order_by('-fecha', '-hora')

    # Enviamos todo al contexto
    return render(request, 'includes/datos_personales.html', {
        'usuario': usuario,
        'perfil': perfil,
        'turnos_cliente': turnos_cliente,
        'turnos_empleado': turnos_empleado,
    })
    
    
@login_required
def editar_datos(request):
    user = request.user

    # Detectar tipo de perfil
    if user.is_cliente:
        perfil = user.cliente
        PerfilForm = EditarClienteForm
    elif user.is_empleado:
        perfil = user.empleado
        PerfilForm = EditarEmpleadoForm
    else:
        perfil = None
        PerfilForm = None

    # Si presiona "Cancelar"
    if request.method == 'POST' and 'cancelar' in request.POST:
        return redirect('datos_personales')

    if request.method == 'POST':
        user_form = EditarUsuarioForm(request.POST, instance=user)
        perfil_form = PerfilForm(request.POST, instance=perfil) if PerfilForm else None

        if user_form.is_valid() and (perfil_form is None or perfil_form.is_valid()):
            user_form.save()
            if perfil_form:
                perfil_form.save()
            messages.success(request, "Datos actualizados correctamente.")
            return redirect('datos_personales')
    else:
        user_form = EditarUsuarioForm(instance=user)
        perfil_form = PerfilForm(instance=perfil) if PerfilForm else None

    return render(request, 'usuarios/editar_datos.html', {
        'user_form': user_form,
        'perfil_form': perfil_form,
    })


##############################################################################



#---------------------------------- LOGIN y demas en uso ----------------------------------
# -------------------------------------------
# REGISTRO
# -------------------------------------------

def register(request):
    #
    if request.method == 'POST': 
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)    #guarda el usuario 
            # Todo registro desde la web será Cliente
            usuario.is_cliente = True
            usuario.is_empleado = False
            usuario.save()  # dispara la señal y crea Cliente automáticamente

            messages.success(request, f'Cuenta creada para: {usuario.get_full_name()} (Cliente)')
            login(request, usuario)
            return redirect('datos')
        else:
            for msg in form.error_messages:
                messages.error(request, f'{msg}: {form.error_messages[msg]}')

    else:
        form = CustomUserCreationForm()
    return render(request, 'registro/registro.html', {"form": form})

# -------------------------------------------
### LOGIN 
# -------------------------------------------

def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # AuthenticationForm usa 'username'
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido {user.get_full_name()}')
                return redirect('home')
            else:
                messages.error(request, 'Usuario o contraseña incorrecta')
        else:
            messages.error(request, 'Usuario o contraseña incorrecta')
    else:
        form = AuthenticationForm() #esto es para que aparezca el formulario vacio
    return render(request, 'login/Login.html', {'form': form})

# -------------------------------------------
### LOGOUT
# -------------------------------------------
def logout_request(request):
    logout(request)
    messages.info(request, "Has cerrado sesión exitosamente")
    return redirect('home')

#---------------------------------- LOGIN y demas en uso ----------------------------------#

