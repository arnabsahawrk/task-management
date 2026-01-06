from django.db import models
from django.contrib.auth.models import AbstractUser

"""
class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name="profile"
    )
    profile_image = models.ImageField(
        upload_to="profile_images",
        blank=True,
        default="profile_images/default_dp.jpg",
    )
    bio = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.user.username} Profile"
"""


class CustomUser(AbstractUser):
    profile_image = models.ImageField(
        upload_to="profile_images",
        blank=True,
        default="profile_images/default_dp.jpg",
    )
    bio = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.username
