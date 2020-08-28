# Generated by Django 3.0.5 on 2020-08-27 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserDataManagment', '0006_auto_20200828_0216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standartuser',
            name='balance_coefficient',
            field=models.FloatField(default=1.0, help_text='\n        <pre> Скажем так, это тот показатель, который влияет на сумму, которую будет ставить бот. \n Данный коэффициент умножается на сумму, которую ставит каппер\n        </pre>\n        <p>\n        <bold> Выберите те группы, которые будет мониторить бот </bold>\n        </p>\n        ', verbose_name='Балансный коэффициент'),
        ),
    ]