# Generated by Django 1.11.20 on 2019-05-29 13:28

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0224_alter_field_realm_video_chat_provider"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArchivedReaction",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("emoji_name", models.TextField()),
                (
                    "reaction_type",
                    models.CharField(
                        choices=[
                            ("unicode_emoji", "Unicode emoji"),
                            ("realm_emoji", "Custom emoji"),
                            ("zulip_extra_emoji", "Zulip extra emoji"),
                        ],
                        default="unicode_emoji",
                        max_length=30,
                    ),
                ),
                ("emoji_code", models.TextField()),
                (
                    "archive_timestamp",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now,
                    ),
                ),
                (
                    "message",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="zerver.ArchivedMessage",
                    ),
                ),
                (
                    "user_profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.AlterUniqueTogether(
            name="archivedreaction",
            unique_together={("user_profile", "message", "emoji_name")},
        ),
    ]
