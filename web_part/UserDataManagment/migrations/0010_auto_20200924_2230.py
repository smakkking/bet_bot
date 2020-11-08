# Generated by Django 3.0.5 on 2020-09-24 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserDataManagment', '0009_standartuser_chrome_dir_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='standartuser',
            name='subcribe_status',
            field=models.BooleanField(default=False, verbose_name='статус подписки 1 - активна, 0 -нет'),
        ),
        migrations.AlterField(
            model_name='standartuser',
            name='chrome_dir_path',
            field=models.CharField(default='', max_length=128, verbose_name='id папки с chrome-профилем'),
        ),
    ]