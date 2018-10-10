from django.db import models
from authors.apps.core.models import TimeStampedModel

from django.db.models.signals import post_save
from django.dispatch import receiver

from authors import settings

# Create your models here.
class Profile(TimeStampedModel):
    """
    This class cretes the user profile model
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(max_length=255, default='Update your bio')
    image_url = models.URLField(max_length=250, default="image-url", null=True)
    following = models.BooleanField(default=False)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_save_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        instance.profile.save()
