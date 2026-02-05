from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

def admin_required(view_func):
    """ Permitir solo usuario "pc" """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            # Capturar la URL solicitada y pasarla como parámetro 'next'
            return redirect(f"{reverse('login')}?next={request.path}")

        if request.user.username != "pc":
            messages.error(request, "No tienes permiso para acceder a esta sección.")
            # Capturar la URL solicitada para redirección después del login
            return redirect(f"{reverse('login')}?next={request.path}")

        return view_func(request, *args, **kwargs)
    return wrapper

#if not request.user.is_staff: