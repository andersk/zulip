# Generated by Django 1.11.6 on 2017-10-30 05:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0114_preregistrationuser_invited_as_admin"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserGroup",
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
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="UserGroupMembership",
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
                    "user_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="zerver.UserGroup",
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
        ),
        migrations.AddField(
            model_name="usergroup",
            name="members",
            field=models.ManyToManyField(
                through="zerver.UserGroupMembership", to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="usergroup",
            name="realm",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="zerver.Realm",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="usergroupmembership", unique_together={("user_group", "user_profile")},
        ),
        migrations.AlterUniqueTogether(name="usergroup", unique_together={("realm", "name")}),
    ]
