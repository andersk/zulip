# Generated by Django 1.11.6 on 2018-02-10 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0147_realm_disallow_disposable_email_addresses"),
    ]

    operations = [
        migrations.AlterField(
            model_name="realm",
            name="max_invites",
            field=models.IntegerField(null=True, db_column="max_invites"),
        ),
        migrations.RenameField(model_name="realm", old_name="max_invites", new_name="_max_invites"),
    ]
