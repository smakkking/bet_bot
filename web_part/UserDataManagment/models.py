from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from global_constants import BOOKMAKER_OFFSET, GROUP_OFFSET

class StandartUser(AbstractUser):
    # поля по букмекерам
    bookmaker = models.CharField(
        max_length=64, 
        null=True,
        blank=True,
        verbose_name='Букмекер',
        choices=tuple([(key, key) for key in BOOKMAKER_OFFSET.keys()]),
    )

    bookmaker_login = models.CharField(
        max_length=64, 
        null=True,
        blank=True,
        verbose_name='Логин для аккаунта букмекерской конторы',
    )

    bookmaker_password = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name='Пароль от аккаунта букмекерской конторы',
    )

    # поля по пользователю
    bet_summ = models.IntegerField(
        default=100,
        verbose_name='Cумма для ставки',
    )

    sub_end_date = models.DateField(
        verbose_name='Дата окончания действия подписки',
        null=True,
        blank=True,
    )

    sub_status = models.BooleanField(
        default=False,
    )

    bot_status = models.BooleanField(
        default=False,
    )

    max_group_count = models.IntegerField(
        default=0,
        validators=[
            MaxValueValidator(len(GROUP_OFFSET.keys())),
            MinValueValidator(0, message="Количество групп не может быть отрицательным")
        ],
        verbose_name="Количество групп"
    )

    personal_count = models.FloatField(
        default=0.0,
        verbose_name="Ваш баланс",
        validators=[
            MinValueValidator(0, message="Ошибка, недостаточно средств на счету")
        ],
    )

    free_trial = models.BooleanField(
        default=True
    )

    # поля для групп

    for group in GROUP_OFFSET.keys():
        s = f"""{group} = models.BooleanField(
            default=False,
            verbose_name="{GROUP_OFFSET[group].TITLE}",
            help_text='<a href="{GROUP_OFFSET[group].WALL_URL}"> подробнее </a>',)
        """
        exec(s)

    def __str__(self):
        return self.username