# Generated by Django 1.11.6 on 2018-01-21 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0137_realm_upload_quota_gb"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile", name="realm_name_in_notifications", field=models.BooleanField(default=False),
        ),
    ]
