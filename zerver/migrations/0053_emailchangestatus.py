# Generated by Django 1.10.5 on 2017-02-23 05:37
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0052_auto_fix_realmalias_realm_nullable"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmailChangeStatus",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("new_email", models.EmailField(max_length=254)),
                ("old_email", models.EmailField(max_length=254)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.IntegerField(default=0)),
                ("realm", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="zerver.Realm")),
                (
                    "user_profile",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
    ]
