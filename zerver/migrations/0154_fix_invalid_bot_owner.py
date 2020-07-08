# Generated by Django 1.11.6 on 2018-04-03 01:52

from django.db import migrations
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps


def migrate_fix_invalid_bot_owner_values(apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
    """Fixes UserProfile objects that incorrectly had a bot_owner set"""
    UserProfile = apps.get_model("zerver", "UserProfile")
    UserProfile.objects.filter(is_bot=False).exclude(bot_owner=None).update(bot_owner=None)


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0153_remove_int_float_custom_fields"),
    ]

    operations = [
        migrations.RunPython(
            migrate_fix_invalid_bot_owner_values, reverse_code=migrations.RunPython.noop, elidable=True,
        ),
    ]
