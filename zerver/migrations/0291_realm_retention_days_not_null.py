# Generated by Django 2.2.13 on 2020-06-24 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zerver', '0290_remove_night_mode_add_color_scheme'),
    ]

    operations = [
        migrations.AlterField(
            model_name='realm',
            name='message_retention_days',
            field=models.IntegerField(default=-1),
        ),
    ]
