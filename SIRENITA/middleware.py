import logging
from django.contrib.auth.models import User
from .signals import registrar_intento_fallido
from .models import RegistroAcceso

logger = logging.getLogger(__name__)


class RegistroAccesoMiddleware:
    """
    Middleware para registrar intentos de login fallidos.
    Se ejecuta después de cualquier request POST al endpoint de login.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Procesar la request
        response = self.get_response(request)
        
        # Registrar intentos de login fallidos
        if request.method == 'POST' and 'login' in request.path.lower():
            # Si el usuario NO está autenticado después del POST a login, fue un intento fallido
            if not request.user.is_authenticated:
                username = request.POST.get('username', 'desconocido')
                obs = f"Intento fallido de login con usuario: {username}"
                
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    user = None
                
                registrar_intento_fallido(user, request, obs)
        
        return response


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
