# Generated by Django 3.0.5 on 2020-11-26 20:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserDataManagment', '0018_auto_20201124_1918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standartuser',
            name='chrome_dir_path',
            field=models.CharField(blank=True, max_length=128, null=True, unique=True, verbose_name='id папки с chrome-профилем'),
        ),
        migrations.AlterField(
            model_name='standartuser',
            name='sub_end_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата окончания действия подписки'),
        ),
    ]
