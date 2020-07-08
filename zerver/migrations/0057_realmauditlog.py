# Generated by Django 1.10.5 on 2017-03-04 07:33
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps
from django.utils.timezone import now as timezone_now


def backfill_user_activations_and_deactivations(
    apps: StateApps, schema_editor: DatabaseSchemaEditor,
) -> None:
    migration_time = timezone_now()
    RealmAuditLog = apps.get_model("zerver", "RealmAuditLog")
    UserProfile = apps.get_model("zerver", "UserProfile")

    for user in UserProfile.objects.all():
        RealmAuditLog.objects.create(
            realm=user.realm,
            modified_user=user,
            event_type="user_created",
            event_time=user.date_joined,
            backfilled=False,
        )

    for user in UserProfile.objects.filter(is_active=False):
        RealmAuditLog.objects.create(
            realm=user.realm,
            modified_user=user,
            event_type="user_deactivated",
            event_time=migration_time,
            backfilled=True,
        )


def reverse_code(apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
    RealmAuditLog = apps.get_model("zerver", "RealmAuditLog")
    RealmAuditLog.objects.filter(event_type="user_created").delete()
    RealmAuditLog.objects.filter(event_type="user_deactivated").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0056_userprofile_emoji_alt_code"),
    ]

    operations = [
        migrations.CreateModel(
            name="RealmAuditLog",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID",
                    ),
                ),
                ("event_type", models.CharField(max_length=40)),
                ("backfilled", models.BooleanField(default=False)),
                ("event_time", models.DateTimeField()),
                (
                    "acting_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "modified_stream",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="zerver.Stream",
                    ),
                ),
                (
                    "modified_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "realm",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="zerver.Realm",
                    ),
                ),
            ],
        ),
        migrations.RunPython(
            backfill_user_activations_and_deactivations,
            reverse_code=reverse_code,
            elidable=True,
        ),
    ]
