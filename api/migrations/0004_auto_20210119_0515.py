# Generated by Django 3.1.5 on 2021-01-19 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20210119_0457'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mail',
            name='folder',
        ),
        migrations.AddField(
            model_name='mail',
            name='folder_name',
            field=models.CharField(default='inbox', max_length=100),
        ),
    ]
