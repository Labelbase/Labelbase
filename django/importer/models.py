from django.db import models
from django.contrib.auth.models import User
from labelbase.models import Labelbase
from uuid_upload_path import upload_to

IMPORTER_CHOICES = (
    ("BIP-0329", "BIP-329 .jsonl"),
    #TODO: ("BIP-0329-7z-enc" , "BIP-329 (encrypted) .7z"),
    ("csv-bluewallet", "BlueWallet .csv"),
    ("csv-bitbox", "BitBox .csv"),
    ("pocket-accointing", "Pocket Accointing .csv")
)


class UploadedData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    labelbase = models.ForeignKey(Labelbase, on_delete=models.CASCADE)
    import_type = models.CharField(max_length=255)
    file = models.FileField(upload_to=upload_to)
    #imported_lables = models.IntegerField(default=0)
    #status = Uploaded, processing, processed_success, processed_failed
