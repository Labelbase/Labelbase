from .utils import compute_type_ref_hash


def update_type_ref_hash(sender, instance, **kwargs):
    """
    This function is triggered before the object is saved and updates
    the hash field based on the 'type' and 'ref' fields.
    """
    instance.type_ref_hash = compute_type_ref_hash(instance.type, instance.ref)


def trigger_electrumx_checkup(sender, instance, **kwargs):
    if instance.type == "output":
        #from finances.models import OutputStat
        #txid, vout =  instance.ref.split(":")
        #obj, created = OutputStat.get_or_create_from_api(
        #                                type_ref_hash=instance.type_ref_hash,
        #                                network=instance.labelbase.network,
        #                                txid=txid, vout=vout, force_reload=True)
        from finances.tasks import check_spent
        check_spent(instance.id)
