from django.apps import AppConfig


class ModulesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules'

    def ready(self):
        import modules.signals  # Import signals when app is ready
