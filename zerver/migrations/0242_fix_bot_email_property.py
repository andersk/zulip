# Generated by Django 1.11.24 on 2019-09-23 20:39

from django.db import migrations
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps


def fix_bot_email_property(apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
    UserProfile = apps.get_model("zerver", "UserProfile")
    for user_profile in UserProfile.objects.filter(is_bot=True):
        if user_profile.email != user_profile.delivery_email:
            user_profile.email = user_profile.delivery_email
            user_profile.save(update_fields=["email"])


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0241_usermessage_bigint_id_migration_finalize"),
    ]

    operations = [
        migrations.RunPython(fix_bot_email_property, reverse_code=migrations.RunPython.noop, elidable=True),
    ]
