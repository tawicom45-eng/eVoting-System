from django.apps import AppConfig


class PostersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'posters'
    verbose_name = 'Campaign Posters'

    def ready(self):
        # import signals or startup hooks here if needed
        pass
