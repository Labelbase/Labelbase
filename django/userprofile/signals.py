from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from userprofile.models import Profile
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)  # create user profile
        Token.objects.create(user=instance)  # create API auth token
