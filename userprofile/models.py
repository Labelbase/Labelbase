from django.db import models
from django.contrib.auth.models import User
from labelbase.models import Labelbase


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mempool_endpoint = models.CharField(
        max_length=160,
        default="https://mempool.space",
        blank=True,
    )

    def labelbases(self):
        return Labelbase.objects.filter(user_id=self.user_id)

    def __str__(self):
        return self.user.username
