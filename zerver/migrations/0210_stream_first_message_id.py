# Generated by Django 1.11.18 on 2019-02-25 12:42

from django.db import migrations
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps


def backfill_first_message_id(apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
    Stream = apps.get_model("zerver", "Stream")
    Message = apps.get_model("zerver", "Message")
    for stream in Stream.objects.all():
        first_message = Message.objects.filter(
            recipient__type_id=stream.id, recipient__type=2,
        ).first()
        if first_message is None:
            # No need to change anything if the outcome is the default of None
            continue

        stream.first_message_id = first_message.id
        stream.save()


class Migration(migrations.Migration):
    dependencies = [
        ("zerver", "0209_stream_first_message_id"),
    ]

    operations = [
        migrations.RunPython(
            backfill_first_message_id, reverse_code=migrations.RunPython.noop, elidable=True,
        ),
    ]
