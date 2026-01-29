from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    """ Permitir solo usuario "pc" """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.username != "pc":
            messages.error(request, "No tienes permiso para acceder a esta sección.")
            return redirect("INICIO")

        return view_func(request, *args, **kwargs)
    return wrapper