from django.apps import AppConfig


class VisionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vision'
    verbose_name = 'Reconocimiento Visual'

    def ready(self):
        from . import detector
        detector.inicializar()
