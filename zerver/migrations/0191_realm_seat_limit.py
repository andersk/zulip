# Generated by Django 1.11.16 on 2018-11-20 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0190_cleanup_pushdevicetoken"),
    ]

    operations = [
        migrations.AddField(
            model_name="realm", name="seat_limit", field=models.PositiveIntegerField(null=True),
        ),
    ]
