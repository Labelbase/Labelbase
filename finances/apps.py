from django.apps import AppConfig


class FinancesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "finances"

    def ready(self):

         from .signals import perform_tasks_on_login
