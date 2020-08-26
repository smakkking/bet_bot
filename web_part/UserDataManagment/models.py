from django.contrib.auth.models import AbstractUser
from django.db import models

class StandartUser(AbstractUser):
    bio = models.CharField(max_length=160, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)

    count_gg = models.IntegerField(null=True, blank=True, default=12)

    def __str__(self):
        return self.username