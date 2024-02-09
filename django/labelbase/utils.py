import hashlib


def compute_type_ref_hash(type, ref):
    data = type + ref
    return hashlib.sha256(data.encode()).hexdigest()
