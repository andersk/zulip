# Generated by Django 2.2.12 on 2020-05-01 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0279_message_recipient_subject_indexes"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile", name="presence_enabled", field=models.BooleanField(default=True),
        ),
    ]
