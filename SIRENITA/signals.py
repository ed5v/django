from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from .models import RegistroAcceso
import logging

logger = logging.getLogger(__name__)


def obtener_ip_cliente(request):
    """Obtiene la IP del cliente desde la request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def obtener_navegador(request):
    """Obtiene el navegador/user-agent del cliente"""
    return request.META.get('HTTP_USER_AGENT', 'Desconocido')[:255]


@receiver(user_logged_in)
def registrar_login(sender, request, user, **kwargs):
    """Se ejecuta cuando un usuario inicia sesión exitosamente"""
    try:
        ip = obtener_ip_cliente(request)
        navegador = obtener_navegador(request)
        
        RegistroAcceso.objects.create(
            usuario=user,
            tipo_acceso='LOGIN',
            ip_address=ip,
            navegador=navegador,
            estado='EXITOSO',
            observaciones='Login exitoso'
        )
        logger.info(f"Usuario {user.username} inició sesión desde {ip}")
    except Exception as e:
        logger.error(f"Error al registrar login: {str(e)}")


@receiver(user_logged_out)
def registrar_logout(sender, request, user, **kwargs):
    """Se ejecuta cuando un usuario cierra sesión"""
    try:
        ip = obtener_ip_cliente(request)
        navegador = obtener_navegador(request)
        
        RegistroAcceso.objects.create(
            usuario=user,
            tipo_acceso='LOGOUT',
            ip_address=ip,
            navegador=navegador,
            estado='EXITOSO',
            observaciones='Logout exitoso'
        )
        logger.info(f"Usuario {user.username} cerró sesión desde {ip}")
    except Exception as e:
        logger.error(f"Error al registrar logout: {str(e)}")


def registrar_intento_fallido(usuario, request, observacion=""):
    """Registra un intento de login fallido"""
    try:
        ip = obtener_ip_cliente(request)
        navegador = obtener_navegador(request)
        
        RegistroAcceso.objects.create(
            usuario=usuario if isinstance(usuario, User) else None,
            tipo_acceso='INTENTO_FALLIDO',
            ip_address=ip,
            navegador=navegador,
            estado='FALLIDO',
            observaciones=observacion
        )
        logger.warning(f"Intento fallido de login desde {ip}: {observacion}")
    except Exception as e:
        logger.error(f"Error al registrar intento fallido: {str(e)}")
