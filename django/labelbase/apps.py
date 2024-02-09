from django.apps import AppConfig


class LabelbaseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "labelbase"

    def ready(self):
        from django.db.models.signals import pre_save, post_save
        from .models import Label
        from .receivers import update_type_ref_hash
        from .receivers import trigger_electrumx_checkup

        pre_save.connect(update_type_ref_hash, sender=Label, dispatch_uid="update_type_ref_hash")
        post_save.connect(trigger_electrumx_checkup, sender=Label, dispatch_uid="trigger_electrumx_checkup")
