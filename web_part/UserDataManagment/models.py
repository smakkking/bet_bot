from django.contrib.auth.models import AbstractUser
from django.db import models

class StandartUser(AbstractUser):
    bookmaker = models.CharField(max_length=128, default='')

    bookmaker_login = models.CharField(max_length=128, default='')
    bookmaker_password = models.CharField(max_length=128, default='')

    AcademiaStavok = models.BooleanField(default=False)
    CSgoNorch = models.BooleanField(default=False)

    def __str__(self):
        return self.username