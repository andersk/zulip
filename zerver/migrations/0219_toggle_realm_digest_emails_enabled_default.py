# Generated by Django 1.11.20 on 2019-05-08 05:42

from django.db import migrations, models
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps


def disable_realm_digest_emails_enabled(apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
    Realm = apps.get_model("zerver", "Realm")
    realms = Realm.objects.filter(digest_emails_enabled=True)
    realms.update(digest_emails_enabled=False)


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0218_remove_create_stream_by_admins_only"),
    ]

    operations = [
        migrations.AlterField(
            model_name="realm", name="digest_emails_enabled", field=models.BooleanField(default=False),
        ),
        migrations.RunPython(
            disable_realm_digest_emails_enabled, reverse_code=migrations.RunPython.noop, elidable=True,
        ),
    ]
