from django.contrib import admin
from django.urls import path
from django.shortcuts import render

#Views de la applications
from applications.views import lista_servicios, agregar_turno, datos_personales,datos, editar_datos, detalle_turno
from applications.views import register, logout_request, login_request
from applications.views import coloracion,corte,tratamiento,lista_turnos

from django.contrib.auth import views as auth_views

def home(request):
    return render(request, "index/index.html")


###############

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home
    path('', home, name='home'),

    # Login y Registro
    path('logout/', logout_request, name= 'logout'),
    path('login/', login_request, name='login'),
    path('register/', register, name='register'),

    # Apps

    path('servicios/', lista_servicios, name='lista_servicios'),
    path('turnos/', agregar_turno, name='agregar_turno'),
    
    path('coloracion/',coloracion, name='coloracion'),
    path('corte/',corte, name='corte'),
    path('tratamiento/',tratamiento, name='tratamiento'),
    path('lista_turnos/', lista_turnos, name='lista_turnos'),
    path('turnos/<int:turno_id>/', detalle_turno, name='detalle_turno'),
    
    #Datos Personales
    path('datos/', datos, name='datos'),
    path('datos_personales/', datos_personales, name='datos_personales'),
    path('datos/editar/', editar_datos, name='editar_datos'),
    
    # Recuperar contraseña
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='login/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='login/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='login/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='login/password_reset_complete.html'), name='password_reset_complete'),
    
    
    
]