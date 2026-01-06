from django.apps import AppConfig
from django.db.models.signals import post_save


class CoachingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coaching'

    def ready(self):
        # Import here to avoid circular imports
        from django.contrib.auth.models import User
        from .models import UserProfile

        # Create user profile when user is created
        def create_user_profile(sender, instance, created, **kwargs):
            if created:
                UserProfile.objects.create(user=instance)

        post_save.connect(create_user_profile, sender=User)
