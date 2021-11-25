from django.apps import AppConfig


class LkappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lkapp'

    def ready(self):
        import lkapp.signals