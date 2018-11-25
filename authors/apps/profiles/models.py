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
    # The related_name attribute specifies the name of the reverse relation from 
    # the Profile model back to itself.
    # symmetrical=False results in creating one row
    following = models.ManyToManyField('self', related_name='is_following',symmetrical=False)
    followers = models.ManyToManyField('self', symmetrical=False)
    def __str__(self):
        return self.user.username

    def follow(self, profile):
        self.following.add(profile)
        profile.followers.add(self.user.id)

    def unfollow(self, profile):
        self.following.remove(profile)
        profile.followers.remove(self.user.id)

    def list_followers(self, profile):
        return profile.is_following.all()

    def list_following(self, profile):
        return profile.following.all()

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_save_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        instance.profile.save()
