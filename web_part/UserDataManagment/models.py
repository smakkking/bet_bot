from django.contrib.auth.models import AbstractUser
from django.db import models

from moduls.bet_manage import BOOKMAKER_OFFSET

class StandartUser(AbstractUser):
    # поля по букмекерам
    bookmaker = models.CharField(
        max_length=128, 
        default='',
        verbose_name='Букмекер',
        choices=tuple([(key, key) for key in BOOKMAKER_OFFSET.keys()]),
    )
    bookmaker_login = models.CharField(
        max_length=128, 
        default='',
        verbose_name='Логин для аккаунта букмекерской конторы',
    )
    bookmaker_password = models.CharField(
        max_length=128,
        default='',
        verbose_name='Пароль от аккаунта букмекерской конторы',     
    )
    # поля по пользователю
    bet_summ = models.IntegerField(
        default=100,
        verbose_name='Cумма для ставки',
    )
    sub_end_date = models.DateField(
        verbose_name='Дата окончания действия подписки',
        null=True
    )
    chrome_dir_path = models.CharField(
        verbose_name="id папки с chrome-профилем",
        max_length=128,
        default='',
    )
    sub_status = models.BooleanField(
        verbose_name='статус подписки 1 - активна, 0 -нет',
        default=False,
    )
    bot_status = models.BooleanField(
        default=False
    )
    # поля для групп
    CSgoVictory = models.BooleanField(
        default=False,
        verbose_name="CS:GO VICTORY | ПРОГНОЗЫ CSGO & DOTA2",
        help_text='<a href="https://vk.com/victorybets_stavki"> подробнее </a>',
    )
    ExpertMnenie = models.BooleanField(
        default=False,
        verbose_name="Экспертное мнение CSGO | Прогнозы CS:GO & DOTA 2", 
        help_text='<a href="https://vk.com/csgo_expert_dota"> подробнее </a>'
    )

    def __str__(self):
        return self.username