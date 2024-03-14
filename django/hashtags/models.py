from django.db import models
from django.contrib.auth.models import User
from django_cryptography.fields import encrypt
from django.urls import reverse
from labelbase.models import Labelbase

class Hashtag(models.Model):
    labelbase = models.ForeignKey(Labelbase, on_delete=models.CASCADE)
    name = encrypt(
        models.CharField(
            max_length=160,
            default="",
            blank=True,
        )
    )
    description = encrypt(models.TextField(default="", blank=True))

    def get_absolute_url(self):
        return reverse('hashtag_edit', kwargs={'pk': self.pk})
