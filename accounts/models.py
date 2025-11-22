from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Profile(models.Model):
    ROLE_CHOICES = [
        ("owner", "Vlasnik"),
        ("staff", "Djelatnik"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=40, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="staff")

    def __str__(self):
        return f"{self.user.get_username()} ({self.get_role_display()})"
