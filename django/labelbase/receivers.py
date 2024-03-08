from .utils import compute_type_ref_hash


def update_type_ref_hash(sender, instance, **kwargs):
    """
    This function is triggered before the object is saved and updates
    the hash field based on the 'type' and 'ref' fields.
    """
    instance.type_ref_hash = compute_type_ref_hash(instance.type, instance.ref)


def trigger_electrumx_checkup(sender, instance, **kwargs):
    if instance.type == "output":
        from finances.tasks import check_spent
        check_spent(instance.id)
