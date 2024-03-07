from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from finances.models import HistoricalPrice
from django.contrib import messages




@receiver(user_logged_in)
def perform_tasks_on_login(sender, user, request, **kwargs):
    """ """
    if user.profile.update_utxo_on_login:
        from finances.tasks import check_all_outputs
        check_all_outputs(user.id)
        messages.info(request, "<strong>FYI:</strong> We are checking all unspent transaction outputs now.")


    # Store nearest price information.
    HistoricalPrice.get_or_create_from_api(-1)
