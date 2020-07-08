# Generated by Django 2.2.10 on 2020-03-27 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("confirmation", "0006_realmcreationkey_presume_email_valid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="confirmation",
            name="confirmation_key",
            field=models.CharField(db_index=True, max_length=40),
        ),
        migrations.AlterField(
            model_name="confirmation",
            name="date_sent",
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name="confirmation",
            name="object_id",
            field=models.PositiveIntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name="realmcreationkey",
            name="creation_key",
            field=models.CharField(db_index=True, max_length=40, verbose_name="activation key"),
        ),
        migrations.AlterUniqueTogether(
            name="confirmation", unique_together={("type", "confirmation_key")},
        ),
    ]
