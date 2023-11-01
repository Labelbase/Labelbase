import hashlib

def update_type_ref_hash(sender, instance, **kwargs):
    """
    This function is triggered before the object is saved and updates
    the hash field based on the 'type' and 'ref' fields.
    """
    data = instance.type + instance.ref
    instance.type_ref_hash = hashlib.sha256(data.encode()).hexdigest()
     
