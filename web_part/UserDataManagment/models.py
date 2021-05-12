from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


from global_links import BOOKMAKER_OFFSET, GROUP_OFFSET


class StandartUser(AbstractUser):
    # поля по букмекерам
    bookmaker = models.CharField(
        max_length=64,
        null=True,
        verbose_name='Букмекер',
        choices=tuple([(key, key) for key in BOOKMAKER_OFFSET.keys()]),
    )

    bookmaker_login = models.CharField(
        max_length=64,
        null=True,
        verbose_name='Логин для аккаунта букмекерской конторы',
        unique=True,
    )

    bookmaker_password = models.CharField(
        max_length=64,
        null=True,
        verbose_name='Пароль от аккаунта букмекерской конторы',
        unique=True,
    )

    # поля по пользователю

    bet_mode = models.CharField(  # 'fixed' || 'bank'
        max_length=16,
        null=False,
        default='fixed',
        choices=(('fixed', 'Фиксированная ставка'),
                 ('bank', 'Процент от текущего банка')),
        verbose_name="Способ ставок",
    )

    bet_summ = models.IntegerField(
        default=100,
        verbose_name='Cумма для ставки',
        help_text="При выборе опции 'Процент от текущего банка' будет сделана ставка на эту сумму, если из поста невозможно понять, сколько ставить)"
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
            MinValueValidator(
                0, message="Количество групп не может быть отрицательным")
        ],
        verbose_name="Количество групп"
    )

    personal_count = models.FloatField(
        default=0.0,
        verbose_name="Ваш баланс"
    )

    free_trial = models.BooleanField(
        default=True,
        verbose_name="Есть ли бесплатная попытка"
    )

    come_from_group = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        verbose_name="Пришел из группы"
    )

    last_month_adding = models.FloatField(
        default=0.0,
        verbose_name="Пополнение за последний месяц",
    )

    # поля для групп

    for group in GROUP_OFFSET.keys():
        s = f"""{group} = models.BooleanField(
            default=False,
            verbose_name="{GROUP_OFFSET[group].TITLE}",
            help_text='<a href="{GROUP_OFFSET[group].WALL_URL}"> подробнее </a>',)
        """
        exec(s)
    for group in GROUP_OFFSET.keys():
        s = f"""is_{group} = models.BooleanField(
            default=False,
            )
        """
        exec(s)

    def __str__(self):
        return self.username
