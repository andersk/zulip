# Generated by Django 1.11.11 on 2018-04-12 01:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("zilencer", "0007_remotezulipserver_fix_uniqueness"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="billing_user",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
