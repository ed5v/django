from django.apps import AppConfig


class SirenitaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'SIRENITA'
    
    def ready(self):
        import SIRENITA.signals  # Cargar señales al iniciar Django
