# Generated by Django 1.11.11 on 2018-05-24 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0170_submessage"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile", name="dense_mode", field=models.BooleanField(default=True),
        ),
    ]
