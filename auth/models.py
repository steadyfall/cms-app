from django.db import models
from django.contrib.auth.models import User
from adminpanel.models import Plant


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    assigned_plant = models.OneToOneField(
        Plant,
        default=Plant.get_default_pk,
        on_delete=models.SET_DEFAULT,
        related_name="supervisor_profile",
    )
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
