from django.contrib.auth.models import AbstractUser
from django.db import models

BOOKMAKER_CHOICES = (
    ('parimatch', 'Parimatch'),
    ('gg_bet', 'GG.bet'),
    ('phon_bet', 'Фонбет'),
)

class StandartUser(AbstractUser):
    # поля по букмекерам
    bookmaker = models.CharField(
        max_length=128, 
        default='',
        verbose_name='Букмекер',
        choices=BOOKMAKER_CHOICES,
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
    max_bet_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Максимальное количество ставок в день',
    )
    # поля по пользователю
    balance_coefficient = models.FloatField(
        default=1.0,
        verbose_name='Балансный коэффициент',
        help_text="""
        <pre> Скажем так, это тот показатель, который влияет на сумму, которую будет ставить бот. \n Данный коэффициент умножается на сумму, которую ставит каппер
        </pre>
        <p>
        <b> Выберите те группы, которые будет мониторить бот: </b>
        </p>
        """,
    )
    subscr_end_date = models.DateField(
        verbose_name='Дата окончания действия подписки',
        null=True
    )
    chrome_dir_path = models.CharField(
        verbose_name="id папки с chrome-профилем",
        max_length=128,
        default='',
    )
    subscribe_status = models.BooleanField(
        verbose_name='статус подписки 1 - активна, 0 -нет',
        default=False,
    )
    # поля для групп
    AcademiaStavok = models.BooleanField(
        default=False,
        verbose_name="Академия Ставок CSGO • Прогнозы CS:GO & Dota 2",
        help_text='<a href="https://vk.com/akademiya_stavki_csgo"> подробнее </a>',
    )
    CSgoNorch = models.BooleanField(
        default=False,
        verbose_name="Норч CSGO | Прогнозы CS:GO",
        help_text='<a href="https://vk.com/csgo_norch"> подробнее </a>',
    )
    CSgoVictory = models.BooleanField(
        default=False,
        verbose_name="CS:GO VICTORY | ПРОГНОЗЫ CSGO & DOTA2",
        help_text='<a href="https://vk.com/victorybets_stavki"> подробнее </a>',
    )

    def __str__(self):
        return self.username