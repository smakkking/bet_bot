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
        unique=True,
    )

    bookmaker_password = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name='Пароль от аккаунта букмекерской конторы',
        unique=True,
    )

    dogon_on = models.BooleanField(
        default=False,
        verbose_name="Использовать ли тактику догона в группах"
    )

    bookmaker_last_login = models.DateTimeField(
        null=True,
        blank=True,
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

    chrome_dir_path = models.CharField(
        verbose_name="id папки с chrome-профилем",
        max_length=64,
        null=True,
        unique=True,
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
            MinValueValidator(1, message="Количество групп не может быть отрицательным")
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

    # поля для групп
    CSgoVictory = models.BooleanField(
        default=False,
        verbose_name="CS:GO VICTORY | ПРОГНОЗЫ CSGO & DOTA2",
        help_text='<a href="' + GROUP_OFFSET['CSgoVictory'].WALL_URL + '"> подробнее </a>',
    )

    ExpertMnenie = models.BooleanField(
        default=False,
        verbose_name="Экспертное мнение CSGO | Прогнозы CS:GO & DOTA 2", 
        help_text='<a href="' + GROUP_OFFSET['ExpertMnenie'].WALL_URL + '"> подробнее </a>',
    )

    BetsPedia = models.BooleanField(
        default=False,
        verbose_name="BETSPEDIA CS:GO | ПРОГНОЗЫ CSGO & DOTA 2",
        help_text='<a href="' + GROUP_OFFSET['BetsPedia'].WALL_URL + '"> подробнее </a>',
    )

    aristocratical = models.BooleanField(
        default=False,
        verbose_name="Аристократ CS:GO | Прогнозы и ставки CSGO & Dota",
        help_text='<a href="' + GROUP_OFFSET['aristocratical'].WALL_URL + '"> подробнее </a>',
    )

    savemoney = models.BooleanField(
        default=False,
        verbose_name="SaveMoney CSGO | Прогнозы и ставки CS:GO & DOTA2",
        help_text='<a href="' + GROUP_OFFSET['savemoney'].WALL_URL + '"> подробнее </a>',
    )

    CSGO99percent = models.BooleanField(
        default=False,
        verbose_name="99% CS:GO | ПРОГНОЗЫ CSGO & DOTA 2",
        help_text='<a href="' + GROUP_OFFSET['CSGO99percent'].WALL_URL + '"> подробнее </a>',
    )


    def __str__(self):
        return self.username