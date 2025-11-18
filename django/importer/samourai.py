import json
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
import hashlib
import re
import base64

from labelbase.serializers import LabelSerializer
from labelbase.models import Label

import logging
logger = logging.getLogger('labelbase')

DefaultPBKDF2Iterations = 5000
DefaultPBKDF2HMACSHA256Iterations = 15000
DefaultSamouraiImportLabel = "Imported form samourai.txt"





def decrypt_v1(payload, password, iterations=DefaultPBKDF2Iterations):
    # V1 uses PBKDF2 for key derivation and AES for decryption
    AESBlockSize = 16
    cipherdata = base64.b64decode(payload)
    iv = cipherdata[:AESBlockSize]
    input_data = cipherdata[AESBlockSize:]
    key = PBKDF2(password, iv, dkLen=32, count=iterations)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(input_data)
    return decrypted.rstrip(b"\x00").decode('utf-8')


def decrypt_v2(payload, password, iterations=DefaultPBKDF2HMACSHA256Iterations):
    # V2 uses SHA256 for key derivation and AES for decryption
    encrypted_bytes = base64.b64decode(payload.replace("\n", ""))
    salt = encrypted_bytes[8:16]
    cipher_text = encrypted_bytes[16:]
    key_iv = PBKDF2(password, salt, dkLen=48, count=iterations, hmac_hash_module=SHA256)
    key = key_iv[:32]
    iv = key_iv[32:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(cipher_text)
    pad_len = decrypted[-1]
    decrypted = decrypted[:-pad_len]
    return decrypted.decode('utf-8')


def import_samourai_labels(labelbase, content, passphrase):
    content = content.decode('utf-8')
    pattern = re.compile(r'\{.*?\}')
    match = pattern.search(content)
    imported_lables = 0
    payload = None
    if match:
        json_content = match.group(0)
        try:
            logger.info(f"json_content {json_content}")
            data = json.loads(json_content)
            logger.info(f"data: {data}")
            version = data.get("version", 1)
            payload = data.get("payload", "")
            if payload:
                if version in [1, "1"]:
                    decrypted_data = decrypt_v1(payload, passphrase)
                elif version in [2, "2"]:
                    decrypted_data = decrypt_v2(payload, passphrase)
                else:
                    logger.error(f"Unsupported backup version: {version}")
                    raise ValueError(f"Unsupported backup version: {version}")
                logger.info(decrypted_data)
                samourai_data = json.loads(decrypted_data)
                logger.info(samourai_data)

                """
                DOC/KB: If the labelbase where you import your samourai.txt into, labelbase will set the fingerprint,
                """
                labels = Label.objects.filter(labelbase__id=labelbase.id)
                if labels.count() == 0:
                    if not labelbase.fingerprint:
                        labelbase.fingerprint = samourai_data.get('wallet').get('fingerprint')
                    if samourai_data.get('wallet').get('testnet'):
                        labelbase.network == labelbase.TESTNET
                    else:
                        labelbase.network == labelbase.MAINNET
                    labelbase.save()

                xpub = samourai_data.get('wallet', {}).get('accounts')[0].get('xpub')
                ypub = samourai_data.get('wallet', {}).get('bip49_accounts')[0].get('ypub')
                zpub = samourai_data.get('wallet', {}).get('bip84_accounts')[0].get('zpub')

                for pub in [xpub, ypub, zpub]:
                    if pub:
                        _data = {
                            "type": Label.TYPE_XPUB,
                            "ref": pub,
                            "label": DefaultSamouraiImportLabel,
                        }
                        _data["labelbase"] = labelbase.id
                        serializer = LabelSerializer(data=_data)
                        if serializer.is_valid():
                            serializer.save()
                            imported_lables += 1

                utxo_notes = samourai_data.get('meta', {}).get('utxo_notes')
                logger.info(utxo_notes)
                for note in utxo_notes:
                    _data = {
                        "type": Label.TYPE_TX,
                        "ref": note[0],
                        "label": note[1],
                    }
                    _data["labelbase"] = labelbase.id
                    serializer = LabelSerializer(data=_data)
                    if serializer.is_valid():
                        serializer.save()
                        imported_lables += 1
                blocked_utxos = samourai_data.get('meta', {}).get('blocked_utxos',{}).get('blocked')
                logger.info(blocked_utxos)
                for utxo in blocked_utxos:
                    _data = {
                        "type": Label.TYPE_OUTPUT,
                        "ref": utxo.get('id','').replace("-", ":"),
                        "label": DefaultSamouraiImportLabel,
                        "spendable": False
                    }
                    _data["labelbase"] = labelbase.id
                    serializer = LabelSerializer(data=_data)
                    if serializer.is_valid():
                        serializer.save()
                        imported_lables += 1
                return imported_lables

            else:
                print("No payload found in the JSON content.")
                logger.error("No payload found in the JSON content.")
                return imported_lables
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}")
            logger.error(f"JSONDecodeError: {e}")
            return imported_lables
        except Exception as ex:
            print(f"An error occurred: {ex}")
            logger.error(f"An error occurred: {ex}")
            logger.error(ex, exc_info=True)
            return imported_lables
    else:
        print("No JSON found in file.")
        logger.error("No JSON found in file.")
    return imported_lables
