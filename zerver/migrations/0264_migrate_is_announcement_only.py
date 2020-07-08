# Generated by Django 1.11.26 on 2020-01-25 23:47

from django.db import migrations
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps


def upgrade_stream_post_policy(apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
    Stream = apps.get_model("zerver", "Stream")
    Stream.STREAM_POST_POLICY_EVERYONE = 1
    Stream.STREAM_POST_POLICY_ADMINS = 2
    Stream.objects.filter(is_announcement_only=False).update(
        stream_post_policy=Stream.STREAM_POST_POLICY_EVERYONE,
    )
    Stream.objects.filter(is_announcement_only=True).update(
        stream_post_policy=Stream.STREAM_POST_POLICY_ADMINS,
    )


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0263_stream_stream_post_policy"),
    ]

    operations = [
        migrations.RunPython(
            upgrade_stream_post_policy, reverse_code=migrations.RunPython.noop, elidable=True,
        ),
    ]
