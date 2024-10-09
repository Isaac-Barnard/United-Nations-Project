from django.apps import AppConfig


class UnAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'un_app'

    def ready(self):
        import un_app.signals