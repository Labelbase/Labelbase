from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from finances.models import HistoricalPrice

@receiver(user_logged_in)
def perform_tasks_on_login(sender, user, request, **kwargs):
    """ """
    from finances.tasks import check_all_outputs
    check_all_outputs(user.id)

    # Store nearest price information.
    HistoricalPrice.get_or_create_from_api(-1)
