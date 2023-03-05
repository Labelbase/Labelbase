from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import jsonfield
from django_cryptography.fields import encrypt

class Labelbase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = encrypt(models.CharField(
        max_length=160,
        default="",
        blank=True,
    ))
    fingerprint = encrypt(models.CharField(
        max_length=8,
        default="",
        blank=True
    ))
    about = encrypt(models.CharField(
        max_length=200,
        default="",
        blank=True
    ))

    def get_absolute_url(self):
         return reverse('labelbase', args=[self.id])

class Label(models.Model):
    TYPE_TX = 'tx'
    TYPE_ADDR = 'addr'
    TYPE_PUBKEY = 'pubkey'
    TYPE_INPUT = 'input'
    TYPE_OUTPUT = 'output'
    TYPE_XPUT = 'xpub'

    TYPE_CHOICES = [
        (TYPE_TX, 'tx'),
        (TYPE_ADDR, 'addr'),
        (TYPE_PUBKEY, 'pubkey'),
        (TYPE_INPUT, 'input'),
        (TYPE_OUTPUT, 'output'),
        (TYPE_XPUT, 'xpub'),
    ]
    type = models.CharField(
        max_length=16,
        choices=TYPE_CHOICES,
        default=TYPE_ADDR,
    )
    ref = encrypt(models.CharField(
        max_length=160,
        default="",
        blank=True,
    ))
    label = encrypt(models.CharField(
        max_length=160,
        default="",
        blank=True,
    ))
    labelbase = models.ForeignKey(Labelbase, on_delete=models.CASCADE)

    def get_absolute_url(self):
        """
        Is used by "edit label" functionality.
        This brings us back to the labelbase once the lable was saved.
        """
        return self.labelbase.get_absolute_url()

    def get_mempool_url(self):
        if self.type == "addr":
            return "https://mempool.space/address/{}".format(self.ref)
        if self.type == "tx":
            return "https://mempool.space/tx/{}".format(self.ref)
        return ""
