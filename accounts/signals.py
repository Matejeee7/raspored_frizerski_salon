from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, created, **kwargs):
    # Ako je nov korisnik, kreiraj Profile; ako je postojeći bez profila, osiguraj da postoji
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)
