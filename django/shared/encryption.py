from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import json
from django.conf import settings

def get_fernet_key(secret_key, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
    return Fernet(key)

# Create a Fernet cipher suite using the derived key
cipher_suite = get_fernet_key(settings.SECRET_KEY, settings.CRYPTOGRAPHY_SALT)

def encrypt_data(data):
    json_data = json.dumps(data).encode('utf-8')
    encrypted_data = cipher_suite.encrypt(json_data)
    return encrypted_data.decode('utf-8')

def decrypt_data(encrypted_data):
    encrypted_data_bytes = encrypted_data.encode('utf-8')
    decrypted_data = cipher_suite.decrypt(encrypted_data_bytes)
    return json.loads(decrypted_data.decode('utf-8'))
