from django.db import models
from django.contrib.auth.models import User

import jsonfield

class Labelbase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=160,
        default="",
        blank=True,
    )
    fingerprint = models.CharField(
        max_length=8,
        default="",
        blank=True
    )
    about = models.CharField(
        max_length=200,
        default="",
        blank=True
    )


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
    ref = models.CharField(
        max_length=160,
        default="",
        blank=True,
    )
    label = models.CharField(
        max_length=160,
        default="",
        blank=True,
    )
    data = jsonfield.JSONField()
    labelbase = models.ForeignKey(Labelbase, on_delete=models.CASCADE)
