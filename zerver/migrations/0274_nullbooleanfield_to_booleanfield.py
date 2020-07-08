# Generated by Django 2.2.12 on 2020-04-26 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0273_migrate_old_bot_messages"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stream", name="invite_only", field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="audible_notifications",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="desktop_notifications",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="email_notifications",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name="subscription", name="is_muted", field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name="subscription", name="push_notifications", field=models.BooleanField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="wildcard_mentions_notify",
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name="userprofile", name="enter_sends", field=models.BooleanField(default=False, null=True),
        ),
    ]
