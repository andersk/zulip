# Generated by Django 1.11.20 on 2019-06-23 21:20

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0230_rename_to_enable_stream_audible_notifications"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArchiveTransaction",
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
                (
                    "timestamp",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now,
                    ),
                ),
                ("restored", models.BooleanField(db_index=True, default=False)),
                ("type", models.PositiveSmallIntegerField(db_index=True)),
                (
                    "realm",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="zerver.Realm",
                    ),
                ),
            ],
        ),
        migrations.RemoveField(
            model_name="archivedattachment", name="archive_timestamp",
        ),
        migrations.RemoveField(model_name="archivedmessage", name="archive_timestamp"),
        migrations.RemoveField(
            model_name="archivedreaction", name="archive_timestamp",
        ),
        migrations.RemoveField(
            model_name="archivedsubmessage", name="archive_timestamp",
        ),
        migrations.RemoveField(
            model_name="archivedusermessage", name="archive_timestamp",
        ),
        migrations.AddField(
            model_name="archivedmessage",
            name="archive_transaction",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="zerver.ArchiveTransaction",
            ),
        ),
    ]
