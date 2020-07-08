# Generated by Django 1.11.20 on 2019-05-29 13:57

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0225_archived_reaction_model"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArchivedSubMessage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID",
                    ),
                ),
                ("msg_type", models.TextField()),
                ("content", models.TextField()),
                (
                    "archive_timestamp",
                    models.DateTimeField(db_index=True, default=django.utils.timezone.now),
                ),
                (
                    "message",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="zerver.ArchivedMessage",
                    ),
                ),
                (
                    "sender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"abstract": False},
        ),
    ]
