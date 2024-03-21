from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from userprofile.models import Profile
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)  # Create user profile
        Token.objects.create(user=instance)  # Create API auth token

        # Check if this is the first user in the system
        if User.objects.count() == 1:
            # Set this user as a staff member if so
            instance.is_staff = True
            instance.save()
