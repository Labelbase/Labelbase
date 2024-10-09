from django.contrib.auth.signals import user_logged_in
from django.contrib import messages
from django.dispatch import receiver
from finances.models import HistoricalPrice

@receiver(user_logged_in)
def perform_tasks_on_login(sender, user, request, **kwargs):
    try:
        if user.profile.update_utxo_on_login:
            from finances.tasks import check_all_outputs
            from labelbase.models import Label
            check_all_outputs(user.id)
            if Label.objects.filter(labelbase__user_id=user.id).exists():
                messages.info(request, (
                    "<strong>Sync in progress:</strong> "
                    "We are checking your unspent transaction outputs now."
                ))
    except Exception as ex:
        messages.info(request, (
            "<strong>Oups:</strong> "
            f"{ex}"
        ))

    # Store nearest price information.
    HistoricalPrice.get_or_create_from_api(user, -1)
