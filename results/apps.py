# results/apps.py
from django.apps import AppConfig


class ResultsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'results'
    verbose_name = 'Academic Results Management'
    
    def ready(self):
        # Import signals when app is ready
        import results.signals  # noqa
